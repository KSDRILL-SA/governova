"""Tests for the codegen surface (governova_codegen) — the deterministic Python path."""

from __future__ import annotations

from governova_codegen.python_types import _strip_leading_docstring, generate_python_types

SCHEMA = '''"""Original module docstring to be replaced."""

from pydantic import BaseModel


class Thing(BaseModel):
    name: str
'''


def test_generate_python_types_vendors_schema(tmp_path):
    src = tmp_path / "schema.py"
    src.write_text(SCHEMA, encoding="utf-8")
    out_root = tmp_path / "types-py"

    models = generate_python_types(src, out_root)

    assert models.exists() and models.name == "models.py"
    text = models.read_text(encoding="utf-8")
    assert "DO NOT EDIT" in text  # banner present
    assert "Original module docstring" not in text  # source docstring stripped
    assert "class Thing(BaseModel):" in text  # code body preserved
    assert (out_root / "governova_types" / "__init__.py").is_file()


def test_strip_leading_docstring():
    assert _strip_leading_docstring('"""doc"""\n\ncode = 1\n').strip() == "code = 1"
    # No docstring -> unchanged.
    assert _strip_leading_docstring("code = 1\n") == "code = 1\n"
