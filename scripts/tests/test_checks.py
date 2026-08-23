"""Tests for the shared detection core (governova_checks)."""

from __future__ import annotations

import pytest
from governova_checks import (
    RULES,
    TEXT_EXTENSIONS,
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


def test_a_curated_domain_error_does_not_fire():
    """The two findings this rule produced on a real adopter, both wrong.

    `AppError` and `DataRequestValidationError` are declared types whose messages
    are written to be read by an API consumer. A bare `return` in front of
    `.message` was signal enough for the old pattern, so both were flagged.
    """
    for line in (
        "    return apiError(err.code, err.message, err.status)",
        "      return apiError('VAL_005', err.message, 400)",
    ):
        assert [f for f in scan_text(line) if f.standard == "S2.18"] == [], line


def test_the_branch_the_standard_was_written_for_still_fires():
    """The unnarrowed handler — the one that can carry a driver message or a
    stack — is what S2.18 exists for, and it was never the flagged one."""
    for line in (
        "res.status(500).json({ error: err.message })",
        "return NextResponse.json({ error: err.stack })",
        "reply.send({ error: err.message })",
        "return { detail: err.stack }",
    ):
        assert [f for f in scan_text(line) if f.standard == "S2.18"] != [], line


def test_a_stack_trace_is_never_client_facing_however_it_is_returned():
    """`.stack` keeps the loose `return` context; `.message` does not. The two
    are not equally decidable from one line, and the rule now says so."""
    assert [f for f in scan_text("return { detail: err.stack }") if f.standard == "S2.18"]
    assert [
        f for f in scan_text("return buildError(err.message)") if f.standard == "S2.18"
    ] == []


def test_the_response_sender_does_not_backtrack_on_a_long_line():
    """This rule runs inside other people's CI as a blocking gate. `AP-D-FINTECH.3a`
    records an 8.7-second line in this codebase, which was a denial of service
    rather than a slow test.

    Measured just under `MAX_LINE_LENGTH`, because anything above it is skipped
    before a pattern ever runs — a longer string would make this test pass by
    never reaching the regex.
    """
    import time

    from governova_checks.rules import MAX_LINE_LENGTH

    line = "res.json({ x: " + "a" * (MAX_LINE_LENGTH - 40) + " })"
    assert len(line) < MAX_LINE_LENGTH
    start = time.perf_counter()
    scan_text(line)
    assert time.perf_counter() - start < 2.0


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
    # Added with the #246 rule batch. Each of these standards carries a second
    # anti-pattern the rule beneath it does *not* implement, which is exactly
    # the confusion this pin exists to prevent.
    "S1.44": "AP-S1.44b",
    "S4.14": "AP-S4.14a",
    "S5.9": "AP-S5.9a",
    # Added with the scan-surface change: `AP-S5.10b` is "a model without
    # `deleted_at`", which is a different claim about the same schema line.
    "S5.10": "AP-S5.10a",
    # Two rules, two siblings, one standard. `AP-S2.17a` is the wildcard `*`;
    # `AP-S2.17b` is a real URL compiled into the application. `AP-S2.12a` is a
    # verb in the path; `AP-S2.12c` is nesting past two levels. Pinning both
    # members is the point — these are the pairs most likely to be swapped.
    "S2.17": ("AP-S2.17a", "AP-S2.17b"),
    "S2.12": ("AP-S2.12a", "AP-S2.12c"),
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

    A standard may carry more than one rule, so the pin holds *every* sibling
    cited for it. The first version of this comparison was a dict comprehension
    keyed by standard, which silently kept the last rule and dropped the rest —
    so the moment `AP-S2.17b` joined `AP-S2.17a`, the pin stopped checking the
    one it was written for. A pin that quietly narrows is worse than no pin.
    """
    expected = {
        standard: frozenset(value) if isinstance(value, tuple) else frozenset({value})
        for standard, value in _CITED_SIBLING.items()
    }

    cited: dict[str, set[str]] = {}
    for rule in RULES:
        if rule.standard in _CITED_SIBLING:
            cited.setdefault(rule.standard, set()).add(rule.anti_pattern)

    assert {k: frozenset(v) for k, v in cited.items()} == expected


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
    # plus **all of C08, C04 and C05**, closed by the ceiling programme. C08 was
    # the corpus's largest gap at 72 bare; C04 followed at 36 and C05 at 35.
    #
    # The figure then took 76 more when the last four constitutions still holding
    # bare blockquote standards were cleared — C06 21, C10 20, C09 18, C07 17.
    # **No standard written in the blockquote shorthand is bare anywhere in the
    # corpus now.** The 65 that remain are all full-form: C01 28, C02 27, C06 10.
    #
    # Then the full-form work: C01's 28 and C02's 27, plus the five *prescriptive*
    # standards among C06's ten. **665 of 670 standards are now bindable.** The five
    # that are not are `S6.39`-`S6.43` — four reference-system attribute tables and
    # a concern-to-constitution map. Those are reference data, not law: no behaviour
    # violates them, so an anti-pattern on one would be invented rather than derived.
    # They stay bare on purpose. 665 is the ceiling, and 670 was never it.
    #
    # The denominator keeps *growing*, which lowers enforcement coverage rather
    # than flattering it. That is the honest direction: writing more of the law
    # down does not enforce it, and this figure should never move because a
    # denominator was trimmed.
    assert cov["total_anti_patterns"] == 789, "core denominator changed unexpectedly"
    assert cov["domain_total_anti_patterns"] > 0
    assert all(ap.startswith("AP-D-") for ap in cov["domain_covered"])
    assert not any(ap.startswith("AP-D-") for ap in cov["covered"])


# The five standards that are deliberately not bindable ───────────────────────

# `S6.39`-`S6.42` are reference-system attribute tables — what FundsLink *is*,
# what Maphophe *is* — and `S6.43` maps a concern to the constitution governing
# it. They are reference data, not law: there is no behaviour that violates
# them, so an anti-pattern attached to one would be invented rather than derived
# from the standard's own words.
#
# They are pinned here because the pressure runs the other way. A gap table that
# reads 665/670 invites someone to close the last five, and closing them means
# writing five anti-patterns nothing can ever fire on — padding the denominator
# to make a figure read 100%. That is the move this corpus exists to refuse.
NOT_BINDABLE = frozenset({"S6.39", "S6.40", "S6.41", "S6.42", "S6.43"})


def test_only_the_reference_data_standards_carry_no_anti_pattern():
    """665 of 670 is the ceiling. The remaining five are not an unfinished job."""
    import json

    from governova_compile.discovery import resolve_repo_root

    root = resolve_repo_root()
    data = json.loads((root / "compiled" / "constitution.json").read_text(encoding="utf-8"))

    bare = {
        standard["id"]
        for constitution in data["constitutions"]
        for standard in constitution["standards"]
        if not standard.get("anti_patterns")
    }

    padded = NOT_BINDABLE - bare
    assert not padded, (
        f"{sorted(padded)} gained an anti-pattern. These describe systems and map "
        "concerns; nothing can violate them, so any rule bound here would be "
        "unfalsifiable. Removing the standard is a real option — inventing an "
        "anti-pattern for it is not."
    )

    regressed = bare - NOT_BINDABLE
    assert not regressed, (
        f"{sorted(regressed)} carry no anti-pattern and so can never become "
        "evidence. Every prescriptive standard in the corpus is bindable; add the "
        "block, or add the standard to NOT_BINDABLE with the reason it is not law."
    )


# ── #246 · the rule batch bound to the raised ceiling ────────────────────────
#
# Each rule is stated twice: the line it must catch, and the *near-miss* it must
# let through. The near-miss is the more important half. A rule that fires on
# the violation is easy; one that also fires on the correct form next to it
# teaches adopters to switch the gate off, and a gate that gets switched off
# enforces nothing at all.
#
# Where a rule is path-scoped, the pair differs only by which file the identical
# line sits in — that is the whole claim such a rule makes.

# The co-author trailer literal is assembled rather than written. This file is a
# fixture, but the string is the exact artefact S1.100 prohibits, and there is no
# reason to commit a real one to make a point about detecting them.
_TRAILER = "Co-Authored" + "-By:"

_CATCHES: list[tuple[str, str, str | None]] = [
    ("AP-S1.100a", f"{_TRAILER} Claude <noreply@anthropic.com>", None),
    ("AP-S1.88a", "@NgModule({ declarations: [AppComponent] })", "src/app.module.ts"),
    ("AP-S1.53a", "export enum Role { Admin = 'ADMIN' }", "src/roles.ts"),
    ("AP-S4.53a", "  changeDetection: ChangeDetectionStrategy.Default,", "src/a.ts"),
    ("AP-S4.47a", '<input [(ngModel)]="name">', "src/form.component.ts"),
    ("AP-S4.60a", '<li *ngFor="let s of students">{{ s.name }}</li>', "src/list.ts"),
    ("AP-S4.55a", "this.http.get('/api/students')", "src/components/list.component.ts"),
    ("AP-S2.75a", "const prisma = new PrismaClient()", "src/api/users.ts"),
    ("AP-S5.18a", 'db["scholarships"].insert_one(doc)', "app/services/store.py"),
    ("AP-S3.11a", "  sameSite: 'none',", "src/session.ts"),
    ("AP-S1.44b", "// remove this later", "src/app.ts"),
    ("AP-S1.68a", "const url = process.env.DATABASE_URL", "src/services/user.ts"),
    ("AP-S2.67a", 'url = os.getenv("DATABASE_URL")', "app/services/user.py"),
    ("AP-S2.69a", "    except Exception:", "app/routers/users.py"),
    ("AP-S2.35a", "await prisma.user.delete({ where: { id } })", "src/services/user.ts"),
    ("AP-S5.9a", "ALTER TABLE users ADD COLUMN phone VARCHAR(20)", "src/admin/fix.ts"),
    ("AP-S1.89a", "new BehaviorSubject<User>(null)", "src/components/user.component.ts"),
    ("AP-S4.14a", '<div class="bg-[#1A2B3C] p-4">', "src/hero.tsx"),
    ("AP-S4.7a", "  height: 100vh;", "src/hero.css"),
    ("AP-S4.26a", "const user = await res.json() as UserProfile;", "src/api.ts"),
    ("AP-S4.23a", "<button onClick={close}><CloseIcon /></button>", "src/modal.tsx"),
    # Reachable only once templates and schemas entered the scan surface.
    ("AP-S5.10a", "  id Int @id @default(autoincrement())", "prisma/schema.prisma"),
    ("AP-S4.17a", '<span class="badge">\U0001f512 Secure</span>', "src/badge.html"),
    ("AP-S4.3a", 'router.get("/mobile/dashboard", handler)', "src/routes.ts"),
    # The API-contract batch.
    ("AP-S2.76a", 'router.get("/api/students", handler)', "src/routers/student-router.ts"),
    ("AP-S1.55a", "export function fetchAll<T>(url: string) {", "src/services/student.ts"),
    ("AP-S2.23a", "const email = request.body.email;", "src/services/student.ts"),
    ("AP-S2.19b", 'return res.json({ data: null });', "src/routers/student-router.ts"),
]

_HOLDS: list[tuple[str, str, str | None]] = [
    # A human co-author is the form the standard exists to protect.
    ("AP-S1.100a", f"{_TRAILER} Thandiwe Mokoena <t@example.com>", None),
    ("AP-S1.88a", "@Component({ standalone: true, selector: 'app-root' })", "src/a.ts"),
    ("AP-S1.53a", "export type Role = 'ADMIN' | 'USER';", "src/roles.ts"),
    # Python has no TypeScript enum, and the rule must not reach for one.
    ("AP-S1.53a", "enum Role { Admin = 'ADMIN' }", "app/roles.py"),
    ("AP-S4.53a", "  changeDetection: ChangeDetectionStrategy.OnPush,", "src/a.ts"),
    ("AP-S4.47a", '<input formControlName="name">', "src/form.component.ts"),
    ("AP-S4.60a", '<li *ngFor="let s of students; trackBy: byId">', "src/list.ts"),
    # The identical call, one layer down, is the prescribed form.
    ("AP-S4.55a", "this.http.get('/api/students')", "src/services/student.service.ts"),
    ("AP-S2.75a", "const prisma = new PrismaClient()", "src/lib/db.ts"),
    ("AP-S5.18a", "await Scholarship.insert(doc)", "app/services/store.py"),
    ("AP-S3.11a", "  sameSite: 'none', secure: true,", "src/session.ts"),
    ("AP-S1.44b", "// TODO: remove this later", "src/app.ts"),
    ("AP-S1.68a", "const url = process.env.DATABASE_URL", "src/config/env.ts"),
    # S2.67 is a backend standard; a CLI reading the environment is not its subject.
    ("AP-S2.67a", 'url = os.getenv("DATABASE_URL")', "scripts/cli.py"),
    ("AP-S2.69a", "    except Exception:", "app/services/users.py"),
    (
        "AP-S2.35a",
        "await prisma.user.update({ where: { id }, data: { deletedAt: now } })",
        "src/services/user.ts",
    ),
    ("AP-S5.9a", "ALTER TABLE users ADD COLUMN phone VARCHAR(20)", "migrations/001_phone.py"),
    ("AP-S1.89a", "new BehaviorSubject<User>(null)", "src/services/user.service.ts"),
    ("AP-S4.14a", '<div class="bg-brand-primary p-4">', "src/hero.tsx"),
    ("AP-S4.7a", "  min-height: 100vh;", "src/hero.css"),
    ("AP-S4.26a", "const user = UserSchema.parse(await res.json());", "src/api.ts"),
    (
        "AP-S4.23a",
        '<button aria-label="Close" onClick={close}><CloseIcon /></button>',
        "src/modal.tsx",
    ),
    ("AP-S5.10a", "  id String @id @default(uuid())", "prisma/schema.prisma"),
    ("AP-S4.17a", '<span class="badge"><LockIcon /> Secure</span>', "src/badge.html"),
    # A word beginning with `m.` is not a mobile subdomain, and prose about
    # mobile is not a mobile build.
    ("AP-S4.3a", "// the mobile layout is handled by the same responsive build", "src/routes.ts"),
    # The API-contract batch. Each near-miss is the correct form of the same line.
    ("AP-S2.76a", 'router.get("/api/v1/students", handler)', "src/routers/student-router.ts"),
    ("AP-S1.55a", "export function fetchAll<TEntity>(url: string) {", "src/services/student.ts"),
    ("AP-S2.23a", "const email = validated.email;", "src/services/student.ts"),
    ("AP-S2.19b", "return res.json({ data: [], count: 0 });", "src/routers/student-router.ts"),
]


@pytest.mark.parametrize(("anti_pattern", "code", "file"), _CATCHES)
def test_the_new_rules_catch_the_violation(anti_pattern, code, file):
    findings = scan_text(code, file=file)
    assert any(f.anti_pattern == anti_pattern for f in findings), (
        f"{anti_pattern} did not fire on {code!r} in {file!r}"
    )


@pytest.mark.parametrize(("anti_pattern", "code", "file"), _HOLDS)
def test_the_new_rules_hold_on_the_near_miss(anti_pattern, code, file):
    findings = scan_text(code, file=file)
    assert not any(f.anti_pattern == anti_pattern for f in findings), (
        f"{anti_pattern} fired on the correct form {code!r} in {file!r}"
    )


def test_every_new_rule_is_stated_in_both_directions():
    """A rule with no near-miss case is a rule nobody has checked for width.

    The pairs above are the specification. This asserts the specification is
    complete rather than trusting that each new rule was given both halves.
    """
    caught = {ap for ap, _, _ in _CATCHES}
    held = {ap for ap, _, _ in _HOLDS}
    assert caught == held, f"missing a direction for {caught ^ held}"


def test_a_path_scoped_rule_declines_when_it_has_no_file():
    """Scope is context the snippet surfaces do not have, so they must not guess.

    The MCP surface scans pasted code with no path. A path-scoped rule that
    fired there would be asserting the snippet's location, which nobody told it.
    """
    scoped = [r for r in RULES if r.path_scoped]
    assert scoped, "the batch added path-scoped rules; this test is about them"
    assert all(not r.applies_to(None) for r in scoped)


# ── The scan surface ─────────────────────────────────────────────────────────


def test_templates_and_schemas_are_in_the_scan_surface():
    """A rule bound to markup is inert until markup is scanned.

    `AP-S4.60a`, `AP-S4.47a` and `AP-S4.23a` describe things written in a
    template. While the surface was source extensions only they could reach the
    minority of components that inline their template, and nothing else — a
    coverage figure counting rules that no file could trigger.
    """
    for ext in (".html", ".htm", ".prisma"):
        assert ext in TEXT_EXTENSIONS


def test_generated_report_directories_are_never_scanned(tmp_path):
    """Coverage reporters embed the source under test, line by line, in markup.

    Scanning them reproduces findings against a path nobody wrote and nobody can
    fix — and reproduces them only partly, since markup splits some tokens and
    not others. A blocking finding in an unfixable file is the fastest way to
    teach an adopter to switch the gate off.
    """
    from governova_checks.gather import iter_source_files

    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.ts").write_text("const a = 1;\n", encoding="utf-8")

    for generated in ("htmlcov", "coverage", "playwright-report", ".next", "storybook-static"):
        d = tmp_path / generated
        d.mkdir()
        (d / "index.html").write_text(
            "<p>app.use(cors({ origin: '*' }))</p>\n", encoding="utf-8"
        )

    found = {p.name for p in iter_source_files(tmp_path)}
    assert found == {"app.ts"}, f"generated output reached the scan surface: {found}"


def test_generated_and_vendored_files_are_never_scanned(tmp_path):
    """A bundle sits beside its source, so no directory list can reach it."""
    from governova_checks.gather import is_generated, iter_source_files

    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.ts").write_text("const a = 1;\n", encoding="utf-8")
    for name in ("vendor.min.js", "app.bundle.js", "styles.min.css", "schema_pb2.py"):
        (tmp_path / "src" / name).write_text(
            "app.use(cors({ origin: '*' }))\n", encoding="utf-8"
        )

    assert is_generated("vendor.MIN.js"), "the check must not depend on case"
    found = {p.name for p in iter_source_files(tmp_path)}
    assert found == {"app.ts"}, f"generated files reached the scan surface: {found}"


def test_an_angular_template_is_read_the_way_a_component_is():
    """The unlock, stated as the thing it unlocks.

    Every violation below is caught and every correct form beside it is left
    alone — in a file type that produced nothing at all before this change.
    """
    template = "\n".join(
        [
            '<li *ngFor="let s of students">{{ s.name }}</li>',
            '<li *ngFor="let t of terms; trackBy: byId">{{ t.name }}</li>',
            '<input [(ngModel)]="query" />',
            '<input [formControl]="queryControl" />',
            "<button (click)=\"close()\"><CloseIcon /></button>",
            '<button aria-label="Close" (click)="close()"><CloseIcon /></button>',
        ]
    )
    findings = scan_text(template, file="src/app/students/list.component.html")
    caught = {(f.anti_pattern, f.line) for f in findings}

    assert ("AP-S4.60a", 1) in caught
    assert ("AP-S4.47a", 3) in caught
    assert ("AP-S4.23a", 5) in caught
    # The corrected form of each, on the very next line.
    assert not any(line in {2, 4, 6} for _, line in caught), (
        f"a rule fired on the prescribed form: {sorted(caught)}"
    )


def test_no_line_produces_findings_from_two_standards():
    """One line, one finding. A duplicate is not a false positive — it is worse.

    Two rules on the same signature are *both correct* about the line, which is
    why review passes them. What they produce is a violation count inflated by
    an engine defect rather than by the code under review, and every figure
    derived from findings inherits it — including the Score's violation-rate
    factor.

    Measured against `expressjs/express` before this was fixed: 36 `console.log`
    lines reported 72 times, because `AP-S1.44a` and `AP-S8.31a` share a
    signature that no line scan can separate. `AP-S2.75a` and `AP-S5.16a` shared
    another.

    The corpus below is every rule's own canonical violating line, so this fails
    the moment a new rule overlaps an existing one.
    """
    overlaps: list[tuple[str, list[str]]] = []
    for anti_pattern, code, file in _CATCHES:
        standards = {f.standard for f in scan_text(code, file=file)}
        if len(standards) > 1:
            overlaps.append((f"{anti_pattern} :: {code}", sorted(standards)))

    assert not overlaps, (
        "these lines are reported against more than one standard:\n  "
        + "\n  ".join(f"{where} -> {found}" for where, found in overlaps)
        + "\nBind one of the anti-patterns, not both. A line scan cannot tell "
        "which of two identically-shaped failures occurred, so claiming both "
        "means one of them is wrong on every line."
    )


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


# ── generated output, recognised by shape rather than by name ────────────────


def test_a_hashed_bundle_is_recognised_as_generated():
    """`is_generated` asks the same question of the file name, and names are the
    weaker signal: webpack's default output is a content hash, so
    `875.6483eb89fd8d09e0.js` matches none of `.min.js`, `.bundle.js` or
    `.chunk.js`.

    The file that exposed this was 2,132 bytes on a single line — under
    `MAX_LINE_LENGTH`, so every rule ran against it and one matched.
    """
    from governova_checks import is_minified

    bundle = "!function(e){" + "a=1;" * 600 + "}();"
    assert len(bundle) > 2000 and "\n" not in bundle
    assert is_minified(bundle)


def test_ordinary_source_is_never_called_generated():
    """The negative case, and the one that matters: this repository's own source
    averages ~45 characters a line against a threshold of 500."""
    from governova_checks import is_minified
    from governova_compile.discovery import resolve_repo_root

    for rel in (
        "scripts/governova_checks/rules.py",
        "scripts/governova_checks/gather.py",
        "README.md",
    ):
        text = (resolve_repo_root() / rel).read_text(encoding="utf-8")
        assert not is_minified(text), rel


def test_a_short_file_with_one_long_line_is_left_alone():
    """Below the size floor a single long line is likelier a paragraph than a
    bundle, and there is little to lose either way."""
    from governova_checks import is_minified

    assert not is_minified("x" * 900)


def test_a_generated_file_produces_no_findings(tmp_path):
    """The whole point. A finding against a bundle cites a file the reader cannot
    open, cannot edit and did not write."""
    violation = "localStorage.setItem('access_token', t);"
    bundle = tmp_path / "875.6483eb89fd8d09e0.js"
    bundle.write_text(violation + ";x=1;" * 500, encoding="utf-8")
    assert scan_file(bundle) == []

    # The same line in a file a person wrote is still reported.
    authored = tmp_path / "auth.js"
    authored.write_text(violation + "\n", encoding="utf-8")
    assert [f.anti_pattern for f in scan_file(authored)] == ["AP-S3.14a"]
