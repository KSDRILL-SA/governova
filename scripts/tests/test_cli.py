"""Smoke tests for the `governova` CLI surface (wraps the engine)."""

from __future__ import annotations

from typer.testing import CliRunner

from governova_cli.__main__ import app

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
