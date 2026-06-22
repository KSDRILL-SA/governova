"""Render the System Bible as markdown or JSON."""

from __future__ import annotations

import json

from governova_bible.model import SystemBible


def to_markdown(bible: SystemBible) -> str:
    lines = [
        "# Governova — System Bible",
        "",
        "*Per-file documentation of the whole codebase (master.md §18.4). "
        "Auto-generated — what every file is for, what it exposes, and what it depends on.*",
        "",
        f"**{bible.total_files} files · {bible.total_loc} lines of code · "
        f"{bible.documented_pct}% with a stated purpose**",
        "",
    ]
    for area, entries in bible.by_area().items():
        lines.append(f"## {area}")
        lines.append("")
        for e in entries:
            lines.append(f"### `{e.path}`")
            lines.append(f"*{e.language} · {e.loc} LOC*")
            lines.append("")
            lines.append(e.purpose if e.purpose else "_No stated purpose._")
            lines.append("")
            if e.semantic_summary:
                lines.append(f"> **Summary:** {e.semantic_summary}")
                lines.append("")
            if e.public:
                lines.append(f"- **Exposes:** {', '.join(f'`{p}`' for p in e.public)}")
            if e.dependencies:
                lines.append(f"- **Depends on:** {', '.join(f'`{d}`' for d in e.dependencies)}")
            lines.append("")
    lines += [
        "---",
        "",
        "*Deep per-file behavioural descriptions are reserved for the semantic tier; "
        "this edition documents structure (purpose, public surface, dependencies) "
        "deterministically.*",
    ]
    return "\n".join(lines)


def to_json(bible: SystemBible) -> str:
    return json.dumps(
        {
            "total_files": bible.total_files,
            "total_loc": bible.total_loc,
            "documented_pct": bible.documented_pct,
            "files": [
                {
                    "path": e.path,
                    "language": e.language,
                    "loc": e.loc,
                    "purpose": e.purpose,
                    "semantic_summary": e.semantic_summary,
                    "public": e.public,
                    "dependencies": e.dependencies,
                }
                for e in bible.entries
            ],
        },
        indent=2,
        ensure_ascii=False,
    )
