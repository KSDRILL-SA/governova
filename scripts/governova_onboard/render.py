"""Render a Baseline for a human, and for a machine.

The console form is the product. **The first run against somebody else's
repository is the only first impression this product gets**, so the ordering here
is a design decision rather than a layout one: what the repository *is* comes
first, because a reader who disagrees with the profile should stop reading the
numbers; the score comes next; the heatmap after that; and the findings last,
capped, because a list nobody finishes changes nothing.

The JSON form carries everything, uncapped and unsorted for presentation, so a
consumer building on top of this is not reverse-engineering a table.
"""

from __future__ import annotations

import json

from rich.table import Table

from governova_onboard.baseline import DEFAULT_TOP, EXAMPLE_FILES, Baseline
from governova_onboard.detect import DIMENSIONS
from governova_onboard.roadmap import Kind, Protection, Roadmap

_VERDICT_MARK = {"satisfied": "[green]✓[/]", "violated": "[red]✗[/]", "unknown": "[yellow]?[/]"}

# What each probed dimension is called in the report, and what its absence means.
# Naming the absence is the point: "no CI configuration found" is a finding an
# adopter can act on, where a missing table row is just a gap in the output.
_ABSENT: dict[str, str] = {
    "stack": "no recognised manifest found — stack undetected",
    "language": "no source files in a recognised language",
    "tests": "no test files or test directories found",
    "ci": "no CI configuration found",
    "schema": "no Prisma or SQL schema found",
    "requirements": "no requirement identifiers reachable (tier 0 — never a violation)",
}


def profile_table(baseline: Baseline) -> Table:
    """What the repository is, one row per probed dimension — including misses."""
    table = Table("Dimension", "Detected", "Evidence", box=None, pad_edge=False)
    for dimension in DIMENSIONS:
        signals = baseline.detection.of(dimension)
        if not signals:
            table.add_row(dimension, "[yellow]—[/]", f"[dim]{_ABSENT[dimension]}[/]")
            continue
        for index, signal in enumerate(signals[:4]):
            table.add_row(dimension if index == 0 else "", signal.value, f"[dim]{signal.evidence}[/]")
    for dimension in ("domain", "phase"):
        table.add_row(
            dimension,
            "[yellow]—[/]",
            "[dim]not derivable from code — a human decides this[/]",
        )
    return table


def score_table(baseline: Baseline) -> Table:
    """All five §18.1 factors, including the ones that could not be assessed."""
    table = Table("Factor", "Weight", "Assessment", box=None, pad_edge=False)
    for factor in baseline.score.factors:
        assessment = (
            f"{factor.score:.0f}/100 — {factor.detail}"
            if factor.assessed
            else f"[yellow]not assessed[/] — {factor.detail}"
        )
        table.add_row(factor.title, f"{factor.weight}%", assessment)
    return table


def heatmap_table(baseline: Baseline) -> Table:
    """Applicable / evidenced / violated / unknown, per core constitution."""
    table = Table(
        "", "Constitution", "Applicable", "Evidenced", "Violated", "Unknown",
        box=None, pad_edge=False,
    )
    for gap in baseline.gaps:
        table.add_row(
            gap.constitution_id,
            gap.name,
            str(gap.applicable),
            f"[green]{gap.evidenced}[/]" if gap.evidenced else "0",
            f"[red]{gap.violated}[/]" if gap.violated else "0",
            f"[yellow]{gap.unknown}[/]" if gap.unknown else "0",
        )
    table.add_row(
        "", "[bold]Total[/]", f"[bold]{baseline.applicable}[/]",
        f"[bold]{baseline.evidenced}[/]", f"[bold]{baseline.violated}[/]",
        f"[bold]{baseline.unknown}[/]",
    )
    return table


def findings_table(baseline: Baseline, *, top: int = DEFAULT_TOP) -> Table:
    """The top finding groups, blocking first.

    File lists are capped here rather than upstream: the cap is a property of a
    table a human reads, not of the finding.
    """
    table = Table(
        "", "Anti-pattern", "Standard", "Count", "Files", "Where",
        box=None, pad_edge=False,
    )
    for group in baseline.groups[:top]:
        mark = "[red]blocking[/]" if group.blocking else "[yellow]advisory[/]"
        shown = list(group.files[:EXAMPLE_FILES])
        if group.reach > EXAMPLE_FILES:
            shown.append(f"+{group.reach - EXAMPLE_FILES} more")
        table.add_row(
            mark, group.anti_pattern, group.standard, str(group.count),
            str(group.reach), f"[dim]{', '.join(shown) if shown else '—'}[/]",
        )
    return table


def structural_table(baseline: Baseline) -> Table:
    """Probe violations — the findings that are facts about the repository."""
    table = Table("", "Standard", "Evidence", box=None, pad_edge=False)
    for result in baseline.violated_probes:
        table.add_row("[red]structural[/]", result.standard, f"[dim]{result.evidence}[/]")
    return table


def probe_table(baseline: Baseline) -> Table:
    """Every structural probe and its verdict — the `unknown`s included."""
    table = Table("", "Standard", "Evidence", box=None, pad_edge=False)
    for result in baseline.probes:
        table.add_row(
            _VERDICT_MARK[str(result.verdict)], result.standard, f"[dim]{result.evidence}[/]"
        )
    return table


def roadmap_table(roadmap: Roadmap, *, top: int | None = None) -> Table:
    """The ordered plan, with the components its ordering was built from.

    Every column except `#` is a measured input to the sort. They are shown so a
    reader can dispute the order by reading it, rather than having to
    reverse-engineer the arithmetic from the rank.
    """
    items = roadmap.items if top is None else roadmap.items[:top]
    table = Table(box=None, pad_edge=False)
    table.add_column("", no_wrap=True)
    table.add_column("Standard", no_wrap=True)
    # Titles are long and vary wildly. Left to wrap, one item takes eight rows
    # and the plan stops being scannable, which defeats the point of ranking it.
    # The console falls back to 80 columns when stdout is not a terminal, so the
    # whole table is built to fit that rather than to look good only when wide.
    table.add_column("What", no_wrap=True, max_width=26, overflow="ellipsis")
    table.add_column("Occ", no_wrap=True, justify="right")
    table.add_column("Files", no_wrap=True, justify="right")
    table.add_column("Test", no_wrap=True, justify="right")
    # Blast and effort collapse into one column rather than three. The ordering
    # still has to be auditable from the table — that is the whole argument for
    # showing components at all — and `5 (20/4)` carries both inputs and the
    # quotient in the space one of them would have taken.
    table.add_column("Leverage", no_wrap=True, justify="right")

    for item in items:
        mark = (
            "[red]block[/]"
            if item.blocking
            else ("[cyan]struct[/]" if item.kind is Kind.STRUCTURAL else "[yellow]advis[/]")
        )
        tests = (
            "[green]ok[/]"
            if item.protection is Protection.PROTECTED and item.protected_by
            else ("[dim]n/a[/]" if item.kind is Kind.STRUCTURAL else "[yellow]?[/]")
        )
        table.add_row(
            mark, item.standard, item.title,
            str(item.occurrences), str(item.reach), tests,
            f"{item.leverage:g} ({item.blast}/{item.effort})",
        )
    return table


def roadmap_to_json(roadmap: Roadmap) -> str:
    """The whole plan, machine-readable — issue-shaped, one item per PR."""
    return json.dumps(
        {
            "items": [
                {
                    "rank": position,
                    "kind": str(item.kind),
                    "standard": item.standard,
                    "title": item.title,
                    "anti_pattern": item.anti_pattern,
                    "summary": item.summary,
                    "occurrences": item.occurrences,
                    "files": list(item.files),
                    "blocking": item.blocking,
                    "priority": str(item.priority),
                    "dependents": item.dependents,
                    "protection": str(item.protection),
                    "protected_by": list(item.protected_by),
                    "needs_characterisation_test": item.needs_characterisation_test,
                    "blast": item.blast,
                    "effort": item.effort,
                    "leverage": item.leverage,
                }
                for position, item in enumerate(roadmap.items, start=1)
            ],
            "totals": {
                "items": len(roadmap),
                "blocking": len(roadmap.blocking_items),
                "needing_characterisation_tests": len(roadmap.needing_tests),
            },
        },
        indent=2,
    )


def to_json(baseline: Baseline, *, top: int | None = None) -> str:
    """The whole baseline, machine-readable. `top` caps findings; None means all."""
    groups = baseline.groups if top is None else baseline.groups[:top]
    payload = {
        "root": baseline.root.as_posix(),
        "provisional": list(baseline.provisional),
        "profile": {
            "name": baseline.profile.name,
            "stacks": list(baseline.profile.stacks),
            "domains": list(baseline.profile.domains),
            "phase": baseline.profile.phase,
        },
        "detection": {
            "files_scanned": baseline.detection.files_scanned,
            "truncated": baseline.detection.truncated,
            "undetected": list(baseline.detection.undetected),
            "signals": [
                {"dimension": s.dimension, "value": s.value, "evidence": s.evidence}
                for s in baseline.detection.signals
            ],
        },
        "score": {
            "score": baseline.score.score,
            "grade": baseline.score.grade,
            "assessed_weight": baseline.score.assessed_weight,
            "factors": [
                {
                    "key": f.key,
                    "weight": f.weight,
                    "score": f.score,
                    "assessed": f.assessed,
                    "detail": f.detail,
                }
                for f in baseline.score.factors
            ],
        },
        "heatmap": {
            "totals": {
                "applicable": baseline.applicable,
                "evidenced": baseline.evidenced,
                "violated": baseline.violated,
                "unknown": baseline.unknown,
            },
            "constitutions": [
                {
                    "id": g.constitution_id,
                    "name": g.name,
                    "applicable": g.applicable,
                    "evidenced": g.evidenced,
                    "violated": g.violated,
                    "unknown": g.unknown,
                }
                for g in baseline.gaps
            ],
        },
        "findings": [
            {
                "anti_pattern": g.anti_pattern,
                "standard": g.standard,
                "message": g.message,
                "confidence": g.confidence,
                "blocking": g.blocking,
                "count": g.count,
                "files": list(g.files),
            }
            for g in groups
        ],
        "structural_violations": [
            {"standard": p.standard, "evidence": p.evidence} for p in baseline.violated_probes
        ],
        "probes": [
            {"standard": p.standard, "verdict": str(p.verdict), "evidence": p.evidence}
            for p in baseline.probes
        ],
        "source_files": baseline.source_files,
    }
    return json.dumps(payload, indent=2)


__all__ = [
    "findings_table",
    "heatmap_table",
    "probe_table",
    "profile_table",
    "roadmap_table",
    "roadmap_to_json",
    "score_table",
    "structural_table",
    "to_json",
]
