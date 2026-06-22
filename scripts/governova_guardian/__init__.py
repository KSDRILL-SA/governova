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
    is_ignored,
    scan_paths,
)
from governova_compile.discovery import resolve_repo_root
from governova_compile.writer import load_index
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
    findings = scan_paths(scannable)
    score = compute_score(r)
    coverage = enforcement_coverage(load_index(r / "compiled" / "constitution.json"))
    return GuardianVerdict(
        base=base,
        files_scanned=len(scannable),
        findings=findings,
        score=score,
        coverage=coverage,
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
        f"| **Governova Score** | {v.score.score}/100 ({v.score.grade}) |",
        f"| **This PR** | {len(v.blocking)} blocking · {len(v.advisory)} advisory · "
        f"{v.files_scanned} file(s) scanned |",
        f"| **Enforcement coverage** | {v.coverage.get('coverage_pct')}% "
        f"({v.coverage.get('enforceable_anti_patterns')}/{v.coverage.get('total_anti_patterns')} anti-patterns) |",
    ]
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
