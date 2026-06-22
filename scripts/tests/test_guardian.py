"""Tests for the PR Guardian (governova_guardian)."""

from __future__ import annotations

from governova_checks import Finding
from governova_guardian import GuardianVerdict, build_verdict, to_markdown
from governova_score.model import Factor, finalize

COV = {"coverage_pct": 6.8, "enforceable_anti_patterns": 30, "total_anti_patterns": 441}


def _verdict(findings):
    score = finalize([Factor("violation_rate", "Violation rate", 30, 100.0, "")])
    return GuardianVerdict(base="origin/main", files_scanned=3, findings=findings, score=score, coverage=COV)


def _finding(conf):
    return Finding(
        anti_pattern="AP-S2.10b", standard="S2.10", message="secret in DSN",
        match="x", line=4, col=1, confidence=conf, file="src/a.ts",
    )


def test_markdown_pass_when_no_blocking():
    md = to_markdown(_verdict([_finding("medium")]))
    assert "PASS" in md and "Governova Guardian" in md
    assert "Governova Score" in md and "6.8%" in md


def test_markdown_blocked_when_blocking_present():
    v = _verdict([_finding("high")])
    assert not v.passed and len(v.blocking) == 1
    md = to_markdown(v)
    assert "BLOCKED" in md and "AP-S2.10b" in md


def test_build_verdict_no_changes_passes():
    # Diffing HEAD against itself yields no changed files -> a clean PASS verdict.
    v = build_verdict("HEAD")
    assert v.files_scanned == 0 and v.passed
    assert 0 <= v.score.score <= 100
