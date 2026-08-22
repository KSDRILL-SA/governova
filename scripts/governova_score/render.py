"""Render a GovernovaScore as text, markdown, JSON, or a shields badge."""

from __future__ import annotations

import json
from urllib.parse import quote

from governova_score.model import QUORUM_WEIGHT, GovernovaScore


def _badge_colour(score: int) -> str:
    if score >= 85:
        return "brightgreen"
    if score >= 70:
        return "green"
    if score >= 60:
        return "yellow"
    return "red"


def _factor_line(score: GovernovaScore) -> list[tuple[str, str, str]]:
    """(title, weight, status) rows for the breakdown."""
    rows = []
    for f in score.factors:
        status = f"{f.score:.0f}/100 — {f.detail}" if f.assessed else f"not assessed — {f.detail}"
        rows.append((f.title, f"{f.weight}%", status))
    return rows


# ADR-012 — below a quorum of the model there is no Governova Score, and every
# surface that renders one has to know that. This module is the one whose whole
# job is rendering it, and it was the last to find out: the amendment landed
# across the CLI, the guardian, the dashboard, the board report and the
# onboarding payload, and left `to_badge`, `to_markdown`, `to_text` and `to_json`
# printing the arithmetic as a headline.
#
# The badge is the one that matters most. It goes in a README, publicly, and it
# would have shown `0/100 (F)` for a repository that was never measured — which
# is the exact first impression the amendment was written to stop.
#
# `test_every_score_renderer_honours_the_quorum` walks this module's public
# surface, so a fifth renderer added later cannot quietly skip it.
_PARTIAL = "partial assessment"


def _partial_note(score: GovernovaScore) -> str:
    """One sentence, used wherever a headline would otherwise go."""
    return (
        f"{len(score.assessed_factors)} of {len(score.factors)} factor(s) assessed "
        f"({score.assessed_weight}% of the model) — no score is issued below "
        f"{QUORUM_WEIGHT}%."
    )


def to_json(score: GovernovaScore) -> str:
    return json.dumps(
        {
            # `headline` is null below quorum; `score` remains the arithmetic over
            # whatever was assessed. A consumer must be able to tell the
            # difference, which is precisely what the text surfaces withhold.
            "headline": score.headline,
            "has_quorum": score.has_quorum,
            "score": score.score,
            "grade": score.grade,
            "certified_eligible": score.certified_eligible,
            "assessed_weight": score.assessed_weight,
            "factors": [
                {
                    "key": f.key,
                    "title": f.title,
                    "weight": f.weight,
                    "score": f.score,
                    "assessed": f.assessed,
                    "detail": f.detail,
                }
                for f in score.factors
            ],
        },
        indent=2,
    )


def to_badge(score: GovernovaScore) -> str:
    label = quote("Governova Score")
    if score.headline is None:
        # A README badge is the most public surface there is. Showing a number
        # here that rests on a minority of the model publishes it.
        msg = quote(f"{_PARTIAL} ({score.assessed_weight}% assessed)")
        colour = "lightgrey"
    else:
        msg = quote(f"{score.score}/100 ({score.grade})")
        colour = _badge_colour(score.score)
    url = f"https://img.shields.io/badge/{label}-{msg}-{colour}"
    return f"![Governova Score]({url})"


def to_markdown(score: GovernovaScore) -> str:
    if score.headline is None:
        # Saying "below the threshold" implies it was measured against one.
        heading = "## Governova Score: not issued"
        cert = _partial_note(score)
    else:
        heading = f"## Governova Score: {score.score}/100 — {score.grade}"
        cert = (
            "✅ **Governova Certified eligible** (≥85)"
            if score.certified_eligible
            else "Below the Governova Certified threshold (85)"
        )
    lines = [
        heading,
        "",
        cert,
        "",
        "| Factor | Weight | Assessment |",
        "|--------|--------|------------|",
    ]
    for title, weight, status in _factor_line(score):
        lines.append(f"| {title} | {weight} | {status} |")
    lines += [
        "",
        f"*Scored over {score.assessed_weight}% of factor weight; the rest awaits "
        "runtime instrumentation (relay, audit). Model: master.md §18.1.*",
    ]
    return "\n".join(lines)


def to_text(score: GovernovaScore) -> str:
    if score.headline is None:
        lines = [f"Governova Score: not issued — {_PARTIAL}"]
    else:
        lines = [f"Governova Score: {score.score}/100  [{score.grade}]"]
    for title, weight, status in _factor_line(score):
        lines.append(f"  {title} ({weight}): {status}")
    if score.headline is None:
        lines.append(_partial_note(score))
    else:
        lines.append(
            "Governova Certified eligible (>=85)"
            if score.certified_eligible
            else "Below Governova Certified threshold (85)"
        )
    return "\n".join(lines)
