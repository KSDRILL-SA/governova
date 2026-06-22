"""governova_checks — the shared, deterministic detection core.

Single source of truth for code-level constitutional checks, consumed by every
surface (MCP advisory tool, CI/CD enforcer gate). Pure standard library.
"""

from __future__ import annotations

from governova_checks.rules import (
    RULES,
    TEXT_EXTENSIONS,
    Finding,
    Rule,
    check_text,
    scan_file,
    scan_paths,
    scan_text,
)

__all__ = [
    "RULES",
    "TEXT_EXTENSIONS",
    "Finding",
    "Rule",
    "check_text",
    "scan_file",
    "scan_paths",
    "scan_text",
]
