"""Build the System Bible by documenting every source file in the repo."""

from __future__ import annotations

import dataclasses
from pathlib import Path

from governova_checks import iter_source_files
from governova_compile.discovery import resolve_repo_root

from governova_bible.extract import extract_file
from governova_bible.model import SystemBible


def build_bible(root: Path | None = None, *, semantic: bool = False) -> SystemBible:
    """Document every source file under `root`.

    Uses an empty ignore set so the Bible covers the whole codebase — including
    tests and the rule set (which the enforcer/score deliberately skip).

    When `semantic` is set and an LLM endpoint is configured, each entry is enriched
    with a one/two-sentence behavioural summary. Without a key it is a clean no-op.
    """
    r = root or resolve_repo_root()
    entries = [extract_file(p, r) for p in iter_source_files(r, ignores=())]

    if semantic:
        from governova_semantic import describe_code, from_env

        if from_env().is_configured:
            enriched = []
            for e in entries:
                code = (r / e.path).read_text(encoding="utf-8", errors="replace")
                enriched.append(dataclasses.replace(e, semantic_summary=describe_code(code)))
            entries = enriched

    entries.sort(key=lambda e: e.path)
    return SystemBible(entries=entries)
