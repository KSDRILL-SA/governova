"""governova_dashboard — a self-contained HTML governance dashboard.

Composes the Governova Score, enforcement coverage, and the constitutional R/A/G
areas into a single standalone HTML page (no server, no external assets).
"""

from __future__ import annotations

from pathlib import Path

from governova_checks import enforcement_coverage
from governova_compile.discovery import resolve_repo_root
from governova_compile.writer import load_active_index
from governova_report import build_report

from governova_dashboard.render import to_html


def build_html(root: Path | None = None) -> str:
    """Build the dashboard HTML for the repo rooted at `root`."""
    r = root or resolve_repo_root()
    report = build_report(r)
    # Resolved rather than assumed — see `governova_score.compute`.
    index = load_active_index(start=r)
    coverage = enforcement_coverage(index)
    return to_html(report, coverage)


__all__ = ["build_html", "to_html"]
