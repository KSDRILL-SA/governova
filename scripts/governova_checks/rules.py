"""Reliable-tier (deterministic) constitutional violation detection.

This is the single source of truth for code-level checks. It is pure — it depends
only on the standard library — so every surface can consume it without pulling in
that surface's dependencies:

- the MCP server exposes these findings *advisorily* (a "review this" signal),
- the CI/CD enforcer turns them into a *merge gate*.

Reliable tier means deterministic and explainable: every finding names the exact
anti-pattern and standard it violates. The semantic/LLM tier is a separate, later
layer of the same enforcer surface — it never silently changes these results.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class Rule:
    """One deterministic check: a regex that, when it matches a line, is a violation."""

    anti_pattern: str
    standard: str
    pattern: re.Pattern[str]
    message: str


@dataclass(frozen=True)
class Finding:
    """A single violation located in source."""

    anti_pattern: str
    standard: str
    message: str
    match: str
    line: int
    col: int
    file: str | None = None
    tier: str = "reliable"
    advisory: bool = True


# ── The rule set ─────────────────────────────────────────────────────────────
# Language-agnostic line patterns. Kept deliberately conservative (low false
# positive) because a blocking gate must be trustworthy.

RULES: list[Rule] = [
    Rule(
        "AP-S3.14a",
        "S3.14",
        re.compile(
            r"\b(?:local|session)Storage\.setItem\s*\(\s*['\"`][^'\"`]*(?:token|jwt|access|refresh|auth)",
            re.I,
        ),
        "Auth token stored in web storage. S3.14: access token in memory, refresh in an HttpOnly cookie.",
    ),
    Rule(
        "AP-S2.17a",
        "S2.17",
        re.compile(
            r"setAllowedOrigins\s*\(\s*[^)]*['\"`]\*['\"`]|Access-Control-Allow-Origin['\"`]?\s*[:,]\s*['\"`]\*['\"`]|origin\s*:\s*['\"`]\*['\"`]",
            re.I,
        ),
        "Wildcard CORS origin. S2.17: explicit allowed origins per environment, never '*' in production.",
    ),
    Rule(
        "AP-S2.34a",
        "S2.34",
        re.compile(
            r"\b(?:double|float)\s+\w*(?:price|amount|balance|total|cost|fee|money|currency)\w*",
            re.I,
        ),
        "Monetary value as float/double. S2.34: money uses BigDecimal/Decimal.",
    ),
    Rule(
        "AP-S2.18a",
        "S2.18",
        re.compile(
            r"\b(?:res\.(?:send|json)|return)\b[^;\n]*\b(?:e|err|error|ex)\.(?:stack|message|getMessage\(\))",
        ),
        "Internal error detail returned to the client. S2.18: never expose stack traces or internal messages.",
    ),
]


# ── Scanning ─────────────────────────────────────────────────────────────────

# Source extensions worth scanning. Detection patterns are language-agnostic, but
# limiting to source files avoids wasting effort on data/binaries.
TEXT_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".svelte", ".astro",
        ".java", ".kt", ".kts", ".scala", ".groovy",
        ".py", ".rb", ".php", ".go", ".rs", ".cs", ".swift", ".m", ".mm",
        ".c", ".cc", ".cpp", ".h", ".hpp", ".dart", ".ex", ".exs",
    }
)


def scan_text(code: str, *, file: str | None = None) -> list[Finding]:
    """Run every rule over `code`, line by line. Returns located findings."""
    findings: list[Finding] = []
    for lineno, line in enumerate(code.splitlines(), start=1):
        for rule in RULES:
            m = rule.pattern.search(line)
            if m:
                findings.append(
                    Finding(
                        anti_pattern=rule.anti_pattern,
                        standard=rule.standard,
                        message=rule.message,
                        match=m.group(0)[:120],
                        line=lineno,
                        col=m.start() + 1,
                        file=file,
                    )
                )
    return findings


def scan_file(path: Path) -> list[Finding]:
    """Scan one file. Silently skips unreadable/binary files."""
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []
    return scan_text(text, file=str(path).replace("\\", "/"))


def scan_paths(paths: Iterable[Path]) -> list[Finding]:
    """Scan every scannable source file in `paths`."""
    findings: list[Finding] = []
    for p in paths:
        if p.is_file() and p.suffix.lower() in TEXT_EXTENSIONS:
            findings.extend(scan_file(p))
    return findings


# ── Backward-compatible MCP shape ────────────────────────────────────────────


def check_text(code: str) -> list[dict[str, Any]]:
    """Reliable-tier checks over a snippet, in the MCP tool's dict shape.

    Advisory only at the MCP surface — never a hard gate there (GOVERNOVA-STRATEGY
    §11.2). The CI enforcer consumes the richer `scan_*` API for blocking.
    """
    return [
        {
            "line": f.line,
            "anti_pattern": f.anti_pattern,
            "standard": f.standard,
            "message": f.message,
            "match": f.match,
            "tier": f.tier,
            "advisory": f.advisory,
        }
        for f in scan_text(code)
    ]
