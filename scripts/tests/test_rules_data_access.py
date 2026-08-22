"""Three rules for the data-access layer, and the reason a fourth was dropped.

`#246` counts **standards**, not rules. Two rules on one standard buy one unit of
coverage, so this batch is deliberately breadth-first: one rule each for `S5.11`,
`S5.14` and `S5.17`, all previously unevidenced.

The hard part here is not the detection, it is the line boundary. A Prisma call
is usually written across several lines:

    const users = await prisma.user.findMany({
      where: { active: true },
      select: { id: true, email: true },
    });

That is the **correct** spelling, and a line-scanning rule looking for `findMany`
without `select` sees only the first line and reports it. Every pattern here
requires the call to close on the same line it opens, so the multi-line form is
invisible to it. That is a deliberate gap: these rules catch the single-line
violation and miss the multi-line one, which is the right way round, because the
alternative reports correct code in every repository that uses Prisma.
"""

from __future__ import annotations

import pytest
from governova_checks import scan_text
from governova_checks.rules import RULES

NEW_RULES = ("AP-S5.11a", "AP-S5.14a", "AP-S5.17a")


def _hits(text: str) -> set[str]:
    return {f.anti_pattern for f in scan_text(text)}


# ─── AP-S5.11a — findMany with no select ────────────────────────────────────


@pytest.mark.parametrize(
    "line",
    [
        "const users = await prisma.user.findMany();",
        "const users = await prisma.user.findMany({ where: { active: true } });",
    ],
)
def test_findmany_without_a_select_is_reported(line: str) -> None:
    """The default returns every column, including the ones nobody meant to read."""
    assert "AP-S5.11a" in _hits(line)


def test_a_select_on_the_same_line_is_not_reported() -> None:
    assert "AP-S5.11a" not in _hits(
        "const users = await prisma.user.findMany({ select: { id: true } });"
    )


def test_the_multiline_form_is_invisible_to_the_rule() -> None:
    """The gap that keeps this rule usable, asserted so nobody closes it.

    A rule that matched this line would report the opening of every correctly
    written Prisma call in existence — the `select` is two lines below and a
    line scanner cannot see it. Widening this pattern to catch the multi-line
    case means reporting correct code, and a report whose findings are mostly
    false does not get read at all.
    """
    assert "AP-S5.11a" not in _hits("  const users = await prisma.user.findMany({")


# ─── AP-S5.14a — a filtered query with no bound ─────────────────────────────


def test_a_filtered_findmany_without_take_is_reported() -> None:
    assert "AP-S5.14a" in _hits(
        "const rows = await prisma.scholarship.findMany({ where: { status: 'ACTIVE' } });"
    )


def test_a_take_on_the_same_line_is_not_reported() -> None:
    assert "AP-S5.14a" not in _hits(
        "const rows = await prisma.s.findMany({ where: { a: 1 }, take: 50 });"
    )


def test_an_unfiltered_query_belongs_to_a_different_standard() -> None:
    """`S5.14` is about a filter that cannot bound its result set.

    A bare `findMany()` is `AP-S2.14a`'s subject — an unbounded query with no
    pagination at all — and that rule already existed. Requiring a `where` here
    keeps the two claims apart instead of giving one line two names.
    """
    bare = _hits("const users = await prisma.user.findMany();")
    assert "AP-S2.14a" in bare
    assert "AP-S5.14a" not in bare


def test_the_two_findmany_rules_make_different_claims() -> None:
    """They co-fire on one line, and that is two findings rather than one twice.

    "returns every column" and "returns every row" are separate defects with
    separate fixes. A reviewer who adds `select` has not bounded the result set,
    and a reviewer who adds `take` is still leaking the password hash.
    """
    both = _hits("const rows = await prisma.s.findMany({ where: { active: true } });")
    assert {"AP-S5.11a", "AP-S5.14a"} <= both

    only_select_missing = _hits(
        "const rows = await prisma.s.findMany({ where: { a: 1 }, take: 50 });"
    )
    assert only_select_missing & {"AP-S5.11a"}
    assert not only_select_missing & {"AP-S5.14a"}


# ─── AP-S5.17a — an assertion over the generated type ───────────────────────


def test_a_type_assertion_on_a_prisma_result_is_reported() -> None:
    assert "AP-S5.17a" in _hits(
        "const user = (await prisma.user.findUnique({ where: { id } })) as CustomUser;"
    )


def test_as_const_is_not_a_type_assertion_over_the_model() -> None:
    """`as const` narrows a literal. It makes no claim the schema could falsify."""
    assert "AP-S5.17a" not in _hits(
        "const ids = (await prisma.user.findMany({ select: { id: true } })) as const;"
    )


# ─── The rule that was written and removed ──────────────────────────────────


def test_sql_string_interpolation_is_detected_once_not_twice() -> None:
    """A rule for `AP-S2.27a` was written for this batch and dropped before landing.

    It matched exactly the lines `AP-S2.28f` already matches — the same defect,
    reported twice under two standards. That inflates every count drawn from
    findings, and it buys a unit of constitutional coverage with a second name
    for something already detected, which is buying it dishonestly.

    Three duplicates reached this file once before and were found only when a
    measurement showed `expressjs/express` reporting 36 lines 72 times. This
    asserts the partition rather than trusting anyone to remember it.
    """
    hits = _hits("const q = `SELECT * FROM users WHERE id = ${userId}`;")
    assert "AP-S2.28f" in hits
    assert "AP-S2.27a" not in hits
    assert "AP-S2.27a" not in {rule.anti_pattern for rule in RULES}


def test_a_parameterised_query_is_not_reported() -> None:
    """The whole point of the standard is that this form is the fix."""
    assert not _hits('cur.execute("SELECT id FROM users WHERE email = %s", (email,))')
    assert not _hits("db.query('SELECT * FROM users WHERE id = $1', [userId])")


# ─── Registration and grounding ─────────────────────────────────────────────


def test_each_new_rule_covers_a_standard_that_had_no_evidence_before() -> None:
    """Breadth-first is the point: coverage counts standards, not rules."""
    registered = {rule.anti_pattern for rule in RULES}
    assert set(NEW_RULES) <= registered

    standards = {rule.standard for rule in RULES if rule.anti_pattern in NEW_RULES}
    assert standards == {"S5.11", "S5.14", "S5.17"}, standards


def test_the_new_rules_bind_anti_patterns_the_corpus_defines() -> None:
    """`REQ-006`. A rule citing law that does not exist is drift, not evidence."""
    from pathlib import Path

    from governova_checks.coverage import validate_rules
    from governova_compile.discovery import resolve_repo_root
    from governova_compile.writer import load_index

    index = load_index(Path(resolve_repo_root()) / "compiled" / "constitution.json")
    assert validate_rules(index) == []
