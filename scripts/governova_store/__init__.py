"""governova_store — Stage 1 persistence. Where the Cloud's rows actually live.

`ADR-015`: **Prisma authors the schema and the migrations; `asyncpg` executes
queries.** `platform/cloud/prisma/schema.prisma` stays the single source of truth
for the data model (`S5.9`), migrations are generated from it and committed as
plain SQL, and nothing Node-shaped exists in any deployed path.

Installed as part of `governova[cloud]`, for the reason `ADR-010` §5.1 gives: the
deterministic engine runs complete and offline forever, so a consumer who
installs `governova` to govern a repository must never acquire a database driver
to do it. `test_identity_isolation.py` asserts that direction rather than
trusting it.

## What this package is careful about

**It holds no opinions.** The invariants live in the database — every unique
constraint, every foreign key, every `NOT NULL` — and the domain rules live in
`governova_ledger` and `governova_org`. This package moves rows. The moment it
starts deciding what a balance is, there are two answers to that question and
no way to tell which is wrong.

**Every query is parameterised.** `asyncpg` binds `$1`-style parameters through
the wire protocol and cannot interpolate a value into SQL, so `S5.21` and
`AP-S2.28f` are properties of the driver here rather than of review.

**A constraint violation is an answer, not an error.** A duplicate idempotency
key means a webhook was retried, which is the expected case and not a failure.
`ledger.record` reads the violation and returns the entry that already exists.
"""

from __future__ import annotations

from governova_store.ledger import LedgerStore
from governova_store.migrations import (
    MIGRATIONS_TABLE,
    Migration,
    MigrationError,
    apply_all,
    discover,
    migrations_dir,
)

__all__ = [
    "MIGRATIONS_TABLE",
    "LedgerStore",
    "Migration",
    "MigrationError",
    "apply_all",
    "discover",
    "migrations_dir",
]
