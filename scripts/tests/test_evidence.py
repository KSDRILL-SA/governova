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
from governova_evidence import (
    PROBES,
    Verdict,
    probed_standards,
    run_probes,
    satisfied_standards,
)


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


def test_s931_a_team_named_as_owner_is_unowned(tmp_path) -> None:
    """Ownership by a group is ownership by nobody.

    Every member reasonably assumes another is watching, which is exactly the failure
    S9.31 exists to prevent — so a cell naming a team must not satisfy the probe.
    """
    from governova_evidence import Verdict, _probe_risk_ownership

    (tmp_path / "RISKS.md").write_text(
        "| Risk | Owner | Mitigation |\n"
        "|---|---|---|\n"
        "| Vendor outage | the platform team | failover |\n",
        encoding="utf-8",
    )
    assert _probe_risk_ownership(tmp_path).verdict is Verdict.VIOLATED


def test_s931_a_named_person_owns_the_risk(tmp_path) -> None:
    from governova_evidence import Verdict, _probe_risk_ownership

    (tmp_path / "RISKS.md").write_text(
        "| Risk | Owner | Mitigation | Trigger |\n"
        "|---|---|---|---|\n"
        "| Vendor outage | Thandi M | dual-region failover | error rate > 2% |\n",
        encoding="utf-8",
    )
    assert _probe_risk_ownership(tmp_path).verdict is Verdict.SATISFIED


def test_s931_absent_register_is_unknown(tmp_path) -> None:
    # A register may live in the tracker this engine never calls.
    from governova_evidence import Verdict, _probe_risk_ownership

    assert _probe_risk_ownership(tmp_path).verdict is Verdict.UNKNOWN


# A real register has more than one table — open risks above, closed below. That
# shape is what exposed the defect these two cover, and it is the ordinary shape,
# not a contrived one.
_TWO_TABLES = (
    "## Open\n\n"
    "| Risk | Owner | Mitigation |\n"
    "|---|---|---|\n"
    "| Vendor outage | the platform team | failover |\n"
    "| Key rotation | unassigned | scheduled |\n"
    "\n## Closed\n\n"
    "| Risk | Owner | Closed |\n"
    "|---|---|---|\n"
    "| Old advisory | Thandi M | 2026-08-20 |\n"
)


def test_s931_unowned_open_risks_are_not_excused_by_a_clean_closed_table(tmp_path) -> None:
    """The negative case, and the reason `_table_rows` reads the *first* table.

    An earlier form cleared its accumulator on every separator and so returned the
    **last** table. On a register shaped like the one above, it read one tidy closed
    row, reported `satisfied`, and never saw that both open risks named nobody.

    That is a false `satisfied` — the single failure this module exists to refuse —
    and it is invisible, because the probe reports a verdict either way.
    """
    from governova_evidence import Verdict, _probe_risk_ownership

    (tmp_path / "RISKS.md").write_text(_TWO_TABLES, encoding="utf-8")
    result = _probe_risk_ownership(tmp_path)
    assert result.verdict is Verdict.VIOLATED
    assert "2/2" in result.evidence, result.evidence


def test_table_rows_reads_the_first_table_not_the_last() -> None:
    """Stated directly, because the probe above can only observe it indirectly."""
    from governova_evidence import _table_rows

    rows = _table_rows(_TWO_TABLES)
    assert len(rows) == 2, rows
    assert rows[0][0] == "Vendor outage"
    assert all("Old advisory" not in cell for row in rows for cell in row)


def test_s932_an_estimate_with_no_actual_is_never_falsified(tmp_path) -> None:
    from governova_evidence import Verdict, _probe_estimate_calibration

    (tmp_path / "ESTIMATES.md").write_text(
        "| Item | Estimate | Actual |\n|---|---|---|\n| REQ-001 | 3-5d | — |\n",
        encoding="utf-8",
    )
    assert _probe_estimate_calibration(tmp_path).verdict is Verdict.VIOLATED


def test_s932_recorded_actuals_make_drift_computable(tmp_path) -> None:
    from governova_evidence import Verdict, _probe_estimate_calibration

    (tmp_path / "ESTIMATES.md").write_text(
        "| Item | Estimate | Actual |\n|---|---|---|\n| REQ-001 | 3-5d | 6d |\n| REQ-002 | 2d | 2d |\n",
        encoding="utf-8",
    )
    assert _probe_estimate_calibration(tmp_path).verdict is Verdict.SATISFIED


def test_s932_absent_record_is_unknown(tmp_path) -> None:
    from governova_evidence import Verdict, _probe_estimate_calibration

    assert _probe_estimate_calibration(tmp_path).verdict is Verdict.UNKNOWN


def _model_repo(tmp_path, *files: tuple[str, str]):
    docs = tmp_path / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    for name, body in files:
        path = docs / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    return tmp_path


def test_c12_absent_models_are_unknown_never_violated(tmp_path) -> None:
    """A team may model in a tool this engine cannot read. Absent is unassessed."""
    from governova_evidence import Verdict, run_probes

    verdicts = {r.standard: r.verdict for r in run_probes(tmp_path)}
    for sid in ("S12.1", "S12.2", "S12.3", "S12.7"):
        assert verdicts[sid] is Verdict.UNKNOWN, sid


def test_c12_diffable_models_satisfy_and_opaque_ones_do_not(tmp_path) -> None:
    from governova_evidence import (
        Verdict,
        _probe_models_are_diffable,
        _probe_models_versioned,
    )

    root = _model_repo(tmp_path, ("system-context.puml", "@startuml\n@enduml\n"))
    assert _probe_models_versioned(root).verdict is Verdict.SATISFIED
    assert _probe_models_are_diffable(root).verdict is Verdict.SATISFIED

    # An opaque model cannot be reviewed, so a change to it is never reviewed.
    (root / "docs" / "architecture.drawio").write_text("<mxfile/>", encoding="utf-8")
    assert _probe_models_are_diffable(root).verdict is Verdict.VIOLATED


def test_c12_a_mermaid_block_in_markdown_counts_as_a_model(tmp_path) -> None:
    # Most teams model in fenced diagrams inside docs rather than in a modelling tool,
    # and a probe that missed those would report `unknown` for repositories that are
    # in fact modelling.
    from governova_evidence import Verdict, _probe_models_versioned

    root = _model_repo(tmp_path, ("design.md", "# Design\n\n```mermaid\ngraph TD;\nA-->B;\n```\n"))
    assert _probe_models_versioned(root).verdict is Verdict.SATISFIED


def test_c12_boundary_model_is_recognised_by_name(tmp_path) -> None:
    from governova_evidence import Verdict, _probe_context_model

    named = _model_repo(tmp_path, ("system-context.puml", "@startuml\n@enduml\n"))
    assert _probe_context_model(named).verdict is Verdict.SATISFIED


def test_c12_models_without_a_boundary_are_unknown_not_violated(tmp_path) -> None:
    # The negative half: a boundary may be modelled inside a document whose filename
    # says nothing, so absence of the *name* is not evidence of absence of the model.
    from governova_evidence import Verdict, _probe_context_model

    unnamed = _model_repo(tmp_path, ("sequence-checkout.puml", "@startuml\n@enduml\n"))
    assert _probe_context_model(unnamed).verdict is Verdict.UNKNOWN


# ─── Repository facts the line scan cannot reach (#246) ──────────────────────
#
# Each probe below is shown satisfied, violated, and — where the question can
# fail to arise at all — undeterminable. The third case is the one that matters:
# a probe that guesses "satisfied" retires a standard nobody will look at again.


def test_s122_a_merge_commit_proves_squash_was_not_used(tmp_path) -> None:
    """A squash merge leaves one parent. Two parents is direct evidence."""
    from governova_evidence import Verdict, _probe_squash_merge

    _git_repo(tmp_path, ["feat: one"])
    subprocess.run(["git", "checkout", "-q", "-b", "side"], cwd=tmp_path, check=True)
    (tmp_path / "side.txt").write_text("x", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "feat: two"], cwd=tmp_path, check=True)
    subprocess.run(["git", "checkout", "-q", "-"], cwd=tmp_path, check=True)
    (tmp_path / "main.txt").write_text("y", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "feat: three"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "merge", "--no-ff", "-q", "-m", "Merge side", "side"], cwd=tmp_path, check=True
    )

    verdict, evidence = _probe_squash_merge(tmp_path).verdict, _probe_squash_merge(tmp_path).evidence
    assert verdict is Verdict.VIOLATED
    # The offending commit is named. "History is not linear" is not actionable.
    assert "Merge side" in evidence


def test_s122_linear_history_satisfies_the_squash_strategy(tmp_path) -> None:
    from governova_evidence import Verdict, _probe_squash_merge

    _git_repo(tmp_path, ["feat: one", "fix: two"])
    assert _probe_squash_merge(tmp_path).verdict is Verdict.SATISFIED


def test_s122_is_unknown_without_git(tmp_path) -> None:
    from governova_evidence import Verdict, _probe_squash_merge

    assert _probe_squash_merge(tmp_path).verdict is Verdict.UNKNOWN


def test_s142_a_save_point_is_not_a_change(tmp_path) -> None:
    from governova_evidence import Verdict, _probe_purposeful_commits

    _git_repo(tmp_path, ["feat: real work", "wip", "checkpoint"])
    result = _probe_purposeful_commits(tmp_path)
    assert result.verdict is Verdict.VIOLATED
    assert "wip" in result.evidence


def test_s142_purposeful_subjects_satisfy(tmp_path) -> None:
    from governova_evidence import Verdict, _probe_purposeful_commits

    _git_repo(tmp_path, ["feat: add the gate", "fix: correct the citation"])
    assert _probe_purposeful_commits(tmp_path).verdict is Verdict.SATISFIED


def test_s117_a_pipeline_that_only_runs_on_prs_leaves_main_unverified(tmp_path) -> None:
    """The branch everyone deploys from must not be the one nothing checks."""
    from governova_evidence import Verdict, _probe_ci_on_main

    _workflow(tmp_path, "on:\n  pull_request:\n    branches: [main]\njobs:\n  t:\n    steps: []\n")
    assert _probe_ci_on_main(tmp_path).verdict is Verdict.VIOLATED


def test_s117_a_push_to_main_trigger_satisfies(tmp_path) -> None:
    from governova_evidence import Verdict, _probe_ci_on_main

    _workflow(
        tmp_path,
        "on:\n  push:\n    branches: [main]\n  pull_request:\njobs:\n  t:\n    steps: []\n",
    )
    assert _probe_ci_on_main(tmp_path).verdict is Verdict.SATISFIED


def test_s117_is_unknown_with_no_workflows(tmp_path) -> None:
    from governova_evidence import Verdict, _probe_ci_on_main

    assert _probe_ci_on_main(tmp_path).verdict is Verdict.UNKNOWN


def test_s146_a_missing_pr_template_is_violated_not_unknown(tmp_path) -> None:
    """Absence is the answer here, not an inability to answer.

    A repository either carries the template or it does not, and the file is
    where it would be. That is a determination, so `unknown` would be a dodge.
    """
    from governova_evidence import Verdict, _probe_pr_template

    assert _probe_pr_template(tmp_path).verdict is Verdict.VIOLATED


def test_s146_an_empty_pr_template_imposes_no_structure(tmp_path) -> None:
    from governova_evidence import Verdict, _probe_pr_template

    (tmp_path / ".github").mkdir()
    (tmp_path / ".github" / "pull_request_template.md").write_text("\n", encoding="utf-8")
    assert _probe_pr_template(tmp_path).verdict is Verdict.VIOLATED


def test_s146_a_real_pr_template_satisfies(tmp_path) -> None:
    from governova_evidence import Verdict, _probe_pr_template

    (tmp_path / ".github").mkdir()
    (tmp_path / ".github" / "pull_request_template.md").write_text(
        "## What changed\n\n## Constitutional compliance\n\n## Verification\n",
        encoding="utf-8",
    )
    assert _probe_pr_template(tmp_path).verdict is Verdict.SATISFIED


def test_s129_issue_templates_satisfy_and_their_absence_violates(tmp_path) -> None:
    from governova_evidence import Verdict, _probe_issue_template

    assert _probe_issue_template(tmp_path).verdict is Verdict.VIOLATED
    directory = tmp_path / ".github" / "ISSUE_TEMPLATE"
    directory.mkdir(parents=True)
    (directory / "feature.md").write_text("## Problem\n## Gate questions\n", encoding="utf-8")
    assert _probe_issue_template(tmp_path).verdict is Verdict.SATISFIED


def test_s173_a_line_length_in_prose_is_not_configuration(tmp_path) -> None:
    """S1.73 closes with *never manually managed*, so a number nobody reads fails."""
    from governova_evidence import Verdict, _probe_line_length_configured

    (tmp_path / "app.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("Lines are 88 characters.\n", encoding="utf-8")
    assert _probe_line_length_configured(tmp_path).verdict is Verdict.VIOLATED


def test_s173_tool_configuration_satisfies(tmp_path) -> None:
    from governova_evidence import Verdict, _probe_line_length_configured

    (tmp_path / "app.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text(
        "[tool.ruff]\nline-length = 88\n", encoding="utf-8"
    )
    assert _probe_line_length_configured(tmp_path).verdict is Verdict.SATISFIED


def test_s173_is_unknown_when_neither_language_is_present(tmp_path) -> None:
    """A standard naming two languages does not arise in a repository with neither."""
    from governova_evidence import Verdict, _probe_line_length_configured

    (tmp_path / "main.go").write_text("package main\n", encoding="utf-8")
    assert _probe_line_length_configured(tmp_path).verdict is Verdict.UNKNOWN


def test_s173_typescript_alone_still_needs_its_half(tmp_path) -> None:
    from governova_evidence import Verdict, _probe_line_length_configured

    (tmp_path / "app.ts").write_text("const a = 1;\n", encoding="utf-8")
    assert _probe_line_length_configured(tmp_path).verdict is Verdict.VIOLATED
    (tmp_path / ".editorconfig").write_text("[*.ts]\nmax_line_length = 100\n", encoding="utf-8")
    assert _probe_line_length_configured(tmp_path).verdict is Verdict.SATISFIED


def test_s174_import_order_must_be_automated(tmp_path) -> None:
    from governova_evidence import Verdict, _probe_import_order_automated

    (tmp_path / "app.py").write_text("import os\n", encoding="utf-8")
    assert _probe_import_order_automated(tmp_path).verdict is Verdict.VIOLATED
    (tmp_path / "pyproject.toml").write_text(
        '[tool.ruff.lint]\nselect = ["E", "I"]\n', encoding="utf-8"
    )
    assert _probe_import_order_automated(tmp_path).verdict is Verdict.SATISFIED


def test_s174_is_unknown_when_nothing_has_imports(tmp_path) -> None:
    from governova_evidence import Verdict, _probe_import_order_automated

    (tmp_path / "notes.md").write_text("nothing here\n", encoding="utf-8")
    assert _probe_import_order_automated(tmp_path).verdict is Verdict.UNKNOWN


def test_s89_ci_must_exist_to_run_anything(tmp_path) -> None:
    from governova_evidence import Verdict, _probe_ci_exists

    assert _probe_ci_exists(tmp_path).verdict is Verdict.VIOLATED
    _workflow(tmp_path, "on: push\njobs:\n  t:\n    steps: []\n")
    assert _probe_ci_exists(tmp_path).verdict is Verdict.SATISFIED


def test_s813_an_uncached_pipeline_is_violated(tmp_path) -> None:
    from governova_evidence import Verdict, _probe_ci_dependency_cache

    _workflow(tmp_path, "on: push\njobs:\n  t:\n    steps:\n      - run: npm ci\n")
    assert _probe_ci_dependency_cache(tmp_path).verdict is Verdict.VIOLATED


def test_s813_a_cached_pipeline_satisfies(tmp_path) -> None:
    from governova_evidence import Verdict, _probe_ci_dependency_cache

    _workflow(
        tmp_path,
        "on: push\njobs:\n  t:\n    steps:\n"
        "      - uses: actions/cache@v4\n      - run: npm ci\n",
    )
    assert _probe_ci_dependency_cache(tmp_path).verdict is Verdict.SATISFIED


def test_s813_is_unknown_with_no_ci(tmp_path) -> None:
    from governova_evidence import Verdict, _probe_ci_dependency_cache

    assert _probe_ci_dependency_cache(tmp_path).verdict is Verdict.UNKNOWN


def test_s861_runbooks_are_found_where_they_are_actually_kept(tmp_path) -> None:
    """The standard names `runbooks/`; a governance directory satisfies its substance.

    Reporting a repository as violating over a path prefix is a false accusation,
    and a governance tool that makes those does not get a second reading.
    """
    from governova_evidence import Verdict, _probe_runbooks

    assert _probe_runbooks(tmp_path).verdict is Verdict.VIOLATED
    directory = tmp_path / "governance" / "runbooks"
    directory.mkdir(parents=True)
    (directory / "RB-01-sev0-response.md").write_text("steps\n", encoding="utf-8")
    # SEV1 still missing — a partial set is not the set the standard names.
    assert _probe_runbooks(tmp_path).verdict is Verdict.VIOLATED
    (directory / "RB-02-sev1-response.md").write_text("steps\n", encoding="utf-8")
    assert _probe_runbooks(tmp_path).verdict is Verdict.SATISFIED


def test_s861_a_readme_is_not_a_runbook(tmp_path) -> None:
    from governova_evidence import Verdict, _probe_runbooks

    directory = tmp_path / "runbooks"
    directory.mkdir()
    (directory / "README.md").write_text("what runbooks are\n", encoding="utf-8")
    assert _probe_runbooks(tmp_path).verdict is Verdict.VIOLATED


def test_s878_a_template_missing_fields_is_violated(tmp_path) -> None:
    from governova_evidence import Verdict, _probe_post_mortem_template

    (tmp_path / "templates").mkdir()
    (tmp_path / "templates" / "post-mortem-template.md").write_text(
        "# Post-mortem\n## Severity\n## Timeline\n", encoding="utf-8"
    )
    result = _probe_post_mortem_template(tmp_path)
    assert result.verdict is Verdict.VIOLATED
    assert "root cause" in result.evidence


def test_s878_a_complete_template_satisfies(tmp_path) -> None:
    from governova_evidence import Verdict, _probe_post_mortem_template

    (tmp_path / "templates").mkdir()
    (tmp_path / "templates" / "post-mortem-template.md").write_text(
        "# Post-mortem\n## Severity\n## Detection\n## Resolution\n"
        "## Incident commander\n## Impact\n## Timeline\n"
        "## Root cause (5 Whys)\n## Action items\n",
        encoding="utf-8",
    )
    assert _probe_post_mortem_template(tmp_path).verdict is Verdict.SATISFIED


def test_s886_a_vendor_list_without_an_exit_plan_is_violated(tmp_path) -> None:
    """S8.86 asks for two things. Listing vendors answers only the first."""
    from governova_evidence import Verdict, _probe_vendor_register

    (tmp_path / "governance").mkdir()
    (tmp_path / "governance" / "vendors.md").write_text(
        "| Vendor | Data held | SLA |\n|---|---|---|\n| Acme | invoices | 99.9% |\n",
        encoding="utf-8",
    )
    assert _probe_vendor_register(tmp_path).verdict is Verdict.VIOLATED


def test_s886_a_register_with_an_exit_plan_satisfies(tmp_path) -> None:
    from governova_evidence import Verdict, _probe_vendor_register

    (tmp_path / "governance").mkdir()
    (tmp_path / "governance" / "vendors.md").write_text(
        "| Vendor | Data held | SLA | Exit plan |\n|---|---|---|---|\n"
        "| Acme | invoices | 99.9% | export monthly, restore to self-hosted |\n",
        encoding="utf-8",
    )
    assert _probe_vendor_register(tmp_path).verdict is Verdict.SATISFIED


def test_a_probe_never_returns_satisfied_from_an_empty_directory(tmp_path) -> None:
    """The rule the whole tier rests on, asserted across every probe at once.

    An empty directory is the strongest case: nothing is present, so nothing can
    be evidence. Any probe claiming SATISFIED here is guessing, and a false
    satisfied silently retires a standard nobody will examine again.
    """
    from governova_evidence import Verdict, run_probes

    guessing = [r.standard for r in run_probes(tmp_path) if r.verdict is Verdict.SATISFIED]
    assert not guessing, f"probe(s) claimed satisfied with no evidence present: {guessing}"


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
    # Verifies REQ-002 — a check that cannot determine an answer reports unknown.
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


def test_a_short_history_is_not_described_as_a_window(tmp_path: Path) -> None:
    """Disclosure must not become its own falsehood.

    A repository with three commits has no history outside the frame, so claiming
    the verdict covers "the last 50" would invent an exclusion that does not exist.
    """
    _git_repo(tmp_path, ["feat: one", "fix: two", "docs: three"])
    _, evidence = _probe(tmp_path, "S1.19")
    assert "all 3 commit(s) in history" in evidence
    assert "not inspected" not in evidence


def test_a_full_window_declares_what_it_did_not_read() -> None:
    """The frame is stated whenever the window could be hiding something.

    `50/50 conventional` was true while a non-conforming commit sat at index 53.
    True, and leaving the reader with a false impression — which is what #213 is.
    """
    from governova_evidence import (
        _CONVENTIONAL_WINDOW,
        _MAINTENANCE_WINDOW,
        _window_note,
    )

    note = _window_note(_CONVENTIONAL_WINDOW, _CONVENTIONAL_WINDOW)
    assert "the last 50" in note
    assert "earlier history is not inspected" in note
    # The two windows differ on purpose, and that difference is why one probe can
    # report 100% conventional while the other names the commit that is not.
    assert _CONVENTIONAL_WINDOW != _MAINTENANCE_WINDOW


# ─── S13.4 — maintenance classification ──────────────────────────────────────


def test_maintenance_classification_satisfied(tmp_path: Path) -> None:
    """A verdict at all is the point: this probe raised `IndexError` on every match.

    `_CONVENTIONAL` held its type in a non-capturing group while the probe read
    `match.group(1)`, so any subject that matched raised and any subject that did not
    was counted unclassified. The probe could not reach `satisfied` by any input, and
    the error surfaced as `undetermined` — which is the correct thing to do with an
    error, and is exactly why it went unnoticed for so long.
    """
    _git_repo(tmp_path, ["fix: correct a thing", "feat: add a thing", "refactor: tidy up"])
    verdict, evidence = _probe(tmp_path, "S13.4")
    assert verdict is Verdict.SATISFIED
    assert "corrective 1" in evidence
    assert "perfective 1" in evidence
    assert "preventive 1" in evidence


def test_maintenance_classification_violated(tmp_path: Path) -> None:
    """The negative case: a type outside the standard is unclassifiable, not adaptive."""
    _git_repo(tmp_path, ["feat: a real one", "harden: security review of the engine"])
    verdict, evidence = _probe(tmp_path, "S13.4")
    assert verdict is Verdict.VIOLATED
    assert "1/2" in evidence


def test_maintenance_classification_unknown_without_git(tmp_path: Path) -> None:
    verdict, evidence = _probe(tmp_path, "S13.4")
    assert verdict is Verdict.UNKNOWN
    assert "git" in evidence or "no commits" in evidence


def test_every_maintenance_key_is_a_type_the_standard_permits() -> None:
    """The map and the pattern must not drift apart.

    A key `_CONVENTIONAL` never matches is unreachable: the class it names can never
    be assigned, and nothing fails to say so. `build` was such a key — `S1.19` does not
    permit that type — and it sat there classifying nothing.
    """
    from governova_evidence import _CONVENTIONAL, _MAINTENANCE_CLASS

    unreachable = [k for k in _MAINTENANCE_CLASS if not _CONVENTIONAL.match(f"{k}: a subject")]
    assert unreachable == [], f"maintenance classes no rule can reach: {unreachable}"


def test_the_conventional_pattern_exposes_the_type_it_matched() -> None:
    """The probe reads the type back by name, so the group must exist and be named."""
    from governova_evidence import _CONVENTIONAL

    assert _CONVENTIONAL.groupindex.get("type") is not None, "the type group must stay named"
    assert _CONVENTIONAL.match("fix(auth)!: drop the check").group("type") == "fix"


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


# ─── S7.25 — the coverage threshold ──────────────────────────────────────────


def test_coverage_gate_satisfied_from_the_command_line(tmp_path: Path) -> None:
    _workflow(
        tmp_path,
        "on:\n  pull_request:\njobs:\n  a:\n    steps:\n"
        "      - run: pytest -q --cov --cov-fail-under=80\n",
    )
    assert _probe(tmp_path, "S7.25")[0] is Verdict.SATISFIED


def test_coverage_gate_satisfied_from_configuration(tmp_path: Path) -> None:
    """The threshold is as real in `pyproject.toml` as it is on the command line."""
    _workflow(tmp_path, "on:\n  pull_request:\njobs:\n  a:\n    steps:\n      - run: pytest -q\n")
    (tmp_path / "pyproject.toml").write_text(
        "[tool.coverage.report]\nfail_under = 80\n", encoding="utf-8"
    )
    assert _probe(tmp_path, "S7.25")[0] is Verdict.SATISFIED


def test_measuring_coverage_without_a_threshold_is_a_violation(tmp_path: Path) -> None:
    """The distinction the standard turns on, and the one worth testing.

    `--cov` produces a number. `S7.25` is specifically *"dropping below these
    thresholds fails the build"*, so a measured percentage nobody is held to is
    exactly the situation the standard exists to name — and it is the situation
    this repository was in when the probe was written.
    """
    _workflow(
        tmp_path,
        "on:\n  pull_request:\njobs:\n  a:\n    steps:\n      - run: pytest -q --cov=src\n",
    )
    verdict, evidence = _probe(tmp_path, "S7.25")
    assert verdict is Verdict.VIOLATED
    assert "no coverage threshold" in evidence


def test_coverage_gate_unknown_without_ci(tmp_path: Path) -> None:
    assert _probe(tmp_path, "S7.25")[0] is Verdict.UNKNOWN


def test_coverage_gate_unknown_when_ci_runs_no_tests(tmp_path: Path) -> None:
    """A repository whose CI runs no tests has no coverage to gate.

    Reporting that as a violation would answer a question nobody asked, and it
    would double-count the failure `S7.6` already reports.
    """
    _workflow(tmp_path, "on:\n  pull_request:\njobs:\n  a:\n    steps:\n      - run: make build\n")
    verdict, evidence = _probe(tmp_path, "S7.25")
    assert verdict is Verdict.UNKNOWN
    assert "no tests" in evidence


def test_this_repository_gates_its_own_coverage(tmp_path: Path) -> None:
    """The probe found this repository violating, and the violation was real.

    Coverage was measured by nobody and gated by nothing. The threshold is now
    `fail_under = 80` — the number `S7.25` sets, not a comfortable one.
    """
    assert _probe(resolve_repo_root(), "S7.25")[0] is Verdict.SATISFIED


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
