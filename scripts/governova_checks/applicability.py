"""Which findings a project has actually declared itself subject to.

The rule set spans two bodies of law. Core standards (`S{C}.{N}`) apply to every
system Governova governs. **Layer 4 domain standards (`D-{DOMAIN}.{N}`) apply to
one sector**, and a project opts into a sector by naming it in
`governance/project.toml` — because no scan can determine it. `governova onboard`
says so in the profile it proposes:

    a domain states which business a system is in, and a payments ledger and a
    lesson planner can be structurally identical

`governova_project.applicable_standards` has always honoured that: a domain's
standards enter the applicable set only when the profile declares the domain. The
*scanner* did not. Every surface reading `scan_paths` received every domain rule's
findings regardless of what the project had declared, so the assessment model and
the merge gate disagreed about what the law was.

Measured on the first external adopter — a Next.js monorepo — that produced **199
blocking `AP-D-FINTECH.1a` findings out of 201**, from a domain the proposed
profile left undeclared. The repository genuinely is fintech, so the findings were
true; they were true by luck. A lesson planner that types a course fee as a plain
`number` received the identical build failure from law it had never adopted.

(That sentence originally spelled the offending declaration out, and the fintech
rule fired on it — a prose description of the rule over-firing, in a docstring
about the rule over-firing. Recorded on the issue tracking that rule's precision.)

**The undeclared reading is the narrow one, and deliberately so.** Everywhere else
in this engine ambiguity resolves toward *more* obligation, because a smaller
denominator is an easier score. Here the direction reverses, for a reason that
does not generalise: an undeclared domain is not an unknown amount of law, it is
law belonging to a different sector. Applying FICA to a lesson planner is not
strictness, it is a wrong answer — and one the reader cannot act on, which is the
property that makes a gate get switched off.

Withheld findings are counted and named, never dropped in silence. A gate that
quietly stops checking something is the failure this module exists to prevent, in
the opposite direction.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from governova_checks.rules import Finding

DOMAIN_PREFIX = "D-"
"""Layer 4 standard IDs are `D-{DOMAIN}.{N}`; core IDs are `S{C}.{N}`.

The two namespaces are separated by the schema itself (`DomainStandardId` and
`StandardId` carry mutually exclusive patterns, and a core document can never
yield a `D-` id), so the prefix is a guarantee rather than a convention worth
double-checking against the index.
"""


def domain_of(standard_id: str) -> str | None:
    """The Layer 4 domain a standard belongs to, or None when it is core.

    >>> domain_of("D-FINTECH.1")
    'D-FINTECH'
    >>> domain_of("S1.68") is None
    True
    """
    if not standard_id.startswith(DOMAIN_PREFIX):
        return None
    return standard_id.split(".", 1)[0].upper()


@dataclass(frozen=True)
class Applicable:
    """Findings split by whether the project declared the law they cite."""

    findings: list[Finding]
    """Everything the project is subject to — core, plus its declared domains."""

    withheld: list[Finding]
    """Findings from Layer 4 domains the project has not declared."""

    @property
    def withheld_domains(self) -> list[str]:
        """The domains that were withheld, in a stable order."""
        return sorted({d for f in self.withheld if (d := domain_of(f.standard))})

    @property
    def note(self) -> str:
        """A one-line account of what was withheld, or "" when nothing was.

        Phrased as an offer rather than a warning: the reader who wants these
        findings needs to know the single line of TOML that returns them, and a
        message that only reports a subtraction sends them to the source.
        """
        if not self.withheld:
            return ""
        domains = ", ".join(self.withheld_domains)
        return (
            f"{len(self.withheld)} finding(s) withheld — Layer 4 {domains} "
            f"not declared in governance/project.toml. Add "
            f'domains = ["{self.withheld_domains[0]}"] to be governed by it.'
        )


def for_declared_domains(
    findings: Iterable[Finding], declared: Iterable[str] | None
) -> Applicable:
    """Partition `findings` by the domains the project has declared.

    `declared` is the profile's `domains` list; `None` means no profile exists at
    all. Both mean the same thing here — nothing has been declared — because a
    project with no profile has adopted no sector, exactly like one whose profile
    leaves the field commented out. That is the state every new adopter is in.
    """
    adopted = {d.upper() for d in (declared or ())}
    kept: list[Finding] = []
    withheld: list[Finding] = []
    for f in findings:
        domain = domain_of(f.standard)
        (kept if domain is None or domain in adopted else withheld).append(f)
    return Applicable(findings=kept, withheld=withheld)
