"""Tests for the core subset — what a free wheel is entitled to carry.

`ADR-011` §1 licenses the corpus and leaves the engine MIT. The boundary is
*entitlement to data*: which file goes in a wheel. Nothing here gates executing
code, and `ADR-010` §5.1's prohibitions on a licence server, machine-ID binding
and phoning home are untouched.

The failure this file exists to prevent is silent over-delivery. A wheel carrying
the full corpus installs cleanly, works perfectly, and gives the product away —
there is no symptom to notice from the outside.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from governova_compile.core_subset import (
    CoreManifest,
    core_index,
    load_manifest,
    unknown_constitutions,
)
from governova_compile.discovery import resolve_repo_root
from governova_compile.schema import CompiledIndex
from governova_compile.writer import CORE_INDEX_NAME, load_index


def _repo_index() -> CompiledIndex:
    return load_index(resolve_repo_root() / "compiled" / "constitution.json")


def _manifest() -> CoreManifest:
    return load_manifest(resolve_repo_root())


# ─── The manifest is data, and it is honoured ────────────────────────────────


def test_the_boundary_is_declared_as_data_not_as_code() -> None:
    """`ADR-011` calls the boundary a judgement. A judgement belongs in a file.

    If this lived in a build script, what the free tier receives would be a
    property of whichever machine ran the build rather than something reviewable
    in a diff.
    """
    manifest = _manifest()
    assert manifest.constitutions
    assert manifest.basis, "the manifest must record why these and not others"


def test_the_core_carries_whole_constitutions() -> None:
    """A subset assembled standard by standard breaks cross-references.

    A free tier whose standards cite standards it does not carry teaches an
    adopter that the product is broken rather than that it is partial.
    """
    index = _repo_index()
    manifest = _manifest()
    subset = core_index(index, manifest)

    by_id = {c.id.upper(): c for c in index.constitutions}
    for constitution in subset.constitutions:
        full = by_id[constitution.id.upper()]
        assert len(constitution.standards) == len(full.standards)


def test_the_core_is_a_strict_subset_of_the_corpus() -> None:
    index = _repo_index()
    subset = core_index(index, _manifest())
    full_ids = {s.id for c in index.constitutions for s in c.standards}
    core_ids = {s.id for c in subset.constitutions for s in c.standards}
    assert core_ids < full_ids


def test_domain_packs_are_never_free() -> None:
    """`ADR-011` §1 lists them beside the full corpus as subscription content."""
    index = _repo_index()
    assert index.domains, "this test is meaningless if the corpus carries no domains"
    subset = core_index(index, _manifest())
    assert subset.domains == []


def test_the_framework_vocabulary_travels_with_the_core() -> None:
    """The primitives are definitions, not law.

    Without them the carried standards cannot be read, so withholding them would
    charge for the dictionary rather than for the corpus.
    """
    subset = core_index(_repo_index(), _manifest())
    assert subset.framework


def test_implementation_guides_follow_their_constitution() -> None:
    """A guide for a constitution the subset lacks is advice about absent law."""
    index = _repo_index()
    manifest = _manifest()
    subset = core_index(index, manifest)
    carried = {c.id.upper() for c in subset.constitutions}
    assert all(i.binds_constitution.upper() in carried for i in subset.implementations)


# ─── The failure that has no symptom ─────────────────────────────────────────


def test_a_typo_in_the_manifest_is_caught_rather_than_silently_shrinking_the_tier() -> None:
    """A misspelled constitution id would hand over less than anyone chose.

    The wheel would still build, install and govern — with fewer standards. That
    is the shape of failure this whole mechanism has to be loud about.
    """
    index = _repo_index()
    manifest = CoreManifest(constitutions=("C01", "C99"))
    assert unknown_constitutions(index, manifest) == ("C99",)


def test_a_correct_manifest_names_nothing_unknown() -> None:
    assert unknown_constitutions(_repo_index(), _manifest()) == ()


def test_the_committed_core_index_matches_the_manifest() -> None:
    """The published boundary and the declared boundary must be the same thing.

    `compiled/constitution.core.json` is what the wheel bundles. If it drifted
    from the manifest, the file in the wheel would be the real boundary and the
    manifest would be documentation of a decision nobody implemented.
    """
    root = resolve_repo_root()
    committed = load_index(root / "compiled" / CORE_INDEX_NAME)
    expected = {c.upper() for c in _manifest().constitutions}
    assert {c.id.upper() for c in committed.constitutions} == expected
    assert committed.domains == []


def test_the_committed_core_index_is_smaller_than_the_full_one() -> None:
    """The assertion the release gate makes, made here so it fails earlier."""
    root = resolve_repo_root()
    full = load_index(root / "compiled" / "constitution.json")
    core = load_index(root / "compiled" / CORE_INDEX_NAME)
    full_count = sum(len(c.standards) for c in full.constitutions)
    core_count = sum(len(c.standards) for c in core.constitutions)
    assert 0 < core_count < full_count


# ─── Absent manifest is not an error ─────────────────────────────────────────


def test_a_repository_with_no_manifest_has_no_core_index(tmp_path) -> None:
    """A consumer compiling their own amended corpus has no boundary to honour.

    Demanding a manifest would make `governova compile` fail in every repository
    but this one, which would be a licensing mechanism breaking other people's
    builds — exactly what `ADR-010` §5 forbids in spirit.
    """
    with pytest.raises(FileNotFoundError):
        load_manifest(tmp_path)


def test_write_index_skips_the_core_when_no_manifest_exists(tmp_path) -> None:
    from governova_compile.writer import write_index

    index = CompiledIndex(compiled_at=datetime(2026, 8, 21, tzinfo=UTC), checksum="")
    out = tmp_path / "compiled"
    written = write_index(index, out)
    assert "core" not in written
    assert not (out / CORE_INDEX_NAME).exists()
