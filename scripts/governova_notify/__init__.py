"""governova_notify — post a governance verdict to a chat webhook.

Provider-agnostic: the webhook URL comes from the environment, the payload is a simple
`{"text": ...}` body accepted by Slack/Teams-style incoming webhooks. Inactive without
a URL (a no-op), so nothing depends on it being configured.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

ENV_WEBHOOK_URL = "GOVERNOVA_WEBHOOK_URL"
ENV_TIMEOUT = "GOVERNOVA_WEBHOOK_TIMEOUT"

# A transport takes (url, payload, timeout) and returns True on success.
Transport = Callable[[str, dict, float], bool]


@dataclass(frozen=True)
class NotifyConfig:
    webhook_url: str | None
    timeout: float = 15.0

    @property
    def is_configured(self) -> bool:
        return bool(self.webhook_url)


def from_env(env: dict[str, str] | None = None) -> NotifyConfig:
    e = env if env is not None else dict(os.environ)
    try:
        timeout = float(e.get(ENV_TIMEOUT, "15"))
    except ValueError:
        timeout = 15.0
    return NotifyConfig(webhook_url=e.get(ENV_WEBHOOK_URL) or None, timeout=timeout)


def urllib_transport(url: str, payload: dict, timeout: float) -> bool:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as resp:
            return 200 <= resp.status < 300
    except (urllib.error.URLError, OSError):
        return False


def notify(
    base: str = "origin/main",
    root: Path | None = None,
    *,
    config: NotifyConfig | None = None,
    transport: Transport | None = None,
) -> bool:
    """Post the Guardian verdict to the webhook. Returns False when inactive or on error."""
    cfg = config or from_env()
    if not cfg.is_configured:
        return False
    from governova_guardian import build_verdict, to_markdown

    verdict = build_verdict(base, root)
    send = transport or urllib_transport
    return send(cfg.webhook_url, {"text": to_markdown(verdict)}, cfg.timeout)


__all__ = ["NotifyConfig", "from_env", "notify", "urllib_transport"]
