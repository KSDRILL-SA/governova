"""Shared source-file selection: which files a surface should scan.

One definition of "scannable source", used by both the enforcer (changed files)
and the Governova Score (whole repo). Test code, fixtures, vendored deps, and the
rule set itself are skipped — they legitimately contain violation patterns.
"""

from __future__ import annotations

import fnmatch
import subprocess
from collections.abc import Iterator
from pathlib import Path

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


def changed_files(base: str, root: Path) -> list[Path]:
    """Files added/copied/modified/renamed vs `base` (three-dot = since merge-base).

    Raises subprocess.SubprocessError / OSError if git cannot compute the diff.
    """
    out = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=ACMR", f"{base}...HEAD"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    ).stdout
    return [root / line.strip() for line in out.splitlines() if line.strip()]


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
