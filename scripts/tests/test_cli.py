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
