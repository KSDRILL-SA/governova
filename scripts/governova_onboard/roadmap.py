"""governova_onboard.roadmap — what to fix first, and why that order.

A baseline says what is wrong. **A roadmap says what to do first, and that
ordering is the product.** Anyone can sort findings by standard number; the
ordering that earns a second run is the one that puts the cheapest high-impact
fix at the top and can defend the choice.

This mechanises `protocols/brownfield-adoption.md` Phase 2 — risk-ranked
remediation — and its output is issue-shaped: one item is one PR, individually
green, individually revertible (`S8.83`).

## How the ordering is built, and what is measured versus chosen

Two quantities, both assembled from facts already in the repository or the
compiled index. Nothing here re-derives a finding.

**Blast radius** — what it costs to leave this alone:

| Component | Where it comes from |
|---|---|
| blocking | the rule's confidence — a blocking finding fails a build |
| priority | the standard's own `priority` in the corpus |
| reach | how many distinct files carry the finding |
| dependents | how many other standards declare `depends_on` this one |

**Effort** — what it costs to fix:

| Component | Where it comes from |
|---|---|
| files to touch | distinct files carrying the finding |
| protection | whether a conventionally-named test file exists for those files |

`reach` appears in both, and that is deliberate rather than double-counting: a
violation spread across forty files genuinely *is* both higher-impact and
higher-effort, and collapsing that into one number would hide the tension the
reader needs to see.

**The component values are measured. The weights are a stated convention.**
That distinction is load-bearing and is why every component is carried on the
item rather than folded into a score — picking a curve is picking a number, and a
ranking nobody can audit is a ranking nobody should trust. Dispute the order by
reading the components; do not reverse-engineer it from the total.

## What it refuses to conclude

**A file with no conventionally-named test is `UNKNOWN`, never "untested".**
Filenames cannot prove absence of coverage — the tests may live anywhere, or be
integration tests, or exercise the module through another entry point. `S1.101`
requires characterisation tests before a brownfield refactor, so "we cannot show
this is protected" is a real reason to sequence an item behind writing one. It
is not a reason to claim the code is bare.

**An empty repository produces an empty roadmap.** A tool that manufactures
work to look busy on a clean codebase has told its first lie about that
codebase.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from governova_compile.schema import CompiledIndex, Priority

from governova_onboard.baseline import Baseline, FindingGroup

# Blast-radius weight per standard priority. A stated convention, not a
# measurement — see the module docstring. Ordered and spaced so that priority
# cannot be outvoted by file count alone on small repositories, which is the
# behaviour a reader expects when a Critical standard is involved.
PRIORITY_WEIGHT: dict[Priority, int] = {
    Priority.CRITICAL: 8,
    Priority.HIGH: 4,
    Priority.STANDARD: 2,
    Priority.GUIDANCE: 1,
}

# A blocking finding fails a build. That is not a weighting opinion — it is what
# blocking means — so it is applied as a separate ordering tier *and* scored.
BLOCKING_WEIGHT = 8

# Added to effort when no conventionally-named test could be found for any file
# the item touches. Refactoring behaviour you cannot pin is the risk `S1.101`
# exists to name, so it makes an item more expensive, never less important.
UNPROTECTED_EFFORT = 3

# Test-file naming conventions, by the extension of the file under test. Keyed on
# the source suffix; `{stem}` is substituted. Deliberately conventional-only:
# these are the forms a reader would also look for by hand.
_TEST_NAME_PATTERNS: dict[str, tuple[str, ...]] = {
    ".py": ("test_{stem}.py", "{stem}_test.py"),
    ".go": ("{stem}_test.go",),
    ".rb": ("{stem}_spec.rb", "{stem}_test.rb"),
    ".java": ("{stem}Test.java", "{stem}Tests.java"),
    ".cs": ("{stem}Tests.cs", "{stem}Test.cs"),
    ".js": ("{stem}.test.js", "{stem}.spec.js", "{stem}_test.js"),
    ".jsx": ("{stem}.test.jsx", "{stem}.spec.jsx"),
    ".ts": ("{stem}.test.ts", "{stem}.spec.ts"),
    ".tsx": ("{stem}.test.tsx", "{stem}.spec.tsx"),
}


class Protection(StrEnum):
    """Whether a characterisation test can be shown to exist (`S1.101`).

    There is no `UNPROTECTED` member, and its absence is the point. A filename
    search can prove a test exists; it cannot prove one does not.
    """

    PROTECTED = "protected"
    UNKNOWN = "unknown"


class Kind(StrEnum):
    """What sort of change an item is, because they are not fixed the same way."""

    CODE = "code"
    """A line in a source file matched a rule. Fixed by editing code."""

    STRUCTURAL = "structural"
    """A repository-level fact — a missing CI step, an absent lockfile gate.
    Usually the cheapest item on the roadmap and often the highest-leverage,
    because it changes no runtime behaviour at all."""


@dataclass(frozen=True)
class Item:
    """One roadmap entry — one PR, individually green, individually revertible."""

    kind: Kind
    standard: str
    title: str
    anti_pattern: str
    summary: str
    occurrences: int
    files: tuple[str, ...]
    protection: Protection
    protected_by: tuple[str, ...]
    blocking: bool
    priority: Priority
    dependents: int

    @property
    def reach(self) -> int:
        """Distinct files carrying the finding."""
        return len(self.files)

    @property
    def blast(self) -> int:
        return (
            PRIORITY_WEIGHT.get(self.priority, 1)
            + (BLOCKING_WEIGHT if self.blocking else 0)
            + self.reach
            + self.dependents
        )

    @property
    def effort(self) -> int:
        """Never below 1 — every item costs at least one file's worth of work."""
        penalty = UNPROTECTED_EFFORT if self.protection is Protection.UNKNOWN else 0
        return max(1, self.reach + penalty)

    @property
    def leverage(self) -> float:
        """Impact per unit of work. The number the ordering is built on."""
        return round(self.blast / self.effort, 2)

    @property
    def needs_characterisation_test(self) -> bool:
        """Whether `S1.101` requires a test to be written before this is touched.

        Structural items never do: adding a licence gate to CI changes no
        runtime behaviour, so there is no behaviour to pin first.
        """
        return self.kind is Kind.CODE and self.protection is Protection.UNKNOWN


@dataclass(frozen=True)
class Roadmap:
    """The ordered plan. Empty is a valid and common result."""

    items: tuple[Item, ...]

    @property
    def blocking_items(self) -> tuple[Item, ...]:
        return tuple(i for i in self.items if i.blocking)

    @property
    def needing_tests(self) -> tuple[Item, ...]:
        return tuple(i for i in self.items if i.needs_characterisation_test)

    def __len__(self) -> int:
        return len(self.items)

    def __bool__(self) -> bool:
        return bool(self.items)


def _dependents(index: CompiledIndex) -> dict[str, int]:
    """How many standards declare `depends_on` each standard.

    A standard several others rest on has wider reach when it is broken, and
    this is recorded in the corpus rather than guessed at.
    """
    counts: dict[str, int] = {}
    for constitution in index.constitutions:
        for standard in constitution.standards:
            for reference in standard.depends_on:
                counts[reference.standard_id] = counts.get(reference.standard_id, 0) + 1
    return counts


def _standards(index: CompiledIndex) -> dict[str, object]:
    return {s.id: s for c in index.constitutions for s in c.standards}


def find_characterisation_tests(root: Path, relative_files: tuple[str, ...]) -> tuple[str, ...]:
    """Conventionally-named test files for the given source files.

    Searches the whole repository rather than a sibling directory, because
    `src/foo.py` is as likely to be tested from `tests/test_foo.py` as from
    beside itself. Returns what was found; finding nothing means `UNKNOWN`, not
    "untested" — see `Protection`.
    """
    wanted: dict[str, None] = {}
    for relative in relative_files:
        path = Path(relative)
        patterns = _TEST_NAME_PATTERNS.get(path.suffix.lower())
        if not patterns:
            continue
        for pattern in patterns:
            wanted.setdefault(pattern.format(stem=path.stem), None)
    if not wanted:
        return ()

    found: list[str] = []
    for candidate in root.rglob("*"):
        if candidate.name in wanted and candidate.is_file():
            try:
                found.append(candidate.relative_to(root).as_posix())
            except ValueError:  # pragma: no cover — rglob stays under root
                continue
    return tuple(sorted(found))


def _code_item(
    root: Path, group: FindingGroup, standard: object, dependents: dict[str, int]
) -> Item:
    tests = find_characterisation_tests(root, group.files)
    return Item(
        kind=Kind.CODE,
        standard=group.standard,
        title=getattr(standard, "title", "") or group.standard,
        anti_pattern=group.anti_pattern,
        summary=group.message,
        occurrences=group.count,
        files=group.files,
        protection=Protection.PROTECTED if tests else Protection.UNKNOWN,
        protected_by=tests,
        blocking=group.blocking,
        priority=getattr(standard, "priority", Priority.STANDARD),
        dependents=dependents.get(group.standard, 0),
    )


def build(baseline: Baseline, index: CompiledIndex) -> Roadmap:
    """Order a baseline's findings into a remediation plan.

    Items are ordered blocking-first, then by leverage — impact per unit of
    work. Blocking is a separate tier rather than a large weight because a
    build-failing finding outranking an advisory one is not an opinion about
    relative importance; it is what blocking means.
    """
    standards = _standards(index)
    dependents = _dependents(index)

    items: list[Item] = [
        _code_item(baseline.root, group, standards.get(group.standard), dependents)
        for group in baseline.groups
    ]

    for probe in baseline.violated_probes:
        standard = standards.get(probe.standard)
        items.append(
            Item(
                kind=Kind.STRUCTURAL,
                standard=probe.standard,
                title=getattr(standard, "title", "") or probe.standard,
                anti_pattern="—",
                summary=probe.evidence,
                occurrences=1,
                files=(),
                # A repository fact changes no runtime behaviour, so there is no
                # behaviour to pin before changing it. Reporting UNKNOWN here
                # would demand a characterisation test for adding a CI step.
                protection=Protection.PROTECTED,
                protected_by=(),
                blocking=False,
                priority=getattr(standard, "priority", Priority.STANDARD),
                dependents=dependents.get(probe.standard, 0),
            )
        )

    items.sort(key=lambda i: (not i.blocking, -i.leverage, -i.blast, i.standard))
    return Roadmap(items=tuple(items))


__all__ = [
    "BLOCKING_WEIGHT",
    "PRIORITY_WEIGHT",
    "UNPROTECTED_EFFORT",
    "Item",
    "Kind",
    "Protection",
    "Roadmap",
    "build",
    "find_characterisation_tests",
]
