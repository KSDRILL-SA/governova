"""governova_settings — one validated read of the environment.

`S1.68` requires environment variables to be validated at startup, and `S2.67`
requires a settings object to own configuration so the shape is checked once
instead of trusted everywhere. This repository did neither: three modules read
their own variables at the point of use, and every one of them fell back
*silently*.

    GOVERNOVA_LLM_TIMEOUT=abc        -> 30.0, no word to anyone
    GOVERNOVA_LLM_PROTOCOL=mesages   -> chat_completions, no word to anyone
    GOVERNOVA_LLM_BASEURL=...        -> ignored entirely; the name is not read

The last is the worst of the three. A misspelled variable is not a wrong value,
it is an *absent* one, and absence is indistinguishable from "not configured" —
so an operator who set the semantic tier up and typed one character wrong is told
the tier is inactive, which is true and useless.

**Absent is still fine.** `ADR-010` §5.1 guarantees the deterministic engine runs
with nothing set, offline, forever. This module never turns an unset variable
into a problem. It reports values that were *supplied and could not be used*, and
names that were supplied and are not read by anything.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from governova_notify import ENV_TIMEOUT as ENV_WEBHOOK_TIMEOUT
from governova_notify import ENV_WEBHOOK_URL
from governova_semantic.config import (
    ENV_API_KEY,
    ENV_API_VERSION,
    ENV_BASE_URL,
    ENV_MAX_TOKENS,
    ENV_MODEL,
    ENV_PROTOCOL,
    ENV_TIMEOUT,
    PROTOCOLS,
)

ENV_CONSTITUTION = "GOVERNOVA_CONSTITUTION"

# Every variable this engine reads. The set is the point: anything matching the
# prefix and absent from here is a name nothing consumes.
KNOWN: tuple[str, ...] = (
    ENV_MODEL,
    ENV_BASE_URL,
    ENV_API_KEY,
    ENV_TIMEOUT,
    ENV_MAX_TOKENS,
    ENV_PROTOCOL,
    ENV_API_VERSION,
    ENV_WEBHOOK_URL,
    ENV_WEBHOOK_TIMEOUT,
    ENV_CONSTITUTION,
)

PREFIX = "GOVERNOVA_"

# Variables whose value must never be printed, whatever the surface. Matched on
# the name so a variable added later is redacted by shape rather than by memory.
_SECRET_MARKERS = ("KEY", "TOKEN", "SECRET", "PASSWORD", "WEBHOOK_URL")


@dataclass(frozen=True)
class Problem:
    """One supplied value that could not be used, and what happened instead."""

    variable: str
    detail: str

    def __str__(self) -> str:
        return f"{self.variable}: {self.detail}"


@dataclass(frozen=True)
class Setting:
    """One variable as resolved, safe to display."""

    variable: str
    set: bool
    shown: str


def is_secret(variable: str) -> bool:
    """Whether a variable's value must be redacted before it is shown."""
    return any(marker in variable.upper() for marker in _SECRET_MARKERS)


def redact(variable: str, value: str) -> str:
    """A value safe to print.

    Secrets are reduced to their length. Length is genuinely useful — it
    separates "the key is set" from "the key is set to an empty string after a
    failed substitution" — and it discloses nothing.
    """
    if not is_secret(variable):
        return value
    return f"<set, {len(value)} character(s)>" if value else "<set but empty>"


def _numeric_problem(
    variable: str, raw: str, cast: Callable[[str], float], fallback: object
) -> Problem | None:
    """A supplied numeric value that cannot be used, or None when it can.

    Zero and negatives are checked separately from parse failures because they
    parse cleanly and are still unusable — a timeout of 0 is the case a bare
    `try/except ValueError` waves through.
    """
    try:
        parsed = cast(raw)
    except (TypeError, ValueError):
        return Problem(variable, f"{raw!r} is not a number — falling back to {fallback}")
    if parsed <= 0:
        return Problem(variable, f"{raw!r} is not positive — falling back to {fallback}")
    return None


def inspect_env(env: dict[str, str] | None = None) -> tuple[Problem, ...]:
    """Every supplied value that cannot be used, and every name nothing reads.

    Returns an empty tuple for an environment with nothing set — that is the
    supported configuration, not a finding.
    """
    e = dict(os.environ) if env is None else dict(env)
    problems: list[Problem] = []

    for variable, cast, fallback in (
        (ENV_TIMEOUT, float, 30.0),
        (ENV_MAX_TOKENS, int, 1024),
        (ENV_WEBHOOK_TIMEOUT, float, 15.0),
    ):
        raw = e.get(variable)
        if raw is None or not raw.strip():
            continue
        problem = _numeric_problem(variable, raw.strip(), cast, fallback)
        if problem is not None:
            problems.append(problem)

    protocol = e.get(ENV_PROTOCOL)
    if protocol and protocol.strip().lower().replace("-", "_") not in PROTOCOLS:
        problems.append(
            Problem(
                ENV_PROTOCOL,
                f"{protocol!r} is not one of {', '.join(PROTOCOLS)} — "
                "falling back to the default protocol",
            )
        )

    webhook = e.get(ENV_WEBHOOK_URL)
    if webhook and not webhook.strip().lower().startswith(("http://", "https://")):
        problems.append(
            Problem(ENV_WEBHOOK_URL, "is not an http(s) URL — notifications will not be sent")
        )

    constitution = e.get(ENV_CONSTITUTION)
    if constitution and not Path(constitution).expanduser().is_file():
        problems.append(
            Problem(ENV_CONSTITUTION, f"{constitution!r} is not a readable file")
        )

    # A partially configured semantic tier is the case an operator most often
    # cannot see: the tier reports itself inactive, which is true, and says
    # nothing about the two variables that *were* set.
    supplied = [v for v in (ENV_MODEL, ENV_BASE_URL, ENV_API_KEY) if e.get(v)]
    if supplied and len(supplied) < 3:
        absent = [v for v in (ENV_MODEL, ENV_BASE_URL, ENV_API_KEY) if not e.get(v)]
        problems.append(
            Problem(
                ", ".join(absent),
                "not set, while the rest of the semantic tier is — the tier stays "
                "inactive and will report itself inactive, which hides the gap",
            )
        )

    for name in sorted(e):
        if name.startswith(PREFIX) and name not in KNOWN:
            problems.append(
                Problem(name, "is not read by anything — check the spelling against `.env.example`")
            )

    return tuple(problems)


def resolved(env: dict[str, str] | None = None) -> tuple[Setting, ...]:
    """Every known variable and how it resolved, with secrets redacted."""
    e = dict(os.environ) if env is None else dict(env)
    settings = []
    for variable in KNOWN:
        raw = e.get(variable)
        if raw is None:
            settings.append(Setting(variable, False, "<unset>"))
        else:
            settings.append(Setting(variable, True, redact(variable, raw)))
    return tuple(settings)
