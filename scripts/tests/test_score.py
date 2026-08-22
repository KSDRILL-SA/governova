"""Tests for the project Governova Score (governova_score)."""

from __future__ import annotations

import json

from governova_score import compute_score, grade_for, to_badge, to_json, to_markdown
from governova_score.model import Factor, finalize
from governova_score.render import to_text


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
    """The 85 boundary, now tested at quorum.

    This test previously asserted certification on `violation_rate` alone —
    30% of the model — which ADR-012 deliberately stops. The boundary it exists
    to pin is 85 versus 84, and that is unchanged; what moved is that the
    boundary is only reachable once enough of the model has been assessed to
    issue a headline at all.

    The partial case is asserted directly below, so removing certification from
    a one-factor assessment is covered rather than merely no longer tested.
    """
    at_quorum = [
        Factor("violation_rate", "Violation rate", 30, 85.0, ""),
        Factor("constitutional_coverage", "Constitutional coverage", 20, 85.0, ""),
    ]
    assert finalize(at_quorum).certified_eligible
    below = [
        Factor("violation_rate", "Violation rate", 30, 84.0, ""),
        Factor("constitutional_coverage", "Constitutional coverage", 20, 84.0, ""),
    ]
    assert not finalize(below).certified_eligible


def test_certification_is_refused_below_quorum_however_high_the_score():
    """A perfect score on 30% of the model certifies nothing (ADR-012)."""
    factors = [Factor("violation_rate", "Violation rate", 30, 100.0, "")]
    result = finalize(factors)
    assert result.score == 100
    assert not result.certified_eligible


def test_renderers(tmp_path):
    _ts(tmp_path, "app.ts", "const x = 1;\n")
    gs = compute_score(tmp_path)
    assert "img.shields.io" in to_badge(gs) and "Governova" in to_badge(gs)
    data = json.loads(to_json(gs))
    assert data["score"] == gs.score and len(data["factors"]) == 5
    assert "Governova Score" in to_markdown(gs)


# ─── ADR-012 · a score drawn from one factor is not a score ──────────────────


def _factors(**scores: float | None) -> list[Factor]:
    """Build a factor list from `key=score`, with None meaning unassessed."""
    from governova_score.model import TITLES, WEIGHTS

    return [
        Factor(key=k, title=TITLES[k], weight=WEIGHTS[k], score=scores.get(k), detail="")
        for k in WEIGHTS
    ]


def test_one_factor_carrying_thirty_percent_issues_no_headline() -> None:
    """The measured first-contact case, and the reason ADR-012 exists.

    On a repository with no Governova instrumentation four factors return None,
    and `finalize` renormalises 30% of the model onto 100% of the answer.
    `pallets/click` was told 0/100 (F) on that basis by a product it had run
    once. The arithmetic was correct; the claim was not.
    """
    from governova_score.model import finalize

    result = finalize(_factors(violation_rate=0.0))
    assert result.assessed_weight == 30
    assert result.has_quorum is False
    assert result.headline is None
    # The arithmetic is still available — it is the *headline* that is withheld.
    assert result.score == 0


def test_a_good_score_on_one_factor_is_withheld_too() -> None:
    """Quorum is about how much of the model was assessed, not about the answer.

    A rule that only suppressed bad scores would be flattery with extra steps.
    """
    from governova_score.model import finalize

    result = finalize(_factors(violation_rate=95.0))
    assert result.headline is None
    assert result.score == 95


def test_accepting_a_profile_reaches_quorum() -> None:
    """Violation rate (30) plus constitutional coverage (20) is exactly 50.

    Coverage becomes assessable when a human accepts the proposed profile, so
    the score appears once the user has told the tool what it is looking at.
    That is where the threshold was placed, rather than at a number chosen to
    produce a pleasing outcome.
    """
    from governova_score.model import finalize

    result = finalize(_factors(violation_rate=80.0, constitutional_coverage=60.0))
    assert result.assessed_weight == 50
    assert result.has_quorum is True
    assert result.headline == result.score


def test_certification_is_impossible_on_a_partial_assessment() -> None:
    """A repository cannot be Certified on evidence that was never gathered."""
    from governova_score.model import finalize

    result = finalize(_factors(violation_rate=100.0))
    assert result.score == 100
    assert result.certified_eligible is False


def test_certification_still_works_at_quorum() -> None:
    from governova_score.model import finalize

    result = finalize(_factors(violation_rate=100.0, constitutional_coverage=100.0))
    assert result.certified_eligible is True


def test_a_fully_assessed_repository_is_unaffected() -> None:
    """The amendment must not change any reading it was not written to change."""
    from governova_score.model import finalize

    result = finalize(
        _factors(
            violation_rate=100.0,
            relay_compliance=85.0,
            constitutional_coverage=15.0,
            amendment_discipline=100.0,
            audit_trail=100.0,
        )
    )
    assert result.assessed_weight == 100
    assert result.has_quorum is True
    assert result.headline == result.score


def test_violation_density_is_reported_beside_the_count(tmp_path) -> None:
    """The count keeps its meaning; density says how spread out it is.

    52 findings across 32 files and 52 across 3,200 are the same number and
    different situations, and the factor is entitled to say so without
    pretending to have measured something else.
    """
    from governova_score.compute import _violation_rate

    src = tmp_path / "src"
    src.mkdir()
    for i in range(4):
        (src / f"m{i}.ts").write_text("localStorage.setItem('access_token', t);\n", encoding="utf-8")

    factor = _violation_rate(tmp_path)
    assert "per file" in factor.detail
    assert "1.00 per file" in factor.detail


def test_a_clean_repository_reports_no_density(tmp_path) -> None:
    """Zero findings per file is not information, and the line stays readable."""
    from governova_score.compute import _violation_rate

    src = tmp_path / "src"
    src.mkdir()
    (src / "m.ts").write_text("const a = 1;\n", encoding="utf-8")

    factor = _violation_rate(tmp_path)
    assert factor.score == 100
    assert "per file" not in factor.detail


def test_the_violation_factor_arithmetic_is_unchanged(tmp_path) -> None:
    """ADR-012 adds a figure beside the count. It does not redefine the count.

    Every historical reading of `violation_rate` must still mean what it meant,
    which is the whole reason density was added alongside rather than instead.
    """
    from governova_score.compute import _ADVISORY_PENALTY, _violation_rate

    src = tmp_path / "src"
    src.mkdir()
    (src / "m.ts").write_text(
        "localStorage.setItem('access_token', t);\nconsole.log('x');\n", encoding="utf-8"
    )
    factor = _violation_rate(tmp_path)
    # One blocking (AP-S3.14a) and one advisory (AP-S8.31a).
    assert factor.score == 100.0 - 10 - _ADVISORY_PENALTY


# ─── ADR-012 across every renderer, not one at a time ────────────────────────


def test_every_score_renderer_honours_the_quorum() -> None:
    """The sweep, because this amendment has now been missed four times.

    `ADR-012` landed across the CLI, the guardian, the dashboard, the board
    report and the onboarding payload — and left `governova_score.render`, the
    module whose entire job is rendering the score, printing the arithmetic as a
    headline on all four of its surfaces.

    Each was found separately, one surface at a time. This walks the module's
    public renderers instead, so a fifth added later cannot quietly skip it.
    """
    import governova_score.render as render

    partial = finalize([Factor("violation_rate", "Violation rate", 30, 0.0, "")])
    renderers = {
        name: value
        for name, value in vars(render).items()
        if name.startswith("to_") and callable(value)
    }
    assert len(renderers) >= 4, f"expected every renderer, found {sorted(renderers)}"

    for name, renderer in renderers.items():
        rendered = renderer(partial)

        # The *headline* is what ADR-012 withholds, not the breakdown. A factor
        # reporting its own `0/100` in the table below is correct and useful —
        # the amendment's whole point is that the factors are shown and the
        # number drawn from them is not. So this reads the headline line only.
        headline_line = rendered.splitlines()[0] if name != "to_badge" else rendered
        assert "0/100" not in headline_line, f"{name} published a score below quorum"

        if name == "to_json":
            # A machine surface carries the fields and lets the consumer decide.
            # `certified_eligible: false` is correct here precisely *because*
            # `has_quorum: false` sits beside it; a reader gets both or neither.
            payload = json.loads(rendered)
            assert payload["headline"] is None
            assert payload["has_quorum"] is False
            continue

        # A prose surface has no second field to qualify a sentence, so the
        # sentence itself must not claim the repository was measured against a
        # threshold it was never measured against.
        assert "partial" in rendered.lower() or "not issued" in rendered.lower(), (
            f"{name} does not say the assessment is partial"
        )
        assert "below the governova certified" not in rendered.lower(), (
            f"{name} says an unmeasured repository is below a threshold"
        )


def test_the_badge_never_publishes_a_score_below_quorum() -> None:
    """The most public surface there is, and the one worth calling out alone.

    A README badge reading `0/100 (F)` for a repository that was never measured
    is the exact first impression `ADR-012` was written to stop — and unlike a
    terminal line, it is indexed, screenshotted and linked.
    """
    partial = finalize([Factor("violation_rate", "Violation rate", 30, 0.0, "")])
    badge = to_badge(partial)
    assert "0/100" not in badge
    assert "partial" in badge
    assert "brightgreen" not in badge and "red" not in badge


def test_the_json_surface_says_whether_it_has_quorum() -> None:
    """A machine consumer must be able to tell, since it reads no prose."""
    partial = finalize([Factor("violation_rate", "Violation rate", 30, 55.0, "")])
    payload = json.loads(to_json(partial))
    assert payload["headline"] is None
    assert payload["has_quorum"] is False
    # The arithmetic is still available; it is the *headline* that is withheld.
    assert payload["score"] == 55


def test_a_full_assessment_still_renders_its_number_everywhere() -> None:
    """The amendment withholds a headline below quorum and changes nothing above it."""
    import governova_score.render as render

    full = finalize(
        [
            Factor("violation_rate", "Violation rate", 30, 90.0, ""),
            Factor("constitutional_coverage", "Constitutional coverage", 20, 90.0, ""),
        ]
    )
    assert "90/100" in to_badge(full)
    assert "90/100" in to_text(full)
    assert "90/100" in to_markdown(full)
    assert json.loads(to_json(full))["headline"] == 90
    assert render.to_json is to_json
