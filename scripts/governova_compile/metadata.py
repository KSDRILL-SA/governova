"""Lightweight metadata extractors for runbooks, ADRs, and implementation bindings."""

from __future__ import annotations

import re
from pathlib import Path

from governova_compile.markdown import parse_attribute_table, slice_sections
from governova_compile.parsers import parse_header
from governova_compile.schema import (
    ADR,
    ConstitutionId,
    DocumentHeader,
    Implementation,
    ImplementationBinding,
    Practice,
    Runbook,
)

RUNBOOK_ID = re.compile(r"RB-(\d{2})")
ADR_ID = re.compile(r"ADR-(\d{3})")
BINDING_HEADING = re.compile(
    r"^S(?P<c>\d+)\.(?P<n>\d+)/(?P<stack>[a-z][a-z0-9_-]*)\s*[-—–]\s*(?P<title>.+)$"
)
BINDING_ANTI_PATTERN = re.compile(r"`?(AP-S\d+\.\d+[a-z])`?")
PRACTICE_HEADING = re.compile(r"^P(?P<c>\d+)\.(?P<n>\d+)\s*[-—–]\s*(?P<title>.+)$")
STANDARD_ID = re.compile(r"\bS\d+\.\d+\b")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _title_from_heading(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def parse_runbook(path: Path, repo_root: Path) -> Runbook | None:
    m = RUNBOOK_ID.search(path.name)
    if not m:
        return None
    text = _read(path)
    attrs = parse_attribute_table(text.splitlines()[:40])
    trigger = attrs.get("trigger") or attrs.get("triggers") or _first_trigger_sentence(text) or "—"
    name = _title_from_heading(text, path.stem)
    # Strip the "RB-NN — " prefix from the title if present.
    name = re.sub(r"^RB-\d{2}\s*[-—–]\s*", "", name).strip()
    return Runbook(
        id=f"RB-{m.group(1)}",
        name=name,
        trigger=trigger.strip(),
        path=str(path.relative_to(repo_root)),
    )


def _first_trigger_sentence(text: str) -> str | None:
    m = re.search(r"(?im)^\s*\**trigger\**\s*[:|]\s*(.+)$", text)
    if m:
        return m.group(1).strip().strip("|").strip()
    return None


def parse_adr(path: Path, repo_root: Path) -> ADR | None:
    m = ADR_ID.search(path.name)
    if not m:
        return None
    text = _read(path)
    attrs = parse_attribute_table(text.splitlines()[:40])
    name = _title_from_heading(text, path.stem)
    name = re.sub(r"^ADR-\d{3}\s*[-—–:]\s*", "", name).strip()
    status = attrs.get("status")
    return ADR(
        id=f"ADR-{m.group(1)}",
        name=name,
        status=status.strip().upper() if status else None,
        path=str(path.relative_to(repo_root)),
    )


def parse_implementation(
    path: Path,
    *,
    stack: str,
    binds_constitution: ConstitutionId,
    name: str,
    repo_root: Path,
) -> Implementation:
    """Parse an implementation guide into Practices and (if present) bindings.

    Current guides express the implementation layer as Practices
    (`## P{C}.{N} — Title`), whose subsections cite the standards they satisfy
    via inline `S{C}.{N}` references. Future spec-compliant guides may use
    `### S{C}.{N}/{stack} — Title` binding headings; both are captured.
    """
    text = _read(path)
    header: DocumentHeader = parse_header(text)

    practices: list[Practice] = []
    seen_practices: set[str] = set()
    for section in slice_sections(text, level=2):
        pm = PRACTICE_HEADING.match(section.heading.text)
        if not pm:
            continue
        pid = f"P{int(pm.group('c'))}.{int(pm.group('n'))}"
        if pid in seen_practices:
            continue
        seen_practices.add(pid)
        body = "\n".join(section.body_lines)
        satisfied = list(dict.fromkeys(STANDARD_ID.findall(body)))
        practices.append(
            Practice(
                id=pid,
                title=pm.group("title").strip(),
                satisfies_standards=satisfied,
                source_path=str(path.relative_to(repo_root)),
                source_line=section.line_start + 1,
            )
        )

    bindings: list[ImplementationBinding] = []
    seen_bindings: set[str] = set()
    for section in slice_sections(text, level=3):
        bm = BINDING_HEADING.match(section.heading.text)
        if not bm:
            continue
        binding_id = f"S{int(bm.group('c'))}.{int(bm.group('n'))}/{bm.group('stack')}"
        if binding_id in seen_bindings:
            continue
        seen_bindings.add(binding_id)
        bound_standard = f"S{int(bm.group('c'))}.{int(bm.group('n'))}"
        body = "\n".join(section.body_lines).strip()
        ap_match = BINDING_ANTI_PATTERN.search(body)
        bindings.append(
            ImplementationBinding(
                id=binding_id,
                binds_standard=bound_standard,
                stack=bm.group("stack"),
                satisfies_by=_first_paragraph(body) or body[:280],
                anti_pattern=ap_match.group(1) if ap_match else None,
            )
        )

    return Implementation(
        stack=stack,
        binds_constitution=binds_constitution,
        name=name,
        header=header,
        path=str(path.relative_to(repo_root)),
        practices=practices,
        bindings=bindings,
    )


def _first_paragraph(text: str) -> str | None:
    para: list[str] = []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("|") or s.startswith("#"):
            continue
        if not s:
            if para:
                break
            continue
        para.append(s)
    return " ".join(para).strip() or None
