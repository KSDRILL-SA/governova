"""Tests for the CI/CD enforcement surface (governova-enforce)."""

from __future__ import annotations

from typer.testing import CliRunner

from governova_enforce.__main__ import app

runner = CliRunner()

VIOLATION = "localStorage.setItem('access_token', t);\n"
CLEAN = "const sum = a + b;\n"


def _write(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return str(p)


def test_block_mode_fails_on_violation(tmp_path):
    f = _write(tmp_path, "bad.ts", VIOLATION)
    result = runner.invoke(app, [f, "--no-default-ignore", "--mode", "block"])
    assert result.exit_code == 1
    assert "AP-S3.14a" in result.stdout


def test_clean_code_passes(tmp_path):
    f = _write(tmp_path, "good.ts", CLEAN)
    result = runner.invoke(app, [f, "--no-default-ignore"])
    assert result.exit_code == 0
    assert "passed" in result.stdout


def test_advisory_mode_reports_but_does_not_fail(tmp_path):
    f = _write(tmp_path, "bad.ts", VIOLATION)
    result = runner.invoke(app, [f, "--no-default-ignore", "--mode", "advisory"])
    assert result.exit_code == 0
    assert "AP-S3.14a" in result.stdout


def test_github_format_emits_annotation(tmp_path):
    f = _write(tmp_path, "bad.ts", VIOLATION)
    result = runner.invoke(app, [f, "--no-default-ignore", "--format", "github"])
    assert result.exit_code == 1
    assert "::error" in result.stdout
    assert "AP-S3.14a" in result.stdout


def test_default_ignore_skips_test_files(tmp_path):
    # A file matching the default ignore globs must not be gated on.
    f = _write(tmp_path, "test_thing.ts", VIOLATION)
    result = runner.invoke(app, [f])
    assert result.exit_code == 0


def test_explicit_ignore_glob(tmp_path):
    f = _write(tmp_path, "bad.ts", VIOLATION)
    result = runner.invoke(app, [f, "--no-default-ignore", "--ignore", "*bad.ts"])
    assert result.exit_code == 0
