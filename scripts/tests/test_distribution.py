"""Tests for running Governova against a repository that is not its own.

The engine was architecturally confined to its own source tree: every surface
resolved a root that had to contain `constitution/`, so an installed `governova`
errored on first use anywhere else. These tests pin the separation that fixed it —
the *constitution* it governs with is distinct from the *repository* it governs —
and, most importantly, pin the precedence order, because getting that wrong would
silently judge a pull request by the wrong constitution.
"""

from __future__ import annotations

import json
import subprocess
import tomllib
from pathlib import Path

import pytest
from governova_compile.discovery import resolve_repo_root, resolve_target_root
from governova_compile.writer import (
    CONSTITUTION_ENV_VAR,
    find_index,
    load_active_index,
    resolve_index_path,
)


def _fake_index(path: Path, *, marker: str) -> Path:
    """A minimal but schema-valid compiled index, tagged so we can tell copies apart."""
    real = resolve_repo_root() / "compiled" / "constitution.json"
    data = json.loads(real.read_text(encoding="utf-8"))
    data["source_commit_sha"] = marker
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


# ─── The two roots are different questions ───────────────────────────────────


def test_target_root_never_raises_in_a_plain_directory(tmp_path: Path) -> None:
    # Verifies REQ-001 — the engine governs a repository holding no source tree.
    """The defect: a directory with no constitution/ was an error, not a target."""
    assert resolve_target_root(tmp_path) == tmp_path.resolve()


def test_target_root_prefers_the_git_working_tree(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    nested = tmp_path / "src" / "deep"
    nested.mkdir(parents=True)
    assert resolve_target_root(nested) == tmp_path.resolve()


def test_repo_root_still_requires_the_source_corpus(tmp_path: Path) -> None:
    """`compile`/`validate`/`codegen` are maintainer operations and must stay strict."""
    with pytest.raises(FileNotFoundError):
        resolve_repo_root(tmp_path)


def test_repo_root_resolves_inside_the_governova_tree() -> None:
    root = resolve_repo_root()
    assert (root / "constitution").is_dir()


# ─── Index precedence — the part that must not be wrong ──────────────────────


def test_an_explicit_path_wins(tmp_path: Path) -> None:
    explicit = _fake_index(tmp_path / "explicit.json", marker="explicit")
    assert resolve_index_path(explicit) == explicit


def test_an_explicit_path_that_does_not_exist_is_an_error(tmp_path: Path) -> None:
    """Silently falling back would govern by a constitution nobody asked for."""
    with pytest.raises(FileNotFoundError):
        resolve_index_path(tmp_path / "missing.json")


def test_the_environment_variable_is_honoured(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    override = _fake_index(tmp_path / "org.json", marker="org-corpus")
    monkeypatch.setenv(CONSTITUTION_ENV_VAR, str(override))
    assert resolve_index_path() == override
    assert load_active_index().source_commit_sha == "org-corpus"


def test_a_bad_environment_variable_is_an_error_not_a_fallback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv(CONSTITUTION_ENV_VAR, str(tmp_path / "nope.json"))
    with pytest.raises(FileNotFoundError):
        resolve_index_path()


def test_a_working_tree_index_beats_the_bundled_one(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The property that keeps Governova's own CI honest.

    A pull request that amends the constitution must be judged by the amendment
    it proposes, not by whichever copy is installed.
    """
    monkeypatch.delenv(CONSTITUTION_ENV_VAR, raising=False)
    local = _fake_index(tmp_path / "compiled" / "constitution.json", marker="in-branch")
    assert resolve_index_path(start=tmp_path) == local
    assert load_active_index(start=tmp_path).source_commit_sha == "in-branch"


def test_the_working_tree_index_is_found_from_a_nested_directory(tmp_path: Path) -> None:
    _fake_index(tmp_path / "compiled" / "constitution.json", marker="root")
    nested = tmp_path / "a" / "b" / "c"
    nested.mkdir(parents=True)
    assert find_index(nested) == tmp_path / "compiled" / "constitution.json"


def test_find_index_returns_none_when_a_repo_has_no_constitution(tmp_path: Path) -> None:
    """The normal case for a repository Governova governs but does not contain."""
    assert find_index(tmp_path) is None


# ─── Governing a foreign repository ──────────────────────────────────────────


def test_the_engine_scans_a_repository_with_no_constitution(tmp_path: Path) -> None:
    """End to end: a violation in somebody else's repo is still detected."""
    from governova_checks import scan_paths

    src = tmp_path / "src"
    src.mkdir()
    api = src / "api.ts"
    api.write_text("const tenantId = req.query.tenantId;\n", encoding="utf-8")

    findings = scan_paths([api])
    assert any(f.anti_pattern == "AP-D-SAAS.1b" and f.blocking for f in findings)


def test_coverage_resolves_a_constitution_without_a_source_tree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from governova_checks import enforcement_coverage

    monkeypatch.setenv(
        CONSTITUTION_ENV_VAR, str(resolve_repo_root() / "compiled" / "constitution.json")
    )
    monkeypatch.chdir(tmp_path)
    assert enforcement_coverage()["total_anti_patterns"] > 0


# ─── Packaging ───────────────────────────────────────────────────────────────


def _packaging() -> dict:
    root = resolve_repo_root()
    return tomllib.loads((root / "scripts" / "pyproject.toml").read_text(encoding="utf-8"))


def test_the_distribution_is_named_for_the_product() -> None:
    assert _packaging()["project"]["name"] == "governova"


def test_the_wheel_bundles_the_compiled_constitution() -> None:
    """Without this the installed package has no constitution to govern with.

    Done by a build hook rather than a static force-include: the file sits at
    `../compiled/` when building in the repository and at `./compiled/` when
    building from an sdist, and `uv build` builds the wheel from the sdist. The
    static form produced a working wheel locally and a broken one in the release
    pipeline.
    """
    cfg = _packaging()
    hook = cfg["tool"]["hatch"]["build"]["hooks"]["custom"]
    assert hook["path"] == "hatch_build.py"
    assert (resolve_repo_root() / "scripts" / "hatch_build.py").is_file()
    assert (resolve_repo_root() / "compiled" / "constitution.json").is_file()


def test_the_sdist_carries_the_constitution_so_it_can_build_a_wheel() -> None:
    """An sdist that cannot build a wheel is broken for `pip install --no-binary`."""
    include = _packaging()["tool"]["hatch"]["build"]["targets"]["sdist"]["force-include"]
    assert include["../compiled/constitution.json"] == "compiled/constitution.json"


def _locate_constitution():  # type: ignore[no-untyped-def]
    """Import the build hook's resolver, which lives outside the packages."""
    import sys

    sys.path.insert(0, str(resolve_repo_root() / "scripts"))
    try:
        from hatch_build import locate_constitution

        return locate_constitution
    finally:
        sys.path.pop(0)


@pytest.mark.parametrize(
    "layout", ["../compiled/constitution.json", "compiled/constitution.json"]
)
def test_the_build_hook_finds_the_constitution_in_both_layouts(
    tmp_path: Path, layout: str
) -> None:
    """The repository and an unpacked sdist put the file in different places.

    `uv build` builds the wheel from the sdist, so a resolver that only knows the
    repository layout produces a working wheel locally and a broken one on release.
    """
    project = tmp_path / "project"
    project.mkdir()
    target = (project / layout).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("{}", encoding="utf-8")

    assert _locate_constitution()(project) == target


def test_the_build_hook_refuses_to_ship_a_wheel_without_a_constitution(
    tmp_path: Path,
) -> None:
    """A wheel missing it installs cleanly and fails on first use.

    That is a defect the installer discovers rather than the shipper, so the
    build fails loudly instead.
    """
    with pytest.raises(FileNotFoundError, match="compiled constitution was not"):
        _locate_constitution()(tmp_path)


def test_the_bundled_index_is_not_committed_as_a_duplicate() -> None:
    """One constitution, one file. The wheel copy is made at build time."""
    duplicate = resolve_repo_root() / "scripts" / "governova_compile" / "data"
    assert not duplicate.exists(), "a committed copy would drift from the real index"


def test_every_console_script_points_at_a_real_module() -> None:
    import importlib

    for entry in _packaging()["project"]["scripts"].values():
        module_name = entry.split(":", 1)[0]
        assert importlib.import_module(module_name)


def test_the_action_installs_the_package_rather_than_syncing_a_workspace() -> None:
    """`uv sync --all-packages` resolved the *consumer's* workspace — the defect."""
    action = (
        resolve_repo_root() / "platform" / "surfaces" / "cicd-enforcer" / "action.yml"
    ).read_text(encoding="utf-8")
    # Comments explain the defect by name, so only executable lines are inspected.
    executable = "\n".join(
        line for line in action.splitlines() if not line.strip().startswith("#")
    )
    assert "uv sync" not in executable
    assert "pip install" in executable
    assert CONSTITUTION_ENV_VAR in executable


def test_governova_governs_itself_from_source_not_from_a_release() -> None:
    """A PR amending the constitution must be judged by the amendment it proposes."""
    workflow = (
        resolve_repo_root() / ".github" / "workflows" / "enforce.yml"
    ).read_text(encoding="utf-8")
    assert "version: source" in workflow


def test_mypy_strictness_is_declared_where_ci_actually_reads_it() -> None:
    """The config CI uses is `scripts/pyproject.toml`, not the root one.

    `mypy` reads the configuration in its working directory, and CI runs
    `working-directory: scripts`. The root `pyproject.toml` had declared
    `strict = true` since it was written and CI never ran under it, so the
    repository declared strict typing, enforced ordinary typing, and stayed
    green — the same shape as a semantic tier reaching nothing while every build
    passed. Enabling it surfaced four real errors.

    This asserts the setting lives in the file that governs the run rather than
    the file that reads well, which is the cheap setup check rather than the
    expensive result check.
    """
    root = resolve_repo_root()
    for manifest in (root / "pyproject.toml", root / "scripts" / "pyproject.toml"):
        config = tomllib.loads(manifest.read_text(encoding="utf-8"))
        assert config["tool"]["mypy"]["strict"] is True, manifest


def test_the_type_check_still_runs_from_scripts() -> None:
    """The assertion above is only meaningful while this stays true.

    If CI ever stops setting `working-directory: scripts`, the config it reads
    changes and the guarantee moves with it. Pinning both halves means the pair
    cannot drift apart silently.
    """
    workflow = (resolve_repo_root() / ".github" / "workflows" / "validate.yml").read_text(
        encoding="utf-8"
    )
    assert "working-directory: scripts" in workflow
    assert "uv run mypy" in workflow
