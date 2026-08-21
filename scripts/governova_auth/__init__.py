"""governova_auth — the client half of identity. `login`, `logout`, `whoami`.

Separate from `governova_identity` because a client and a service are different
things with different dependencies. Someone running `governova login` on their
laptop needs a keychain; they do not need a web framework, an ASGI server and a
cryptography stack, and `governova[auth]` gives them only the first.

Nothing here is imported by any deterministic command. `ADR-010` §5.1 guarantees
the engine runs complete and offline forever, and `test_identity_isolation.py`
asserts it by making these packages unimportable and running the engine anyway.
"""

from __future__ import annotations

from governova_auth.store import (
    KeychainStore,
    KeychainUnavailableError,
    MemoryStore,
    Session,
)

__all__ = [
    "KeychainStore",
    "KeychainUnavailableError",
    "MemoryStore",
    "Session",
]
