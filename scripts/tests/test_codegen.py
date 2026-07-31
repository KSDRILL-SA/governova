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


# ─── A complete distribution, not just modules ───────────────────────────────


def test_the_generated_tree_is_a_resolvable_workspace_member(tmp_path):
    """The bug this closes.

    `platform/shared/types-py` is declared a uv workspace member. Emitting only
    the modules left a member directory uv could not resolve, so running codegen
    broke `uv sync` — invisible in CI, where a fresh checkout has no such
    directory at all.
    """
    src = tmp_path / "schema.py"
    src.write_text(SCHEMA, encoding="utf-8")
    out_root = tmp_path / "types-py"

    generate_python_types(src, out_root)

    manifest = out_root / "pyproject.toml"
    assert manifest.is_file(), "a workspace member without a manifest cannot be resolved"
    text = manifest.read_text(encoding="utf-8")
    assert 'name = "governova-types"' in text
    assert "hatchling" in text


def test_the_generated_package_ships_a_typing_marker(tmp_path):
    """A typed package with no marker is untyped to its consumers (S1.49)."""
    src = tmp_path / "schema.py"
    src.write_text(SCHEMA, encoding="utf-8")
    generate_python_types(src, tmp_path / "types-py")
    assert (tmp_path / "types-py" / "governova_types" / "py.typed").is_file()


def test_the_generated_package_does_not_depend_on_the_engine(tmp_path):
    """Consuming the types must never drag in the build tooling."""
    src = tmp_path / "schema.py"
    src.write_text(SCHEMA, encoding="utf-8")
    generate_python_types(src, tmp_path / "types-py")
    text = (tmp_path / "types-py" / "pyproject.toml").read_text(encoding="utf-8")
    assert 'dependencies = ["pydantic>=2.9"]' in text
    assert "governova-scripts" not in text
    assert 'name = "governova"' not in text


def test_the_version_tracks_the_schema_version(tmp_path):
    """This package *is* the schema; an independent version would drift."""
    from governova_compile.schema import SCHEMA_VERSION

    src = tmp_path / "schema.py"
    src.write_text(SCHEMA, encoding="utf-8")
    generate_python_types(src, tmp_path / "types-py")
    text = (tmp_path / "types-py" / "pyproject.toml").read_text(encoding="utf-8")
    assert f'version = "{SCHEMA_VERSION}"' in text


def test_generation_is_deterministic(tmp_path):
    """Committed output can only be drift-checked if the generator is stable.

    No timestamps, no commit SHAs — two runs must be byte-identical.
    """
    src = tmp_path / "schema.py"
    src.write_text(SCHEMA, encoding="utf-8")

    first_root, second_root = tmp_path / "a", tmp_path / "b"
    generate_python_types(src, first_root)
    generate_python_types(src, second_root)

    for relative in (
        "pyproject.toml",
        "README.md",
        "governova_types/__init__.py",
        "governova_types/models.py",
    ):
        assert (first_root / relative).read_text(encoding="utf-8") == (
            second_root / relative
        ).read_text(encoding="utf-8"), relative


def test_generated_files_covers_everything_actually_written(tmp_path):
    """`--check` compares against this map, so an unlisted file drifts unnoticed."""
    from governova_codegen.python_types import generated_files

    src = tmp_path / "schema.py"
    src.write_text(SCHEMA, encoding="utf-8")
    out_root = tmp_path / "types-py"
    generate_python_types(src, out_root)

    written = {p for p in out_root.rglob("*") if p.is_file()}
    declared = set(generated_files(out_root)) | {out_root / "governova_types" / "models.py"}
    assert written == declared, "a generated file is missing from generated_files()"


# ─── The committed artifact ──────────────────────────────────────────────────


def test_the_committed_generated_types_are_current():
    """Mirrors the compiled-index drift check: committed output must match its source."""
    from governova_codegen.python_types import _BANNER, generated_files
    from governova_compile.discovery import resolve_repo_root

    root = resolve_repo_root()
    types_py_root = root / "platform" / "shared" / "types-py"
    expected = dict(generated_files(types_py_root))
    expected[types_py_root / "governova_types" / "models.py"] = (
        _BANNER
        + "\n"
        + _strip_leading_docstring(
            (root / "scripts" / "governova_compile" / "schema.py").read_text(encoding="utf-8")
        )
    )

    for path, content in expected.items():
        assert path.is_file(), f"{path.relative_to(root).as_posix()} is not committed"
        actual = path.read_text(encoding="utf-8").replace("\r\n", "\n")
        assert actual == content.replace("\r\n", "\n"), (
            f"{path.relative_to(root).as_posix()} is stale — "
            f"run `governova-codegen --skip-ts` and commit"
        )


def test_the_committed_package_parses_the_real_index():
    """The published contract: read the index with pydantic alone."""
    import json
    import sys

    from governova_compile.discovery import resolve_repo_root

    root = resolve_repo_root()
    types_py = root / "platform" / "shared" / "types-py"
    sys.path.insert(0, str(types_py))
    try:
        for module in [m for m in sys.modules if m.startswith("governova_types")]:
            del sys.modules[module]
        import governova_types

        data = json.loads((root / "compiled" / "constitution.json").read_text(encoding="utf-8"))
        index = governova_types.CompiledIndex.model_validate(data)
        assert len(index.constitutions) == 15
        assert index.domains, "Layer 4 must survive the round trip"
    finally:
        sys.path.remove(str(types_py))
