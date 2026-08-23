"""Applying the committed migration SQL, and refusing to apply it twice.

`ADR-015` makes the SQL the artifact: `prisma migrate diff` writes it at
authoring time, a human reviews it in a pull request, and this module runs it.
Applying a migration therefore needs PostgreSQL and nothing else — no Node, no
code generation, no network.

Three properties, each because the alternative is a bad afternoon:

**Ordered by name, and the names are timestamps.** `20260823000000_stage_1_initial`
sorts before anything written after it, for the same reason every migration tool
does this. A directory listing is not an order.

**Recorded, so a second run is a no-op.** The applied set lives in a table rather
than in a file, because the question "has this database had that migration?" is
about the database and any other place to keep the answer can be out of step with
it.

**Checksummed, so an edited migration is refused.** A migration that has already
run and whose text has since changed is not a migration — it is two different
statements with one name, and the database has had one of them. Silently
accepting it means the schema in front of you is not the schema described by the
files. This is the same reasoning as the ledger's hash chain, applied to DDL.
"""

from __future__ import annotations

import dataclasses
import hashlib
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Protocol

MIGRATIONS_TABLE = "_governova_migration"
"""Where the applied set is recorded.

Leading underscore because it is infrastructure rather than data, and it is
deliberately *not* in `schema.prisma`: Prisma does not own this table, and a
model for it there would be a fact about the migration runner leaking into the
data model it applies.
"""

# Written out rather than interpolated from `MIGRATIONS_TABLE`, and the reason is
# not style. An f-string that builds SQL is `AP-S2.28f`, which this repository
# ships as a finding into other people's CI — and the engine reported it here, on
# this file, the first time the suite ran. The name being a constant makes it
# safe and does not make it *look* safe, and a rule that has to distinguish those
# two cases from one line cannot. Keeping the SQL literal costs one duplicated
# identifier and removes the shape entirely.
_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS _governova_migration (
    name        TEXT        PRIMARY KEY,
    checksum    TEXT        NOT NULL,
    applied_at  TIMESTAMPTZ NOT NULL DEFAULT now()
)
"""

_SELECT_APPLIED = "SELECT name, checksum FROM _governova_migration"

_RECORD_APPLIED = "INSERT INTO _governova_migration (name, checksum) VALUES ($1, $2)"


class MigrationError(RuntimeError):
    """A migration this module refused to apply, and why."""


class _Connection(Protocol):
    """The slice of `asyncpg.Connection` this module uses.

    A protocol rather than the real type so the module imports without
    `asyncpg` present, and so a test can supply a recorder without a database.
    Naming exactly what is used is also the honest statement of how much of the
    driver this depends on: three methods.
    """

    async def execute(self, query: str, *args: Any) -> Any: ...
    async def fetch(self, query: str, *args: Any) -> Any: ...
    def transaction(self) -> Any: ...


@dataclasses.dataclass(frozen=True)
class Migration:
    """One committed SQL file, and the checksum of what it said when applied."""

    name: str
    sql: str

    @property
    def checksum(self) -> str:
        """SHA-256 of the SQL, with line endings normalised.

        Normalised because this repository is developed on Windows and run on
        Linux, and a checksum that changes with `git`'s line-ending translation
        would refuse every migration on the other platform — a guard that fires
        on the wrong thing gets disabled, and then it guards nothing.
        """
        return hashlib.sha256(self.sql.replace("\r\n", "\n").encode("utf-8")).hexdigest()


def migrations_dir(root: Path) -> Path:
    """Where the committed migrations live, relative to a repository root."""
    return root / "platform" / "cloud" / "prisma" / "migrations"


def discover(directory: Path) -> list[Migration]:
    """Every migration in `directory`, in the order it must be applied.

    A migration is a directory containing `migration.sql`, which is the layout
    `prisma migrate` produces. `migration_lock.toml` sits beside them and is not
    one.
    """
    if not directory.is_dir():
        raise MigrationError(
            f"no migrations directory at {directory}. Stage 1's schema is committed "
            f"SQL (ADR-015); if this path is wrong, nothing will be applied and the "
            f"database will look empty rather than unmigrated."
        )
    found: list[Migration] = []
    for child in sorted(directory.iterdir()):
        if not child.is_dir():
            continue
        sql_path = child / "migration.sql"
        if not sql_path.is_file():
            raise MigrationError(
                f"{child.name} is in the migrations directory and has no "
                f"migration.sql. An empty migration directory is indistinguishable "
                f"from one whose file was lost, so it is refused rather than skipped."
            )
        found.append(Migration(name=child.name, sql=sql_path.read_text(encoding="utf-8")))
    return found


async def _applied(conn: _Connection) -> dict[str, str]:
    """The migrations this database has already had, name → checksum."""
    rows = await conn.fetch(_SELECT_APPLIED)
    return {row["name"]: row["checksum"] for row in rows}


async def apply_all(conn: _Connection, migrations: Sequence[Migration]) -> list[str]:
    """Apply everything not yet applied, in order. Returns what it applied.

    Each migration runs **inside a transaction with the row that records it**, so
    a database cannot end up having run the SQL without knowing that it did. The
    failure that ordering prevents is the expensive one: a half-applied schema
    that the runner believes is unapplied, which it then tries to apply again.
    """
    await conn.execute(_CREATE_TABLE)
    already = await _applied(conn)

    applied: list[str] = []
    for migration in migrations:
        recorded = already.get(migration.name)
        if recorded is not None:
            if recorded != migration.checksum:
                raise MigrationError(
                    f"{migration.name} has already been applied to this database, and "
                    f"the file has changed since. The database has the old statement "
                    f"and the repository has the new one, so the schema in front of "
                    f"you is not the schema these files describe. Write a new "
                    f"migration; never edit one that has run."
                )
            continue

        async with conn.transaction():
            await conn.execute(migration.sql)
            await conn.execute(_RECORD_APPLIED, migration.name, migration.checksum)
        applied.append(migration.name)

    return applied
