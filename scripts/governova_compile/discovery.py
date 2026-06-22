"""Repo discovery — locate constitution, implementation, runbook, and ADR files.

The constitution registry (phase, hierarchy rank, name) is authoritative from
C0 §5.1 and §7.1. We keep it here as the single mapping between file locations
and constitutional metadata, rather than re-deriving facts the constitution
already states about itself.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from governova_compile.schema import ConstitutionId, Phase


@dataclass(frozen=True)
class ConstitutionEntry:
    """Static metadata for one core constitution, from C0 §5.1 / §7.1."""

    id: ConstitutionId
    number: int
    name: str
    phase: Phase | None
    hierarchy_rank: int
    binds_implementation: bool
    relative_path: str


# C0 §5.1 (register) + §7.1 (hierarchy). hierarchy_rank: 1 = highest authority.
CONSTITUTION_REGISTRY: tuple[ConstitutionEntry, ...] = (
    ConstitutionEntry(
        "C00", 0, "Constitutional Order", None, 1, False, "constitution/C00-constitutional-order.md"
    ),
    ConstitutionEntry(
        "C01",
        1,
        "Engineering Standards",
        Phase.FOUNDATION,
        7,
        False,
        "constitution/core/phase-0-foundation/C01-engineering-standards.md",
    ),
    ConstitutionEntry(
        "C02",
        2,
        "Backend Constitution",
        Phase.CORE_ARCHITECTURE,
        3,
        True,
        "constitution/core/phase-1-core-architecture/C02-backend-constitution.md",
    ),
    ConstitutionEntry(
        "C03",
        3,
        "Auth Constitution",
        Phase.CORE_ARCHITECTURE,
        2,
        True,
        "constitution/core/phase-1-core-architecture/C03-auth-constitution.md",
    ),
    ConstitutionEntry(
        "C04",
        4,
        "Frontend Constitution",
        Phase.CORE_ARCHITECTURE,
        5,
        True,
        "constitution/core/phase-1-core-architecture/C04-frontend-constitution.md",
    ),
    ConstitutionEntry(
        "C05",
        5,
        "Database Constitution",
        Phase.CORE_ARCHITECTURE,
        4,
        True,
        "constitution/core/phase-1-core-architecture/C05-database-constitution.md",
    ),
    ConstitutionEntry(
        "C06",
        6,
        "Full-Stack Architecture",
        Phase.CORE_ARCHITECTURE,
        6,
        False,
        "constitution/core/phase-1-core-architecture/C06-fullstack-architecture-constitution.md",
    ),
    ConstitutionEntry(
        "C07",
        7,
        "Testing Constitution",
        Phase.QUALITY_RELIABILITY,
        8,
        False,
        "constitution/core/phase-2-quality-reliability/C07-testing-constitution.md",
    ),
    ConstitutionEntry(
        "C08",
        8,
        "Platform Reliability",
        Phase.QUALITY_RELIABILITY,
        9,
        False,
        "constitution/core/phase-2-quality-reliability/C08-platform-reliability-constitution.md",
    ),
    ConstitutionEntry(
        "C09",
        9,
        "Product & Feature",
        Phase.PRODUCT_INTELLIGENCE,
        10,
        False,
        "constitution/core/phase-3-product-intelligence/C09-product-feature-constitution.md",
    ),
    ConstitutionEntry(
        "C10",
        10,
        "AI Collaboration",
        Phase.PRODUCT_INTELLIGENCE,
        11,
        False,
        "constitution/core/phase-3-product-intelligence/C10-ai-collaboration-constitution.md",
    ),
)

# Hierarchy order from C0 §7.1, highest authority first.
HIERARCHY_ORDER: tuple[ConstitutionId, ...] = (
    "C00",
    "C03",
    "C02",
    "C05",
    "C04",
    "C06",
    "C01",
    "C07",
    "C08",
    "C09",
    "C10",
)


@dataclass(frozen=True)
class ImplementationEntry:
    """Static metadata for one implementation binding document."""

    stack: str
    binds_constitution: ConstitutionId
    name: str
    relative_path: str


IMPLEMENTATION_REGISTRY: tuple[ImplementationEntry, ...] = (
    ImplementationEntry(
        "fastapi",
        "C02",
        "FastAPI Backend Bindings",
        "constitution/implementation/fastapi/C02-backend-fastapi.md",
    ),
    ImplementationEntry(
        "spring-boot",
        "C02",
        "Spring Boot Backend Bindings",
        "constitution/implementation/spring-boot/C02-backend-spring-boot.md",
    ),
    ImplementationEntry(
        "nextauth",
        "C03",
        "NextAuth Bindings",
        "constitution/implementation/nextauth/C03-auth-nextauth.md",
    ),
    ImplementationEntry(
        "nextjs",
        "C04",
        "Next.js Frontend Bindings",
        "constitution/implementation/nextjs/C04-frontend-nextjs.md",
    ),
    ImplementationEntry(
        "prisma-postgresql",
        "C05",
        "Prisma + PostgreSQL Bindings",
        "constitution/implementation/prisma-postgresql/C05-database-prisma.md",
    ),
)


@dataclass(frozen=True)
class FrameworkEntry:
    id: str
    title: str
    summary: str
    relative_path: str


FRAMEWORK_REGISTRY: tuple[FrameworkEntry, ...] = (
    FrameworkEntry(
        "format-specification",
        "Format Specification",
        "S{C}.{N} standard ID format, AP anti-pattern format, document structure",
        "framework/format-specification.md",
    ),
    FrameworkEntry(
        "phase-model",
        "Phase Model",
        "The four-phase read and dependency order (Phase 0–3)",
        "framework/phase-model.md",
    ),
    FrameworkEntry(
        "severity-model",
        "Severity Model",
        "SEV0–SEV3 classification for violations and incidents",
        "framework/severity-model.md",
    ),
    FrameworkEntry(
        "permission-model",
        "Permission Model",
        "L1–L4 AI permission levels; L4 permanently human-only",
        "framework/permission-model.md",
    ),
    FrameworkEntry(
        "conflict-resolution",
        "Conflict Resolution",
        "Constitutional hierarchy and four-step conflict resolution protocol",
        "framework/conflict-resolution.md",
    ),
    FrameworkEntry(
        "amendment-protocol",
        "Amendment Protocol",
        "How standards are changed, audited, and versioned",
        "framework/amendment-protocol.md",
    ),
)


def resolve_repo_root(start: Path | None = None) -> Path:
    """Walk upward from `start` (or cwd) to find the repo root.

    The root is identified structurally: the directory that holds both the
    `constitution/` corpus and the workspace `pyproject.toml`. This is stable
    regardless of where strategic docs live (they were relocated under docs/),
    and it ignores the nested `scripts/pyproject.toml` because that directory
    has no `constitution/` sibling.
    """
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / "constitution").is_dir() and (candidate / "pyproject.toml").is_file():
            return candidate
    raise FileNotFoundError(
        "Could not locate repo root (no directory with constitution/ and pyproject.toml found)."
    )


def find_runbooks(repo_root: Path) -> list[Path]:
    runbook_dir = repo_root / "governance" / "runbooks"
    if not runbook_dir.is_dir():
        return []
    return sorted(p for p in runbook_dir.glob("RB-*.md") if p.is_file())


def find_adrs(repo_root: Path) -> list[Path]:
    adr_dir = repo_root / "governance" / "decisions"
    if not adr_dir.is_dir():
        return []
    return sorted(p for p in adr_dir.glob("ADR-*.md") if p.is_file())


def find_domain_constitutions(repo_root: Path) -> list[Path]:
    """Find any domain constitution documents (Layer 4). May be empty."""
    domain_dir = repo_root / "constitution" / "domains"
    if not domain_dir.is_dir():
        return []
    # Domain constitutions follow the D-{DOMAIN}.md naming or *-constitution.md.
    return sorted(
        p for p in domain_dir.rglob("*.md") if p.is_file() and p.name.lower() != "readme.md"
    )
