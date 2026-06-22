"""governova_score — the project Governova Score (master.md §18.1).

A 0–100 governance score for a repository, computed as a weighted average over the
factors that can be assessed (renormalised), with a transparent per-factor report.
"""

from __future__ import annotations

from governova_score.compute import compute_score
from governova_score.model import (
    CERTIFIED_THRESHOLD,
    WEIGHTS,
    Factor,
    GovernovaScore,
    grade_for,
)
from governova_score.render import to_badge, to_json, to_markdown, to_text

__all__ = [
    "CERTIFIED_THRESHOLD",
    "WEIGHTS",
    "Factor",
    "GovernovaScore",
    "compute_score",
    "grade_for",
    "to_badge",
    "to_json",
    "to_markdown",
    "to_text",
]
