"""Six rules added against `#246`'s ceiling programme, and the guard that caught a bug in them.

`#246` is linear in one factor: the score is `76.25 + 0.20 × constitutional
coverage`, and coverage moves when a standard acquires evidence. A rule is one
of the three ways a standard gets it.

Each rule below is asserted two ways — it fires on the real thing, and it stays
silent on the correct form of the same code. The second half is the one that
matters: a rule that reports correct code is a rule people switch off, and then
the standard behind it is enforced by nothing at all.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from governova_checks import scan_text
from governova_checks.rules import RULES
from governova_compile.discovery import resolve_repo_root

NEW_RULES = (
    "AP-S2.10a",
    "AP-S2.12a",
    "AP-S2.12c",
    "AP-S2.17b",
    "AP-S2.21a",
    "AP-S4.20a",
)


def _hits(text: str, *, file: str | None = None) -> set[str]:
    return {f.anti_pattern for f in scan_text(text, file=file)}


# ─── AP-S2.10a — behaviour branching on the environment name ─────────────────


@pytest.mark.parametrize(
    "line",
    [
        "if (process.env.NODE_ENV === 'production') { skipAudit(); }",
        "if os.environ['ENV'] == 'production':",
        "if (APP_ENV == 'prod') { useRealGateway(); }",
    ],
)
def test_branching_on_the_environment_is_reported(line: str) -> None:
    """The production path is the one nobody exercised before shipping it."""
    assert "AP-S2.10a" in _hits(line)


@pytest.mark.parametrize(
    "line",
    [
        # Reading it is how a build chooses a bundle. Only the *branch* is the
        # anti-pattern, so the assignment has to stay clean or the rule fires on
        # every config file in every repository it is pointed at.
        "const isProd = process.env.NODE_ENV === 'production';",
        "level = os.environ.get('ENV', 'development')",
    ],
)
def test_reading_the_environment_is_not_reported(line: str) -> None:
    assert "AP-S2.10a" not in _hits(line)


# ─── AP-S2.12a / AP-S2.12c — the path is not the verb ───────────────────────


@pytest.mark.parametrize(
    "line",
    ['fetch("/api/v1/getStudentProfile")', "router.post('/api/v1/create-student')"],
)
def test_a_verb_in_the_path_is_reported(line: str) -> None:
    assert "AP-S2.12a" in _hits(line)


@pytest.mark.parametrize(
    "line",
    [
        'fetch("/api/v1/students")',
        # A collection whose name merely begins with a verb. `updates` and
        # `posts` are ordinary resources, and a rule that renames them is a rule
        # that gets switched off.
        'fetch("/api/v1/updates")',
        'fetch("/api/v1/posts")',
    ],
)
def test_a_resource_that_reads_like_a_verb_is_not_reported(line: str) -> None:
    assert "AP-S2.12a" not in _hits(line)


def test_nesting_past_two_levels_is_reported() -> None:
    assert "AP-S2.12c" in _hits('app.get("/api/v1/schools/{id}/students/{sid}/grades/{gid}")')


def test_two_levels_of_nesting_is_the_documented_limit() -> None:
    """The version segment is not one of the two, which is where an off-by-one lives."""
    assert "AP-S2.12c" not in _hits('app.get("/api/v1/schools/{id}/students")')


# ─── AP-S2.17b — an origin that only a deploy can change ────────────────────


@pytest.mark.parametrize(
    "line",
    ['allow_origins=["https://app.example.com"]', "const allowedOrigins = ['https://foo.co.za']"],
)
def test_a_hardcoded_origin_is_reported(line: str) -> None:
    assert "AP-S2.17b" in _hits(line)


@pytest.mark.parametrize(
    "line",
    [
        "allow_origins=[settings.cors_origins]",
        # Localhost is excluded deliberately. It is the one origin that is the
        # same in every environment, so it is the one literal that is not a
        # value somebody will need to change without a deploy.
        'allow_origins=["http://localhost:3000"]',
    ],
)
def test_a_configured_or_local_origin_is_not_reported(line: str) -> None:
    assert "AP-S2.17b" not in _hits(line)


def test_the_hardcoded_origin_rule_is_distinct_from_the_wildcard_rules() -> None:
    """Three CORS rules exist and they must not be three names for one finding.

    `AP-S2.17a` and `AP-S3.29a` catch `*`. This one catches a real URL. Three
    duplicate rules were removed from this file once already after they inflated
    a measured count; the way that does not happen again is to check the
    partition rather than to remember it.
    """
    wildcard = _hits('allow_origins=["*"]')
    literal = _hits('allow_origins=["https://app.example.com"]')
    assert "AP-S2.17b" not in wildcard
    assert not literal & {"AP-S2.17a", "AP-S3.29a"}


# ─── AP-S2.21a — a create that answers 200 ──────────────────────────────────


@pytest.mark.parametrize(
    "line",
    ['@router.post("/students", status_code=200)', '@app.post("/x", status_code=status.HTTP_200_OK)'],
)
def test_a_post_declared_to_return_200_is_reported(line: str) -> None:
    assert "AP-S2.21a" in _hits(line)


@pytest.mark.parametrize("line", ['@router.post("/students", status_code=201)', "@Get()"])
def test_a_correct_status_declaration_is_not_reported(line: str) -> None:
    assert "AP-S2.21a" not in _hits(line)


def test_the_nestjs_form_is_a_known_gap_rather_than_a_false_positive() -> None:
    """`@HttpCode(HttpStatus.OK)` sits on its own line, above GET as often as POST.

    Catching it would mean firing on correct code. The rule declines, and this
    records that the silence is a decision rather than an oversight — so nobody
    "fixes" it later by widening the pattern and reintroducing the false
    positive it was narrowed to avoid.
    """
    assert "AP-S2.21a" not in _hits("@HttpCode(HttpStatus.OK)")


# ─── AP-S4.20a — the input that zooms iOS Safari ────────────────────────────


@pytest.mark.parametrize(
    "line",
    ["input { font-size: 14px; }", 'input[type="text"] { color: red; font-size: 0.875rem; }'],
)
def test_a_small_form_input_is_reported(line: str) -> None:
    assert "AP-S4.20a" in _hits(line)


@pytest.mark.parametrize("line", ["body { font-size: 14px; }", "p { font-size: 0.875rem; }"])
def test_small_body_copy_is_not_reported(line: str) -> None:
    """14px prose is a design choice. 14px in an input is a broken viewport."""
    assert "AP-S4.20a" not in _hits(line)


def test_an_input_at_the_threshold_is_not_reported() -> None:
    assert "AP-S4.20a" not in _hits("input { font-size: 16px; }")


# ─── The rule set does not report itself ────────────────────────────────────


def test_the_rule_set_is_excluded_from_the_scan_surface() -> None:
    """`rules.py` is a file of patterns describing defects, so it resembles one.

    Fourteen rules match the lines that define them — `AP-S3.29a`'s message
    quotes the wildcard CORS call it detects, `AP-S5.28a`'s pattern contains the
    float declaration it looks for. That is unavoidable: a rule that cannot
    describe what it detects is a rule nobody can review.

    `gather.DEFAULT_IGNORES` is what keeps those out of every report, and it is
    a one-line exclusion that a future cleanup could delete without any visible
    symptom in this repository — until a consumer who vendors the engine gets
    fourteen findings that are not real. So the exclusion is asserted here
    rather than trusted.

    Found while adding the six rules above: an ad-hoc sweep that read files
    directly, bypassing `gather`, reported `AP-S2.12a` against this file. That
    was an artefact of the sweep rather than a defect in the rule — but it is
    exactly what a consumer would see if this exclusion went away.
    """
    from governova_checks.gather import DEFAULT_IGNORES, is_ignored

    assert is_ignored("scripts/governova_checks/rules.py", DEFAULT_IGNORES), (
        "the rule set is scannable; every rule that quotes what it detects "
        "becomes a finding in any repository carrying the engine"
    )


def test_none_of_the_six_new_rules_needs_that_exclusion() -> None:
    """The exclusion is a safety net, not a licence to write self-matching rules.

    A rule that only stays quiet because one file is skipped is a rule whose
    message cannot be quoted in a runbook, an ADR or an error string without
    reappearing somewhere else. These six are clean on their own definitions.
    """
    import ast

    rules_file = Path(resolve_repo_root()) / "scripts" / "governova_checks" / "rules.py"
    source = rules_file.read_text(encoding="utf-8")
    lines = source.splitlines()

    blocks: dict[str, tuple[int, int]] = {}
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call) or getattr(node.func, "id", None) != "Rule":
            continue
        first = node.args[0] if node.args else None
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            blocks[first.value] = (node.lineno, node.end_lineno or node.lineno)
    assert len(blocks) > 60, "the block scan found almost nothing; the parse is wrong"

    offenders: list[str] = []
    for rule in RULES:
        if rule.anti_pattern not in NEW_RULES:
            continue
        start_line, end_line = blocks[rule.anti_pattern]
        for offset, line in enumerate(lines[start_line - 1 : end_line], start=start_line):
            if rule.pattern.search(line):
                offenders.append(f"{rule.anti_pattern} matches its own line {offset}")

    assert not offenders, "; ".join(offenders)


def test_the_new_rules_are_all_registered() -> None:
    """A rule that was written and not added to `RULES` evidences nothing."""
    registered = {rule.anti_pattern for rule in RULES}
    assert set(NEW_RULES) <= registered


def test_the_new_rules_bind_anti_patterns_the_corpus_defines() -> None:
    """`REQ-006`. A rule citing law that does not exist is drift, not evidence."""
    from governova_checks.coverage import validate_rules
    from governova_compile.writer import load_index

    index = load_index(Path(resolve_repo_root()) / "compiled" / "constitution.json")
    assert validate_rules(index) == []
