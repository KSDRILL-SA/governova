"""Markdown link-integrity check (locked decision D5).

Scans every tracked markdown file for relative `[text](path)` links and verifies
the target file exists. External links (http/https/mailto), pure anchors (#...),
and template placeholders ({...}) are skipped.
"""

from __future__ import annotations

import re
from pathlib import Path

from governova_compile.schema import IntegrityIssue, Severity

LINK = re.compile(r"\[(?P<text>[^\]]*)\]\((?P<target>[^)]+)\)")
INLINE_CODE = re.compile(r"`+[^`]*`+")
SKIP_PREFIXES = ("http://", "https://", "mailto:", "tel:", "#")


def _should_skip(target: str) -> bool:
    t = target.strip()
    if not t or t.startswith(SKIP_PREFIXES):
        return True
    # Template placeholders like {system} or {N} are not real paths.
    return "{" in t or "}" in t


def _iter_markdown_files(repo_root: Path) -> list[Path]:
    skip_dirs = {".git", ".venv", "node_modules", "compiled", "dist", "build"}
    files: list[Path] = []
    for path in repo_root.rglob("*.md"):
        if any(part in skip_dirs for part in path.parts):
            continue
        files.append(path)
    return sorted(files)


def check_links(repo_root: Path) -> tuple[list[IntegrityIssue], int]:
    """Return (issues, links_checked)."""
    issues: list[IntegrityIssue] = []
    checked = 0

    for md in _iter_markdown_files(repo_root):
        rel = md.relative_to(repo_root)
        lines = md.read_text(encoding="utf-8").splitlines()
        in_code = False
        for lineno, line in enumerate(lines, start=1):
            if line.lstrip().startswith("```"):
                in_code = not in_code
                continue
            if in_code:
                continue
            # Strip inline code spans so `[text](path)` examples aren't treated as links.
            scannable = INLINE_CODE.sub("", line)
            for m in LINK.finditer(scannable):
                target = m.group("target").strip()
                if _should_skip(target):
                    continue
                checked += 1
                # Strip any anchor fragment from the path portion.
                path_part = target.split("#", 1)[0]
                if not path_part:
                    continue
                resolved = (md.parent / path_part).resolve()
                if not resolved.exists():
                    issues.append(
                        IntegrityIssue(
                            severity=Severity.SEV2,
                            code="broken-link",
                            message=f"Link target does not exist: {target}",
                            source_path=str(rel),
                            source_line=lineno,
                        )
                    )
    return issues, checked
