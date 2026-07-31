"""Transport for the semantic tier — two minimal HTTP protocols, no SDK.

Both transports use only the standard library (urllib): no provider dependency and
no vendor SDK. Which one runs is the operator's choice via `GOVERNOVA_LLM_PROTOCOL`;
`chat_completions` is the default, so an existing deployment is unaffected.

The transport is a plain callable so tests inject a fake and never touch the network.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from typing import Any

from governova_checks.net import require_http_url

from governova_semantic.config import MESSAGES, SemanticConfig

# A transport takes (config, messages) and returns the assistant's text content.
Transport = Callable[[SemanticConfig, list[dict[str, str]]], str]


class SemanticUnavailableError(RuntimeError):
    """Raised when the endpoint cannot be reached or returns an unusable response.

    `status` carries the HTTP status when there was one. A status code is **safe to
    surface** — unlike the URL, it embeds no credential — and it is the difference
    between a diagnosis and a shrug: `410` says the service is retiring, `401` says
    the token, `404` says the path, `429` says the quota. The tier that swallowed all
    four indistinguishably is what made this defect invisible for two releases.
    """

    def __init__(self, message: str, *, status: int | None = None) -> None:
        super().__init__(message)
        self.status = status


TRANSIENT_STATUSES: frozenset[int] = frozenset({429, 500, 502, 503, 504})
"""Statuses that mean *try again*, not *this will never work*.

Deliberately narrow. `401`, `404` and `410` are answers — retrying them wastes a
build's time and tells nobody anything. These five are the ones a healthy endpoint
still emits under load or during a deploy.

Found while measuring a hosted backend: a single evaluation makes tens of sequential
calls, and the provider returned an isolated `502` partway through more than once. The
harness correctly refused to report a partial score, so the measurement could not be
taken at all — a retry is the difference between measurable and not.
"""

MAX_ATTEMPTS = 3
"""Total tries, not extra ones. Bounded so an outage still fails, and fails promptly.

After the last attempt the error is raised exactly as before, so an endpoint that is
genuinely down is still reported as `UNAVAILABLE` with its status. A retry must never
be able to turn an outage into silence.
"""

BACKOFF_SECONDS = 2.0
"""Base for exponential backoff between attempts — 2s, then 4s."""


def _post(config: SemanticConfig, headers: dict[str, str], payload: dict[str, Any]) -> Any:
    """POST JSON to the configured endpoint and return the decoded body.

    Retries only `TRANSIENT_STATUSES`, at most `MAX_ATTEMPTS` times, with exponential
    backoff. Every other failure is raised on the first attempt.
    """
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            return _post_once(config, headers, payload)
        except SemanticUnavailableError as exc:
            retryable = exc.status in TRANSIENT_STATUSES
            if not retryable or attempt == MAX_ATTEMPTS:
                raise
            time.sleep(BACKOFF_SECONDS ** (attempt - 1) * BACKOFF_SECONDS)
    raise AssertionError("unreachable")  # pragma: no cover - the loop always returns or raises


def _post_once(config: SemanticConfig, headers: dict[str, str], payload: dict[str, Any]) -> Any:
    """One POST. Separated so the retry policy is readable on its own."""
    endpoint = require_http_url(config.endpoint, what="semantic endpoint")
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=config.timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        # The status is reported; the URL and the body are not. urllib puts the
        # request URL in the exception text, and an endpoint configured with inline
        # credentials (`https://user:key@host`) would put them in a CI log that many
        # people can read. A bare status code carries no secret and answers the only
        # question worth asking: was this the endpoint, the token, or the model.
        raise SemanticUnavailableError(
            f"semantic endpoint returned HTTP {exc.code}", status=exc.code
        ) from exc
    except (urllib.error.URLError, OSError, ValueError) as exc:
        # No status to report — DNS, TLS, timeout, or a malformed body. The exception
        # type is the most that can be said without echoing the request.
        raise SemanticUnavailableError(
            f"semantic endpoint unreachable ({type(exc).__name__})"
        ) from exc


def _split_system(messages: list[dict[str, str]]) -> tuple[str, list[dict[str, str]]]:
    """Separate system turns from the conversation.

    The `messages` protocol carries the system prompt in a dedicated top-level field
    and does not accept `system` as a conversational role, so a prompt built once has
    to be reshaped rather than passed straight through.
    """
    system = "\n\n".join(m.get("content", "") for m in messages if m.get("role") == "system")
    rest = [m for m in messages if m.get("role") != "system"]
    return system, rest


def chat_completions_transport(config: SemanticConfig, messages: list[dict[str, str]]) -> str:
    """POST to a `/chat/completions` endpoint with bearer auth."""
    body = _post(
        config,
        {"Authorization": f"Bearer {config.api_key}"},
        {
            "model": config.model,
            "messages": messages,
            "temperature": 0,
            "max_tokens": config.max_tokens,
        },
    )
    try:
        return str(body["choices"][0]["message"]["content"])
    except (KeyError, IndexError, TypeError) as exc:
        raise SemanticUnavailableError("unexpected response shape from semantic endpoint") from exc


def messages_transport(config: SemanticConfig, messages: list[dict[str, str]]) -> str:
    """POST to a `/messages` endpoint with key and API-version headers.

    Three deliberate differences from `chat_completions`, each required by the
    protocol rather than stylistic:

    - The system prompt is a top-level field, not a turn (see `_split_system`).
    - No sampling parameter is sent. Current models on this protocol reject
      `temperature` outright, so carrying over the `chat_completions` default of
      `0` would fail every request.
    - The reply is a list of typed blocks. The first *text* block is the answer;
      earlier blocks may be reasoning and must be skipped rather than indexed past.
    """
    system, turns = _split_system(messages)
    payload: dict[str, Any] = {
        "model": config.model,
        "max_tokens": config.max_tokens,
        "messages": turns,
    }
    if system:
        payload["system"] = system
    body = _post(
        config,
        # Header names are fixed by the protocol; both are mandatory.
        {"x-api-key": config.api_key or "", "anthropic-version": config.api_version},
        payload,
    )
    try:
        text = next(b["text"] for b in body["content"] if b.get("type") == "text")
    except (KeyError, TypeError, StopIteration) as exc:
        # Also the path taken when the endpoint declines the request: the reply is
        # well-formed but carries no text block. Advisory findings degrade to none,
        # which is the correct outcome either way.
        raise SemanticUnavailableError("unexpected response shape from semantic endpoint") from exc
    return str(text)


_TRANSPORTS: dict[str, Transport] = {MESSAGES: messages_transport}


def default_transport(config: SemanticConfig, messages: list[dict[str, str]]) -> str:
    """Dispatch to the transport for the configured protocol."""
    return _TRANSPORTS.get(config.protocol, chat_completions_transport)(config, messages)
