"""Requirement ↔ code ↔ test linkage.

The two findings ADR-007 names as the ones teams most need and least have — **a
requirement with no test**, and **a change with no requirement** — are both available
from tier 1 alone, which costs an adopting team nothing.

The governing rule is the one that makes the feature adoptable at all: **a repository
that exposes no requirements is `unknown`, never in violation.** A team that has not
adopted this is not failing it. Reporting otherwise would make the first run of this
tool its last, and it is the same rule `governova_evidence` follows for a probe that
cannot determine an answer.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from governova_requirements.model import Finding, RequirementSet, Tier


@dataclass(frozen=True)
class TraceReport:
    """What could be determined about traceability, and what could not."""

    tier: Tier
    requirements: int = 0
    tested: int = 0
    untested: int = 0
    findings: list[Finding] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def assessed(self) -> bool:
        """False at tier 0 — the report is `unknown`, not a pass and not a failure."""
        return self.tier >= Tier.REFERENCED

    @property
    def coverage_pct(self) -> float | None:
        """Share of requirements with a citing test. None when unassessable."""
        if not self.assessed or self.requirements == 0:
            return None
        return round(100 * self.tested / self.requirements, 1)


def trace(requirement_set: RequirementSet) -> TraceReport:
    """Analyse linkage. Returns an unassessed report at tier 0 rather than findings."""
    if requirement_set.tier < Tier.REFERENCED:
        return TraceReport(
            tier=requirement_set.tier,
            notes=[
                *requirement_set.notes,
                "no requirements are reachable — traceability is unknown, not violated",
            ],
        )

    findings: list[Finding] = []
    tested = 0

    for rid in sorted(requirement_set.requirements):
        has_test = bool(requirement_set.cited_by(rid, "test"))
        if has_test:
            tested += 1
            continue
        findings.append(
            Finding(
                code="requirement-without-test",
                message=f"{rid} is cited in the repository but no test references it",
                requirement_id=rid,
                location=_first_location(requirement_set, rid),
            )
        )

    findings.extend(_untraced_requirements(requirement_set))

    total = len(requirement_set.requirements)
    return TraceReport(
        tier=requirement_set.tier,
        requirements=total,
        tested=tested,
        untested=total - tested,
        findings=findings,
        notes=list(requirement_set.notes),
    )


def _first_location(requirement_set: RequirementSet, rid: str) -> str | None:
    for citation in requirement_set.citations:
        if citation.requirement_id == rid:
            return citation.location
    return None


def _untraced_requirements(requirement_set: RequirementSet) -> list[Finding]:
    """Requirements the manifest declares that nothing in the repository implements.

    Only meaningful once the manifest is readable. At tier 1 the requirement set *is*
    the set of citations, so every requirement is cited by construction and asking the
    question would answer itself — which is why this stays silent below tier 2 rather
    than reporting a hollow zero.
    """
    if requirement_set.tier < Tier.EXPORTED:
        return []
    cited = {c.requirement_id for c in requirement_set.citations}
    return [
        Finding(
            code="requirement-without-implementation",
            message=f"{rid} is declared but nothing in the repository cites it",
            requirement_id=rid,
        )
        for rid in sorted(requirement_set.requirements)
        if rid not in cited
    ]
