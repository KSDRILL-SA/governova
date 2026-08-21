"""The client and the service, over a real socket.

Everything else tests one half against a stub. This runs the actual FastAPI app
on a real port and drives the actual `urllib` client against it, because the
seams between them are where a login breaks: a path that does not match, an
error envelope the other side does not read, a status code nobody expected.

Skipped when the `cloud` extra is absent, which is the honest behaviour — the
service is an extra and a machine without it cannot run its service.
"""

from __future__ import annotations

import contextlib
import socket
import threading
import time
from collections.abc import Iterator

import pytest

pytest.importorskip("fastapi", reason="the identity service is an extra: governova[cloud]")
uvicorn = pytest.importorskip("uvicorn", reason="the identity service is an extra")

import urllib.request  # noqa: E402

from governova_auth.device_flow import LoginError, poll, revoke, start  # noqa: E402
from governova_identity.app import IdentityService, create_app  # noqa: E402
from governova_identity.tokens import SigningKey  # noqa: E402


def _free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


@pytest.fixture(scope="module")
def live_service() -> Iterator[str]:
    """The real app, on a real port, in a background thread."""
    port = _free_port()
    base = f"http://127.0.0.1:{port}"
    service = IdentityService(SigningKey.generate(), base_url=base)
    config = uvicorn.Config(
        create_app(service), host="127.0.0.1", port=port, log_level="error"
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        with (
            contextlib.suppress(OSError),
            urllib.request.urlopen(f"{base}/health", timeout=1) as response,
        ):
            if response.status == 200:
                break
        time.sleep(0.1)
    else:  # pragma: no cover - the service failed to come up
        pytest.fail("the identity service did not start")

    yield base

    server.should_exit = True
    thread.join(timeout=10)


def _approve(base: str, user_code: str, subject: str, *, approve: bool = True) -> int:
    """The browser half, as an HTTP call."""
    import json

    request = urllib.request.Request(
        f"{base}/api/v1/oauth/device/approve",
        data=json.dumps(
            {"user_code": user_code, "subject": subject, "approve": approve}
        ).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        return int(response.status)


def test_a_whole_login_works_over_the_wire(live_service: str) -> None:
    """Start, approve, poll, and get a session the service accepts.

    The one test that would catch a path mismatch, an envelope the other side
    cannot read, or a status code the client does not handle.
    """
    pending = start(live_service)
    assert pending.user_code
    assert pending.verification_uri.startswith(live_service)

    assert _approve(live_service, pending.user_code, "person@example.invalid") == 200

    session = poll(live_service, pending, sleep=lambda _: None)
    assert session.subject == "person@example.invalid"

    request = urllib.request.Request(
        f"{live_service}/api/v1/me",
        headers={"Authorization": f"Bearer {session.access_token}"},
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        assert response.status == 200


def test_a_login_the_user_typed_in_lower_case_still_works(live_service: str) -> None:
    """The code is shown upper case with a hyphen; people type what they like."""
    pending = start(live_service)
    typed = pending.user_code.lower().replace("-", "")
    assert _approve(live_service, typed, "person@example.invalid") == 200
    assert poll(live_service, pending, sleep=lambda _: None).subject == "person@example.invalid"


def test_a_denied_login_reaches_the_client_as_a_sentence(live_service: str) -> None:
    pending = start(live_service)
    _approve(live_service, pending.user_code, "person@example.invalid", approve=False)
    with pytest.raises(LoginError, match="denied"):
        poll(live_service, pending, sleep=lambda _: None)


def test_logout_revokes_and_the_session_stops_working(live_service: str) -> None:
    """`#254` criterion 2, end to end: revocation actually stops the token."""
    pending = start(live_service)
    _approve(live_service, pending.user_code, "person@example.invalid")
    session = poll(live_service, pending, sleep=lambda _: None)

    revoke(live_service, session.access_token)

    request = urllib.request.Request(
        f"{live_service}/api/v1/me",
        headers={"Authorization": f"Bearer {session.access_token}"},
    )
    with pytest.raises(urllib.error.HTTPError) as caught:
        urllib.request.urlopen(request, timeout=5)
    assert caught.value.code == 401


def test_the_client_says_something_useful_when_nothing_is_listening() -> None:
    """An unreachable service must not surface as a stack trace.

    And the message says the thing a user most needs to hear: this is the only
    command that needs a network.
    """
    dead = f"http://127.0.0.1:{_free_port()}"
    with pytest.raises(LoginError) as caught:
        start(dead, timeout=2)
    assert "could not reach" in str(caught.value)
    assert "offline" in str(caught.value)
