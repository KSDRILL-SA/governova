"""OAuth 2.0 Device Authorization Grant — RFC 8628.

The flow a CLI on a machine with no browser uses: `governova login` asks the
service for a pair of codes, shows the human a short one and a URL, and polls
while they approve it somewhere else.

The state lives here and nowhere else. Stage 0 has no database — that is Stage 1
— so the store is in memory and says so. What matters at this stage is that the
*rules* are right, because they are the part that is expensive to change once
tokens have been issued against them.

Four of those rules are security properties rather than conveniences:

- **The user code is short, and therefore guessable.** It is what a person types,
  so it cannot be long. RFC 8628 §5.1 is explicit that the trade-off is covered
  by rate limiting and a short expiry, both of which are enforced below.
- **The device code is not short.** It is never typed by anyone, so it carries
  the entropy the user code cannot.
- **Polling is rate limited.** A client that polls faster than the interval it
  was given is told `slow_down` rather than served, because the alternative is
  that the user code's small keyspace is searched at whatever rate a client likes.
- **A code is single use.** Once exchanged it is gone, so a device code captured
  from a log or a shell history cannot be replayed.
"""

from __future__ import annotations

import dataclasses
import datetime as dt
import secrets
from enum import StrEnum

# Ambiguous characters are removed. `0`/`O` and `1`/`I`/`L` are the pairs people
# mistype when reading a code off one screen and typing it into another, and a
# mistyped code is indistinguishable from a wrong one — the user is told their
# code is invalid and has no way to know why.
_USER_CODE_ALPHABET = "BCDFGHJKMNPQRSTVWXZ23456789"
_USER_CODE_GROUPS = 2
_USER_CODE_GROUP_SIZE = 4

DEFAULT_EXPIRY = dt.timedelta(minutes=10)
DEFAULT_INTERVAL = 5  # seconds between polls, per RFC 8628 §3.2

# How much faster than `interval` a client may poll before being told to slow
# down. A small tolerance absorbs clock jitter without weakening the limit.
_POLL_TOLERANCE = dt.timedelta(seconds=1)


class GrantState(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXCHANGED = "exchanged"


class PollOutcome(StrEnum):
    """RFC 8628 §3.5 error codes, plus success."""

    AUTHORIZATION_PENDING = "authorization_pending"
    SLOW_DOWN = "slow_down"
    ACCESS_DENIED = "access_denied"
    EXPIRED_TOKEN = "expired_token"
    INVALID_GRANT = "invalid_grant"
    APPROVED = "approved"


@dataclasses.dataclass
class DeviceGrant:
    """One in-flight authorization."""

    device_code: str
    user_code: str
    expires_at: dt.datetime
    interval: int
    state: GrantState = GrantState.PENDING
    subject: str | None = None
    last_polled_at: dt.datetime | None = None

    def is_expired(self, now: dt.datetime) -> bool:
        return now >= self.expires_at


def new_user_code() -> str:
    """A short code a person reads aloud and types. `BCDF-GH23` shape."""
    groups = [
        "".join(secrets.choice(_USER_CODE_ALPHABET) for _ in range(_USER_CODE_GROUP_SIZE))
        for _ in range(_USER_CODE_GROUPS)
    ]
    return "-".join(groups)


def normalise_user_code(raw: str) -> str:
    """What the human typed, as the code they were shown.

    Case and hyphens are cosmetic. Rejecting `bcdfgh23` when the screen said
    `BCDF-GH23` teaches nothing and costs the login.
    """
    return "".join(ch for ch in raw.upper() if ch.isalnum())


class DeviceGrantStore:
    """In-memory grants.

    **Not durable, and deliberately so.** Stage 0 ships identity without a
    database; Stage 1 brings PostgreSQL. A restart drops in-flight logins, which
    is a ten-minute inconvenience rather than a correctness problem — no issued
    token depends on this state.
    """

    def __init__(
        self,
        *,
        expiry: dt.timedelta = DEFAULT_EXPIRY,
        interval: int = DEFAULT_INTERVAL,
    ) -> None:
        self._by_device_code: dict[str, DeviceGrant] = {}
        self._by_user_code: dict[str, str] = {}
        self._expiry = expiry
        self._interval = interval

    def start(self, now: dt.datetime) -> DeviceGrant:
        """Create a grant. The device code carries the entropy; the user code is typed."""
        from governova_identity.tokens import new_opaque_secret

        user_code = new_user_code()
        while normalise_user_code(user_code) in self._by_user_code:
            user_code = new_user_code()  # pragma: no cover — collision is ~1 in 27^8

        grant = DeviceGrant(
            device_code=new_opaque_secret(),
            user_code=user_code,
            expires_at=now + self._expiry,
            interval=self._interval,
        )
        self._by_device_code[grant.device_code] = grant
        self._by_user_code[normalise_user_code(user_code)] = grant.device_code
        return grant

    def find_by_user_code(self, raw: str) -> DeviceGrant | None:
        device_code = self._by_user_code.get(normalise_user_code(raw))
        return self._by_device_code.get(device_code) if device_code else None

    def approve(self, raw_user_code: str, subject: str, now: dt.datetime) -> bool:
        """Record that a human said yes. Returns whether there was anything to approve."""
        grant = self.find_by_user_code(raw_user_code)
        if grant is None or grant.is_expired(now) or grant.state is not GrantState.PENDING:
            return False
        grant.state = GrantState.APPROVED
        grant.subject = subject
        return True

    def deny(self, raw_user_code: str, now: dt.datetime) -> bool:
        grant = self.find_by_user_code(raw_user_code)
        if grant is None or grant.is_expired(now) or grant.state is not GrantState.PENDING:
            return False
        grant.state = GrantState.DENIED
        return True

    def poll(self, device_code: str, now: dt.datetime) -> tuple[PollOutcome, DeviceGrant | None]:
        """One poll from the CLI.

        Order matters. An unknown device code is `invalid_grant` and is answered
        without consulting anything else, so a caller cannot learn from the
        response whether a code exists — the rate-limit branch below would
        otherwise be an oracle for guessing device codes.
        """
        grant = self._by_device_code.get(device_code)
        if grant is None:
            return PollOutcome.INVALID_GRANT, None

        if grant.state is GrantState.EXCHANGED:
            # Single use. A replayed device code is refused even while the
            # original grant would otherwise still be valid.
            return PollOutcome.INVALID_GRANT, None

        if grant.is_expired(now):
            return PollOutcome.EXPIRED_TOKEN, None

        if grant.last_polled_at is not None:
            earliest = grant.last_polled_at + dt.timedelta(seconds=grant.interval)
            if now + _POLL_TOLERANCE < earliest:
                # Per RFC 8628 §3.5 the client must then increase its interval.
                # The poll clock is deliberately *not* advanced here: a client
                # hammering the endpoint must not be able to hold the window open.
                return PollOutcome.SLOW_DOWN, None

        grant.last_polled_at = now

        if grant.state is GrantState.DENIED:
            return PollOutcome.ACCESS_DENIED, None
        if grant.state is GrantState.PENDING:
            return PollOutcome.AUTHORIZATION_PENDING, None

        grant.state = GrantState.EXCHANGED
        return PollOutcome.APPROVED, grant

    def purge_expired(self, now: dt.datetime) -> int:
        """Drop grants past their expiry. Returns how many went."""
        stale = [code for code, g in self._by_device_code.items() if g.is_expired(now)]
        for code in stale:
            grant = self._by_device_code.pop(code)
            self._by_user_code.pop(normalise_user_code(grant.user_code), None)
        return len(stale)

    def __len__(self) -> int:
        return len(self._by_device_code)
