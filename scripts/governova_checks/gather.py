"""Shared source-file selection: which files a surface should scan.

One definition of "scannable source", used by both the enforcer (changed files)
and the Governova Score (whole repo). Test code, fixtures, vendored deps, and the
rule set itself are skipped — they legitimately contain violation patterns.
"""

from __future__ import annotations

import fnmatch
import re
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


# A git revision: SHA, branch, tag, or `origin/main`-style remote ref. Deliberately
# strict — see `changed_files` for why anything looser is dangerous.
_SAFE_REV = re.compile(r"\A[A-Za-z0-9][A-Za-z0-9._/@^~-]{0,254}\Z")


def _validate_rev(base: str) -> str:
    """Reject a revision that git could read as an option.

    `git diff … "{base}...HEAD"` interpolates caller input into an argument
    vector. There is no shell, so there is no shell injection — but git parses
    leading-dash arguments as options, and `--output=<path>` writes a file. A
    `base` of `--output=/path/to/anything` therefore writes an attacker-chosen
    file, which is a real capability inside CI.

    The value reaches us from a workflow input; a consumer wiring it from a
    branch name or a `pull_request_target` payload hands that capability to
    whoever opens a pull request. So it is validated here, at the boundary,
    rather than trusted because the default happens to be safe.
    """
    if not _SAFE_REV.match(base):
        raise ValueError(
            f"refusing to use {base!r} as a git revision — expected a SHA, branch, "
            f"tag, or remote ref, and a value that git could parse as an option is "
            f"never one of those."
        )
    return base


def changed_files(base: str, root: Path) -> list[Path]:
    """Files added/copied/modified/renamed vs `base` (three-dot = since merge-base).

    Raises ValueError for a revision git could misread as an option, and
    subprocess.SubprocessError / OSError if git cannot compute the diff.
    """
    rev = _validate_rev(base)
    out = subprocess.run(
        # `--` terminates option parsing; nothing after it is read as a flag.
        ["git", "diff", "--name-only", "--diff-filter=ACMR", f"{rev}...HEAD", "--"],
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
