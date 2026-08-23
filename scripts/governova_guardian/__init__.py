"""governova_guardian — the consolidated PR governance verdict.

One panel for a pull request: the overall Governova Score, the enforcement result on
this PR's changed files (blocking vs advisory), and enforcement coverage. Designed to
render in the GitHub job summary so every PR carries a single, plain governance verdict.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from governova_checks import (
    DEFAULT_IGNORES,
    Finding,
    changed_files,
    enforcement_coverage,
    for_declared_domains,
    is_ignored,
    scan_paths,
)
from governova_compile.discovery import resolve_repo_root
from governova_compile.writer import load_active_index
from governova_project import load_profile
from governova_score import compute_score
from governova_score.model import GovernovaScore


@dataclass(frozen=True)
class GuardianVerdict:
    base: str
    files_scanned: int
    findings: list[Finding]
    score: GovernovaScore
    coverage: dict[str, Any]
    generated_on: str = ""
    withheld_note: str = ""
    """What Layer 4 law was not enforced, and why. Empty when nothing was withheld."""

    @property
    def blocking(self) -> list[Finding]:
        return [f for f in self.findings if f.blocking]

    @property
    def advisory(self) -> list[Finding]:
        return [f for f in self.findings if not f.blocking]

    @property
    def passed(self) -> bool:
        return not self.blocking


def build_verdict(base: str = "origin/main", root: Path | None = None) -> GuardianVerdict:
    """Assemble the Guardian verdict for the changes vs `base`."""
    r = root or resolve_repo_root()
    scannable = [
        p
        for p in changed_files(base, r)
        if p.is_file() and not is_ignored(_rel(p, r), DEFAULT_IGNORES)
    ]
    # The Guardian is a merge gate like `governova-enforce`, and answers to the
    # same body of law: core standards always, Layer 4 only where declared.
    profile = load_profile(r)
    applicable = for_declared_domains(
        scan_paths(scannable), profile.domains if profile else None
    )
    findings = applicable.findings
    score = compute_score(r)
    coverage = enforcement_coverage(load_active_index(start=r))
    return GuardianVerdict(
        base=base,
        files_scanned=len(scannable),
        findings=findings,
        score=score,
        coverage=coverage,
        withheld_note=applicable.note,
    )


def _rel(p: Path, root: Path) -> str:
    try:
        return p.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return p.as_posix()


def to_markdown(v: GuardianVerdict) -> str:
    icon = "✅" if v.passed else "❌"
    headline = (
        "Governance verdict: **PASS** — no blocking violations on this PR."
        if v.passed
        else f"Governance verdict: **BLOCKED** — {len(v.blocking)} blocking violation(s) must be fixed."
    )
    lines = [
        f"## {icon} Governova Guardian",
        "",
        headline,
        "",
        "| | |",
        "|--|--|",
        # ADR-012 — a headline is withheld below quorum rather than qualified.
        # This surface posts to a pull request, where a number is quoted and a
        # caveat beside it is not.
        (
            f"| **Governova Score** | {v.score.score}/100 ({v.score.grade}) |"
            if v.score.headline is not None
            else (
                "| **Governova Score** | partial assessment — "
                f"{len(v.score.assessed_factors)} of {len(v.score.factors)} factor(s), "
                f"{v.score.assessed_weight}% of the model |"
            )
        ),
        f"| **This PR** | {len(v.blocking)} blocking · {len(v.advisory)} advisory · "
        f"{v.files_scanned} file(s) scanned |",
        f"| **Enforcement coverage** | {v.coverage.get('coverage_pct')}% "
        f"({v.coverage.get('enforceable_anti_patterns')}/{v.coverage.get('total_anti_patterns')} anti-patterns) |",
    ]
    if v.withheld_note:
        # Stated on the panel, not only in the code. A reviewer reading a PASS
        # is entitled to know which body of law was not consulted to produce it.
        lines.append(f"| **Not enforced** | {v.withheld_note} |")
    if v.findings:
        lines += ["", "### Findings on this PR", ""]
        for f in (*v.blocking, *v.advisory):
            kind = "**BLOCK**" if f.blocking else "warn"
            loc = f"{f.file}:{f.line}" if f.file else "?"
            lines.append(f"- {kind} `{loc}` **{f.anti_pattern}** ({f.standard}) — {f.message}")
    lines += [
        "",
        "*Reliable tier only (deterministic). Advisory findings never block. "
        "Generated automatically by Governova.*",
    ]
    return "\n".join(lines)


__all__ = ["GuardianVerdict", "build_verdict", "to_markdown"]
