"""Tests for the CI/CD enforcement surface (governova-enforce)."""

from __future__ import annotations

import json

from governova_enforce.__main__ import app
from typer.testing import CliRunner

runner = CliRunner()

VIOLATION = "localStorage.setItem('access_token', t);\n"  # AP-S3.14a, high → blocks
MEDIUM_ONLY = "db.query(`SELECT * FROM users WHERE id = ${userId}`)\n"  # AP-S2.28f, medium
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


def test_semantic_flag_inactive_is_noop(tmp_path, monkeypatch):
    for v in ("GOVERNOVA_LLM_MODEL", "GOVERNOVA_LLM_BASE_URL", "GOVERNOVA_LLM_API_KEY"):
        monkeypatch.delenv(v, raising=False)
    f = _write(tmp_path, "good.ts", CLEAN)
    result = runner.invoke(app, [f, "--no-default-ignore", "--semantic"])
    assert result.exit_code == 0
    assert "semantic tier inactive" in result.stdout


def test_medium_confidence_does_not_block(tmp_path):
    # A medium-confidence finding is reported but never fails the build.
    f = _write(tmp_path, "query.ts", MEDIUM_ONLY)
    result = runner.invoke(app, [f, "--no-default-ignore", "--mode", "block"])
    assert result.exit_code == 0
    assert "AP-S2.28f" in result.stdout
    assert "advisory" in result.stdout


# ── the machine contract ─────────────────────────────────────────────────────
#
# `--format json` exists so a CI job or an editor can consume findings. It wrote
# a human summary to stdout ahead of the array and a verdict after it, so every
# such consumer failed on the first line — `json.loads` raising at char 4, which
# names nothing about the cause. Each test below asserts a parse, because the
# tests that existed asserted only that a finding *appeared* in the payload, and
# that was true throughout.


def test_json_output_parses(tmp_path):
    f = _write(tmp_path, "bad.ts", VIOLATION)
    result = runner.invoke(app, [f, "--no-default-ignore", "--format", "json"])
    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert [x["anti_pattern"] for x in payload] == ["AP-S3.14a"]


def test_json_output_parses_when_clean(tmp_path):
    """An empty result set is still a result set.

    The clean path returned before emitting anything, so a consumer that parsed
    a run with findings crashed on the run that fixed them.
    """
    f = _write(tmp_path, "good.ts", CLEAN)
    result = runner.invoke(app, [f, "--no-default-ignore", "--format", "json"])
    assert result.exit_code == 0
    assert json.loads(result.stdout) == []


def test_the_json_summary_survives_on_stderr(tmp_path):
    """Routed, not deleted. A human watching a `--format json` run still wants
    the counts; deleting them would have been the smaller diff and the worse
    product."""
    f = _write(tmp_path, "bad.ts", VIOLATION)
    result = runner.invoke(
        app, [f, "--no-default-ignore", "--format", "json"], catch_exceptions=False
    )
    assert "1 finding(s)" in result.stderr
    assert "FAILED" in result.stderr


def test_the_text_format_keeps_its_summary_on_stdout(tmp_path):
    """The fix works by changing which channel a line goes to, so the format
    that was already correct is pinned."""
    f = _write(tmp_path, "bad.ts", VIOLATION)
    result = runner.invoke(app, [f, "--no-default-ignore"])
    assert "1 finding(s)" in result.stdout
    assert "FAILED" in result.stdout
