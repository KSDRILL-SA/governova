"""Tests for the project Governova Score (governova_score)."""

from __future__ import annotations

import json

from governova_score import compute_score, grade_for, to_badge, to_json, to_markdown
from governova_score.model import Factor, finalize


def _ts(tmp_path, name, content):
    (tmp_path / name).write_text(content, encoding="utf-8")


def test_clean_repo_scores_high(tmp_path):
    _ts(tmp_path, "app.ts", "const sum = a + b;\n")
    gs = compute_score(tmp_path)
    vr = next(f for f in gs.factors if f.key == "violation_rate")
    assert vr.assessed and vr.score == 100.0
    assert gs.score == 100 and gs.grade == "A+"


def test_violations_lower_the_score(tmp_path):
    _ts(tmp_path, "app.ts", "localStorage.setItem('access_token', t);\n")  # 1 blocking
    gs = compute_score(tmp_path)
    vr = next(f for f in gs.factors if f.key == "violation_rate")
    assert vr.score == 90.0  # 100 - 10 per blocking
    assert gs.score == 90


def test_runtime_factors_not_assessed(tmp_path):
    _ts(tmp_path, "app.ts", "const x = 1;\n")
    gs = compute_score(tmp_path)
    for key in ("relay_compliance", "constitutional_coverage", "audit_trail"):
        assert not next(f for f in gs.factors if f.key == key).assessed


def test_amendment_discipline_assessed_when_records_present(tmp_path):
    _ts(tmp_path, "app.ts", "const x = 1;\n")
    (tmp_path / "governance" / "changelog").mkdir(parents=True)
    (tmp_path / "governance" / "decisions").mkdir(parents=True)
    (tmp_path / "governance" / "changelog" / "amendments-log.md").write_text("# log\n- A1\n", encoding="utf-8")
    (tmp_path / "governance" / "decisions" / "ADR-001.md").write_text("# adr\n", encoding="utf-8")
    gs = compute_score(tmp_path)
    amd = next(f for f in gs.factors if f.key == "amendment_discipline")
    assert amd.assessed and amd.score == 100.0


def test_renormalisation_over_assessed_factors():
    factors = [
        Factor("violation_rate", "Violation rate", 30, 100.0, ""),
        Factor("relay_compliance", "Relay", 25, None, ""),
        Factor("constitutional_coverage", "Coverage", 20, None, ""),
        Factor("amendment_discipline", "Amendment", 15, 50.0, ""),
        Factor("audit_trail", "Audit", 10, None, ""),
    ]
    gs = finalize(factors)
    # (100*30 + 50*15) / (30+15) = 3750 / 45 = 83.3 -> 83
    assert gs.score == 83
    assert gs.assessed_weight == 45


def test_grade_thresholds():
    assert grade_for(96) == "A+"
    assert grade_for(85) == "B+"   # Governova Certified threshold
    assert grade_for(84) == "B"
    assert grade_for(59) == "F"


def test_certified_eligibility_boundary():
    factors = [Factor("violation_rate", "Violation rate", 30, 85.0, "")]
    assert finalize(factors).certified_eligible
    factors = [Factor("violation_rate", "Violation rate", 30, 84.0, "")]
    assert not finalize(factors).certified_eligible


def test_renderers(tmp_path):
    _ts(tmp_path, "app.ts", "const x = 1;\n")
    gs = compute_score(tmp_path)
    assert "img.shields.io" in to_badge(gs) and "Governova" in to_badge(gs)
    data = json.loads(to_json(gs))
    assert data["score"] == gs.score and len(data["factors"]) == 5
    assert "Governova Score" in to_markdown(gs)
