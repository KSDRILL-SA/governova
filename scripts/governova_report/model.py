"""The Board-Level Governance Report model — master.md §18.3.

A one-page, plain-English report for non-technical stakeholders: overall score and
certification status, red/amber/green per constitutional area, governance events,
and an honest note on metrics that await runtime instrumentation (trend, AI-action
volume).
"""

from __future__ import annotations

from dataclasses import dataclass

from governova_score.model import GovernovaScore

GREEN = "GREEN"
AMBER = "AMBER"
RED = "RED"


@dataclass(frozen=True)
class AreaStatus:
    """Red/amber/green for one constitutional area."""

    constitution_id: str
    name: str
    status: str
    blocking: int
    advisory: int
    standards: int

    @property
    def summary(self) -> str:
        if self.status == GREEN:
            return "No violations detected"
        if self.status == AMBER:
            return f"{self.advisory} advisory finding(s) — review recommended"
        return f"{self.blocking} blocking violation(s) — action required"


@dataclass(frozen=True)
class GovernanceEvents:
    """Counts of recorded governance activity."""

    amendments: int
    adrs: int
    runbooks: int


@dataclass(frozen=True)
class BoardReport:
    generated_on: str  # ISO date
    score: GovernovaScore
    areas: list[AreaStatus]
    events: GovernanceEvents

    @property
    def areas_red(self) -> int:
        return sum(1 for a in self.areas if a.status == RED)

    @property
    def areas_amber(self) -> int:
        return sum(1 for a in self.areas if a.status == AMBER)

    @property
    def areas_green(self) -> int:
        return sum(1 for a in self.areas if a.status == GREEN)

    @property
    def headline(self) -> str:
        """One plain-English sentence for the top of the report."""
        s = self.score
        cert = "is Governova Certified eligible" if s.certified_eligible else "is below the certification threshold"
        if self.areas_red:
            return (
                f"Governance posture needs attention: {self.areas_red} constitutional "
                f"area(s) have blocking violations. The overall score is {s.score}/100 "
                f"({s.grade}) and {cert}."
            )
        if self.areas_amber:
            return (
                f"Governance posture is sound with minor advisories: {self.areas_amber} "
                f"area(s) to review. The overall score is {s.score}/100 ({s.grade}) and {cert}."
            )
        return (
            f"Governance posture is strong: every constitutional area is green. "
            f"The overall score is {s.score}/100 ({s.grade}) and {cert}."
        )
