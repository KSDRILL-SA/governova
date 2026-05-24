"""Integration tests against the real constitutional database."""

from __future__ import annotations

import pytest
from governova_compile.compiler import compile_index
from governova_compile.discovery import CONSTITUTION_REGISTRY, resolve_repo_root
from governova_compile.writer import compute_checksum
from governova_validate.checks import (
    check_hierarchy,
    check_phases,
    check_references,
)
from governova_validate.links import check_links

# The declared per-constitution standard counts from C0 §5.1.
EXPECTED_COUNTS = {
    "C00": 0,
    "C01": 97,
    "C02": 80,
    "C03": 36,
    "C04": 82,
    "C05": 64,
    "C06": 44,
    "C07": 43,
    "C08": 82,
    "C09": 30,
    "C10": 36,
}
EXPECTED_TOTAL = 594


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
    assert compute_checksum(index) == compute_checksum(index)


def test_standard_ids_are_unique(index):
    ids = [s.id for c in index.constitutions for s in c.standards]
    assert len(ids) == len(set(ids))


def test_hierarchy_covers_all_constitutions(index):
    assert set(index.hierarchy) == {c.id for c in index.constitutions}


def test_link_integrity(repo_root):
    issues, _ = check_links(repo_root)
    assert issues == [], f"broken links: {[(i.source_path, i.message) for i in issues]}"
