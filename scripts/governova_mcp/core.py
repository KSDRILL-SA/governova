"""Pure, MCP-agnostic query logic over the compiled constitutional index.

Kept separate from the FastMCP wiring so every tool is unit-testable without an
MCP client. Loads `compiled/constitution.json` (the index of record) once.
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from governova_compile.discovery import resolve_repo_root
from governova_compile.schema import CompiledIndex
from governova_compile.writer import load_index


@lru_cache(maxsize=1)
def _index() -> CompiledIndex:
    root = resolve_repo_root()
    return load_index(root / "compiled" / "constitution.json")


def reload_index() -> None:
    """Drop the cached index (after a recompile)."""
    _index.cache_clear()


def _standards() -> list:
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


# ── Reliable-tier (deterministic) violation checks ───────────────────────────
# Same discipline as the IDE surface: deterministic, advisory. No semantic/LLM
# checks here — those belong to the CI/PR surfaces.

_RULES: list[tuple[str, str, re.Pattern[str], str]] = [
    (
        "AP-S3.14a",
        "S3.14",
        re.compile(
            r"\b(?:local|session)Storage\.setItem\s*\(\s*['\"`][^'\"`]*(?:token|jwt|access|refresh|auth)",
            re.I,
        ),
        "Auth token stored in web storage. S3.14: access token in memory, refresh in an HttpOnly cookie.",
    ),
    (
        "AP-S2.17a",
        "S2.17",
        re.compile(
            r"setAllowedOrigins\s*\(\s*[^)]*['\"`]\*['\"`]|Access-Control-Allow-Origin['\"`]?\s*[:,]\s*['\"`]\*['\"`]|origin\s*:\s*['\"`]\*['\"`]",
            re.I,
        ),
        "Wildcard CORS origin. S2.17: explicit allowed origins per environment, never '*' in production.",
    ),
    (
        "AP-S2.34a",
        "S2.34",
        re.compile(r"\b(?:double|float)\s+\w*(?:price|amount|balance|total|cost|fee|money|currency)\w*", re.I),
        "Monetary value as float/double. S2.34: money uses BigDecimal/Decimal.",
    ),
    (
        "AP-S2.18a",
        "S2.18",
        re.compile(r"\b(?:res\.(?:send|json)|return)\b[^;\n]*\b(?:e|err|error|ex)\.(?:stack|message|getMessage\(\))"),
        "Internal error detail returned to the client. S2.18: never expose stack traces or internal messages.",
    ),
]


def check_text(code: str) -> list[dict[str, Any]]:
    """Run reliable-tier (deterministic, advisory) checks over a code snippet.

    Returns a list of findings: {line, anti_pattern, standard, message, match}.
    Advisory only — never a hard gate (GOVERNOVA-STRATEGY §11.2).
    """
    findings: list[dict[str, Any]] = []
    for lineno, line in enumerate(code.splitlines(), start=1):
        for ap_id, std, pat, msg in _RULES:
            m = pat.search(line)
            if m:
                findings.append(
                    {
                        "line": lineno,
                        "anti_pattern": ap_id,
                        "standard": std,
                        "message": msg,
                        "match": m.group(0)[:120],
                        "tier": "reliable",
                        "advisory": True,
                    }
                )
    return findings


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
