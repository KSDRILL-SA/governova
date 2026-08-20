"""Unit tests for the constitution parsers."""

from __future__ import annotations

from governova_compile.markdown import (
    parse_attribute_table,
    parse_labeled_blocks,
    slice_sections,
)
from governova_compile.parsers import (
    parse_blockquote_standards,
    parse_constitution,
    parse_grounded_in,
    parse_references,
    parse_standard,
)
from governova_compile.schema import Phase, Priority

FULL_STANDARD = """\
# C9 — Test Constitution

| Attribute | Value |
|-----------|-------|
| **Document** | C9 — Test |
| **Status** | LOCKED |

### S9.1 — First Standard

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S9.1 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 3 — Product & Intelligence |
| **Depends On**  | `S9.2` (other thing) |
| **Enforced By** | CI · Code Review |

**Standard:**
The system must do the thing.

**Rationale:**
Because otherwise it breaks.

**Anti-Patterns:**
- `AP-S9.1a` — Not doing the thing.
- `AP-S9.1b` — Doing it twice.

**Cross-References:** `S9.2` (reason)

---

### S9.2–S9.4 — Grouped Standards

> **S9.2** — The second standard does another thing referencing S9.1.

> **S9.3** — The third standard.

> **S9.4** — The fourth standard.

---
"""

# A standard carrying provenance. `Grounded In` is the only optional element of the
# block (C0 §3.1), so the parser is exercised against a standard that has it and
# against FULL_STANDARD above, which does not.
GROUNDED_STANDARD = """\
### S9.9 — Standard With Provenance

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S9.9 |
| **Priority**    | High |

**Standard:**
The system must do the grounded thing.

**Rationale:**
Because the canon says so and production agrees.

**Anti-Patterns:**
- `AP-S9.9a` — Not doing the grounded thing.

**Grounded In:**
- Sommerville, *Software Engineering* 10e — ch. 4
- Coronel & Rob, *Database Systems* — ch. 3

---
"""


def test_parse_attribute_table():
    lines = [
        "| Attribute | Value |",
        "|-----------|-------|",
        "| **ID** | S9.1 |",
        "| **Priority** | Critical |",
    ]
    attrs = parse_attribute_table(lines)
    assert attrs["id"] == "S9.1"
    assert attrs["priority"] == "Critical"


def test_parse_labeled_blocks():
    lines = [
        "**Standard:**",
        "Line one.",
        "Line two.",
        "",
        "**Rationale:**",
        "Why it matters.",
    ]
    blocks = parse_labeled_blocks(lines)
    assert "Line one." in blocks["standard"]
    assert blocks["rationale"] == "Why it matters."


def test_parse_references_with_descriptions():
    refs = parse_references("`S9.2` (other thing), `S9.3` (another)")
    assert [r.standard_id for r in refs] == ["S9.2", "S9.3"]
    assert refs[0].description == "other thing"


def test_parse_references_dash_is_empty():
    assert parse_references("—") == []
    assert parse_references("") == []


def test_parse_full_standard():
    sections = slice_sections(FULL_STANDARD, level=3)
    std = parse_standard(sections[0], "C09")
    assert std is not None
    assert std.id == "S9.1"
    assert std.title == "First Standard"
    assert std.priority is Priority.CRITICAL
    assert std.phase is Phase.PRODUCT_INTELLIGENCE
    assert std.statement.startswith("The system must do")
    assert "breaks" in std.rationale
    assert {ap.id for ap in std.anti_patterns} == {"AP-S9.1a", "AP-S9.1b"}
    assert std.depends_on[0].standard_id == "S9.2"
    assert not std.abbreviated


def test_range_heading_is_skipped():
    sections = slice_sections(FULL_STANDARD, level=3)
    # The second section is the range heading S9.2–S9.4 — must not parse as a standard.
    range_section = sections[1]
    assert parse_standard(range_section, "C09") is None


def test_blockquote_standards_extracted():
    abbr = parse_blockquote_standards(
        FULL_STANDARD,
        constitution_id="C09",
        phase=Phase.PRODUCT_INTELLIGENCE,
        phase_label="Phase 3",
        path="x.md",
    )
    ids = {s.id for s in abbr}
    assert ids == {"S9.2", "S9.3", "S9.4"}
    s2 = next(s for s in abbr if s.id == "S9.2")
    assert s2.abbreviated
    # Inline S9.1 reference becomes a cross-reference.
    assert any(r.standard_id == "S9.1" for r in s2.cross_references)


ABBREVIATED_WITH_ANTI_PATTERNS = """\
### S7.21–S7.24 — Additional E2E Standards

> **S7.21** — Playwright tests use `page.getByRole()` — never `page.locator('.css')`.
>
> **Anti-Patterns:**
> - `AP-S7.21a` — CSS class selectors break on every styling refactor.

> **S7.22** — E2E specs run against a seeded database.

> **S7.23** — Flaky specs are quarantined, not retried.
>
> **Anti-Patterns:**
> - `AP-S7.23a` — A retry loop around a flaky spec hides the race it is racing.
> - `AP-S7.23b` — Deleting the assertion rather than the flake.
"""


def _abbreviated(text):
    return {
        s.id: s
        for s in parse_blockquote_standards(
            text,
            constitution_id="C07",
            phase=Phase.QUALITY_RELIABILITY,
            phase_label="Phase 2",
            path="x.md",
        )
    }


def test_abbreviated_standard_carries_a_declared_anti_pattern():
    """The positive case: shorthand used to discard these unconditionally."""
    std = _abbreviated(ABBREVIATED_WITH_ANTI_PATTERNS)["S7.21"]
    assert std.abbreviated
    assert [ap.id for ap in std.anti_patterns] == ["AP-S7.21a"]
    assert std.anti_patterns[0].parent_standard_id == "S7.21"
    assert "styling refactor" in std.anti_patterns[0].description


def test_abbreviated_standard_declaring_none_still_has_none():
    """The negative case, and the one that matters.

    A standard doing exactly what a standard is for — stating a rule and stopping —
    must not acquire anti-patterns from the block that follows it. `S7.22` sits
    between two standards that do declare them, which is the arrangement that
    catches a continuation scan running past its own quote.
    """
    parsed = _abbreviated(ABBREVIATED_WITH_ANTI_PATTERNS)
    assert parsed["S7.22"].anti_patterns == []
    # And the standard after it keeps its own, both of them.
    assert [ap.id for ap in parsed["S7.23"].anti_patterns] == [
        "AP-S7.23a",
        "AP-S7.23b",
    ]


def test_abbreviated_anti_patterns_stop_at_the_next_standard():
    """Two standards in one unbroken quote, only the first declaring."""
    text = (
        "> **S8.18** — Docker images use specific version tags.\n"
        "> **Anti-Patterns:**\n"
        "> - `AP-S8.18a` — `latest` produces non-reproducible builds.\n"
        "> **S8.19** — Images run as a non-root user.\n"
    )
    parsed = _abbreviated(text)
    assert [ap.id for ap in parsed["S8.18"].anti_patterns] == ["AP-S8.18a"]
    assert parsed["S8.19"].anti_patterns == []


def test_parse_grounded_in_reads_one_citation_per_line():
    block = "- Sommerville, *Software Engineering* 10e — ch. 4\n- Coronel & Rob — ch. 3"
    assert parse_grounded_in(block) == [
        "Sommerville, *Software Engineering* 10e — ch. 4",
        "Coronel & Rob — ch. 3",
    ]


def test_parse_grounded_in_drops_blanks_and_duplicates():
    block = "- A source\n\n- A source\n*  Another source  \n"
    assert parse_grounded_in(block) == ["A source", "Another source"]


def test_parse_grounded_in_empty_block_is_empty_list():
    assert parse_grounded_in("") == []
    assert parse_grounded_in("\n\n  \n") == []


def test_parse_grounded_in_does_not_enforce_length():
    # The parser records what was written; `check_grounded_in` is what rejects an
    # excerpt. A parser that silently dropped an over-long entry would hide the
    # exact thing the bound exists to catch.
    long_entry = "x" * 400
    assert parse_grounded_in(f"- {long_entry}") == [long_entry]


def test_parse_standard_captures_grounded_in():
    section = slice_sections(GROUNDED_STANDARD, level=3)[0]
    std = parse_standard(section, "C09")
    assert std is not None
    assert std.grounded_in == [
        "Sommerville, *Software Engineering* 10e — ch. 4",
        "Coronel & Rob, *Database Systems* — ch. 3",
    ]
    # Provenance must not be mistaken for the statement or the rationale.
    assert "Sommerville" not in std.statement
    assert "Sommerville" not in std.rationale


def test_parse_standard_without_grounded_in_is_empty_not_absent():
    # The negative case: the overwhelming majority of the 618 standards carry no
    # provenance, and an unsourced standard is not a malformed one.
    section = slice_sections(FULL_STANDARD, level=3)[0]
    std = parse_standard(section, "C09")
    assert std is not None
    assert std.grounded_in == []


def test_full_constitution_dedupes_and_counts():
    c = parse_constitution(
        FULL_STANDARD,
        constitution_id="C09",
        number=9,
        name="Test",
        phase=Phase.PRODUCT_INTELLIGENCE,
        path="x.md",
        hierarchy_rank=10,
        binds_implementation=False,
    )
    # S9.1 (full) + S9.2, S9.3, S9.4 (blockquote) = 4 standards, no duplicates.
    ids = [s.id for s in c.standards]
    assert ids == ["S9.1", "S9.2", "S9.3", "S9.4"]
