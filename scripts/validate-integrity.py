#!/usr/bin/env python3
"""Governova — Constitutional Integrity Validator (v2 shim).

This is the documented entry path referenced by MANIFEST.md. The real
implementation lives in the `governova_compile` and `governova_validate`
packages (installed via the uv workspace). This shim compiles the index and
runs the full validator so the historical path keeps working.

Usage:
    python scripts/validate-integrity.py [--strict] [--skip-links]

Prefer the installed entry points when the workspace is set up:
    uv run governova-compile
    uv run governova-validate [--strict]

Exit codes:
    0 — integrity OK
    2 — integrity failure (or warnings under --strict)
    3 — environment error (workspace not installed)
"""

from __future__ import annotations

import sys


def main() -> int:
    try:
        from governova_compile.compiler import compile_index
        from governova_compile.discovery import resolve_repo_root
        from governova_compile.writer import write_index
    except ModuleNotFoundError:
        sys.stderr.write(
            "Governova workspace is not installed. Run `uv sync --all-packages` "
            "from the repo root, then use `uv run governova-validate`.\n"
        )
        return 3

    from governova_validate.__main__ import app

    root = resolve_repo_root()
    write_index(compile_index(root), root / "compiled")

    # Delegate argument handling (--strict, --skip-links) to the Typer app.
    try:
        app(prog_name="validate-integrity.py")
    except SystemExit as exc:
        return int(exc.code or 0)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
