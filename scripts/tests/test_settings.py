"""Tests for the single validated read of the environment.

`S1.68` asks for validation at startup rather than at the point of use. The
defect this module was written for is not that the fallbacks were wrong — they
are sensible — but that they were **silent**, so a misconfigured deployment is
indistinguishable from an unconfigured one.
"""

from __future__ import annotations

import pytest
from governova_settings import (
    ENV_CONSTITUTION,
    KNOWN,
    inspect_env,
    is_secret,
    redact,
    resolved,
)


def _problems(env: dict[str, str]) -> dict[str, str]:
    return {p.variable: p.detail for p in inspect_env(env)}


def test_an_empty_environment_is_the_supported_configuration() -> None:
    """ADR-010 §5.1 — the deterministic engine runs with nothing set.

    An unset variable must never become a finding. If it did, every offline
    install would open with a wall of complaints about a guarantee it is keeping.
    """
    assert inspect_env({}) == ()


def test_unrelated_variables_are_not_this_engines_business() -> None:
    assert inspect_env({"PATH": "/usr/bin", "HOME": "/home/t"}) == ()


@pytest.mark.parametrize(
    "variable",
    ["GOVERNOVA_LLM_TIMEOUT", "GOVERNOVA_LLM_MAX_TOKENS", "GOVERNOVA_WEBHOOK_TIMEOUT"],
)
def test_a_value_that_is_not_a_number_is_reported_rather_than_absorbed(variable: str) -> None:
    found = _problems({variable: "abc"})
    assert variable in found
    assert "not a number" in found[variable]
    # The fallback is still named, because the operator needs to know what ran.
    assert "falling back" in found[variable]


@pytest.mark.parametrize("bad", ["0", "-5"])
def test_a_non_positive_timeout_is_reported(bad: str) -> None:
    """Zero is parseable and unusable, which is the case a `try/except` misses."""
    found = _problems({"GOVERNOVA_LLM_TIMEOUT": bad})
    assert "not positive" in found["GOVERNOVA_LLM_TIMEOUT"]


def test_a_valid_number_is_not_a_problem() -> None:
    assert inspect_env({"GOVERNOVA_LLM_TIMEOUT": "45", "GOVERNOVA_LLM_MAX_TOKENS": "2048"}) == ()


def test_a_misspelled_protocol_is_reported_with_the_options() -> None:
    found = _problems({"GOVERNOVA_LLM_PROTOCOL": "mesages"})
    detail = found["GOVERNOVA_LLM_PROTOCOL"]
    assert "chat_completions" in detail and "messages" in detail


@pytest.mark.parametrize("good", ["messages", "chat_completions", "CHAT-COMPLETIONS"])
def test_the_accepted_protocol_spellings_are_not_problems(good: str) -> None:
    assert inspect_env({"GOVERNOVA_LLM_PROTOCOL": good}) == ()


def test_a_variable_name_nothing_reads_is_reported() -> None:
    """The failure mode that has no other symptom.

    A misspelled name is not a wrong value, it is an *absent* one — and absence
    is indistinguishable from "not configured", so the operator is told the tier
    is inactive, which is true and useless.
    """
    found = _problems({"GOVERNOVA_LLM_BASEURL": "http://localhost:11434/v1"})
    assert "GOVERNOVA_LLM_BASEURL" in found
    assert "not read by anything" in found["GOVERNOVA_LLM_BASEURL"]


def test_every_known_variable_is_accepted_without_complaint() -> None:
    """The unknown-name check must not fire on the names this engine documents."""
    env = {name: "1" for name in KNOWN if "TIMEOUT" not in name and "TOKENS" not in name}
    env.pop(ENV_CONSTITUTION, None)
    env["GOVERNOVA_LLM_PROTOCOL"] = "messages"
    env["GOVERNOVA_WEBHOOK_URL"] = "https://example.invalid/hook"
    unknown = [v for v, detail in _problems(env).items() if "not read by anything" in detail]
    assert not unknown


def test_a_partly_configured_semantic_tier_is_reported() -> None:
    """The tier reports itself inactive, which is true and hides the gap."""
    found = _problems(
        {"GOVERNOVA_LLM_MODEL": "qwen", "GOVERNOVA_LLM_API_KEY": "sk-x"}
    )
    assert any("GOVERNOVA_LLM_BASE_URL" in variable for variable in found)


def test_a_fully_configured_semantic_tier_is_not_reported() -> None:
    assert (
        inspect_env(
            {
                "GOVERNOVA_LLM_MODEL": "qwen",
                "GOVERNOVA_LLM_BASE_URL": "http://localhost:11434/v1",
                "GOVERNOVA_LLM_API_KEY": "sk-x",
            }
        )
        == ()
    )


def test_a_webhook_that_is_not_http_is_reported() -> None:
    found = _problems({"GOVERNOVA_WEBHOOK_URL": "localhost/hook"})
    assert "http" in found["GOVERNOVA_WEBHOOK_URL"]


def test_a_constitution_path_that_does_not_exist_is_reported(tmp_path) -> None:
    found = _problems({ENV_CONSTITUTION: str(tmp_path / "nope.json")})
    assert "not a readable file" in found[ENV_CONSTITUTION]


def test_a_constitution_path_that_exists_is_not_reported(tmp_path) -> None:
    target = tmp_path / "constitution.json"
    target.write_text("{}", encoding="utf-8")
    assert inspect_env({ENV_CONSTITUTION: str(target)}) == ()


# ── Secrets ──────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "variable",
    ["GOVERNOVA_LLM_API_KEY", "GOVERNOVA_WEBHOOK_URL", "SOME_TOKEN", "DB_PASSWORD"],
)
def test_credential_shaped_names_are_secret(variable: str) -> None:
    """Matched by shape, so a variable added later is redacted without being remembered."""
    assert is_secret(variable)


def test_a_secret_is_never_shown_even_partially() -> None:
    """Not a prefix, not a suffix, not a hash — a length and nothing else."""
    secret = "sk-live-abcdef123456"
    shown = redact("GOVERNOVA_LLM_API_KEY", secret)
    assert "sk-" not in shown
    assert "abcdef" not in shown
    assert str(len(secret)) in shown


def test_an_empty_secret_is_distinguished_from_an_absent_one() -> None:
    """A failed substitution sets the variable to "" — which is not the same as unset."""
    assert redact("GOVERNOVA_LLM_API_KEY", "") == "<set but empty>"


def test_a_non_secret_is_shown_as_supplied() -> None:
    assert redact("GOVERNOVA_LLM_MODEL", "qwen2.5-coder") == "qwen2.5-coder"


def test_resolved_redacts_every_secret_it_reports() -> None:
    env = dict.fromkeys(KNOWN, "supersecretvalue")
    for setting in resolved(env):
        if is_secret(setting.variable):
            assert "supersecretvalue" not in setting.shown


def test_resolved_covers_every_known_variable() -> None:
    assert {s.variable for s in resolved({})} == set(KNOWN)
    assert all(not s.set for s in resolved({}))
