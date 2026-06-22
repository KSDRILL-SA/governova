"""Configuration for the semantic tier — entirely environment-driven.

The semantic tier speaks the widely-supported chat-completions protocol over plain
HTTP, so it works with any compatible endpoint. There is no provider lock-in and no
vendor name anywhere: the model, endpoint, and key are supplied by the operator via
the environment. With nothing configured, the tier is inactive.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

ENV_MODEL = "GOVERNOVA_LLM_MODEL"
ENV_BASE_URL = "GOVERNOVA_LLM_BASE_URL"
ENV_API_KEY = "GOVERNOVA_LLM_API_KEY"
ENV_TIMEOUT = "GOVERNOVA_LLM_TIMEOUT"
ENV_MAX_TOKENS = "GOVERNOVA_LLM_MAX_TOKENS"


@dataclass(frozen=True)
class SemanticConfig:
    model: str | None
    base_url: str | None
    api_key: str | None
    timeout: float = 30.0
    max_tokens: int = 1024

    @property
    def is_configured(self) -> bool:
        """The tier is active only when an endpoint, key, and model are all present."""
        return bool(self.model and self.base_url and self.api_key)

    @property
    def endpoint(self) -> str:
        base = (self.base_url or "").rstrip("/")
        return f"{base}/chat/completions"


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
    )
