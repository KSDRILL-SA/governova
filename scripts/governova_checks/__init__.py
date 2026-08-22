"""governova_checks — the shared, deterministic detection core.

Single source of truth for code-level constitutional checks, consumed by every
surface (MCP advisory tool, CI/CD enforcer gate). The detection logic in `rules`
is pure stdlib; `coverage` governs the rule set against the compiled constitution.
"""

from __future__ import annotations

from governova_checks.coverage import (
    domain_anti_patterns,
    enforcement_coverage,
    index_anti_patterns,
    unresolved_bindings,
    validate_rules,
)
from governova_checks.gather import (
    DEFAULT_IGNORES,
    SKIP_DIRS,
    changed_files,
    is_ignored,
    iter_source_files,
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
    "DEFAULT_IGNORES",
    "RULES",
    "SKIP_DIRS",
    "TEXT_EXTENSIONS",
    "Confidence",
    "Finding",
    "Rule",
    "changed_files",
    "check_text",
    "covered_anti_patterns",
    "domain_anti_patterns",
    "enforcement_coverage",
    "index_anti_patterns",
    "is_ignored",
    "iter_source_files",
    "scan_file",
    "scan_paths",
    "scan_text",
    "unresolved_bindings",
    "validate_rules",
]
