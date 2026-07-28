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
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

Confidence = Literal["high", "medium"]


@dataclass(frozen=True)
class Rule:
    """One deterministic check. A regex match on a line is a violation.

    `confidence`: high rules block the build; medium rules warn even in block mode.

    `path_include` / `path_exclude` scope a rule to an architectural region. They
    exist because architectural standards are not properties of a line — the same
    database call is correct inside a repository and a violation inside a UI
    component. Without file context such a standard is undetectable by
    construction, which is why the reliable tier could not reach S1.103/S1.104
    before. A rule carrying either predicate is skipped entirely when no file is
    known, so snippet surfaces stay conservative rather than guessing.
    """

    anti_pattern: str
    standard: str
    pattern: re.Pattern[str]
    message: str
    confidence: Confidence = "high"
    path_include: re.Pattern[str] | None = None
    path_exclude: re.Pattern[str] | None = None

    @property
    def path_scoped(self) -> bool:
        return self.path_include is not None or self.path_exclude is not None

    def applies_to(self, file: str | None) -> bool:
        """Whether this rule may fire against `file`.

        A path-scoped rule needs context it does not have when `file` is None,
        so it declines rather than assuming the file sits in the region.
        """
        if not self.path_scoped:
            return True
        if file is None:
            return False
        path = file.replace("\\", "/").lower()
        if self.path_include is not None and not self.path_include.search(path):
            return False
        return not (self.path_exclude is not None and self.path_exclude.search(path))


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


# ── Architectural regions ────────────────────────────────────────────────────
# Where a file sits decides whether some lines are correct or violations. These
# name the regions the constitution already reasons about (C1 Part 19), matched
# against a lower-cased, forward-slashed path.

# Presentation layer: components, pages, views, and single-file component formats.
UI_LAYER = re.compile(
    r"(?:^|/)(?:components?|pages?|views?|screens?|widgets?|app)/|\.(?:vue|svelte|jsx|tsx)$"
)

# The only place raw data access is permitted (S1.104), plus the places where a
# raw statement is legitimately expected: migrations, seeds, and tests.
DATA_LAYER = re.compile(
    r"(?:^|/)(?:repositor(?:y|ies)|dao|daos|data[-_]?access|persistence|"
    r"migrations?|seeds?|fixtures?|prisma|alembic)/|"
    r"(?:^|/)[^/]*(?:repository|repositories|dao)[^/]*\.[a-z]+$|"
    r"(?:^|/)(?:tests?|__tests__|spec|e2e)/|"
    r"[._-](?:test|spec)\.[a-z]+$|(?:^|/)test_[^/]*\.py$|(?:^|/)conftest\.py$"
)

# Test files — several rules must not fire here (fixtures legitimately hold
# literal URLs, floats, and hand-built tenant contexts).
TEST_PATHS = re.compile(
    r"(?:^|/)(?:tests?|__tests__|spec|e2e|cypress|playwright|fixtures?|mocks?)/|"
    r"[._-](?:test|spec)\.[a-z]+$|(?:^|/)test_[^/]*\.py$|(?:^|/)conftest\.py$"
)

# Raw database / ORM access — the signature S1.104 governs.
_RAW_DATA_ACCESS = (
    r"\b(?:"
    r"prisma\.\$(?:queryRaw|executeRaw)\w*|"
    r"(?:db|conn|connection|cursor|session)\.(?:execute|executemany|raw)\s*\(|"
    r"session\.query\s*\(|"
    r"createQueryBuilder\s*\(|"
    r"knex\.raw\s*\(|"
    r"psycopg2\.connect\s*\(|"
    r"sqlalchemy\.(?:create_engine|text)\s*\(|"
    r"mongoose\.connect\s*\(|"
    r"getConnection\s*\(\s*\)\s*\.\s*query"
    r")"
)

# Identifiers whose value is money. Used by the fintech rules — deliberately
# narrow so that ordinary numeric code is never implicated.
_MONEY = r"(?:price|amount|balance|total|subtotal|cost|fee|salary|payment|refund|money|currency)"


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
    # ── Part 19 — Architectural Discipline (path-scoped) ──────────────────
    # These are the rules S1.103/S1.104 declare in their `Enforced By` fields.
    # Each is a violation only because of where the file sits, which is why they
    # need path scoping rather than a cleverer regex.
    Rule(
        "AP-S1.103a",
        "S1.103",
        re.compile(_RAW_DATA_ACCESS, re.I),
        "Database access inside a UI component. S1.103: presentation delegates to a service; it holds no data access or business rules.",
        "high",
        path_include=UI_LAYER,
        path_exclude=TEST_PATHS,
    ),
    Rule(
        "AP-S1.104a",
        "S1.104",
        re.compile(_RAW_DATA_ACCESS, re.I),
        "Raw database/ORM access outside the repository layer. S1.104: persistence is reached through a repository.",
        "medium",
        path_exclude=DATA_LAYER,
    ),
    Rule(
        "AP-S1.105a",
        "S1.105",
        re.compile(
            r"\b\w*(?:base_?url|api_?url|endpoint|webhook_?url|host_?name|service_?url)\w*\s*[:=]\s*"
            r"['\"]https?://(?!localhost|127\.0\.0\.1|0\.0\.0\.0|example\.|schemas?\.|www\.w3\.org)",
            re.I,
        ),
        "Environment-specific URL inlined as a literal. S1.105: environment values are named configuration, not source constants.",
        "medium",
        path_exclude=TEST_PATHS,
    ),
    # ── Layer 4 — domain anti-patterns ────────────────────────────────────
    Rule(
        "AP-D-FINTECH.1a",
        "D-FINTECH.1",
        re.compile(
            rf"(?:\b(?:parse)?[Ff]loat\s*\(\s*\w*{_MONEY}|"
            rf"\b\w*{_MONEY}\w*\s*:\s*(?:float|number)\b|"
            rf"\bNumber\s*\(\s*\w*{_MONEY})",
            re.I,
        ),
        "Monetary value coerced through a floating-point type. D-FINTECH.1: money is an exact decimal, never a float.",
        "high",
        path_exclude=TEST_PATHS,
    ),
    Rule(
        "AP-D-FINTECH.3a",
        "D-FINTECH.3",
        re.compile(
            # `account.balance = account.balance + x`, `balance += x`, and the
            # SQL form. The optional `[\w.]*\.` prefixes let the backreference
            # survive an object path on either side of the assignment.
            r"(?:[\w.]*\.)?(\w*balance\w*)\s*=\s*(?:[\w.]*\.)?\1\s*[+-]|"
            r"\b[\w.]*\bbalance\w*\s*[+-]=|"
            r"\bSET\s+\w*balance\w*\s*=\s*\w*balance\w*\s*[+-]",
            re.I,
        ),
        "Balance mutated in place. D-FINTECH.3: balances are derived from immutable double-entry ledger entries.",
        "high",
        path_exclude=TEST_PATHS,
    ),
    Rule(
        "AP-D-FINTECH.6b",
        "D-FINTECH.6",
        re.compile(
            # The money term may sit either side of the assertion —
            # `assertAlmostEqual(invoice.total, x)` or `expect(o.amount).toBeCloseTo(x)` —
            # so require both on the line rather than a fixed order.
            rf"^(?=.*{_MONEY}).*\b(?:assertAlmostEqual|toBeCloseTo|pytest\.approx|approx)\s*\(",
            re.I,
        ),
        "Approximate comparison asserted against a monetary value. D-FINTECH.6: assert exact decimals — tolerance hides the discrepancy the standard exists to prevent.",
        "high",
    ),
    Rule(
        "AP-D-SAAS.1b",
        "D-SAAS.1",
        re.compile(
            # Dot access (`req.query.tenantId`) or subscript, including header
            # names that carry a vendor prefix (`req.headers["x-tenant-id"]`).
            r"\b(?:req|request|ctx)\.(?:query|body|params|headers)\s*"
            r"(?:\.\s*|\[\s*['\"][\w-]*?)"
            r"(?:tenant|org(?:anisation|anization)?|account|workspace|company)[_-]?id\b",
            re.I,
        ),
        "Tenant identity taken from client-controlled request input. D-SAAS.1: tenant context is derived server-side from the authenticated session.",
        "high",
        path_exclude=TEST_PATHS,
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
    applicable = [r for r in RULES if r.applies_to(file)]
    for lineno, line in enumerate(code.splitlines(), start=1):
        for rule in applicable:
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
