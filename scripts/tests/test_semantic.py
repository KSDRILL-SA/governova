"""Tests for the semantic tier (governova_semantic) — fully mocked, no network."""

from __future__ import annotations

import json

from governova_compile.discovery import resolve_repo_root
from governova_compile.writer import load_index
from governova_semantic import SemanticConfig, build_messages, parse_findings, relevant_standards, review
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
    from governova_semantic.client import SemanticUnavailable

    std = next(s for c in INDEX.constitutions for s in c.standards)

    def boom(cfg, messages):
        raise SemanticUnavailable("down")

    assert review("code", standards=[std], index=INDEX, config=ACTIVE, transport=boom) == []


def test_relevant_standards_and_messages():
    picked = relevant_standards(INDEX, "authentication token refresh session", limit=5)
    assert len(picked) <= 5
    msgs = build_messages("code here", picked)
    assert msgs[0]["role"] == "system" and "code here" in msgs[1]["content"]
