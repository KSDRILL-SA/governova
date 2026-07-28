"""Tests for the structural evidence probes.

Each probe gets three cases: satisfied, violated, and **undeterminable**. The
third is the one that matters. A probe that guesses "satisfied" when it cannot
tell inflates coverage and silently retires a standard nobody will look at again,
so every probe must be shown to say `unknown` rather than assume.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from governova_checks.rules import scan_text
from governova_compile.discovery import resolve_repo_root
from governova_compile.writer import load_index
from governova_evidence import PROBES, Verdict, probed_standards, run_probes, satisfied_standards


def _probe(root: Path, standard: str) -> tuple[Verdict, str]:
    result = next(r for r in run_probes(root) if r.standard == standard)
    return result.verdict, result.evidence


def _workflow(root: Path, body: str) -> None:
    wf = root / ".github" / "workflows"
    wf.mkdir(parents=True, exist_ok=True)
    (wf / "ci.yml").write_text(body, encoding="utf-8")


def _git_repo(root: Path, subjects: list[str]) -> None:
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=root, check=True)
    for i, subject in enumerate(subjects):
        (root / f"f{i}.txt").write_text("x", encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=root, check=True)
        subprocess.run(["git", "commit", "-q", "-m", subject], cwd=root, check=True)


# ─── Governance of the probe set ─────────────────────────────────────────────


def test_every_probe_binds_a_standard_that_exists() -> None:
    """A probe citing a non-existent standard is as ungrounded as a stray rule."""
    root = resolve_repo_root()
    index = load_index(root / "compiled" / "constitution.json")
    known = {s.id for c in index.constitutions for s in c.standards}
    assert probed_standards() <= known


def test_probe_standards_are_unique() -> None:
    ids = [p.standard for p in PROBES]
    assert len(set(ids)) == len(ids)


def test_a_probe_that_raises_is_unknown_never_satisfied() -> None:
    from governova_evidence import Probe, ProbeResult

    def explode(_: Path) -> ProbeResult:
        raise RuntimeError("boom")

    broken = Probe("S1.1", "t", explode)
    original = PROBES
    try:
        import governova_evidence as mod

        mod.PROBES = (broken,)  # type: ignore[misc]
        result = run_probes(Path("."))
        assert result[0].verdict is Verdict.UNKNOWN
        assert not result[0].satisfied
    finally:
        import governova_evidence as mod

        mod.PROBES = original  # type: ignore[misc]


def test_an_empty_directory_yields_no_satisfied_standards(tmp_path: Path) -> None:
    """Nothing present must never read as compliant."""
    assert satisfied_standards(tmp_path) == set()


# ─── S1.19 — conventional commits ────────────────────────────────────────────


def test_conventional_commits_satisfied(tmp_path: Path) -> None:
    _git_repo(tmp_path, ["feat: add a thing", "fix(auth): correct the check", "docs: update"])
    verdict, evidence = _probe(tmp_path, "S1.19")
    assert verdict is Verdict.SATISFIED
    assert "100%" in evidence


def test_conventional_commits_violated(tmp_path: Path) -> None:
    _git_repo(tmp_path, ["feat: good one", "updated some stuff"])
    verdict, evidence = _probe(tmp_path, "S1.19")
    assert verdict is Verdict.VIOLATED
    assert "updated some stuff" in evidence


def test_conventional_commits_unknown_without_git(tmp_path: Path) -> None:
    verdict, evidence = _probe(tmp_path, "S1.19")
    assert verdict is Verdict.UNKNOWN
    assert "git" in evidence or "no commits" in evidence


# ─── S1.70 / S7.6 — CI enforcement ───────────────────────────────────────────


def test_lint_in_ci_satisfied(tmp_path: Path) -> None:
    _workflow(tmp_path, "on: [pull_request]\njobs:\n  a:\n    steps:\n      - run: ruff check src/\n")
    assert _probe(tmp_path, "S1.70")[0] is Verdict.SATISFIED


def test_lint_in_ci_violated_when_ci_exists_without_lint(tmp_path: Path) -> None:
    _workflow(tmp_path, "on: [pull_request]\njobs:\n  a:\n    steps:\n      - run: echo hi\n")
    assert _probe(tmp_path, "S1.70")[0] is Verdict.VIOLATED


def test_lint_in_ci_unknown_without_any_ci(tmp_path: Path) -> None:
    """No CI is not a lint violation — it is a question this probe cannot answer."""
    assert _probe(tmp_path, "S1.70")[0] is Verdict.UNKNOWN


def test_tests_in_ci_satisfied(tmp_path: Path) -> None:
    _workflow(tmp_path, "on:\n  pull_request:\njobs:\n  a:\n    steps:\n      - run: pytest -q\n")
    assert _probe(tmp_path, "S7.6")[0] is Verdict.SATISFIED


def test_tests_in_ci_violated(tmp_path: Path) -> None:
    _workflow(tmp_path, "on:\n  pull_request:\njobs:\n  a:\n    steps:\n      - run: make build\n")
    assert _probe(tmp_path, "S7.6")[0] is Verdict.VIOLATED


def test_tests_in_ci_unknown_without_pull_request_trigger(tmp_path: Path) -> None:
    _workflow(tmp_path, "on:\n  schedule:\n    - cron: '0 9 * * *'\njobs:\n  a:\n    steps: []\n")
    assert _probe(tmp_path, "S7.6")[0] is Verdict.UNKNOWN


# ─── S1.71 — pre-commit hooks ────────────────────────────────────────────────


def test_pre_commit_satisfied_by_either_toolchain(tmp_path: Path) -> None:
    (tmp_path / ".pre-commit-config.yaml").write_text("repos: []", encoding="utf-8")
    assert _probe(tmp_path, "S1.71")[0] is Verdict.SATISFIED

    other = tmp_path / "node"
    (other / ".husky").mkdir(parents=True)
    (other / ".husky" / "pre-commit").write_text("lint-staged", encoding="utf-8")
    assert _probe(other, "S1.71")[0] is Verdict.SATISFIED


def test_pre_commit_violated_when_absent(tmp_path: Path) -> None:
    assert _probe(tmp_path, "S1.71")[0] is Verdict.VIOLATED


def test_an_empty_husky_directory_does_not_satisfy(tmp_path: Path) -> None:
    (tmp_path / ".husky").mkdir()
    assert _probe(tmp_path, "S1.71")[0] is Verdict.VIOLATED


# ─── S1.84 — README ──────────────────────────────────────────────────────────


def test_readme_satisfied(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text(
        "# App\n\n## What it does\nPurpose here.\n\n## Setup\nInstall steps.\n", encoding="utf-8"
    )
    assert _probe(tmp_path, "S1.84")[0] is Verdict.SATISFIED


def test_readme_violated_when_missing_setup(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# App\n\nPurpose only.\n", encoding="utf-8")
    verdict, evidence = _probe(tmp_path, "S1.84")
    assert verdict is Verdict.VIOLATED and "setup" in evidence


def test_readme_violated_when_absent(tmp_path: Path) -> None:
    assert _probe(tmp_path, "S1.84")[0] is Verdict.VIOLATED


# ─── S1.85 — ADRs ────────────────────────────────────────────────────────────


def test_adrs_satisfied(tmp_path: Path) -> None:
    d = tmp_path / "governance" / "decisions"
    d.mkdir(parents=True)
    (d / "ADR-001-stack.md").write_text("x", encoding="utf-8")
    assert _probe(tmp_path, "S1.85")[0] is Verdict.SATISFIED


def test_the_adr_template_alone_does_not_satisfy(tmp_path: Path) -> None:
    """Scaffolding is not a decision."""
    d = tmp_path / "governance" / "decisions"
    d.mkdir(parents=True)
    (d / "ADR-000-template.md").write_text("x", encoding="utf-8")
    assert _probe(tmp_path, "S1.85")[0] is Verdict.VIOLATED


# ─── S1.98 — reproducible installs ───────────────────────────────────────────


def test_frozen_install_satisfied(tmp_path: Path) -> None:
    (tmp_path / "uv.lock").write_text("x", encoding="utf-8")
    _workflow(tmp_path, "jobs:\n  a:\n    steps:\n      - run: uv sync --frozen\n")
    verdict, evidence = _probe(tmp_path, "S1.98")
    assert verdict is Verdict.SATISFIED and "uv.lock" in evidence


def test_lockfile_without_a_frozen_ci_install_is_violated(tmp_path: Path) -> None:
    (tmp_path / "package-lock.json").write_text("{}", encoding="utf-8")
    _workflow(tmp_path, "jobs:\n  a:\n    steps:\n      - run: npm install\n")
    assert _probe(tmp_path, "S1.98")[0] is Verdict.VIOLATED


def test_no_lockfile_is_violated(tmp_path: Path) -> None:
    assert _probe(tmp_path, "S1.98")[0] is Verdict.VIOLATED


def test_lockfile_without_ci_is_unknown_not_satisfied(tmp_path: Path) -> None:
    """Half the requirement met is not the requirement met."""
    (tmp_path / "uv.lock").write_text("x", encoding="utf-8")
    assert _probe(tmp_path, "S1.98")[0] is Verdict.UNKNOWN


# ─── S8.25 — environment hygiene ─────────────────────────────────────────────


def test_env_hygiene_satisfied(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text(".env\n", encoding="utf-8")
    (tmp_path / ".env.example").write_text("API_URL=\n", encoding="utf-8")
    assert _probe(tmp_path, "S8.25")[0] is Verdict.SATISFIED


def test_env_not_gitignored_is_violated(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text("node_modules/\n", encoding="utf-8")
    assert _probe(tmp_path, "S8.25")[0] is Verdict.VIOLATED


def test_missing_env_example_is_unknown_not_violated(tmp_path: Path) -> None:
    """A project may legitimately need no environment variables."""
    (tmp_path / ".gitignore").write_text(".env\n", encoding="utf-8")
    assert _probe(tmp_path, "S8.25")[0] is Verdict.UNKNOWN


# ─── Regression: the false positive that prompted path-scoping the TS rules ──


def test_pythons_any_builtin_is_not_a_typescript_any_annotation() -> None:
    """`: any` is a TypeScript annotation; Python's `any(...)` is a builtin call.

    Matching it everywhere flagged real Python dict literals — a false positive on
    a rule that reaches the enforcer.
    """
    code = 'x = {"k": any(c in s for c in cs)}'
    assert not [f for f in scan_text(code, file="src/probe.py") if f.anti_pattern == "AP-S1.49a"]


def test_the_typescript_any_rules_still_fire_where_they_should() -> None:
    assert list(scan_text("let x: any = 1;", file="src/a.ts"))
    assert list(scan_text("const y = z as any;", file="src/a.vue"))


def test_this_repository_scans_clean() -> None:
    from governova_checks import iter_source_files, scan_paths

    root = resolve_repo_root()
    findings = scan_paths(list(iter_source_files(root)))
    assert not findings, f"self-scan regressed: {[(f.anti_pattern, f.file) for f in findings]}"
