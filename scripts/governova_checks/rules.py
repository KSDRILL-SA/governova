"""Reliable-tier (deterministic) constitutional violation detection.

The single source of truth for code-level checks. Pure — depends only on the
standard library — so every surface consumes it without that surface's deps:

- the MCP server exposes these findings *advisorily*,
- the CI/CD enforcer turns them into a *merge gate*.

Two governance properties make this a rule *engine*, not a pile of regexes:

* **Index-bound** — every rule references a real anti-pattern (AP-S{C}.{N}{x}).
  `governova_checks.coverage` validates this against the compiled index, so the
  rule set cannot drift from the constitution.
* **Tiered** — each rule has a confidence. HIGH-confidence rules *block* a build;
  MEDIUM-confidence rules only *warn*, even in block mode. The gate hard-fails
  only on near-certain violations, so it stays trustworthy. Confidence governs
  blocking, never detection. The semantic/LLM tier is a separate, later layer.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Literal

Confidence = Literal["high", "medium"]


@dataclass(frozen=True)
class Rule:
    """One deterministic check. A regex match on a line is a violation.

    `confidence`: high rules block the build; medium rules warn even in block mode.
    """

    anti_pattern: str
    standard: str
    pattern: re.Pattern[str]
    message: str
    confidence: Confidence = "high"


@dataclass(frozen=True)
class Finding:
    """A single violation located in source."""

    anti_pattern: str
    standard: str
    message: str
    match: str
    line: int
    col: int
    confidence: Confidence = "high"
    file: str | None = None
    tier: str = "reliable"
    advisory: bool = True

    @property
    def blocking(self) -> bool:
        """Whether this finding fails a build in block mode (high confidence only)."""
        return self.confidence == "high"


# ── The rule set ─────────────────────────────────────────────────────────────
# Language-agnostic line patterns, each bound to a real anti-pattern in the
# constitution. Kept conservative (low false positive) — a blocking gate must be
# trustworthy, so anything FP-prone is tier "medium" (warns, never blocks).

RULES: list[Rule] = [
    # ── HIGH confidence — specific signatures, near-zero false positive ──
    Rule(
        "AP-S3.14a",
        "S3.14",
        re.compile(
            r"\b(?:local|session)Storage\.setItem\s*\(\s*['\"`][^'\"`]*(?:token|jwt|access|refresh|auth)",
            re.I,
        ),
        "Auth token stored in web storage. S3.14: access token in memory, refresh in an HttpOnly cookie.",
        "high",
    ),
    Rule(
        "AP-S2.17a",
        "S2.17",
        re.compile(
            r"setAllowedOrigins\s*\(\s*[^)]*['\"`]\*['\"`]|Access-Control-Allow-Origin['\"`]?\s*[:,]\s*['\"`]\*['\"`]|origin\s*:\s*['\"`]\*['\"`]",
            re.I,
        ),
        "Wildcard CORS origin. S2.17: explicit allowed origins per environment, never '*' in production.",
        "high",
    ),
    Rule(
        "AP-S3.29a",
        "S3.29",
        re.compile(r"allow_origins\s*=\s*\[\s*['\"]\*['\"]", re.I),
        "Wildcard CORS in FastAPI/ASGI middleware. S3.29: never allow_origins=['*'] in production.",
        "high",
    ),
    Rule(
        "AP-S2.34a",
        "S2.34",
        re.compile(
            r"\b(?:double|float)\s+\w*(?:price|amount|balance|total|cost|fee|money|currency)\w*",
            re.I,
        ),
        "Monetary value as float/double. S2.34: money uses BigDecimal/Decimal.",
        "high",
    ),
    Rule(
        "AP-S2.18a",
        "S2.18",
        re.compile(
            r"\b(?:res\.(?:send|json)|return)\b[^;\n]*\b(?:e|err|error|ex)\.(?:stack|message|getMessage\(\))",
        ),
        "Internal error detail returned to the client. S2.18: never expose stack traces or internal messages.",
        "high",
    ),
    Rule(
        "AP-S2.10b",
        "S2.10",
        re.compile(
            r"\b(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis|amqp)://[^\s'\"`]*:[^\s'\"`@/]+@",
            re.I,
        ),
        "Hardcoded connection string with embedded credentials. S2.10: connection strings come from configuration.",
        "high",
    ),
    Rule(
        "AP-S5.21a",
        "S5.21",
        re.compile(r"\$queryRawUnsafe\s*\(", re.I),
        "Unsafe raw SQL ($queryRawUnsafe) — injection risk. S5.21: use parameterised queries only.",
        "high",
    ),
    # ── MEDIUM confidence — strong signal, but context-dependent: warn only ──
    Rule(
        "AP-S2.28f",
        "S2.28",
        re.compile(
            r"(?:`|f['\"])[^`'\"]*\b(?:SELECT|INSERT|UPDATE|DELETE)\b[^`'\"]*(?:\$\{|\{[a-z_])",
            re.I,
        ),
        "SQL built by string interpolation (injection risk). S2.28: parameterise every query.",
        "medium",
    ),
    Rule(
        "AP-S2.10c",
        "S2.10",
        re.compile(
            # The quoted value must not be an identifier/ENV-name reference
            # (e.g. "GOVERNOVA_LLM_API_KEY") — only literal-looking secrets.
            r"(?:api[_-]?key|secret|passwd|password|access[_-]?key|private[_-]?key)\s*[:=]\s*"
            r"['\"](?![A-Za-z0-9]+(?:_[A-Za-z0-9]+)+['\"])[^'\"\s$]{12,}['\"]",
            re.I,
        ),
        "Possible hardcoded secret. S2.10: secrets come from configuration, never committed to source.",
        "medium",
    ),
    Rule(
        "AP-S2.54b",
        "S2.54",
        re.compile(
            r"(?:createHash\s*\(\s*['\"](?:md5|sha1|sha256)|MessageDigest\.getInstance\s*\(\s*['\"](?:MD5|SHA-?1|SHA-?256))",
            re.I,
        ),
        "Weak hash (MD5/SHA). S2.54: passwords use a slow KDF (bcrypt/argon2), not a fast cryptographic hash.",
        "medium",
    ),
    Rule(
        "AP-S2.52a",
        "S2.52",
        re.compile(
            r"console\.(?:log|info|debug|warn|error)\s*\([^)]*\b(?:req\.headers|request\.headers|authorization|password)\b",
            re.I,
        ),
        "Logging request headers / credentials. S2.52: never log secrets or the Authorization header.",
        "medium",
    ),
    Rule(
        "AP-S2.16b",
        "S2.16",
        re.compile(
            r"\b(?:res\.(?:send|json)|return)\b[^;\n]*\b(?:passwordHash|password_hash|refreshToken|refresh_token)\b",
            re.I,
        ),
        "Secret field in an API response. S2.16: never serialise passwordHash/refreshToken to the client.",
        "medium",
    ),
    Rule(
        "AP-S4.19a",
        "S4.19",
        re.compile(r":focus\b[^{}]*\{[^}]*outline\s*:\s*(?:none|0)\b", re.I),
        "Focus outline removed. S4.19: keep a visible keyboard focus indicator (accessibility).",
        "medium",
    ),
    Rule(
        "AP-S1.48b",
        "S1.48",
        re.compile(r"@ts-(?:ignore|expect-error)"),
        "Type checking suppressed (@ts-ignore/@ts-expect-error). S1.48: suppress only with a tracked issue reference.",
        "medium",
    ),
    Rule(
        "AP-S1.49b",
        "S1.49",
        re.compile(r"\bas\s+any\b"),
        "Cast to `any` defeats type safety. S1.49: use `unknown` and validate.",
        "medium",
    ),
    Rule(
        "AP-S3.3a",
        "S3.3",
        re.compile(r"bcrypt\.hash\s*\([^,)]+,\s*\d+"),
        "Hardcoded bcrypt cost factor. S3.3: the work factor must be configurable, not a literal.",
        "medium",
    ),
    Rule(
        "AP-S2.14a",
        "S2.14",
        re.compile(r"\.findMany\(\s*\)"),
        "Unbounded query: findMany() with no pagination. S2.14: bound results with take/skip.",
        "medium",
    ),
    Rule(
        "AP-S5.23a",
        "S5.23",
        re.compile(r"\$queryRaw\s*<\s*any", re.I),
        "Raw query typed as any defeats type safety. S5.23: type raw query results explicitly.",
        "medium",
    ),
    Rule(
        "AP-S2.35a",
        "S2.35",
        re.compile(r"\.delete\(\s*\{\s*where\b"),
        "Hard delete on a possibly-auditable entity. S2.35: prefer soft-delete for auditable records.",
        "medium",
    ),
    Rule(
        "AP-S8.31a",
        "S8.31",
        re.compile(r"\bconsole\.log\s*\("),
        "Unstructured logging via console.log. S8.31: use the structured logger with correlation fields.",
        "medium",
    ),
    Rule(
        "AP-S1.67b",
        "S1.67",
        re.compile(r"setTimeout\s*\([^,]+,\s*\d{4,}\b"),
        "Magic timeout literal. S1.67: name the duration (e.g. SESSION_TIMEOUT_MS), don't inline a number.",
        "medium",
    ),
    Rule(
        "AP-S3.9a",
        "S3.9",
        re.compile(r"\bmaxAge\s*:\s*\d{4,}\b"),
        "Hardcoded session lifetime (maxAge). S3.9: session duration is a deployment-time configuration value.",
        "medium",
    ),
    Rule(
        "AP-S3.21a",
        "S3.21",
        re.compile(r"\.role\s*===?\s*['\"][A-Za-z]"),
        "Role compared to a string literal. S3.21: compare against a defined enum/constant, not a raw string.",
        "medium",
    ),
    Rule(
        "AP-S7.16a",
        "S7.16",
        re.compile(r"\.toMatchSnapshot\s*\("),
        "Snapshot test. S7.16: assert on behaviour, not a brittle rendered-output snapshot.",
        "medium",
    ),
    Rule(
        "AP-S7.17a",
        "S7.17",
        re.compile(r"""(?:from\s+['"]cypress['"]|require\(\s*['"]cypress['"]|\bcy\.(?:visit|get|intercept|contains)\s*\()"""),
        "Cypress detected. S7.17: Cypress is not an approved test stack for this organisation.",
        "medium",
    ),
    Rule(
        "AP-S1.49a",
        "S1.49",
        re.compile(r":\s*any\b"),
        "Type annotated as `any` defeats type safety. S1.49: use `unknown` and validate.",
        "medium",
    ),
    Rule(
        "AP-S1.57b",
        "S1.57",
        re.compile(r"#\s*type:\s*ignore"),
        "Type checking suppressed (# type: ignore). S1.57: fix the type, or reference a tracked issue.",
        "medium",
    ),
    Rule(
        "AP-S2.75a",
        "S2.75",
        re.compile(r"\bnew\s+PrismaClient\s*\("),
        "Ad-hoc PrismaClient instance. S2.75: use a single shared client to avoid connection-pool exhaustion.",
        "medium",
    ),
    Rule(
        "AP-S1.56a",
        "S1.56",
        re.compile(r"""from\s+['"]\.\./\.\./\.\."""),
        "Deep relative import (../../../). S1.56: import across modules via a stable path, not deep traversal.",
        "medium",
    ),
    Rule(
        "AP-S4.27a",
        "S4.27",
        re.compile(r"\bconsole\.error\s*\("),
        "Error sent only to console.error. S4.27: surface errors to the user and the logger; don't swallow them.",
        "medium",
    ),
]


# ── Scanning ─────────────────────────────────────────────────────────────────

# Source extensions worth scanning. Patterns are language-agnostic, but limiting
# to source files avoids wasting effort on data/binaries.
TEXT_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".svelte", ".astro",
        ".java", ".kt", ".kts", ".scala", ".groovy",
        ".py", ".rb", ".php", ".go", ".rs", ".cs", ".swift", ".m", ".mm",
        ".c", ".cc", ".cpp", ".h", ".hpp", ".dart", ".ex", ".exs", ".css", ".scss",
    }
)


def covered_anti_patterns() -> set[str]:
    """The set of anti-pattern ids the rule set can detect."""
    return {r.anti_pattern for r in RULES}


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
                        confidence=rule.confidence,
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
            "confidence": f.confidence,
            "tier": f.tier,
            "advisory": f.advisory,
        }
        for f in scan_text(code)
    ]
