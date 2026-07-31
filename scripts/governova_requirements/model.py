"""The requirements interchange model — what Governova reads, never what it owns.

ADR-007's addendum decides this: **Governova defines an interchange format and reads
that. It never becomes the source of truth for requirements.** Real requirements live in
Jira, Azure DevOps, Linear, Confluence, a spreadsheet, or a stakeholder's head, and a
governance tool that demands migration before it will say anything is a governance tool
nobody adopts. The pattern already works here — we do not own your dependency graph, we
read CycloneDX.

The tier model is the whole design. A team exposes as much as it is willing to, and the
tool's power scales with that. **Tier 0 is `unknown`, never `violated`** — the standing
rule from `governova_evidence` applies exactly, because punishing a team for a requirement
we cannot see would make the first run of this tool its last.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum


class Tier(IntEnum):
    """How much of its requirements a repository exposes.

    Ordered so `tier >= Tier.EXPORTED` reads naturally: the higher the tier, the more
    Governova can say. Nothing about a low tier is a failing — tier 1 is where most
    teams will live, and it costs them nothing.
    """

    INVISIBLE = 0
    """No requirements reachable. Everything is `unknown`. Never a violation."""

    REFERENCED = 1
    """No export; code, tests, and commits cite requirement IDs.

    Linkage only — the text cannot be linted because it is never seen. This is the
    tier that matters most for adoption: a team keeps its tracker and its process,
    and writes `REQ-1234` in a test name or a commit trailer.
    """

    EXPORTED = 2
    """A manifest generated from the team's own tracker by their own CI."""

    NATIVE = 3
    """Requirements authored directly in the Governova interchange format."""


# The obligation verbs, and what each one binds the system to. The canon specifies a
# grammar rather than a philosophy, and this is the part of it that is decidable.
OBLIGATIONS: dict[str, str] = {
    "shall": "mandatory",
    "must": "mandatory and critical",
    "should": "recommended",
    "may": "optional",
}

KINDS: frozenset[str] = frozenset({"functional", "non-functional", "domain", "constraint"})


@dataclass(frozen=True)
class Requirement:
    """One requirement, however it reached us.

    Only `id` is guaranteed. At tier 1 a requirement is an *identifier observed in the
    repository* and nothing more — no statement, no kind, no obligation — because the
    text lives in a tracker we never call. Every field beyond `id` is therefore
    optional, and a check that needs an absent field returns `unknown` rather than
    assuming a default.
    """

    id: str
    statement: str | None = None
    kind: str | None = None
    obligation: str | None = None
    source: str | None = None
    acceptance: str | None = None
    origin: str = "unknown"
    """Which reader produced this — `referenced`, `manifest`, or a registered extension."""

    @property
    def has_text(self) -> bool:
        """Whether there is a statement to lint at all."""
        return bool(self.statement and self.statement.strip())


@dataclass(frozen=True)
class Citation:
    """One place a requirement identifier was observed."""

    requirement_id: str
    location: str
    """Repo-relative file path, or `commit:<sha>` for a citation in history."""

    kind: str
    """`test`, `source`, or `commit` — what kind of artifact cited it."""

    line: int | None = None


@dataclass
class RequirementSet:
    """Everything one reader could determine about a repository's requirements."""

    tier: Tier = Tier.INVISIBLE
    requirements: dict[str, Requirement] = field(default_factory=dict)
    citations: list[Citation] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    """Human-readable statements of *why* a tier was concluded. An auditor asking
    'how do you know' must get an answer that points at something."""

    def cited_by(self, requirement_id: str, kind: str) -> list[Citation]:
        return [c for c in self.citations if c.requirement_id == requirement_id and c.kind == kind]

    def merge(self, other: RequirementSet) -> RequirementSet:
        """Combine two readers' results, the higher tier winning on conflict.

        A repository can be tier 2 *and* cite requirements from tests; both readings
        are true and both are useful. Requirements carrying text always beat bare
        identifiers, because a reader that saw the statement knows strictly more.
        """
        merged = RequirementSet(
            tier=max(self.tier, other.tier),
            requirements=dict(self.requirements),
            citations=[*self.citations, *other.citations],
            notes=[*self.notes, *other.notes],
        )
        for rid, requirement in other.requirements.items():
            existing = merged.requirements.get(rid)
            if existing is None or (requirement.has_text and not existing.has_text):
                merged.requirements[rid] = requirement
        return merged


@dataclass(frozen=True)
class Finding:
    """One requirements-governance finding.

    `advisory` findings never fail a build. Nothing here blocks by default: this tier
    is new, and a check that fires wrongly on its first encounter with a real
    repository does not get a second one.
    """

    code: str
    message: str
    requirement_id: str | None = None
    location: str | None = None
    advisory: bool = True
