"""Where a session lives: the OS keychain, and nowhere else.

`#254`'s third acceptance criterion is absolute — *no token is ever written to
disk in plaintext by any path, including error handling* — and it asks for that
to be asserted by test rather than by inspection.

So this module has no file path in it at all. There is no cache location, no
fallback file, no "temporary" write. The failure mode being designed out is not
a bug someone would introduce deliberately; it is the perfectly reasonable
fallback somebody adds later so that login works on a headless box, which then
leaves a bearer token in a dotfile on every developer machine that ever ran it.

**When there is no keychain, login refuses.** That is worse ergonomics and it is
the only honest option: a credential store that silently degrades to a plaintext
file is not a credential store. The CI path is an organisation-scoped API key,
which is a different credential with different revocation properties, and it
arrives with Stage 1's organisations.
"""

from __future__ import annotations

import dataclasses
import datetime as dt
import json
from typing import Any

SERVICE_NAME = "governova"
ACCOUNT = "default"


class KeychainUnavailableError(RuntimeError):
    """No OS credential store. Never fallen back from — see the module docstring."""

    def __init__(self, detail: str = "") -> None:
        super().__init__(
            "No OS keychain is available, so there is nowhere safe to keep a session.\n"
            "Governova will not write a token to a file — a bearer token in a dotfile "
            "outlives the session, survives backups, and is readable by anything that "
            "can read your home directory.\n"
            + (f"\nThe keyring library reported: {detail}\n" if detail else "")
            + "\nOn a headless machine or in CI, use an organisation API key instead of "
            "an interactive login."
        )


@dataclasses.dataclass(frozen=True)
class Session:
    """What is kept between commands.

    The access token is here because the alternative is asking for it again on
    every invocation, which a CLI cannot do. It is kept in the OS credential
    store, which is the same place the platform keeps every other secret.
    """

    access_token: str
    refresh_token: str
    subject: str
    expires_at: dt.datetime

    def is_expired(self, now: dt.datetime | None = None) -> bool:
        return (now or dt.datetime.now(dt.UTC)) >= self.expires_at

    def to_json(self) -> str:
        return json.dumps(
            {
                "access_token": self.access_token,
                "refresh_token": self.refresh_token,
                "subject": self.subject,
                "expires_at": self.expires_at.isoformat(),
            }
        )

    @classmethod
    def from_json(cls, raw: str) -> Session | None:
        """A stored session, or None when the stored value is unreadable.

        Unreadable is treated as absent rather than as an error: a keychain entry
        written by an older version is not something a user can act on, and
        telling them to log in again is both true and useful.
        """
        try:
            data: dict[str, Any] = json.loads(raw)
            return cls(
                access_token=str(data["access_token"]),
                refresh_token=str(data["refresh_token"]),
                subject=str(data["subject"]),
                expires_at=dt.datetime.fromisoformat(str(data["expires_at"])),
            )
        except (ValueError, KeyError, TypeError):
            return None

    def __repr__(self) -> str:
        """Never the tokens.

        A session reaching a log, a traceback or a `--verbose` dump goes through
        this. `dataclasses` would otherwise print both tokens in full, and the
        place that happens is an error path — exactly where nobody is looking.
        """
        return f"Session(subject={self.subject!r}, expires_at={self.expires_at.isoformat()!r})"

    __str__ = __repr__


class KeychainStore:
    """The OS credential store, behind a seam tests can replace."""

    def __init__(self, service: str = SERVICE_NAME, account: str = ACCOUNT) -> None:
        self.service = service
        self.account = account

    def _keyring(self) -> Any:
        try:
            import keyring
        except ModuleNotFoundError as exc:  # pragma: no cover - exercised via the CLI
            raise KeychainUnavailableError(
                "the `keyring` package is not installed — `pip install governova[auth]`"
            ) from exc
        return keyring

    def save(self, session: Session) -> None:
        keyring = self._keyring()
        try:
            keyring.set_password(self.service, self.account, session.to_json())
        except Exception as exc:
            raise KeychainUnavailableError(str(exc)) from exc

    def load(self) -> Session | None:
        keyring = self._keyring()
        try:
            raw = keyring.get_password(self.service, self.account)
        except Exception as exc:
            raise KeychainUnavailableError(str(exc)) from exc
        return Session.from_json(raw) if raw else None

    def clear(self) -> bool:
        """Remove the stored session. Returns whether there was one.

        A missing entry is not an error: `logout` when already logged out should
        say so calmly rather than fail.
        """
        keyring = self._keyring()
        try:
            if keyring.get_password(self.service, self.account) is None:
                return False
            keyring.delete_password(self.service, self.account)
        except Exception as exc:
            raise KeychainUnavailableError(str(exc)) from exc
        return True


class MemoryStore:
    """An in-process store, for tests only.

    Deliberately not exported as a fallback. Its existence is why the keychain
    path can be tested without a keychain, and it never touches a filesystem —
    so a test using it cannot accidentally establish that writing to disk is fine.
    """

    def __init__(self) -> None:
        self._value: str | None = None

    def save(self, session: Session) -> None:
        self._value = session.to_json()

    def load(self) -> Session | None:
        return Session.from_json(self._value) if self._value else None

    def clear(self) -> bool:
        had = self._value is not None
        self._value = None
        return had
