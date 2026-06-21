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
