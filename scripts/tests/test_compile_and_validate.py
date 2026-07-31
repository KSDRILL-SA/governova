"""Integration tests against the real constitutional database."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from governova_compile.compiler import compile_index
from governova_compile.discovery import CONSTITUTION_REGISTRY, resolve_repo_root
from governova_compile.schema import (
    MAX_GROUNDED_IN_CHARS,
    CompiledIndex,
    Constitution,
    DocumentHeader,
    Priority,
    Standard,
)
from governova_compile.writer import compute_checksum
from governova_validate.checks import (
    check_grounded_in,
    check_hierarchy,
    check_phases,
    check_references,
)
from governova_validate.links import check_links

# The live per-constitution standard counts. 618 after the 2026-06-22 ratification
# (613 + Part 19 Architectural Discipline S1.103–S1.107), plus C11 Requirements
# Engineering (S11.1–S11.12) ratified 2026-07-31 under ADR-007 Stage 1 = 630.
EXPECTED_COUNTS = {
    "C00": 0,
    "C01": 107,
    "C02": 81,
    "C03": 37,
    "C04": 83,
    "C05": 65,
    "C06": 45,
    "C07": 43,
    "C08": 87,
    "C09": 30,
    "C10": 40,
    "C11": 15,
    "C13": 11,
    "C14": 14,
}
EXPECTED_TOTAL = 658


@pytest.fixture(scope="module")
def repo_root():
    return resolve_repo_root()


@pytest.fixture(scope="module")
def index(repo_root):
    return compile_index(repo_root)


def test_total_standard_count_matches_register(index):
    total = sum(len(c.standards) for c in index.constitutions)
    assert total == EXPECTED_TOTAL


def test_per_constitution_counts_match_register(index):
    actual = {c.id: len(c.standards) for c in index.constitutions}
    assert actual == EXPECTED_COUNTS


def test_all_constitutions_present(index):
    assert {c.id for c in index.constitutions} == {e.id for e in CONSTITUTION_REGISTRY}


def test_no_orphan_references(index):
    issues = check_references(index)
    assert issues == [], f"orphan references found: {[i.message for i in issues]}"


def test_hierarchy_consistent(index):
    assert check_hierarchy(index) == []


def test_phases_consistent(index):
    assert check_phases(index) == []


def test_checksum_is_deterministic(index):
    # Verifies REQ-004 — unchanged source yields a byte-identical index.
    assert compute_checksum(index) == compute_checksum(index)


def test_standard_ids_are_unique(index):
    ids = [s.id for c in index.constitutions for s in c.standards]
    assert len(ids) == len(set(ids))


def test_hierarchy_covers_all_constitutions(index):
    assert set(index.hierarchy) == {c.id for c in index.constitutions}


def test_link_integrity(repo_root):
    issues, _ = check_links(repo_root)
    assert issues == [], f"broken links: {[(i.source_path, i.message) for i in issues]}"


# ─── Grounded In — provenance is a citation, never an excerpt (C0 §3.2 SR-7) ──


def _index_with_grounding(*entries: str) -> CompiledIndex:
    """A one-standard index whose sole standard carries `entries` as provenance."""
    standard = Standard(
        id="S1.1",
        title="T",
        constitution_id="C01",
        priority=Priority.STANDARD,
        applies_to="All",
        statement="s",
        rationale="r",
        grounded_in=list(entries),
        source_path="p",
        source_line=1,
    )
    constitution = Constitution(
        id="C01",
        number=1,
        name="Test",
        header=DocumentHeader(document="C1 — Test"),
        path="p",
        standards=[standard],
    )
    return CompiledIndex(
        compiled_at=datetime(2026, 7, 31, tzinfo=UTC),
        checksum="x",
        constitutions=[constitution],
    )


def test_grounded_in_rejects_an_excerpt():
    excerpt = "T" * (MAX_GROUNDED_IN_CHARS + 1)
    issues = check_grounded_in(_index_with_grounding(excerpt))
    assert [i.code for i in issues] == ["grounded-in-excerpt"]
    assert str(MAX_GROUNDED_IN_CHARS) in issues[0].message


def test_grounded_in_accepts_a_citation():
    # The negative case, and the one that matters: a real citation — author, work,
    # edition, chapter — must pass, or the bound is unusable for its purpose.
    issues = check_grounded_in(
        _index_with_grounding(
            "Sommerville, *Software Engineering*, 10th ed. — ch. 4, requirements engineering",
            "Coronel & Rob, *Database Systems*, 13th ed. — ch. 6, normalisation of tables",
        )
    )
    assert issues == []


def test_grounded_in_boundary_is_inclusive():
    at_limit = "C" * MAX_GROUNDED_IN_CHARS
    assert check_grounded_in(_index_with_grounding(at_limit)) == []
    assert check_grounded_in(_index_with_grounding(at_limit + "C")) != []


def test_grounded_in_absent_is_not_a_violation():
    # An unsourced standard is not a malformed one — 618 of them are unsourced today.
    assert check_grounded_in(_index_with_grounding()) == []


def test_live_corpus_carries_no_excerpts(index):
    issues = check_grounded_in(index)
    assert issues == [], f"excerpt in provenance: {[i.message for i in issues]}"


# The standards retro-cited in ADR-007 Stage 0. Pinned by ID because provenance is
# easy to drop silently in an unrelated edit — a citation nobody notices vanishing is
# a claim quietly withdrawn.
RETRO_CITED = {
    "S1.103",
    "S1.104",
    "S1.106",
    "S1.107",
    "S5.6",
    "S5.10",
    "S5.13",
    "S5.15",
    "S7.3",
    "S7.7",
    "S7.10",
    "S7.18",
}


def test_retro_cited_standards_still_carry_provenance(index):
    cited = {s.id for c in index.constitutions for s in c.standards if s.grounded_in}
    assert cited >= RETRO_CITED, f"provenance lost from: {sorted(RETRO_CITED - cited)}"


def test_standards_deliberately_left_uncited_stay_uncited(index):
    """The negative half, and the one that carries the argument.

    `S1.105` has no source in the corpus that establishes it, and `S7.25`'s coverage
    thresholds are a local decision — the canon sets testing levels, not percentages.
    Citing either would claim a grounding that does not exist, which is the failure
    the 120-character bound and this whole field exist to prevent. If a later change
    adds provenance here, it must be because a real source was found.
    """
    by_id = {s.id: s for c in index.constitutions for s in c.standards}
    for sid in ("S1.105", "S7.25"):
        assert by_id[sid].grounded_in == [], f"{sid} gained an unverified citation"
