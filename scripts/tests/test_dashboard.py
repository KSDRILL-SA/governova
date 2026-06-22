"""Tests for the web dashboard (governova_dashboard)."""

from __future__ import annotations

from governova_dashboard import build_html, to_html
from governova_report.model import AreaStatus, BoardReport, GovernanceEvents, GREEN, RED
from governova_score.model import Factor, finalize


def _report():
    score = finalize([Factor("violation_rate", "Violation rate", 30, 100.0, "")])
    areas = [
        AreaStatus("C01", "Engineering", GREEN, 0, 0, 102),
        AreaStatus("C03", "Auth", RED, 1, 0, 37),
    ]
    return BoardReport("2026-06-22", score, areas, GovernanceEvents(2, 5, 8))


def test_to_html_is_self_contained_and_complete():
    cov = {
        "coverage_pct": 6.8, "enforceable_anti_patterns": 30, "total_anti_patterns": 441,
        "blocking_rules": 7, "advisory_rules": 23,
    }
    out = to_html(_report(), cov)
    assert out.startswith("<!doctype html>")
    assert "<style>" in out and "<script" not in out  # self-contained, no JS
    assert "Governova Score" in out and "100" in out and "A+" in out
    assert "6.8%" in out
    assert "Engineering" in out and "Auth" in out  # both areas rendered


def test_build_html_on_repo():
    out = build_html()
    assert out.startswith("<!doctype html>")
    assert "Governance Dashboard" in out and "Enforcement coverage" in out
