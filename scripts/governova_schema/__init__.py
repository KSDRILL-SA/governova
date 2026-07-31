"""governova_schema — is this data model sound?

C05 governs how data is *accessed*. Nothing in the corpus asked whether the schema being
accessed is **sound** — and a data-model defect is, with a requirements defect, one of the
two most expensive places in software to be wrong. Neither is refactored away later.

**Prisma and SQL DDL first**, because both are declarative: relations are *stated* rather
than inferred, which is what makes referential integrity decidable instead of guessed. A
parser per ecosystem is a permanent tax, and paying it five times before the rule set has
proven itself is the wrong order (ADR-007 §2.1).

**The refusal is the feature.** 2NF and 3NF are properties of functional dependencies,
which a schema does not declare. This analyser returns them as `Unknown`, explicitly,
rather than inferring dependencies from column names — because a false 3NF finding on a
deliberately denormalised reporting table would destroy trust in every other check it
makes. Registering the gap is what keeps the rest credible.

Nothing here blocks a build. The checks are new and they report on schemas this project
did not design.
"""

from __future__ import annotations

import contextlib
from pathlib import Path

from governova_schema.checks import ALL_CHECKS, analyse, normalisation_unknowns
from governova_schema.model import (
    Column,
    Confidence,
    Finding,
    Relation,
    Schema,
    Table,
    Unknown,
)
from governova_schema.prisma import parse_prisma
from governova_schema.sql import parse_sql

__all__ = [
    "ALL_CHECKS",
    "Column",
    "Confidence",
    "Finding",
    "Relation",
    "Schema",
    "Table",
    "Unknown",
    "analyse",
    "analyse_path",
    "analyse_repository",
    "find_schema_files",
    "normalisation_unknowns",
    "parse_prisma",
    "parse_schema",
    "parse_sql",
]

_SKIP_DIRS = frozenset(
    {".git", ".venv", "venv", "node_modules", "__pycache__", "dist", "build", ".mypy_cache",
     ".pytest_cache", ".ruff_cache", "site-packages", ".tox", "migrations"}
)
_MAX_SCHEMA_BYTES = 2_000_000


def parse_schema(text: str, *, dialect: str, source_path: str = "") -> Schema:
    """Parse `text` in the named dialect. Unknown dialects yield an empty schema."""
    if dialect == "prisma":
        return parse_prisma(text, source_path=source_path)
    if dialect == "sql":
        return parse_sql(text, source_path=source_path)
    return Schema(dialect=dialect, source_path=source_path, notes=[f"unknown dialect {dialect!r}"])


def _dialect_for(path: Path) -> str | None:
    suffix = path.suffix.lower()
    if suffix == ".prisma":
        return "prisma"
    if suffix == ".sql":
        return "sql"
    return None


def find_schema_files(root: Path) -> list[Path]:
    """Every readable schema file under `root`, in a stable order.

    `migrations/` is skipped deliberately. A migration is a *historical* statement —
    reporting that a table created three releases ago lacked a key it has since gained
    would be noise about the past rather than a finding about the schema.
    """
    if not root.is_dir():
        return []
    found: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or _dialect_for(path) is None:
            continue
        if any(part.lower() in _SKIP_DIRS for part in path.parts):
            continue
        try:
            if path.stat().st_size > _MAX_SCHEMA_BYTES:
                continue
        except OSError:
            continue
        found.append(path)
    return sorted(found, key=lambda p: p.as_posix())


def analyse_path(path: Path, *, root: Path | None = None) -> tuple[Schema, list[Finding], list[Unknown]]:
    """Parse and analyse one schema file."""
    dialect = _dialect_for(path)
    relative = path.as_posix()
    if root is not None:
        # A path outside the root keeps its absolute form rather than failing — an
        # explicitly named file need not live under the repository being governed.
        with contextlib.suppress(ValueError):
            relative = path.relative_to(root).as_posix()
    if dialect is None:
        schema = Schema(source_path=relative, notes=[f"{path.name}: unsupported extension"])
        return schema, [], []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        schema = Schema(dialect=dialect, source_path=relative, notes=[f"{relative}: unreadable"])
        return schema, [], []
    schema = parse_schema(text, dialect=dialect, source_path=relative)
    findings, unknowns = analyse(schema)
    return schema, findings, unknowns


def analyse_repository(root: Path) -> tuple[list[Schema], list[Finding], list[Unknown]]:
    """Analyse every schema in a repository.

    A repository with no schema is **not** a repository with a sound schema. It returns
    nothing and says nothing, the same rule the requirements tier follows for tier 0:
    a question that cannot be asked is unknown, never satisfied.
    """
    schemas: list[Schema] = []
    findings: list[Finding] = []
    unknowns: list[Unknown] = []
    for path in find_schema_files(root):
        schema, file_findings, file_unknowns = analyse_path(path, root=root)
        schemas.append(schema)
        findings.extend(file_findings)
        unknowns.extend(file_unknowns)
    return schemas, findings, unknowns
