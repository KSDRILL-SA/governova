"""The System Bible model — master.md §18.4.

Per-file documentation of the whole codebase: what each file is for, what it exposes,
and what it depends on. Turns AI-generated code from a black box into something a
maintainer can navigate.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class FileEntry:
    """Documentation for one source file."""

    path: str  # repo-relative, posix
    language: str
    loc: int
    purpose: str  # "" when none could be extracted
    public: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)

    @property
    def area(self) -> str:
        """Top-level area (first path segment)."""
        return self.path.split("/", 1)[0] if "/" in self.path else "(root)"

    @property
    def documented(self) -> bool:
        return bool(self.purpose.strip())


@dataclass(frozen=True)
class SystemBible:
    entries: list[FileEntry]

    @property
    def total_files(self) -> int:
        return len(self.entries)

    @property
    def total_loc(self) -> int:
        return sum(e.loc for e in self.entries)

    @property
    def documented_files(self) -> int:
        return sum(1 for e in self.entries if e.documented)

    @property
    def documented_pct(self) -> float:
        return round(100 * self.documented_files / self.total_files, 1) if self.entries else 0.0

    def by_area(self) -> dict[str, list[FileEntry]]:
        areas: dict[str, list[FileEntry]] = {}
        for e in sorted(self.entries, key=lambda x: x.path):
            areas.setdefault(e.area, []).append(e)
        return areas
