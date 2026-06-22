"""governova_bible — the System Bible (master.md §18.4).

Per-file documentation of the whole codebase: purpose, public surface, and
dependencies for every source file, rendered as a navigable document.
"""

from __future__ import annotations

from governova_bible.compute import build_bible
from governova_bible.extract import extract_file
from governova_bible.model import FileEntry, SystemBible
from governova_bible.render import to_json, to_markdown

__all__ = [
    "FileEntry",
    "SystemBible",
    "build_bible",
    "extract_file",
    "to_json",
    "to_markdown",
]
