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
    # Verifies REQ-008 — an advisory tier leaves the build result unchanged.
    from governova_semantic.client import SemanticUnavailableError

    std = next(s for c in INDEX.constitutions for s in c.standards)

    def boom(cfg, messages):
        raise SemanticUnavailableError("down")

    assert review("code", standards=[std], index=INDEX, config=ACTIVE, transport=boom) == []


def test_a_clean_review_and_a_failed_one_are_distinguishable():
    """The defect #142 was filed for, and the reason it survived two releases.

    An unreachable endpoint, a rejected token, and a genuinely clean review all
    produce zero findings. Before this, all three produced *identical* output — so a
    green build was not evidence the tier had run, and for two releases it had not.
    """
    from governova_semantic import Outcome, review_result
    from governova_semantic.client import SemanticUnavailableError

    std = next(s for c in INDEX.constitutions for s in c.standards)

    def clean(cfg, messages):
        return json.dumps({"findings": []})

    def dead(cfg, messages):
        raise SemanticUnavailableError("semantic endpoint returned HTTP 410", status=410)

    reviewed = review_result("code", standards=[std], index=INDEX, config=ACTIVE, transport=clean)
    failed = review_result("code", standards=[std], index=INDEX, config=ACTIVE, transport=dead)

    # Both have no findings — that is the whole trap.
    assert reviewed.findings == failed.findings == []
    # And they are no longer confusable.
    assert reviewed.outcome is Outcome.REVIEWED and reviewed.ran
    assert failed.outcome is Outcome.UNAVAILABLE and not failed.ran
    assert failed.status == 410


def test_the_inactive_and_ungrounded_outcomes_are_also_named():
    from governova_semantic import Outcome, review_result

    inactive = review_result("anything", config=from_env({}), transport=lambda c, m: 1 / 0)
    assert inactive.outcome is Outcome.INACTIVE and not inactive.ran

    ungrounded = review_result(
        "code", standards=[], index=INDEX, config=ACTIVE, transport=lambda c, m: 1 / 0
    )
    assert ungrounded.outcome is Outcome.NOT_GROUNDED and not ungrounded.ran


def test_the_diagnostic_never_echoes_a_url_or_a_key():
    """ADR-006 — errors never echo URLs or credentials, and CI logs are widely read.

    The negative half of the fix: making failure visible must not make secrets
    visible. A status code carries no secret; a URL configured as
    `https://user:key@host` carries two.
    """
    import urllib.error

    from governova_semantic.client import SemanticUnavailableError, _post

    secret_url = "https://user:sup3rs3cret@endpoint.example/v1"
    cfg = SemanticConfig(model="m", base_url=secret_url, api_key="sk-abcdef123456")

    def raiser(request, timeout):
        raise urllib.error.HTTPError(secret_url, 410, "Gone", {}, None)  # type: ignore[arg-type]

    import governova_semantic.client as client_mod

    original = client_mod.urllib.request.urlopen
    client_mod.urllib.request.urlopen = raiser  # type: ignore[assignment]
    try:
        with pytest.raises(SemanticUnavailableError) as excinfo:
            _post(cfg, {}, {})
    finally:
        client_mod.urllib.request.urlopen = original  # type: ignore[assignment]

    text = str(excinfo.value)
    assert "410" in text
    assert "sup3rs3cret" not in text
    assert "sk-abcdef123456" not in text
    assert "endpoint.example" not in text


def test_no_endpoint_is_bundled_anywhere():
    """ADR-008 — the semantic tier ships with no default endpoint.

    The retired one sat in a workflow default for two releases and reached nothing
    while every build stayed green. A default that lies is worse than no default,
    because it turns an absent capability into a believed one. This asserts that no
    hostname this project does not control has crept back into the engine or the CI
    configuration.
    """
    cfg = from_env({})
    assert cfg.base_url is None and cfg.model is None and cfg.api_key is None
    assert not cfg.is_configured

    root = resolve_repo_root()
    sources = [
        *(root / "scripts").rglob("*.py"),
        *(root / ".github" / "workflows").glob("*.yml"),
    ]
    offenders = [
        p.relative_to(root).as_posix()
        for p in sources
        if "test_semantic" not in p.name and "models.github.ai" in p.read_text(
            encoding="utf-8", errors="replace"
        )
    ]
    assert offenders == [], f"a retired endpoint is still referenced in: {offenders}"


def test_an_empty_reply_is_not_a_clean_review():
    """A 200 carrying no verdict must not read as "reviewed, nothing found".

    The case that produced this: a reasoning model spent its token budget on an internal
    `reasoning` field and returned `content: ""`. Nothing errored, the status was 200, and
    a build would have gone green on a review that produced no answer — `#142`'s failure
    class wearing different clothes.
    """
    from governova_semantic import Outcome, review_result

    std = next(s for c in INDEX.constitutions for s in c.standards)
    result = review_result("code", standards=[std], index=INDEX, config=ACTIVE, transport=lambda c, m: "")
    assert result.outcome is Outcome.UNPARSEABLE
    assert not result.ran
    assert "MAX_TOKENS" in result.detail


def test_prose_instead_of_json_is_also_no_verdict():
    from governova_semantic import Outcome, review_result

    std = next(s for c in INDEX.constitutions for s in c.standards)
    chatty = "Sure! I looked at the code and it seems fine to me."
    result = review_result("code", standards=[std], index=INDEX, config=ACTIVE, transport=lambda c, m: chatty)
    assert result.outcome is Outcome.UNPARSEABLE


def test_an_explicit_empty_findings_list_is_a_clean_review():
    """The negative half, and the distinction the whole change rests on.

    `{"findings": []}` is the model saying *no violations*. That is a real answer and
    must stay distinguishable from no answer at all.
    """
    from governova_semantic import Outcome, review_result

    std = next(s for c in INDEX.constitutions for s in c.standards)
    result = review_result(
        "code", standards=[std], index=INDEX, config=ACTIVE,
        transport=lambda c, m: json.dumps({"findings": []}),
    )
    assert result.outcome is Outcome.REVIEWED
    assert result.ran
    assert result.findings == []


def test_describe_code_with_mock_and_inactive():
    out = describe_code("def f():\n    pass\n", config=ACTIVE, transport=lambda c, m: "  Defines f.  ")
    assert out == "Defines f."
    assert describe_code("code", config=from_env({})) == ""  # inactive


def test_relevant_standards_and_messages():
    from governova_semantic.review import ALWAYS_GROUNDED

    picked = relevant_standards(INDEX, "authentication token refresh session", limit=5)
    # `limit` bounds the *lexically matched* set. The unconditional standards are added
    # on top of it, because word overlap can never select them and they are the two the
    # tier exists to reach.
    assert len(picked) <= 5 + len(ALWAYS_GROUNDED)
    msgs = build_messages("code here", picked)
    assert msgs[0]["role"] == "system" and "code here" in msgs[1]["content"]


def test_standards_with_no_lexical_signature_are_always_submitted():
    """The recall ceiling the evaluation harness found on its first run.

    `S1.106` and `S1.107` are aphorisms — "Don't Repeat Yourself", "The Simplest Correct
    Solution" — whose words never appear in the code they govern. Both are deliberately
    left to the semantic tier because they have no *deterministic* signature, so a purely
    lexical pre-filter guaranteed the tier could never reach the two standards it exists
    for. A perfect backend scored 0.5 recall with nothing wrong with the backend.
    """
    from governova_semantic.review import ALWAYS_GROUNDED

    unrelated = "def add(a, b):\n    return a + b\n"
    picked = {s.id for s in relevant_standards(INDEX, unrelated)}
    assert set(ALWAYS_GROUNDED) <= picked


def test_the_unconditional_set_is_not_duplicated_when_it_also_matches():
    # A standard that matches lexically *and* is unconditional must appear once, or the
    # prompt carries it twice and the catalogue reads as though it mattered more.
    picked = relevant_standards(INDEX, "shared code repeat yourself simplest correct solution")
    ids = [s.id for s in picked]
    assert len(ids) == len(set(ids))


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
