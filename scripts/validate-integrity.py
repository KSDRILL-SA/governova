#!/usr/bin/env python3
"""
Governova — Constitutional Integrity Validator

Checks that every S{C}.{N} reference in the repo resolves to a real standard
defined in the constitution core.

Authoritative definition model: a standard S{C}.{N} is "defined" if it appears
in the core constitution file that owns constitution C (matched by the C{NN}
prefix in the filename). This is robust to the fact that constitutions define
standards in several formats — section headings, tables, and grouped lists —
not only `### S{C}.{N}` headings. Numbers are normalised (S2.04 == S2.4) because
the corpus mixes zero-padded and bare references.

Usage:
  python scripts/validate-integrity.py
  python scripts/validate-integrity.py --strict   (exit non-zero on any gap)

Exit codes:
  0 — All references resolve
  1 — Unresolved references found
  2 — Script error
"""

import re
import sys
import argparse
from pathlib import Path

STD = re.compile(r'\bS(\d+)\.(\d+)\b')
FILE_C = re.compile(r'\bC(\d+)\b')

CONSTITUTION_DIR = Path('constitution')
CORE_DIR = CONSTITUTION_DIR / 'core'
SCAN_DIRS = ['constitution', 'protocols', 'governance', 'framework',
             'reference-systems', 'templates']


def norm(c, n):
    return f'S{int(c)}.{int(n)}'


def owning_constitution(md_file: Path):
    """Constitution number that a core file owns, from its C{NN} filename prefix."""
    m = FILE_C.search(md_file.name)
    return int(m.group(1)) if m else None


def extract_defined() -> set:
    """A standard is defined if its ID appears in the core file owning its constitution."""
    defined = set()
    core_files = list(CORE_DIR.rglob('*.md')) + list(CONSTITUTION_DIR.glob('C*.md'))
    for md in core_files:
        owner = owning_constitution(md)
        if owner is None:
            continue
        text = md.read_text(encoding='utf-8')
        for m in STD.finditer(text):
            if int(m.group(1)) == owner:
                defined.add(norm(m.group(1), m.group(2)))
    return defined


def extract_references() -> dict:
    refs = {}
    known = set()  # constitutions that actually define standards
    for scan in SCAN_DIRS:
        base = Path(scan)
        if not base.exists():
            continue
        for md in base.rglob('*.md'):
            for ln, line in enumerate(md.read_text(encoding='utf-8').splitlines(), 1):
                for m in STD.finditer(line):
                    refs.setdefault(norm(m.group(1), m.group(2)), []).append((str(md), ln))
    return refs


def main():
    ap = argparse.ArgumentParser(description='Validate Governova constitutional integrity')
    ap.add_argument('--strict', action='store_true', help='exit non-zero on any gap')
    ap.parse_args()

    print('Governova Constitutional Integrity Validator')
    print('=' * 50)

    if not CORE_DIR.exists():
        print(f'ERROR: core directory not found: {CORE_DIR}')
        sys.exit(2)

    defined = extract_defined()
    print(f'Defined standards (authoritative): {len(defined)}')

    refs = extract_references()
    print(f'Unique standard references found:  {len(refs)}')

    # Only validate references to constitutions that define standards (C1..C10).
    defined_constitutions = {int(s[1:].split(".")[0]) for s in defined}
    unresolved = {
        sid: locs for sid, locs in refs.items()
        if int(sid[1:].split(".")[0]) in defined_constitutions and sid not in defined
    }

    if not unresolved:
        print('\nAll references resolve. Integrity check passed.')
        sys.exit(0)

    print(f'\n{len(unresolved)} unresolved references:')
    for sid, locs in sorted(unresolved.items()):
        print(f'\n  {sid} - not defined in its constitution')
        for fp, ln in locs[:3]:
            print(f'    {fp}:{ln}')
        if len(locs) > 3:
            print(f'    ... and {len(locs) - 3} more')

    sys.exit(1)


if __name__ == '__main__':
    main()
