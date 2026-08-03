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
    assert any(f.anti_pattern == "AP-S2.34a" for f in findings)


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


def test_the_known_s234_miscitation_is_still_recorded_not_forgotten():
    """`S2.34` is *"All Financial Data Writes Are Idempotent"*.

    Its two anti-patterns are a missing disbursement check and a missing
    idempotency key. The rule citing it matches `double price` / `float amount`
    — money represented as a float, which is **`S5.28`**, a different standard in
    a different constitution.

    It is not silently re-cited here because `S5.28` carries **no anti-pattern**
    for a rule to bind to, and the standing rule is *amend the standard first,
    law before check, never the reverse*. Amending the corpus is `C0 §8` and
    belongs to L4, so this asserts the defect is still exactly where it was
    rather than pretending it is fixed. **When `AP-S5.28a` is ratified, re-cite
    the rule and delete this test.**
    """
    rule = next(r for r in RULES if r.standard == "S2.34")
    assert rule.anti_pattern == "AP-S2.34a"
    assert rule.confidence == "high", "still blocking builds under the wrong citation"


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
    # 446 core anti-patterns, plus C11's twelve ratified under ADR-007 Stage 1.
    assert cov["total_anti_patterns"] == 498, "core denominator changed unexpectedly"
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
    """`unless` is a second regex rather than a lookahead so this cannot backtrack.

    A negative lookahead spanning the rest of the line would reintroduce exactly the
    cost `MAX_LINE_LENGTH` exists to bound, on a gate that runs in other people's CI.
    """
    import time

    hostile = "# type: ignore " + ("#" * 3000)
    start = time.perf_counter()
    for _ in range(200):
        scan_text(hostile, file="a.py")
    assert time.perf_counter() - start < 2.0
