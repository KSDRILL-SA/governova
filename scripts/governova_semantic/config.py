"""Configuration for the semantic tier — entirely environment-driven.

The semantic tier speaks one of two open HTTP protocols, selected by the operator:

- `chat_completions` (the default) — `POST {base}/chat/completions` with bearer auth.
- `messages` — `POST {base}/messages` with a key header and an API-version header.

Which endpoint, which model, and which key are always supplied by the operator via
the environment; there is no default provider, no bundled hostname, and no credential
in this repository. With nothing configured, the tier is inactive.

Two protocols rather than one because the single most common enterprise endpoint does
not speak `chat_completions`, and a governance tool that cannot read a team's own
model is a governance tool that team does not run.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

ENV_MODEL = "GOVERNOVA_LLM_MODEL"
ENV_BASE_URL = "GOVERNOVA_LLM_BASE_URL"
ENV_API_KEY = "GOVERNOVA_LLM_API_KEY"
ENV_TIMEOUT = "GOVERNOVA_LLM_TIMEOUT"
ENV_MAX_TOKENS = "GOVERNOVA_LLM_MAX_TOKENS"
ENV_PROTOCOL = "GOVERNOVA_LLM_PROTOCOL"
ENV_API_VERSION = "GOVERNOVA_LLM_API_VERSION"

CHAT_COMPLETIONS = "chat_completions"
MESSAGES = "messages"
PROTOCOLS = (CHAT_COMPLETIONS, MESSAGES)

# The `messages` protocol requires a dated API-version header. This is the stable
# value at time of writing; it is configurable so a deployment can move without a
# code change, and so this constant can never silently pin an operator to the past.
DEFAULT_API_VERSION = "2023-06-01"

# Path suffix per protocol. `base_url` carries the version segment, exactly as it
# does for `chat_completions` — one convention, both protocols.
_PATHS = {CHAT_COMPLETIONS: "/chat/completions", MESSAGES: "/messages"}


@dataclass(frozen=True)
class SemanticConfig:
    model: str | None
    base_url: str | None
    api_key: str | None
    timeout: float = 30.0
    max_tokens: int = 1024
    protocol: str = CHAT_COMPLETIONS
    api_version: str = DEFAULT_API_VERSION

    @property
    def is_configured(self) -> bool:
        """The tier is active only when an endpoint, key, and model are all present."""
        return bool(self.model and self.base_url and self.api_key)

    @property
    def endpoint(self) -> str:
        base = (self.base_url or "").rstrip("/")
        return f"{base}{_PATHS.get(self.protocol, _PATHS[CHAT_COMPLETIONS])}"


def _protocol(raw: str | None) -> str:
    """Normalise the configured protocol, falling back to the default when unknown.

    An unrecognised value degrades to the default rather than raising: a typo in an
    operator's CI secret must not fail a build over an advisory tier.
    """
    value = (raw or "").strip().lower().replace("-", "_")
    return value if value in PROTOCOLS else CHAT_COMPLETIONS


def from_env(env: dict[str, str] | None = None) -> SemanticConfig:
    e = env if env is not None else dict(os.environ)
    try:
        timeout = float(e.get(ENV_TIMEOUT, "30"))
    except ValueError:
        timeout = 30.0
    try:
        max_tokens = int(e.get(ENV_MAX_TOKENS, "1024"))
    except ValueError:
        max_tokens = 1024
    return SemanticConfig(
        model=e.get(ENV_MODEL) or None,
        base_url=e.get(ENV_BASE_URL) or None,
        api_key=e.get(ENV_API_KEY) or None,
        timeout=timeout,
        max_tokens=max_tokens,
        protocol=_protocol(e.get(ENV_PROTOCOL)),
        api_version=e.get(ENV_API_VERSION) or DEFAULT_API_VERSION,
    )
