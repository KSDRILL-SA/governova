"""Markdown tokenisation and section-slicing helpers.

We use markdown-it-py to build a token stream, then use heading token line maps
to slice the source into well-defined sections. Field extraction within a
section operates on the original source lines for that section only — this is
AST-guided extraction, not regex-on-the-whole-document.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from markdown_it import MarkdownIt
from markdown_it.token import Token

_md = MarkdownIt("commonmark").enable("table")


@dataclass(frozen=True)
class Heading:
    """A markdown heading with its level, text, and source line range."""

    level: int
    text: str
    line_start: int  # 0-indexed line where the heading appears
    line_end: int  # 0-indexed line just past the heading line


@dataclass
class Section:
    """A slice of a document beginning at a heading and ending before the next
    heading of the same or higher level."""

    heading: Heading
    line_start: int  # 0-indexed, inclusive (the heading line)
    line_end: int  # 0-indexed, exclusive
    lines: list[str] = field(default_factory=list)

    @property
    def body_lines(self) -> list[str]:
        """Section lines excluding the heading line itself."""
        return self.lines[1:]


def tokenize(text: str) -> list[Token]:
    """Return the markdown-it token stream for a document."""
    return _md.parse(text)


def extract_headings(text: str) -> list[Heading]:
    """Extract all ATX headings with their source line ranges, via the token map."""
    tokens = tokenize(text)
    headings: list[Heading] = []
    for i, tok in enumerate(tokens):
        if tok.type == "heading_open" and tok.map is not None:
            level = int(tok.tag[1:])  # 'h3' -> 3
            inline = tokens[i + 1] if i + 1 < len(tokens) else None
            content = inline.content.strip() if inline is not None else ""
            headings.append(
                Heading(
                    level=level,
                    text=content,
                    line_start=tok.map[0],
                    line_end=tok.map[1],
                )
            )
    return headings


def slice_sections(text: str, *, level: int) -> list[Section]:
    """Slice a document into sections rooted at headings of exactly `level`.

    A section runs from its heading line to the line before the next heading of
    the same or higher level (lower or equal numeric level).
    """
    lines = text.splitlines()
    headings = extract_headings(text)
    sections: list[Section] = []

    target = [h for h in headings if h.level == level]
    for h in target:
        # Find the next heading at the same or higher authority (<= level).
        end = len(lines)
        for other in headings:
            if other.line_start > h.line_start and other.level <= level:
                end = other.line_start
                break
        sections.append(
            Section(
                heading=h,
                line_start=h.line_start,
                line_end=end,
                lines=lines[h.line_start : end],
            )
        )
    return sections


# ─── Table parsing ───────────────────────────────────────────────────────────

_TABLE_ROW = re.compile(r"^\s*\|(.+)\|\s*$")
_TABLE_SEP = re.compile(r"^\s*\|[\s:|-]+\|\s*$")


def parse_pipe_table(lines: list[str]) -> list[dict[str, str]]:
    """Parse the first GitHub-style pipe table found in `lines`.

    Returns a list of row dicts keyed by the (stripped) header cells.
    Returns an empty list if no table is found.
    """
    rows: list[list[str]] = []
    in_table = False
    for line in lines:
        if _TABLE_SEP.match(line):
            in_table = True
            continue
        m = _TABLE_ROW.match(line)
        if m:
            cells = [c.strip() for c in m.group(1).split("|")]
            rows.append(cells)
        elif in_table:
            break  # table ended

    if not rows:
        return []

    header, *body = rows
    # The header is the row immediately before the separator; with our loop the
    # header is the first collected row and body rows follow the separator.
    header = [h.strip("* ").strip() for h in header]
    result: list[dict[str, str]] = []
    for row in body:
        if len(row) != len(header):
            continue
        result.append(dict(zip(header, row, strict=False)))
    return result


def parse_attribute_table(lines: list[str]) -> dict[str, str]:
    """Parse a two-column attribute table (`| **Key** | Value |`) into a dict.

    Keys are normalised: bold markers stripped, lowercased, spaces → underscores.
    """
    attrs: dict[str, str] = {}
    for line in lines:
        if _TABLE_SEP.match(line):
            continue
        m = _TABLE_ROW.match(line)
        if not m:
            continue
        cells = [c.strip() for c in m.group(1).split("|")]
        if len(cells) != 2:
            continue
        key_raw = cells[0].strip("* ").strip()
        if key_raw.lower() in ("attribute", "field"):
            continue  # header row
        key = key_raw.lower().replace(" ", "_")
        attrs[key] = cells[1].strip()
    return attrs


# ─── Bold-prefixed prose blocks ──────────────────────────────────────────────

_BOLD_LABEL = re.compile(r"^\*\*(?P<label>[A-Za-z][A-Za-z \-]*?):?\*\*\s*(?P<inline>.*)$")


def parse_labeled_blocks(lines: list[str]) -> dict[str, str]:
    """Parse `**Label:**` prefixed prose blocks into a dict of label → text.

    A block starts at a `**Label:**` line and runs until the next label, a
    horizontal rule, or end of section. Inline text on the label line is kept.
    Keys are normalised: lowercased, spaces → underscores.
    """
    blocks: dict[str, list[str]] = {}
    current: str | None = None
    for line in lines:
        stripped = line.strip()
        if stripped in ("---", "***", "___"):
            current = None
            continue
        m = _BOLD_LABEL.match(stripped)
        if m:
            label = m.group("label").strip().lower().replace(" ", "_")
            current = label
            blocks[current] = []
            inline = m.group("inline").strip()
            if inline:
                blocks[current].append(inline)
            continue
        if current is not None:
            blocks[current].append(line.rstrip())

    return {k: "\n".join(v).strip() for k, v in blocks.items()}
