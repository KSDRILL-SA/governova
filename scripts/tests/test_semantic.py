"""Tests for the semantic tier (governova_semantic) — fully mocked, no network."""

from __future__ import annotations

import json
from dataclasses import replace

import pytest
from governova_compile.discovery import resolve_repo_root
from governova_compile.writer import load_index
from governova_semantic import (
    SemanticConfig,
    build_messages,
    client,
    describe_code,
    parse_findings,
    relevant_standards,
    review,
)
from governova_semantic import config as config_mod
from governova_semantic.config import from_env

INDEX = load_index(resolve_repo_root() / "compiled" / "constitution.json")
ACTIVE = SemanticConfig(model="m", base_url="https://endpoint.example/v1", api_key="k")


def test_inactive_without_config():
    cfg = from_env({})
    assert not cfg.is_configured
    # Even with a transport that would raise, an inactive tier returns [] before calling it.
    out = review("anything", config=cfg, transport=lambda c, m: 1 / 0)
    assert out == []


def test_configured_detection_and_endpoint():
    assert ACTIVE.is_configured
    assert ACTIVE.endpoint == "https://endpoint.example/v1/chat/completions"
    assert not SemanticConfig(model="m", base_url=None, api_key="k").is_configured


def test_parse_drops_hallucinated_standards():
    content = json.dumps(
        {"findings": [
            {"standard": "S2.34", "line": 5, "message": "money as float"},
            {"standard": "S99.99", "line": 1, "message": "not a real standard"},
        ]}
    )
    out = parse_findings(content, allowed_ids={"S2.34"})
    assert len(out) == 1 and out[0].standard == "S2.34" and out[0].line == 5


def test_parse_handles_code_fenced_json():
    content = "```json\n" + json.dumps({"findings": [{"standard": "S2.1", "message": "x"}]}) + "\n```"
    out = parse_findings(content, allowed_ids={"S2.1"})
    assert len(out) == 1 and out[0].standard == "S2.1"


def test_review_with_mock_transport_keeps_only_grounded():
    std = next(s for c in INDEX.constitutions for s in c.standards)  # a real standard

    def fake_transport(cfg, messages):
        return json.dumps(
            {"findings": [
                {"standard": std.id, "line": 3, "message": "violates this"},
                {"standard": "S88.88", "line": 9, "message": "hallucinated"},
            ]}
        )

    out = review("some code", standards=[std], index=INDEX, config=ACTIVE, transport=fake_transport)
    assert len(out) == 1 and out[0].standard == std.id.upper()
    assert out[0].advisory and out[0].tier == "semantic"


def test_review_degrades_on_transport_error():
    from governova_semantic.client import SemanticUnavailableError

    std = next(s for c in INDEX.constitutions for s in c.standards)

    def boom(cfg, messages):
        raise SemanticUnavailableError("down")

    assert review("code", standards=[std], index=INDEX, config=ACTIVE, transport=boom) == []


def test_describe_code_with_mock_and_inactive():
    out = describe_code("def f():\n    pass\n", config=ACTIVE, transport=lambda c, m: "  Defines f.  ")
    assert out == "Defines f."
    assert describe_code("code", config=from_env({})) == ""  # inactive


def test_relevant_standards_and_messages():
    picked = relevant_standards(INDEX, "authentication token refresh session", limit=5)
    assert len(picked) <= 5
    msgs = build_messages("code here", picked)
    assert msgs[0]["role"] == "system" and "code here" in msgs[1]["content"]


# --- protocol selection ---------------------------------------------------------


def test_protocol_defaults_to_chat_completions():
    assert from_env({}).protocol == config_mod.CHAT_COMPLETIONS
    assert ACTIVE.protocol == config_mod.CHAT_COMPLETIONS
    assert ACTIVE.endpoint.endswith("/chat/completions")


def test_protocol_is_read_and_normalised_from_env():
    env = {"GOVERNOVA_LLM_PROTOCOL": " MESSAGES "}
    assert from_env(env).protocol == config_mod.MESSAGES
    # Hyphens are accepted for the underscored form.
    assert from_env({"GOVERNOVA_LLM_PROTOCOL": "chat-completions"}).protocol == (
        config_mod.CHAT_COMPLETIONS
    )


def test_unknown_protocol_degrades_to_the_default():
    """A typo in a CI secret must not fail a build over an advisory tier."""
    assert from_env({"GOVERNOVA_LLM_PROTOCOL": "nonsense"}).protocol == (
        config_mod.CHAT_COMPLETIONS
    )


def test_messages_protocol_endpoint_path():
    cfg = replace(ACTIVE, protocol=config_mod.MESSAGES)
    assert cfg.endpoint == "https://endpoint.example/v1/messages"


def test_api_version_default_and_override():
    assert from_env({}).api_version == config_mod.DEFAULT_API_VERSION
    assert from_env({"GOVERNOVA_LLM_API_VERSION": "2099-01-01"}).api_version == "2099-01-01"


# --- transports (no network: `_post` is replaced) --------------------------------


def _capture(monkeypatch, response):
    """Replace the HTTP POST with a recorder returning `response`."""
    seen: dict[str, object] = {}

    def fake_post(cfg, headers, payload):
        seen["config"] = cfg
        seen["headers"] = headers
        seen["payload"] = payload
        return response

    monkeypatch.setattr(client, "_post", fake_post)
    return seen


PROMPT = [{"role": "system", "content": "be strict"}, {"role": "user", "content": "code"}]


def test_chat_completions_transport_shape(monkeypatch):
    seen = _capture(monkeypatch, {"choices": [{"message": {"content": "ok"}}]})
    assert client.chat_completions_transport(ACTIVE, PROMPT) == "ok"

    assert seen["headers"] == {"Authorization": "Bearer k"}
    payload = seen["payload"]
    assert payload["messages"] == PROMPT  # system stays a conversational turn
    assert payload["temperature"] == 0
    assert payload["max_tokens"] == ACTIVE.max_tokens


def test_messages_transport_shape(monkeypatch):
    cfg = replace(ACTIVE, protocol=config_mod.MESSAGES)
    seen = _capture(monkeypatch, {"content": [{"type": "text", "text": "ok"}]})
    assert client.messages_transport(cfg, PROMPT) == "ok"

    assert seen["headers"] == {"x-api-key": "k", "anthropic-version": cfg.api_version}
    payload = seen["payload"]
    # The system prompt is hoisted out of the turns into its own field.
    assert payload["system"] == "be strict"
    assert payload["messages"] == [{"role": "user", "content": "code"}]
    # Sending a sampling parameter here is rejected by current models on this protocol.
    assert "temperature" not in payload
    assert payload["max_tokens"] == cfg.max_tokens


def test_messages_transport_skips_leading_non_text_blocks(monkeypatch):
    """The answer is the first *text* block — earlier blocks may be reasoning."""
    cfg = replace(ACTIVE, protocol=config_mod.MESSAGES)
    _capture(
        monkeypatch,
        {"content": [{"type": "thinking", "thinking": ""}, {"type": "text", "text": "answer"}]},
    )
    assert client.messages_transport(cfg, PROMPT) == "answer"


def test_messages_transport_reports_unavailable_when_no_text_block(monkeypatch):
    """A declined request is well-formed but carries no text — degrade, do not crash."""
    cfg = replace(ACTIVE, protocol=config_mod.MESSAGES)
    _capture(monkeypatch, {"content": [], "stop_reason": "refusal"})
    with pytest.raises(client.SemanticUnavailableError):
        client.messages_transport(cfg, PROMPT)

    # And the tier as a whole reports nothing rather than failing the caller.
    std = next(s for c in INDEX.constitutions for s in c.standards)
    assert review("code", standards=[std], index=INDEX, config=cfg) == []


def test_default_transport_dispatches_on_protocol(monkeypatch):
    seen = _capture(monkeypatch, {"choices": [{"message": {"content": "cc"}}]})
    assert client.default_transport(ACTIVE, PROMPT) == "cc"
    assert "Authorization" in seen["headers"]

    cfg = replace(ACTIVE, protocol=config_mod.MESSAGES)
    seen = _capture(monkeypatch, {"content": [{"type": "text", "text": "msg"}]})
    assert client.default_transport(cfg, PROMPT) == "msg"
    assert "x-api-key" in seen["headers"]


def test_both_protocols_refuse_a_non_http_endpoint():
    """`require_http_url` guards every transport, not just the original one."""
    for protocol in config_mod.PROTOCOLS:
        cfg = replace(ACTIVE, base_url="file:///etc/passwd", protocol=protocol)
        with pytest.raises(ValueError):
            client.default_transport(cfg, PROMPT)
