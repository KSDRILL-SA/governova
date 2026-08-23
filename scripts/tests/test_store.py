"""Stage 1 persistence — the migration runner and the ledger store.

These run **without a database**. A fake connection records what was executed and
replays rows back, which is enough to exercise the parts that are this
repository's own reasoning: migration ordering, checksum refusal, and the two
concurrency branches where a unique violation is an answer rather than an error.

What it deliberately does *not* prove is that the SQL is valid PostgreSQL. That
needs a real server, it belongs in CI beside a `postgres` service, and pretending
otherwise here would be the failure this repository names most often — a test
that cannot fail for its stated reason. `test_the_insert_names_columns_the_migration_creates`
is the compromise: it checks the statements against the committed schema, which
catches a renamed column without claiming to catch a syntax error.
"""

from __future__ import annotations

import asyncio
import datetime as dt
from pathlib import Path
from typing import Any

import pytest
from governova_compile.discovery import resolve_repo_root
from governova_ledger import EntryKind, LedgerError
from governova_store import (
    LedgerStore,
    Migration,
    MigrationError,
    apply_all,
    discover,
    migrations_dir,
)

# ── a connection that records, and can be told to refuse ─────────────────────


class _Transaction:
    async def __aenter__(self) -> None:
        return None

    async def __aexit__(self, *exc: object) -> bool:
        return False


class FakeConnection:
    """Enough of `asyncpg.Connection` to drive the code under test.

    `rows` is what `fetch` returns; `refuse` names a constraint the next insert
    should violate, which is how the concurrency branches are reached without two
    real processes racing.
    """

    def __init__(self, rows: list[dict[str, Any]] | None = None) -> None:
        self.rows: list[dict[str, Any]] = rows or []
        self.executed: list[tuple[str, tuple[Any, ...]]] = []
        self.refuse: str | None = None
        self.rows_after_refusal: list[dict[str, Any]] | None = None
        """What the other writer had committed, revealed only once we lose.

        Set alongside `refuse` to model the race honestly: our first read does
        not see their row — that is *why* both processes build an entry — and it
        appears only after the database has refused our insert. Handing the row
        over before the read would make `Ledger` find the key itself and return
        early, and the violation branch under test would never run.
        """

    async def execute(self, query: str, *args: Any) -> None:
        if "INSERT INTO \"LedgerEntry\"" in query:
            # As strict as the driver where it matters. `asyncpg` binds by Python
            # type and rejects a `str` for a `timestamptz` before the statement's
            # cast is reached — and this fake accepted one, so the whole unit
            # suite passed against a statement that could never have executed.
            # A fake looser than the thing it stands in for is a test that cannot
            # fail for its stated reason.
            occurred_at = args[5]
            if not isinstance(occurred_at, dt.datetime):
                raise TypeError(
                    f"asyncpg binds $6 as timestamptz and requires a datetime; "
                    f"got {type(occurred_at).__name__}"
                )
        if self.refuse and "INSERT INTO \"LedgerEntry\"" in query:
            constraint, self.refuse = self.refuse, None
            if self.rows_after_refusal is not None:
                self.rows = self.rows_after_refusal
            raise _UniqueViolationError(constraint)
        self.executed.append((query, args))

    async def fetch(self, query: str, *args: Any) -> list[dict[str, Any]]:
        if "_governova_migration" in query:
            return [r for r in self.rows if "checksum" in r]
        return [r for r in self.rows if "record_hash" in r]

    def transaction(self) -> _Transaction:
        return _Transaction()


class _UniqueViolationError(Exception):
    """Shaped like `asyncpg.UniqueViolationError`: it carries a constraint name."""

    def __init__(self, constraint_name: str) -> None:
        super().__init__("duplicate key value violates unique constraint")
        self.constraint_name = constraint_name


def _run(coro: Any) -> Any:
    return asyncio.run(coro)


# ── the committed migrations ─────────────────────────────────────────────────


def _committed() -> list[Migration]:
    return discover(migrations_dir(Path(resolve_repo_root())))


def test_the_repository_ships_a_migration() -> None:
    """`ADR-015` makes the SQL the artifact rather than something regenerated on
    demand. If this is empty, a fresh database comes up with no tables and looks
    merely empty rather than unmigrated."""
    assert [m.name for m in _committed()] == ["20260823000000_stage_1_initial"]


def test_the_migration_carries_the_two_constraints_the_ledger_rests_on() -> None:
    """Neither is enforceable in application code, and the ledger's correctness
    is exactly these two lines. `governova_store.ledger` matches on their names."""
    sql = _committed()[0].sql
    assert "LedgerEntry_organisation_id_idempotency_key_key" in sql
    assert "LedgerEntry_organisation_id_seq_key" in sql


def test_the_migration_makes_a_cross_tenant_team_membership_impossible() -> None:
    """The composite foreign keys, which are the reason `organisation_id` is
    denormalised onto `TeamMembership` at all (`S14.8`)."""
    sql = _committed()[0].sql
    assert 'FOREIGN KEY ("organisation_id", "team_id")' in sql
    assert 'FOREIGN KEY ("organisation_id", "membership_id")' in sql


# ── the runner ───────────────────────────────────────────────────────────────


def test_migrations_apply_in_order_and_record_themselves() -> None:
    conn = FakeConnection()
    applied = _run(apply_all(conn, [Migration("001_a", "SELECT 1"), Migration("002_b", "SELECT 2")]))
    assert applied == ["001_a", "002_b"]
    inserts = [q for q, _ in conn.executed if "INSERT INTO _governova_migration" in q]
    assert len(inserts) == 2


def test_a_second_run_applies_nothing() -> None:
    """The applied set lives in the database, because the question is about the
    database and any other place to keep the answer can be out of step with it."""
    migration = Migration("001_a", "SELECT 1")
    conn = FakeConnection(rows=[{"name": "001_a", "checksum": migration.checksum}])
    assert _run(apply_all(conn, [migration])) == []


def test_an_edited_migration_is_refused() -> None:
    """A migration that has run and whose text has since changed is two different
    statements with one name, and the database has had one of them."""
    conn = FakeConnection(rows=[{"name": "001_a", "checksum": "a-different-checksum"}])
    with pytest.raises(MigrationError, match="has already been applied"):
        _run(apply_all(conn, [Migration("001_a", "SELECT 1")]))


def test_the_checksum_ignores_line_endings() -> None:
    """This repository is developed on Windows and runs on Linux. A checksum that
    changed with git's line-ending translation would refuse every migration on
    the other platform — and a guard that fires on the wrong thing gets disabled,
    after which it guards nothing."""
    assert Migration("a", "CREATE TABLE t();\n").checksum == (
        Migration("a", "CREATE TABLE t();\r\n").checksum
    )


def test_a_migration_directory_with_no_sql_is_refused(tmp_path: Path) -> None:
    (tmp_path / "001_empty").mkdir()
    with pytest.raises(MigrationError, match=r"no migration\.sql"):
        discover(tmp_path)


def test_a_missing_migrations_directory_is_refused(tmp_path: Path) -> None:
    with pytest.raises(MigrationError, match="no migrations directory"):
        discover(tmp_path / "nowhere")


# ── the ledger store ─────────────────────────────────────────────────────────


def _stored_row(entry: Any) -> dict[str, Any]:
    """One entry as `asyncpg` would hand it back, timestamp included.

    `occurred_at` returns as a `datetime` from `timestamptz`, which is the round
    trip that used to break the hash.
    """
    return {
        "seq": entry.seq,
        "organisation_id": entry.organisation_id,
        "kind": str(entry.kind).upper(),
        "amount_minor": entry.amount_minor,
        "idempotency_key": entry.idempotency_key,
        "occurred_at": dt.datetime.fromisoformat(entry.occurred_at),
        "detail": entry.detail,
        "prev_hash": entry.prev_hash,
        "record_hash": entry.record_hash,
    }


def test_an_entry_survives_the_round_trip_the_database_performs() -> None:
    """Written, read back as `asyncpg` returns it, and the chain still verifies.

    This is the store-level statement of the defect fixed alongside it: a row
    written in local time hashed one string and read back another, and `verify()`
    reported a broken chain on data nobody had touched.
    """
    sast = dt.timezone(dt.timedelta(hours=2))
    conn = FakeConnection()
    store = LedgerStore(conn)
    written = _run(
        store.record(
            "org-1",
            EntryKind.GRANT,
            100,
            idempotency_key="evt_1",
            occurred_at=dt.datetime(2026, 8, 23, 12, 0, tzinfo=sast),
        )
    )
    assert written.created

    conn.rows = [_stored_row(written.entry)]
    reloaded = _run(store.load("org-1"))
    assert reloaded.verify().valid
    assert reloaded.entries[0].record_hash == written.entry.record_hash


def test_a_duplicate_idempotency_key_returns_the_existing_charge() -> None:
    """The webhook case. Another process won the race; the charge exists, and the
    caller's correct behaviour is to acknowledge rather than retry forever."""
    sast = dt.UTC
    conn = FakeConnection()
    store = LedgerStore(conn)
    first = _run(
        store.record("org-1", EntryKind.CONSUMPTION, 5, idempotency_key="evt_1",
                     occurred_at=dt.datetime(2026, 8, 23, 12, 0, tzinfo=sast))
    )

    # A second process wrote it between our read and our insert. Our read must
    # still see nothing — that is why we build an entry at all — so the row is
    # revealed only when the database refuses us.
    fresh = FakeConnection()
    fresh.refuse = "LedgerEntry_organisation_id_idempotency_key_key"
    fresh.rows_after_refusal = [_stored_row(first.entry)]
    store = LedgerStore(fresh)

    again = _run(store.record("org-1", EntryKind.CONSUMPTION, 5, idempotency_key="evt_1"))
    assert again.replayed
    assert again.entry.record_hash == first.entry.record_hash


def test_losing_the_race_for_a_sequence_number_retries() -> None:
    """Two writers computed the same next position from the same snapshot. The
    loser rebuilds against what the winner wrote — the only way a hash chain is
    appended to concurrently without a lock."""
    conn = FakeConnection()
    store = LedgerStore(conn)
    winner = _run(
        store.record("org-1", EntryKind.GRANT, 100, idempotency_key="evt_1",
                     occurred_at=dt.datetime(2026, 8, 23, 12, 0, tzinfo=dt.UTC))
    )

    # Our read sees an empty chain, so we compute seq 1 — and lose. The winner's
    # entry appears only after the refusal, and the retry rebuilds against it.
    fresh = FakeConnection()
    fresh.refuse = "LedgerEntry_organisation_id_seq_key"
    fresh.rows_after_refusal = [_stored_row(winner.entry)]
    store = LedgerStore(fresh)

    second = _run(store.record("org-1", EntryKind.GRANT, 50, idempotency_key="evt_2"))
    assert second.created
    assert second.entry.seq == 2
    assert second.entry.prev_hash == winner.entry.record_hash


def test_an_unrecognised_error_is_not_swallowed() -> None:
    """Only the two named constraints mean something here. Anything else is a
    real failure, and turning it into a returned entry would report a charge that
    never happened."""
    conn = FakeConnection()
    conn.refuse = "some_other_constraint"
    with pytest.raises(_UniqueViolationError):
        _run(LedgerStore(conn).record("org-1", EntryKind.GRANT, 1, idempotency_key="evt_1"))


def test_find_raises_rather_than_returning_none() -> None:
    """Every caller reaching `find` has just been told by the database that the
    key exists. A `None` flowing from here would end up in a receipt."""
    from governova_ledger import Ledger

    with pytest.raises(LedgerError, match="no entry for idempotency key"):
        Ledger("org-1").find("never-written")


def test_the_insert_names_columns_the_migration_creates() -> None:
    """Not a syntax check — that needs a real server and belongs in CI. This
    catches the cheaper and likelier mistake: a column renamed in the schema and
    not here, which would fail at runtime against a correct database."""
    from governova_store.ledger import _INSERT_ENTRY, _SELECT_ENTRIES

    sql = _committed()[0].sql
    for column in (
        "organisation_id", "seq", "kind", "amount_minor",
        "idempotency_key", "occurred_at", "detail", "prev_hash", "record_hash",
    ):
        assert f'"{column}"' in sql, column
        assert column in _INSERT_ENTRY, column
        assert column in _SELECT_ENTRIES, column
