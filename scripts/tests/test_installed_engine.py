"""What an adopter gets, rather than what the source tree gets.

Every other test in this suite runs inside a Governova checkout, where
`compiled/constitution.json` is on disk and `.venv` is somewhere the walk never
reaches. Two defects lived in the gap between that and a real installation, and
both were found by hand rather than by anything here:

**`governova enforce .` scanned the user's dependencies.** A directory argument
was expanded with a bare `rglob("*")` that never consulted `SKIP_DIRS`. Measured
against a freshly installed wheel in an empty project: **51 blocking findings,
every one from inside `site-packages`**. The exclusions existed and were only
applied on the *other* branch of that function — the one CI uses, because CI
never passes a path. So the CI path was right, the human path was wrong, and
nothing noticed.

**No installed user could ever be issued a Governova Score.** The constitutional
coverage factor looked for `root / "compiled" / "constitution.json"`, a path that
exists only in a Governova checkout, so it returned "no compiled index" for every
adopter. `ADR-012` names that factor as the one that reaches quorum, so the
headline number of the product was structurally unobtainable for every user who
was not running from source.

These tests use the resolver and the walk directly rather than building a wheel —
a build in the unit suite would be minutes per run. `test_release.py` covers what
the wheel carries; this covers what the code does when the checkout is absent.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from governova_checks import DEFAULT_IGNORES, scan_paths
from governova_compile.writer import (
    BUNDLED_INDEX,
    CONSTITUTION_ENV_VAR,
    resolve_index_path,
)
from governova_enforce.__main__ import _candidate_files, _not_ignored


def _project(root: Path) -> None:
    """A small project laid out the way a real one is, dependencies and all."""
    (root / "src").mkdir(parents=True, exist_ok=True)
    (root / "src" / "auth.ts").write_text(
        "localStorage.setItem('access_token', token);\n", encoding="utf-8"
    )

    # The directories an adopter has and never wrote.
    for vendored in (
        root / ".venv" / "Lib" / "site-packages" / "somedep",
        root / "node_modules" / "leftpad",
        root / "dist",
    ):
        vendored.mkdir(parents=True, exist_ok=True)
        (vendored / "index.js").write_text(
            "localStorage.setItem('access_token', stolen);\n", encoding="utf-8"
        )


# ─── `governova enforce .` ──────────────────────────────────────────────────


def test_a_directory_argument_does_not_reach_into_dependencies(tmp_path) -> None:
    """The first command a new adopter types, and what it must not report.

    Every vendored file below contains a real violation. Reporting them is not a
    false positive in the narrow sense — the line really is there — and that is
    exactly why this is worse than a bad regex. The findings are true and
    unactionable, and the reader cannot edit any of them.
    """
    _project(tmp_path)

    candidates = _candidate_files([tmp_path], "main", tmp_path)
    reached = {path.relative_to(tmp_path).as_posix() for path in candidates}

    assert "src/auth.ts" in reached
    for vendored in (".venv", "node_modules", "dist"):
        assert not any(part.startswith(vendored) for part in reached), (
            f"the walk reached into {vendored}: {sorted(reached)}"
        )


def test_the_project_own_violation_is_still_reported(tmp_path) -> None:
    """The fix skips what nobody wrote. It does not soften the gate."""
    _project(tmp_path)

    scannable = _not_ignored(_candidate_files([tmp_path], "main", tmp_path), tmp_path, DEFAULT_IGNORES)
    findings = scan_paths(scannable)

    assert [f.anti_pattern for f in findings] == ["AP-S3.14a"], findings
    assert Path(findings[0].file).name == "auth.ts"


def test_a_file_named_explicitly_is_honoured_wherever_it_lives(tmp_path) -> None:
    """Naming a file is a decision; naming a directory is not a decision about
    everything vendored inside it."""
    _project(tmp_path)
    inside = tmp_path / "node_modules" / "leftpad" / "index.js"

    assert _candidate_files([inside], "main", tmp_path) == [inside]


def test_generated_output_beside_its_source_is_skipped_too(tmp_path) -> None:
    """A bundle inherits its directory, so `SKIP_DIRS` cannot reach it."""
    _project(tmp_path)
    (tmp_path / "src" / "app.min.js").write_text(
        "localStorage.setItem('access_token', t);\n", encoding="utf-8"
    )

    reached = {p.name for p in _candidate_files([tmp_path], "main", tmp_path)}
    assert "auth.ts" in reached
    assert "app.min.js" not in reached


# ─── The score an adopter can actually be issued ────────────────────────────


@pytest.mark.skipif(
    not BUNDLED_INDEX.is_file(),
    reason="the bundled index is written at wheel-build time and is absent from a checkout",
)
def test_the_constitution_resolves_with_no_checkout_in_sight(tmp_path) -> None:
    """`resolve_index_path` falls through to the copy bundled in the package.

    Skipped in a source tree, where `BUNDLED_INDEX` does not exist yet — the
    hatch hook writes it into the wheel. That is worth knowing on its own: the
    fallback every adopter depends on is exercised by nothing in this suite,
    which is part of why the defects below survived.
    """
    assert resolve_index_path(start=tmp_path).is_file()


def test_the_coverage_factor_no_longer_needs_a_checkout(tmp_path, monkeypatch) -> None:
    """The factor `ADR-012` names as the one that reaches quorum.

    While it looked for a repo-relative path it returned `None` for every
    installed user, which put every installed user permanently below quorum — so
    the product's headline number could never be issued to anyone.

    The environment override stands in for the bundled index here, which
    isolates the defect from where the file happens to live: `tmp_path` has no
    `compiled/` directory and no checkout above it, exactly like an adopter's
    project, and the factor must still be assessed.
    """
    from governova_compile.discovery import resolve_repo_root
    from governova_score.compute import _constitutional_coverage

    _project(tmp_path)
    # An adopter declares this once, via `governova onboard`. Without it the
    # factor is unassessed by design — an undeclared project is never assumed
    # compliant — so it has to be present for this test to be about the index.
    (tmp_path / "governance").mkdir(exist_ok=True)
    (tmp_path / "governance" / "project.toml").write_text(
        '[project]\nname = "demo"\nstacks = ["python"]\nphase = 1\n',
        encoding="utf-8",
    )
    monkeypatch.setenv(
        CONSTITUTION_ENV_VAR,
        str(Path(resolve_repo_root()) / "compiled" / "constitution.json"),
    )

    factor = _constitutional_coverage(tmp_path)
    assert factor.assessed, factor.detail
    assert "no compiled index" not in factor.detail
    assert "no constitution index found" not in factor.detail


def test_the_factor_says_so_when_no_index_exists_anywhere(tmp_path, monkeypatch) -> None:
    """The other half: unresolvable is reported, never assumed compliant.

    Without this the fix could have been "return 100 when you cannot tell",
    which is the failure the whole verdict discipline exists to prevent.
    """
    from governova_score.compute import _constitutional_coverage

    monkeypatch.delenv(CONSTITUTION_ENV_VAR, raising=False)
    monkeypatch.setattr("governova_compile.writer.BUNDLED_INDEX", tmp_path / "absent.json")

    factor = _constitutional_coverage(tmp_path)
    assert not factor.assessed
    assert factor.score is None


def test_no_surface_hard_codes_the_checkout_relative_index() -> None:
    """The mechanism, asserted across every surface rather than the one that broke.

    Six modules spelled `root / "compiled" / "constitution.json"` while
    `resolve_index_path` existed to answer exactly that question, and each
    degraded differently once installed — no score, no dashboard, no board
    report, no guardian, no handoff. Fixing only the score would have left five.
    """
    from governova_compile.discovery import resolve_repo_root

    scripts = Path(resolve_repo_root()) / "scripts"
    offenders: list[str] = []
    for path in scripts.rglob("*.py"):
        if "tests" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for line in text.splitlines():
            if 'compiled" / "constitution.json"' in line and not line.lstrip().startswith("#"):
                offenders.append(f"{path.relative_to(scripts).as_posix()}: {line.strip()}")

    # `governova_validate` is the one legitimate holdout: it validates a *source
    # tree's* freshly compiled index, so the checkout-relative path is its
    # subject rather than a shortcut. It takes an explicit override first.
    offenders = [o for o in offenders if not o.startswith("governova_validate/")]
    assert not offenders, "these surfaces cannot run from an installed wheel:\n  " + "\n  ".join(
        offenders
    )


def test_the_environment_override_still_wins(tmp_path, monkeypatch) -> None:
    """`GOVERNOVA_CONSTITUTION` lets an organisation govern with its own corpus.

    Routing the surfaces through the resolver is what makes that reach them; it
    was previously honoured by some commands and silently ignored by the rest,
    so an organisation pointing Governova at its own amended constitution got
    its corpus for `enforce` and ours for `govscore`.
    """
    from governova_compile.discovery import resolve_repo_root

    index = Path(resolve_repo_root()) / "compiled" / "constitution.json"
    monkeypatch.setenv(CONSTITUTION_ENV_VAR, str(index))
    assert resolve_index_path(start=tmp_path) == index

    monkeypatch.setenv(CONSTITUTION_ENV_VAR, str(tmp_path / "nope.json"))
    with pytest.raises(FileNotFoundError):
        resolve_index_path(start=tmp_path)


@pytest.mark.skipif(
    os.environ.get(CONSTITUTION_ENV_VAR) is not None,
    reason="the override is set in this environment, which is what the test removes",
)
def test_a_bundled_index_is_the_last_resort_not_the_first(tmp_path) -> None:
    """A checkout's index still wins, so CI governs with the branch under review.

    Without this ordering, a developer's installed copy would quietly outrank
    the corpus they are editing.
    """
    from governova_compile.discovery import resolve_repo_root

    inside = Path(resolve_repo_root()) / "scripts"
    assert resolve_index_path(start=inside).is_relative_to(Path(resolve_repo_root()))
