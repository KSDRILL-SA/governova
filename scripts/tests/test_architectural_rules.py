"""Tests for path-scoped rules and the Part 19 / Layer 4 rule set.

Every rule here carries a **negative** test alongside its positive one. A blocking
gate is only worth having if it is trusted, and the way these rules lose trust is
by firing on legitimate code — a repository doing exactly what a repository is for,
a test fixture holding a literal, an ordinary variable that happens to be numeric.
The negative cases are therefore the point, not padding.
"""

from __future__ import annotations

import re

from governova_checks.coverage import domain_anti_patterns, validate_rules
from governova_checks.rules import RULES, Confidence, Rule, scan_text


def _fired(code: str, *, file: str | None = None) -> set[str]:
    return {f.anti_pattern for f in scan_text(code, file=file)}


def _rule(anti_pattern: str) -> Rule:
    return next(r for r in RULES if r.anti_pattern == anti_pattern)


# ─── The path-scoping mechanism ──────────────────────────────────────────────


def test_a_path_scoped_rule_declines_without_file_context() -> None:
    """No file means no architectural context, so the rule must not guess."""
    code = "const rows = await db.execute(sql);"
    assert "AP-S1.103a" not in _fired(code, file=None)
    assert "AP-S1.104a" not in _fired(code, file=None)


def test_an_unscoped_rule_still_fires_without_file_context() -> None:
    assert "AP-S5.21a" in _fired("prisma.$queryRawUnsafe(q)", file=None)


def test_applies_to_honours_include_and_exclude() -> None:
    r = Rule(
        "AP-S1.1a",
        "S1.1",
        re.compile("x"),
        "m",
        "high",
        path_include=re.compile(r"/src/"),
        path_exclude=re.compile(r"/tests?/"),
    )
    assert r.applies_to("app/src/thing.ts")
    assert not r.applies_to("app/lib/thing.ts")  # outside include
    assert not r.applies_to("app/src/test/thing.ts")  # inside exclude
    assert not r.applies_to(None)  # no context
    assert r.path_scoped


def test_path_matching_is_case_and_separator_insensitive() -> None:
    """Windows checkouts must behave identically to POSIX ones."""
    code = "const rows = await db.execute(sql);"
    assert "AP-S1.103a" in _fired(code, file=r"App\Components\Cart.tsx")


# ─── AP-S1.103a — data access in the presentation layer ──────────────────────


def test_database_access_in_a_component_is_blocking() -> None:
    code = "const rows = await db.execute('SELECT * FROM orders');"
    findings = scan_text(code, file="src/components/OrderList.tsx")
    hit = next(f for f in findings if f.anti_pattern == "AP-S1.103a")
    assert hit.blocking, "a component reaching the database is unambiguous — it must block"


def test_a_service_reaching_the_database_is_not_a_presentation_violation() -> None:
    fired = _fired("await db.execute(q)", file="src/services/order_service.py")
    assert "AP-S1.103a" not in fired


def test_a_component_test_is_not_a_presentation_violation() -> None:
    fired = _fired("await db.execute(q)", file="src/components/__tests__/OrderList.test.tsx")
    assert "AP-S1.103a" not in fired


# ─── AP-S1.104a — data access outside the repository layer ───────────────────


def test_raw_access_outside_the_repository_layer_warns() -> None:
    findings = scan_text("session.query(User).all()", file="src/api/routes/users.py")
    hit = next(f for f in findings if f.anti_pattern == "AP-S1.104a")
    assert not hit.blocking, "layer inference is context-dependent — advisory, never blocking"


def test_a_repository_doing_data_access_is_not_a_violation() -> None:
    """The whole point of a repository. If this fires, the rule is worthless."""
    for path in (
        "src/repositories/user_repository.py",
        "src/dao/UserDao.java",
        "app/data-access/orders.ts",
        "src/repository/orders.ts",
    ):
        assert "AP-S1.104a" not in _fired("session.query(User).all()", file=path), path


def test_migrations_seeds_and_tests_may_use_raw_access() -> None:
    for path in (
        "migrations/0001_init.py",
        "prisma/seed.ts",
        "alembic/versions/abc.py",
        "tests/test_orders.py",
        "src/orders.spec.ts",
        "conftest.py",
    ):
        assert "AP-S1.104a" not in _fired("db.execute(sql)", file=path), path


# ─── AP-S1.105a — environment values inlined ─────────────────────────────────


def test_hardcoded_service_url_is_flagged() -> None:
    assert "AP-S1.105a" in _fired(
        'const apiUrl = "https://api.production.example-corp.io/v1";',
        file="src/config.ts",
    )


def test_localhost_and_schema_urls_are_not_configuration_leaks() -> None:
    for line in (
        'const baseUrl = "http://localhost:3000";',
        'const apiUrl = "http://127.0.0.1:8000";',
        'xmlns = "http://www.w3.org/2000/svg"',
        'const endpoint = "https://example.com/docs";',
    ):
        assert "AP-S1.105a" not in _fired(line, file="src/config.ts"), line


def test_a_url_read_from_configuration_is_not_flagged() -> None:
    assert "AP-S1.105a" not in _fired(
        'const apiUrl = process.env.API_URL;', file="src/config.ts"
    )


# ─── AP-D-FINTECH.1a — money through a float ─────────────────────────────────


def test_money_coerced_to_float_is_blocking() -> None:
    for line in (
        "const total = parseFloat(amountRaw);",
        "price: number = 12.5",
        "value = float(balance_raw)",
        "const n = Number(totalDue);",
    ):
        assert "AP-D-FINTECH.1a" in _fired(line, file="src/billing.ts"), line


def test_ordinary_numeric_code_is_not_a_money_violation() -> None:
    for line in (
        "const ratio = parseFloat(percentage);",
        "count: number = 3",
        "timeout = float(seconds)",
        "const n = Number(pageIndex);",
    ):
        assert "AP-D-FINTECH.1a" not in _fired(line, file="src/billing.ts"), line


def test_money_float_in_a_test_fixture_is_not_flagged() -> None:
    assert "AP-D-FINTECH.1a" not in _fired(
        "const total = parseFloat(x);", file="src/billing.test.ts"
    )


def test_integer_minor_units_are_not_a_money_violation() -> None:
    """The rule blocked the remedy its own standard prescribes.

    Measured on a real DebiCheck submission path, where cents were carried as
    integers — money done correctly — and the gate failed the build for it. A
    developer who read the finding, applied D-FINTECH.1 and re-ran got the same
    finding back, so compliance was unreachable through the tool's own advice.
    """
    for line in (
        "  totalCents: number",
        "  collectionAmountCents: number",
        "  maximumCollectionAmountCents: number",
        "  total_cents: number",
        "  amountMinor: number",
    ):
        assert "AP-D-FINTECH.1a" not in _fired(line, file="src/netcash.ts"), line


def test_a_counter_is_not_money_however_it_is_spelled() -> None:
    """`totalPages` in a pagination type is not a rand, and neither is a count
    of months sitting beside `currentStreak` and `longestStreak`."""
    for line in (
        "  totalPages: number",
        "  initialTotalPages: number",
        "  totalItems: number",
        "  totalCount: number",
        "  totalPaidMonths: number",
        "  totalOnTimeMonths: number",
        "  paymentDays: number",
    ):
        assert "AP-D-FINTECH.1a" not in _fired(line, file="src/api-response.ts"), line


def test_the_suffix_guard_does_not_silence_real_money() -> None:
    """The guard reads the rest of the identifier, not any later word on the
    line — so a money field keeps firing even where a counter word is nearby."""
    for line in (
        "  amount: number",
        "  amountDue: number",
        "  amountPaid: number",
        "  totalPaid: number",
        "  totalOverdue: number",
        "  monthlyAmount: number",
        "  priceMonthly: number",
        "  amount: number  // alongside totalPages: number",
    ):
        assert "AP-D-FINTECH.1a" in _fired(line, file="src/ledger.ts"), line


def test_a_bare_total_still_fires() -> None:
    """Deliberate, and recorded rather than assumed. `total: number` is genuinely
    ambiguous — one instance in the measured codebase was a pagination field and
    the rest were money — so it stays with the majority reading. This test is
    where a decision to change that gets made."""
    assert "AP-D-FINTECH.1a" in _fired("  total: number", file="src/invoice.ts")


# ─── AP-D-FINTECH.3a — balance mutated in place ──────────────────────────────


def test_balance_mutated_in_place_is_blocking() -> None:
    for line in (
        "account.balance = account.balance + amount",
        "balance += amount",
        "UPDATE accounts SET balance = balance - 100",
    ):
        assert "AP-D-FINTECH.3a" in _fired(line, file="src/ledger.py"), line


def test_deriving_a_balance_from_entries_is_not_a_violation() -> None:
    for line in (
        "balance = sum(e.amount for e in entries)",
        "const balance = entries.reduce((a, e) => a.plus(e.amount), ZERO);",
        "counter += 1",
    ):
        assert "AP-D-FINTECH.3a" not in _fired(line, file="src/ledger.py"), line


# ─── AP-D-FINTECH.6b — approximate monetary assertion ────────────────────────


def test_approximate_monetary_assertion_is_blocking() -> None:
    for line in (
        "self.assertAlmostEqual(invoice.total, 100.00)",
        "expect(result.amount).toBeCloseTo(9.99)",
    ):
        assert "AP-D-FINTECH.6b" in _fired(line, file="tests/test_billing.py"), line


def test_approximate_assertion_on_a_non_monetary_value_is_fine() -> None:
    assert "AP-D-FINTECH.6b" not in _fired(
        "self.assertAlmostEqual(ratio, 0.33)", file="tests/test_stats.py"
    )


def test_the_monetary_assertion_rule_is_not_excluded_from_tests() -> None:
    """It exists to police test code, so excluding test paths would disable it."""
    assert _rule("AP-D-FINTECH.6b").path_exclude is None


# ─── AP-D-SAAS.1b — tenant identity from client input ────────────────────────


def test_tenant_id_from_request_input_is_blocking() -> None:
    for line in (
        "const tenantId = req.query.tenantId;",
        'const t = req.headers["x-tenant-id"];',
        "tenant = request.body.tenant_id",
        "org = req.params.organisation_id",
    ):
        assert "AP-D-SAAS.1b" in _fired(line, file="src/api/orders.ts"), line


def test_tenant_id_from_the_session_is_correct_and_not_flagged() -> None:
    for line in (
        "const tenantId = session.user.tenantId;",
        "tenant_id = current_user.tenant_id",
        "const t = ctx.auth.tenantId;",
    ):
        assert "AP-D-SAAS.1b" not in _fired(line, file="src/api/orders.ts"), line


def test_an_unrelated_request_parameter_is_not_flagged() -> None:
    assert "AP-D-SAAS.1b" not in _fired("const id = req.query.orderId;", file="src/api/o.ts")


# ─── Rule-set governance ─────────────────────────────────────────────────────


def test_every_rule_remains_grounded_in_the_constitution() -> None:
    assert validate_rules() == []


def test_domain_rules_bind_real_domain_anti_patterns() -> None:
    defined = domain_anti_patterns()
    bound = {r.anti_pattern for r in RULES if r.anti_pattern.startswith("AP-D-")}
    assert bound, "no domain rule bound — Layer 4 would be unenforced"
    assert bound <= defined


def test_no_rule_for_the_two_standards_with_no_deterministic_signature() -> None:
    """DRY and 'simplest correct solution' are semantic-tier concerns.

    Writing a regex for them would trade the gate's trustworthiness for a
    coverage number, so their absence is deliberate and asserted.
    """
    bound = {r.anti_pattern for r in RULES}
    assert "AP-S1.106a" not in bound
    assert "AP-S1.107a" not in bound


def test_confidence_values_are_valid() -> None:
    valid: set[Confidence] = {"high", "medium"}
    assert all(r.confidence in valid for r in RULES)


def test_path_scoped_rules_all_declare_a_usable_predicate() -> None:
    for rule in RULES:
        if rule.path_scoped:
            assert rule.path_include is not None or rule.path_exclude is not None
            assert not rule.applies_to(None)
