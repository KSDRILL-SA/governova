"""The credit ledger, on disk.

`governova_ledger` holds every rule about what an entry is and what a balance
means. This module holds none of them. It reads rows, hands them to the domain
object, and writes back what that object produced — because **the storage layer
must not acquire a second opinion about what a balance is**, which is a sentence
already in that module and this is where it would first stop being true.

## Why the database decides idempotency and this code does not

`Ledger` keeps an index of idempotency keys, and that index is correct and
useless under the condition that matters. Two deliveries of the same payment
webhook arrive at two processes. Both load the ledger, both find no such key,
both build an entry, both write. Only the database sees both, and only because
`@@unique([organisation_id, idempotency_key])` exists.

So `record` here treats a unique violation as **an answer rather than an error**:
the key was used, the charge already happened, and the caller gets the entry that
already exists with `created=False`. That is the correct behaviour for a webhook
handler, whose alternative is to retry forever on a message that was handled.

The same reasoning covers `@@unique([organisation_id, seq])`. Two concurrent
writers can compute the same next sequence number from the same snapshot; the
loser retries against the ledger the winner just extended, which is the only way
a hash chain can be appended to concurrently without a lock.
"""

from __future__ import annotations

import datetime as dt
from typing import Any, Protocol

from governova_ledger import EntryKind, Ledger, LedgerEntry, Written, replay

_SELECT_ENTRIES = """
SELECT seq, organisation_id, kind, amount_minor, idempotency_key,
       occurred_at, detail, prev_hash, record_hash
  FROM "LedgerEntry"
 WHERE organisation_id = $1
 ORDER BY seq
"""

_INSERT_ENTRY = """
INSERT INTO "LedgerEntry"
       (id, organisation_id, seq, kind, amount_minor, idempotency_key,
        occurred_at, detail, prev_hash, record_hash)
VALUES (gen_random_uuid()::text, $1, $2, $3::"LedgerEntryKind", $4, $5, $6::timestamptz, $7, $8, $9)
"""

# How many times a writer will retry after losing a race for a sequence number.
# Bounded because an unbounded retry against a contended chain is a livelock, and
# a caller that is told "busy" can back off; a caller that never returns cannot.
_MAX_APPEND_ATTEMPTS = 5


class _Connection(Protocol):
    """The slice of `asyncpg.Connection` used here. See `migrations._Connection`."""

    async def execute(self, query: str, *args: Any) -> Any: ...
    async def fetch(self, query: str, *args: Any) -> Any: ...


class LedgerStore:
    """An organisation's ledger, backed by PostgreSQL."""

    def __init__(self, conn: _Connection) -> None:
        self._conn = conn

    async def load(self, organisation_id: str) -> Ledger:
        """Rebuild the ledger from stored rows.

        Through `replay`, which is the constructor that validates the chain and
        rejects a stored duplicate key. Reading rows into a `Ledger` any other
        way would skip that, and the one thing worth knowing about a ledger read
        back from disk is whether it is still the ledger that was written.
        """
        rows = await self._conn.fetch(_SELECT_ENTRIES, organisation_id)
        return replay([_entry_from_row(row) for row in rows], organisation_id)

    async def record(
        self,
        organisation_id: str,
        kind: EntryKind,
        amount: Any,
        *,
        idempotency_key: str,
        occurred_at: dt.datetime | None = None,
        detail: str = "",
    ) -> Written:
        """Append one movement, or return the one this key already wrote.

        Read-compute-write against a database that will refuse a duplicate. The
        loop exists for the sequence-number race and nothing else; the
        idempotency race is settled on the first attempt because losing it means
        the work is already done.
        """
        for _ in range(_MAX_APPEND_ATTEMPTS):
            ledger = await self.load(organisation_id)
            written = ledger.record(
                kind,
                amount,
                idempotency_key=idempotency_key,
                occurred_at=occurred_at,
                detail=detail,
            )
            if written.replayed:
                # This process had already written it. No insert to attempt.
                return written

            try:
                await self._insert(written.entry)
            except Exception as exc:
                violation = _violation(exc)
                if violation == "idempotency_key":
                    # Another writer won. The charge exists; say so rather than
                    # raising, because the caller is a retried webhook whose
                    # correct behaviour is to acknowledge.
                    existing = await self.load(organisation_id)
                    return Written(existing.find(idempotency_key), created=False)
                if violation == "seq":
                    # Another writer extended the chain first. Rebuild against
                    # what they wrote and try again.
                    continue
                raise
            return written

        raise RuntimeError(
            f"could not append to organisation {organisation_id!r}'s ledger after "
            f"{_MAX_APPEND_ATTEMPTS} attempts — every attempt lost the race for a "
            f"sequence number. This is contention, not corruption; the caller should "
            f"back off and retry rather than treat it as a failed charge."
        )

    async def _insert(self, entry: LedgerEntry) -> None:
        await self._conn.execute(
            _INSERT_ENTRY,
            entry.organisation_id,
            entry.seq,
            str(entry.kind).upper(),
            entry.amount_minor,
            entry.idempotency_key,
            entry.occurred_at,
            entry.detail,
            entry.prev_hash,
            entry.record_hash,
        )


def _entry_from_row(row: Any) -> LedgerEntry:
    """One stored row as a domain entry.

    `occurred_at` comes back from `timestamptz` as a `datetime`, and
    `LedgerEntry.__post_init__` canonicalises it to the same string that was
    hashed. That is the whole reason `canonical_timestamp` exists — before it,
    a row written in local time hashed one string and read back another, and
    `verify()` reported a broken chain on data nobody had touched.
    """
    return LedgerEntry(
        seq=row["seq"],
        organisation_id=row["organisation_id"],
        kind=EntryKind(str(row["kind"]).lower()),
        amount_minor=int(row["amount_minor"]),
        idempotency_key=row["idempotency_key"],
        occurred_at=row["occurred_at"],
        detail=row["detail"],
        prev_hash=row["prev_hash"],
        record_hash=row["record_hash"],
    )


def _violation(exc: BaseException) -> str | None:
    """Which unique constraint an exception reports, if it reports one.

    Matched on the constraint name rather than the exception class, so this works
    with `asyncpg.UniqueViolationError` without importing `asyncpg` — which keeps
    this module importable wherever the domain is, and keeps the test suite able
    to exercise the branches without a database.

    The names come from the migration, and a test asserts they still appear in
    it. A handler that silently stops recognising a violation would turn a
    duplicate charge from a returned entry into a raised exception, and the
    webhook would retry forever.
    """
    text = str(getattr(exc, "constraint_name", "") or exc)
    if "idempotency_key" in text:
        return "idempotency_key"
    if "seq" in text:
        return "seq"
    return None
