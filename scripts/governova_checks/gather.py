"""Shared source-file selection: which files a surface should scan.

One definition of "scannable source", used by both the enforcer (changed files)
and the Governova Score (whole repo). Test code, fixtures, vendored deps, and the
rule set itself are skipped — they legitimately contain violation patterns.
"""

from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import Iterator

from governova_checks.rules import TEXT_EXTENSIONS

# Directories never worth scanning (matched on any path part).
SKIP_DIRS: frozenset[str] = frozenset(
    {
        ".git", ".venv", "venv", "node_modules", "__pycache__", "compiled",
        "dist", "build", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    }
)

# Path globs skipped by default: test code, fixtures, and the rule set itself.
DEFAULT_IGNORES: tuple[str, ...] = (
    "*/tests/*",
    "tests/*",
    "*/test_*",
    "test_*",
    "*_test.*",
    "scripts/governova_checks/rules.py",
)


def is_ignored(rel: str, ignores: tuple[str, ...]) -> bool:
    """Whether a repo-relative posix path matches any ignore glob."""
    return any(fnmatch.fnmatch(rel, pat) for pat in ignores)


def iter_source_files(
    root: Path, *, ignores: tuple[str, ...] = DEFAULT_IGNORES
) -> Iterator[Path]:
    """Yield every scannable source file under `root` (skipping ignores)."""
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        rel = path.relative_to(root).as_posix()
        if is_ignored(rel, ignores):
            continue
        yield path
