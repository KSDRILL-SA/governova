"""Measure whether a semantic backend is good enough to be trusted with governance.

Before this existed, *"is this model good enough"* was unanswerable, and the honest
consequence was that no backend could be relied on — a semantic tier that invents a
finding against `S1.104` is worse than one switched off, because a wrong finding teaches
every reader to discount the right ones.

Three properties make this a harness rather than a demo.

**Precision is weighted far above recall.** A missed violation is a disappointment; an
invented one is corrosive, and it is corrosive to *every other finding the tier makes*.
The bar reflects that asymmetry rather than optimising a symmetric F-score.

**A grounding miss is reported separately from a model miss.** `relevant_standards()`
pre-filters the corpus before the model sees anything, so a standard that was never
submitted cannot be found — and blaming the model for that would send the next engineer
tuning the wrong component. The two failures look identical in a naive harness and have
completely different fixes.

This distinction earned its place immediately. On the first run against a *perfect*
backend the harness scored 0.5 recall, and the cause was not the backend: `S1.106` and
`S1.107` are aphorisms whose words never appear in code, so lexical pre-filtering could
never submit the two standards the tier exists to reach. `ALWAYS_GROUNDED` in `review.py`
is the fix, and this harness is how it was found and how it was confirmed.

**No backend configured is `unknown`, never a pass.** The standing rule, applied to the
thing that measures the tier rather than to the tier itself.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from governova_compile.schema import CompiledIndex, Standard
from governova_compile.writer import load_active_index

from governova_semantic.config import SemanticConfig, from_env
from governova_semantic.fixtures import FIXTURES, Fixture
from governova_semantic.review import (
    Outcome,
    ReviewResult,
    Transport,
    relevant_standards,
    review_result,
)

MIN_PRECISION = 0.90
"""A finding that is wrong discredits every finding beside it.

Set high deliberately. The semantic tier supplements a deterministic floor that already
runs; its value is entirely in the standards regex cannot reach, and that value is
destroyed the moment its output cannot be taken at face value.
"""

MIN_RECALL = 0.40
"""Missing findings is tolerable; inventing them is not.

Lower than precision on purpose. The tier is advisory and additive — the reliable tier and
the probes still run underneath it — so a backend that catches a useful minority with high
confidence is worth more than one that catches most and is wrong often enough to be argued
with.
"""


@dataclass(frozen=True)
class FixtureOutcome:
    """What a backend did with one fixture."""

    fixture_id: str
    expected: frozenset[str]
    found: frozenset[str]
    grounded: frozenset[str]
    """Standards the pre-filter actually submitted to the model."""

    outcome: Outcome
    detail: str = ""

    @property
    def true_positives(self) -> frozenset[str]:
        return self.expected & self.found

    @property
    def false_positives(self) -> frozenset[str]:
        return self.found - self.expected

    @property
    def false_negatives(self) -> frozenset[str]:
        return self.expected - self.found

    @property
    def ungrounded(self) -> frozenset[str]:
        """Expected standards the model was never shown.

        Not the model's fault, and not counted against it — but counted, because a
        pre-filter that never submits the right standard caps the tier's recall no matter
        how good the model is.
        """
        return self.expected - self.grounded


@dataclass(frozen=True)
class EvaluationReport:
    """A measurement of one backend at one moment. Never a permanent property.

    `model` and `measured_at` are carried because this is a *sample*: providers change
    models behind a name, and a score without a date and a model id is a claim nobody can
    reproduce or challenge.
    """

    assessed: bool
    outcomes: list[FixtureOutcome] = field(default_factory=list)
    model: str | None = None
    measured_at: str = ""
    notes: list[str] = field(default_factory=list)

    @property
    def true_positives(self) -> int:
        return sum(len(o.true_positives) for o in self.outcomes)

    @property
    def false_positives(self) -> int:
        return sum(len(o.false_positives) for o in self.outcomes)

    @property
    def false_negatives(self) -> int:
        return sum(len(o.false_negatives) for o in self.outcomes)

    @property
    def ungrounded(self) -> int:
        return sum(len(o.ungrounded) for o in self.outcomes)

    @property
    def precision(self) -> float | None:
        """Of what it reported, how much was real. None when it reported nothing."""
        reported = self.true_positives + self.false_positives
        return round(self.true_positives / reported, 3) if reported else None

    @property
    def recall(self) -> float | None:
        """Of what was there, how much it found. None when nothing was expected."""
        present = self.true_positives + self.false_negatives
        return round(self.true_positives / present, 3) if present else None

    @property
    def clean_fixtures_kept_clean(self) -> int:
        return sum(1 for o in self.outcomes if not o.expected and not o.found)

    @property
    def clean_fixtures(self) -> int:
        return sum(1 for o in self.outcomes if not o.expected)

    @property
    def passed(self) -> bool | None:
        """Whether this backend clears the bar. None when unassessed.

        A backend that reported nothing at all does not pass: precision is undefined
        rather than perfect, and a silent tier is exactly the failure `#142` was about.
        """
        if not self.assessed:
            return None
        if self.precision is None or self.recall is None:
            return False
        return self.precision >= MIN_PRECISION and self.recall >= MIN_RECALL

    def summary(self) -> str:
        if not self.assessed:
            return "unassessed — no semantic backend configured"
        precision = "—" if self.precision is None else f"{self.precision:.0%}"
        recall = "—" if self.recall is None else f"{self.recall:.0%}"
        return (
            f"precision {precision} (bar {MIN_PRECISION:.0%}) · "
            f"recall {recall} (bar {MIN_RECALL:.0%}) · "
            f"clean kept clean {self.clean_fixtures_kept_clean}/{self.clean_fixtures}"
        )


def _grounded_for(index: CompiledIndex, fixture: Fixture) -> list[Standard]:
    return relevant_standards(index, fixture.code)


def evaluate(
    *,
    fixtures: tuple[Fixture, ...] = FIXTURES,
    index: CompiledIndex | None = None,
    config: SemanticConfig | None = None,
    transport: Transport | None = None,
) -> EvaluationReport:
    """Run every fixture against the configured backend and score the result.

    Never raises. A backend that becomes unreachable mid-run produces an unassessed
    report rather than a partial score, because a score computed over the fixtures that
    happened to complete before the endpoint died is not a measurement of anything.
    """
    cfg = config or from_env()
    if not cfg.is_configured:
        return EvaluationReport(
            assessed=False,
            notes=[
                "no endpoint, model, or key configured — set GOVERNOVA_LLM_* "
                "(ADR-008: no default is bundled)"
            ],
        )

    idx = index or load_active_index()
    outcomes: list[FixtureOutcome] = []

    for fixture in fixtures:
        grounded = _grounded_for(idx, fixture)
        result: ReviewResult = review_result(
            fixture.code, standards=grounded, index=idx, config=cfg, transport=transport
        )
        if result.outcome is Outcome.UNAVAILABLE:
            return EvaluationReport(
                assessed=False,
                model=cfg.model,
                notes=[
                    f"backend became unreachable at fixture {fixture.id!r}: {result.detail}",
                    "no partial score is reported — it would measure nothing",
                ],
            )
        outcomes.append(
            FixtureOutcome(
                fixture_id=fixture.id,
                expected=fixture.expected,
                found=frozenset(f.standard.upper() for f in result.findings),
                grounded=frozenset(s.id.upper() for s in grounded),
                outcome=result.outcome,
                detail=result.detail,
            )
        )

    notes: list[str] = []
    ungrounded = [o for o in outcomes if o.ungrounded]
    if ungrounded:
        notes.append(
            "grounding pre-filter never submitted "
            + ", ".join(sorted({s for o in ungrounded for s in o.ungrounded}))
            + " — a recall ceiling in `relevant_standards`, not a model failure"
        )

    return EvaluationReport(
        assessed=True,
        outcomes=outcomes,
        model=cfg.model,
        measured_at=datetime.now(UTC).strftime("%Y-%m-%d"),
        notes=notes,
    )
