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
    declares_semantic_tier,
    describe_code,
    parse_findings,
    relevant_standards,
    review,
    semantic_pool,
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
        {
            "findings": [
                {"standard": "S2.34", "line": 5, "message": "money as float"},
                {"standard": "S99.99", "line": 1, "message": "not a real standard"},
            ]
        }
    )
    out = parse_findings(content, allowed_ids={"S2.34"})
    assert len(out) == 1 and out[0].standard == "S2.34" and out[0].line == 5


def test_parse_drops_findings_the_model_is_unsure_about():
    """The ungrounded-citation filter, applied to certainty instead of identity.

    Measured on `gpt-oss:120b-cloud`, 5 runs per condition: worst-run precision
    45% → 53% with recall held at 90%, and the 53% floor reproduced across a
    second five runs. The verdict uses the worst run, so the floor is the number
    that moved.
    """
    content = json.dumps(
        {
            "findings": [
                {"standard": "S2.34", "message": "money as float", "confidence": "high"},
                {"standard": "S2.34", "message": "arguable", "confidence": "medium"},
                {"standard": "S2.34", "message": "a stretch", "confidence": "low"},
            ]
        }
    )
    out = parse_findings(content, allowed_ids={"S2.34"})
    assert [f.message for f in out] == ["money as float"]


def test_parse_keeps_a_finding_that_carries_no_confidence():
    """A backend that ignores the field must not be silently emptied.

    Dropping unmarked findings would turn any endpoint that does not implement
    the schema into a tier reporting a clean review it never performed — the
    exact failure `Outcome.UNPARSEABLE` exists to prevent. Keeping is also the
    only direction that cannot cost recall.
    """
    content = json.dumps({"findings": [{"standard": "S2.34", "message": "no confidence field"}]})
    assert len(parse_findings(content, allowed_ids={"S2.34"})) == 1

    unrecognised = json.dumps(
        {"findings": [{"standard": "S2.34", "message": "x", "confidence": "probably"}]}
    )
    assert len(parse_findings(unrecognised, allowed_ids={"S2.34"})) == 1


def test_the_prompt_asks_for_the_confidence_it_filters_on():
    """Filtering on a field the model was never asked for would drop nothing.

    Cheap, and it is the setup check rather than the result check — the class of
    gate that has repeatedly paid for itself here.
    """
    from governova_semantic.review import build_messages

    std = next(s for c in INDEX.constitutions for s in c.standards)
    system = build_messages("x = 1", [std])[0]["content"]
    assert "confidence" in system
    for level in ("high", "medium", "low"):
        assert level in system


def test_parse_handles_code_fenced_json():
    content = (
        "```json\n" + json.dumps({"findings": [{"standard": "S2.1", "message": "x"}]}) + "\n```"
    )
    out = parse_findings(content, allowed_ids={"S2.1"})
    assert len(out) == 1 and out[0].standard == "S2.1"


def test_review_with_mock_transport_keeps_only_grounded():
    std = next(s for c in INDEX.constitutions for s in c.standards)  # a real standard

    def fake_transport(cfg, messages):
        return json.dumps(
            {
                "findings": [
                    {"standard": std.id, "line": 3, "message": "violates this"},
                    {"standard": "S88.88", "line": 9, "message": "hallucinated"},
                ]
            }
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
        if "test_semantic" not in p.name
        and "models.github.ai" in p.read_text(encoding="utf-8", errors="replace")
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
    result = review_result(
        "code", standards=[std], index=INDEX, config=ACTIVE, transport=lambda c, m: ""
    )
    assert result.outcome is Outcome.UNPARSEABLE
    assert not result.ran
    assert "MAX_TOKENS" in result.detail


def test_prose_instead_of_json_is_also_no_verdict():
    from governova_semantic import Outcome, review_result

    std = next(s for c in INDEX.constitutions for s in c.standards)
    chatty = "Sure! I looked at the code and it seems fine to me."
    result = review_result(
        "code", standards=[std], index=INDEX, config=ACTIVE, transport=lambda c, m: chatty
    )
    assert result.outcome is Outcome.UNPARSEABLE


def test_an_explicit_empty_findings_list_is_a_clean_review():
    """The negative half, and the distinction the whole change rests on.

    `{"findings": []}` is the model saying *no violations*. That is a real answer and
    must stay distinguishable from no answer at all.
    """
    from governova_semantic import Outcome, review_result

    std = next(s for c in INDEX.constitutions for s in c.standards)
    result = review_result(
        "code",
        standards=[std],
        index=INDEX,
        config=ACTIVE,
        transport=lambda c, m: json.dumps({"findings": []}),
    )
    assert result.outcome is Outcome.REVIEWED
    assert result.ran
    assert result.findings == []


def test_describe_code_with_mock_and_inactive():
    out = describe_code(
        "def f():\n    pass\n", config=ACTIVE, transport=lambda c, m: "  Defines f.  "
    )
    assert out == "Defines f."
    assert describe_code("code", config=from_env({})) == ""  # inactive


def test_the_pool_is_exactly_what_declares_the_tier():
    """Membership is a declaration in `enforced_by`, not an inference from vocabulary."""
    pool = semantic_pool(INDEX)
    assert pool, "no standard declares the semantic tier — the tier would review nothing"
    assert all(declares_semantic_tier(s) for s in pool)
    declared = {s.id for c in INDEX.constitutions for s in c.standards if declares_semantic_tier(s)}
    assert {s.id for s in pool} == declared, "the pool must not add or drop anything"


def test_selection_does_not_depend_on_the_words_in_the_code():
    """The defect that made the first measurement round meaningless.

    The old pre-filter ranked all 670 standards by title-word overlap against the
    identifiers in the code. On a loan-assessment handler all twelve it chose matched a
    single incidental token — `async` selected "Async Standup Replaces Synchronous Daily
    Meetings", `debt` selected "The System Maintains a Debt Register" — while `S1.103` and
    `S1.105`, which the code actually violated, scored zero and were never submitted. The
    tier was scored on standards it was never shown.

    Two snippets sharing no vocabulary must now be reviewed against the same standards,
    because what the tier is responsible for does not depend on what a variable is called.
    """
    arithmetic = "def add(a, b):\n    return a + b\n"
    handler = '@router.post("/loans")\nasync def assess(application):\n    return {}\n'
    assert [s.id for s in relevant_standards(INDEX, arithmetic)] == [
        s.id for s in relevant_standards(INDEX, handler)
    ]


def test_standards_with_no_lexical_signature_are_still_submitted():
    """The recall ceiling the evaluation harness found on its first run.

    `S1.106` and `S1.107` are aphorisms — "Don't Repeat Yourself", "The Simplest Correct
    Solution" — whose words never appear in the code they govern. They were once carried
    by a hardcoded `ALWAYS_GROUNDED` list, which fixed the two known cases and left every
    other standard of the same kind unreachable. Declaring the tier covers them all.
    """
    picked = {s.id for s in relevant_standards(INDEX, "def add(a, b):\n    return a + b\n")}
    assert {"S1.106", "S1.107"} <= picked


def test_ranking_only_applies_once_the_pool_outgrows_the_budget():
    pool = semantic_pool(INDEX)
    assert len(relevant_standards(INDEX, "code", limit=len(pool))) == len(pool)
    squeezed = relevant_standards(INDEX, "code", limit=2)
    assert len(squeezed) == 2
    ids = [s.id for s in squeezed]
    assert len(ids) == len(set(ids))


def test_messages_carry_the_catalogue_and_the_code():
    msgs = build_messages("code here", relevant_standards(INDEX, "code here"))
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


# ─── Transient failures versus real ones ────────────────────────────────────


def _stub_urlopen(responses):
    """Serve `responses` in order: an int raises that HTTP status, a dict is a body."""
    import urllib.error

    calls = {"n": 0}

    def urlopen(request, timeout=None):
        calls["n"] += 1
        item = responses[min(calls["n"] - 1, len(responses) - 1)]
        if isinstance(item, int):
            raise urllib.error.HTTPError("https://endpoint.example/v1", item, "err", {}, None)
        if isinstance(item, BaseException):
            raise item

        payload = json.dumps(item).encode("utf-8")

        class _Resp:
            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

            def read(self):
                return payload

        return _Resp()

    return urlopen, calls


def _patched(monkeypatch, responses):
    import governova_semantic.client as client_mod

    urlopen, calls = _stub_urlopen(responses)
    monkeypatch.setattr(client_mod.urllib.request, "urlopen", urlopen)
    monkeypatch.setattr(client_mod.time, "sleep", lambda _s: None)  # no real backoff in tests
    return calls


def test_a_transient_status_is_retried_and_can_succeed(monkeypatch):
    """A single 502 partway through a run must not lose the whole measurement.

    An evaluation makes tens of sequential calls, and a hosted backend returned an
    isolated 502 more than once. The harness correctly refuses to report a partial
    score, so one blip made the measurement impossible to take at all.
    """
    from governova_semantic.client import _post

    body = {"choices": [{"message": {"content": "{}"}}]}
    calls = _patched(monkeypatch, [502, body])
    assert _post(ACTIVE, {}, {}) == body
    assert calls["n"] == 2, "the first attempt should have been retried"


def test_a_retry_never_turns_an_outage_into_silence(monkeypatch):
    from governova_semantic.client import MAX_ATTEMPTS, SemanticUnavailableError, _post

    calls = _patched(monkeypatch, [503])
    with pytest.raises(SemanticUnavailableError) as excinfo:
        _post(ACTIVE, {}, {})
    assert excinfo.value.status == 503, "the real status must survive every retry"
    assert calls["n"] == MAX_ATTEMPTS, "retries are bounded, so an outage still fails promptly"


def test_a_definitive_answer_is_not_retried(monkeypatch):
    """401, 404 and 410 are answers. Retrying them wastes a build and tells nobody anything."""
    from governova_semantic.client import SemanticUnavailableError, _post

    for status in (401, 404, 410):
        calls = _patched(monkeypatch, [status])
        with pytest.raises(SemanticUnavailableError):
            _post(ACTIVE, {}, {})
        assert calls["n"] == 1, f"HTTP {status} must fail on the first attempt"


def test_a_timeout_is_retried_even_though_it_carries_no_status(monkeypatch):
    """A `502` got three attempts and a timeout got one, on the same endpoint.

    Retrying was decided by HTTP status, and a timeout has none, so it matched nothing
    and failed on the first attempt. Measured: 14 consecutive single-run evaluations lost
    to `semantic endpoint unreachable (TimeoutError)` while direct probes of that same
    endpoint were still answering 200. A timeout is not a verdict — the endpoint said
    nothing, so nothing has been ruled out.
    """
    from governova_semantic.client import _post

    body = {"choices": [{"message": {"content": "{}"}}]}
    calls = _patched(monkeypatch, [TimeoutError("timed out"), body])
    assert _post(ACTIVE, {}, {}) == body
    assert calls["n"] == 2, "a timeout should have been retried"


def test_a_connect_timeout_wrapped_in_urlerror_is_also_retried(monkeypatch):
    """`urlopen` reports a read timeout bare and a connect timeout wrapped."""
    import urllib.error

    from governova_semantic.client import _post

    body = {"choices": [{"message": {"content": "{}"}}]}
    wrapped = urllib.error.URLError(TimeoutError("timed out"))
    calls = _patched(monkeypatch, [wrapped, body])
    assert _post(ACTIVE, {}, {}) == body
    assert calls["n"] == 2, "both spellings of a timeout must be retried"


def test_a_status_less_failure_that_is_not_a_timeout_still_fails_fast(monkeypatch):
    """The negative case, and the one that keeps the retry narrow.

    A refused connection, a DNS failure and a malformed body are answers. Retrying them
    wastes a build and rules nothing out, so only a timeout earns another attempt.
    """
    import urllib.error

    from governova_semantic.client import SemanticUnavailableError, _post

    for failure in (
        urllib.error.URLError(ConnectionRefusedError("refused")),
        OSError("dns"),
        ValueError("malformed body"),
    ):
        calls = _patched(monkeypatch, [failure])
        with pytest.raises(SemanticUnavailableError):
            _post(ACTIVE, {}, {})
        assert calls["n"] == 1, f"{failure!r} must fail on the first attempt"


def test_a_timeout_outage_still_fails_and_keeps_its_diagnosis(monkeypatch):
    """A retry must never turn an outage into silence, timeouts included."""
    from governova_semantic.client import MAX_ATTEMPTS, SemanticUnavailableError, _post

    calls = _patched(monkeypatch, [TimeoutError("timed out")])
    with pytest.raises(SemanticUnavailableError) as excinfo:
        _post(ACTIVE, {}, {})
    assert "TimeoutError" in str(excinfo.value), "the cause must survive every retry"
    assert calls["n"] == MAX_ATTEMPTS, "retries stay bounded, so an outage fails promptly"
