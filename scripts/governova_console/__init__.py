"""One console, configured so it cannot crash on a terminal narrower than its output.

Every command surface in this engine prints `✓` and `✗`. Windows terminals — Git Bash
especially — frequently present stdout as cp1252, which can encode neither, and `rich`
raises `UnicodeEncodeError` from inside `print` rather than degrading. The result is a
command that **crashes while reporting its result**, with a traceback where the answer
should be.

Two things make that worse than a cosmetic bug:

- **It fires on the failure path.** `✗` is printed when something is wrong, so the command
  most likely to crash is the one delivering bad news. `governova-codegen --check` — a
  step in the pre-PR checklist — died this way while correctly detecting no drift.
- **It was documented as a workaround rather than fixed.** The handoff told engineers to
  "use PowerShell for anything that prints a table" because "commands look like they crash
  when they have not". They sometimes had.

Six entrypoints instantiated their own `Console()`, so this lives here once and is imported
(`S1.106`) rather than repaired six times and forgotten in the seventh.
"""

from __future__ import annotations

import contextlib
import sys
from typing import TextIO

from rich.console import Console

__all__ = [
    "configure_stderr",
    "configure_stdout",
    "console",
    "err_console",
]


def _make_safe(stream: TextIO) -> None:
    """Make one stream able to carry the characters this engine prints.

    `errors="replace"` is the belt to UTF-8's braces: where reconfiguration succeeds but
    the terminal still cannot render a character, it degrades to a replacement glyph
    rather than raising. Losing a tick mark is acceptable; losing the result is not.

    A redirected, wrapped, or already-detached stream may not support reconfiguration at
    all, so the method is looked up rather than assumed — which also avoids a type
    suppression, since the streams are declared as the `TextIO` protocol and only the
    concrete `TextIOWrapper` carries `reconfigure`. `S1.57` asks for the type to be fixed
    rather than silenced, and an explicit capability check is the fix.

    The remaining guard covers a stream that *has* the method and still refuses — being
    unable to *improve* the encoding must never be the thing that breaks the command.
    """
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is None:
        return
    with contextlib.suppress(Exception):
        reconfigure(encoding="utf-8", errors="replace")


def configure_stdout() -> None:
    """Make stdout able to carry the characters this engine prints."""
    _make_safe(sys.stdout)


def configure_stderr() -> None:
    """The same for stderr, which now carries prose of its own.

    stderr used to carry only error lines, which were ASCII, so the gap did not
    show. `governova-enforce --format json` changed that: its stdout became a
    machine contract, and every human line — summaries, verdicts, the note saying
    which Layer 4 domain went unenforced — moved to stderr, em dashes included.
    The first run of it printed the note with a replacement glyph mid-sentence.
    """
    _make_safe(sys.stderr)


def console() -> Console:
    """A `rich` console on a stdout that has been made safe first."""
    configure_stdout()
    return Console()


def err_console() -> Console:
    """A `rich` console on a stderr that has been made safe first.

    Exists for the same reason `console` does — six entrypoints once built their
    own, and the seventh forgot. One stream should not be reconfigured in a
    module that happens to notice it needs it.
    """
    configure_stderr()
    return Console(stderr=True)
