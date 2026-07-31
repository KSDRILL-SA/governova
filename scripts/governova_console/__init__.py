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

from rich.console import Console

__all__ = ["configure_stdout", "console"]


def configure_stdout() -> None:
    """Make stdout able to carry the characters this engine prints.

    `errors="replace"` is the belt to UTF-8's braces: where reconfiguration succeeds but
    the terminal still cannot render a character, it degrades to a replacement glyph
    rather than raising. Losing a tick mark is acceptable; losing the result is not.

    A redirected, wrapped, or already-detached stream may not support reconfiguration at
    all, so the method is looked up rather than assumed — which also avoids a type
    suppression, since `sys.stdout` is declared as the `TextIO` protocol and only the
    concrete `TextIOWrapper` carries `reconfigure`. `S1.57` asks for the type to be fixed
    rather than silenced, and an explicit capability check is the fix.

    The remaining guard covers a stream that *has* the method and still refuses — being
    unable to *improve* the encoding must never be the thing that breaks the command.
    """
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if reconfigure is None:
        return
    with contextlib.suppress(Exception):
        reconfigure(encoding="utf-8", errors="replace")


def console() -> Console:
    """A `rich` console on a stdout that has been made safe first."""
    configure_stdout()
    return Console()
