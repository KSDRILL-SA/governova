"""Pure, MCP-agnostic query logic over the compiled constitutional index.

Kept separate from the FastMCP wiring so every tool is unit-testable without an
MCP client. Loads `compiled/constitution.json` (the index of record) once.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from governova_checks import check_text
from governova_compile.discovery import resolve_repo_root
from governova_compile.schema import CompiledIndex
from governova_compile.writer import load_index

# check_text is re-exported here so the MCP surface exposes the same reliable-tier
# checks the enforcer uses — one rule set, shown advisorily.
__all__ = [
    "check_text",
    "constitution_health",
    "get_anti_pattern",
    "get_binding",
    "get_standard",
    "list_constitutions",
    "reload_index",
    "search_standards",
]


@lru_cache(maxsize=1)
def _index() -> CompiledIndex:
    root = resolve_repo_root()
    return load_index(root / "compiled" / "constitution.json")


def reload_index() -> None:
    """Drop the cached index (after a recompile)."""
    _index.cache_clear()


def _standards() -> list[Any]:
    return [s for c in _index().constitutions for s in c.standards]


def _std_dict(s: Any) -> dict[str, Any]:
    return {
        "id": s.id,
        "title": s.title,
        "constitution_id": s.constitution_id,
        "priority": getattr(s.priority, "value", None),
        "phase": s.phase_label,
        "applies_to": s.applies_to,
        "statement": s.statement,
        "rationale": s.rationale or None,
        "anti_patterns": [
            {"id": ap.id, "description": ap.description} for ap in s.anti_patterns
        ],
    }


# ── Query functions (each backs one MCP tool) ────────────────────────────────


def list_constitutions() -> list[dict[str, Any]]:
    """Every constitution with its standard count and phase."""
    return [
        {
            "id": c.id,
            "name": c.name,
            "phase": getattr(c.phase, "value", None),
            "standards": len(c.standards),
        }
        for c in _index().constitutions
    ]


def get_standard(standard_id: str) -> dict[str, Any] | None:
    """Full detail for one standard (e.g. 'S3.14'), or None if not found."""
    target = standard_id.strip().upper()
    for s in _standards():
        if s.id.upper() == target:
            return _std_dict(s)
    return None


def search_standards(query: str, limit: int = 20) -> list[dict[str, Any]]:
    """Standards whose id, title, or statement matches the query (case-insensitive)."""
    q = query.strip().lower()
    if not q:
        return []
    out = []
    for s in _standards():
        hay = f"{s.id} {s.title} {s.statement}".lower()
        if q in hay:
            out.append({"id": s.id, "title": s.title, "constitution_id": s.constitution_id})
            if len(out) >= limit:
                break
    return out


def get_anti_pattern(anti_pattern_id: str) -> dict[str, Any] | None:
    """An anti-pattern by id (e.g. 'AP-S3.14a') with the standard it violates."""
    target = anti_pattern_id.strip().upper()
    for s in _standards():
        for ap in s.anti_patterns:
            if ap.id.upper() == target:
                return {
                    "id": ap.id,
                    "description": ap.description,
                    "violates_standard": s.id,
                    "standard_title": s.title,
                }
    return None


def get_binding(stack: str, standard_id: str) -> dict[str, Any] | None:
    """The implementation binding of a standard in a stack, e.g. ('spring-boot','S2.1')."""
    st = stack.strip().lower()
    sid = standard_id.strip().upper()
    for impl in _index().implementations:
        if impl.stack.lower() != st:
            continue
        for b in impl.bindings:
            if b.binds_standard.upper() == sid:
                return {
                    "id": b.id,
                    "stack": impl.stack,
                    "binds_standard": b.binds_standard,
                    "satisfies_by": b.satisfies_by,
                    "anti_pattern": b.anti_pattern,
                }
    return None


# Reliable-tier violation checks (check_text) are re-exported from governova_checks
# above — one rule set, shown advisorily here and enforced by the CI/CD surface.


def constitution_health() -> dict[str, Any]:
    """Constitution Health Score (0-100): completeness of the database itself."""
    standards = _standards()
    n = len(standards)
    if n == 0:
        return {"score": 0, "standards": 0}
    with_ap = sum(1 for s in standards if s.anti_patterns)
    with_rat = sum(1 for s in standards if (s.rationale or "").strip())
    ap_cov = with_ap / n
    rat_cov = with_rat / n
    score = round(100 * (0.40 * 1.0 + 0.35 * ap_cov + 0.25 * rat_cov))
    return {
        "score": score,
        "standards": n,
        "anti_pattern_coverage": round(ap_cov, 3),
        "rationale_coverage": round(rat_cov, 3),
    }
