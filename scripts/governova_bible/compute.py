"""Build the System Bible by documenting every source file in the repo."""

from __future__ import annotations

from pathlib import Path

from governova_checks import iter_source_files
from governova_compile.discovery import resolve_repo_root

from governova_bible.extract import extract_file
from governova_bible.model import SystemBible


def build_bible(root: Path | None = None) -> SystemBible:
    """Document every source file under `root`.

    Uses an empty ignore set so the Bible covers the whole codebase — including
    tests and the rule set (which the enforcer/score deliberately skip).
    """
    r = root or resolve_repo_root()
    entries = [extract_file(p, r) for p in iter_source_files(r, ignores=())]
    entries.sort(key=lambda e: e.path)
    return SystemBible(entries=entries)
