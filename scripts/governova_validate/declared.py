"""Declared-but-uncompiled anti-pattern check.

An anti-pattern reaches the compiled index exactly one way: `parse_anti_patterns`
reads the `**Anti-Patterns:**` block inside a standard's own section and binds each
entry to that standard. Two *other* places in the repository also list anti-patterns
— the summary table at the foot of each constitution, and
`constitution/indexes/anti-patterns-index.md`. Neither is parsed. Both are read by
humans as if they were authoritative.

When a standard is written in the compact blockquote form used under a range heading
— `### S7.33–S7.38 — Additional Python Testing Standards` — it carries no field
structure and therefore no `**Anti-Patterns:**` block. Its anti-patterns exist in the
summary table and nowhere the compiler can see. The standard still compiles; only its
anti-patterns are dropped, silently, and its `anti_patterns` list comes out empty
beside a neighbour in the same table that has one.

Eleven had accumulated that way before anything looked, six of them Critical. A rule
cannot cite an anti-pattern the compiled index does not contain, so not one of them
could ever be enforced, while the summary table went on saying the repository
governs it. Declared law that fails to compile is worse than absent law.

This check does not decide which source wins. It reports that they disagree.
"""

from __future__ import annotations

import re
from pathlib import Path

from governova_compile.schema import CompiledIndex, IntegrityIssue, Severity

# A table row whose first cell is an anti-pattern ID, with or without backticks.
# Anchored at the row start so an ID mentioned in prose or inside a fenced example
# is never mistaken for a declaration.
_TABLE_ROW = re.compile(r"^\|\s*`?(AP-S\d+\.\d+[a-z])`?\s*\|")

_SKIP_DIRS = frozenset({".git", ".venv", "node_modules", "compiled", "dist", "build"})


def _declared_in_sources(constitution_root: Path) -> dict[str, tuple[str, int]]:
    """Every anti-pattern ID declared in a markdown table, to where it was declared.

    First declaration wins, so the reported location is the one a reader would
    most likely have reached for.
    """
    declared: dict[str, tuple[str, int]] = {}
    for path in sorted(constitution_root.rglob("*.md")):
        if any(part in _SKIP_DIRS for part in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        in_fence = False
        for lineno, line in enumerate(text.splitlines(), start=1):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            # A constitution teaching what a table looks like is not declaring one.
            if in_fence:
                continue
            match = _TABLE_ROW.match(line)
            if match and match.group(1) not in declared:
                declared[match.group(1)] = (str(path).replace("\\", "/"), lineno)
    return declared


def _compiled_anti_patterns(index: CompiledIndex) -> set[str]:
    return {
        ap.id
        for constitution in (*index.constitutions, *index.domains)
        for std in constitution.standards
        for ap in std.anti_patterns
    }


def check_declared_anti_patterns(
    repo_root: Path, index: CompiledIndex
) -> list[IntegrityIssue]:
    """Report anti-patterns a markdown table declares and the compiled index lacks.

    Deliberately SEV3. The remedy is to give each orphan an `**Anti-Patterns:**`
    block in its constitution body, which amends the constitution and is an L4 act.
    A blocking check would fail every build on a condition the engine has no
    authority to fix. **Promote this to SEV2 once the outstanding orphans have
    homes** — at that point recurrence is a regression, not a backlog.

    The reverse direction is not checked. `anti-patterns-index.md` lists 110 of the
    498 compiled anti-patterns, so it is a partial digest rather than a mirror, and
    reporting the other 388 would bury this finding in noise. That the index
    document is not a mirror is a documentation gap, not an integrity failure.
    """
    constitution_root = repo_root / "constitution"
    if not constitution_root.is_dir():
        return []

    compiled = _compiled_anti_patterns(index)
    issues: list[IntegrityIssue] = []
    for ap_id, (source_path, source_line) in sorted(
        _declared_in_sources(constitution_root).items()
    ):
        if ap_id in compiled:
            continue
        implied = ap_id[len("AP-") :].rstrip("abcdefghijklmnopqrstuvwxyz")
        issues.append(
            # SEV2, promoted from SEV3 once the outstanding list reached zero.
            #
            # While eleven orphans stood, this reported a *backlog* — a known debt
            # being worked down, which is SEV3's job. With none outstanding, a new
            # one is a **regression**: law was declared in a summary table and
            # silently failed to compile, between one commit and the next. That is
            # the failure mode the check was written for, and it deserves the
            # severity that says so.
            IntegrityIssue(
                severity=Severity.SEV2,
                code="declared-anti-pattern-uncompiled",
                message=(
                    f"{ap_id} is declared in a markdown table but is absent from the "
                    f"compiled index, so no rule can cite it and nothing enforces it. "
                    f"Give {implied} an **Anti-Patterns:** block in its constitution body."
                ),
                source_path=source_path,
                source_line=source_line,
            )
        )
    return issues
