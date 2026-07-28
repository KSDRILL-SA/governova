"""Unit tests for Layer 4 — domain constitution parsing, identity, and integrity."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest
from governova_compile.compiler import compile_index
from governova_compile.discovery import DOMAIN_BY_SLUG, DOMAIN_REGISTRY, find_domain_constitutions
from governova_compile.parsers import parse_domain_constitution
from governova_compile.schema import (
    AntiPattern,
    CompiledIndex,
    Constitution,
    DocumentHeader,
    Priority,
    Reference,
    Standard,
)
from governova_validate.checks import check_anti_patterns, check_domain_extensions, check_references
from pydantic import ValidationError

DOMAIN_DOC = """\
# Test Domain Constitution

| Attribute | Value |
|-----------|-------|
| **Document** | Test Domain Constitution |
| **Status** | ACTIVE |

### D-FINTECH.1 — Amounts Are Exact

| Attribute       | Value |
|-----------------|-------|
| **ID**          | D-FINTECH.1 |
| **Priority**    | Critical |
| **Applies To**  | All Stacks |
| **Enforced By** | CI · Code Review |

**Extends:**
`S5.28` (decimal for money), `S1.67` (named constants)

**Standard:**
Monetary amounts are exact decimals carrying a currency code.

**Rationale:**
Binary floating point cannot represent decimal fractions exactly.

**Anti-Patterns:**
- `AP-D-FINTECH.1a` — An amount stored as a float.
- `AP-D-FINTECH.1b` — An amount stored without a currency code.

### D-FINTECH.2 — Movement Is Idempotent

| Attribute       | Value |
|-----------------|-------|
| **ID**          | D-FINTECH.2 |
| **Priority**    | Critical |
| **Applies To**  | All Stacks |

**Extends:**
`S5.15`

**Standard:**
Value movement accepts a caller-supplied idempotency key.

**Rationale:**
Every layer between a caller and a ledger retries.

**Anti-Patterns:**
- `AP-D-FINTECH.2a` — A money-moving endpoint with no idempotency key.
"""


def _parse(text: str = DOMAIN_DOC) -> Constitution:
    return parse_domain_constitution(
        text,
        entry_id="D-FINTECH",
        name="Financial Technology",
        slug="fintech",
        regulatory_basis=["PCI-DSS"],
        reference_systems=["FundsLink Academy"],
        path="constitution/domains/fintech/doc.md",
    )


def _header() -> DocumentHeader:
    return DocumentHeader(document="Test")


def _domain(*standards: Standard, domain_id: str = "D-SAAS", slug: str = "saas") -> Constitution:
    return Constitution(
        id=domain_id,
        number=99,
        name="SaaS",
        header=_header(),
        path="p",
        slug=slug,
        standards=list(standards),
    )


def _index(*domains: Constitution) -> CompiledIndex:
    return CompiledIndex(
        compiled_at=datetime(2026, 7, 28, tzinfo=UTC), checksum="x", domains=list(domains)
    )


def _standard(sid: str, constitution_id: str, **kwargs: object) -> Standard:
    defaults: dict[str, object] = {
        "title": "T",
        "priority": Priority.STANDARD,
        "applies_to": "All",
        "statement": "s",
        "rationale": "r",
        "source_path": "p",
        "source_line": 1,
    }
    defaults.update(kwargs)
    return Standard(id=sid, constitution_id=constitution_id, **defaults)  # type: ignore[arg-type]


# ─── Parsing ─────────────────────────────────────────────────────────────────


def test_domain_standards_are_parsed_with_domain_ids() -> None:
    domain = _parse()
    assert [s.id for s in domain.standards] == ["D-FINTECH.1", "D-FINTECH.2"]
    assert all(s.constitution_id == "D-FINTECH" for s in domain.standards)


def test_domain_identity_comes_from_the_registry_not_the_filename() -> None:
    domain = _parse()
    assert domain.id == "D-FINTECH"
    assert domain.slug == "fintech"
    assert domain.name == "Financial Technology"
    assert domain.regulatory_basis == ["PCI-DSS"]
    assert domain.reference_systems == ["FundsLink Academy"]


def test_domains_have_no_phase_or_hierarchy_rank() -> None:
    """A domain extends the whole core, so it does not sit at one point in it."""
    domain = _parse()
    assert domain.phase is None
    assert domain.hierarchy_rank is None
    assert all(s.phase is None for s in domain.standards)


def test_extends_block_becomes_core_dependencies() -> None:
    first = _parse().standards[0]
    assert [r.standard_id for r in first.depends_on] == ["S5.28", "S1.67"]
    assert first.depends_on[0].description == "decimal for money"


def test_domain_anti_patterns_are_parsed_and_attributed() -> None:
    first = _parse().standards[0]
    assert [ap.id for ap in first.anti_patterns] == ["AP-D-FINTECH.1a", "AP-D-FINTECH.1b"]
    assert all(ap.parent_standard_id == "D-FINTECH.1" for ap in first.anti_patterns)


def test_standards_sort_numerically_not_lexically() -> None:
    doc = DOMAIN_DOC + "\n### D-FINTECH.10 — Later\n\n**Standard:**\nLater.\n"
    assert [s.id for s in _parse(doc).standards][-1] == "D-FINTECH.10"


def test_a_foreign_namespace_heading_is_not_claimed() -> None:
    """A D-GOVTECH heading inside the fintech document is not silently absorbed."""
    doc = DOMAIN_DOC + "\n### D-GOVTECH.1 — Not Ours\n\n**Standard:**\nx.\n"
    assert "D-GOVTECH.1" not in [s.id for s in _parse(doc).standards]


def test_core_standard_headings_are_ignored_in_a_domain_document() -> None:
    doc = DOMAIN_DOC + "\n### S1.1 — Core Standard\n\n**Standard:**\nx.\n"
    assert all(s.id.startswith("D-FINTECH.") for s in _parse(doc).standards)


# ─── Discovery ───────────────────────────────────────────────────────────────


def test_every_registry_domain_has_a_unique_identity() -> None:
    ids = [d.id for d in DOMAIN_REGISTRY]
    slugs = [d.slug for d in DOMAIN_REGISTRY]
    assert len(set(ids)) == len(ids), "domain IDs must be unique — no C99-style collision"
    assert len(set(slugs)) == len(slugs)


def test_registry_ids_match_the_domain_id_format() -> None:
    for entry in DOMAIN_REGISTRY:
        assert entry.id.startswith("D-") and entry.id.isupper()


def test_discovery_skips_readmes_and_unregistered_folders(tmp_path: Path) -> None:
    domains = tmp_path / "constitution" / "domains"
    (domains / "fintech").mkdir(parents=True)
    (domains / "fintech" / "README.md").write_text("stub", encoding="utf-8")
    (domains / "fintech" / "D-FINTECH-domain-constitution.md").write_text(
        DOMAIN_DOC, encoding="utf-8"
    )
    (domains / "not-a-domain").mkdir()
    (domains / "not-a-domain" / "invented.md").write_text(DOMAIN_DOC, encoding="utf-8")

    found = find_domain_constitutions(tmp_path)
    assert [(e.slug, p.name) for e, p in found] == [
        ("fintech", "D-FINTECH-domain-constitution.md")
    ]


def test_a_declared_but_unwritten_domain_compiles_to_nothing(tmp_path: Path) -> None:
    domains = tmp_path / "constitution" / "domains" / "iot"
    domains.mkdir(parents=True)
    (domains / "README.md").write_text("stub", encoding="utf-8")
    assert find_domain_constitutions(tmp_path) == []


# ─── Integrity checks ────────────────────────────────────────────────────────


def test_domain_standard_extending_nothing_is_flagged() -> None:
    index = _index(_domain(_standard("D-SAAS.1", "D-SAAS")))
    assert "domain-extends-nothing" in {i.code for i in check_domain_extensions(index)}


def test_domain_standard_in_a_foreign_namespace_is_flagged() -> None:
    index = _index(_domain(_standard("D-FINTECH.1", "D-SAAS")))
    issues = [i for i in check_domain_extensions(index) if i.code == "domain-namespace-mismatch"]
    assert len(issues) == 1
    assert issues[0].severity.value == "SEV1"


def test_domain_reference_to_a_nonexistent_core_standard_is_flagged() -> None:
    index = _index(
        _domain(_standard("D-SAAS.1", "D-SAAS", depends_on=[Reference(standard_id="S99.999")]))
    )
    assert any(i.code == "orphan-reference" for i in check_references(index))


def test_domain_anti_pattern_parentage_is_checked() -> None:
    index = _index(
        _domain(
            _standard(
                "D-SAAS.1",
                "D-SAAS",
                anti_patterns=[
                    AntiPattern(
                        id="AP-D-SAAS.2a",
                        description="wrong parent",
                        parent_standard_id="D-SAAS.1",
                    )
                ],
            )
        )
    )
    assert any(i.code == "anti-pattern-mismatch" for i in check_anti_patterns(index))


# ─── Schema boundaries ───────────────────────────────────────────────────────


@pytest.mark.parametrize("bad_id", ["d-fintech.1", "D-FINTECH", "D-FINTECH.", "DFINTECH.1"])
def test_malformed_domain_standard_ids_are_rejected(bad_id: str) -> None:
    with pytest.raises(ValidationError):
        _standard(bad_id, "D-FINTECH")


def test_core_and_domain_ids_both_remain_valid() -> None:
    assert _standard("S1.1", "C01").id == "S1.1"
    assert _standard("D-FINTECH.1", "D-FINTECH").id == "D-FINTECH.1"


# ─── Live corpus ─────────────────────────────────────────────────────────────


def test_the_repository_compiles_its_domains() -> None:
    """Guards against a regression that silently drops Layer 4 from the index."""
    index = compile_index()
    assert index.domains, "no domain compiled — Layer 4 regressed to empty"
    assert index.integrity.domain_standards_extracted == sum(
        len(d.standards) for d in index.domains
    )
    for domain in index.domains:
        assert domain.standards, f"{domain.id} compiled with zero standards"
        for std in domain.standards:
            assert std.id.startswith(f"{domain.id}.")
            assert DOMAIN_BY_SLUG[domain.slug or ""].id == domain.id
