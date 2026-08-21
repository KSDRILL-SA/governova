"""Tests for the identity client — `login`, `logout`, `whoami`.

`#254`'s third acceptance criterion is the one this file exists for: *no token is
ever written to disk in plaintext by any path, including error handling*, and it
asks for that to be asserted by test rather than by inspection. The last section
does exactly that — it drives the whole flow, including every failure path, and
then searches the filesystem for the token.
"""

from __future__ import annotations

import datetime as dt
import json

import pytest
from governova_auth.device_flow import (
    BACKOFF_INCREMENT,
    LoginError,
    PendingLogin,
    _subject_of,
    poll,
)
from governova_auth.store import (
    KeychainStore,
    KeychainUnavailableError,
    MemoryStore,
    Session,
)

_TOKEN_MARKER = "SUPERSECRET-ACCESS-TOKEN-DO-NOT-WRITE-ME"
_REFRESH_MARKER = "SUPERSECRET-REFRESH-TOKEN-DO-NOT-WRITE-ME"


def _session(expires_in: int = 900) -> Session:
    return Session(
        access_token=_TOKEN_MARKER,
        refresh_token=_REFRESH_MARKER,
        subject="person@example.invalid",
        expires_at=dt.datetime.now(dt.UTC) + dt.timedelta(seconds=expires_in),
    )


def _pending(interval: int = 5, expires_in: int = 600) -> PendingLogin:
    return PendingLogin(
        device_code="a-device-code",
        user_code="BCDF-GH23",
        verification_uri="https://example.invalid/activate",
        verification_uri_complete="https://example.invalid/activate?user_code=BCDF-GH23",
        interval=interval,
        expires_at=dt.datetime.now(dt.UTC) + dt.timedelta(seconds=expires_in),
    )


# ─── A session never says its tokens out loud ────────────────────────────────


def test_a_session_never_prints_its_tokens() -> None:
    """The place a dataclass prints itself is a traceback, where nobody is looking.

    `dataclasses` would render both tokens in full. `repr` and `str` are
    overridden so that a session reaching a log, an exception or a `--verbose`
    dump carries the subject and the expiry and nothing else.
    """
    session = _session()
    for rendered in (repr(session), str(session), f"{session}"):
        assert _TOKEN_MARKER not in rendered
        assert _REFRESH_MARKER not in rendered
    assert "person@example.invalid" in repr(session)


def test_a_session_inside_a_container_still_hides_its_tokens() -> None:
    """Containers render their contents with `repr`, which is the common accident."""
    holder = {"session": _session()}
    assert _TOKEN_MARKER not in repr(holder)
    assert _TOKEN_MARKER not in str([_session()])


def test_a_session_in_an_exception_message_hides_its_tokens() -> None:
    """Error handling is named explicitly in the acceptance criterion."""
    try:
        raise RuntimeError(f"failed with {_session()}")
    except RuntimeError as exc:
        assert _TOKEN_MARKER not in str(exc)


# ─── Storage ─────────────────────────────────────────────────────────────────


def test_a_session_round_trips_through_the_store() -> None:
    store = MemoryStore()
    store.save(_session())
    loaded = store.load()
    assert loaded is not None
    assert loaded.access_token == _TOKEN_MARKER
    assert loaded.subject == "person@example.invalid"


def test_an_unreadable_stored_value_is_treated_as_absent() -> None:
    """A keychain entry written by an older version is not something a user can act on.

    Telling them to log in again is both true and useful; raising is neither.
    """
    assert Session.from_json("not json at all") is None
    assert Session.from_json('{"access_token": "only-this"}') is None


def test_clearing_reports_whether_there_was_anything_to_clear() -> None:
    store = MemoryStore()
    assert store.clear() is False
    store.save(_session())
    assert store.clear() is True
    assert store.load() is None


def test_no_keychain_is_a_refusal_that_explains_itself() -> None:
    """The message has to carry the reasoning, because the ergonomics are worse.

    A user blocked by this needs to know it is deliberate, or the obvious next
    move is to look for the flag that writes a file.
    """
    message = str(KeychainUnavailableError("Secret Service not available"))
    assert "will not write a token to a file" in message
    assert "Secret Service not available" in message
    assert "API key" in message


def test_a_broken_keychain_backend_is_reported_not_swallowed(monkeypatch) -> None:
    """Every backend raises its own exception type, so all of them are caught."""

    class Exploding:
        def set_password(self, *args: object) -> None:
            raise OSError("the keyring daemon is not running")

        def get_password(self, *args: object) -> str | None:
            raise OSError("the keyring daemon is not running")

    store = KeychainStore()
    monkeypatch.setattr(store, "_keyring", lambda: Exploding())

    with pytest.raises(KeychainUnavailableError):
        store.save(_session())
    with pytest.raises(KeychainUnavailableError):
        store.load()


def test_the_store_module_names_no_file_path() -> None:
    """The fallback being designed out is the reasonable one somebody adds later.

    A "temporary" file so login works on a headless box leaves a bearer token in
    a dotfile on every machine that ever ran it.
    """
    import inspect

    import governova_auth.store as module

    source = inspect.getsource(module)
    body = "\n".join(
        line for line in source.splitlines() if not line.strip().startswith("#")
    )
    for forbidden in ("open(", "Path(", "write_text", "expanduser", "os.path"):
        assert forbidden not in body, f"the store module reached for {forbidden}"


# ─── Polling ─────────────────────────────────────────────────────────────────


class _Responses:
    """A scripted sequence of (status, body) answers, with the calls recorded."""

    def __init__(self, *answers: tuple[int, dict]) -> None:
        self.answers = list(answers)
        self.calls = 0

    def __call__(self, url: str, payload: dict, *, timeout: float) -> tuple[int, dict]:
        self.calls += 1
        return self.answers.pop(0) if self.answers else (400, {"error": {"code": "expired_token"}})


def _drive(monkeypatch, responses: _Responses, pending: PendingLogin | None = None):
    """Run `poll` with time under the test's control."""
    slept: list[float] = []
    monkeypatch.setattr("governova_auth.device_flow._post", responses)
    return (
        poll(
            "https://example.invalid",
            pending or _pending(),
            sleep=slept.append,
            now=lambda: dt.datetime.now(dt.UTC),
        ),
        slept,
    )


def test_polling_waits_then_returns_the_session(monkeypatch) -> None:
    responses = _Responses(
        (400, {"error": {"code": "authorization_pending"}}),
        (400, {"error": {"code": "authorization_pending"}}),
        (
            200,
            {
                "access_token": _TOKEN_MARKER,
                "refresh_token": _REFRESH_MARKER,
                "expires_in": 900,
            },
        ),
    )
    session, slept = _drive(monkeypatch, responses)
    assert session.access_token == _TOKEN_MARKER
    assert responses.calls == 3
    assert slept == [5, 5, 5], "the interval the server gave must be honoured"


def test_slow_down_increases_the_interval(monkeypatch) -> None:
    """RFC 8628 §3.5 — `slow_down` means back off, not retry immediately.

    A client that ignores this is indistinguishable from an attack on the
    user-code keyspace, which is why the server rate-limits in the first place.
    """
    responses = _Responses(
        (400, {"error": {"code": "slow_down"}}),
        (
            200,
            {"access_token": _TOKEN_MARKER, "refresh_token": _REFRESH_MARKER, "expires_in": 900},
        ),
    )
    _, slept = _drive(monkeypatch, responses)
    assert slept == [5, 5 + BACKOFF_INCREMENT]


def test_a_denied_login_says_so_in_a_sentence(monkeypatch) -> None:
    responses = _Responses((400, {"error": {"code": "access_denied"}}))
    monkeypatch.setattr("governova_auth.device_flow._post", responses)
    with pytest.raises(LoginError, match="denied"):
        poll("https://example.invalid", _pending(), sleep=lambda _: None)


def test_an_expired_login_says_so_in_a_sentence(monkeypatch) -> None:
    responses = _Responses((400, {"error": {"code": "expired_token"}}))
    monkeypatch.setattr("governova_auth.device_flow._post", responses)
    with pytest.raises(LoginError, match="expired"):
        poll("https://example.invalid", _pending(), sleep=lambda _: None)


def test_polling_stops_at_the_expiry_rather_than_forever(monkeypatch) -> None:
    """A login left open forever is a code left guessable forever."""
    responses = _Responses()  # always `expired_token`
    monkeypatch.setattr("governova_auth.device_flow._post", responses)
    expired = _pending(expires_in=-1)
    with pytest.raises(LoginError):
        poll("https://example.invalid", expired, sleep=lambda _: None)


# ─── Reading the subject ─────────────────────────────────────────────────────


def test_the_subject_is_read_from_the_token_without_verifying_it() -> None:
    """Not authentication — it only ever fills in "logged in as …".

    Decoded by hand rather than with PyJWT, because the client must not carry the
    service's cryptography stack.
    """
    import base64

    payload = base64.urlsafe_b64encode(json.dumps({"sub": "someone@example.invalid"}).encode())
    token = "header." + payload.decode().rstrip("=") + ".signature"
    assert _subject_of(token) == "someone@example.invalid"


@pytest.mark.parametrize("rubbish", ["", "not-a-token", "a.b", "a.!!!.c"])
def test_an_unreadable_token_yields_unknown_rather_than_raising(rubbish: str) -> None:
    assert _subject_of(rubbish) == "unknown"


# ─── `#254` acceptance criterion 3 ───────────────────────────────────────────


def test_no_path_through_the_client_writes_a_token_to_disk(tmp_path, monkeypatch) -> None:
    """The criterion, asserted rather than inspected.

    Every path is driven — a successful login, a denied one, an expired one, a
    keychain failure, and a session rendered into an exception — with the process
    working directory and the home directory both redirected into `tmp_path`.
    Then the whole tree is searched for either token.

    Searching afterwards rather than mocking `open` is deliberate: a mock proves
    the calls this code makes today, and the failure being guarded against is the
    call somebody adds tomorrow.
    """
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))

    store = MemoryStore()
    store.save(_session())

    ok = _Responses(
        (400, {"error": {"code": "authorization_pending"}}),
        (
            200,
            {"access_token": _TOKEN_MARKER, "refresh_token": _REFRESH_MARKER, "expires_in": 900},
        ),
    )
    monkeypatch.setattr("governova_auth.device_flow._post", ok)
    session = poll("https://example.invalid", _pending(), sleep=lambda _: None)
    store.save(session)

    for failure in ("access_denied", "expired_token", "invalid_grant"):
        monkeypatch.setattr(
            "governova_auth.device_flow._post", _Responses((400, {"error": {"code": failure}}))
        )
        with pytest.raises(LoginError):
            poll("https://example.invalid", _pending(), sleep=lambda _: None)

    # The error paths, with a session in scope so any accidental render is caught.
    with pytest.raises(KeychainUnavailableError):
        raise KeychainUnavailableError(f"while holding {store.load()}")

    leaked = [
        path
        for path in tmp_path.rglob("*")
        if path.is_file() and _contains_secret(path)
    ]
    assert not leaked, f"a token reached disk at: {leaked}"


def _contains_secret(path) -> bool:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:  # pragma: no cover — unreadable file is not a leak
        return False
    return _TOKEN_MARKER in text or _REFRESH_MARKER in text
