"""Tests for the shared console.

The bug this guards against: every command surface prints `✓` and `✗`, Windows terminals
frequently present stdout as cp1252, and `rich` raises `UnicodeEncodeError` from inside
`print` rather than degrading. A command then **crashes while reporting its result** — and
because `✗` is the failure glyph, the command most likely to crash is the one delivering
bad news.
"""

from __future__ import annotations

import io
import subprocess
import sys
from pathlib import Path

from governova_console import configure_stdout, console

REPO = Path(__file__).resolve().parents[2]

# Every entrypoint that builds a console. Kept as a list so adding a seventh surface
# without routing it through the shared console fails here rather than in somebody's
# terminal (S1.106 — shared code is shared).
ENTRYPOINT_MODULES = (
    "governova_cli",
    "governova_codegen",
    "governova_compile",
    "governova_enforce",
    "governova_ingest",
    "governova_validate",
)


def test_configure_stdout_survives_a_stream_that_cannot_be_reconfigured():
    """Being unable to improve the encoding must never break the command."""
    original = sys.stdout
    sys.stdout = io.StringIO()  # no `.reconfigure`
    try:
        configure_stdout()  # must not raise
    finally:
        sys.stdout = original


def test_console_is_usable_after_configuration():
    assert console() is not None


def test_every_entrypoint_routes_through_the_shared_console():
    """A surface that builds its own bare `Console()` reintroduces the crash.

    Asserted against source rather than behaviour because the failure only reproduces on
    a cp1252 terminal, which CI is not.
    """
    offenders: list[str] = []
    for module in ENTRYPOINT_MODULES:
        source = (REPO / "scripts" / module / "__main__.py").read_text(encoding="utf-8")
        if "governova_console" not in source:
            offenders.append(module)
    assert offenders == [], f"entrypoints not using the shared console: {offenders}"


def test_a_glyph_reaches_a_narrow_stdout_without_raising():
    """The end-to-end guarantee, reproduced by forcing the encoding that broke it.

    A subprocess is used because the encoding must be wrong *before* the interpreter
    starts — reconfiguring inside the test would be testing the fix against itself.
    """
    script = (
        "from governova_console import console\n"
        "console().print('[bold red]\\u2717 below the bar[/] and \\u2713 above it')\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=REPO / "scripts",
        capture_output=True,
        text=True,
        encoding="cp1252",
        errors="replace",
        env={**_clean_env(), "PYTHONIOENCODING": "cp1252"},
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
    assert "UnicodeEncodeError" not in result.stderr


def _clean_env() -> dict[str, str]:
    import os

    env = dict(os.environ)
    env.pop("PYTHONIOENCODING", None)
    return env
