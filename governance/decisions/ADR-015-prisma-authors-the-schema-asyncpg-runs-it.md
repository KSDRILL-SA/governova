# ADR-015 — Prisma authors the schema, asyncpg runs it

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-23 |
| **Authority** | L4 — `C0 §8`. Implements `ADR-010`'s inherited "PostgreSQL via Prisma" |
| **Supersedes** | Nothing. Decides a question `ADR-010` left implicit |
| **Relates To** | `S5.9`, `S5.21`, `S5.30`, `S8.84`, `S8.85`, `ADR-010 §2`, `#255` |

---

## Context

`ADR-010 §2` inherits **"PostgreSQL via Prisma (`S5.9`)"** from the stack matrix, and
`platform/cloud/prisma/schema.prisma` declares `generator client { provider = "prisma-client-py" }`.
The implementation guide `constitution/implementation/fastapi/C02-backend-fastapi.md:1224` shows
`from prisma import Prisma`.

Read together, those read as a decision that has already been taken. **It has not.** `S5.9` makes
the Prisma schema the single source of truth for the *data model*; it says nothing about which
library issues queries at runtime, and the generator line was written before anybody checked the
package.

Checked now, before Stage 1 builds financial code on it:

| | |
|---|---|
| Latest release | `prisma` **0.15.0** |
| Uploaded | **2024-08-16** — two years ago |
| Import without codegen | `RuntimeError: The Client hasn't been generated yet` |
| Runtime requirement | a generated client, produced by a **Node** query engine |

The package resolves cleanly beside `pydantic 2.13.4`, so this is not a dependency conflict. It
is three other things.

**It puts a Node toolchain in the production path.** `prisma generate` downloads and runs engine
binaries, and the generated client must then be committed or regenerated at deploy time. The
Python engine has no Node dependency anywhere today.

**It is a two-year-stale dependency under two gates that exist to catch exactly that.** `S8.84`
puts the lockfile behind a CVE gate and `S8.85` behind a licence allowlist. A package with no
release in two years is one where a disclosed vulnerability has nobody to fix it, and the gate
would then be reporting a problem we chose.

**Stage 2 is financial code.** `planning/phase-4-cloud.md` says so, and `#255` calls the ledger
financial code in its title. The correctness of a credit ledger rests on two database
constraints — `@@unique([organisation_id, idempotency_key])` and `@@unique([organisation_id, seq])`
— not on an ORM's query builder. What the runtime library buys us there is close to nothing, and
what it costs is a build step and an unmaintained supply-chain edge.

One further observation, recorded because it cost time and will cost the next person the same:
**`prisma@7`'s `migrate diff --from-empty --to-schema` produced an empty file and exited 0.**
`prisma@5`'s `--to-schema-datamodel` produced the correct 6 KB of SQL. A schema tool that emits
nothing and reports success is the failure mode this repository names most often, and it argues
on its own for the SQL being a committed artifact rather than something regenerated on demand.

---

## Decision

**Prisma owns the schema and authors the migrations. `asyncpg` executes queries at runtime.
No Node binary exists in any deployed path.**

Concretely:

1. `schema.prisma` remains the single source of truth for the data model, unchanged. `S5.9` is
   satisfied by the schema, not by the client.
2. Migrations are **generated** by `prisma migrate diff` (Node, authoring time only) and
   **committed as plain SQL** under `platform/cloud/prisma/migrations/`. The SQL is the artifact;
   the tool that wrote it is not a runtime dependency.
3. Migrations are **applied** by a small Python runner over `asyncpg`, which records what it has
   applied. Applying a migration therefore needs Postgres and nothing else.
4. Repositories live in `governova_store`, in the `cloud` extra, never in the base wheel —
   `ADR-010 §1` guarantees the deterministic engine runs complete and offline, and a consumer
   governing a repository must never acquire a database driver.
5. Every query is parameterised. `asyncpg` binds `$1`-style parameters natively and cannot
   interpolate, which is `S5.21` and `S2.28f` enforced by the driver rather than by review.
6. `governova_ledger`'s domain logic does not move. It already reconstructs from stored entries
   through its constructor and derives a balance from entries alone; the store supplies the
   entries and appends new ones. **The storage layer must not acquire a second opinion about what
   a balance is** — that sentence is already in the module and this decision keeps it true.

---

## Consequences

### What becomes easier

- **Nothing Node-shaped is deployed.** The Cloud runs on Python and Postgres, the same two things
  the engine already needs.
- **The CVE and licence gates keep working.** `asyncpg` is actively maintained and Apache-2.0.
- **Migrations are reviewable.** A pull request shows the SQL that will run, not a schema diff a
  reader must trust a generator to have translated correctly.
- **Tests need no codegen step.** A test can create the schema from committed SQL against a
  throwaway database.

### What becomes harder

- **Queries are written, not generated.** Six tables' worth of repository code exists that a
  generated client would have provided. This is the real cost and it is accepted: the surface is
  small, explicit, and confined to `governova_store`.
- **Schema and repositories can drift.** The generator would have made that impossible. A test
  asserts that the committed migration SQL still matches `schema.prisma` — `prisma migrate diff`
  against the applied migrations must come back empty, which is the same check the generator was
  providing, moved into CI.
- **The implementation guide is now wrong.** `C02-backend-fastapi.md:1224` shows
  `from prisma import Prisma`. It is a guide rather than a standard, but it must be corrected or
  it will teach the next reader the thing this ADR decided against.

### Constitutional alignment

- `S5.9` — satisfied by `schema.prisma` remaining the source of truth. The ADR narrows what
  "via Prisma" governs: the model, not the driver.
- `S5.21`, `S2.28f` — parameterisation is a property of `asyncpg`'s protocol, not of discipline.
- `S5.30` — uniqueness stays in the database. This decision does not move a single constraint
  into application code; it is the reason the runtime library matters so little.
- `S8.84`, `S8.85` — the driver is maintained and its licence is on the allowlist.
- `ADR-010 §1` — `governova_store` ships in the `cloud` extra, so the free engine gains nothing.

---

## Alternatives Considered

| Option | Why rejected |
|---|---|
| **`prisma-client-py` as decided-by-implication** | Two years without a release, requires a Node codegen step, and puts engine binaries in the deploy path — for a benefit that is close to zero on six tables whose invariants live in the database. |
| **SQLAlchemy (ORM) + Alembic** | Would work, and is well maintained. Rejected because it makes *Alembic* the source of truth for the schema and `schema.prisma` a document nobody runs — which is the drift `S5.9` exists to prevent. Keeping Prisma as the author and dropping only its runtime is the smaller deviation. |
| **SQLAlchemy Core over the Prisma-authored schema** | Closer, and defensible. Rejected for now on size: it adds a dependency and an abstraction to write six tables of explicit SQL that `asyncpg` executes directly. Revisit if the repository layer outgrows one module. |
| **Hand-written migration SQL, no Prisma at all** | Removes the drift check entirely. The schema is where `governova schema` already runs its C14 analysis, and `#255` asked for exactly that — throwing it away to avoid one dev-time Node call is the wrong trade. |

---

## Approved Deviations

| Standard | Deviation | Approved alternative |
|---|---|---|
| `ADR-010 §2` inherited "PostgreSQL via Prisma" | The Prisma **client** is not used at runtime | Prisma authors schema and migrations; `asyncpg` executes. The database, the schema language and the migration tool are unchanged. |

---

> **Status: PROPOSED — 2026-08-23**
> *Ratification is L4 and belongs to the owner: Maluleke Kurhula Success.*
