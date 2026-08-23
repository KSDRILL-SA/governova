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

# The tail, and nothing else. `record` needs `seq` and `record_hash` to build the
# next link, and reading the whole chain to learn them made every write cost the
# entire history — quadratic over a ledger's life, on the metering path, which is
# the query that runs most often in the system. Served by the existing
# `@@unique([organisation_id, seq])`, so the index is already there.
_SELECT_TAIL = """
SELECT seq, record_hash
  FROM "LedgerEntry"
 WHERE organisation_id = $1
 ORDER BY seq DESC
 LIMIT 1
"""

# Has this key been used. An indexed lookup on
# `@@unique([organisation_id, idempotency_key])` — the same constraint that
# refuses the duplicate insert, asked in advance so the common case does not have
# to go through an exception.
_SELECT_BY_KEY = """
SELECT seq, organisation_id, kind, amount_minor, idempotency_key,
       occurred_at, detail, prev_hash, record_hash
  FROM "LedgerEntry"
 WHERE organisation_id = $1 AND idempotency_key = $2
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

# A stand-in instant for the synthetic tail entry, which exists only to carry a
# sequence number and a hash. Canonical so it survives `__post_init__`.
_EPOCH = "1970-01-01T00:00:00.000000+00:00"


class _Connection(Protocol):
    """The slice of `asyncpg.Connection` used here. See `migrations._Connection`."""

    async def execute(self, query: str, *args: Any) -> Any: ...
    async def fetch(self, query: str, *args: Any) -> Any: ...


class LedgerStore:
    """An organisation's ledger, backed by PostgreSQL."""

    def __init__(self, conn: _Connection) -> None:
        self._conn = conn

    async def load(self, organisation_id: str) -> Ledger:
        """Rebuild the **whole** ledger from stored rows.

        This reads every entry, deliberately and unavoidably: it exists so
        `verify()` can walk the chain, and a chain cannot be verified from part
        of itself. It is an audit operation, not a write path.

        **`record` must not call this**, and did — which made every write read the
        entire history and cost a ledger `n(n+1)/2` row reads over its life.

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

        Implements REQ-009 — the reads here are bounded and do not grow with the
        number of entries already recorded.

        Read-compute-write against a database that will refuse a duplicate. The
        loop exists for the sequence-number race and nothing else; the
        idempotency race is settled on the first attempt because losing it means
        the work is already done.
        """
        for _ in range(_MAX_APPEND_ATTEMPTS):
            # Two facts, not the history. The domain still decides everything —
            # the hash, the direction, the amount — it just is not handed rows it
            # does not read.
            existing = await self._by_key(organisation_id, idempotency_key)
            if existing is not None:
                return Written(existing, created=False)

            tail = await self._tail(organisation_id)
            # A one-entry ledger reproduces the tail's link exactly, which is all
            # `next_link` reads. Passing the tail rather than the chain keeps the
            # sequence and hash decisions inside the domain object where they
            # belong, without paying for rows nobody looks at.
            ledger = Ledger(organisation_id, [tail] if tail is not None else [])
            written = ledger.record(
                kind,
                amount,
                idempotency_key=idempotency_key,
                occurred_at=occurred_at,
                detail=detail,
            )

            try:
                await self._insert(written.entry)
            except Exception as exc:
                violation = _violation(exc)
                if violation == "idempotency_key":
                    # Another writer won between our lookup and our insert. The
                    # charge exists; say so rather than raising, because the
                    # caller is a retried webhook whose correct behaviour is to
                    # acknowledge. One indexed read, not the chain.
                    winner = await self._by_key(organisation_id, idempotency_key)
                    if winner is None:
                        raise
                    return Written(winner, created=False)
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

    async def _tail(self, organisation_id: str) -> LedgerEntry | None:
        """The last entry, or None for an empty ledger.

        Only `seq` and `record_hash` are read from the row; the rest of the
        returned entry is filler that `next_link` never looks at. It is built as
        a real `LedgerEntry` rather than a tuple so the domain keeps deciding what
        a link is.
        """
        rows = await self._conn.fetch(_SELECT_TAIL, organisation_id)
        if not rows:
            return None
        row = rows[0]
        return LedgerEntry(
            seq=row["seq"],
            organisation_id=organisation_id,
            kind=EntryKind.GRANT,
            amount_minor=0,
            idempotency_key=f"__tail_{row['seq']}",
            occurred_at=_EPOCH,
            record_hash=row["record_hash"],
        )

    async def _by_key(self, organisation_id: str, key: str) -> LedgerEntry | None:
        """The entry written under `key`, or None. One indexed lookup."""
        rows = await self._conn.fetch(_SELECT_BY_KEY, organisation_id, key)
        return _entry_from_row(rows[0]) if rows else None

    async def _insert(self, entry: LedgerEntry) -> None:
        await self._conn.execute(
            _INSERT_ENTRY,
            entry.organisation_id,
            entry.seq,
            str(entry.kind).upper(),
            entry.amount_minor,
            entry.idempotency_key,
            # A `datetime`, not the canonical string. `asyncpg` binds parameters
            # by Python type through the wire protocol and rejects a `str` for a
            # `timestamptz` before the `::timestamptz` cast in the statement is
            # ever reached — the cast applies to the value the server receives,
            # and the driver never gets that far.
            #
            # Parsing back is safe precisely because the string is canonical:
            # UTC, microsecond precision, `+00:00`. The instant survives, the
            # server returns it unchanged, and `__post_init__` produces the same
            # string again on the way back — which is what keeps the hash intact.
            #
            # Found by the first run against a real PostgreSQL. The fake
            # connection had accepted a string, so every unit test passed while
            # the statement could never have executed. `FakeConnection` now
            # refuses one too.
            dt.datetime.fromisoformat(entry.occurred_at),
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
