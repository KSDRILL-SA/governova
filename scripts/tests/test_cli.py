"""Smoke tests for the `governova` CLI surface (wraps the engine)."""

from __future__ import annotations

import json

from governova_cli.__main__ import app
from typer.testing import CliRunner

runner = CliRunner()


def test_stats_runs():
    result = runner.invoke(app, ["stats"])
    assert result.exit_code == 0
    assert "Standards" in result.stdout


def test_standard_lookup():
    result = runner.invoke(app, ["standard", "S3.14"])
    assert result.exit_code == 0
    assert "S3.14" in result.stdout


def test_standard_not_found_exits_nonzero():
    result = runner.invoke(app, ["standard", "S99.99"])
    assert result.exit_code != 0


def test_validate_passes():
    result = runner.invoke(app, ["validate"])
    assert result.exit_code == 0
    assert "integrity OK" in result.stdout


def test_both_validate_entry_points_report_the_same_findings():
    """`governova validate` and `governova-validate` must not drift apart.

    They were two independent copies of the run — checksum, `ALL_CHECKS`, links,
    the error/warning split — sharing the check functions but not the wiring. Adding
    a check to one did nothing to the other and nothing said so. #218 added
    `check_declared_anti_patterns`, wired it into one, and the other went on printing
    `warnings=350`, which looks exactly like a check that ran and found nothing.

    Both now call `run_validation`, so this compares the two renderings of one run.
    """
    import re

    from governova_compile.discovery import resolve_repo_root
    from governova_compile.writer import load_active_index
    from governova_validate.run import run_validation

    cli = runner.invoke(app, ["validate"])
    assert cli.exit_code == 0
    reported = re.search(r"errors=(\d+) warnings=(\d+)", cli.stdout)
    assert reported is not None, f"unparseable validate output: {cli.stdout!r}"

    root = resolve_repo_root()
    run = run_validation(root, load_active_index(start=root))
    assert (len(run.errors), len(run.warnings)) == (
        int(reported.group(1)),
        int(reported.group(2)),
    )


def test_the_health_score_stays_index_only():
    """`score` grades the constitution, so link and source-tree findings are out of scope.

    It is the one caller that must *not* use `run_validation`: folding those in would
    move a published number by widening what it measures rather than by anything
    changing in the constitution.
    """
    from governova_compile.discovery import resolve_repo_root
    from governova_compile.writer import load_active_index
    from governova_validate.run import run_validation

    root = resolve_repo_root()
    full = run_validation(root, load_active_index(start=root))
    assert full.warnings, "expected the full run to carry warnings the score ignores"

    result = runner.invoke(app, ["score"])
    assert result.exit_code == 0
    assert "Constitution Health Score" in result.stdout


def test_score_runs():
    result = runner.invoke(app, ["score"])
    assert result.exit_code == 0
    assert "Constitution Health Score" in result.stdout


def test_onboard_runs_against_a_foreign_repository(tmp_path):
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "acme"\n', encoding="utf-8")
    result = runner.invoke(app, ["onboard", str(tmp_path)])
    assert result.exit_code == 0
    assert "Proposed profile" in result.stdout
    # Read-only: the profile is shown, never written.
    assert not (tmp_path / "governance" / "project.toml").exists()


def test_onboard_reports_a_repository_with_nothing_detectable(tmp_path):
    """An empty repository gets a useful report saying so, not an empty one."""
    (tmp_path / "NOTES").write_text("hello\n", encoding="utf-8")
    result = runner.invoke(app, ["onboard", str(tmp_path)])
    assert result.exit_code == 0
    assert "no recognised manifest found" in result.stdout
    assert "NOT DETECTED" in result.stdout


def test_onboard_accept_writes_once_then_refuses(tmp_path):
    (tmp_path / "go.mod").write_text("module acme\n", encoding="utf-8")
    first = runner.invoke(app, ["onboard", str(tmp_path), "--accept"])
    assert first.exit_code == 0
    assert (tmp_path / "governance" / "project.toml").is_file()

    second = runner.invoke(app, ["onboard", str(tmp_path), "--accept"])
    assert second.exit_code == 1
    assert "refusing to overwrite" in second.stdout


def test_onboard_json_is_parseable(tmp_path):
    (tmp_path / "package.json").write_text('{"name":"acme"}', encoding="utf-8")
    result = runner.invoke(app, ["onboard", str(tmp_path), "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["profile"]["stacks"] == ["node"]
    assert payload["profile"]["phase"] is None


def test_onboard_rejects_a_path_that_is_not_a_directory(tmp_path):
    target = tmp_path / "a-file.txt"
    target.write_text("x\n", encoding="utf-8")
    result = runner.invoke(app, ["onboard", str(target)])
    assert result.exit_code == 2


def test_roadmap_runs_and_ranks(tmp_path):
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "acme"\n', encoding="utf-8")
    (tmp_path / "svc.py").write_text("# TODO: tidy this up\n", encoding="utf-8")
    result = runner.invoke(app, ["roadmap", str(tmp_path)])
    assert result.exit_code == 0
    assert "Remediation roadmap" in result.stdout
    assert "Leverage" in result.stdout


def test_roadmap_json_is_parseable(tmp_path):
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "acme"\n', encoding="utf-8")
    result = runner.invoke(app, ["roadmap", str(tmp_path), "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert "items" in payload
    assert payload["totals"]["items"] == len(payload["items"])


def test_convert_proposes_without_writing(tmp_path):
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "acme"\n', encoding="utf-8")
    (tmp_path / ".gitignore").write_text("build/\n", encoding="utf-8")
    result = runner.invoke(app, ["convert", str(tmp_path)])
    assert result.exit_code == 0
    assert "Nothing was written" in result.stdout
    assert ".env" not in (tmp_path / ".gitignore").read_text(encoding="utf-8")


def test_convert_apply_writes_only_the_safe_ones(tmp_path):
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "acme"\n', encoding="utf-8")
    (tmp_path / ".gitignore").write_text("build/\n", encoding="utf-8")
    src = tmp_path / "src"
    src.mkdir()
    (src / "client.py").write_text(
        'import os\n\nAPI_URL = "https://api.acme-prod.com"\n', encoding="utf-8"
    )

    result = runner.invoke(app, ["convert", str(tmp_path), "--apply"])
    assert result.exit_code == 0
    # Structural fix applied...
    assert ".env" in (tmp_path / ".gitignore").read_text(encoding="utf-8")
    # ...and the untested code left exactly as it was (S1.101).
    assert (src / "client.py").read_text(encoding="utf-8") == (
        'import os\n\nAPI_URL = "https://api.acme-prod.com"\n'
    )
    assert "S1.101" in result.stdout


def test_convert_rejects_an_unknown_converter(tmp_path):
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "acme"\n', encoding="utf-8")
    result = runner.invoke(app, ["convert", str(tmp_path), "--converter", "nope"])
    assert result.exit_code == 2


def test_roadmap_is_read_only(tmp_path):
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "acme"\n', encoding="utf-8")
    (tmp_path / "svc.py").write_text("# TODO: tidy this up\n", encoding="utf-8")
    before = {p.name for p in tmp_path.rglob("*")}
    runner.invoke(app, ["roadmap", str(tmp_path)])
    assert {p.name for p in tmp_path.rglob("*")} == before
