"""Governance of the rule set against the constitution.

Kept separate from `rules.py` (which is pure stdlib) because these functions read
the compiled index. They answer two questions:

- Is every rule *legitimate* — does it bind a real anti-pattern? (`validate_rules`)
- How much of the constitution is mechanically enforceable? (`enforcement_coverage`)
"""

from __future__ import annotations

from typing import Any

from governova_checks.rules import RULES, covered_anti_patterns
from governova_compile.discovery import resolve_repo_root
from governova_compile.schema import CompiledIndex
from governova_compile.writer import load_index


def _load_index(index: CompiledIndex | None) -> CompiledIndex:
    if index is not None:
        return index
    return load_index(resolve_repo_root() / "compiled" / "constitution.json")


def index_anti_patterns(index: CompiledIndex | None = None) -> set[str]:
    """Every anti-pattern id defined in the compiled constitution."""
    idx = _load_index(index)
    return {
        ap.id
        for c in idx.constitutions
        for s in c.standards
        for ap in s.anti_patterns
    }


def validate_rules(index: CompiledIndex | None = None) -> list[str]:
    """Anti-pattern ids referenced by rules that do NOT exist in the constitution.

    An empty list means the rule set is fully grounded in the constitution.
    """
    defined = index_anti_patterns(index)
    return sorted(r.anti_pattern for r in RULES if r.anti_pattern not in defined)


def enforcement_coverage(index: CompiledIndex | None = None) -> dict[str, Any]:
    """How much of the constitution's anti-pattern surface is enforceable."""
    defined = index_anti_patterns(index)
    covered = covered_anti_patterns() & defined
    total = len(defined)
    pct = round(100 * len(covered) / total, 1) if total else 0.0
    high = sum(1 for r in RULES if r.confidence == "high")
    medium = sum(1 for r in RULES if r.confidence == "medium")
    return {
        "rules": len(RULES),
        "blocking_rules": high,
        "advisory_rules": medium,
        "enforceable_anti_patterns": len(covered),
        "total_anti_patterns": total,
        "coverage_pct": pct,
        "covered": sorted(covered),
    }
