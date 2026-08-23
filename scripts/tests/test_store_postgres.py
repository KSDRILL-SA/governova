"""Stage 1 against a real PostgreSQL. The half `test_store.py` cannot prove.

`test_store.py` runs everywhere and exercises this repository's own reasoning —
migration ordering, checksum refusal, the two concurrency branches — against a
fake connection. What it cannot do is establish that the committed SQL is valid
PostgreSQL, that the constraints exist once it has run, or that a row survives
the round trip through `timestamptz`.

Those need a server. They run in CI beside a `postgres` service, and **skip
elsewhere with the reason stated** rather than passing: a check that cannot
determine an answer returns `unknown`, never `satisfied`, which is the first
standing rule in this repository and applies to its own tests before anything
else.

To run locally:

    docker run --rm -e POSTGRES_PASSWORD=x -p 5432:5432 postgres:16
    GOVERNOVA_TEST_DATABASE_URL=postgresql://postgres:x@localhost:5432/postgres \\
      uv run pytest scripts/tests/test_store_postgres.py
"""

from __future__ import annotations

import asyncio
import datetime as dt
import os
import uuid
from pathlib import Path
from typing import Any

import pytest
from governova_compile.discovery import resolve_repo_root
from governova_ledger import EntryKind
from governova_store import LedgerStore, apply_all, discover, migrations_dir

DATABASE_URL = os.environ.get("GOVERNOVA_TEST_DATABASE_URL", "")

asyncpg = pytest.importorskip(
    "asyncpg",
    reason="asyncpg is in the `cloud` extra; the engine does not carry a database driver",
)

pytestmark = pytest.mark.skipif(
    not DATABASE_URL,
    reason=(
        "GOVERNOVA_TEST_DATABASE_URL is unset, so there is no server to ask. These "
        "assertions are unknown rather than satisfied — they run in CI beside a "
        "postgres service."
    ),
)


def _run(coro: Any) -> Any:
    return asyncio.run(coro)


async def _fresh_schema() -> Any:
    """A connection to a schema of its own, migrated from the committed SQL.

    Each test gets its own PostgreSQL schema rather than its own database:
    creating a database needs a separate connection to `postgres` and a
    `CREATE DATABASE` outside a transaction, and a schema gives the same
    isolation for what is being tested here.
    """
    conn = await asyncpg.connect(DATABASE_URL)
    name = f"t_{uuid.uuid4().hex[:12]}"
    await conn.execute(f'CREATE SCHEMA "{name}"')
    await conn.execute(f'SET search_path TO "{name}"')
    return conn


def test_the_committed_migration_is_valid_postgresql() -> None:
    """The assertion `test_store.py` explicitly refuses to make.

    A syntax error, a column type PostgreSQL does not have, or a constraint that
    references a missing column all fail here and nowhere else.
    """

    async def go() -> list[str]:
        conn = await _fresh_schema()
        try:
            return await apply_all(conn, discover(migrations_dir(Path(resolve_repo_root()))))
        finally:
            await conn.close()

    assert _run(go()) == ["20260823000000_stage_1_initial"]


def test_applying_twice_is_a_no_op() -> None:
    """Against a real server this time, so the recorded set is a real table."""

    async def go() -> list[str]:
        conn = await _fresh_schema()
        try:
            migrations = discover(migrations_dir(Path(resolve_repo_root())))
            await apply_all(conn, migrations)
            return await apply_all(conn, migrations)
        finally:
            await conn.close()

    assert _run(go()) == []


def test_a_ledger_entry_survives_a_real_round_trip() -> None:
    """Written through the store, read back through `timestamptz`, chain intact.

    The defect this guards was found before Stage 1 stored anything: a row
    written in local time hashed one string and read back another, and `verify()`
    reported a broken chain on data nobody had touched. Proving it against a real
    column is the only version of that claim worth having.
    """

    async def go() -> Any:
        conn = await _fresh_schema()
        try:
            await apply_all(conn, discover(migrations_dir(Path(resolve_repo_root()))))
            org = str(uuid.uuid4())
            await conn.execute(
                'INSERT INTO "Organisation" (id, slug, name, updated_at) '
                "VALUES ($1, $2, $3, now())",
                org,
                f"org-{org[:8]}",
                "Test Organisation",
            )
            store = LedgerStore(conn)
            sast = dt.timezone(dt.timedelta(hours=2))
            written = await store.record(
                org,
                EntryKind.GRANT,
                "100.5",
                idempotency_key="evt_1",
                occurred_at=dt.datetime(2026, 8, 23, 12, 0, tzinfo=sast),
            )
            reloaded = await store.load(org)
            return written, reloaded
        finally:
            await conn.close()

    written, reloaded = _run(go())
    assert written.created
    assert reloaded.verify().valid, "the chain broke on a round trip through timestamptz"
    assert reloaded.entries[0].record_hash == written.entry.record_hash
    assert str(reloaded.balance()) == "100.5"


def test_the_database_refuses_a_second_charge_for_one_key() -> None:
    """The constraint the ledger's correctness actually rests on, exercised as a
    real violation rather than a simulated one.

    `test_store.py` raises a shaped exception to reach the handler. This proves
    the constraint exists in the schema that shipped — the half a fake cannot.
    """

    async def go() -> Any:
        conn = await _fresh_schema()
        try:
            await apply_all(conn, discover(migrations_dir(Path(resolve_repo_root()))))
            org = str(uuid.uuid4())
            await conn.execute(
                'INSERT INTO "Organisation" (id, slug, name, updated_at) '
                "VALUES ($1, $2, $3, now())",
                org,
                f"org-{org[:8]}",
                "Test Organisation",
            )
            store = LedgerStore(conn)
            first = await store.record(org, EntryKind.CONSUMPTION, 5, idempotency_key="evt_1")
            again = await store.record(org, EntryKind.CONSUMPTION, 5, idempotency_key="evt_1")
            ledger = await store.load(org)
            return first, again, ledger
        finally:
            await conn.close()

    first, again, ledger = _run(go())
    assert first.created
    assert again.replayed
    assert again.entry.record_hash == first.entry.record_hash
    assert len(ledger.entries) == 1, "a retried webhook charged twice"


def test_a_ledger_entry_cannot_belong_to_an_organisation_that_does_not_exist() -> None:
    """The foreign key, which application code cannot enforce for a bulk import,
    a support script or a direct INSERT — all normal things to do to a production
    database."""

    async def go() -> str:
        conn = await _fresh_schema()
        try:
            await apply_all(conn, discover(migrations_dir(Path(resolve_repo_root()))))
            store = LedgerStore(conn)
            try:
                await store.record(
                    str(uuid.uuid4()), EntryKind.GRANT, 1, idempotency_key="evt_1"
                )
            except Exception as exc:  # asyncpg.ForeignKeyViolationError
                return type(exc).__name__
            return "no error"
        finally:
            await conn.close()

    assert _run(go()) == "ForeignKeyViolationError"
