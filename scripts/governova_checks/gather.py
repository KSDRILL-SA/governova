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
#
# The generated-output entries are load-bearing, not housekeeping. Coverage
# reporters embed the *source under test* line by line inside markup, so a
# report directory is a second copy of the repository that no rule should read:
# scanning `htmlcov/` reproduces findings against code nobody wrote at that path
# and nobody can fix there, and it reproduces them only *partly*, because markup
# splits some tokens and not others. A blocking finding whose file cannot be
# edited is the fastest way to teach an adopter to switch the gate off.
#
# This mattered less while the surface was source extensions only. It became
# load-bearing the moment `.html` was added, which is why both changes are in
# one commit rather than the extension arriving first.
SKIP_DIRS: frozenset[str] = frozenset(
    {
        # Version control, environments, caches.
        ".git", ".venv", "venv", "node_modules", "__pycache__", "compiled",
        ".pytest_cache", ".mypy_cache", ".ruff_cache", ".tox", ".nox",
        ".gradle", ".terraform", "vendor",
        # Build output.
        "dist", "build", "out", "target", "bin", "obj",
        ".next", ".nuxt", ".svelte-kit", ".angular", ".astro", ".output",
        # Generated reports — these embed source.
        "htmlcov", "coverage", "playwright-report", "test-results",
        "allure-results", "storybook-static", "site", "_site",
    }
)

# Files that are generated or vendored rather than written. Matched on the file
# name, because the giveaway is the name: a bundle sits beside its source and
# inherits its directory, so a directory list cannot reach it.
GENERATED_SUFFIXES: tuple[str, ...] = (
    ".min.js", ".min.css", ".bundle.js", ".chunk.js",
    ".generated.ts", ".generated.js", ".g.dart", "_pb2.py", ".pb.go",
)

# Path globs skipped by default: test code, fixtures, and the rule set itself.
#
# The directory list covers the conventions in common use, not just the one this
# repository happens to follow. It originally knew `tests/` and nothing else,
# which was invisible for as long as the engine only ever scanned its own source
# tree — Governova keeps its tests in `scripts/tests/`.
#
# The first run of `governova onboard` against a third-party repository found it
# immediately: 20 of express's 21 blocking findings were error-handling fixtures
# in `test/`, singular, which is the dominant convention across Node, Go and Ruby.
# Every one was code written deliberately to exercise the behaviour the rule
# looks for. That is precisely what this list exists to skip, so the gap was in
# the list rather than in the rules, and a governance tool whose first report
# about a healthy repository is twenty false accusations does not get a second
# reading.
#
# `fnmatch`'s `*` spans `/`, so the bare form anchors a top-level directory and
# the `*/`-prefixed form matches it at any depth.
DEFAULT_IGNORES: tuple[str, ...] = (
    "*/tests/*",
    "tests/*",
    "*/test/*",
    "test/*",
    "*/__tests__/*",
    "__tests__/*",
    "*/spec/*",
    "spec/*",
    "*/specs/*",
    "specs/*",
    "*/test_*",
    "test_*",
    "*_test.*",
    # The JavaScript and TypeScript filename convention, and the one the
    # constitution itself mandates. `S1.69`: *"Unit test files are co-located
    # with the source file they test, named `{source-file}.test.ts` or
    # `{source-file}.spec.ts`."*
    #
    # These were missing while `test_*` (Python) and `*_test.*` (Go) were here,
    # so a repository following `S1.69` was scanned against every rule its own
    # tests deliberately exercise. Measured before the fix: a co-located
    # `auth.test.ts` asserting that a token in `localStorage` is rejected was
    # reported as `AP-S3.14a` — the violation the test exists to prevent.
    #
    # That is the express failure a second time. The note above records the
    # first: 20 of 21 blocking findings were fixtures in `test/`. The fix that
    # followed added the directory conventions and two of the three filename
    # ones, and nothing checked whether the set was complete —
    # `test_every_test_convention_is_skipped` checks it now.
    #
    # `*.test.*` and `*.spec.*` need the dots, so `latest.ts` and `spectrum.ts`
    # are untouched. A source file genuinely named `openapi.spec.ts` would be
    # skipped, which is the one real cost here and much the cheaper error: a
    # missed finding in one unusually-named file, against a false accusation in
    # every test file of every repository that follows the convention.
    "*.test.*",
    "*.spec.*",
    "scripts/governova_checks/rules.py",
)


def is_ignored(rel: str, ignores: tuple[str, ...]) -> bool:
    """Whether a repo-relative posix path matches any ignore glob."""
    return any(fnmatch.fnmatch(rel, pat) for pat in ignores)


def is_generated(name: str) -> bool:
    """Whether a file name marks output rather than something someone wrote.

    Name-based on purpose: a bundle sits in the same directory as its source and
    inherits it, so `SKIP_DIRS` cannot reach it. Reporting a violation inside a
    minified bundle is reporting it against a file the author cannot edit.
    """
    lowered = name.lower()
    return any(lowered.endswith(suffix) for suffix in GENERATED_SUFFIXES)


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
        if is_generated(path.name):
            continue
        rel = path.relative_to(root).as_posix()
        if is_ignored(rel, ignores):
            continue
        yield path
