"""Render a GovernovaScore as text, markdown, JSON, or a shields badge."""

from __future__ import annotations

import json
from urllib.parse import quote

from governova_score.model import GovernovaScore


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


def to_json(score: GovernovaScore) -> str:
    return json.dumps(
        {
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
    msg = quote(f"{score.score}/100 ({score.grade})")
    url = f"https://img.shields.io/badge/{label}-{msg}-{_badge_colour(score.score)}"
    return f"![Governova Score]({url})"


def to_markdown(score: GovernovaScore) -> str:
    cert = (
        "✅ **Governova Certified eligible** (≥85)"
        if score.certified_eligible
        else "Below the Governova Certified threshold (85)"
    )
    lines = [
        f"## Governova Score: {score.score}/100 — {score.grade}",
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
    lines = [f"Governova Score: {score.score}/100  [{score.grade}]"]
    for title, weight, status in _factor_line(score):
        lines.append(f"  {title} ({weight}): {status}")
    lines.append(
        "Governova Certified eligible (>=85)"
        if score.certified_eligible
        else "Below Governova Certified threshold (85)"
    )
    return "\n".join(lines)
