"""Tests for the Board-Level Governance Report (governova_report)."""

from __future__ import annotations

import json

from governova_report import build_report, to_json, to_markdown
from governova_report.model import AMBER, GREEN, RED, AreaStatus, BoardReport, GovernanceEvents
from governova_score.model import Factor, finalize


def _report(areas, score_value=100):
    score = finalize([Factor("violation_rate", "Violation rate", 30, float(score_value), "")])
    return BoardReport(
        generated_on="2026-06-22",
        score=score,
        areas=areas,
        events=GovernanceEvents(amendments=2, adrs=5, runbooks=8),
    )


def _area(cid, status, blocking=0, advisory=0):
    return AreaStatus(cid, f"{cid} area", status, blocking, advisory, 10)


def test_headline_all_green():
    br = _report([_area("C01", GREEN), _area("C02", GREEN)])
    assert "strong" in br.headline and br.areas_green == 2


def test_headline_amber():
    br = _report([_area("C01", GREEN), _area("C02", AMBER, advisory=1)])
    assert "minor advisories" in br.headline and br.areas_amber == 1


def test_headline_red_needs_attention():
    br = _report([_area("C01", RED, blocking=2)])
    assert "needs attention" in br.headline and br.areas_red == 1


def test_area_summaries():
    assert "No violations" in _area("C01", GREEN).summary
    assert "advisory" in _area("C01", AMBER, advisory=3).summary
    assert "action required" in _area("C01", RED, blocking=1).summary


def test_markdown_render():
    md = to_markdown(_report([_area("C03", RED, blocking=1)]))
    assert "Board-Level Governance Report" in md
    assert "🔴" in md and "Governova Score" in md
    assert "Governance events" in md


def test_json_render():
    data = json.loads(to_json(_report([_area("C01", GREEN), _area("C02", AMBER, advisory=2)])))
    assert data["areas_summary"]["green"] == 1
    assert data["governance_events"]["adrs"] == 5
    assert len(data["areas"]) == 2


def test_build_report_on_repo_is_well_formed():
    # Composition test against the real repo: 12 constitutional areas, counts add up.
    br = build_report()
    assert len(br.areas) == 12
    assert br.areas_green + br.areas_amber + br.areas_red == 12
    assert br.events.adrs >= 1 and br.events.runbooks >= 1
    assert 0 <= br.score.score <= 100
