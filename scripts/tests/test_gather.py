"""Tests for the scan surface — which files the engine reads, and which it does not.

A rule can only be as good as the set of files it is pointed at. Two failures
live here, and they are opposites: scanning a test file produces a finding that
is true about the line and false about the repository, and over-matching the
ignore list silently stops covering part of the tree.
"""

from __future__ import annotations

import pytest
from governova_checks import iter_source_files, scan_paths
from governova_checks.gather import DEFAULT_IGNORES, is_ignored

# ─── Test files are not scanned, in every convention ────────────────────────


# Every layout a test file is written in, and what the scanner must do with it.
# Enumerated rather than spot-checked: the list this asserts against was correct
# for Python and Go and silently missing JavaScript, and nothing failed. A
# convention added to `DEFAULT_IGNORES` without a row here, or a row here with no
# entry in the list, is the same defect in either direction.
_TEST_LAYOUTS = (
    ("tests/auth.ts", "tests/ directory"),
    ("test/auth.js", "test/ directory, singular"),
    ("__tests__/auth.ts", "__tests__/ directory"),
    ("spec/auth.rb", "spec/ directory"),
    ("src/nested/tests/auth.ts", "tests/ directory, nested"),
    ("test_auth.py", "Python filename"),
    ("pkg/test_auth.py", "Python filename, nested"),
    ("auth_test.go", "Go filename"),
    ("src/auth.test.ts", "JS/TS co-located, .test."),
    ("src/auth.spec.ts", "JS/TS co-located, .spec."),
    ("src/auth.test.tsx", "JS/TS co-located, .test. with tsx"),
)

# Source files whose names merely resemble the conventions above.
_NOT_TESTS = (
    "src/latest.ts",
    "src/spectrum.ts",
    "src/contest.py",
    "src/protest.go",
)


@pytest.mark.parametrize(("path", "convention"), _TEST_LAYOUTS)
def test_every_test_convention_is_skipped(path: str, convention: str) -> None:
    """`S1.69` mandates co-located `{source}.test.ts`, and it was being scanned.

    A test file exists to exercise the behaviour a rule looks for, so scanning
    one produces a finding that is true about the line and false about the
    repository. `governova onboard` against express reported 20 of 21 blocking
    findings from fixtures in `test/`; the fix that followed added the directory
    conventions plus Python and Go filenames, and stopped there.

    So a repository following the constitution's own test layout was reported
    against every rule its tests deliberately trigger. This parametrisation is
    the thing that was missing — not another entry in the list, but a check that
    the list is complete.
    """
    assert is_ignored(path, DEFAULT_IGNORES), f"{convention} is scanned: {path}"


@pytest.mark.parametrize("path", _NOT_TESTS)
def test_a_source_file_that_merely_reads_like_a_test_is_still_scanned(path: str) -> None:
    """The globs need the dots. `latest.ts` is not `auth.test.ts`.

    An ignore list that over-matches is the opposite failure and a quieter one:
    nothing is reported, so nothing looks wrong, and the rules silently stop
    covering part of the tree.
    """
    assert not is_ignored(path, DEFAULT_IGNORES), f"a source file is being skipped: {path}"


def test_a_colocated_test_produces_no_findings_end_to_end(tmp_path) -> None:
    """The property that matters, measured the way a consumer experiences it.

    Asserted through `iter_source_files` rather than `is_ignored`, because the
    bug was invisible to anyone testing `scan_text` directly — that function
    never consults the ignore list, and an earlier sweep of this repository
    reported a file the scanner does not read.
    """
    src = tmp_path / "src"
    src.mkdir()
    exercises_a_rule = "localStorage.setItem('access_token', 'fake');\n"
    (src / "auth.test.ts").write_text(
        "it('rejects a token in storage', () => {\n  " + exercises_a_rule + "});\n",
        encoding="utf-8",
    )

    assert scan_paths(list(iter_source_files(tmp_path))) == []

    # The same line in a source file is still a finding — the fix skips test
    # files, it does not weaken the rule.
    (src / "auth.ts").write_text(exercises_a_rule, encoding="utf-8")
    findings = scan_paths(list(iter_source_files(tmp_path)))
    assert [f.anti_pattern for f in findings] == ["AP-S3.14a"], findings


# ── pruning, not filtering ───────────────────────────────────────────────────


def test_walk_files_prunes_rather_than_filters(tmp_path):
    """The difference between reading a repository and reading its dependencies.

    Measured on a Next.js monorepo: `root.rglob("*")` enumerated 104,536 entries
    in 6.4s where a pruned walk found 877 in 0.1s. Several probes each paid that
    separately, which is most of why `governova onboard` took nine minutes there.
    """
    from governova_checks import walk_files

    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.ts").write_text("x", encoding="utf-8")
    deps = tmp_path / "node_modules" / "left-pad"
    deps.mkdir(parents=True)
    (deps / "index.js").write_text("x", encoding="utf-8")

    found = {p.name for p in walk_files(tmp_path)}
    assert found == {"app.ts"}


def test_walk_files_does_not_prune_a_dotted_directory(tmp_path):
    """`.github/workflows` is authored, and several probes read it.

    Pruning every dotted directory would be the obvious shortcut and would turn
    satisfied standards into `unknown` — a probe cannot find a CI gate in a
    directory the walker refused to enter.
    """
    from governova_checks import walk_files

    wf = tmp_path / ".github" / "workflows"
    wf.mkdir(parents=True)
    (wf / "ci.yml").write_text("on: push\n", encoding="utf-8")

    assert "ci.yml" in {p.name for p in walk_files(tmp_path)}


def test_walk_files_skips_an_installed_dependency_tree_outside_a_venv(tmp_path):
    """`site-packages` is named as well as `.venv`.

    An installed tree is not always inside one — a system interpreter, a
    container image, or a virtualenv under a different name all put it somewhere
    `.venv` does not reach. The defect that made a fresh install report 50
    findings from other people's code was this directory.
    """
    from governova_checks import walk_files

    sp = tmp_path / "env" / "lib" / "site-packages" / "requests"
    sp.mkdir(parents=True)
    (sp / "api.py").write_text("x", encoding="utf-8")
    (tmp_path / "mine.py").write_text("x", encoding="utf-8")

    assert {p.name for p in walk_files(tmp_path)} == {"mine.py"}


def test_iter_source_files_selects_the_same_files_as_before(tmp_path):
    """The walker changed how the tree is enumerated, not which files count."""
    from governova_checks import iter_source_files

    (tmp_path / "a.ts").write_text("x", encoding="utf-8")
    (tmp_path / "b.min.js").write_text("x", encoding="utf-8")  # generated
    (tmp_path / "c.png").write_text("x", encoding="utf-8")  # not a text extension
    nm = tmp_path / "node_modules" / "dep"
    nm.mkdir(parents=True)
    (nm / "d.ts").write_text("x", encoding="utf-8")

    assert {p.name for p in iter_source_files(tmp_path)} == {"a.ts"}


def test_a_virtualenv_is_pruned_whatever_it_is_called(tmp_path):
    """`SKIP_DIRS` holds `.venv`, `venv` and `site-packages`, and the list cannot
    be finished — `.venv311`, `venv-dev`, `env` and `.direnv` all follow.

    Measured with the published 0.2.2 on a repository carrying two environments,
    `.venv` and `.venv-min`: the first was skipped, the second read as source,
    and its one blocking finding was a vendored bundle the reader cannot edit.

    A virtualenv is not a name. It is a directory containing `pyvenv.cfg`.
    """
    from governova_checks import walk_files

    for name in (".venv-min", ".venv311", "venv-dev", "env", "whatever"):
        env = tmp_path / name
        env.mkdir()
        (env / "pyvenv.cfg").write_text("home = /usr\n", encoding="utf-8")
        (env / "vendored.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "mine.py").write_text("x = 1\n", encoding="utf-8")

    assert {p.name for p in walk_files(tmp_path)} == {"mine.py"}


def test_a_directory_that_merely_looks_like_an_env_is_still_read(tmp_path):
    """The test is `pyvenv.cfg`, not the name. A source directory called `env/`
    holding configuration is authored code and must survive."""
    from governova_checks import walk_files

    src = tmp_path / "env"
    src.mkdir()
    (src / "settings.py").write_text("DEBUG = False\n", encoding="utf-8")

    assert {p.name for p in walk_files(tmp_path)} == {"settings.py"}
