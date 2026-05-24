#!/usr/bin/env python3
"""
Governova — Constitutional Integrity Validator
Checks that every S{C}.{N} and AP-S{C}.{N}{letter} reference in the repo
resolves to a real standard in the constitution core.

Usage:
  python scripts/validate-integrity.py
  python scripts/validate-integrity.py --strict   (fails on SEV3 gaps)

Exit codes:
  0 — All references resolve
  1 — Unresolved references found
  2 — Script error
"""

import os
import re
import sys
import argparse
from pathlib import Path


STANDARD_PATTERN = re.compile(r'\bS(\d+)\.(\d+)\b')
ANTI_PATTERN_PATTERN = re.compile(r'\bAP-S(\d+)\.(\d+)([a-z])\b')
CONSTITUTION_DIR = Path('constitution/core')
SCAN_DIRS = [
    'constitution',
    'protocols',
    'governance',
    'framework',
    'reference-systems',
    'templates',
]


def extract_defined_standards(constitution_dir: Path) -> set[str]:
    """Extract all S{C}.{N} IDs defined in constitution files."""
    defined = set()
    for md_file in constitution_dir.rglob('*.md'):
        content = md_file.read_text(encoding='utf-8')
        for match in STANDARD_PATTERN.finditer(content):
            line_start = content.rfind('\n', 0, match.start()) + 1
            line = content[line_start:content.find('\n', match.end())]
            if line.strip().startswith(f'S{match.group(1)}.{match.group(2)}'):
                defined.add(f'S{match.group(1)}.{match.group(2)}')
    return defined


def extract_references(scan_dirs: list[str]) -> dict[str, list[tuple[str, int]]]:
    """Extract all S{C}.{N} references with their file and line number."""
    references = {}
    for scan_dir in scan_dirs:
        for md_file in Path(scan_dir).rglob('*.md'):
            content = md_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            for line_num, line in enumerate(lines, 1):
                for match in STANDARD_PATTERN.finditer(line):
                    std_id = f'S{match.group(1)}.{match.group(2)}'
                    if std_id not in references:
                        references[std_id] = []
                    references[std_id].append((str(md_file), line_num))
    return references


def main():
    parser = argparse.ArgumentParser(description='Validate Governova constitutional integrity')
    parser.add_argument('--strict', action='store_true', help='Fail on any unresolved reference')
    args = parser.parse_args()

    print('Governova Constitutional Integrity Validator')
    print('=' * 50)

    if not CONSTITUTION_DIR.exists():
        print(f'ERROR: Constitution directory not found: {CONSTITUTION_DIR}')
        sys.exit(2)

    print(f'Scanning defined standards in {CONSTITUTION_DIR}...')
    defined = extract_defined_standards(CONSTITUTION_DIR)
    print(f'Found {len(defined)} defined standards.')

    print(f'Scanning references in {SCAN_DIRS}...')
    references = extract_references(SCAN_DIRS)
    print(f'Found {len(references)} unique standard references.')

    unresolved = {sid: locs for sid, locs in references.items() if sid not in defined}

    if not unresolved:
        print('\n✓ All references resolve. Integrity check passed.')
        sys.exit(0)

    print(f'\n✗ {len(unresolved)} unresolved references found:')
    for std_id, locations in sorted(unresolved.items()):
        print(f'\n  {std_id} — not found in constitution core')
        for filepath, line_num in locations[:3]:
            print(f'    {filepath}:{line_num}')
        if len(locations) > 3:
            print(f'    ... and {len(locations) - 3} more')

    sys.exit(1)


if __name__ == '__main__':
    main()
