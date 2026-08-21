"""Tests for the per-ecosystem dependency parsers behind repository detection.

These decide what a repository *is*, which decides its proposed profile, which
decides **which standards apply to it**. A wrong parse is not a cosmetic error:
it hands an adopter a profile for a stack they are not using, and every number
downstream is then measured against the wrong law.

Branch coverage found several of them entirely unexercised — Maven, Gradle,
Composer, Gemfile and Poetry among them. Each is tested here for what it reads,
and for what it does with input it cannot read at all, because a manifest that
is malformed, empty or simply not a mapping is the ordinary case in somebody
else's repository rather than the exotic one.
"""

from __future__ import annotations

import pytest
from governova_onboard.detect import (
    _composer_dependencies,
    _gemfile_dependencies,
    _gradle_dependencies,
    _maven_dependencies,
    _no_dependencies,
    _node_dependencies,
    _pyproject_dependencies,
    _requirements_txt_dependencies,
)

_PARSERS = (
    _node_dependencies,
    _pyproject_dependencies,
    _requirements_txt_dependencies,
    _maven_dependencies,
    _gradle_dependencies,
    _composer_dependencies,
    _gemfile_dependencies,
    _no_dependencies,
)


# ─── Every parser survives input it cannot read ──────────────────────────────


@pytest.mark.parametrize("parse", _PARSERS)
@pytest.mark.parametrize(
    "text",
    ["", "   \n\n  ", "not structured at all", "{", "<<<>>>", "\x00\x01"],
)
def test_no_parser_raises_on_input_it_cannot_read(parse, text: str) -> None:
    """Detection runs against strangers' repositories, where manifests are odd.

    A parser that raises takes the whole onboarding run down, and the person it
    fails for is the one who has not yet decided whether to trust the tool.
    """
    assert isinstance(parse(text), set)


@pytest.mark.parametrize("parse", (_node_dependencies, _composer_dependencies))
def test_json_parsers_reject_a_document_that_is_not_a_mapping(parse) -> None:
    """Valid JSON that is a list, a string or a number is still not a manifest."""
    for text in ("[1, 2, 3]", '"a string"', "42", "null"):
        assert parse(text) == set()


# ─── Node ────────────────────────────────────────────────────────────────────


def test_node_reads_all_three_dependency_blocks() -> None:
    text = """
    {
      "dependencies": {"react": "^18"},
      "devDependencies": {"vitest": "^2"},
      "peerDependencies": {"typescript": "^5"}
    }
    """
    assert _node_dependencies(text) == {"react", "vitest", "typescript"}


def test_node_ignores_a_dependency_block_that_is_not_a_mapping() -> None:
    assert _node_dependencies('{"dependencies": ["react"]}') == set()


# ─── Python ──────────────────────────────────────────────────────────────────


def test_pyproject_reads_pep621_dependencies() -> None:
    text = '[project]\ndependencies = ["pydantic>=2.9", "typer[all]>=0.12"]\n'
    assert _pyproject_dependencies(text) == {"pydantic", "typer"}


def test_pyproject_reads_poetry_dependencies() -> None:
    """Poetry keeps them under a different table, and plenty of projects use it."""
    text = '[tool.poetry.dependencies]\npython = "^3.12"\nfastapi = "^0.115"\n'
    assert _pyproject_dependencies(text) == {"python", "fastapi"}


def test_pyproject_survives_invalid_toml() -> None:
    assert _pyproject_dependencies("[project\nname = ") == set()


def test_requirements_txt_skips_comments_and_flags() -> None:
    """`-r`, `--hash` and comments are not package names."""
    text = "\n".join(
        [
            "# runtime",
            "pydantic>=2.9",
            "-r other.txt",
            "--index-url https://example.invalid/simple",
            "",
            "typer == 0.12.0",
            "rich",
        ]
    )
    assert _requirements_txt_dependencies(text) == {"pydantic", "typer", "rich"}


# ─── JVM ─────────────────────────────────────────────────────────────────────


def test_maven_reads_artifact_ids() -> None:
    text = """
    <dependencies>
      <dependency><groupId>org.springframework</groupId><artifactId>spring-core</artifactId></dependency>
      <dependency><groupId>junit</groupId><artifactId>JUnit</artifactId></dependency>
    </dependencies>
    """
    assert _maven_dependencies(text) == {"spring-core", "junit"}


def test_gradle_reads_the_artifact_out_of_a_coordinate() -> None:
    """A coordinate is `group:artifact:version`; only the middle is the name."""
    text = """
    dependencies {
        implementation 'org.springframework.boot:spring-boot-starter-web:3.2.0'
        testImplementation "org.junit.jupiter:junit-jupiter:5.10.0"
    }
    """
    assert _gradle_dependencies(text) == {"spring-boot-starter-web", "junit-jupiter"}


# ─── PHP and Ruby ────────────────────────────────────────────────────────────


def test_composer_reads_require_and_require_dev() -> None:
    text = """
    {
      "require": {"laravel/framework": "^11.0"},
      "require-dev": {"phpunit/phpunit": "^11.0"}
    }
    """
    assert _composer_dependencies(text) == {"laravel/framework", "phpunit/phpunit"}


def test_gemfile_reads_quoted_gem_names() -> None:
    text = "\n".join(
        [
            "source 'https://rubygems.invalid'",
            "gem 'rails', '~> 7.1'",
            'gem "puma"',
            "  gem 'rspec-rails', group: :test",
            "# gem 'commented-out'",
        ]
    )
    found = _gemfile_dependencies(text)
    assert {"rails", "puma", "rspec-rails"} <= found


# ─── The deliberate no-op ────────────────────────────────────────────────────


def test_the_no_dependency_parser_always_returns_nothing() -> None:
    """Some manifests mark a language without listing anything readable.

    `go.mod` and friends are detected by their *presence*; this parser exists so
    that a manifest can be registered without inventing a parse for it.
    """
    assert _no_dependencies("module example.com/thing\n\ngo 1.22\n") == set()


# ─── Detection end to end, against the shapes real repositories take ─────────


from pathlib import Path  # noqa: E402

from governova_onboard.detect import (  # noqa: E402
    MAX_MANIFEST_BYTES,
    _project_name,
    _read,
    _stack_signals,
    detect,
)


def _write(root: Path, relative: str, text: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_a_manifest_too_large_to_be_a_manifest_is_not_read(tmp_path) -> None:
    """A lockfile committed under a manifest's name would otherwise be parsed.

    Detection runs on strangers' repositories; the size bound is what stops a
    50MB generated file becoming a JSON parse in the middle of onboarding.
    """
    big = _write(tmp_path, "package.json", "x" * (MAX_MANIFEST_BYTES + 1))
    assert _read(big) is None


def test_an_unreadable_manifest_is_skipped_rather_than_fatal(tmp_path) -> None:
    assert _read(tmp_path / "does-not-exist.json") is None


def test_a_dotnet_project_is_detected_from_its_project_file(tmp_path) -> None:
    """`.csproj` has no dependency block this reads — presence is the signal."""
    project = _write(tmp_path, "Api/Api.csproj", "<Project Sdk=\"Microsoft.NET.Sdk\" />")
    signals = _stack_signals(tmp_path, [project])
    assert [s.value for s in signals] == ["dotnet"]


def test_a_framework_is_reported_with_the_dependency_that_declared_it(tmp_path) -> None:
    """The evidence is the point: a signal nobody can check is an assertion."""
    manifest = _write(
        tmp_path, "package.json", '{"dependencies": {"next": "^14", "react": "^18"}}'
    )
    signals = _stack_signals(tmp_path, [manifest])
    frameworks = [s for s in signals if s.value != "node"]
    assert frameworks, "next should have been detected"
    assert "package.json → next" in frameworks[0].evidence


def test_the_same_stack_is_not_reported_twice_from_two_manifests(tmp_path) -> None:
    """A monorepo has many `package.json` files and is still one Node stack."""
    a = _write(tmp_path, "package.json", '{"name": "root"}')
    b = _write(tmp_path, "apps/web/package.json", '{"name": "web"}')
    signals = _stack_signals(tmp_path, [a, b])
    assert [s.value for s in signals].count("node") == 1


def test_the_project_names_itself_from_its_manifest(tmp_path) -> None:
    manifest = _write(tmp_path, "package.json", '{"name": "  the-real-name  "}')
    assert _project_name(tmp_path, [manifest]) == "the-real-name"


def test_a_python_project_names_itself_from_pyproject(tmp_path) -> None:
    manifest = _write(tmp_path, "pyproject.toml", '[project]\nname = "the-python-one"\n')
    assert _project_name(tmp_path, [manifest]) == "the-python-one"


def test_a_manifest_with_no_usable_name_falls_back_to_the_directory(tmp_path) -> None:
    """The directory name is a fact about the checkout, not a guess about the project."""
    blank = _write(tmp_path, "package.json", '{"name": "   "}')
    assert _project_name(tmp_path, [blank]) == tmp_path.name


def test_an_unparseable_manifest_does_not_stop_the_search_for_a_name(tmp_path) -> None:
    """One broken file must not cost the name a later file could have supplied."""
    broken = _write(tmp_path, "package.json", "{not json")
    good = _write(tmp_path, "api/pyproject.toml", '[project]\nname = "found-later"\n')
    assert _project_name(tmp_path, [broken, good]) == "found-later"


def test_detect_returns_a_usable_detection_for_an_empty_directory(tmp_path) -> None:
    """Nothing to detect is a valid answer, and onboarding must survive it."""
    result = detect(tmp_path)
    assert result.name == tmp_path.name
    assert isinstance(result.signals, tuple)
