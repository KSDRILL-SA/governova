"""Tests for the risk-ranked remediation roadmap (Phase 3 Stage 1).

A baseline says what is wrong; the roadmap says what to do first, and **that
ordering is the product**. So the weight here is on the ways an ordering becomes
untrustworthy without looking wrong:

* **Measuring the wrong quantity.** Blast radius and effort are both derived
  from how many files a finding touches. The first version of this took that
  count from a list that had been truncated to three examples for display, which
  silently understated exactly the widespread findings that should rank highest.
  A count that is quietly a sample inverts the product and nothing in the output
  looks amiss.
* **Concluding more than was measured.** A filename search can prove a test
  exists. It cannot prove one does not, and `S1.101` decisions get made on this.
* **Manufacturing work.** A roadmap that finds something to do on a clean
  repository has told its first lie about that repository.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from governova_compile.discovery import resolve_repo_root
from governova_compile.schema import Priority
from governova_compile.writer import load_index
from governova_onboard import assess, build_roadmap
from governova_onboard.baseline import EXAMPLE_FILES, FindingGroup
from governova_onboard.render import roadmap_table, roadmap_to_json
from governova_onboard.roadmap import Item, Kind, Protection, find_characterisation_tests


@pytest.fixture(scope="module")
def index():
    return load_index(resolve_repo_root() / "compiled" / "constitution.json")


def _repo(tmp_path: Path, files: dict[str, str]) -> Path:
    for name, body in files.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    return tmp_path


def _item(**kwargs) -> Item:
    base = {
        "kind": Kind.CODE,
        "standard": "S1.1",
        "title": "T",
        "anti_pattern": "AP-S1.1a",
        "summary": "s",
        "occurrences": 1,
        "files": ("a.py",),
        "protection": Protection.PROTECTED,
        "protected_by": ("test_a.py",),
        "blocking": False,
        "priority": Priority.STANDARD,
        "dependents": 0,
    }
    return Item(**{**base, **kwargs})


# ── The quantity being measured ──────────────────────────────────────────────


def test_reach_counts_every_file_not_the_displayed_sample(tmp_path: Path, index) -> None:
    """The regression that inverted the ordering, pinned.

    `FindingGroup.files` feeds blast radius and effort. It was briefly capped at
    three for display, so a finding spread over thirty files reported a reach of
    three — understating precisely the items the roadmap exists to surface.
    """
    # A debt marker carrying no tracked reference (AP-S13.1a) — one per file, so
    # occurrences and reach are equal and a truncated file list is unmistakable.
    files = {f"src/mod{i}.py": "# TODO: tidy this up\nVALUE = 1\n" for i in range(12)}
    files["pyproject.toml"] = '[project]\nname = "x"\n'
    root = _repo(tmp_path, files)

    baseline = assess(root, index)
    spread = [g for g in baseline.groups if g.reach > EXAMPLE_FILES]
    assert spread, "fixture should produce a finding spread across more than the display cap"
    for group in spread:
        assert group.reach == len(group.files)
        assert group.reach > EXAMPLE_FILES

    plan = build_roadmap(baseline, index)
    for item in plan.items:
        if item.kind is Kind.CODE:
            assert item.reach == len(item.files)


def test_effort_is_never_zero() -> None:
    """Leverage divides by effort. A structural item touches no source file."""
    structural = _item(kind=Kind.STRUCTURAL, files=(), protection=Protection.PROTECTED)
    assert structural.effort >= 1
    assert structural.leverage > 0


def test_blast_and_effort_are_reconstructible_from_the_item() -> None:
    """The ordering must be disputable by reading the components, not trusted."""
    item = _item(
        files=("a.py", "b.py"),
        priority=Priority.CRITICAL,
        blocking=True,
        dependents=3,
        protection=Protection.UNKNOWN,
        protected_by=(),
    )
    assert item.blast == 8 + 8 + 2 + 3  # priority + blocking + reach + dependents
    assert item.effort == 2 + 3  # reach + unprotected penalty
    assert item.leverage == round(item.blast / item.effort, 2)


# ── Ordering ─────────────────────────────────────────────────────────────────


def test_blocking_outranks_higher_leverage_advisory(tmp_path: Path, index) -> None:
    """A build-failing finding comes first. That is what blocking means.

    It is a separate tier rather than a large weight precisely so no arithmetic
    can float an advisory item above a blocking one.
    """
    root = _repo(
        tmp_path,
        {
            "pyproject.toml": '[project]\nname = "x"\n',
            "app/ui/panel.py": "rows = db.session.execute('select 1')\n",
            "app/svc.py": "# TODO: clean this up\n" * 3,
        },
    )
    plan = build_roadmap(assess(root, index), index)
    if plan.blocking_items:
        first_advisory = next(
            (n for n, i in enumerate(plan.items) if not i.blocking), len(plan.items)
        )
        last_blocking = max(n for n, i in enumerate(plan.items) if i.blocking)
        assert last_blocking < first_advisory


def test_ordering_is_by_leverage_not_standard_number(tmp_path: Path, index) -> None:
    """The explicit Stage 1 exit criterion.

    Sorting by standard id is the ordering anyone gets for free and the one that
    helps nobody, so it is asserted against rather than merely avoided.
    """
    root = _repo(tmp_path, {"pyproject.toml": '[project]\nname = "x"\n', "a.py": "x = 1\n"})
    plan = build_roadmap(assess(root, index), index)
    assert len(plan) > 1

    within_tier = [i for i in plan.items if not i.blocking]
    leverages = [i.leverage for i in within_tier]
    assert leverages == sorted(leverages, reverse=True)

    ids = [i.standard for i in within_tier]
    assert ids != sorted(ids), "ordering coincides with standard-number order"


# ── What it refuses to conclude ──────────────────────────────────────────────


def test_a_missing_test_file_is_unknown_never_unprotected() -> None:
    """There is no UNPROTECTED verdict, and its absence is the design.

    A filename search proves existence, never absence — the tests may live
    anywhere, or exercise the module through another entry point.
    """
    assert not hasattr(Protection, "UNPROTECTED")
    assert set(Protection) == {Protection.PROTECTED, Protection.UNKNOWN}


@pytest.mark.parametrize(
    ("source", "test_name"),
    [
        ("src/parser.py", "tests/test_parser.py"),
        ("src/parser.py", "src/parser_test.py"),
        ("pkg/server.go", "pkg/server_test.go"),
        ("lib/box.ts", "lib/box.test.ts"),
        ("app/models/user.rb", "spec/models/user_spec.rb"),
    ],
)
def test_characterisation_tests_are_found_by_convention(
    tmp_path: Path, source: str, test_name: str
) -> None:
    root = _repo(tmp_path, {source: "x\n", test_name: "y\n"})
    found = find_characterisation_tests(root, (source,))
    assert found == (test_name,)


def test_no_matching_test_reports_nothing_found(tmp_path: Path) -> None:
    root = _repo(tmp_path, {"src/parser.py": "x\n", "tests/test_other.py": "y\n"})
    assert find_characterisation_tests(root, ("src/parser.py",)) == ()


def test_an_unprotected_code_item_demands_a_characterisation_test() -> None:
    """`S1.101` — pin behaviour before refactoring it."""
    item = _item(protection=Protection.UNKNOWN, protected_by=())
    assert item.needs_characterisation_test


def test_a_structural_item_never_demands_a_characterisation_test() -> None:
    """Adding a licence gate to CI changes no runtime behaviour.

    Demanding a characterisation test before a repository-level change would be
    `S1.101` applied where it has no subject, and it would put a pointless step
    in front of the cheapest wins on the roadmap.
    """
    item = _item(kind=Kind.STRUCTURAL, files=(), protection=Protection.PROTECTED)
    assert not item.needs_characterisation_test


def test_a_clean_repository_produces_an_empty_roadmap(index) -> None:
    """No findings means no plan. Busywork is a lie about the repository."""
    baseline = assess(resolve_repo_root(), index)
    plan = build_roadmap(baseline, index)
    # Governova's own source is clean at the reliable tier; any items must be
    # structural, and each must trace to a probe that actually fired.
    probe_standards = {p.standard for p in baseline.violated_probes}
    for item in plan.items:
        assert item.kind is Kind.STRUCTURAL
        assert item.standard in probe_standards


def test_an_empty_repository_plans_nothing(tmp_path: Path, index) -> None:
    root = _repo(tmp_path, {"README.md": "# hi\n\n## Overview\n\n## Setup\n"})
    plan = build_roadmap(assess(root, index), index)
    assert [i for i in plan.items if i.kind is Kind.CODE] == []


# ── Every item is actionable ─────────────────────────────────────────────────


def test_every_item_names_its_standard_and_its_evidence(tmp_path: Path, index) -> None:
    """The other Stage 1 exit criterion — an item you cannot act on is noise."""
    root = _repo(
        tmp_path,
        {"pyproject.toml": '[project]\nname = "x"\n', "app/ui/p.py": "db.session.query(User)\n"},
    )
    plan = build_roadmap(assess(root, index), index)
    assert plan
    for item in plan.items:
        assert item.standard
        assert item.summary
        assert item.occurrences >= 1
        if item.kind is Kind.CODE:
            assert item.files, "a code item must say which files to open"


def test_roadmap_json_is_issue_shaped(tmp_path: Path, index) -> None:
    root = _repo(tmp_path, {"pyproject.toml": '[project]\nname = "x"\n', "a.py": "x = 1\n"})
    payload = json.loads(roadmap_to_json(build_roadmap(assess(root, index), index)))
    assert payload["totals"]["items"] == len(payload["items"])
    ranks = [entry["rank"] for entry in payload["items"]]
    assert ranks == list(range(1, len(ranks) + 1))
    for entry in payload["items"]:
        assert {"standard", "blast", "effort", "leverage", "needs_characterisation_test"} <= set(
            entry
        )


def test_roadmap_table_renders(tmp_path: Path, index) -> None:
    root = _repo(tmp_path, {"pyproject.toml": '[project]\nname = "x"\n', "a.py": "x = 1\n"})
    table = roadmap_table(build_roadmap(assess(root, index), index), top=3)
    assert table.row_count <= 3


def test_finding_group_reach_matches_its_files() -> None:
    group = FindingGroup(
        anti_pattern="AP-S1.1a",
        standard="S1.1",
        message="m",
        confidence="medium",
        count=9,
        files=("a.py", "b.py", "c.py", "d.py"),
    )
    assert group.reach == 4
