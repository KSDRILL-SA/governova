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
    acceptable: frozenset[str] = frozenset()
    """Defensible findings, counted as neither a hit nor an invention."""

    @property
    def true_positives(self) -> frozenset[str]:
        return self.expected & self.found

    @property
    def false_positives(self) -> frozenset[str]:
        """Findings that are neither required nor defensible.

        `acceptable` is subtracted because scoring a correct finding as an invention
        measures how completely the fixture was annotated, not how good the backend is.
        """
        return self.found - self.expected - self.acceptable

    @property
    def tolerated_extras(self) -> frozenset[str]:
        """Defensible findings the backend made. Reported, never penalised."""
        return self.found & self.acceptable

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
class RunScore:
    """One pass over the whole fixture set."""

    precision: float | None
    recall: float | None
    true_positives: int
    false_positives: int
    false_negatives: int


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
    runs: list[RunScore] = field(default_factory=list)
    """Per-run scores when the set was measured more than once.

    Empty for a single run, where `outcomes` is the whole story.
    """

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
    def tolerated_extras(self) -> int:
        """Defensible findings across the run. Neither rewarded nor penalised."""
        return sum(len(o.tolerated_extras) for o in self.outcomes)

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
        return sum(1 for o in self.outcomes if not o.expected and not o.false_positives)

    @property
    def clean_fixtures(self) -> int:
        return sum(1 for o in self.outcomes if not o.expected)

    @property
    def worst_run(self) -> RunScore | None:
        """The weakest pass over the set. None for a single-run report.

        Used for the verdict rather than the mean, because **consistency is the property
        a governance gate needs.** A backend that clears the bar on average and fails one
        run in three produces findings a team cannot act on: the same code reviewed twice
        gives two answers, and neither can be defended.
        """
        scored = [r for r in self.runs if r.precision is not None]
        if not scored:
            return None
        return min(scored, key=lambda r: (r.precision or 0.0, r.recall or 0.0))

    @property
    def spread(self) -> str | None:
        """Precision range across runs — how much a single run can be trusted.

        None when every run agreed, because "100%–100%" is not a spread and printing it
        implies an instability that was not observed.
        """
        values = [r.precision for r in self.runs if r.precision is not None]
        if len(values) < 2 or min(values) == max(values):
            return None
        return f"{min(values):.0%}–{max(values):.0%}"

    @property
    def passed(self) -> bool | None:
        """Whether this backend clears the bar. None when unassessed.

        A backend that reported nothing at all does not pass: precision is undefined
        rather than perfect, and a silent tier is exactly the failure `#142` was about.

        With multiple runs the **worst** run must clear the bar. Measured variance on a
        real model was large — precision ranged 50%–75% across eight passes over
        identical input (`gpt-oss:120b`, 2026-07-31) — so a single run is a sample, not a
        property, and averaging it away would hide exactly the instability that makes a
        backend unusable.
        """
        if not self.assessed:
            return None
        worst = self.worst_run
        if worst is not None:
            if worst.precision is None or worst.recall is None:
                return False
            return worst.precision >= MIN_PRECISION and worst.recall >= MIN_RECALL
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
    runs: int = 1,
) -> EvaluationReport:
    """Run every fixture against the configured backend and score the result.

    `runs` repeats the whole set. **More than one is strongly recommended before making a
    decision**: measured variance on a real model was large — precision ranged 50%-75% across eight
    passes over identical input — so a single run is a sample, not a property.
    The default stays 1 because every extra run costs latency and, on a metered endpoint,
    money.

    Never raises. A backend that becomes unreachable mid-run produces an unassessed
    report rather than a partial score, because a score computed over the fixtures that
    happened to complete before the endpoint died is not a measurement of anything.
    """
    if runs > 1:
        return _evaluate_repeatedly(
            fixtures=fixtures, index=index, config=config, transport=transport, runs=runs
        )
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
        if result.outcome is Outcome.UNPARSEABLE:
            # The endpoint answered and said nothing readable. That is a deficiency of
            # this backend, not a broken run — it is scored as finding nothing, and the
            # outcome records why so it is not mistaken for a clean review.
            outcomes.append(
                FixtureOutcome(
                    fixture_id=fixture.id,
                    expected=fixture.expected,
                    acceptable=fixture.acceptable,
                    found=frozenset(),
                    grounded=frozenset(s.id.upper() for s in grounded),
                    outcome=result.outcome,
                    detail=result.detail,
                )
            )
            continue
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
                acceptable=fixture.acceptable,
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


def _evaluate_repeatedly(
    *,
    fixtures: tuple[Fixture, ...],
    index: CompiledIndex | None,
    config: SemanticConfig | None,
    transport: Transport | None,
    runs: int,
) -> EvaluationReport:
    """Measure the set `runs` times and keep the spread.

    The returned `outcomes` are the **last** pass, so the per-fixture table still shows a
    real, self-consistent run rather than an average that never happened. The verdict
    comes from `runs`, where the worst pass governs.
    """
    reports = [
        evaluate(fixtures=fixtures, index=index, config=config, transport=transport)
        for _ in range(runs)
    ]
    unassessed = next((r for r in reports if not r.assessed), None)
    if unassessed is not None:
        return unassessed

    last = reports[-1]
    return EvaluationReport(
        assessed=True,
        outcomes=last.outcomes,
        model=last.model,
        measured_at=last.measured_at,
        notes=[
            *last.notes,
            f"{runs} runs — the worst governs the verdict, because the same code reviewed "
            f"twice must not give two answers",
        ],
        runs=[
            RunScore(
                precision=r.precision,
                recall=r.recall,
                true_positives=r.true_positives,
                false_positives=r.false_positives,
                false_negatives=r.false_negatives,
            )
            for r in reports
        ],
    )
