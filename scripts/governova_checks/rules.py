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
    unless: re.Pattern[str] | None = None
    """The escape hatch an anti-pattern's own text grants, matched on the same line.

    Several anti-patterns are written as *"X **without** Y"* — `AP-S1.57b` is
    "`# type: ignore` without a GitHub Issue reference". A rule that matches only X
    grades against a rubric wider than the standard it cites, and punishes the
    documented form exactly as hard as the undocumented one, which removes any
    incentive to document. `unless` carries the Y clause so the rule matches the whole
    sentence rather than its first half.

    Expressed as a second pattern rather than a negative lookahead deliberately: a
    lookahead spanning the rest of the line reintroduces the backtracking that
    `MAX_LINE_LENGTH` exists to bound, and two linear scans cannot.
    """

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
#
# **`app/` is not on this list, and removing it is the point.** The directory
# means the presentation layer in Next.js — the App Router — and it means the
# *entire backend package* in the FastAPI and Flask conventions, which is
# `app/main.py`, `app/core/`, `app/db/`, `app/modules/`. One name, two opposite
# architectural claims, and the bare form asserted the wrong one for every Python
# backend using the standard layout.
#
# Measured on a FastAPI repository the engine had never seen: **ten blocking
# findings, every one of them in `app/db/`** — the layer that is *supposed* to
# hold `session.execute(`. One of the flagged files opens by explaining that it
# exists so "parameterisation is the only door in". Correct code, blocked, with
# no edit available that satisfies the tool.
#
# Next.js is still reached, and by a stronger signal than the directory name: the
# App Router's reserved filenames. `app/dashboard/page.tsx` is a page because it
# is called `page`, not because it sits under `app/`. Every quantifier is bounded
# — this runs on every scanned path.
UI_LAYER = re.compile(
    r"(?:^|/)(?:components?|pages?|views?|screens?|widgets?)/|"
    r"(?:^|/)app/(?:[^/]{1,64}/){0,12}"
    r"(?:page|layout|template|error|loading|not-found|default)\.[jt]sx?$|"
    r"\.(?:vue|svelte|jsx|tsx)$"
)

# The only place raw data access is permitted (S1.104), plus the places where a
# raw statement is legitimately expected: migrations, seeds, and tests.
#
# `db` is the commonest name a data layer has and was the one name missing, so a
# `app/db/sql.py` matched neither the exclusion that would have saved it nor any
# of the aliases beside it. `store` is deliberately absent: a front-end `store/`
# is where Redux and Pinia live, and a store reaching the database is exactly the
# violation S1.103 exists to report.
DATA_LAYER = re.compile(
    r"(?:^|/)(?:repositor(?:y|ies)|dao|daos|data[-_]?access|persistence|"
    r"db|database|datastore|sql|queries|"
    r"migrations?|seeds?|fixtures?|prisma|alembic)/|"
    r"(?:^|/)[^/]*(?:repository|repositories|dao)[^/]*\.[a-z]+$|"
    r"(?:^|/)(?:tests?|__tests__|spec|e2e)/|"
    r"[._-](?:test|spec)\.[a-z]+$|(?:^|/)test_[^/]*\.py$|(?:^|/)conftest\.py$"
)

# A reference to a tracked issue, in the forms a suppression is actually written
# with: `#123`, `GH-123`, or a link to an issue on any forge. This is the `Y` in
# the several anti-patterns phrased "X without a GitHub Issue reference".
#
# `#123` requires a preceding space or delimiter so it cannot match the `#` that
# opens the suppression comment itself, and every quantifier is bounded: this runs
# on every line of every scanned file inside other people's CI.
ISSUE_REFERENCE = re.compile(
    r"(?:(?<=\s)|(?<=[(\[,:]))#\d{1,7}\b|\bGH-\d{1,7}\b|/issues/\d{1,7}\b",
    re.IGNORECASE,
)

# TypeScript-family files. `: any` and `as any` are type annotations that exist
# only here — matching them everywhere flags Python's builtin `any(...)` call and
# any language with a similar shape, which is a false positive on a blocking
# surface. Plain .js/.jsx are excluded: without a type system there is nothing to
# annotate.
TS_FAMILY = re.compile(r"\.(?:ts|tsx|mts|cts|vue|svelte|astro)$")

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

# Suffixes that turn a money-shaped name into something that is not a money
# violation. Applied immediately after `_MONEY`, so they describe the rest of the
# identifier rather than any later word on the line.
#
# Two separate mistakes, found on the first external fintech codebase Governova
# read, where this rule produced 199 of 201 blocking findings:
#
#   * `cents` / `minor` — integer minor units, which is the representation
#     D-FINTECH.1 *prescribes*. `totalCents` and `collectionAmountCents` in a
#     DebiCheck submission path were blocked for being money done correctly. A
#     developer who read the finding, applied the standard's own remedy and
#     re-ran the gate got the same finding back, which makes compliance
#     unreachable through the tool's own advice — worse than an ordinary false
#     positive, because it teaches the reader that the gate cannot be satisfied.
#
#   * `pages` / `items` / `count` / `months` / `days` — counters. `totalPages`
#     and `totalItems` in a pagination type, `totalPaidMonths` beside
#     `currentStreak` and `longestStreak`. A page count is not a rand.
#
# A bare `total` deliberately still fires. It is genuinely ambiguous — one
# instance in that codebase was a pagination field and the rest were money — and
# no suffix separates them, so it stays with the majority reading rather than
# being settled by a guess.
_NOT_MONEY = r"(?!\w*(?:cents?|minor|pages?|items?|count|months?|days?)\b)"

# A framework method that puts a value on the wire, including the chained form
# `res.status(500).json(...)`. Every quantifier is bounded: this rule runs inside
# other people's CI as a blocking gate, and an unbounded run over a minified
# bundle is a denial of service rather than a slow test (see `AP-D-FINTECH.3a`).
_RESPONSE_SENDER = r"(?:res|reply|response)\.(?:\w{1,32}\([^)\n]{0,60}\)\.)?(?:send|json)"

# The conventional names for a caught error.
_ERR = r"(?:e|err|error|ex)"

# Where configuration is *supposed* to read the environment. S1.68 and S2.67 both
# require the environment to be read once, at startup, into a validated settings
# object — so a raw read is a violation everywhere except here.
CONFIG_PATHS = re.compile(
    r"(?:^|/)(?:config|configs|settings|env)/|"
    r"(?:^|/)[^/]*(?:config|settings|environment)[^/]*\.[a-z]+$|"
    r"(?:^|/)(?:next|vite|nuxt|astro|tailwind|jest|vitest|webpack|rollup)\.[a-z.]+$"
)

# Backend service code. C2 is the *backend* constitution: several of its
# standards describe how a service holds itself together, and are not claims
# about any line that happens to look similar in a CLI, a build script or a
# code generator.
BACKEND_PATHS = re.compile(
    r"(?:^|/)(?:app|api|backend|server|services?|routers?|endpoints?|"
    r"controllers?|domain|usecases?)/"
)

# The HTTP edge: routers, route handlers, controllers. S2.69 governs *where* an
# exception handler lives, which is not a property of a line — it is only
# answerable with the file in hand.
ROUTER_PATHS = re.compile(
    r"(?:^|/)(?:routers?|routes?|api|endpoints?|controllers?|handlers?)/|"
    r"(?:^|/)[^/]*(?:router|route|controller)[^/]*\.[a-z]+$"
)

# Service and model modules. Narrower than `BACKEND_PATHS` on purpose: `S1.55`
# and `S2.23` are both claims about the *service layer* specifically. A router is
# exactly where `request.body` is supposed to be touched — that is the boundary
# doing its job — so including routers here would report the correct code and
# miss the point of the standard.
SERVICE_PATHS = re.compile(
    r"(?:^|/)(?:services?|models?|domain|usecases?|use[-_]cases?)/|"
    r"(?:^|/)[^/]*(?:service|usecase)[^/]*\.[a-z]+$"
)

# Test paths, plus the one module a database client is *meant* to be built in.
_TESTS_OR_DB_SINGLETON = re.compile(
    TEST_PATHS.pattern + r"|(?:^|/)(?:prisma|db|database)\.[a-z]+$"
)

# Test paths or a configuration module — the union S1.68 and S2.67 both need.
_TESTS_OR_CONFIG = re.compile(TEST_PATHS.pattern + r"|" + CONFIG_PATHS.pattern)



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
        "AP-S5.28a",
        "S5.28",
        re.compile(
            # The C-family declaration: `double price`, `float amount`.
            r"\b(?:double|float)\s+\w*(?:price|amount|balance|total|cost|fee|money|currency)\w*"
            # The Python annotation: `amount: float`, `balance: float = 0.0`.
            #
            # Added because the pattern above cannot see Python at all, and this
            # rule blocks builds. Governova's own credit ledger is Python, so
            # `#255`'s "no float in monetary arithmetic, asserted by our own
            # enforcer" would have passed over it without reading a line.
            #
            # `total` is deliberately absent from this half. `\w*total\w*` also
            # matches `total_seconds`, `total_count` and `total_files`, none of
            # which are money — and a blocking rule that fires on those is one
            # people turn off. `subtotal` carries the monetary sense on its own.
            r"|\b\w{0,40}(?:price|amount|balance|subtotal|cost|fee|money|currency|credit)\w{0,40}"
            r"\s*:\s*float\b"
            # A function that returns money as a float. Same reasoning.
            r"|\bdef\s+\w{0,40}(?:price|amount|balance|subtotal|cost|fee|money|currency|credit)"
            r"\w{0,40}\s*\([^)]{0,160}\)\s*->\s*float\b",
            re.I,
        ),
        "Monetary value as float/double. S5.28: money uses Decimal, never Float.",
        "high",
    ),
    Rule(
        # `AP-S2.18b`, not `AP-S2.18a`. S2.18 carries two anti-patterns and this
        # pattern implements the second one verbatim:
        #
        #   AP-S2.18a — Raw *database* error message returned in the API response.
        #   AP-S2.18b — `error.message` or `error.stack` sent directly to the client.
        #
        # Nothing here is database-specific, so the rule was filed under the wrong
        # one of its own standard's anti-patterns. The standard was right, which is
        # why it survived review: the finding is true and only its label was false.
        #
        # That label is what the report shows an adopter. Onboarding `expressjs/express`
        # produced exactly one blocking finding — `res.send({ error: err.message })` —
        # and described it as a raw database error returned to the client, with no
        # database anywhere near the line. A first report that misdescribes its one
        # true finding is how a reader learns to discount the rest.
        #
        # The pattern below splits by *which property* leaves the handler,
        # because the two are not equally decidable from one line.
        #
        # `.stack` and `.getMessage()` are never client-facing values, however
        # they are returned — a bare `return` is signal enough.
        #
        # `.message` is not. A curated domain error carries a message written to
        # be read by an API consumer, and the previous pattern accepted a bare
        # `return` in front of it, so it flagged this:
        #
        #     if (err instanceof AppError) {
        #       return apiError(err.code, err.message, err.status)   // <- flagged
        #     }
        #     logger.error('Unhandled error in API route', { err })
        #     return apiError('SYS_500', 'An unexpected error occurred', 500)
        #
        # Both flagged lines on that adopter were narrowed by `instanceof` to a
        # project-declared error type. The branch handling `unknown` — the one
        # this standard exists for — already returned a fixed string and was not
        # flagged. The rule reported the two safe branches and had nothing to say
        # about the dangerous one.
        #
        # A line scanner cannot see the enclosing `instanceof` guard, so `.message`
        # now requires a framework response sender instead. The cost is a false
        # negative wherever a project wraps its responses in its own helper. That
        # is the right side to be wrong on for a **blocking** rule: a gate that
        # fires on correct code is one that gets switched off, and then the
        # finding that was true goes with it.
        "AP-S2.18b",
        "S2.18",
        re.compile(
            rf"\b(?:return|{_RESPONSE_SENDER})\b[^;\n]{{0,120}}\b{_ERR}\.(?:stack|getMessage\(\))"
            rf"|\b{_RESPONSE_SENDER}\b[^;\n]{{0,120}}\b{_ERR}\.message"
            rf"|\b(?:Next)?Response\.json\s*\([^;\n]{{0,120}}\b{_ERR}\.message",
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
    # `S2.27` says the same thing and has no rule of its own, deliberately. A
    # rule was written for `AP-S2.27a` and removed before landing: it matched
    # the same lines as the one above, which would have reported one defect
    # twice under two standards and inflated every count drawn from findings.
    # Three duplicates already reached this file once and were removed after
    # they showed up in a measurement — express reported 36 lines 72 times.
    # Coverage counts standards, and buying one with a second name for a
    # finding that already exists is buying it dishonestly.
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
        # Same "without a GitHub Issue reference" clause as AP-S1.57b, and the same
        # defect: `@ts-expect-error` is idiomatically written *with* a justification,
        # so the undocumented form is the one the standard is aimed at.
        unless=ISSUE_REFERENCE,
    ),
    Rule(
        "AP-S1.49b",
        "S1.49",
        re.compile(r"\bas\s+any\b"),
        "Cast to `any` defeats type safety. S1.49: use `unknown` and validate.",
        "medium",
        path_include=TS_FAMILY,
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
        # Scoping taken from the `AP-S5.8a` rule removed as a duplicate of this
        # one: a fixture that deletes its own row is not the failure S2.35 names.
        path_exclude=TEST_PATHS,
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
    # S7.21 forbids the *class-selector* form specifically — "never
    # `page.locator('.some-class')`" — not `.locator()` as such. A
    # `page.locator('[data-testid=…]')` is a stable selector and is not what breaks
    # on a styling refactor, so the rule matches the quote-then-dot shape and
    # nothing wider. Matching every `.locator(` would grade against a rubric wider
    # than the standard it cites.
    #
    # Deliberately not scoped to TypeScript: Playwright's Python binding uses the
    # identical `page.locator(".foo")` call, and the standard is about the selector,
    # not the language.
    Rule(
        "AP-S7.21a",
        "S7.21",
        re.compile(r"""\.locator\s*\(\s*['"`]\s*\."""),
        "CSS class selector in a Playwright locator. S7.21: use getByRole()/getByLabel().",
        "medium",
    ),
    # S7.38 — the one rule in this module that fires *only* inside test files.
    # `TEST_PATHS` is a `path_exclude` everywhere else precisely because fixtures
    # legitimately hold floats; this standard is the stated exception. A float in a
    # test is fine until the value it stands for is money.
    #
    # Scans are bounded (`.{0,80}`) rather than greedy, matching `AP-S13.1a` and
    # `AP-S13.7a`: this engine runs as a blocking gate inside other people's CI.
    #
    # **`total`, `fee` and `tax` are deliberately absent from the word list.**
    # `\w*total\w*` matches `totalCount` and `totalPages`, `fee` matches `feedback`
    # and `coffee`, `tax` matches `taxonomy`. The sibling rule `AP-S5.28a` can afford
    # `total` because a `double`/`float` type declaration disambiguates it; this one
    # has no such anchor. Prefer reporting less and being right.
    #
    # Confidence is medium, and that is a *detection* judgement rather than a
    # severity one. S7.38 is Critical, but a heuristic that cannot be trusted to be
    # right must not block somebody's build. A Critical standard with a fuzzy
    # detector warns.
    Rule(
        "AP-S7.38a",
        "S7.38",
        re.compile(
            r"\b(?:assert\w*|expect|should)\b.{0,80}"
            r"\b\w*(?:price|amount|balance|currency|salary|invoice|refund|payment|subtotal|money|cost)\w*\b"
            r".{0,80}\b\d+\.\d+",
            re.I,
        ),
        "Float literal compared against a monetary value in a test. S7.38: expect Decimal.",
        "medium",
        path_include=TEST_PATHS,
    ),
    Rule(
        "AP-S1.49a",
        "S1.49",
        re.compile(r":\s*any\b"),
        "Type annotated as `any` defeats type safety. S1.49: use `unknown` and validate.",
        "medium",
        path_include=TS_FAMILY,
    ),
    Rule(
        "AP-S1.57b",
        "S1.57",
        re.compile(r"#\s{0,8}type:\s{0,8}ignore"),
        "Type checking suppressed (# type: ignore). S1.57: fix the type, or reference a tracked issue.",
        "medium",
        unless=ISSUE_REFERENCE,
    ),
    Rule(
        "AP-S2.75a",
        "S2.75",
        re.compile(r"\bnew\s+PrismaClient\s*\("),
        "Ad-hoc PrismaClient instance. S2.75: use a single shared client to avoid connection-pool exhaustion.",
        "medium",
        # Scoping taken from the `AP-S5.16a` rule that was removed as a duplicate
        # of this one. The module a client is *meant* to be built in must not be
        # reported for building it — without this the rule flags the fix.
        path_exclude=_TESTS_OR_DB_SINGLETON,
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
            rf"(?:\b(?:parse)?[Ff]loat\s*\(\s*\w*{_MONEY}{_NOT_MONEY}|"
            rf"\b\w*{_MONEY}{_NOT_MONEY}\w*\s*:\s*(?:float|number)\b|"
            rf"\bNumber\s*\(\s*\w*{_MONEY}{_NOT_MONEY})",
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
            # SQL form.
            #
            # Every quantifier here is bounded. The original placed unbounded
            # `[\w.]*` immediately before `\w*balance\w*` — overlapping classes,
            # so on a long run of word characters containing no `balance` the
            # engine retried every split point and degraded super-quadratically:
            # 8.7 seconds on one 20k-character line, which is an entirely
            # ordinary minified bundle. This rule runs inside other people's CI
            # as a blocking gate, so that was a denial of service, not a slow
            # test. The backreference is gone as well — `balance = otherBalance
            # + x` is equally a balance mutation, and backrefs defeat the
            # engine's optimisations.
            r"\b[\w.]{0,64}balance\w{0,32}\s*[+-]=|"
            r"\b[\w.]{0,64}balance\w{0,32}\s*=\s*[\w.]{0,64}balance\w{0,32}\s*[+-]|"
            r"\bSET\s+\w{0,32}balance\w{0,32}\s*=\s*\w{0,32}balance\w{0,32}\s*[+-]",
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
    # ── C13 — Software Evolution & Maintenance ──────────────────────────────
    #
    # All three are `medium`, so they warn and never block. Each describes work
    # somebody deliberately left behind, and the judgement about whether it was
    # right to belongs to the team, not to a gate. Test paths are excluded
    # throughout: a fixture legitimately contains a bare `TODO` or a commented
    # line, and firing there would make the rules noise on their first run.
    Rule(
        "AP-S13.1a",
        "S13.1",
        re.compile(
            # A debt marker on a line carrying no tracked reference. The reference is
            # sought across the *whole line* rather than after the marker, because
            # `see #412 — TODO` is as common as `TODO(#412)`. Accepts `#123`,
            # `PROJ-1234`, and bare issue URLs, covering every tracker convention in
            # common use. Both quantifiers are bounded.
            r"^(?!.{0,300}(?:#\d{1,7}|\b[A-Z][A-Z0-9]{1,9}-\d{1,7}\b|https?://))"
            r".{0,200}\b(?:TODO|FIXME|HACK|XXX)\b",
        ),
        "Debt marker with no tracked reference. S13.1: a deferred decision carries a reference to the item that records it — a bare marker is invisible to planning.",
        "medium",
        path_exclude=TEST_PATHS,
    ),
    Rule(
        "AP-S13.3a",
        "S13.3",
        re.compile(
            # A comment whose content is executable code. Requires both a statement
            # keyword *and* a code-shaped terminator, because prose frequently
            # contains the word "return" and almost never ends in `;` or `{`.
            r"^\s{0,60}(?://|#)\s{0,4}"
            r"(?:return|def |class |import |from |const |let |var |function |public |private |if |for |while |print)"
            r"[^\n]{0,160}[;{)]\s{0,4}$",
        ),
        "Executable code retained as a comment. S13.3: delete it — version control is the record of what it was, with an author, a date, and a reason.",
        "medium",
        path_exclude=TEST_PATHS,
    ),
    Rule(
        "AP-S13.7a",
        "S13.7",
        re.compile(
            # A deprecation marker on a line stating no version, date, or removal.
            # Scanned across the whole line rather than after the marker: in
            # `warnings.warn("gone in 2.5", DeprecationWarning)` the removal note
            # precedes the marker, and a trailing-only lookahead reported it as
            # open-ended. Both quantifiers are bounded.
            r"^(?!.{0,300}(?:\bv?\d{1,3}\.\d{1,3}|20\d\d-\d\d|\bremov|\bsunset|\bdrop))"
            r".{0,200}(?:@[Dd]eprecated|DeprecationWarning|@[Oo]bsolete)",
        ),
        "Deprecation with no stated removal. S13.7: name the version or date it goes — an open-ended deprecation gives no consumer a reason to migrate.",
        "medium",
        path_exclude=TEST_PATHS,
    ),
    # ── #246 · binding the ceiling the amendment passes raised ───────────────
    # Six passes added 281 anti-patterns and bound none of them. These are the
    # ones a line scan can actually reach: each names a signature that is a
    # violation on sight rather than a judgement about intent.
    #
    # Two patterns below are written with their literal split across adjacent
    # string pieces. That is deliberate. This repository governs itself with the
    # engine in the branch under review, so a rule whose pattern matches its own
    # source blocks the pull request introducing it — which has now happened
    # here three times. Splitting the literal keeps the warning reproducible.
    Rule(
        "AP-S1.100a",
        "S1.100",
        re.compile(
            r"Co-Authored" r"-By:[^<\n]{0,80}"
            r"\b(?:claude|copilot|codex|chatgpt|cursor|devin|gemini|\w{0,20}\[bot\])\b",
            re.I,
        ),
        "Assistant attribution in a co-author trailer. S1.100: the metadata surface carries human attribution only.",
        "high",
    ),
    Rule(
        "AP-S1.88a",
        "S1.88",
        re.compile(r"@NgModule\s*\("),
        "Module declaration for a component. S1.88: components are standalone — a module wrapper reintroduces exactly the indirection standalone removed.",
        "high",
    ),
    Rule(
        "AP-S1.53a",
        "S1.53",
        re.compile(r"^\s*(?:export\s+)?(?:const\s+)?enum\s+[A-Z]\w{0,40}\s*\{"),
        "Enum declaration. S1.53: use a string-literal union or a const assertion — an enum emits runtime code and does not narrow structurally.",
        "high",
        path_include=TS_FAMILY,
    ),
    Rule(
        "AP-S4.53a",
        "S4.53",
        re.compile(r"ChangeDetectionStrategy\s*\.\s*Default\b"),
        "Default change detection on a component. S4.53: OnPush — the default re-checks every component on every event, and that cost lands on the devices least able to absorb it.",
        "high",
    ),
    Rule(
        "AP-S4.47a",
        "S4.47",
        re.compile(r"\[\(\s*ngModel\s*\)\]"),
        "Template-driven two-way binding. S4.47: reactive forms — a template-driven form cannot be tested without rendering the whole component.",
        "high",
    ),
    Rule(
        "AP-S4.60a",
        "S4.60",
        re.compile(r"\*ng" r"For\s*="),
        "List repeater with no track function. S4.60: without one the whole list re-renders on any change, discarding focus, scroll position and in-progress input inside the rows.",
        "high",
        unless=re.compile(r"\btrackBy\b"),
    ),
    Rule(
        "AP-S4.55a",
        "S4.55",
        re.compile(r"\bthis\s*\.\s*http\s*\.\s*(?:get|post|put|patch|delete|request)\s*\("),
        "HTTP call issued from a component. S4.55: go through a service — a component that calls the network directly cannot be unit-tested without mocking the transport.",
        "high",
        path_include=UI_LAYER,
    ),
    Rule(
        "AP-S5.18a",
        "S5.18",
        re.compile(
            r"\bdb\s*\[\s*['\"][^'\"]{1,60}['\"]\s*\]\s*\.\s*"
            r"(?:insert_one|insert_many|find_one|find|update_one|update_many|"
            r"delete_one|delete_many|aggregate)\s*\("
        ),
        "Raw collection access. S5.18: go through the ODM — a raw call bypasses model validation at the one boundary where the document shape is not guaranteed.",
        "high",
        path_exclude=TEST_PATHS,
    ),
    Rule(
        "AP-S3.11a",
        "S3.11",
        re.compile(r"\bsame" r"[_-]?site\s*[:=]\s*['\"]?none\b", re.I),
        "Cross-site cookie delivery with no secure flag on the same line. S3.11: this disables the primary CSRF defence — pair it with Secure and a documented reason.",
        "high",
        unless=re.compile(r"\bsecure\s*[:=]\s*(?:true|True)\b"),
    ),
    # ── MEDIUM — the signature is right, the context decides ─────────────────
    Rule(
        # `AP-S1.44a` is "`console.log` left in code", and binding it here was a
        # duplicate: `AP-S8.31a` above already matches that exact signature, so
        # every such line produced *two* findings. Measured against express, that
        # was 36 lines reported 72 times — a violation count inflated by an
        # engine defect rather than by the code under review.
        #
        # A line scan cannot separate "left behind after debugging" (S1.44) from
        # "used as the logging mechanism" (S8.31); the text is identical. Binding
        # both asserts both, and one of them is wrong on any given line. S8.31
        # keeps the signature because its message names the fix.
        #
        # `S1.44` is bound to its *other* anti-pattern instead, which has a
        # signature of its own. Nothing is lost and the double count is gone.
        "AP-S1.44b",
        "S1.44",
        re.compile(
            r"^\s*(?://|#|/\*)"
            r"(?=.{0,160}?\b(?:remove|delete|drop|clean\s*up)\b)"
            r"(?=.{0,160}?\b(?:later|eventually|someday|for\s+now|"
            r"before\s+(?:merge|release|ship))\b)"
            r".{0,200}"
        ),
        "Commented-out code kept with a note to remove it later. S1.44: delete it — version control already holds it, and the note outlives the intention.",
        "medium",
        # A marker comment belongs to `AP-S13.1a`, which owns that signature and
        # checks for a tracked issue. Without this the two overlap on
        # `// TODO: remove this later`, which is the defect being fixed above.
        unless=re.compile(r"\b(?:TODO|FIXME|HACK|XXX)\b"),
        path_exclude=TEST_PATHS,
    ),
    Rule(
        "AP-S1.68a",
        "S1.68",
        re.compile(r"\bprocess\s*\.\s*env\s*\.\s*\w{1,60}"),
        "Environment read inline at the point of use. S1.68: read and validate at startup — an absent variable should fail the boot, not the one request that happens to need it.",
        "medium",
        path_exclude=_TESTS_OR_CONFIG,
    ),
    Rule(
        "AP-S2.67a",
        "S2.67",
        re.compile(r"\bos\s*\.\s*(?:getenv\s*\(|environ\s*[.\[])"),
        "Environment read inline at the point of use. S2.67: a settings object owns configuration, so the shape is validated once instead of trusted everywhere.",
        "medium",
        # Scoped to backend service code because that is the standard's own
        # scope: S2.67 is a C2 standard about how a *FastAPI service* holds its
        # configuration. Unscoped, this rule fired eight times on this very
        # repository — four on `GITHUB_STEP_SUMMARY`, a path the CI runner
        # supplies rather than application configuration, and three inside a
        # code generator, where the match was a docstring and a string being
        # *written out* for the user. None is the failure S2.67 describes, and a
        # rule that reports them grades against a rubric wider than the law it
        # cites. The scope is taken from the standard, not from what makes this
        # repository quiet: in a FastAPI service the anti-pattern's own example
        # still fires exactly as written.
        path_include=BACKEND_PATHS,
        path_exclude=_TESTS_OR_CONFIG,
    ),
    Rule(
        "AP-S2.69a",
        "S2.69",
        re.compile(r"\bexcept\s+Exception\b"),
        "Route handler catching the base exception. S2.69: register handlers globally — a handler here returns one endpoint's failures in a shape nothing else uses.",
        "medium",
        path_include=ROUTER_PATHS,
        path_exclude=TEST_PATHS,
    ),
    Rule(
        "AP-S5.9a",
        "S5.9",
        re.compile(r"\bALTER\s+TABLE\b", re.I),
        "Schema change outside a migration. S5.9: the schema file is the source of truth — a change applied directly exists in production and in nobody's code.",
        "medium",
        path_exclude=DATA_LAYER,
    ),
    Rule(
        "AP-S1.89a",
        "S1.89",
        re.compile(r"\bnew\s+BehaviorSubject\s*[<(]"),
        "Manual stream for local component state. S1.89: signals — a manual subscription makes teardown the author's responsibility on every component, and one that forgets leaks a listener per mount.",
        "medium",
        path_include=UI_LAYER,
    ),
    Rule(
        "AP-S4.14a",
        "S4.14",
        re.compile(r"\b(?:bg|text|border|fill|stroke|ring|from|via|to)-\[#[0-9a-f]{3,8}\]", re.I),
        "Brand colour as an inline arbitrary value. S4.14: name it in the theme — an arbitrary value cannot be changed in one place, so a rebrand becomes a search.",
        "medium",
    ),
    Rule(
        "AP-S4.7a",
        "S4.7",
        re.compile(r"(?<!min-)(?<!max-)\bheight\s*:\s*100vh\b", re.I),
        "Fixed viewport height. S4.7: use a minimum height — mobile browser chrome makes the viewport unit taller than what is visible, so the bottom of the section is cut off.",
        "medium",
    ),
    Rule(
        "AP-S4.26a",
        "S4.26",
        re.compile(r"\.\s*json\s*\(\s*\).{0,80}\bas\s+[A-Z]\w{0,40}\b"),
        "Response cast to a type with no runtime validation. S4.26: validate the payload — an assertion tells the compiler what to believe and checks nothing at the one boundary where the shape is not yours.",
        "medium",
    ),
    Rule(
        "AP-S4.23a",
        "S4.23",
        re.compile(r"<button\b[^>]{0,160}>\s*<[A-Z]\w{0,30}Icon\b"),
        "Icon-only control with no accessible name. S4.23: label it — a screen reader announces the control and nothing about what it does.",
        "medium",
        unless=re.compile(r"aria-label"),
    ),
    # ── Reachable only once templates and schemas entered the scan surface ────
    Rule(
        "AP-S5.10a",
        "S5.10",
        re.compile(r"@id\b.{0,40}@default\s*\(\s*autoincrement\s*\(\s*\)"),
        "Sequential integer primary key. S5.10: a UUID — a sequential id publishes the total record count and makes the next record guessable.",
        "high",
    ),
    Rule(
        "AP-S4.17a",
        "S4.17",
        # Pictographs used as interface iconography. The ranges are the emoji
        # blocks proper; letters, digits and punctuation are untouched.
        re.compile(
            r"<(?:span|div|i|b|button|td|p|h[1-6])\b[^>]{0,120}>\s*"
            r"[\U0001F300-\U0001FAFF←-⇿☀-➿️]"
        ),
        "Emoji standing in for an icon. S4.17: use the icon component — an emoji renders differently on every platform and is announced by its unicode name.",
        "medium",
    ),
    Rule(
        "AP-S4.3a",
        "S4.3",
        re.compile(r"""["'`(\s]/mobile/|\bm\.[a-z0-9-]{2,40}\.(?:com|co\.za|org|net|io|app)\b"""),
        "Separate mobile surface. S4.3: one responsive build — a second surface diverges from the first, and the divergence is discovered by the users on it.",
        "medium",
    ),
    Rule(
        "AP-S2.10a",
        "S2.10",
        # The conditional, not the read. `process.env.NODE_ENV` appearing in a
        # config file is how a build learns which bundle to emit and is correct;
        # a *branch* on it inside application code is a code path that has never
        # run in the environment it was written for.
        re.compile(
            r"""(?:if|elif|when|&&|\|\|)\s*\(?\s*[^)
]{0,80}"""
            r"""(?:process\.env\.NODE_ENV|ENVIRONMENT|APP_ENV|os\.environ\[['"]ENV)"""
            r"""[^)
]{0,40}(?:===?|==|!=|!==|is)\s*['"](?:prod|production)['"]"""
        ),
        "Behaviour branching on the environment name. S2.10: the production path is the one nobody exercised — configure the difference, do not branch on it.",
        "medium",
    ),
    Rule(
        "AP-S2.12a",
        "S2.12",
        # A verb in the path is the signature. The verb has to be followed by a
        # capital or a separator so that a resource legitimately named `updates`
        # or `posts` does not match.
        #
        # The message below names the collection and the method rather than
        # quoting a verb-based path, because quoting one would make this rule
        # report the file that defines it. Two other rules here split a literal
        # for the same reason. A rule whose first finding is itself spends the
        # reader's first ten minutes on something that is not real.
        re.compile(
            r"""["'`]/(?:api/)?(?:v\d+/)?(?:get|create|update|delete|fetch|list|"""
            r"""remove|save|set|do|make|send)(?:[A-Z][A-Za-z0-9]{1,30}|[-_][a-z][a-z0-9-_]{1,30})"""
        ),
        "Verb-based endpoint path. S2.12: the HTTP method is the verb — "
        "`POST` against the collection, not the operation named in the path, "
        "which needs a second convention for every operation ever added.",
        "high",
    ),
    Rule(
        "AP-S2.12c",
        "S2.12",
        # Four or more segments after the version. Two levels of nesting is the
        # documented limit, and the version segment is not one of them.
        re.compile(
            r"""["'`]/api/v\d+(?:/[A-Za-z0-9_{}:$-]{1,40}){4,}["'`/]"""
        ),
        "Endpoint nested more than two levels. S2.12: deep nesting encodes one traversal path into the URL, and every client that needs another one gets a new endpoint.",
        "medium",
    ),
    Rule(
        "AP-S2.17b",
        "S2.17",
        # A literal origin inside an allow-list. Distinct from the wildcard rules
        # above (`AP-S2.17a`, `AP-S3.29a`): those catch `*`, this catches a real
        # URL compiled into the application, which cannot differ per environment
        # and is changed by a deploy rather than by configuration.
        re.compile(
            r"""(?:allow_origins|allowedOrigins|allowed_origins|cors(?:Origins)?|origin)\s*"""
            r"""[=:]\s*\[?\s*['"`]https?://(?!localhost|127\.0\.0\.1)[a-z0-9.-]{3,60}""",
            re.I,
        ),
        "Allowed CORS origin hardcoded in application code. S2.17: origins differ per environment, so a literal here is a value that can only be corrected by a deploy.",
        "medium",
    ),
    Rule(
        "AP-S2.21a",
        "S2.21",
        # FastAPI declares the code on the route decorator, so this is a
        # single-line fact rather than an inference about the handler body.
        #
        # Deliberately narrower than it could be. A bare `@HttpCode(HttpStatus.OK)`
        # was in the first version and had to come out: NestJS puts that
        # decorator on its own line, above `@Get()` as often as above `@Post()`,
        # and on a GET it is correct. Catching the NestJS form would mean firing
        # on correct code, and a rule that does that is one people switch off.
        # So the FastAPI form is caught and the NestJS form is not, which is a
        # gap rather than a defect: `S2.21` is still enforced where it is
        # visible on one line.
        re.compile(
            r"""@\w{0,20}\.?post\s*\([^)
]{0,120}"""
            r"""status_code\s*=\s*(?:200|status\.HTTP_200_OK)"""
        ),
        "POST declared to return 200. S2.21: a creation returns 201 with the created resource — a client cannot tell a create from an update when both answer 200.",
        "medium",
    ),
    Rule(
        "AP-S4.20a",
        "S4.20",
        # Below 16px, iOS Safari zooms the viewport on focus and the layout
        # breaks. Scoped to a rule that also mentions an input, so ordinary body
        # copy at 14px is untouched.
        re.compile(
            r"""(?:input|textarea|select|\[type=)[^{;
]{0,80}\{[^}
]{0,120}"""
            r"""font-size\s*:\s*(?:1[0-5](?:\.\d+)?px|0?\.\d+rem)""",
            re.I,
        ),
        "Form input below 16px. S4.20: iOS Safari zooms the viewport when a smaller input takes focus, and the page the user came back to is not the one they left.",
        "medium",
    ),
    Rule(
        "AP-S5.11a",
        "S5.11",
        # Only the form that closes on its own line. A multi-line Prisma call
        # opens with `findMany({` and its `select` is three lines below, so a
        # pattern that did not require the closing paren would report the correct
        # spelling of this call in almost every repository that uses Prisma.
        re.compile(r"\.findMany\s*\([^)\n]{0,200}\)"),
        "findMany with no select clause. S5.11: name the columns — the default "
        "returns every field on the model, including the password hash and the "
        "refresh token, to anything that calls it.",
        "medium",
        unless=re.compile(r"\bselect\s*:"),
    ),
    Rule(
        "AP-S5.14a",
        "S5.14",
        # Same single-line restriction, and a `where` is required: an unfiltered
        # `findMany()` is `AP-S5.11a`'s subject, and a filtered one that still
        # cannot bound its result set is this one's.
        re.compile(r"\.findMany\s*\(\s*\{[^)\n]{0,200}\bwhere\b[^)\n]{0,200}\}\s*\)"),
        "findMany with a filter and no take. S5.14: bound the result — this works "
        "on the row count the table has today and exhausts memory on the count it "
        "will have, with no code change in between.",
        "medium",
        unless=re.compile(r"\btake\s*:"),
    ),
    Rule(
        "AP-S5.17a",
        "S5.17",
        # `as SomeType` applied to a Prisma result. The assertion silences the
        # one check that would have caught the schema drift.
        re.compile(
            r"\bprisma\.[A-Za-z_$][\w$]{0,60}\.[A-Za-z_$][\w$]{0,40}\s*\([^;\n]{0,200}"
            r"\)\s*(?:as\s+(?!const\b)[A-Z][\w<>\[\]]{0,60})"
        ),
        "Type assertion on a Prisma result. S5.17: the generated type is the "
        "schema's guarantee, and asserting over it turns a compile error about a "
        "renamed column into a runtime one about undefined.",
        "medium",
    ),
    Rule(
        "AP-S2.76a",
        "S2.76",
        # `/api/` not followed by a version segment. The negative lookahead is
        # the whole rule: `/api/v1/students` is the correct form and must not
        # match, `/api/students` is the violation.
        #
        # Scoped to where routes are *declared*. `S2.76` governs the endpoint —
        # "All API endpoints are prefixed with `/api/v1/` from the first endpoint
        # implemented" — and a frontend calling an unversioned URL is a symptom
        # of a backend that declared one, fixable only at the declaration.
        #
        # Without the scope this fired on `this.http.get('/api/students')` in an
        # Angular component, which `AP-S4.55a` already reports for a different
        # and equally true reason: the component is calling the network at all.
        # Two standards on one line is what `test_no_line_produces_findings_from_
        # two_standards` exists to stop, and it caught this before it landed.
        re.compile(r"""["'`]/api/(?!v\d+[/"'`])[a-z]"""),
        "Endpoint declared with no version in the path. S2.76: prefix `/api/v1/` "
        "from the first endpoint — an unversioned route cannot gain a v2 beside "
        "it, so the only path to a breaking change is breaking the clients.",
        "medium",
        path_include=ROUTER_PATHS,
    ),
    Rule(
        "AP-S1.55a",
        "S1.55",
        # A single-letter type parameter on a declaration. `S1.55` permits one in
        # a utility type "where the abstraction is so total that no meaningful
        # name exists", so this is scoped to service and model code, which is
        # exactly where the standard says a name is owed.
        re.compile(
            r"\b(?:function|class|interface|type)\s+[A-Za-z_$][\w$]{0,60}\s*"
            r"<\s*[A-Z]\s*(?:,\s*[A-Z]\s*)*[,>]"
        ),
        "Single-letter generic in service or model code. S1.55: name it for its "
        "role — `TEntity`, `TPayload` — because a caller reading the signature "
        "cannot tell what the parameter is for.",
        "medium",
        path_include=SERVICE_PATHS,
    ),
    Rule(
        "AP-S2.23a",
        "S2.23",
        # A request body read *inside the service layer*. Reaching the service at
        # all means it came through the boundary, and the boundary's job was to
        # replace it with a validated value — so the raw shape appearing here is
        # the evidence that it did not.
        re.compile(r"\b(?:request|req|ctx\.request)\s*\.\s*(?:body|query|params)\s*[.\[]"),
        "Raw request data read in the service layer. S2.23: validate at the "
        "boundary — a service reading the unvalidated shape is a service that "
        "trusts whatever the client sent.",
        "medium",
        path_include=SERVICE_PATHS,
    ),
    Rule(
        "AP-S2.19b",
        "S2.19",
        # The detectable half of the response contract. `S2.20` says the same
        # thing about a collection — see the note below.
        re.compile(r"""["']?\bdata["']?\s*:\s*(?:null|None)\b"""),
        "`data: null` in a response envelope. S2.19: `data` is never null — a "
        "client cannot tell an empty result from a failed one, so every consumer "
        "grows a special case for it.",
        "medium",
    ),
    # `S2.20` — the same shape for a *collection*, where the correct value is `[]`
    # rather than an object — has no rule of its own, deliberately. Its
    # anti-pattern is "`data: null` when list is empty", and a line scanner cannot
    # know whether the endpoint returns a collection: the fact on the line is
    # `data: null` and nothing more. Binding it here as well would report one line
    # under two standards, which is how three duplicate rules reached this file
    # before. `S2.19b` is the claim the evidence actually supports.
    #
    # `S6.22` and `AP-S2.76a` stand in the same relation. `S6.22` requires the
    # `/api/v1/` prefix and cites `S2.76` for the versioning policy, so the rule
    # is written once, against the standard that owns the rule.
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
        # Templates. A large part of C4 lives here and nowhere else: the list
        # repeater, form binding and icon-button anti-patterns (`AP-S4.60a`,
        # `AP-S4.47a`, `AP-S4.23a`) are written in markup, so rules bound to
        # them could only ever reach the minority of components that inline
        # their template. Named by id rather than quoted, so this comment does
        # not become a violation of the rules it describes. Safe to add because
        # `gather.SKIP_DIRS` now excludes the generated reports that embed
        # source — see the note there.
        ".html", ".htm",
        # Schema. `S5.10` is a claim about a column definition, which exists in
        # exactly one kind of file.
        ".prisma",
    }
)


def covered_anti_patterns() -> set[str]:
    """The set of anti-pattern ids the rule set can detect."""
    return {r.anti_pattern for r in RULES}


# Lines longer than this are not scanned.
#
# Defence in depth against pathological regex backtracking. Individual rules use
# bounded quantifiers, but this engine runs inside other people's CI as a
# blocking gate, and a single hostile or merely minified line must never be able
# to stall their pipeline — the cost of a regex is a function of line length, so
# the length is capped rather than trusted.
#
# 4000 characters is far beyond any human-authored source line; what exceeds it
# is minified bundles, embedded data URIs, and generated blobs, none of which are
# reviewable and none of which the standards meaningfully govern.
MAX_LINE_LENGTH = 4000


def scan_text(code: str, *, file: str | None = None) -> list[Finding]:
    """Run every rule over `code`, line by line. Returns located findings."""
    findings: list[Finding] = []
    applicable = [r for r in RULES if r.applies_to(file)]
    for lineno, line in enumerate(code.splitlines(), start=1):
        if len(line) > MAX_LINE_LENGTH:
            continue
        for rule in applicable:
            m = rule.pattern.search(line)
            if m and not (rule.unless is not None and rule.unless.search(line)):
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


# A file this dense on average is output, not something a person typed. Ordinary
# source in this repository averages 45 characters a line; the minified bundle
# that produced the finding below averaged 2,132. The threshold sits an order of
# magnitude above the first and four times below the second, which is as much
# room as a heuristic ever gets.
MINIFIED_MEAN_LINE = 500

# Below this, a single long line is more likely a paragraph than a bundle, and
# there is little to lose either way.
MINIFIED_MIN_BYTES = 1000


def is_minified(text: str) -> bool:
    """Whether this content is generated output rather than authored source.

    `is_generated` asks the same question of the file *name*, and names are the
    weaker signal: webpack's default output is a content hash, so
    `875.6483eb89fd8d09e0.js` matches none of `.min.js`, `.bundle.js` or
    `.chunk.js`. The giveaway is the shape.

    `MAX_LINE_LENGTH` already skips individual lines longer than 4,000
    characters, which is why bundles usually produce nothing. The file that
    exposed this gap was 2,132 bytes on one line — under that ceiling, so every
    rule ran against it, and one matched.
    """
    if len(text) < MINIFIED_MIN_BYTES:
        return False
    # `count` rather than `splitlines`, because this runs on every scanned file
    # and `scan_text` is about to build that list anyway. A trailing newline
    # would overcount by one line, which rounds the wrong way — toward calling a
    # bundle authored — so it is not worth correcting.
    lines = text.count("\n") + 1
    return len(text) / lines > MINIFIED_MEAN_LINE


def scan_file(path: Path) -> list[Finding]:
    """Scan one file. Silently skips unreadable/binary files and generated output."""
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []
    # Checked here rather than in `iter_source_files`, because the shape test
    # needs the content and this is where the content already is. A finding
    # against a bundle cites a file the reader cannot edit, which is the fastest
    # way to teach an adopter to switch the gate off.
    if is_minified(text):
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
