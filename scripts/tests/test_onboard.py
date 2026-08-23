"""Tests for brownfield onboarding — arriving at a repository never seen before.

The weight here is on the two ways a baseline becomes worthless, because neither
is visible from the report itself:

* **Guessing.** A profile field inferred rather than read makes every number
  downstream confident and wrong, and the adopter believes the numbers long
  before they question the profile. So the tests assert what detection *refuses*
  to conclude at least as hard as what it concludes.
* **Writing.** Scan & Learn is read-only. A tool that silently authors
  `governance/project.toml` has decided which standards apply on the adopter's
  behalf, which is the one decision that is not the tool's to make.

The third group pins arithmetic that is easy to get subtly wrong: the heatmap's
four columns must partition the applicable set exactly once, so a standard can
never be counted as both evidenced and violated.
"""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

import pytest
from governova_checks import DEFAULT_IGNORES, is_ignored
from governova_cli.__main__ import DEFAULT_ONBOARD_TOP
from governova_compile.discovery import resolve_repo_root
from governova_compile.writer import load_index
from governova_evidence import ProbeResult, Verdict
from governova_onboard import (
    DEFAULT_TOP,
    DIMENSIONS,
    ProfileExistsError,
    accept,
    assess,
    detect,
    proposed_profile,
    render_profile,
)
from governova_onboard.baseline import Baseline, _heatmap
from governova_onboard.render import to_json
from governova_project import Profile


@pytest.fixture(scope="module")
def index():
    return load_index(resolve_repo_root() / "compiled" / "constitution.json")


def _repo(tmp_path: Path, files: dict[str, str]) -> Path:
    for name, body in files.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    return tmp_path


# ── Detection reads; it does not infer ───────────────────────────────────────


def test_stack_comes_from_the_manifest_that_declares_it(tmp_path: Path) -> None:
    root = _repo(tmp_path, {"pyproject.toml": '[project]\nname = "x"\ndependencies = ["fastapi"]\n'})
    found = detect(root)
    assert "python" in found.stacks
    assert "fastapi" in found.stacks
    # Every claim points at the file that proves it.
    assert all(s.evidence.startswith("pyproject.toml") for s in found.of("stack"))


def test_a_language_count_never_becomes_a_stack(tmp_path: Path) -> None:
    """Ninety Ruby files with no Gemfile is an observation, not a declaration.

    Extension counts are reported for the reader and deliberately kept out of
    applicability. Letting them narrow the applicable set would mean a stray
    vendored file could exclude a whole constitution.
    """
    root = _repo(tmp_path, {f"lib/f{i}.rb": "puts 1\n" for i in range(90)})
    found = detect(root)
    assert "ruby" in found.values("language")
    assert found.stacks == ()
    assert "stack" in found.undetected


def test_framework_matching_is_exact_not_substring(tmp_path: Path) -> None:
    """`next-auth` is not Next.js, and `nextra` is not Next.js.

    A substring rule would report a Next.js project — and therefore apply an
    entire stack-exclusive body of standards — on the strength of a session
    library that merely starts with the same five letters.
    """
    root = _repo(
        tmp_path,
        {"package.json": json.dumps({"dependencies": {"next-auth": "^4", "nextra": "^2"}})},
    )
    found = detect(root)
    assert "node" in found.stacks
    assert "nextjs" not in found.stacks


def test_a_broken_manifest_still_yields_its_base_stack(tmp_path: Path) -> None:
    """An unparseable manifest is still a manifest. It proves the stack exists."""
    root = _repo(tmp_path, {"package.json": "{ this is not json"})
    found = detect(root)
    assert "node" in found.stacks


def test_domain_and_phase_are_never_detected(tmp_path: Path) -> None:
    """The two dimensions no scan can settle stay unset, whatever is in the repo.

    A payments ledger and a lesson planner can be structurally identical, and
    code on disk cannot distinguish a completed phase from a thorough one.
    """
    root = _repo(
        tmp_path,
        {
            "pyproject.toml": '[project]\nname = "bank"\ndependencies = ["django"]\n',
            "app/payments.py": "def transfer(): ...\n",
            "app/ledger.py": "BALANCE = 0\n",
        },
    )
    profile = proposed_profile(detect(root))
    assert profile.domains == []
    assert profile.phase is None


def test_a_proposed_profile_declares_no_satisfied_standards(tmp_path: Path) -> None:
    """Arriving at a repository does not grant it evidence.

    Coverage is a ratio. A profile that proposes satisfactions inflates the
    numerator on first contact, which is the one number an adopter will quote.
    """
    root = _repo(tmp_path, {"go.mod": "module x\n"})
    profile = proposed_profile(detect(root))
    assert profile.satisfied == []
    assert profile.exceptions == []


def test_every_probed_dimension_is_reported_even_when_empty(tmp_path: Path) -> None:
    """A repository with nothing detectable produces a useful report, not none."""
    root = _repo(tmp_path, {"NOTES": "hello\n"})
    found = detect(root)
    assert found.empty
    # Everything was looked for, and everything came back undetected.
    assert set(found.undetected) == set(DIMENSIONS)


def test_tests_and_ci_are_detected_with_evidence(tmp_path: Path) -> None:
    root = _repo(
        tmp_path,
        {
            "pyproject.toml": '[project]\nname = "x"\n',
            "tests/test_thing.py": "def test_x(): ...\n",
            ".github/workflows/ci.yml": "on: push\n",
        },
    )
    found = detect(root)
    assert found.values("tests") == ("present",)
    assert found.values("ci") == ("GitHub Actions",)
    assert found.of("ci")[0].evidence == ".github/workflows/ci.yml"


# ── Scan & Learn is read-only ────────────────────────────────────────────────


def _tree(root: Path) -> set[str]:
    return {p.relative_to(root).as_posix() for p in root.rglob("*")}


def test_assess_writes_nothing(tmp_path: Path, index) -> None:
    """The whole of Scan & Learn touches no file. This is the mode's promise."""
    root = _repo(
        tmp_path,
        {
            "pyproject.toml": '[project]\nname = "x"\n',
            "app/main.py": "PASSWORD = 'hunter2'\n",
        },
    )
    before = _tree(root)
    assess(root, index)
    assert _tree(root) == before


def test_the_profile_is_written_only_when_asked(tmp_path: Path, index) -> None:
    root = _repo(tmp_path, {"pyproject.toml": '[project]\nname = "x"\n'})
    text = render_profile(detect(root))
    assert not (root / "governance" / "project.toml").exists()
    written = accept(root, text)
    assert written.is_file()


def test_accept_refuses_to_overwrite_an_existing_profile(tmp_path: Path) -> None:
    """An existing profile is a human decision about which standards apply.

    Replacing it with a generated guess would discard the strongest statement
    the repository makes about itself.
    """
    root = _repo(tmp_path, {"governance/project.toml": '[project]\nname = "mine"\n'})
    with pytest.raises(ProfileExistsError):
        accept(root, render_profile(detect(root)))
    assert (root / "governance" / "project.toml").read_text(encoding="utf-8") == (
        '[project]\nname = "mine"\n'
    )


def test_the_proposed_profile_is_valid_toml(tmp_path: Path) -> None:
    """It is offered for a human to accept, so it has to parse when they do.

    The first version of this rendered through a markup-parsing console, which
    read `[project]` as a style tag and deleted it — offering a reviewer a file
    that could not load.
    """
    root = _repo(tmp_path, {"pyproject.toml": '[project]\nname = "x"\ndependencies = ["flask"]\n'})
    text = render_profile(detect(root), domains=("D-SAAS",))
    parsed = tomllib.loads(text)
    assert parsed["project"]["name"] == "x"
    assert "flask" in parsed["project"]["stacks"]
    # The two underivable fields are present as commented placeholders, not
    # omitted — a field absent from a generated file is one nobody fills in.
    assert "# domains = []" in text
    assert "# phase = 3" in text
    assert "domains" not in parsed["project"]
    assert "phase" not in parsed["project"]


def test_an_undetected_stack_is_stated_rather_than_left_blank(tmp_path: Path) -> None:
    root = _repo(tmp_path, {"README": "hi\n"})
    text = render_profile(detect(root))
    assert "NOT DETECTED" in text
    assert tomllib.loads(text)["project"].get("stacks") is None


# ── The heatmap's arithmetic ─────────────────────────────────────────────────


def test_heatmap_columns_partition_the_applicable_set(tmp_path: Path, index) -> None:
    """applicable == evidenced + violated + unknown, on every row and in total.

    A row that does not add up means a standard was counted twice, which makes
    every percentage drawn from the table wrong in a way no reader can see.
    """
    root = _repo(
        tmp_path,
        {"pyproject.toml": '[project]\nname = "x"\n', "app/api.py": "def f(): ...\n"},
    )
    baseline = assess(root, index)
    for gap in baseline.gaps:
        assert gap.applicable == gap.evidenced + gap.violated + gap.unknown
    assert baseline.applicable == baseline.evidenced + baseline.violated + baseline.unknown


def test_a_violation_outranks_a_clean_check_on_the_same_standard(index) -> None:
    """Evidence against beats evidence for, and the counts stay disjoint."""
    profile = Profile(name="x", stacks=[], domains=[], phase=None)
    shared = "S1.103"
    rows = _heatmap(index, profile, evidenced={shared}, violated={shared})
    row = next(r for r in rows if r.constitution_id == "C01")
    assert row.violated >= 1
    assert row.evidenced == 0
    assert row.applicable == row.evidenced + row.violated + row.unknown


def test_undetermined_is_never_counted_as_satisfied(tmp_path: Path, index) -> None:
    """A repository with almost nothing in it is mostly `unknown`, not mostly clean.

    This is the temptation Stage 0 exists to resist: a baseline full of
    `unknown` looks less impressive than one full of violations, and it is the
    honest one.
    """
    root = _repo(tmp_path, {"main.py": "x = 1\n"})
    baseline = assess(root, index)
    assert baseline.unknown > baseline.evidenced
    assert baseline.unknown > baseline.violated


def test_structural_violations_are_reportable(tmp_path: Path, index) -> None:
    """Anything counted in the `violated` column must be printable somewhere.

    The first run of this report showed a violated standard beside "no findings",
    because the findings section only knew about the reliable tier. A number the
    report cannot explain is worse than a number it does not show.
    """
    baseline = assess(resolve_repo_root(), index)
    accounted = {g.standard for g in baseline.groups} | {
        p.standard for p in baseline.violated_probes
    }
    counted = sum(g.violated for g in baseline.gaps)
    assert counted <= len(accounted)


# ── Guards ───────────────────────────────────────────────────────────────────


def test_cli_default_top_matches_the_package_default() -> None:
    """The CLI duplicates this constant because typer evaluates defaults at import.

    Duplication is acceptable; silent drift is not, so it is asserted rather
    than trusted.
    """
    assert DEFAULT_ONBOARD_TOP == DEFAULT_TOP


@pytest.mark.parametrize(
    "path",
    [
        "test/app.route.js",
        "packages/core/test/thing.js",
        "__tests__/component.tsx",
        "spec/models/user_spec.rb",
        "specs/api.js",
        "tests/test_x.py",
    ],
)
def test_test_directories_are_skipped_whatever_the_convention(path: str) -> None:
    """Test code legitimately contains the patterns the rules look for.

    `tests/` alone was invisible for as long as the engine only scanned its own
    source tree. The first onboarding run against express found twenty blocking
    findings in `test/`, singular — every one an error-handling fixture written
    on purpose.
    """
    assert is_ignored(path, DEFAULT_IGNORES)


@pytest.mark.parametrize(
    "path",
    [
        "src/latest/api.py",       # "latest" ends in "test"
        "contest/main.go",         # "contest" ends in "test"
        "spectrum/analyser.py",    # "spectrum" starts with "spec"
        "app/specials/rate.rb",    # "specials" starts with "spec"
    ],
)
def test_the_skip_list_does_not_swallow_production_code(path: str) -> None:
    """The directory globs must match path segments, not the letters inside them.

    Every case here is a real directory name containing `test` or `spec` as a
    substring. Widening the skip list until a report looks clean is how a
    scanner stops scanning, and it would be invisible: the findings simply never
    appear.
    """
    assert not is_ignored(path, DEFAULT_IGNORES)


def test_json_output_carries_the_provisional_reasons(tmp_path: Path, index) -> None:
    """A machine consumer must be able to see the numbers are not settled."""
    root = _repo(tmp_path, {"go.mod": "module x\n"})
    payload = json.loads(to_json(assess(root, index)))
    assert payload["profile"]["domains"] == []
    assert payload["profile"]["phase"] is None
    assert any("domain" in reason for reason in payload["provisional"])
    assert payload["heatmap"]["totals"]["unknown"] > 0


def test_baseline_probe_results_are_carried_untouched(tmp_path: Path, index) -> None:
    """Probes reach the report as they were produced, `unknown` included."""
    root = _repo(tmp_path, {"main.py": "x = 1\n"})
    baseline: Baseline = assess(root, index)
    assert baseline.probes
    assert any(p.verdict is Verdict.UNKNOWN for p in baseline.probes)
    assert all(isinstance(p, ProbeResult) for p in baseline.probes)


# ── first-run friction ───────────────────────────────────────────────────────


def test_assess_reports_each_phase_as_it_starts(tmp_path: Path, index) -> None:
    """Measured at 9m15s on 711 files with nothing printed until the report.

    On a first run, against a tool the reader has no reason to trust yet, a
    silent wait that long is indistinguishable from a hang — and `onboard` is
    deliberately the first command a new adopter types.
    """
    root = _repo(tmp_path, {"a.ts": "const sum = a + b;\n"})
    seen: list[str] = []
    assess(root, index, progress=seen.append)

    assert seen, "no phase was reported"
    # The scan and the score are the two long ones; a progress line that skipped
    # them would be reassurance rather than information.
    joined = " | ".join(seen)
    assert "scanning" in joined
    assert "Score" in joined


def test_assess_still_runs_without_a_progress_callback(tmp_path: Path, index) -> None:
    root = _repo(tmp_path, {"a.ts": "const sum = a + b;\n"})
    assert assess(root, index) is not None
