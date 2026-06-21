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
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

SCHEMA_VERSION = "1.0.0"
"""Semantic version of the compiled-index schema. See module docstring."""


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
"""A standard ID in `S{C}.{N}` format. C0 §2.2."""

AntiPatternId = Annotated[
    str, Field(pattern=r"^AP-S\d+\.\d+[a-z]$", examples=["AP-S1.1a", "AP-S3.14b"])
]
"""An anti-pattern ID in `AP-S{C}.{N}{letter}` format. C0 §2.2."""

ImplementationBindingId = Annotated[
    str,
    Field(pattern=r"^S\d+\.\d+/[a-z][a-z0-9_-]*$", examples=["S2.7/fastapi", "S3.14/nextauth"]),
]
"""A stack binding ID in `S{C}.{N}/{stack}` format."""

PracticeId = Annotated[str, Field(pattern=r"^P\d+\.\d+$", examples=["P2.1", "P3.14"])]
"""A practice ID in `P{C}.{N}` format. C0 §2.1 — lives in implementation guides only."""

ConstitutionId = Annotated[str, Field(pattern=r"^C\d{2}$", examples=["C00", "C01", "C10"])]
"""A zero-padded constitution ID. C00, C01, … C10."""

RunbookId = Annotated[str, Field(pattern=r"^RB-\d{2}$", examples=["RB-01", "RB-08"])]

AdrId = Annotated[str, Field(pattern=r"^ADR-\d{3}$", examples=["ADR-001", "ADR-042"])]


# ─── Building blocks ─────────────────────────────────────────────────────────


class Reference(BaseModel):
    """A reference to another standard, with optional inline description.

    Used in `depends_on` and `cross_references` fields. The description is
    typically the parenthetical hint shown in the source markdown.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    standard_id: StandardId
    description: str | None = Field(
        default=None,
        description="Optional inline description, e.g. the parenthetical in source markdown.",
    )


class AntiPattern(BaseModel):
    """A documented failure mode of a standard."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: AntiPatternId
    description: str = Field(description="What the failure looks like in practice.")
    parent_standard_id: StandardId = Field(description="The standard this anti-pattern violates.")


class Standard(BaseModel):
    """A governing statement in a constitution.

    Mirrors the canonical block defined in C0 §3.1.
    """

    model_config = ConfigDict(extra="forbid")

    id: StandardId
    title: str
    constitution_id: ConstitutionId = Field(description="The owning constitution, e.g. 'C01'.")
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
    """A core constitution document (C00–C10) or a domain extension."""

    model_config = ConfigDict(extra="forbid")

    id: ConstitutionId
    number: int = Field(ge=0, description="Numeric constitution number (0–99).")
    name: str
    phase: Phase | None = Field(default=None, description="None for C0; otherwise 0–3.")
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
