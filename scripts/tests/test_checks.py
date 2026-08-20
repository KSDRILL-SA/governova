"""Tests for the shared detection core (governova_checks)."""

from __future__ import annotations

from governova_checks import (
    RULES,
    Finding,
    check_text,
    enforcement_coverage,
    scan_file,
    scan_paths,
    scan_text,
    validate_rules,
)


def test_scan_text_flags_localstorage_token():
    findings = scan_text("localStorage.setItem('access_token', t);")
    assert len(findings) == 1
    f = findings[0]
    assert isinstance(f, Finding)
    assert f.anti_pattern == "AP-S3.14a"
    assert f.standard == "S3.14"
    assert f.line == 1


def test_scan_text_flags_wildcard_cors():
    findings = scan_text("app.use(cors({ origin: '*' }))")
    assert any(f.anti_pattern == "AP-S2.17a" for f in findings)


def test_scan_text_flags_money_as_double():
    findings = scan_text("double totalPrice = 10.0;")
    assert any(f.anti_pattern == "AP-S5.28a" for f in findings)


def test_scan_text_clean_code_has_no_findings():
    assert scan_text("const sum = a + b;") == []


def test_secret_rule_ignores_env_var_name_constants():
    # An env-var NAME reference is not a hardcoded secret (precision, not noise).
    assert not any(f.anti_pattern == "AP-S2.10c" for f in scan_text('API_KEY = "GOVERNOVA_LLM_API_KEY"'))
    # A literal-looking secret is still flagged.
    assert any(f.anti_pattern == "AP-S2.10c" for f in scan_text('api_key = "sk9s8d7f0a1b2c3d"'))


def test_check_text_keeps_mcp_dict_shape():
    out = check_text("localStorage.setItem('jwt', x);")
    assert out and {"line", "anti_pattern", "standard", "message", "match", "tier", "advisory"} <= set(out[0])
    assert out[0]["advisory"] is True


def test_scan_text_flags_fastapi_wildcard_cors():
    findings = scan_text('app.add_middleware(CORSMiddleware, allow_origins=["*"])')
    f = next(f for f in findings if f.anti_pattern == "AP-S3.29a")
    assert f.confidence == "high" and f.blocking


def test_scan_text_sql_interpolation_is_advisory():
    findings = scan_text('db.query(`SELECT * FROM users WHERE id = ${userId}`)')
    f = next(f for f in findings if f.anti_pattern == "AP-S2.28f")
    assert f.confidence == "medium" and not f.blocking


def test_new_blocking_dsn_credentials_rule():
    findings = scan_text('const url = "postgres://admin:s3cr3t@db.internal:5432/app"')
    f = next(f for f in findings if f.anti_pattern == "AP-S2.10b")
    assert f.confidence == "high" and f.blocking


def test_dsn_without_credentials_not_flagged():
    # No embedded user:pass@ — not a credential leak.
    assert not any(f.anti_pattern == "AP-S2.10b" for f in scan_text('redis://localhost:6379'))


def test_new_advisory_rules_fire():
    cases = {
        "AP-S1.48b": "// @ts-ignore\nconst x = y;",
        "AP-S1.49b": "const v = data as any;",
        "AP-S3.3a": "const h = bcrypt.hash(password, 10);",
        "AP-S2.14a": "const all = await prisma.user.findMany();",
        "AP-S5.23a": "const r = await prisma.$queryRaw<any[]>(sql);",
        "AP-S2.35a": "await prisma.user.delete({ where: { id } });",
    }
    for ap, code in cases.items():
        # `as any` is scoped to the TypeScript family — it is a type annotation
        # that exists nowhere else. Unscoped rules ignore the file.
        findings = scan_text(code, file="src/sample.ts")
        match = next(f for f in findings if f.anti_pattern == ap)
        assert match.confidence == "medium" and not match.blocking, ap


def test_batch2_blocking_unsafe_raw_sql():
    findings = scan_text("await prisma.$queryRawUnsafe(`SELECT * FROM u WHERE id='${id}'`)")
    f = next(f for f in findings if f.anti_pattern == "AP-S5.21a")
    assert f.confidence == "high" and f.blocking


def test_batch2_advisory_rules_fire():
    cases = {
        "AP-S8.31a": "console.log('User logged in', userId)",
        "AP-S1.67b": "setTimeout(refresh, 900000)",
        "AP-S3.9a": "const cfg = { maxAge: 2592000 }",
        "AP-S3.21a": 'if (user.role === "admin") allow()',
        "AP-S7.16a": "expect(wrapper.html()).toMatchSnapshot()",
        "AP-S7.17a": "import { defineConfig } from 'cypress'",
    }
    # A TypeScript path: the `: any` / `as any` rules are scoped to the TS family,
    # because those are type annotations that exist nowhere else. Unscoped rules
    # ignore the file, so one path serves every case here.
    for ap, code in cases.items():
        match = next((f for f in scan_text(code, file="src/sample.ts") if f.anti_pattern == ap), None)
        assert match is not None and match.confidence == "medium" and not match.blocking, ap


def test_batch3_advisory_rules_fire():
    cases = {
        "AP-S1.49a": "let data: any = x;",
        "AP-S1.57b": "value = something()  # type: ignore",
        "AP-S2.75a": "const db = new PrismaClient();",
        "AP-S1.56a": "import { x } from '../../../services/x';",
        "AP-S4.27a": "console.error(error);",
    }
    # A TypeScript path: the `: any` / `as any` rules are scoped to the TS family,
    # because those are type annotations that exist nowhere else. Unscoped rules
    # ignore the file, so one path serves every case here.
    for ap, code in cases.items():
        match = next((f for f in scan_text(code, file="src/sample.ts") if f.anti_pattern == ap), None)
        assert match is not None and match.confidence == "medium", ap


def test_c13_debt_marker_rule_needs_a_tracked_reference():
    findings = scan_text("# TODO: come back to this\nx = 1\n", file="src/app.py")
    assert any(f.anti_pattern == "AP-S13.1a" for f in findings)


def test_c13_debt_marker_with_a_reference_is_recorded_debt():
    # The negative half, and the whole point of the rule: a marker that names its
    # tracked item *is* the recorded decision S13.1 asks for.
    for recorded in (
        "# TODO(#412): drop the shim once the migration lands",
        "// FIXME PROJ-1187 — waiting on upstream",
        "# HACK: see https://github.com/example/repo/issues/9",
    ):
        assert not any(
            f.anti_pattern == "AP-S13.1a"
            for f in scan_text(recorded + "\nx = 1\n", file="src/app.py")
        ), recorded


def test_c13_commented_out_code_is_flagged_but_prose_is_not():
    flagged = scan_text("# return compute(x);\nvalue = 2\n", file="src/app.py")
    assert any(f.anti_pattern == "AP-S13.3a" for f in flagged)
    # Ordinary commentary frequently contains these words and must never fire —
    # a rule that flags explanation is a rule teams delete.
    for prose in (
        "# return early when the cache is warm",
        "# import order matters here for the plugin registry",
        "# if the endpoint is unreachable we degrade to no findings",
    ):
        assert not any(
            f.anti_pattern == "AP-S13.3a" for f in scan_text(prose + "\n", file="src/app.py")
        ), prose


def test_c13_deprecation_needs_a_stated_removal():
    assert any(
        f.anti_pattern == "AP-S13.7a"
        for f in scan_text("@deprecated\ndef old_api():\n    pass\n", file="src/app.py")
    )


def test_c13_deprecation_with_a_removal_is_a_plan():
    for planned in (
        "@deprecated — removed in v3.0",
        "@deprecated: sunset 2027-01-01",
        'warnings.warn("gone in 2.5", DeprecationWarning)',
    ):
        assert not any(
            f.anti_pattern == "AP-S13.7a" for f in scan_text(planned + "\n", file="src/app.py")
        ), planned


def test_c13_rules_do_not_fire_in_test_fixtures():
    # A fixture legitimately holds a bare TODO or a commented line. Firing there
    # would make all three rules noise on their first run against a real repository.
    noisy = "# TODO: no reference here\n# return compute(x);\n@deprecated\n"
    assert not any(
        f.anti_pattern.startswith("AP-S13.") for f in scan_text(noisy, file="tests/test_x.py")
    )


def test_internal_error_detail_reaching_the_client_is_blocking():
    """The positive case for `AP-S2.18b` — the shape express ships as an example."""
    findings = scan_text("app.use(function (err, req, res, next) { res.send({ error: err.message }); });")
    hit = [f for f in findings if f.standard == "S2.18"]
    assert len(hit) == 1
    assert hit[0].anti_pattern == "AP-S2.18b"
    assert hit[0].blocking


def test_a_translated_error_response_does_not_fire():
    """The negative case, and the one that matters.

    A handler that logs the internal detail and returns a uniform, non-revealing
    shape is doing exactly what `S2.18` asks. A rule that flags it punishes the
    compliant form as hard as the leaking one, which removes any reason to
    comply.
    """
    compliant = (
        'logger.error("lookup failed", err);\n'
        'res.status(503).json({ error: "Account lookup is unavailable.", code: "UNAVAILABLE" });\n'
    )
    assert [f for f in scan_text(compliant) if f.standard == "S2.18"] == []


def test_every_rule_binds_a_real_anti_pattern():
    # Verifies REQ-006 — no rule may bind an anti-pattern outside the corpus.
    # The governance guarantee: no rule may reference an anti-pattern that does
    # not exist in the compiled constitution.
    assert validate_rules() == []


# Every rule whose standard carries more than one anti-pattern, pinned to the
# sibling it cites. Twenty-one rules sit on that surface, and *existing* is all
# `validate_rules` can check — `AP-S2.18a` existed, so it passed while the rule
# beneath it implemented `AP-S2.18b`.
#
# Which sibling a rule cites is what a report shows an adopter, so a change here
# has to be deliberate rather than incidental. This pin is the record of that
# choice, and one entry is deliberately a record of a **known defect** rather
# than a blessing — see the S2.34 note below.
_CITED_SIBLING: dict[str, str] = {
    "S1.48": "AP-S1.48b",
    "S1.57": "AP-S1.57b",
    "S1.67": "AP-S1.67b",
    "S2.14": "AP-S2.14a",
    "S2.16": "AP-S2.16b",
    "S2.17": "AP-S2.17a",
    "S2.18": "AP-S2.18b",
    "S2.28": "AP-S2.28f",
    "S2.35": "AP-S2.35a",
    "S2.52": "AP-S2.52a",
    "S2.54": "AP-S2.54b",
    "S3.14": "AP-S3.14a",
    "S3.21": "AP-S3.21a",
    "S3.3": "AP-S3.3a",
    "S4.19": "AP-S4.19a",
    "S5.21": "AP-S5.21a",
}


def test_a_rule_cites_the_sibling_anti_pattern_it_actually_implements():
    """A standard's anti-patterns are not interchangeable, and the id is what is shown.

    `validate_rules` proves a cited anti-pattern *exists*. It cannot prove the
    right one was cited, and that gap let `AP-S2.18a` — "raw **database** error
    message returned in the API response" — sit on a rule matching any
    `error.message` reaching a client. The finding was true; only its label was
    false, which is why review passed it. Onboarding `expressjs/express` then
    described its one blocking finding as a database error with no database in
    sight.
    """
    cited = {r.standard: r.anti_pattern for r in RULES if r.standard in _CITED_SIBLING}
    assert cited == _CITED_SIBLING


def test_playwright_css_class_locator_is_flagged():
    findings = scan_text("await page.locator('.submit-button').click();")
    assert any(f.anti_pattern == "AP-S7.21a" for f in findings)
    # The Python binding is the same call and the same violation.
    assert any(
        f.anti_pattern == "AP-S7.21a"
        for f in scan_text('page.locator(".submit-button").click()')
    )


def test_a_stable_playwright_locator_is_not_flagged():
    """The negative case, and the reason the rule is not `\\.locator\\(`.

    S7.21 forbids the class-selector form — *"never `page.locator('.some-class')`"*.
    A `data-testid` attribute selector is the stable alternative the standard exists
    to steer people towards, and an id selector does not break on a styling
    refactor either. A rule matching every `.locator(` would flag the fix as
    hard as the defect and grade against a rubric wider than the standard it cites.
    """
    for stable in (
        "await page.locator('[data-testid=\"submit\"]').click();",
        "await page.locator('#submit').click();",
        "await page.getByRole('button', { name: 'Submit' }).click();",
    ):
        assert not any(f.anti_pattern == "AP-S7.21a" for f in scan_text(stable)), stable


def test_float_compared_against_money_in_a_test_is_flagged():
    findings = scan_text(
        "assert invoice.amount == 10.50", file="tests/test_billing.py"
    )
    assert any(f.anti_pattern == "AP-S7.38a" for f in findings)
    assert all(f.confidence == "medium" for f in findings if f.anti_pattern == "AP-S7.38a")


def test_float_money_rule_is_scoped_to_tests_and_to_money():
    """Three negatives, and each is a different way this rule could be wrong.

    1. **Outside a test** the rule must not fire at all. `S7.38` is about tests;
       production money-as-float is `S5.28`, a different standard with its own rule.
    2. **A non-monetary float in a test is exactly what `TEST_PATHS` exists to
       protect.** That predicate is a `path_exclude` on every other rule in the
       module because fixtures legitimately hold floats — a timeout, a ratio, a
       coordinate. Only the ones standing for money are forbidden.
    3. **`totalCount`, `feedback` and `taxonomy` are not money**, and a word list
       wrapped in `\\w*` would swallow all three.
    """
    assert not any(
        f.anti_pattern == "AP-S7.38a"
        for f in scan_text("price = 10.50", file="src/billing/service.py")
    )
    for benign in (
        "assert elapsed < 2.5",
        "assert ratio == 0.75",
        "assert totalCount == 3.0",
        "assert feedback.score == 4.5",
        "assert taxonomy.depth == 1.5",
    ):
        assert not any(
            f.anti_pattern == "AP-S7.38a"
            for f in scan_text(benign, file="tests/test_thing.py")
        ), benign


def test_money_as_float_cites_the_standard_it_implements():
    """Replaces the pin that recorded this as a known, unfixable defect.

    The rule matching `double price` / `float amount` cited `S2.34` — *All
    Financial Data Writes Are Idempotent*, whose anti-patterns are a missing
    disbursement check and a missing idempotency key. Neither is about float.
    The finding was true and its label was false, which is exactly why review
    passed it for as long as it did.

    It could not be re-cited earlier because `S5.28` carried no anti-pattern to
    bind to — not because none was written, but because `S5.28` is blockquote
    shorthand and the compiler discarded anti-patterns for all 227 standards in
    that form. `AP-S5.28a` was declared in C05's summary table the whole time.
    The engine learned to read it, the constitution gave it a home, and only then
    was this a one-line change. **Law before check, never the reverse.**
    """
    rule = next(r for r in RULES if r.anti_pattern == "AP-S5.28a")
    assert rule.standard == "S5.28"
    assert rule.confidence == "high", "it blocks builds, and now under the right citation"
    assert not any(r.standard == "S2.34" for r in RULES), "nothing cites S2.34 any more"


def test_rule_coverage_floor():
    """Guard against silent regression of *mechanical reach*.

    The floor used to be `coverage_pct >= 7.0`. That is the reliable-tier ratio, and it
    falls whenever the corpus grows even though no rule was touched — C11 and C14 added
    29 anti-patterns and pushed 33/446 to 33/475. Holding the old number would have made
    this test fail on honest growth, and the only ways to pass it would be to delete
    standards or lower the bar. Both are worse than measuring the right thing.

    So the guard is expressed as what it was always trying to protect: the rule set must
    not shrink, and the *mechanical* reach — rules plus analysers — must not fall. The
    reliable-tier ratio is still reported and still comparable with every historical
    reading of it; it just is not the floor any more, because it stopped being the whole
    story when detection grew past line-scanning.
    """
    cov = enforcement_coverage()
    assert len(RULES) >= 40
    assert cov["mechanical_coverage_pct"] >= 7.0
    # The analyser tier must actually be contributing, or the metric above is a rename.
    assert cov["analyser_enforceable_anti_patterns"] >= 20


def test_enforcement_coverage_metric():
    cov = enforcement_coverage()
    assert cov["rules"] == len(RULES)
    # Every rule binds a real, distinct anti-pattern — but a rule may bind either
    # a core (C00–C10) or a Layer 4 domain anti-pattern, and the headline metric
    # counts only the core so that adding a domain cannot move it.
    assert cov["enforceable_anti_patterns"] + cov["domain_enforceable_anti_patterns"] == len(
        RULES
    )
    assert cov["blocking_rules"] + cov["advisory_rules"] == len(RULES)
    assert 0 < cov["coverage_pct"] < 100
    assert 0 < cov["domain_coverage_pct"] < 100


def test_domain_coverage_is_reported_separately_from_core():
    """Layer 4 must never inflate the headline coverage metric."""
    cov = enforcement_coverage()
    # 446 core anti-patterns, plus C11's twelve ratified under ADR-007 Stage 1,
    # plus the nine orphans given `**Anti-Patterns:**` blocks once the abbreviated
    # form could carry them, plus `AP-S10.8b` — the L4 amendment boundary, which
    # reached the index by being re-parented off a stale row naming `S10.14` —
    # plus **all of C08 and all of C04**, closed by the ceiling programme. C08 was
    # the corpus's largest gap at 72 bare standards; C04 was the next at 36.
    #
    # The denominator keeps *growing*, which lowers enforcement coverage rather
    # than flattering it. That is the honest direction: writing more of the law
    # down does not enforce it, and this figure should never move because a
    # denominator was trimmed.
    assert cov["total_anti_patterns"] == 618, "core denominator changed unexpectedly"
    assert cov["domain_total_anti_patterns"] > 0
    assert all(ap.startswith("AP-D-") for ap in cov["domain_covered"])
    assert not any(ap.startswith("AP-D-") for ap in cov["covered"])


def test_scan_file_sets_file_and_reports_line(tmp_path):
    p = tmp_path / "sample.ts"
    p.write_text("ok();\nlocalStorage.setItem('refresh_token', r);\n", encoding="utf-8")
    findings = scan_file(p)
    assert len(findings) == 1
    assert findings[0].line == 2
    assert findings[0].file and findings[0].file.endswith("sample.ts")


def test_scan_paths_skips_non_source_extensions(tmp_path):
    (tmp_path / "data.json").write_text("localStorage.setItem('access_token', t)", encoding="utf-8")
    src = tmp_path / "x.ts"
    src.write_text("localStorage.setItem('access_token', t)", encoding="utf-8")
    findings = scan_paths(list(tmp_path.iterdir()))
    # Only the .ts file is scanned; the .json is ignored by extension.
    assert all(f.file and f.file.endswith("x.ts") for f in findings)
    assert len(findings) == 1


# ─── The escape hatch an anti-pattern's own text grants (#128) ───────────────


def _suppression_findings(line: str, file: str = "sample.ts") -> list[str]:
    return [f.anti_pattern for f in scan_text(line, file=file) if f.anti_pattern in SUPPRESSIONS]


SUPPRESSIONS = {"AP-S1.48b", "AP-S1.57b"}


def test_an_undocumented_type_suppression_still_fires():
    assert _suppression_findings("value = something()  # type: ignore") == ["AP-S1.57b"]
    assert _suppression_findings("value = something()  # type: ignore[arg-type]") == ["AP-S1.57b"]


def test_a_type_suppression_carrying_an_issue_reference_does_not_fire():
    """`AP-S1.57b` is "`# type: ignore` **without** a GitHub Issue reference".

    Matching only the first half of that sentence grades against a rubric wider than the
    standard it cites, and punishes the documented form exactly as hard as the
    undocumented one — which removes the incentive to document that S1.57 is asking for.
    """
    for line in (
        "value = f()  # type: ignore[arg-type]  # see #456",
        "value = f()  # type: ignore  # GH-4321",
        "value = f()  # type: ignore  # https://github.com/owner/repo/issues/12",
    ):
        assert _suppression_findings(line) == [], line


def test_the_typescript_suppression_has_the_same_clause_and_the_same_narrowing():
    assert _suppression_findings("// @ts-ignore") == ["AP-S1.48b"]
    assert _suppression_findings("// @ts-expect-error") == ["AP-S1.48b"]
    assert _suppression_findings("// @ts-expect-error -- upstream types are wrong, see #98") == []


def test_the_issue_reference_cannot_be_satisfied_by_the_comment_marker_itself():
    # `#` opens the suppression comment. If `ISSUE_REFERENCE` matched a bare `#` or a
    # `#` followed by anything, every suppression would excuse itself.
    assert _suppression_findings("value = f()  # type: ignore  # fix later") == ["AP-S1.57b"]
    assert _suppression_findings("value = f()  # type: ignore  # ticket") == ["AP-S1.57b"]


def test_an_unless_clause_never_widens_what_a_rule_detects():
    # `unless` may only remove findings. A rule without one is unaffected.
    plain = scan_text("localStorage.setItem('access_token', t)", file="a.ts")
    assert plain, "an unrelated rule must be untouched by the suppression mechanism"


def test_suppression_scanning_stays_linear_on_a_hostile_line():
    """A coarse smoke test against catastrophic backtracking. Nothing finer.

    **The budget is deliberately loose, and that is what makes it a real test.**
    The property being guarded differs by *orders of magnitude*: a linear scan of
    this line costs ~4ms, and catastrophic backtracking would not finish a single
    iteration inside the whole budget. Measured, against `'a'*L + '!'`:

        14-char line     2.201 ms       11x the median rule
        18-char line    70.010 ms      355x
        22-char line   740.539 ms     3756x

    At 25 characters it did not complete one scan in 300 seconds. A tight budget
    does not discriminate that any better — it just adds a second failure mode,
    where a slow machine looks like a broken regex. The original form ran 200
    iterations against 2.0s and measured 0.91s here; under `--cov`, which is how
    CI runs the suite, it tipped over and failed a build where nothing was wrong.

    **What this test does NOT guard, despite what it used to claim.** It said it
    existed because a negative lookahead spanning the rest of the line would
    reintroduce the cost `MAX_LINE_LENGTH` bounds. It cannot see that. Swapping the
    suppression rule for each design and running this assertion unchanged:

        linear, two regexes (current)      0.989s   PASS
        rest-of-line negative lookahead    1.066s   PASS
        nested-quantifier lookahead        0.989s   PASS

    The gate runs 40 rules over every line, so one rule's cost is diluted to
    nothing here. Nor is that design forbidden: `AP-D-FINTECH.6b` ships
    `^(?=.*(?:price|amount|…))`, precisely the shape. The repository's real
    discipline is to *bound* the scan — `AP-S13.1a` and `AP-S13.7a` use `.{0,300}`
    and `.{0,200}` — not to avoid lookaheads. See #219.

    Per-rule cost is guarded by `test_no_rule_costs_wildly_more_than_the_others`,
    which is where the dilution does not apply.
    """
    import time

    hostile = "# type: ignore " + ("#" * 3000)
    scan_text(hostile, file="a.py")  # warm the compiled patterns

    start = time.perf_counter()
    for _ in range(20):
        scan_text(hostile, file="a.py")
    elapsed = time.perf_counter() - start
    assert elapsed < 5.0, f"20 hostile scans took {elapsed:.2f}s — suspect backtracking"


# The ratio a single rule may cost against the median rule. One number, shared by
# the ceiling test and the test proving the ceiling still catches something.
COST_CEILING = 25.0

# Samples taken per (rule, line). The cost of a scan is `true cost + noise`, and
# scheduler noise is **never negative** — so the minimum of several samples
# converges on the true cost, while a single sample can only ever be inflated.
#
# This is not a tolerance and it does not move the ceiling. It is the standard
# microbenchmark treatment, and it is here because the previous single-sample form
# failed roughly three runs in eight under CPU contention:
#
#     current, 8 trials under load    3 failures, ratios to 255.8x
#     min-of-3, same 8 trials         0 failures, 7.3x – 12.7x
#
# **255.8x is the finding.** The ceiling is set against 355x for a genuinely
# exponential rule, so under contention the noise floor climbed into the signal and
# the gate could no longer tell a pathological rule from a descheduled one. The
# giveaway was that the rule it accused *changed between runs* — `AP-D-FINTECH.6b`
# at 255.8x and 40.0x, `AP-S13.7a` at 27.3x. A real pathological rule is the same
# rule every time.
#
# The numerator is a `max` over rules and the denominator a `median` across all of
# them, so one-sided noise inflates the numerator alone and the median absorbs it.
# That asymmetry is why a slow machine cancels out and a *busy* one does not.
_COST_REPEATS = 3


def _worst_cost_ratio(rules, lines):
    """The most expensive rule's cost as a ratio to the median rule's.

    Returns `(anti_pattern, cost_seconds, ratio)`.
    """
    import statistics
    import time

    def cost_once(rule, line: str) -> float:
        rule.pattern.search(line)  # warm the compiled pattern
        start = time.perf_counter()
        for _ in range(20):
            match = rule.pattern.search(line)
            if match and rule.unless is not None:
                rule.unless.search(line)
        return time.perf_counter() - start

    costs: dict[str, float] = {}
    for rule in rules:
        worst = 0.0
        for line in lines:
            best = min(cost_once(rule, line) for _ in range(_COST_REPEATS))
            worst = max(worst, best)
        costs[rule.anti_pattern] = worst
    median = statistics.median(costs.values())
    assert median > 0, "timer resolution too coarse to compare rules"
    ap, cost = max(costs.items(), key=lambda kv: kv[1])
    return ap, cost, cost / median


def test_no_rule_costs_wildly_more_than_the_others():
    """One pathological rule, measured where the other 39 cannot dilute it.

    The ceiling is a **ratio to the median rule**, not a duration, so it does not
    measure the machine: a slow runner moves every rule and the median with it.

    The threshold sits between two reachable scores, which is the only thing that
    makes it a threshold. Worst-case cost at `MAX_LINE_LENGTH` over hostile,
    money-word and filler lines:

        median rule          3.943 ms / 20 scans
        AP-D-FINTECH.6b     34.169 ms   8.7x   <- the most expensive real rule
        AP-D-FINTECH.1a     27.493 ms   7.0x
        AP-S1.105a          19.636 ms   5.0x

    against 355x for a nested-quantifier rule on an 18-character line, climbing
    without bound. 25x is comfortably clear of the real spread and orders below
    the failure it exists to catch.

    `AP-D-FINTECH.6b` is not a defect at 1.7ms per 4000-character scan. It is the
    headroom the ceiling is set against.

    **The short line is measured first, and that ordering is load-bearing.** An
    exponential rule does not fail the full-length pass, it *hangs* it — a first
    draft of this test timed out at 300s instead of reporting, which burns a CI job
    rather than naming the rule. The same rule is 166ms on a 60-character line
    against 17.7us for the worst real one, so the cheap pass catches it in
    milliseconds and the expensive pass never runs.
    """
    from governova_checks.rules import MAX_LINE_LENGTH, RULES

    # Pass 1 — short adversarial lines. Cheap, and exponential blowup is already
    # thousands of times the median here, so a pathological rule is named rather
    # than left to hang the pass below.
    short = [("ab " * 40)[:60], ("a" * 40 + "!")[:60], "# type: ignore " + "#" * 45]
    ap, cost, ratio = _worst_cost_ratio(RULES, short)
    assert ratio < COST_CEILING, (
        f"{ap} costs {ratio:.1f}x the median rule on a 60-character line "
        f"({cost * 1e6:.0f}us per 20 scans) — suspect a nested quantifier"
    )

    # Pass 2 — full-length lines. Catches a rule that is costly but not explosive,
    # which the short pass cannot see.
    probes = (
        "# type: ignore " + "#" * MAX_LINE_LENGTH,
        "price amount balance total " * (MAX_LINE_LENGTH // 27),
        "x" * MAX_LINE_LENGTH,
    )
    ap, cost, ratio = _worst_cost_ratio(RULES, [p[:MAX_LINE_LENGTH] for p in probes])
    assert ratio < COST_CEILING, (
        f"{ap} costs {ratio:.1f}x the median rule at MAX_LINE_LENGTH "
        f"({cost * 1000:.1f}ms per 20 scans) — suspect an unbounded quantifier"
    )


def test_the_cost_ceiling_still_catches_a_pathological_rule():
    """The gate must be shown to **fail**, not only to pass.

    A ceiling that has only ever been observed passing has not been shown to be a
    ceiling. `(a+)+b` against a run of `a` with no `b` is the textbook catastrophic
    backtrack — the shape the ratio exists to name.

    **The run length is 12 on purpose.** The cost is `2**n`, so this is bounded at
    roughly four thousand steps: unmistakable and effectively instant. The committed
    probes above contain a 40-character run, and this rule against *that* does not
    report at all — it runs past 600 seconds. Building the negative case is
    therefore not a matter of splicing the rule into the existing probes, and a
    first attempt that did exactly that had to be killed.

    Measured separation on this machine, min-of-repeats, both sides:

        the 40 real rules      6.5x  –  14.8x
        ceiling                        25.0x
        `(a+)+b` on 12 a's           2,646.9x     in 0.04s

    Three orders of magnitude, so the ceiling sits between two reachable scores
    with enormous margin on both sides — which is the only thing that makes it a
    threshold rather than a number.
    """
    import re
    from dataclasses import replace

    from governova_checks.rules import RULES

    pathological = replace(
        RULES[0],
        anti_pattern="AP-SYNTHETIC",
        pattern=re.compile(r"(a+)+b"),
        unless=None,
        path_include=None,
        path_exclude=None,
    )
    ap, _cost, ratio = _worst_cost_ratio([*RULES, pathological], ["a" * 12])
    assert ap == "AP-SYNTHETIC", "the synthetic rule should be the most expensive by far"
    assert ratio >= COST_CEILING, (
        f"a catastrophically backtracking rule measured only {ratio:.1f}x the median "
        f"— the ceiling can no longer detect what it exists for"
    )


def test_a_line_past_the_cap_costs_nothing_to_reject():
    """`MAX_LINE_LENGTH` is the actual bound, so it is asserted directly.

    A minified bundle or a base64 blob on one line is the realistic hostile input,
    and the guarantee is that it is declined rather than scanned. Timing the
    length check is stable in a way that timing a regex is not: rejecting is
    O(1) whatever the machine.
    """
    from governova_checks.rules import MAX_LINE_LENGTH

    over_the_cap = "# type: ignore " + ("#" * (MAX_LINE_LENGTH * 4))
    assert scan_text(over_the_cap, file="a.py") == []
