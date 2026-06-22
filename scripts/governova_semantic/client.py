"""Transport for the semantic tier — a minimal chat-completions HTTP client.

Speaks the widely-supported `/chat/completions` JSON protocol using only the
standard library (urllib): no SDK, no provider dependency, no vendor lock-in. The
transport is a plain callable so tests inject a fake and never touch the network.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from collections.abc import Callable

from governova_semantic.config import SemanticConfig

# A transport takes (config, messages) and returns the assistant's text content.
Transport = Callable[[SemanticConfig, list[dict[str, str]]], str]


class SemanticUnavailableError(RuntimeError):
    """Raised when the endpoint cannot be reached or returns an unusable response."""


def urllib_transport(config: SemanticConfig, messages: list[dict[str, str]]) -> str:
    """Default transport: POST to a `/chat/completions` endpoint."""
    payload = json.dumps(
        {
            "model": config.model,
            "messages": messages,
            "temperature": 0,
            "max_tokens": config.max_tokens,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        config.endpoint,
        data=payload,
        headers={
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=config.timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, OSError, ValueError) as exc:
        raise SemanticUnavailableError(f"semantic endpoint unreachable: {exc}") from exc
    try:
        return body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise SemanticUnavailableError("unexpected response shape from semantic endpoint") from exc
