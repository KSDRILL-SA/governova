"""Four rules for the API contract, and two standards deliberately left without one.

`#246` counts standards, so this batch is one rule each for `S2.76`, `S1.55`,
`S2.23` and `S2.19` — all previously unevidenced, and none of them a line any
existing rule already claims.

Two of the four have a near-twin in the corpus, and neither twin gets a rule:

- `S2.20` says `data: null` is wrong for a **collection**, where the correct
  value is `[]`. A line scanner cannot tell whether an endpoint returns a
  collection; the fact on the line is `data: null` and nothing more. `S2.19b` is
  the claim the evidence actually supports.
- `S6.22` requires the `/api/v1/` prefix and cites `S2.76` for the versioning
  policy it enforces, so the rule is written once, against the standard that
  owns it.

Binding both halves of either pair would report one line under two standards.
That is how three duplicate rules reached `rules.py` before, and it buys
constitutional coverage with a second name for a finding that already exists.
"""

from __future__ import annotations

import pytest
from governova_checks import scan_text
from governova_checks.rules import RULES

SERVICE = "src/services/student-service.ts"
ROUTER = "src/routers/student-router.ts"

NEW_RULES = ("AP-S2.76a", "AP-S1.55a", "AP-S2.23a", "AP-S2.19b")


def _hits(text: str, file: str | None = None) -> set[str]:
    return {f.anti_pattern for f in scan_text(text, file=file)}


# ─── AP-S2.76a — a route with no version in the path ────────────────────────


@pytest.mark.parametrize(
    "line",
    ['router.get("/api/students", handler)', 'app.get("/api/students", handler)'],
)
def test_an_unversioned_endpoint_is_reported(line: str) -> None:
    """An unversioned route cannot gain a v2 beside it."""
    assert "AP-S2.76a" in _hits(line, ROUTER)


@pytest.mark.parametrize(
    "line",
    ['router.get("/api/v1/students", handler)', 'router.get("/api/v2/students", handler)'],
)
def test_a_versioned_endpoint_is_not_reported(line: str) -> None:
    assert "AP-S2.76a" not in _hits(line, ROUTER)


def test_a_path_that_merely_starts_with_api_is_not_reported() -> None:
    """`/apiary/` is not `/api/`, and the boundary is the whole rule."""
    assert "AP-S2.76a" not in _hits('router.get("/apiary/students")', ROUTER)


def test_a_call_site_outside_the_router_layer_is_not_reported() -> None:
    """`S2.76` governs the endpoint, not everyone who calls it.

    A frontend requesting an unversioned URL is a symptom of a backend that
    declared one, and it is fixable only at the declaration. Scoping matters
    here for a second reason: unscoped, this fired on
    `this.http.get('/api/students')` inside an Angular component, which
    `AP-S4.55a` already reports for a different and equally true reason — the
    component is calling the network at all. `test_no_line_produces_findings_from_two_standards`
    caught that before it landed.
    """
    component = "src/components/student-list.component.ts"
    assert "AP-S2.76a" not in _hits("this.http.get('/api/students')", component)
    assert "AP-S4.55a" in _hits("this.http.get('/api/students')", component)


# ─── AP-S1.55a — a type parameter with no name ──────────────────────────────


@pytest.mark.parametrize(
    "line",
    [
        "export function fetchAll<T>(url: string) {",
        "export function map<T, U>(x: T): U {",
        "export interface Repository<T> {",
    ],
)
def test_a_single_letter_generic_in_a_service_is_reported(line: str) -> None:
    assert "AP-S1.55a" in _hits(line, SERVICE)


def test_a_named_type_parameter_is_not_reported() -> None:
    assert "AP-S1.55a" not in _hits("export function fetchAll<TEntity>(url: string) {", SERVICE)


def test_a_single_letter_generic_outside_service_code_is_not_reported() -> None:
    """`S1.55` permits one "in utility types where the abstraction is so total
    that no meaningful name exists" — so the rule is scoped to the layer the
    standard actually addresses. A rule that fired in `utils/` would be grading
    against a rubric wider than its own standard."""
    assert "AP-S1.55a" not in _hits("export function fetchAll<T>(url: string) {", "src/utils/http.ts")


# ─── AP-S2.23a — unvalidated request data past the boundary ─────────────────


@pytest.mark.parametrize(
    "line",
    ["const email = request.body.email;", "const page = req.query.page;"],
)
def test_raw_request_data_in_a_service_is_reported(line: str) -> None:
    """Reaching the service means it came through the boundary, and the
    boundary's job was to replace it with a validated value."""
    assert "AP-S2.23a" in _hits(line, SERVICE)


def test_raw_request_data_in_a_router_is_not_reported() -> None:
    """The router is exactly where `request.body` is supposed to be touched.

    That is the boundary doing its job. A rule that fired here would report the
    correct code and miss what the standard is about — which is the reason this
    one is scoped more narrowly than `BACKEND_PATHS`.
    """
    assert "AP-S2.23a" not in _hits("const email = request.body.email;", ROUTER)


def test_a_validated_value_is_not_reported() -> None:
    assert "AP-S2.23a" not in _hits("const email = validated.email;", SERVICE)


# ─── AP-S2.19b — a null where the payload belongs ───────────────────────────


@pytest.mark.parametrize(
    "line",
    ['return res.json({ data: null, message: "ok" });', 'return {"data": None, "message": "ok"}'],
)
def test_a_null_data_field_is_reported(line: str) -> None:
    """Both spellings of one defect — a client cannot tell empty from failed."""
    assert "AP-S2.19b" in _hits(line)


def test_an_empty_collection_is_the_correct_form_and_is_not_reported() -> None:
    assert "AP-S2.19b" not in _hits("return res.json({ data: [], count: 0 });")


def test_another_field_being_null_is_not_reported() -> None:
    """The standard is about `data`. `metadata: null` is somebody else's business."""
    assert "AP-S2.19b" not in _hits("return res.json({ metadata: null });")


# ─── The two standards deliberately left without a rule ─────────────────────


def test_a_null_data_field_is_reported_once_not_twice() -> None:
    """`S2.20` makes the same claim about a collection and gets no rule.

    Its anti-pattern is "`data: null` when list is empty", and a line scanner
    cannot know the endpoint returns a list. Binding it as well would report one
    line under two standards and buy a unit of coverage with a second name for
    a finding that already exists.
    """
    hits = _hits('return res.json({ data: null });')
    assert hits == {"AP-S2.19b"}, hits
    assert "AP-S2.20a" not in {rule.anti_pattern for rule in RULES}


def test_an_unversioned_route_is_reported_once_not_twice() -> None:
    """`S6.22` requires the same prefix and cites `S2.76` for the policy."""
    hits = _hits('router.get("/api/students", handler)', ROUTER)
    assert hits == {"AP-S2.76a"}, hits
    assert "AP-S6.22a" not in {rule.anti_pattern for rule in RULES}


# ─── Registration and grounding ─────────────────────────────────────────────


def test_each_rule_covers_a_distinct_standard() -> None:
    registered = {rule.anti_pattern for rule in RULES}
    assert set(NEW_RULES) <= registered

    standards = {rule.standard for rule in RULES if rule.anti_pattern in NEW_RULES}
    assert standards == {"S2.76", "S1.55", "S2.23", "S2.19"}, standards


def test_the_new_rules_bind_anti_patterns_the_corpus_defines() -> None:
    """`REQ-006`. A rule citing law that does not exist is drift, not evidence."""
    from pathlib import Path

    from governova_checks.coverage import validate_rules
    from governova_compile.discovery import resolve_repo_root
    from governova_compile.writer import load_index

    index = load_index(Path(resolve_repo_root()) / "compiled" / "constitution.json")
    assert validate_rules(index) == []
