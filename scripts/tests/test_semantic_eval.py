"""Tests for the semantic evaluation harness.

Every backend here is a fake transport — no network, fully deterministic. The harness
measures a model; these tests measure the harness, and the two must not be confused.

The governance test in this file is `test_every_fixture_cites_a_real_standard`. It is the
same guarantee `validate_rules()` gives the reliable tier: a fixture expecting a standard
that does not exist is testing fiction, and would report a backend as wrong for correctly
declining to invent it.
"""

from __future__ import annotations

import json
import re

from governova_compile.discovery import resolve_repo_root
from governova_compile.writer import load_index
from governova_semantic import (
    MIN_PRECISION,
    MIN_RECALL,
    SemanticConfig,
    evaluate,
)
from governova_semantic.client import SemanticUnavailableError
from governova_semantic.config import from_env
from governova_semantic.fixtures import FIXTURES, Fixture, expected_standards

INDEX = load_index(resolve_repo_root() / "compiled" / "constitution.json")
ACTIVE = SemanticConfig(model="probe-model", base_url="https://endpoint.example/v1", api_key="k")


def _backend(behaviour):
    """Build a fake transport from a function of (code) -> list of standard ids."""

    def transport(cfg, messages):
        code = messages[-1]["content"]
        return json.dumps(
            {
                "findings": [
                    {"standard": sid, "line": 1, "message": "fixture backend"}
                    for sid in behaviour(code)
                ]
            }
        )

    return transport


def _perfect(code: str) -> list[str]:
    """A backend that reports exactly what each fixture expects."""
    for fixture in FIXTURES:
        if fixture.code.strip() in code:
            return sorted(fixture.expected)
    return []


# ─── The governance guarantee ────────────────────────────────────────────────


def test_every_fixture_cites_a_real_standard():
    """A fixture naming a standard that does not exist is testing fiction.

    The same guarantee `validate_rules()` gives the reliable tier. Without it, the harness
    could mark a backend wrong for correctly refusing to invent a standard.
    """
    known = {s.id for c in INDEX.constitutions for s in c.standards}
    unknown = sorted(expected_standards() - known)
    assert unknown == [], f"fixtures expect standards that do not exist: {unknown}"


def test_the_fixture_set_measures_both_directions():
    # Precision is measured only by clean fixtures and recall only by violating ones.
    # A set with none of either silently measures half of what it claims to.
    assert any(f.is_clean for f in FIXTURES), "no clean fixtures — precision is unmeasured"
    assert any(not f.is_clean for f in FIXTURES), "no violating fixtures — recall is unmeasured"


def test_fixture_ids_are_unique():
    ids = [f.id for f in FIXTURES]
    assert len(ids) == len(set(ids))


# ─── Scoring ─────────────────────────────────────────────────────────────────


def test_a_perfect_backend_scores_perfectly_and_passes():
    report = evaluate(index=INDEX, config=ACTIVE, transport=_backend(_perfect))
    assert report.assessed
    assert report.precision == 1.0
    assert report.recall == 1.0
    assert report.false_positives == 0
    assert report.clean_fixtures_kept_clean == report.clean_fixtures
    assert report.passed is True


def test_a_hallucinating_backend_fails_on_precision():
    """The failure that matters. A backend inventing findings on clean code is unusable,
    however much it also gets right.

    The invented standard is drawn from the prompt's own catalogue, because that is the
    realistic threat: `parse_findings` already drops citations outside the grounded set,
    so a model can only mislead by misapplying a standard it *was* shown.
    """
    catalogue = re.compile(r"^- (S\d+\.\d+):", re.M)

    def noisy(cfg, messages):
        prompt = messages[-1]["content"]
        expected = set(_perfect(prompt))
        grounded = [sid for sid in catalogue.findall(prompt) if sid not in expected]
        reported = sorted(expected | ({grounded[0]} if grounded else set()))
        return json.dumps(
            {"findings": [{"standard": sid, "line": 1, "message": "x"} for sid in reported]}
        )

    report = evaluate(index=INDEX, config=ACTIVE, transport=noisy)
    assert report.false_positives > 0
    assert report.precision is not None and report.precision < MIN_PRECISION
    assert report.passed is False
    # Recall is untouched — it found everything real. Precision alone sinks it.
    assert report.recall == 1.0


def test_an_invention_outside_the_grounded_set_is_dropped_before_scoring():
    """The anti-hallucination filter is upstream of the harness, and stays there.

    A backend citing a standard it was never shown is discarded by `parse_findings`, so
    it can never reach the score. Worth pinning: if that filter were ever loosened, this
    harness would start measuring a threat it currently cannot see.
    """

    def cites_ungrounded(code: str) -> list[str]:
        return [*_perfect(code), "S8.99"]  # not a real standard, never grounded

    report = evaluate(index=INDEX, config=ACTIVE, transport=_backend(cites_ungrounded))
    assert report.false_positives == 0
    assert report.precision == 1.0


def test_a_defensible_finding_is_neither_a_hit_nor_an_invention():
    """The neutral class, added after the first real measurement.

    A 120b model scored well below its real accuracy because most of its "inventions"
    were correct —
    `S1.50` (explicit return types) is genuinely violated by these Python snippets.
    Scoring a correct finding as an invention measures how completely the fixture was
    annotated, not how good the backend is.
    """
    fixture = next(f for f in FIXTURES if f.acceptable)
    extra = sorted(fixture.acceptable)[0]

    def also_acceptable(code: str) -> list[str]:
        # Only on the fixture that tolerates it. Adding it everywhere would be a real
        # invention on fixtures that do not — `clean-plain-utility` declares its return
        # type, so `S1.50` there would be genuinely wrong.
        found = set(_perfect(code))
        if fixture.code.strip() in code:
            found.add(extra)
        return sorted(found)

    report = evaluate(index=INDEX, config=ACTIVE, transport=_backend(also_acceptable))
    assert report.false_positives == 0, "a defensible finding was scored as an invention"
    assert report.precision == 1.0
    assert report.tolerated_extras > 0, "the defensible findings should still be reported"


def test_a_clean_fixture_tolerating_an_extra_still_counts_as_kept_clean():
    # Otherwise `clean kept clean` silently measures annotation completeness too.
    clean = next(f for f in FIXTURES if f.is_clean and f.acceptable)
    extra = sorted(clean.acceptable)[0]
    report = evaluate(
        index=INDEX, config=ACTIVE, transport=_backend(lambda code: [extra] if clean.code.strip() in code else [])
    )
    assert report.clean_fixtures_kept_clean == report.clean_fixtures


def test_an_unreadable_reply_scores_as_finding_nothing_not_as_a_broken_run():
    """A backend that answers with no verdict is deficient, not absent.

    Scored as finding nothing — which costs it recall — while the outcome records why,
    so it is never mistaken for a clean review.
    """
    from governova_semantic import Outcome

    report = evaluate(index=INDEX, config=ACTIVE, transport=lambda cfg, msgs: "")
    assert report.assessed, "an unreadable reply must not abort the run"
    assert all(o.outcome is Outcome.UNPARSEABLE for o in report.outcomes)
    assert report.recall == 0.0
    assert report.passed is False


def test_an_inconsistent_backend_is_judged_on_its_worst_run():
    """Consistency is the property a governance gate needs.

    Measured on a real model: precision ranged 50%-75% across eight passes over identical
    input. A backend that clears the bar on average and fails one run in three gives two
    answers for the same code, and neither can be defended — so the worst run governs and
    averaging it away would hide exactly the instability that makes it unusable.
    """
    calls = {"n": 0}

    def flaky(cfg, messages):
        # Perfect on the first pass over the set, then invents on every later one.
        calls["n"] += 1
        expected = set(_perfect(messages[-1]["content"]))
        if calls["n"] > len(FIXTURES):
            expected.add("S3.14")
        return json.dumps(
            {"findings": [{"standard": s, "line": 1, "message": "x"} for s in sorted(expected)]}
        )

    report = evaluate(index=INDEX, config=ACTIVE, transport=flaky, runs=3)
    assert len(report.runs) == 3
    assert report.runs[0].precision == 1.0, "the first pass should be clean"
    worst = report.worst_run
    assert worst is not None and worst.precision is not None and worst.precision < 1.0
    assert report.passed is False, "a backend that fails any run must not pass"
    assert report.spread is not None


def test_a_consistent_backend_passes_across_runs():
    # The negative half: repeating the measurement must not itself cause a failure.
    report = evaluate(index=INDEX, config=ACTIVE, transport=_backend(_perfect), runs=3)
    assert len(report.runs) == 3
    assert report.passed is True
    assert report.spread is None, "no spread when every run agrees"


def test_a_single_run_reports_no_spread():
    report = evaluate(index=INDEX, config=ACTIVE, transport=_backend(_perfect))
    assert report.runs == []
    assert report.worst_run is None
    assert report.spread is None


def test_a_silent_backend_does_not_pass():
    """Reporting nothing is not perfect precision. It is #142 in miniature."""
    report = evaluate(index=INDEX, config=ACTIVE, transport=_backend(lambda code: []))
    assert report.assessed
    assert report.precision is None
    assert report.recall == 0.0
    assert report.passed is False


def test_recall_below_the_bar_fails_even_with_perfect_precision():
    def timid(code: str) -> list[str]:
        found = _perfect(code)
        # Report only the first violating fixture's standard; ignore the rest.
        return found if found == ["S1.103"] else []

    report = evaluate(index=INDEX, config=ACTIVE, transport=_backend(timid))
    assert report.precision == 1.0
    assert report.recall is not None and report.recall < MIN_RECALL
    assert report.passed is False


def test_a_clean_fixture_that_stays_clean_is_not_counted_as_a_true_positive():
    # Precision must be earned on violating fixtures, not inflated by silence on clean
    # ones — otherwise a backend that reports nothing would score perfectly.
    report = evaluate(index=INDEX, config=ACTIVE, transport=_backend(_perfect))
    clean = [o for o in report.outcomes if not o.expected]
    assert clean and all(not o.true_positives for o in clean)


# ─── Unassessable states ─────────────────────────────────────────────────────


def test_no_backend_configured_is_unassessed_never_a_pass():
    """The standing rule, applied to the thing that measures the tier."""
    report = evaluate(index=INDEX, config=from_env({}), transport=_backend(_perfect))
    assert report.assessed is False
    assert report.passed is None
    assert any("no endpoint" in note for note in report.notes)


def test_a_backend_that_dies_mid_run_yields_no_partial_score():
    """A score over the fixtures that happened to finish is a measurement of nothing."""
    calls = {"n": 0}

    def flaky(cfg, messages):
        calls["n"] += 1
        if calls["n"] > 2:
            raise SemanticUnavailableError("semantic endpoint returned HTTP 503", status=503)
        return json.dumps({"findings": []})

    report = evaluate(index=INDEX, config=ACTIVE, transport=flaky)
    assert report.assessed is False
    assert report.passed is None
    assert report.outcomes == []
    assert any("unreachable" in note for note in report.notes)


# ─── The distinction a naive harness would miss ──────────────────────────────


def test_a_standard_the_prefilter_never_submitted_is_reported_as_ungrounded():
    """A grounding miss and a model miss look identical and have different fixes.

    `relevant_standards` filters the corpus by title-word overlap before the model sees
    anything. Blaming the model for a standard it was never shown sends the next engineer
    tuning the wrong component.
    """
    impossible = Fixture(
        id="ungroundable",
        language="python",
        expected=frozenset({"S3.14"}),  # a real standard, unrelated to this code
        code="def add(a, b):\n    return a + b\n",
    )
    report = evaluate(
        fixtures=(impossible,), index=INDEX, config=ACTIVE, transport=_backend(lambda c: [])
    )
    outcome = report.outcomes[0]
    assert "S3.14" in outcome.false_negatives
    assert "S3.14" in outcome.ungrounded, "a never-submitted standard must not read as a model miss"
    assert any("grounding pre-filter" in note for note in report.notes)


def test_a_grounded_miss_is_not_reported_as_ungrounded():
    """The negative half: when the standard *was* submitted, the miss is the model's."""
    report = evaluate(index=INDEX, config=ACTIVE, transport=_backend(lambda code: []))
    grounded_misses = [o for o in report.outcomes if o.false_negatives and not o.ungrounded]
    assert grounded_misses, "expected at least one fixture whose standard was submitted"


# ─── The report is a sample, not a property ──────────────────────────────────


def test_the_report_records_the_model_and_the_date():
    # A score without a model id and a date is a claim nobody can reproduce or challenge,
    # and providers change models behind a stable name.
    report = evaluate(index=INDEX, config=ACTIVE, transport=_backend(_perfect))
    assert report.model == "probe-model"
    assert report.measured_at and report.measured_at[:2] == "20"


def test_the_bars_are_asymmetric_and_precision_is_the_higher_one():
    # Encodes the reasoning rather than trusting the comment: a missed violation
    # disappoints, an invented one discredits every finding beside it.
    assert MIN_PRECISION > MIN_RECALL
