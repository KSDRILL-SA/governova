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
        findings = scan_text(code)
        match = next(f for f in findings if f.anti_pattern == ap)
        assert match.confidence == "medium" and not match.blocking, ap


def test_every_rule_binds_a_real_anti_pattern():
    # The governance guarantee: no rule may reference an anti-pattern that does
    # not exist in the compiled constitution.
    assert validate_rules() == []


def test_enforcement_coverage_metric():
    cov = enforcement_coverage()
    assert cov["rules"] == len(RULES)
    assert cov["enforceable_anti_patterns"] == len(RULES)  # all bind real, distinct APs
    assert cov["blocking_rules"] + cov["advisory_rules"] == len(RULES)
    assert 0 < cov["coverage_pct"] < 100


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
