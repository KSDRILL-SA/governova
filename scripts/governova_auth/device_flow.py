"""The client half of RFC 8628 — what `governova login` actually does.

Ask for a pair of codes, show the human the short one, poll until they approve
it somewhere else. The whole flow is stdlib: `urllib` rather than a new HTTP
dependency, because this runs on a developer's machine and every package added
here is one they did not ask for.

Three rules the client owes the server:

- **Honour the interval it was given.** The server sends one; a client that
  ignores it and polls in a tight loop is indistinguishable from an attack on
  the user-code keyspace.
- **Back off when told to.** `slow_down` means increase the interval, not retry
  immediately. RFC 8628 §3.5.
- **Stop at the expiry.** A login left open forever is a code left guessable
  forever.

And one it owes the user: **say what is happening.** A CLI that prints nothing
while polling looks hung, and the thing it is waiting for is an action only the
user can take.
"""

from __future__ import annotations

import dataclasses
import datetime as dt
import json
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from typing import Any

from governova_auth.store import Session

DEVICE_CODE_GRANT = "urn:ietf:params:oauth:grant-type:device_code"

# Absolute ceiling on the wait, independent of what the server says. A server
# that returns a very large `expires_in` should not be able to hold a terminal
# open indefinitely.
MAX_WAIT = dt.timedelta(minutes=15)

# Applied on `slow_down`, per RFC 8628 §3.5.
BACKOFF_INCREMENT = 5


class LoginError(RuntimeError):
    """A login that did not complete, with a sentence a person can act on."""


@dataclasses.dataclass(frozen=True)
class PendingLogin:
    """What the user is shown while they approve."""

    device_code: str
    user_code: str
    verification_uri: str
    verification_uri_complete: str
    interval: int
    expires_at: dt.datetime


def _post(url: str, payload: dict[str, Any], *, timeout: float) -> tuple[int, dict[str, Any]]:
    """POST JSON, returning the status and the decoded body.

    A non-2xx is a normal outcome here rather than an exception: RFC 8628 uses
    400 for `authorization_pending`, which is the answer for most of a login.
    """
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(  # URL is operator-supplied config
        url, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        try:
            return exc.code, json.loads(exc.read().decode("utf-8"))
        except (ValueError, OSError):
            return exc.code, {}
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        raise LoginError(
            f"could not reach the identity service at {url} — {exc}. "
            "Every other Governova command works offline; only login needs the network."
        ) from exc


def start(base_url: str, *, timeout: float = 15.0) -> PendingLogin:
    """Ask for a device code. RFC 8628 §3.1."""
    status, body = _post(f"{base_url.rstrip('/')}/api/v1/oauth/device/code", {}, timeout=timeout)
    if status != 200:
        raise LoginError(f"the identity service refused to start a login (HTTP {status})")

    return PendingLogin(
        device_code=str(body["device_code"]),
        user_code=str(body["user_code"]),
        verification_uri=str(body["verification_uri"]),
        verification_uri_complete=str(body["verification_uri_complete"]),
        interval=int(body.get("interval", 5)),
        expires_at=dt.datetime.now(dt.UTC) + dt.timedelta(seconds=int(body["expires_in"])),
    )


def poll(
    base_url: str,
    pending: PendingLogin,
    *,
    sleep: Callable[[float], None] = time.sleep,
    now: Callable[[], dt.datetime] = lambda: dt.datetime.now(dt.UTC),
    timeout: float = 15.0,
) -> Session:
    """Wait for the human, then exchange the code. RFC 8628 §3.4–3.5.

    `sleep` and `now` are injected so a test can drive the whole flow — including
    the back-off behaviour — without spending real seconds on it.
    """
    interval = pending.interval
    deadline = min(pending.expires_at, now() + MAX_WAIT)
    url = f"{base_url.rstrip('/')}/api/v1/oauth/token"

    while now() < deadline:
        sleep(interval)
        status, body = _post(
            url,
            {"grant_type": DEVICE_CODE_GRANT, "device_code": pending.device_code},
            timeout=timeout,
        )

        if status == 200:
            return _session_from(body)

        code = str(body.get("error", {}).get("code") or body.get("error") or "")
        if code == "authorization_pending":
            continue
        if code == "slow_down":
            interval += BACKOFF_INCREMENT
            continue
        if code == "access_denied":
            raise LoginError("that login was denied in the browser.")
        if code == "expired_token":
            raise LoginError("this login expired before it was approved. Try again.")
        raise LoginError(
            body.get("error", {}).get("message")
            or f"the identity service refused the login (HTTP {status})"
        )

    raise LoginError("this login expired before it was approved. Try again.")


def _session_from(body: dict[str, Any]) -> Session:
    access = str(body["access_token"])
    expires_in = int(body.get("expires_in", 900))
    return Session(
        access_token=access,
        refresh_token=str(body["refresh_token"]),
        subject=_subject_of(access),
        expires_at=dt.datetime.now(dt.UTC) + dt.timedelta(seconds=expires_in),
    )


def _subject_of(access_token: str) -> str:
    """Read `sub` out of the token without verifying it.

    **This is not authentication.** The client cannot verify a signature without
    fetching the JWKS, and it does not need to: the token is about to be sent to
    the service, which verifies it properly. This value is only ever used to
    print "logged in as …", so a forged token here would fool the user's own
    terminal and nothing else.

    Decoded by hand rather than with PyJWT because the client must not carry the
    service's dependencies — `governova[auth]` installs a keychain, not a JWT
    library and a cryptography stack.
    """
    import base64

    try:
        payload = access_token.split(".")[1]
        padded = payload + "=" * (-len(payload) % 4)
        claims = json.loads(base64.urlsafe_b64decode(padded).decode("utf-8"))
        return str(claims.get("sub", "unknown"))
    except (IndexError, ValueError, UnicodeDecodeError):
        return "unknown"


def revoke(base_url: str, access_token: str, *, timeout: float = 15.0) -> None:
    """Tell the service to forget this session.

    Failure here is not fatal to `logout`: the local session is cleared either
    way, and a user who cannot reach the network still expects logging out to
    log them out. The caller decides what to say about it.
    """
    url = f"{base_url.rstrip('/')}/api/v1/oauth/revoke"
    request = urllib.request.Request(  # URL is operator-supplied config
        url, data=b"", headers={"Authorization": f"Bearer {access_token}"}, method="POST"
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout):
            return
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        raise LoginError(f"could not reach the identity service to revoke: {exc}") from exc
