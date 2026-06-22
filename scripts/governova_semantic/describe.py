"""Semantic file description — a plain-English summary of what a file does.

The second capability of the semantic tier (alongside violation review): used by the
System Bible to turn a file from a black box into one or two sentences a maintainer
can read. Inactive without configuration; advisory and best-effort.
"""

from __future__ import annotations

from governova_semantic.client import SemanticUnavailable, Transport, urllib_transport
from governova_semantic.config import SemanticConfig, from_env

_MAX_CHARS = 6000  # keep prompts bounded; the head of a file is enough to summarise it


def describe_code(
    code: str,
    *,
    config: SemanticConfig | None = None,
    transport: Transport | None = None,
) -> str:
    """Return a one/two-sentence plain summary of `code`, or "" when inactive/unavailable."""
    cfg = config or from_env()
    if not cfg.is_configured or not code.strip():
        return ""
    messages = [
        {
            "role": "system",
            "content": (
                "You document source files for maintainers. Given a file, reply with one "
                "or two plain sentences describing what it does and why it exists. No "
                "preamble, no code, no markdown — just the sentences."
            ),
        },
        {"role": "user", "content": code[:_MAX_CHARS]},
    ]
    send = transport or urllib_transport
    try:
        content = send(cfg, messages)
    except SemanticUnavailable:
        return ""
    return " ".join(content.split()).strip()
