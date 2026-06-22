"""Tests for the chat notifier (governova_notify) — mocked, no network."""

from __future__ import annotations

from governova_notify import NotifyConfig, from_env, notify


def test_inactive_without_url():
    cfg = from_env({})
    assert not cfg.is_configured
    # Inactive returns False without ever calling the transport.
    assert notify(config=cfg, transport=lambda u, p, t: 1 / 0) is False


def test_configured_detection():
    assert NotifyConfig(webhook_url="https://hooks.example/x").is_configured
    assert not NotifyConfig(webhook_url=None).is_configured


def test_notify_posts_with_mock_transport():
    cfg = NotifyConfig(webhook_url="https://hooks.example/x")
    captured = {}

    def fake(url, payload, timeout):
        captured["url"] = url
        captured["payload"] = payload
        return True

    ok = notify("HEAD", config=cfg, transport=fake)
    assert ok is True
    assert captured["url"] == "https://hooks.example/x"
    assert "text" in captured["payload"] and "Governova Guardian" in captured["payload"]["text"]
