"""Pydantic v2 schema — the single source of truth for the compiled constitutional index.

Every other Governova surface (CLI, MCP server, engine, IDE extension, dashboard)
derives its types from this schema.

Two type-generation paths flow from this module:
    1. JSON Schema (draft 2020-12) → `compiled/constitution.schema.json`
    2. TypeScript types via json-schema-to-typescript → `platform/shared/types-ts/`
    3. Python re-exports → `platform/shared/types-py/governova_types/`

Versioning:
    - SCHEMA_VERSION uses semantic versioning
    - Additions to optional fields = minor bump
    - Removed / renamed / type-changed fields = major bump
"""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

SCHEMA_VERSION = "1.3.0"
"""Semantic version of the compiled-index schema. See module docstring."""

MAX_GROUNDED_IN_CHARS = 120
"""The line between a citation and an excerpt.

`Standard.grounded_in` records *where a practice is written down*, not what it
says. Ideas and methods are not copyrightable; expression is. A reference line —
author, work, edition, chapter — fits comfortably inside this bound; a paragraph
of somebody else's prose does not. `governova validate` rejects any entry that
exceeds it, which is what keeps the provenance field a citation index rather than
an unlicensed anthology.
"""


# ─── Enums ───────────────────────────────────────────────────────────────────


class Priority(StrEnum):
    """Standard priority — how important is the standard itself.

    Mirrors C0 §2.3. Distinct from Severity (which classifies incidents).
    """

    CRITICAL = "Critical"
    HIGH = "High"
    STANDARD = "Standard"
    GUIDANCE = "Guidance"


class Severity(StrEnum):
    """Incident / violation severity — how severe is the failure.

    Mirrors `framework/severity-model.md`. Distinct from Priority.
    """

    SEV0 = "SEV0"
    SEV1 = "SEV1"
    SEV2 = "SEV2"
    SEV3 = "SEV3"


class Phase(StrEnum):
    """The four phases per C0 §6."""

    FOUNDATION = "0"
    CORE_ARCHITECTURE = "1"
    QUALITY_RELIABILITY = "2"
    PRODUCT_INTELLIGENCE = "3"


class DocumentStatus(StrEnum):
    """Lifecycle status of a constitutional document."""

    DRAFT = "DRAFT"
    LOCKED = "LOCKED"
    DEPRECATED = "DEPRECATED"


# ─── Identifier types (string aliases with documentation) ────────────────────

StandardId = Annotated[str, Field(pattern=r"^S\d+\.\d+$", examples=["S1.1", "S3.14"])]
"""A core standard ID in `S{C}.{N}` format. C0 §2.2."""

AntiPatternId = Annotated[
    str, Field(pattern=r"^AP-S\d+\.\d+[a-z]$", examples=["AP-S1.1a", "AP-S3.14b"])
]
"""A core anti-pattern ID in `AP-S{C}.{N}{letter}` format. C0 §2.2."""

DomainStandardId = Annotated[
    str, Field(pattern=r"^D-[A-Z][A-Z0-9-]*\.\d+$", examples=["D-FINTECH.1", "D-GOVTECH.12"])
]
"""A Layer 4 domain standard ID in `D-{DOMAIN}.{N}` format. master.md Appendix A."""

DomainAntiPatternId = Annotated[
    str,
    Field(pattern=r"^AP-D-[A-Z][A-Z0-9-]*\.\d+[a-z]$", examples=["AP-D-FINTECH.1a"]),
]
"""A Layer 4 domain anti-pattern ID in `AP-D-{DOMAIN}.{N}{letter}` format."""

# Layer 2 (core) and Layer 4 (domain) standards share one `Standard` model so that
# every downstream consumer — validator, score, bible, dashboard, MCP — iterates
# `(*index.constitutions, *index.domains)` uniformly without branching on type.
# The namespaces stay separate at parse time: a core document only ever yields
# `S{C}.{N}` and a domain document only ever yields `D-{DOMAIN}.{N}`.
AnyStandardId = Annotated[
    str,
    Field(
        pattern=r"^(?:S\d+\.\d+|D-[A-Z][A-Z0-9-]*\.\d+)$",
        examples=["S1.1", "D-FINTECH.1"],
    ),
]
"""Either a core standard ID or a domain standard ID."""

AnyAntiPatternId = Annotated[
    str,
    Field(
        pattern=r"^AP-(?:S\d+\.\d+|D-[A-Z][A-Z0-9-]*\.\d+)[a-z]$",
        examples=["AP-S1.1a", "AP-D-FINTECH.1a"],
    ),
]
"""Either a core anti-pattern ID or a domain anti-pattern ID."""

ImplementationBindingId = Annotated[
    str,
    Field(pattern=r"^S\d+\.\d+/[a-z][a-z0-9_-]*$", examples=["S2.7/fastapi", "S3.14/nextauth"]),
]
"""A stack binding ID in `S{C}.{N}/{stack}` format."""

PracticeId = Annotated[str, Field(pattern=r"^P\d+\.\d+$", examples=["P2.1", "P3.14"])]
"""A practice ID in `P{C}.{N}` format. C0 §2.1 — lives in implementation guides only."""

ConstitutionId = Annotated[str, Field(pattern=r"^C\d{2}$", examples=["C00", "C01", "C10"])]
"""A zero-padded core constitution ID. C00, C01, … C10."""

DomainId = Annotated[
    str, Field(pattern=r"^D-[A-Z][A-Z0-9-]*$", examples=["D-FINTECH", "D-GOVTECH"])
]
"""A Layer 4 domain document ID, e.g. `D-FINTECH`."""

AnyConstitutionId = Annotated[
    str,
    Field(pattern=r"^(?:C\d{2}|D-[A-Z][A-Z0-9-]*)$", examples=["C01", "D-FINTECH"]),
]
"""Either a core constitution ID or a domain document ID."""

RunbookId = Annotated[str, Field(pattern=r"^RB-\d{2}$", examples=["RB-01", "RB-08"])]

AdrId = Annotated[str, Field(pattern=r"^ADR-\d{3}$", examples=["ADR-001", "ADR-042"])]


# ─── Building blocks ─────────────────────────────────────────────────────────


class Reference(BaseModel):
    """A reference to another standard, with optional inline description.

    Used in `depends_on` and `cross_references` fields. The description is
    typically the parenthetical hint shown in the source markdown.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    standard_id: AnyStandardId
    description: str | None = Field(
        default=None,
        description="Optional inline description, e.g. the parenthetical in source markdown.",
    )


class AntiPattern(BaseModel):
    """A documented failure mode of a standard."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: AnyAntiPatternId
    description: str = Field(description="What the failure looks like in practice.")
    parent_standard_id: AnyStandardId = Field(
        description="The standard this anti-pattern violates."
    )


class Standard(BaseModel):
    """A governing statement in a constitution.

    Mirrors the canonical block defined in C0 §3.1.
    """

    model_config = ConfigDict(extra="forbid")

    id: AnyStandardId
    title: str
    constitution_id: AnyConstitutionId = Field(
        description="The owning document — a core constitution ('C01') or a domain ('D-FINTECH')."
    )
    priority: Priority
    applies_to: str = Field(
        description="Scope — free-form, e.g. 'Both Stacks', 'Next.js Only', 'All Systems'."
    )
    phase: Phase | None = Field(
        default=None,
        description="The phase the owning constitution belongs to. None for C0.",
    )
    phase_label: str | None = Field(
        default=None, description="Original phase string from source, e.g. 'Phase 0 — Foundation'."
    )
    depends_on: list[Reference] = Field(
        default_factory=list, description="Standards this one cannot function without."
    )
    enforced_by: list[str] = Field(
        default_factory=list,
        description="Enforcement mechanisms, e.g. ['CI', 'ESLint', 'Code Review'].",
    )
    statement: str = Field(description="The standard text — what must be true.")
    rationale: str = Field(
        default="", description="Why this standard exists — production consequence."
    )
    anti_patterns: list[AntiPattern] = Field(default_factory=list)
    cross_references: list[Reference] = Field(default_factory=list)
    grounded_in: list[str] = Field(
        default_factory=list,
        description=(
            "Provenance — where this requirement is established in the engineering "
            "canon. Each entry is a citation (author, work, edition, chapter), never "
            f"an excerpt; entries over {MAX_GROUNDED_IN_CHARS} characters are rejected "
            "by `governova validate`. Empty means unsourced, not unfounded."
        ),
    )
    abbreviated: bool = Field(
        default=False,
        description=(
            "True if the standard was authored in blockquote shorthand "
            "(`> **S{C}.{N}** — ...`) and therefore lacks a full attribute table, "
            "rationale, and dedicated anti-pattern block."
        ),
    )
    source_path: str = Field(description="Repo-relative path to the source markdown file.")
    source_line: int = Field(description="1-indexed line number where the standard heading begins.")


# ─── Documents ───────────────────────────────────────────────────────────────


class DocumentHeader(BaseModel):
    """The identity block at the top of every constitution / implementation guide."""

    model_config = ConfigDict(extra="forbid")

    document: str = Field(description="Full document title, e.g. 'C1 — Engineering Standards'.")
    organisation: str = "KSDRILL SA"
    version: str = "v1.0"
    status: DocumentStatus = DocumentStatus.DRAFT
    locked_date: date | None = None
    next_review: date | None = None
    applies_to: str | None = None
    paired_with: str | None = None


class Constitution(BaseModel):
    """A core constitution document (C00–C10) or a Layer 4 domain extension.

    Domains reuse this model so downstream consumers iterate core and domain
    documents uniformly. A domain is identified by `id` matching `D-{DOMAIN}`,
    carries `slug`, `regulatory_basis`, and `reference_systems`, and has no
    phase or hierarchy rank — it extends the whole core rather than sitting
    at one point in it.
    """

    model_config = ConfigDict(extra="forbid")

    id: AnyConstitutionId
    number: int = Field(ge=0, description="Numeric constitution number (0–99). 99 for domains.")
    name: str
    phase: Phase | None = Field(default=None, description="None for C0 and domains; else 0–3.")
    slug: str | None = Field(
        default=None,
        description="Domain folder slug, e.g. 'fintech'. None for core constitutions.",
    )
    regulatory_basis: list[str] = Field(
        default_factory=list,
        description="Regulations the domain encodes, e.g. ['PCI-DSS', 'FICA']. Domains only.",
    )
    reference_systems: list[str] = Field(
        default_factory=list,
        description="Reference systems that seeded the domain. Domains only.",
    )
    header: DocumentHeader
    path: str = Field(description="Repo-relative path to the source markdown file.")
    hierarchy_rank: int | None = Field(
        default=None,
        ge=1,
        description="Position in C0 §7.1 conflict-resolution hierarchy. 1 = highest authority.",
    )
    binds_implementation: bool = Field(
        default=False, description="True if this constitution has paired stack bindings."
    )
    standards: list[Standard] = Field(default_factory=list)


class ImplementationBinding(BaseModel):
    """How a universal standard is satisfied in a specific stack."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: ImplementationBindingId = Field(description="e.g. 'S2.7/fastapi'.")
    binds_standard: StandardId
    stack: str = Field(description="Stack identifier, e.g. 'fastapi', 'nextjs'.")
    satisfies_by: str = Field(description="How the standard is met in this stack.")
    anti_pattern: AntiPatternId | None = None


class Practice(BaseModel):
    """An operational how-to in an implementation guide. C0 §2.1.

    A practice references the standard(s) it satisfies via inline `S{C}.{N}`
    citations in its section.
    """

    model_config = ConfigDict(extra="forbid")

    id: PracticeId
    title: str
    satisfies_standards: list[StandardId] = Field(
        default_factory=list, description="Standards this practice operationalises."
    )
    source_path: str
    source_line: int


class Implementation(BaseModel):
    """A stack-specific implementation guide for one core constitution.

    Current guides express the implementation layer as Practices (`P{C}.{N}`).
    The `bindings` field supports the `S{C}.{N}/{stack}` format from
    `framework/format-specification.md` for future spec-compliant guides.
    """

    model_config = ConfigDict(extra="forbid")

    stack: str
    binds_constitution: ConstitutionId
    name: str
    header: DocumentHeader
    path: str
    practices: list[Practice] = Field(default_factory=list)
    bindings: list[ImplementationBinding] = Field(default_factory=list)


class FrameworkPrimitive(BaseModel):
    """A Layer 1 framework primitive — universal, stack-agnostic."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(description="Slug, e.g. 'format-specification'.")
    title: str
    path: str
    summary: str = Field(description="One-line description.")


class Runbook(BaseModel):
    """An operational response procedure."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: RunbookId
    name: str
    trigger: str = Field(description="When this runbook is activated.")
    path: str


class ADR(BaseModel):
    """An Architecture Decision Record."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: AdrId
    name: str
    status: str | None = Field(default=None, description="e.g. 'ACCEPTED', 'PROPOSED'.")
    path: str


# ─── Integrity report ────────────────────────────────────────────────────────


class IntegrityIssue(BaseModel):
    """A single integrity finding from the compile / validate pipeline."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    severity: Severity
    code: str = Field(description="Short machine-readable code, e.g. 'orphan-reference'.")
    message: str
    source_path: str | None = None
    source_line: int | None = None


class IntegrityReport(BaseModel):
    """Aggregate integrity status for one compile run."""

    model_config = ConfigDict(extra="forbid")

    standards_extracted: int = 0
    anti_patterns_extracted: int = 0
    bindings_extracted: int = 0
    domain_standards_extracted: int = 0
    domain_anti_patterns_extracted: int = 0
    references_resolved: int = 0
    references_unresolved: int = 0
    links_checked: int = 0
    links_broken: int = 0
    errors: list[IntegrityIssue] = Field(default_factory=list)
    warnings: list[IntegrityIssue] = Field(default_factory=list)


# ─── Root document ───────────────────────────────────────────────────────────


class CompiledIndex(BaseModel):
    """The complete machine-readable constitutional database.

    Every Governova consumer reads this document instead of the source markdown.
    Generated by `governova-compile`, validated by `governova-validate`,
    consumed by every product surface.
    """

    model_config = ConfigDict(extra="forbid")

    schema_version: str = Field(
        default=SCHEMA_VERSION, description="Semantic version of the schema."
    )
    compiled_at: datetime
    source_commit_sha: str | None = Field(default=None, description="Git SHA of the source tree.")
    checksum: str = Field(description="SHA-256 of the index body (everything except this field).")

    corpus: Literal["full", "core"] = Field(
        default="full",
        description=(
            "Which corpus this document is. `ADR-011` ships a core subset in the "
            "wheel and keeps the domain packs licensed, and until this field "
            "existed the two files were indistinguishable: same schema version, "
            "same commit, different law. Every metric computed from an index is "
            "computed against a denominator, and a denominator whose provenance "
            "cannot be read invites the wrong comparison — `ADR-013` §(c)."
        ),
    )

    framework: list[FrameworkPrimitive] = Field(default_factory=list)
    constitutions: list[Constitution] = Field(default_factory=list)
    implementations: list[Implementation] = Field(default_factory=list)
    domains: list[Constitution] = Field(default_factory=list)
    runbooks: list[Runbook] = Field(default_factory=list)
    adrs: list[ADR] = Field(default_factory=list)

    hierarchy: list[ConstitutionId] = Field(
        default_factory=list,
        description="Conflict-resolution order from C0 §7.1 (highest authority first).",
    )
    phases: dict[Phase, list[ConstitutionId]] = Field(
        default_factory=dict, description="Mapping of phase → constitutions in that phase."
    )

    integrity: IntegrityReport = Field(default_factory=IntegrityReport)

    @field_validator("hierarchy")
    @classmethod
    def hierarchy_unique(cls, v: list[str]) -> list[str]:
        if len(v) != len(set(v)):
            raise ValueError("hierarchy entries must be unique")
        return v


# ─── JSON Schema export entry point ──────────────────────────────────────────


def export_json_schema() -> dict[str, Any]:
    """Return the JSON Schema (draft 2020-12) for `CompiledIndex`."""
    schema = CompiledIndex.model_json_schema(mode="serialization")
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    schema["$id"] = f"https://governova.dev/schema/v{SCHEMA_VERSION}/constitution.schema.json"
    schema["title"] = "Governova Compiled Constitutional Index"
    schema["description"] = (
        f"Machine-readable form of the Governova constitutional database, "
        f"schema version {SCHEMA_VERSION}. See https://governova.dev/docs/schema."
    )
    return schema
