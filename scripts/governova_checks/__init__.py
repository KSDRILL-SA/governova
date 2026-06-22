"""governova_checks — the shared, deterministic detection core.

Single source of truth for code-level constitutional checks, consumed by every
surface (MCP advisory tool, CI/CD enforcer gate). The detection logic in `rules`
is pure stdlib; `coverage` governs the rule set against the compiled constitution.
"""

from __future__ import annotations

from governova_checks.coverage import (
    enforcement_coverage,
    index_anti_patterns,
    validate_rules,
)
from governova_checks.rules import (
    RULES,
    TEXT_EXTENSIONS,
    Confidence,
    Finding,
    Rule,
    check_text,
    covered_anti_patterns,
    scan_file,
    scan_paths,
    scan_text,
)

__all__ = [
    "RULES",
    "TEXT_EXTENSIONS",
    "Confidence",
    "Finding",
    "Rule",
    "check_text",
    "covered_anti_patterns",
    "scan_file",
    "scan_paths",
    "scan_text",
    "enforcement_coverage",
    "index_anti_patterns",
    "validate_rules",
]
