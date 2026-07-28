"""governova_project — per-project applicability and constitutional coverage.

Answers the question the Governova Score's coverage factor asks: *which standards
apply to this system, and which of them are satisfied?*

**Applicability is derived, not declared.** The compiled index already records each
standard's `applies_to` scope and phase. A project declares a short profile — its
stacks, its Layer 4 domains, the phase it has reached — and the applicable set
follows from that. Asking anyone to hand-list 618 standards would produce a stale
list, and a stale list is worse than none because it looks maintained.

Two rules keep the metric honest, and both exist because the obvious
implementation is trivially inflatable:

1. **Ambiguity resolves toward *more* applicable standards.** A narrower
   denominator is an easier score. Any scope string the matcher does not
   confidently recognise as stack-exclusive is treated as applicable, so the
   default leans against the failure mode that flatters every project.

2. **Satisfaction requires evidence that resolves.** A declaration citing a file
   that is not on disk, or an exception citing an ADR that does not exist, counts
   for nothing and is reported as a broken claim. Without this the factor becomes
   a self-assessment — the same defect the audit factor carried before the
   runtime landed, where any file at all scored 100.

Profile: `governance/project.toml`, read with stdlib `tomllib`. Read-only by
design — humans author it, Governova never rewrites it.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from governova_compile.schema import CompiledIndex, Standard

PROJECT_RELATIVE_PATH = "governance/project.toml"

# Stack-exclusive scope markers found in the corpus, mapped to the stack token a
# project declares. A standard whose scope names one of these applies only to a
# project using that stack.
STACK_MARKERS: dict[str, tuple[str, ...]] = {
    "angular": ("angular only", "angular stack"),
    "nextjs": ("next.js only", "next.js stack", "nextjs only", "nextjs stack"),
}


@dataclass(frozen=True)
class Claim:
    """A declared satisfaction or exception, and whether its evidence resolved."""

    standard: str
    kind: str  # "satisfied" | "exception"
    evidence: str
    resolved: bool
    reason: str = ""


@dataclass
class Profile:
    """What a project declares about itself. Deliberately small."""

    name: str = ""
    stacks: list[str] = field(default_factory=list)
    domains: list[str] = field(default_factory=list)
    phase: int | None = None
    satisfied: list[dict[str, Any]] = field(default_factory=list)
    exceptions: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class Coverage:
    """The computed coverage result."""

    applicable: int
    satisfied: int
    excepted: int
    mechanical: int
    declared: int
    unaddressed: int
    broken_claims: list[Claim]
    pct: float

    @property
    def detail(self) -> str:
        # "evidenced" is deliberate. This measures demonstrated compliance, not
        # actual compliance — a standard satisfied in practice but never evidenced
        # is uncounted, exactly as an auditor would treat it.
        bits = [
            f"{self.satisfied + self.excepted}/{self.applicable} applicable standard(s) "
            f"evidenced or excepted",
            f"{self.mechanical} mechanically verified",
        ]
        if self.broken_claims:
            bits.append(f"{len(self.broken_claims)} unresolved claim(s) not counted")
        return ", ".join(bits)


def profile_path(root: Path) -> Path:
    return root / PROJECT_RELATIVE_PATH


def load_profile(root: Path) -> Profile | None:
    """Read the profile, or None when the project has not declared one."""
    path = profile_path(root)
    if not path.is_file():
        return None
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, OSError):
        return None

    project = data.get("project", {})
    return Profile(
        name=str(project.get("name", "")),
        stacks=[str(s).lower() for s in project.get("stacks", [])],
        domains=[str(d).upper() for d in project.get("domains", [])],
        phase=project.get("phase"),
        satisfied=list(data.get("satisfied", [])),
        exceptions=list(data.get("exception", [])),
    )


def _stack_excluded(applies_to: str, stacks: list[str]) -> bool:
    """Whether a stack-exclusive scope rules this standard out for the project.

    Returns True only when the scope names a stack the project does not use. Any
    scope with no recognised stack marker returns False — applicable — because
    guessing narrower would shrink the denominator and inflate the score.
    """
    scope = applies_to.lower()
    named = [stack for stack, markers in STACK_MARKERS.items() if any(m in scope for m in markers)]
    if not named:
        return False  # no stack qualifier recognised → applies
    return not any(stack in stacks for stack in named)


def applies(standard: Standard, profile: Profile) -> bool:
    """Whether one standard applies to the project described by `profile`."""
    if _stack_excluded(standard.applies_to, profile.stacks):
        return False
    # A phase the project has not reached is not yet applicable. Standards with no
    # phase (C00, domains) are always in scope.
    if profile.phase is not None and standard.phase is not None:
        try:
            if int(standard.phase.value) > profile.phase:
                return False
        except (TypeError, ValueError):
            return True
    return True


def applicable_standards(index: CompiledIndex, profile: Profile) -> list[Standard]:
    """Every core standard in scope, plus those of the profile's declared domains."""
    result = [s for c in index.constitutions for s in c.standards if applies(s, profile)]
    for domain in index.domains:
        if domain.id.upper() in profile.domains:
            result.extend(domain.standards)
    return result


def _evidence_resolves(root: Path, evidence: str) -> bool:
    """A cited path must actually exist. An unresolvable citation is not evidence."""
    if not evidence:
        return False
    return (root / evidence).exists()


def _adr_exists(root: Path, adr: str) -> bool:
    if not adr:
        return False
    return any((root / "governance" / "decisions").glob(f"{adr}*.md"))


def verify_claims(root: Path, profile: Profile) -> list[Claim]:
    """Check every declared satisfaction and exception against reality."""
    claims: list[Claim] = []
    for entry in profile.satisfied:
        evidence = str(entry.get("evidence", ""))
        claims.append(
            Claim(
                standard=str(entry.get("standard", "")),
                kind="satisfied",
                evidence=evidence,
                resolved=_evidence_resolves(root, evidence),
                reason=str(entry.get("note", "")),
            )
        )
    for entry in profile.exceptions:
        adr = str(entry.get("adr", ""))
        claims.append(
            Claim(
                standard=str(entry.get("standard", "")),
                kind="exception",
                evidence=adr,
                resolved=_adr_exists(root, adr),
                reason=str(entry.get("reason", "")),
            )
        )
    return claims


def compute_coverage(
    root: Path, index: CompiledIndex, profile: Profile, *, enforced: set[str] | None = None
) -> Coverage:
    """Constitutional coverage for the project.

    `enforced` is the set of standard ids the reliable tier covers and found
    clean — the strongest form of evidence, because it needed no declaration.
    """
    standards = applicable_standards(index, profile)
    applicable_ids = {s.id for s in standards}
    mechanical = (enforced or set()) & applicable_ids

    claims = verify_claims(root, profile)
    resolved = [c for c in claims if c.resolved and c.standard in applicable_ids]
    broken = [c for c in claims if not c.resolved]

    declared_ids = {c.standard for c in resolved if c.kind == "satisfied"} - mechanical
    excepted_ids = {c.standard for c in resolved if c.kind == "exception"} - mechanical

    satisfied_ids = mechanical | declared_ids
    covered = satisfied_ids | excepted_ids
    total = len(applicable_ids)
    pct = round(100 * len(covered) / total, 1) if total else 0.0

    return Coverage(
        applicable=total,
        satisfied=len(satisfied_ids),
        excepted=len(excepted_ids),
        mechanical=len(mechanical),
        declared=len(declared_ids),
        unaddressed=total - len(covered),
        broken_claims=broken,
        pct=pct,
    )


def enforced_clean_standards(root: Path) -> set[str]:
    """Standards mechanically verified as satisfied — the strongest evidence.

    Two independent sources, neither requiring a declaration:

    * **Reliable tier** — a rule covers the standard and found nothing. A rule
      that fires is evidence *against*, so any standard with a finding is
      excluded rather than merely unproven.
    * **Structural probes** — repository-level facts (`governova_evidence`) that
      no line-scan can reach. A probe that cannot determine the answer returns
      UNKNOWN and contributes nothing.
    """
    from governova_checks import RULES, iter_source_files, scan_paths
    from governova_evidence import satisfied_standards

    violated = {f.standard for f in scan_paths(list(iter_source_files(root)))}
    from_rules = {r.standard for r in RULES} - violated
    return from_rules | satisfied_standards(root)


def coverage_factor(root: Path, index: CompiledIndex) -> tuple[float | None, str]:
    """The Governova Score's constitutional-coverage factor.

    Returns (None, reason) when the project has declared no profile — an
    undeclared project is unassessed, never assumed compliant.
    """
    profile = load_profile(root)
    if profile is None:
        return None, "no project profile (governance/project.toml) — applicability undeclared"
    result = compute_coverage(root, index, profile, enforced=enforced_clean_standards(root))
    if result.applicable == 0:
        return None, "profile declares no applicable standards"
    return result.pct, result.detail
