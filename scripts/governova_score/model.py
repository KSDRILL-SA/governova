"""The Governova Score model — faithful to docs/vision/master.md §18.1.

A 0–100 score for a governed repository, as a weighted average of five factors.
Each factor is assessed independently; factors that require a live Governova
runtime (relay, audit trail) report "not assessed" until that data exists, and
the score is renormalised over the assessed factors. The model never changes —
factors simply light up as instrumentation lands.
"""

from __future__ import annotations

from dataclasses import dataclass

# §18.1 — factor weights (must sum to 100).
WEIGHTS: dict[str, int] = {
    "violation_rate": 30,
    "relay_compliance": 25,
    "constitutional_coverage": 20,
    "amendment_discipline": 15,
    "audit_trail": 10,
}

TITLES: dict[str, str] = {
    "violation_rate": "Violation rate",
    "relay_compliance": "Relay compliance",
    "constitutional_coverage": "Constitutional coverage",
    "amendment_discipline": "Amendment discipline",
    "audit_trail": "Audit trail completeness",
}

# §18.2 — Governova Certified threshold.
CERTIFIED_THRESHOLD = 85

# ADR-012 — the least of the model that must be assessed before a headline score
# is issued at all.
#
# Below this, `finalize` renormalises a minority of the model onto 100% of the
# answer. Measured: on first contact with a repository carrying no Governova
# instrumentation, four factors return None and violation rate alone — 30% of the
# model — becomes the whole score. `pallets/click` was told 0/100 (F) on that
# basis, by a product it had run once.
#
# 50 is a majority of the weight, not a tuned number: it is the least that can be
# claimed by something calling itself a weighted average of five factors. It also
# falls where the product's own design already places the boundary — violation
# rate (30) plus constitutional coverage (20) — and coverage becomes assessable
# exactly when a human accepts the proposed profile. So the score appears once
# the user has told the tool what it is looking at, and not before.
QUORUM_WEIGHT = 50


@dataclass(frozen=True)
class Factor:
    """One scored factor. `score` is None when the factor cannot be assessed
    from the available data (e.g. no runtime instrumentation)."""

    key: str
    title: str
    weight: int
    score: float | None
    detail: str

    @property
    def assessed(self) -> bool:
        return self.score is not None

    @property
    def contribution(self) -> float:
        """Weighted points this factor contributes before renormalisation."""
        return (self.score or 0.0) * self.weight


@dataclass(frozen=True)
class GovernovaScore:
    """The computed score and its transparent breakdown."""

    score: int
    grade: str
    factors: list[Factor]
    assessed_weight: int

    @property
    def has_quorum(self) -> bool:
        """Whether enough of the model was assessed to issue a headline (ADR-012)."""
        return self.assessed_weight >= QUORUM_WEIGHT

    @property
    def headline(self) -> int | None:
        """The score to publish, or None when the assessment is partial.

        `score` remains the arithmetic over whatever was assessed, because that
        figure is still worth showing beside the factors it came from. `headline`
        is the one a surface may present as *the* Governova Score, and it is
        withheld rather than qualified: a number with a caveat beside it is read
        as a number, and the caveat is not what gets quoted.
        """
        return self.score if self.has_quorum else None

    @property
    def certified_eligible(self) -> bool:
        """Certification requires a quorum. A partial assessment certifies nothing."""
        return self.has_quorum and self.score >= CERTIFIED_THRESHOLD

    @property
    def assessed_factors(self) -> list[Factor]:
        return [f for f in self.factors if f.assessed]


def grade_for(score: int) -> str:
    """Letter grade. The B+ band starts at the Governova Certified threshold (85)."""
    if score >= 95:
        return "A+"
    if score >= 90:
        return "A"
    if score >= CERTIFIED_THRESHOLD:
        return "B+"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


def finalize(factors: list[Factor]) -> GovernovaScore:
    """Weighted average over assessed factors, with weights renormalised."""
    assessed = [f for f in factors if f.assessed]
    total_weight = sum(f.weight for f in assessed)
    score = (
        0
        if total_weight == 0
        else round(sum(f.contribution for f in assessed) / total_weight)
    )
    return GovernovaScore(
        score=score,
        grade=grade_for(score),
        factors=factors,
        assessed_weight=total_weight,
    )
