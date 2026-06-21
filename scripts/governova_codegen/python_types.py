"""Generate the standalone `governova_types` Python package from schema.py.

The published `governova-types` package must not depend on the build tooling
(`governova-scripts`). So we vendor the schema models into it: read schema.py,
prepend a generated-file banner, and write it as `governova_types/models.py`.
The schema remains the single source of truth — codegen propagates it.
"""

from __future__ import annotations

from pathlib import Path

_BANNER = '''"""Governova — compiled constitutional index models.

DO NOT EDIT. Generated from scripts/governova_compile/schema.py by
`governova-codegen`. Edit the source schema, then re-run codegen.
"""
'''

_INIT = '''"""Generated Governova types. Do not edit — run `uv run governova-codegen`."""

from governova_types.models import (
    ADR,
    SCHEMA_VERSION,
    AntiPattern,
    CompiledIndex,
    Constitution,
    DocumentHeader,
    DocumentStatus,
    FrameworkPrimitive,
    Implementation,
    ImplementationBinding,
    IntegrityIssue,
    IntegrityReport,
    Phase,
    Practice,
    Priority,
    Reference,
    Runbook,
    Severity,
    Standard,
    export_json_schema,
)

__all__ = [
    "ADR",
    "SCHEMA_VERSION",
    "AntiPattern",
    "CompiledIndex",
    "Constitution",
    "DocumentHeader",
    "DocumentStatus",
    "FrameworkPrimitive",
    "Implementation",
    "ImplementationBinding",
    "IntegrityIssue",
    "IntegrityReport",
    "Phase",
    "Practice",
    "Priority",
    "Reference",
    "Runbook",
    "Severity",
    "Standard",
    "export_json_schema",
]
'''


def generate_python_types(schema_source: Path, types_py_root: Path) -> Path:
    """Vendor schema.py into the governova_types package. Returns the models path."""
    pkg = types_py_root / "governova_types"
    pkg.mkdir(parents=True, exist_ok=True)

    source = schema_source.read_text(encoding="utf-8")
    # Replace the original module docstring (first triple-quoted block) with the banner.
    body = _strip_leading_docstring(source)
    (pkg / "models.py").write_text(_BANNER + "\n" + body, encoding="utf-8")
    (pkg / "__init__.py").write_text(_INIT, encoding="utf-8")
    return pkg / "models.py"


def _strip_leading_docstring(source: str) -> str:
    """Remove the module-level docstring so the banner replaces it cleanly."""
    stripped = source.lstrip()
    if stripped.startswith('"""'):
        end = stripped.find('"""', 3)
        if end != -1:
            return stripped[end + 3 :].lstrip("\n")
    return source
