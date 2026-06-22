"""governova_report — the Board-Level Governance Report (master.md §18.3).

A one-page, plain-English governance report for non-technical stakeholders,
composed from the Governova Score, the compiled constitution, and governance records.
"""

from __future__ import annotations

from governova_report.compute import build_report
from governova_report.model import AreaStatus, BoardReport, GovernanceEvents
from governova_report.render import to_json, to_markdown

__all__ = [
    "AreaStatus",
    "BoardReport",
    "GovernanceEvents",
    "build_report",
    "to_json",
    "to_markdown",
]
