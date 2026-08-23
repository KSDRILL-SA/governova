"""Assemble the Board-Level Governance Report from the engine + governance records."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from governova_checks import for_declared_domains, iter_source_files, scan_paths
from governova_compile.discovery import resolve_repo_root
from governova_compile.writer import load_active_index
from governova_project import load_profile
from governova_score import compute_score

from governova_report.model import (
    AMBER,
    GREEN,
    RED,
    AreaStatus,
    BoardReport,
    GovernanceEvents,
)

_DATE_ROW = re.compile(r"^\|\s*\d{4}-\d{2}-\d{2}\s*\|")


def _governance_events(root: Path) -> GovernanceEvents:
    log = root / "governance" / "changelog" / "amendments-log.md"
    amendments = 0
    if log.is_file():
        amendments = sum(1 for line in log.read_text(encoding="utf-8").splitlines() if _DATE_ROW.match(line))
    decisions = root / "governance" / "decisions"
    adrs = len(list(decisions.glob("ADR-*.md"))) if decisions.is_dir() else 0
    runbooks_dir = root / "governance" / "runbooks"
    runbooks = len(list(runbooks_dir.glob("RB-*.md"))) if runbooks_dir.is_dir() else 0
    return GovernanceEvents(amendments=amendments, adrs=adrs, runbooks=runbooks)


def build_report(root: Path | None = None, *, today: date | None = None) -> BoardReport:
    """Build the board report for the repo rooted at `root`."""
    r = root or resolve_repo_root()
    score = compute_score(r)
    # `load_active_index` so a board report can be generated from an
    # installed wheel, not only inside a Governova checkout.
    index = load_active_index(start=r)

    # The areas this report covers: the core constitutions, plus the Layer 4
    # domains the project has declared.
    #
    # Both the lookup and the tally were built from `index.constitutions` alone,
    # and the compiled index keeps `domains` in a **separate list**. So
    # `std_to_con.get("D-FINTECH.1")` returned None, `None in tally` was False,
    # and every domain finding was dropped — silently, and for every project,
    # because the declaration was never consulted either.
    #
    # This is the mirror of the defect in the merge gate: that one applied sector
    # law to projects which had never adopted it, this one withheld it from the
    # board of a project that had. The sector standards are the ones with a
    # regulatory basis behind them — PCI-DSS, FICA, FATF — and a board report
    # structurally incapable of showing such a finding is worse than one that
    # omits the section, because the omission reads as an absence of findings.
    profile = load_profile(r)
    declared = profile.domains if profile else []
    documents = [*index.constitutions, *(d for d in index.domains if d.id.upper() in declared)]

    std_to_con = {s.id: s.constitution_id for c in documents for s in c.standards}
    tally: dict[str, dict[str, int]] = {c.id: {"blocking": 0, "advisory": 0} for c in documents}
    # An undeclared domain contributes no row here and no finding anywhere else,
    # so the report answers to the same body of law as the gate and the score.
    findings = for_declared_domains(scan_paths(list(iter_source_files(r))), declared).findings
    for f in findings:
        cid = std_to_con.get(f.standard)
        if cid in tally:
            tally[cid]["blocking" if f.blocking else "advisory"] += 1

    areas: list[AreaStatus] = []
    for c in documents:
        b = tally[c.id]["blocking"]
        a = tally[c.id]["advisory"]
        status = RED if b else AMBER if a else GREEN
        areas.append(
            AreaStatus(
                constitution_id=c.id,
                name=c.name,
                status=status,
                blocking=b,
                advisory=a,
                standards=len(c.standards),
            )
        )

    return BoardReport(
        generated_on=(today or date.today()).isoformat(),
        score=score,
        areas=areas,
        events=_governance_events(r),
    )
