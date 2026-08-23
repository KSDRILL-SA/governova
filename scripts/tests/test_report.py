"""Tests for the Board-Level Governance Report (governova_report)."""

from __future__ import annotations

import json

from governova_report import build_report, to_json, to_markdown
from governova_report.model import (
    AMBER,
    GREEN,
    RED,
    AreaStatus,
    BoardReport,
    GovernanceEvents,
)
from governova_score.model import Factor, finalize


def _report(areas, score_value=100, *, assessed_weight=50):
    """A board report at quorum by default.

    The fixture previously used `violation_rate` alone — 30% of the model. Under
    ADR-012 that is a partial assessment and issues no headline score, so these
    tests would have been exercising the partial wording while claiming to test
    the red/amber/green wording. Reaching quorum keeps each test on its subject;
    `assessed_weight=30` opts back into the partial case for the test that wants
    it.
    """
    factors = [Factor("violation_rate", "Violation rate", 30, float(score_value), "")]
    if assessed_weight >= 50:
        factors.append(
            Factor("constitutional_coverage", "Constitutional coverage", 20, float(score_value), "")
        )
    score = finalize(factors)
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
    # Composition test against the real repo: the 15 core constitutions plus the
    # one Layer 4 domain this project declares (`D-SAAS`), and the counts add up.
    br = build_report()
    assert len(br.areas) == 16
    assert br.areas_green + br.areas_amber + br.areas_red == 16
    assert br.events.adrs >= 1 and br.events.runbooks >= 1
    assert 0 <= br.score.score <= 100


def test_a_declared_domain_gets_an_area(tmp_path):
    """The board could not show a Layer 4 finding at all.

    `std_to_con` and the tally were both built from `index.constitutions`, and
    the compiled index keeps `domains` in a separate list — so every domain
    finding was dropped, silently, for every project. The sector standards are
    the ones with a regulatory basis behind them, and a report structurally
    incapable of showing such a finding is worse than one omitting the section,
    because the omission reads as an absence of findings.
    """
    ids = {a.constitution_id for a in build_report().areas}
    assert "D-SAAS" in ids, "this repository declares D-SAAS and it must appear"


def test_an_undeclared_domain_gets_no_area():
    """The report answers to the same law as the gate and the score: a domain the
    project has not adopted contributes no row and no finding."""
    ids = {a.constitution_id for a in build_report().areas}
    assert "D-FINTECH" not in ids
    assert "D-EDTECH" not in ids
    assert "D-GOVTECH" not in ids


def test_headline_states_a_partial_assessment_rather_than_a_score():
    """ADR-012 — below quorum the sentence reports what was measured and stops.

    Saying a repository "is below the certification threshold" implies it was
    measured against that threshold. On a partial assessment it was not, and the
    board report is exactly the surface where that sentence gets quoted.
    """
    br = _report([_area("C01", GREEN)], assessed_weight=30)
    assert "Partial assessment" in br.headline
    assert "certification threshold" not in br.headline
    assert "out of 100" not in br.headline and "/100" not in br.headline


def test_a_partial_headline_still_names_blocking_violations():
    """Quorum governs the score, not the findings. Blocking violations are real."""
    br = _report([_area("C01", RED, blocking=2)], assessed_weight=30)
    assert "blocking violations" in br.headline
