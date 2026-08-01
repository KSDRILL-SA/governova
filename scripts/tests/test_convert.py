"""Tests for safe conversion (Phase 3 Stage 2).

This is the stage that can break somebody's working system, so the tests are
weighted almost entirely toward **what it refuses to do**. A converter that
occasionally fails to fire is an inconvenience; one that quietly rewrites
untested legacy code is the end of an adoption.

Three properties carry the guarantee:

* **`S1.101` has no override.** A code conversion against files with no
  characterisation test is refused, and no flag skips it. A guarantee with a
  bypass is a suggestion.
* **Nothing is written without being asked.** Proposing is pure.
* **Every applied change is individually revertible (`S8.83`)**, and applying
  against content that has moved since the diff was reviewed is refused rather
  than forced.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from governova_compile.discovery import resolve_repo_root
from governova_compile.writer import load_index
from governova_onboard import assess
from governova_onboard.convert import (
    Conversion,
    ConversionRefusedError,
    ConversionStaleError,
    apply,
    propose_conversions,
    register_converter,
    registered_converters,
    revert,
)
from governova_onboard.roadmap import Kind, Protection


@pytest.fixture(scope="module")
def index():
    return load_index(resolve_repo_root() / "compiled" / "constitution.json")


def _repo(tmp_path: Path, files: dict[str, str]) -> Path:
    for name, body in files.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    return tmp_path


def _proposals(root: Path, index, **kwargs) -> list[Conversion]:
    return propose_conversions(root, assess(root, index), **kwargs)


# ── Proposing writes nothing ─────────────────────────────────────────────────


def test_proposing_touches_no_file(tmp_path: Path, index) -> None:
    root = _repo(
        tmp_path,
        {
            "pyproject.toml": '[project]\nname = "d"\n',
            ".gitignore": "__pycache__/\n",
            "src/client.py": 'import os\n\nAPI_URL = "https://api.acme-prod.com"\n',
        },
    )
    snapshot = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
    assert _proposals(root, index)
    assert {p: p.read_bytes() for p in root.rglob("*") if p.is_file()} == snapshot


# ── S1.101 has no override ───────────────────────────────────────────────────


def test_a_code_conversion_without_a_test_is_refused(tmp_path: Path, index) -> None:
    root = _repo(
        tmp_path,
        {
            "pyproject.toml": '[project]\nname = "d"\n',
            "src/client.py": 'import os\n\nAPI_URL = "https://api.acme-prod.com"\n',
        },
    )
    conversion = next(c for c in _proposals(root, index) if c.path == "src/client.py")
    assert conversion.protection is Protection.UNKNOWN
    assert not conversion.applicable
    assert "S1.101" in conversion.refusal

    with pytest.raises(ConversionRefusedError):
        apply(root, conversion)
    # And the file is untouched by the attempt.
    assert (root / "src/client.py").read_text(encoding="utf-8") == conversion.before


def test_a_code_conversion_with_a_test_is_allowed(tmp_path: Path, index) -> None:
    """The same conversion, once behaviour is pinned, becomes applicable."""
    root = _repo(
        tmp_path,
        {
            "pyproject.toml": '[project]\nname = "d"\n',
            "src/client.py": 'import os\n\nAPI_URL = "https://api.acme-prod.com"\n',
            "tests/test_client.py": "def test_url(): ...\n",
        },
    )
    conversion = next(c for c in _proposals(root, index) if c.path == "src/client.py")
    assert conversion.protection is Protection.PROTECTED
    assert conversion.applicable, conversion.refusal


def test_there_is_no_flag_that_overrides_the_refusal() -> None:
    """`apply` takes no force parameter, and that is the guarantee.

    Asserted on the signature rather than trusted, because adding one later
    would be a one-line change that silently removes `S1.101`.
    """
    import inspect

    parameters = set(inspect.signature(apply).parameters)
    assert parameters == {"root", "conversion"}


# ── The transformation preserves behaviour ───────────────────────────────────


def test_the_url_conversion_keeps_the_current_value_as_the_default(
    tmp_path: Path, index
) -> None:
    """`os.environ["NAME"]` would raise where the literal used to work.

    Preserving the literal as the default is what makes this non-breaking: an
    unset variable produces exactly the previous value.
    """
    root = _repo(
        tmp_path,
        {
            "pyproject.toml": '[project]\nname = "d"\n',
            "src/client.py": 'import os\n\nAPI_URL = "https://api.acme-prod.com"\n',
            "tests/test_client.py": "def test_url(): ...\n",
        },
    )
    conversion = next(c for c in _proposals(root, index) if c.path == "src/client.py")
    assert 'os.environ.get("API_URL", "https://api.acme-prod.com")' in conversion.after
    # The transformed module still executes, and to the same value.
    namespace: dict[str, object] = {}
    exec(compile(conversion.after, "client.py", "exec"), namespace)
    assert namespace["API_URL"] == "https://api.acme-prod.com"


def test_a_file_without_an_os_import_is_left_alone(tmp_path: Path, index) -> None:
    """Inserting an import means guessing where it goes. The guess is not worth it."""
    root = _repo(
        tmp_path,
        {
            "pyproject.toml": '[project]\nname = "d"\n',
            "src/legacy.py": 'SERVICE_URL = "https://svc.acme-prod.com"\n',
            "tests/test_legacy.py": "def test_x(): ...\n",
        },
    )
    assert [c for c in _proposals(root, index) if c.path == "src/legacy.py"] == []


def test_the_conversion_changes_only_the_line_it_targets(tmp_path: Path, index) -> None:
    """A larger diff than the change gives a reviewer something extra to explain.

    The first version matched with `\\s*$`, which spans newlines — so it ate the
    blank line after the assignment and deleted whitespace it had no business
    touching.
    """
    source = 'import os\n\nAPI_URL = "https://api.acme-prod.com"\n\nTIMEOUT = 30\n'
    root = _repo(
        tmp_path,
        {
            "pyproject.toml": '[project]\nname = "d"\n',
            "src/client.py": source,
            "tests/test_client.py": "def test_url(): ...\n",
        },
    )
    conversion = next(c for c in _proposals(root, index) if c.path == "src/client.py")
    before_lines = conversion.before.splitlines()
    after_lines = conversion.after.splitlines()
    assert len(before_lines) == len(after_lines)
    differing = [
        n for n, (a, b) in enumerate(zip(before_lines, after_lines, strict=True)) if a != b
    ]
    assert len(differing) == 1


def test_a_non_url_literal_is_not_touched(tmp_path: Path, index) -> None:
    """The converter must not act where its rule would not have fired."""
    root = _repo(
        tmp_path,
        {
            "pyproject.toml": '[project]\nname = "d"\n',
            "src/client.py": (
                'import os\n\nAPI_URL = "https://api.acme-prod.com"\n'
                'DOCS = "https://docs.acme-prod.com"\n'
            ),
            "tests/test_client.py": "def test_url(): ...\n",
        },
    )
    conversion = next(c for c in _proposals(root, index) if c.path == "src/client.py")
    assert 'DOCS = "https://docs.acme-prod.com"' in conversion.after


# ── Applying, reverting, and staleness ───────────────────────────────────────


def test_apply_then_revert_restores_the_file_exactly(tmp_path: Path, index) -> None:
    """`S8.83` — the way back is a string this object holds, not a re-derivation."""
    root = _repo(tmp_path, {"pyproject.toml": '[project]\nname = "d"\n', ".gitignore": "build/\n"})
    conversion = next(c for c in _proposals(root, index) if c.path == ".gitignore")
    original = (root / ".gitignore").read_text(encoding="utf-8")

    apply(root, conversion)
    assert ".env" in (root / ".gitignore").read_text(encoding="utf-8")

    revert(root, conversion)
    assert (root / ".gitignore").read_text(encoding="utf-8") == original


def test_applying_against_moved_content_is_refused(tmp_path: Path, index) -> None:
    """A diff reviewed against content that has since changed is a different diff."""
    root = _repo(tmp_path, {"pyproject.toml": '[project]\nname = "d"\n', ".gitignore": "build/\n"})
    conversion = next(c for c in _proposals(root, index) if c.path == ".gitignore")

    (root / ".gitignore").write_text("build/\ndist/\n", encoding="utf-8")
    with pytest.raises(ConversionStaleError):
        apply(root, conversion)
    assert (root / ".gitignore").read_text(encoding="utf-8") == "build/\ndist/\n"


def test_reverting_a_file_that_moved_on_is_refused(tmp_path: Path, index) -> None:
    root = _repo(tmp_path, {"pyproject.toml": '[project]\nname = "d"\n', ".gitignore": "build/\n"})
    conversion = next(c for c in _proposals(root, index) if c.path == ".gitignore")
    apply(root, conversion)
    (root / ".gitignore").write_text("something else entirely\n", encoding="utf-8")
    with pytest.raises(ConversionStaleError):
        revert(root, conversion)


def test_the_gitignore_conversion_satisfies_the_probe_it_cites(tmp_path: Path, index) -> None:
    """A converter must fix the thing, not the check — so check the check.

    This is the test that separates a real conversion from one that merely
    silences a probe: after applying, the probe that produced the finding is no
    longer violated.
    """
    from governova_evidence import Verdict, run_probes

    root = _repo(tmp_path, {"pyproject.toml": '[project]\nname = "d"\n', ".gitignore": "build/\n"})
    before = next(r for r in run_probes(root) if r.standard == "S8.25")
    assert before.verdict is Verdict.VIOLATED

    apply(root, next(c for c in _proposals(root, index) if c.path == ".gitignore"))

    after = next(r for r in run_probes(root) if r.standard == "S8.25")
    assert after.verdict is not Verdict.VIOLATED


def test_nothing_is_proposed_for_a_compliant_repository(tmp_path: Path, index) -> None:
    root = _repo(
        tmp_path,
        {"pyproject.toml": '[project]\nname = "d"\n', ".gitignore": "build/\n.env\n"},
    )
    assert [c for c in _proposals(root, index) if c.path == ".gitignore"] == []


# ── The registry ─────────────────────────────────────────────────────────────


def test_converters_are_registered_not_hardcoded() -> None:
    assert "gitignore-env" in registered_converters()
    assert "env-sourced-urls" in registered_converters()


def test_an_unknown_converter_name_is_an_error(tmp_path: Path, index) -> None:
    root = _repo(tmp_path, {"pyproject.toml": '[project]\nname = "d"\n'})
    with pytest.raises(KeyError):
        _proposals(root, index, only="no-such-converter")


def test_a_house_converter_can_be_added_without_editing_core(tmp_path: Path, index) -> None:
    """`AP-S1.107a` — the extension point, exercised rather than asserted."""
    marker = "house-only-test-converter"

    def _house(root: Path, baseline) -> list[Conversion]:
        return [
            Conversion(
                converter=marker,
                standard="S1.1",
                path="NOTES.md",
                before="",
                after="added\n",
                rationale="house rule",
                kind=Kind.STRUCTURAL,
                protection=Protection.PROTECTED,
            )
        ]

    register_converter(marker, _house)
    try:
        root = _repo(tmp_path, {"pyproject.toml": '[project]\nname = "d"\n'})
        proposed = _proposals(root, index, only=marker)
        assert [c.converter for c in proposed] == [marker]
    finally:
        from governova_onboard.convert import _REGISTRY

        _REGISTRY.pop(marker, None)


def test_a_conversion_that_changes_nothing_is_refused() -> None:
    """An empty diff is not a change, and offering one wastes a review."""
    conversion = Conversion(
        converter="x",
        standard="S1.1",
        path="a.txt",
        before="same\n",
        after="same\n",
        rationale="r",
        kind=Kind.STRUCTURAL,
        protection=Protection.PROTECTED,
    )
    assert not conversion.applicable
    assert conversion.diff == ""
