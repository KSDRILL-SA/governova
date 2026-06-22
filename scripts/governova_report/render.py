"""Render the Board-Level Governance Report as markdown or JSON."""

from __future__ import annotations

import json

from governova_report.model import AMBER, GREEN, RED, BoardReport

_DOT = {GREEN: "🟢", AMBER: "🟡", RED: "🔴"}


def to_markdown(report: BoardReport) -> str:
    s = report.score
    cert = (
        "✅ Eligible (score ≥ 85)"
        if s.certified_eligible
        else "Below threshold (85)"
    )
    lines = [
        "# Governova — Board-Level Governance Report",
        "",
        f"*Generated {report.generated_on} · auto-generated · for board, audit, and "
        "stakeholder review*",
        "",
        "## Executive summary",
        "",
        report.headline,
        "",
        "| | |",
        "|--|--|",
        f"| **Governova Score** | **{s.score} / 100 ({s.grade})** |",
        f"| **Governova Certified** | {cert} |",
        f"| **Constitutional areas** | {_DOT[GREEN]} {report.areas_green} green · "
        f"{_DOT[AMBER]} {report.areas_amber} amber · {_DOT[RED]} {report.areas_red} red |",
        "",
        "## Constitutional areas",
        "",
        "| Area | Status | Standards | Assessment |",
        "|------|--------|-----------|------------|",
    ]
    for a in report.areas:
        lines.append(
            f"| {a.constitution_id} — {a.name} | {_DOT[a.status]} {a.status} "
            f"| {a.standards} | {a.summary} |"
        )

    e = report.events
    lines += [
        "",
        "## Governance events",
        "",
        f"- {e.amendments} constitutional amendment(s) recorded in the append-only audit log",
        f"- {e.adrs} architectural decision record(s) (ADRs)",
        f"- {e.runbooks} incident runbook(s) maintained",
        "",
        "## Not yet instrumented",
        "",
        "These require the Governova runtime (audit trail / historical series) and are "
        "not yet included:",
        "",
        "- Score trend over time",
        "- AI action volume",
        "",
        "---",
        "",
        "*Generated automatically by Governova. Scoring model: master.md §18.1–§18.3. "
        "Nobody else generates this report automatically.*",
    ]
    return "\n".join(lines)


def to_json(report: BoardReport) -> str:
    return json.dumps(
        {
            "generated_on": report.generated_on,
            "score": report.score.score,
            "grade": report.score.grade,
            "certified_eligible": report.score.certified_eligible,
            "areas": [
                {
                    "constitution_id": a.constitution_id,
                    "name": a.name,
                    "status": a.status,
                    "blocking": a.blocking,
                    "advisory": a.advisory,
                    "standards": a.standards,
                }
                for a in report.areas
            ],
            "governance_events": {
                "amendments": report.events.amendments,
                "adrs": report.events.adrs,
                "runbooks": report.events.runbooks,
            },
            "areas_summary": {
                "green": report.areas_green,
                "amber": report.areas_amber,
                "red": report.areas_red,
            },
        },
        indent=2,
        ensure_ascii=False,
    )
