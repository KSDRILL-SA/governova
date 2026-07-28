"""Extractors that turn markdown sections into typed schema objects."""

from __future__ import annotations

import re
from datetime import date

from governova_compile.markdown import (
    _TABLE_ROW,
    _TABLE_SEP,
    Section,
    parse_attribute_table,
    parse_labeled_blocks,
    slice_sections,
)
from governova_compile.schema import (
    AntiPattern,
    Constitution,
    ConstitutionId,
    DocumentHeader,
    DocumentStatus,
    Phase,
    Priority,
    Reference,
    Standard,
)

# ─── Regexes ─────────────────────────────────────────────────────────────────

STANDARD_HEADING = re.compile(r"^S(?P<c>\d+)\.(?P<n>\d+)\s*[-—–]\s*(?P<title>.+)$")
# Layer 4 domain standard heading: `### D-FINTECH.1 — Monetary values are exact`.
DOMAIN_STANDARD_HEADING = re.compile(
    r"^(?P<id>D-[A-Z][A-Z0-9-]*\.\d+)\s*[-—–]\s*(?P<title>.+)$"
)
DOMAIN_ANTI_PATTERN_LINE = re.compile(
    r"`?(?P<id>AP-D-[A-Z][A-Z0-9-]*\.\d+[a-z])`?\s*[-—–]\s*(?P<desc>.+)$"
)
# A range/group heading like `S8.4–S8.8 — Additional Platform Standards`. These
# are section headers for grouped standards; the individuals live in blockquotes.
RANGE_HEADING = re.compile(r"^S\d+\.\d+\s*[-—–]\s*S\d+\.\d+")
_ATTR_KEYS = {"id", "priority", "applies_to", "phase", "depends_on", "enforced_by"}
STANDARD_ID = re.compile(r"\bS\d+\.\d+\b")
ANTI_PATTERN_ID = re.compile(r"\bAP-S\d+\.\d+[a-z]\b")
# Blockquote shorthand: `> **S8.4** — Preview deployments are generated ...`
BLOCKQUOTE_STANDARD = re.compile(r"^>\s*\*\*(?P<id>S\d+\.\d+)\*\*\s*[-—–]\s*(?P<text>.+)$")
ANTI_PATTERN_LINE = re.compile(r"`?(?P<id>AP-S\d+\.\d+[a-z])`?\s*[-—–]\s*(?P<desc>.+)$")
REFERENCE_WITH_DESC = re.compile(r"`?(?P<id>S\d+\.\d+)`?\s*(?:\((?P<desc>[^)]*)\))?")
PHASE_LABEL = re.compile(r"Phase\s+(?P<num>\d+)", re.IGNORECASE)
ENFORCED_SPLIT = re.compile(r"\s*[·•,]\s*")


def _padded_constitution_id(c: int) -> ConstitutionId:
    return f"C{c:02d}"


def parse_priority(raw: str) -> Priority | None:
    """Map a raw priority cell to the Priority enum, tolerant of extra text."""
    token = raw.strip().split()[0].strip("*").strip() if raw.strip() else ""
    for p in Priority:
        if token.lower() == p.value.lower():
            return p
    return None


def parse_phase(label: str | None) -> tuple[Phase | None, str | None]:
    """Extract the Phase enum and keep the original label string."""
    if not label or label.strip() in ("—", "-", ""):
        return None, None
    m = PHASE_LABEL.search(label)
    if not m:
        return None, label.strip()
    num = m.group("num")
    try:
        return Phase(num), label.strip()
    except ValueError:
        return None, label.strip()


def parse_references(raw: str) -> list[Reference]:
    """Parse a `Depends On` / `Cross-References` cell into Reference objects.

    Handles: '—', '`S1.27` (reason), `S2.7` (other reason)'.
    """
    if not raw or raw.strip() in ("—", "-", "None", "n/a", "N/A"):
        return []
    refs: list[Reference] = []
    seen: set[str] = set()
    # Split on commas that separate distinct references, but reasons may contain
    # commas — so we anchor on the standard-id token instead.
    for m in re.finditer(r"`?(S\d+\.\d+)`?\s*(?:\(([^)]*)\))?", raw):
        sid = m.group(1)
        if sid in seen:
            continue
        seen.add(sid)
        desc = m.group(2).strip() if m.group(2) else None
        refs.append(Reference(standard_id=sid, description=desc))
    return refs


def parse_enforced_by(raw: str) -> list[str]:
    if not raw or raw.strip() in ("—", "-", ""):
        return []
    parts = [p.strip() for p in ENFORCED_SPLIT.split(raw) if p.strip()]
    # Strip trailing parenthetical standard hints like 'gate (S1.27)' → keep text.
    return [p for p in parts if p and p not in ("—", "-")]


def parse_anti_patterns(raw_block: str, parent_id: str) -> list[AntiPattern]:
    """Parse the `**Anti-Patterns:**` block into AntiPattern objects."""
    results: list[AntiPattern] = []
    for line in raw_block.splitlines():
        stripped = line.strip().lstrip("-* ").strip()
        m = ANTI_PATTERN_LINE.search(stripped)
        if m:
            results.append(
                AntiPattern(
                    id=m.group("id"),
                    description=m.group("desc").strip(),
                    parent_standard_id=parent_id,
                )
            )
    return results


def _fallback_statement(body_lines: list[str]) -> str:
    """Capture section content when there is no `**Standard:**` labeled block.

    Removes the leading attribute table (2-column, known keys) and keeps the
    remaining prose, code blocks, and data tables verbatim. Used for standards
    whose content is expressed as prose, a checklist, or a data table.
    """
    lines = list(body_lines)
    start = end = None
    for i, line in enumerate(lines):
        if _TABLE_ROW.match(line) or _TABLE_SEP.match(line):
            if start is None:
                start = i
            end = i
        elif start is not None:
            break
    if start is not None and end is not None:
        attrs = parse_attribute_table(lines[start : end + 1])
        if any(k in attrs for k in _ATTR_KEYS):
            del lines[start : end + 1]
    return "\n".join(line.rstrip() for line in lines).strip()


def parse_standard(section: Section, constitution_id: ConstitutionId) -> Standard | None:
    """Parse one `### S{C}.{N} — Title` section into a Standard, or None if the
    heading is not a single-standard heading (no match, or a range/group header)."""
    if RANGE_HEADING.match(section.heading.text):
        return None  # group header — individuals are captured from blockquotes
    m = STANDARD_HEADING.match(section.heading.text)
    if not m:
        return None

    sid = f"S{int(m.group('c'))}.{int(m.group('n'))}"
    title = m.group("title").strip()

    attrs = parse_attribute_table(section.body_lines)
    blocks = parse_labeled_blocks(section.body_lines)

    priority = parse_priority(attrs.get("priority", "")) or Priority.STANDARD
    applies_to = attrs.get("applies_to", "").strip() or "Both Stacks"
    phase, phase_label = parse_phase(attrs.get("phase"))
    depends_on = parse_references(attrs.get("depends_on", ""))
    enforced_by = parse_enforced_by(attrs.get("enforced_by", ""))

    statement = blocks.get("standard", "").strip()
    if not statement:
        statement = _fallback_statement(section.body_lines)
    rationale = blocks.get("rationale", "").strip()
    anti_patterns = parse_anti_patterns(
        blocks.get("anti-patterns", "") or blocks.get("anti_patterns", ""), sid
    )
    cross_references = parse_references(
        blocks.get("cross-references", "") or blocks.get("cross_references", "")
    )

    return Standard(
        id=sid,
        title=title,
        constitution_id=constitution_id,
        priority=priority,
        applies_to=applies_to,
        phase=phase,
        phase_label=phase_label,
        depends_on=depends_on,
        enforced_by=enforced_by,
        statement=statement,
        rationale=rationale,
        anti_patterns=anti_patterns,
        cross_references=cross_references,
        source_path="",  # filled by caller
        source_line=section.line_start + 1,  # 1-indexed
    )


def parse_domain_anti_patterns(raw_block: str, parent_id: str) -> list[AntiPattern]:
    """Parse a domain standard's `**Anti-Patterns:**` block (`AP-D-{DOMAIN}.{N}{x}`)."""
    results: list[AntiPattern] = []
    for line in raw_block.splitlines():
        stripped = line.strip().lstrip("-* ").strip()
        m = DOMAIN_ANTI_PATTERN_LINE.search(stripped)
        if m:
            results.append(
                AntiPattern(
                    id=m.group("id"),
                    description=m.group("desc").strip(),
                    parent_standard_id=parent_id,
                )
            )
    return results


def parse_domain_standard(section: Section, domain_id: str) -> Standard | None:
    """Parse one `### D-{DOMAIN}.{N} — Title` section into a Standard.

    Domain standards use the same block shape as core standards (attribute table
    plus `**Standard:**` / `**Rationale:**` / `**Anti-Patterns:**` labelled blocks)
    so one format specification covers Layer 2 and Layer 4. The domain-specific
    part is `**Extends:**` — the core standards this domain standard builds on,
    captured as `depends_on` so the reference graph spans both layers.
    """
    m = DOMAIN_STANDARD_HEADING.match(section.heading.text)
    if not m:
        return None

    sid = m.group("id")
    if not sid.startswith(f"{domain_id}."):
        return None  # a heading from another domain's namespace — not ours to claim

    attrs = parse_attribute_table(section.body_lines)
    blocks = parse_labeled_blocks(section.body_lines)

    statement = blocks.get("standard", "").strip() or _fallback_statement(section.body_lines)
    extends = parse_references(
        blocks.get("extends", "") or attrs.get("extends", "") or attrs.get("depends_on", "")
    )

    return Standard(
        id=sid,
        title=m.group("title").strip(),
        constitution_id=domain_id,
        priority=parse_priority(attrs.get("priority", "")) or Priority.STANDARD,
        applies_to=attrs.get("applies_to", "").strip() or "All systems in domain",
        phase=None,  # a domain extends the whole core, not one phase of it
        phase_label=None,
        depends_on=extends,
        enforced_by=parse_enforced_by(attrs.get("enforced_by", "")),
        statement=statement,
        rationale=blocks.get("rationale", "").strip(),
        anti_patterns=parse_domain_anti_patterns(
            blocks.get("anti-patterns", "") or blocks.get("anti_patterns", ""), sid
        ),
        cross_references=parse_references(
            blocks.get("cross-references", "") or blocks.get("cross_references", "")
        ),
        source_path="",  # filled by caller
        source_line=section.line_start + 1,
    )


def parse_domain_constitution(
    text: str,
    *,
    entry_id: str,
    name: str,
    slug: str,
    regulatory_basis: list[str],
    reference_systems: list[str],
    path: str,
) -> Constitution:
    """Parse a Layer 4 domain extension document into a Constitution."""
    standards: list[Standard] = []
    seen: set[str] = set()

    for section in slice_sections(text, level=3):
        std = parse_domain_standard(section, entry_id)
        if std is None or std.id in seen:
            continue
        std.source_path = path
        standards.append(std)
        seen.add(std.id)

    standards.sort(key=lambda s: int(s.id.rsplit(".", 1)[1]))

    return Constitution(
        id=entry_id,
        number=99,
        name=name,
        phase=None,
        slug=slug,
        regulatory_basis=regulatory_basis,
        reference_systems=reference_systems,
        header=parse_header(text),
        path=path,
        hierarchy_rank=None,
        binds_implementation=False,
        standards=standards,
    )


def _derive_title(statement: str, max_len: int = 80) -> str:
    """Derive a short title from an abbreviated standard's statement.

    Takes the leading clause up to the first sentence boundary, em-dash, or
    `max_len` characters — whichever comes first.
    """
    text = statement.strip()
    for sep in (". ", " — ", " – ", ": "):
        idx = text.find(sep)
        if 0 < idx <= max_len:
            return text[:idx].strip()
    if len(text) <= max_len:
        return text.rstrip(".")
    return text[:max_len].rsplit(" ", 1)[0].strip() + "…"


def parse_blockquote_standards(
    text: str,
    *,
    constitution_id: ConstitutionId,
    phase: Phase | None,
    phase_label: str | None,
    path: str,
) -> list[Standard]:
    """Extract abbreviated standards written in blockquote shorthand.

    These appear under range headings (`### S8.4–S8.8 — ...`) or directly under
    Part headings. Each is `> **S{C}.{N}** — {statement}`. They carry an ID and
    a statement; priority/rationale/anti-patterns are not separately declared.
    Inline `S{C}.{N}` mentions in the statement become cross-references so the
    reference graph stays complete.
    """
    standards: list[Standard] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        m = BLOCKQUOTE_STANDARD.match(line.strip())
        if not m:
            continue
        sid = m.group("id")
        statement = m.group("text").strip()
        cross = [
            Reference(standard_id=ref)
            for ref in dict.fromkeys(STANDARD_ID.findall(statement))
            if ref != sid
        ]
        standards.append(
            Standard(
                id=sid,
                title=_derive_title(statement),
                constitution_id=constitution_id,
                priority=Priority.STANDARD,
                applies_to="Both Stacks",
                phase=phase,
                phase_label=phase_label,
                depends_on=[],
                enforced_by=[],
                statement=statement,
                rationale="",
                anti_patterns=[],
                cross_references=cross,
                abbreviated=True,
                source_path=path,
                source_line=lineno,
            )
        )
    return standards


# ─── Document header ─────────────────────────────────────────────────────────

_DATE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")


def _parse_date(raw: str | None) -> date | None:
    if not raw:
        return None
    m = _DATE.search(raw)
    if not m:
        return None
    return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))


def parse_header(text: str) -> DocumentHeader:
    """Parse the document identity block (the first attribute table)."""
    lines = text.splitlines()
    # The identity block is the first attribute table in the document.
    attrs = parse_attribute_table(lines[:60])

    status_raw = attrs.get("status", "DRAFT").strip().upper()
    try:
        status = DocumentStatus(status_raw)
    except ValueError:
        status = DocumentStatus.DRAFT

    return DocumentHeader(
        document=attrs.get("document", "").strip() or "Unknown",
        organisation=attrs.get("organisation", "KSDRILL SA").strip() or "KSDRILL SA",
        version=attrs.get("version", "v1.0").strip() or "v1.0",
        status=status,
        locked_date=_parse_date(attrs.get("locked")),
        next_review=_parse_date(attrs.get("next_review")),
        applies_to=attrs.get("applies_to", "").strip() or None,
        paired_with=(
            None
            if attrs.get("paired_with", "").strip().startswith("—")
            else attrs.get("paired_with", "").strip() or None
        ),
    )


def parse_constitution(
    text: str,
    *,
    constitution_id: ConstitutionId,
    number: int,
    name: str,
    phase: Phase | None,
    path: str,
    hierarchy_rank: int | None,
    binds_implementation: bool,
) -> Constitution:
    """Parse a full constitution document into a Constitution object.

    Captures both the full `### S{C}.{N}` block format and the blockquote
    shorthand `> **S{C}.{N}** — ...`. Full standards take precedence; a
    blockquote standard is only added if its ID was not already captured.
    """
    header = parse_header(text)
    standards: list[Standard] = []
    seen: set[str] = set()

    # Phase label is consistent within a constitution; sample it for abbreviated
    # standards from the first full standard, or synthesise from the phase.
    phase_label = f"Phase {phase.value}" if phase is not None else None

    for section in slice_sections(text, level=3):
        std = parse_standard(section, constitution_id)
        if std is not None:
            std.source_path = path
            standards.append(std)
            seen.add(std.id)
            if std.phase_label:
                phase_label = std.phase_label

    for abbr in parse_blockquote_standards(
        text,
        constitution_id=constitution_id,
        phase=phase,
        phase_label=phase_label,
        path=path,
    ):
        if abbr.id not in seen:
            standards.append(abbr)
            seen.add(abbr.id)

    standards.sort(key=lambda s: (int(s.id.split(".")[0][1:]), int(s.id.split(".")[1])))

    return Constitution(
        id=constitution_id,
        number=number,
        name=name,
        phase=phase,
        header=header,
        path=path,
        hierarchy_rank=hierarchy_rank,
        binds_implementation=binds_implementation,
        standards=standards,
    )
