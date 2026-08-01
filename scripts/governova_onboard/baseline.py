"""governova_onboard.baseline — the honest starting line for a repository.

This is Scan & Learn, and it is the mode most adopters will only ever use. It
runs every deterministic tier the engine has against a repository the engine has
never seen, and reports four things: what the repository *is*, what it scores,
where the gaps sit, and what to look at first.

**Nothing here is new detection.** The rules, the probes, the requirements
analyser and the schema analyser all already exist and are all already tested;
this module assembles them and does the arithmetic. That is deliberate — a
baseline built from a second, onboarding-only detection path would be a second
thing to keep true, and the first time the two disagreed the adopter would be
right to trust neither.

## The one rule that governs the whole report

**Detection degrades; it never guesses.** A repository with no tests is not a
repository that fails `S7.6` — it is a repository where that question is
`unknown`. The temptation to break this is strongest here, because a baseline
full of `unknown` looks less impressive than one full of violations. It is also
the honest one, and it is the only version that makes the second run credible.

So the heatmap carries four columns and `unknown` is expected to be the largest
by a wide margin on first contact. That number is not a defect in the report; it
is the report.

## Why the score has holes in it

Three of the five §18.1 factors — relay compliance, audit-trail completeness and
constitutional coverage — need governance instrumentation the repository does not
have yet. They come back unassessed, and `finalize` renormalises over the rest.
The report prints all five anyway, each with the reason it could not be assessed,
because "we did not measure this" is information an adopter needs and a silently
dropped factor is not.

Constitutional coverage is the interesting one: it is unassessed *by design*
until a human accepts the proposed profile. Scoring coverage against a profile
Governova guessed at would be grading the repository against a constitution
nobody agreed to.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from governova_checks import Finding, iter_source_files, scan_paths
from governova_compile.schema import CompiledIndex
from governova_evidence import ProbeResult, Verdict, run_probes
from governova_project import Profile, applicable_standards
from governova_score.model import GovernovaScore

from governova_onboard.detect import Detection, detect

# How many finding groups a report shows by default. A baseline nobody finishes
# reading is a baseline that changes nothing, so the cap is a feature.
DEFAULT_TOP = 12

# Example paths carried per finding group, so a reader can open one without the
# report becoming a file listing.
_EXAMPLES = 3


@dataclass(frozen=True)
class ConstitutionGap:
    """One constitution's row in the heatmap.

    The four counts partition the applicable set exactly, so `applicable` always
    equals the sum of the other three. A row that does not add up means a
    standard was counted as two things at once, which the test suite asserts
    against.
    """

    constitution_id: str
    name: str
    applicable: int
    evidenced: int
    violated: int
    unknown: int

    @property
    def evidenced_pct(self) -> float:
        return round(100 * self.evidenced / self.applicable, 1) if self.applicable else 0.0


@dataclass(frozen=True)
class FindingGroup:
    """Every occurrence of one anti-pattern, collapsed into a single row.

    A baseline that lists forty instances of the same fix as forty findings
    reports effort, not risk. Grouping by anti-pattern is what makes the top of
    the list readable, and the count is retained because forty occurrences and
    one occurrence are genuinely different situations.
    """

    anti_pattern: str
    standard: str
    message: str
    confidence: str
    count: int
    files: tuple[str, ...]

    @property
    def blocking(self) -> bool:
        return self.confidence == "high"


@dataclass(frozen=True)
class Baseline:
    """The complete read-only assessment of a repository."""

    root: Path
    detection: Detection
    profile: Profile
    score: GovernovaScore
    gaps: tuple[ConstitutionGap, ...]
    groups: tuple[FindingGroup, ...]
    probes: tuple[ProbeResult, ...]
    source_files: int
    provisional: tuple[str, ...]
    """Reasons the numbers below are provisional — every one of them a profile
    field a human still has to settle. Empty means the profile was accepted."""

    @property
    def applicable(self) -> int:
        return sum(g.applicable for g in self.gaps)

    @property
    def evidenced(self) -> int:
        return sum(g.evidenced for g in self.gaps)

    @property
    def violated(self) -> int:
        return sum(g.violated for g in self.gaps)

    @property
    def unknown(self) -> int:
        return sum(g.unknown for g in self.gaps)

    @property
    def blocking_groups(self) -> tuple[FindingGroup, ...]:
        return tuple(g for g in self.groups if g.blocking)

    @property
    def blocking_findings(self) -> int:
        return sum(g.count for g in self.blocking_groups)

    @property
    def violated_probes(self) -> tuple[ProbeResult, ...]:
        """Structural violations — repository facts, not lines of code.

        These count toward `violated` in the heatmap, so they must be reportable
        somewhere a reader can see them. The first run of this report printed
        "no findings" beside a heatmap showing one violated standard, because the
        findings section only knew about the reliable tier. A number the report
        cannot explain is worse than a number it does not show.
        """
        return tuple(p for p in self.probes if p.verdict is Verdict.VIOLATED)

    @property
    def clean(self) -> bool:
        """Whether every deterministic tier found nothing to report."""
        return not self.groups and not self.violated_probes


def proposed_profile(detection: Detection) -> Profile:
    """The profile a baseline is computed against, before any human sees it.

    `domains` and `phase` are left unset, and both defaults lean the same way —
    **toward a larger applicable set**, which is the harder score. An unset phase
    applies every phase's standards rather than a convenient subset, matching the
    rule `governova_project` already states: ambiguity resolves toward *more*
    applicable standards, because a narrower denominator is an easier number.

    No `satisfied` or `exception` entries are ever proposed. Evidence is
    something a repository demonstrates, not something an onboarding tool grants
    it on arrival.
    """
    return Profile(name=detection.name, stacks=list(detection.stacks), domains=[], phase=None)


def _provisional_reasons(detection: Detection) -> tuple[str, ...]:
    """What a human must settle before these numbers stop being provisional."""
    reasons: list[str] = []
    if not detection.stacks:
        reasons.append(
            "no stack detected — standards scoped to a specific stack are being "
            "excluded on an undetected basis, which narrows the applicable set"
        )
    reasons.append(
        "no Layer 4 domain declared — sector standards are not counted, and no scan "
        "can tell which sector this system serves"
    )
    reasons.append(
        "no lifecycle phase declared — every phase's standards are counted, which is "
        "the widest reading and the hardest score"
    )
    if detection.truncated:
        reasons.append(
            "the scan stopped at its file limit — the profile is drawn from a partial walk"
        )
    return tuple(reasons)


def _relative(root: Path, path: str) -> str:
    """A finding's location as the reader will look for it.

    `scan_paths` records whatever path it was handed, and `iter_source_files`
    hands it absolute ones. Reporting those makes every row in the findings table
    a truncated temp directory, which is worse than useless on a first run
    against somebody else's checkout — it hides the filename, the one part that
    matters.
    """
    try:
        return Path(path).resolve().relative_to(root.resolve()).as_posix()
    except (ValueError, OSError):
        return Path(path).as_posix()


def _group_findings(root: Path, findings: list[Finding]) -> tuple[FindingGroup, ...]:
    """Collapse findings by anti-pattern, blocking first, then by frequency."""
    buckets: dict[str, list[Finding]] = {}
    for finding in findings:
        buckets.setdefault(finding.anti_pattern, []).append(finding)

    groups = [
        FindingGroup(
            anti_pattern=anti_pattern,
            standard=members[0].standard,
            message=members[0].message,
            confidence=members[0].confidence,
            count=len(members),
            files=tuple(
                sorted({_relative(root, m.file) for m in members if m.file is not None})[
                    :_EXAMPLES
                ]
            ),
        )
        for anti_pattern, members in buckets.items()
    ]
    # Blocking before advisory, then most-frequent, then a stable tiebreak. Risk
    # ordering by blast radius proper is Stage 1; this is the honest cheap version
    # and it must not pretend to be more.
    groups.sort(key=lambda g: (not g.blocking, -g.count, g.anti_pattern))
    return tuple(groups)


def _heatmap(
    index: CompiledIndex,
    profile: Profile,
    *,
    evidenced: set[str],
    violated: set[str],
) -> tuple[ConstitutionGap, ...]:
    """Per-constitution applicable / evidenced / violated / unknown.

    Core constitutions only. Domain standards are counted separately wherever
    they are reported, because core and domain metrics never mix — a domain
    average folded into a core one hides both.
    """
    applicable_ids = {s.id for s in applicable_standards(index, profile)}
    rows: list[ConstitutionGap] = []
    for constitution in index.constitutions:
        ids = {s.id for s in constitution.standards} & applicable_ids
        if not ids:
            continue
        hit = ids & violated
        # A violation outranks a clean check on the same standard: evidence
        # against is stronger than evidence for, and this also guarantees the
        # four counts partition the set exactly once.
        clean = (ids & evidenced) - hit
        rows.append(
            ConstitutionGap(
                constitution_id=constitution.id,
                name=constitution.name,
                applicable=len(ids),
                evidenced=len(clean),
                violated=len(hit),
                unknown=len(ids) - len(clean) - len(hit),
            )
        )
    return tuple(rows)


def assess(root: Path, index: CompiledIndex) -> Baseline:
    """Run every deterministic tier against `root` and assemble the baseline.

    `index` is passed in rather than resolved here so the caller controls which
    constitution governs — for a foreign repository that is the bundled copy, and
    for a repository already carrying one it is theirs.
    """
    from governova_checks import RULES
    from governova_score.compute import compute_score

    detection = detect(root)
    profile = proposed_profile(detection)

    files = list(iter_source_files(root))
    findings = scan_paths(files)
    probes = run_probes(root)

    violated_by_rule = {f.standard for f in findings}
    violated_by_probe = {p.standard for p in probes if p.verdict is Verdict.VIOLATED}
    violated = violated_by_rule | violated_by_probe

    # Mechanical evidence, exactly as `governova_project.enforced_clean_standards`
    # defines it — a rule that covers a standard and found nothing, plus a probe
    # that returned SATISFIED. Recomputed from the scan already done rather than
    # called, because calling it would scan the repository a second time.
    rule_clean = {rule.standard for rule in RULES} - violated_by_rule
    probe_clean = {p.standard for p in probes if p.verdict is Verdict.SATISFIED}
    evidenced = rule_clean | probe_clean

    return Baseline(
        root=root,
        detection=detection,
        profile=profile,
        score=compute_score(root),
        gaps=_heatmap(index, profile, evidenced=evidenced, violated=violated),
        groups=_group_findings(root, findings),
        probes=tuple(probes),
        source_files=len(files),
        provisional=_provisional_reasons(detection),
    )


__all__ = [
    "DEFAULT_TOP",
    "Baseline",
    "ConstitutionGap",
    "FindingGroup",
    "assess",
    "proposed_profile",
]
