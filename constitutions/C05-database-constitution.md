# C5 — Database Constitution

---

| Attribute          | Value                                                              |
|--------------------|--------------------------------------------------------------------|
| **Document**       | C5 — Database Constitution                                         |
| **Organisation**   | KSDRILL SA                                                         |
| **Version**        | v1.0                                                               |
| **Status**         | LOCKED                                                             |
| **Locked**         | 2026-05-08                                                         |
| **Next Review**    | 2026-08-08                                                         |
| **Applies To**     | Both Stacks                                                        |
| **Paired With**    | C5 — Database Implementation Guide                                 |

---

> *"One source of truth per data type. The right tool for the right data. ORM for clarity, SQL for power — both are first-class."*

---

## Opening Statement

The Database Constitution governs how data is stored, accessed, queried, migrated, and protected across all KSDRILL SA systems. Three database technologies serve three distinct, non-overlapping purposes: PostgreSQL for all structured relational data with ACID guarantees, MongoDB for flexible document data without rigid schemas (Angular stack only), and ChromaDB for vector embeddings and semantic similarity search (FundsLink Academy only). Data that belongs to one type must never be stored in another.

The database access philosophy in this constitution is explicit and enforced: **Prisma ORM is the primary interface for all standard database operations — inserts, updates, deletes, standard queries, paginated lists, and schema migrations. Raw SQL is a first-class, governed tool for use cases where the ORM is insufficient or architecturally inappropriate — complex aggregates, recursive CTEs, reporting queries, window functions, and precision financial calculations.** Both are professional industry tools. Neither is a fallback or a crutch. The choice between them is a technical decision governed by the criteria defined here — not by habit or preference.

This is identical to the frontend styling philosophy (Tailwind + Custom CSS): use the right tool for each job. ORM gives you type safety, migration management, and readable query code. Raw SQL gives you precision, performance, and expressiveness for complex data operations. Using only ORM for everything produces unmaintainable aggregate queries. Using only raw SQL for everything loses the migration tracking, type safety, and refactoring benefits that ORM provides.

This constitution does not govern how the frontend consumes API responses — that is C4. It does not govern how auth data flows through the service layer — that is C3, though it mandates the database assignment. It does not govern deployment of database infrastructure — that is C8. What this constitution governs is every decision made at the boundary between the application and its data: assignment, schema design, query patterns, transaction governance, migration protocol, and cross-database integrity.

---

## Table of Contents

| Part | Title | Standards |
|------|-------|-----------|
| Part 1 | Database Strategy & Assignment | S5.1–S5.8 |
| Part 2 | ORM Standards — Prisma as Primary Interface | S5.9–S5.18 |
| Part 3 | Raw SQL — Governed Use for Complex Queries | S5.19–S5.24 |
| Part 4 | PostgreSQL Schema Standards | S5.25–S5.32 |
| Part 5 | MongoDB & Beanie Standards | S5.33–S5.44 |
| Part 6 | ChromaDB — Vector Store Standards | S5.45–S5.52 |
| Part 7 | Cross-Database Integrity | S5.53–S5.58 |
| Part 8 | Migration Governance | S5.59–S5.64 |
| Anti-Patterns Index | — | AP-S5.* |
| Cross-Constitution Dependency Map | — | — |
| Amendment Log | — | — |

---

## Part 1 — Database Strategy & Assignment (`S5.1`–`S5.8`)

Assignment standards govern which data belongs to which database. These decisions are made at design time and are immutable without a constitutional amendment. Assignment errors are the most expensive class of database mistakes — they cannot be fixed without a data migration.

---

### S5.1 — Three-Database Separation — One Purpose Per Database Type

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S5.1 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S6.1` (stack assignment determines which databases are used) |
| **Enforced By** | Schema Review · Code Review |

**Standard:**
Three database technologies serve three purposes. PostgreSQL: structured relational data, ACID guarantees, all entities with relationships or financial implications. MongoDB: flexible document data, schema-evolving content, AI-generated content, application logs — Angular stack only. ChromaDB: vector embeddings, semantic similarity search, RAG context — FundsLink Academy only. A data entity that belongs to one type must never be stored in another.

**Rationale:**
The most expensive production database mistake is putting financial data in a non-ACID store, or putting schema-evolving content in a rigid relational schema. The three-database separation is designed to prevent both errors by making the assignment criteria explicit before schema work begins.

**Anti-Patterns:**
- `AP-S5.1a` — Storing financial transaction amounts in MongoDB because "it's already there" — MongoDB's eventual consistency model provides no ACID guarantees; balance inconsistency becomes possible.
- `AP-S5.1b` — Storing vector embeddings in PostgreSQL `JSONB` columns — PostgreSQL is not a vector similarity database; cosine similarity over JSONB is orders of magnitude slower than ChromaDB.

**Cross-References:** `S5.3` (financial data — PostgreSQL only), `S5.4` (auth data — PostgreSQL only), `CF-03` (Common Failure Register — financial data in MongoDB)

---

### S5.2 — PostgreSQL Is the System of Record — All Entities Originate Here

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S5.2 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S5.1` (three-database separation) |
| **Enforced By** | Schema Review · Code Review |

**Standard:**
Every core entity — user, student, funder, resident, account holder, creator — is first created and owned by PostgreSQL. MongoDB documents and ChromaDB embeddings reference these entities but are subordinate. If PostgreSQL and MongoDB ever report conflicting state for the same entity, PostgreSQL is correct. MongoDB is updated to match PostgreSQL.

**Rationale:**
Without a designated system of record, conflicts between databases have no resolution authority. The PostgreSQL-as-primary rule eliminates this ambiguity — there is always one source of truth for entity identity.

**Anti-Patterns:**
- `AP-S5.2a` — Creating a user document in MongoDB before creating the corresponding User record in PostgreSQL — the MongoDB document references an entity that does not yet exist.

**Cross-References:** `S5.1` (three-database separation), `S5.5` (cross-database references use PostgreSQL IDs)

---

### S5.3 — Financial Data in PostgreSQL Only — Never MongoDB or Redis

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S5.3 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S5.1` (three-database separation), `S5.2` (PostgreSQL as system of record) |
| **Enforced By** | Schema Review · Security Audit |

**Standard:**
All financial data — account balances, transaction amounts, deposit schedules, interest rates, lock periods, payment records — must live exclusively in PostgreSQL. This rule has no exceptions. MongoDB's eventual consistency and lack of native multi-document ACID transactions make it structurally unsuitable for financial records. Redis without persistence cannot guarantee durability.

**Rationale:**
A balance inconsistency caused by non-ACID storage is a financial integrity failure. Reserve Bank deposit schedules, FundsLink funding amounts, and any monetary calculation that must be correct for regulatory and user trust reasons require the full ACID guarantees only PostgreSQL provides.

**Anti-Patterns:**
- `AP-S5.3a` — `deposits_collection` in MongoDB with `amount` and `balance` fields — this is the CF-03 failure; MongoDB's lack of ACID means partial writes can leave balances inconsistent.

**Cross-References:** `CF-03` (Common Failure Register — financial in MongoDB = SEV0)

---

### S5.4 — Authentication Data in PostgreSQL Only

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S5.4 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S3.2` (C3 Auth — mandates PostgreSQL for auth data), `S5.1` |
| **Enforced By** | Schema Review · Security Audit |

**Standard:**
All authentication data — user credentials, password hashes, JWT refresh tokens, reset tokens, email verification tokens, session records, role assignments — lives in PostgreSQL. Authentication requires ACID consistency to prevent race conditions in token validation and session management. See S3.2 for the security rationale.

**Anti-Patterns:**
- `AP-S5.4a` — Session table in MongoDB on the Angular stack — MongoDB's eventual consistency creates race conditions in session invalidation, allowing revoked sessions to remain valid briefly.

**Cross-References:** `S3.2` (C3 mandates this), `CF-07` (auth data in MongoDB = SEV0)

---

### S5.5 — Cross-Database References Use PostgreSQL `cuid` — Never MongoDB ObjectID

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S5.5 |
| **Priority**    | Critical |
| **Applies To**  | Angular Only |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S5.2` (PostgreSQL as system of record), `S5.10` (cuid on all tables) |
| **Enforced By** | Schema Review · Code Review |

**Standard:**
When a MongoDB document or ChromaDB embedding references an entity that exists in PostgreSQL, the reference field stores the PostgreSQL `cuid` string value. MongoDB ObjectIDs are never used as cross-database foreign references. This keeps PostgreSQL as the unambiguous system of record and enables joins at the application layer without ambiguity.

**Anti-Patterns:**
- `AP-S5.5a` — `student_id: ObjectId` in a MongoDB scholarship document — MongoDB ObjectID has no meaning in PostgreSQL; the application layer cannot resolve the reference without a MongoDB query first.

**Cross-References:** `S5.2` (PostgreSQL system of record), `S5.10` (cuid standard)

---

### S5.6 — Database Selection Documented at Design Time — Never at Implementation Time

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S5.6 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S5.1` (three-database separation) |
| **Enforced By** | Feature proposal review (S1.27) |

**Standard:**
Every new data entity has its database destination documented in the feature proposal before schema work begins. The proposal must answer: relational joins needed? ACID required? Schema fixed or dynamic? AI-generated content? The answers determine the database. No ad-hoc database decisions at implementation time.

**Anti-Patterns:**
- `AP-S5.6a` — "We'll figure out where to store this when we build it" — ad-hoc decisions made at implementation time are driven by convenience rather than correctness.

**Cross-References:** `S1.27` (feature lifecycle — design phase includes database assignment), `S5.1` (criteria)

---

### S5.7 — No Direct Database Access from Frontend — Always Through Backend

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S5.7 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S2.1` (service layer owns all database access) |
| **Enforced By** | Code Review · Network audit |

**Standard:**
The browser never connects directly to PostgreSQL, MongoDB, or ChromaDB. All database access goes through the backend service layer — Next.js API routes (Next.js stack) or FastAPI (Angular stack). No client-side Prisma client, no browser MongoDB driver, no direct ChromaDB HTTP calls from Angular.

**Anti-Patterns:**
- `AP-S5.7a` — Prisma client imported in a Next.js client component — the database connection string is exposed to the browser bundle.

**Cross-References:** `S2.1` (service layer boundary), `CF-08` (direct API bypass — same principle)

---

### S5.8 — Soft Delete on All Databases — Never Hard Delete in Production

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S5.8 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S5.10` (required fields on every table) |
| **Enforced By** | Schema Review · Code Review |

**Standard:**
No production record is ever permanently deleted by user action. PostgreSQL uses `deleted_at DateTime?` via Prisma. MongoDB uses `deletedAt: Date` via Beanie. ChromaDB documents are archived, not deleted. All queries default-filter records where `deleted_at IS NULL`. Hard deletes require a documented admin process and are never triggered by user-facing actions.

**Rationale:**
Accidental deletions, disputes over deleted content, and audit requirements all require data to be recoverable. Hard deletes are irreversible; soft deletes are recoverable. The `deleted_at` filter is the default query behaviour, not an optional add-on.

**Anti-Patterns:**
- `AP-S5.8a` — `prisma.user.delete()` called from a user-facing "Delete Account" endpoint — hard delete is irreversible; soft delete enables account recovery and audit.

**Cross-References:** `S5.10` (required fields), `S5.12` (queries filter `deleted_at`)

---

## Part 2 — ORM Standards — Prisma as Primary Interface (`S5.9`–`S5.18`)

Prisma is the primary database interface for all standard PostgreSQL operations. It provides type safety, migration management, and readable query code. These standards govern how Prisma is used correctly and where its limitations define the boundary for raw SQL.

---

### S5.9 — Prisma Schema Is the Single Source of Truth — All Changes Through Migrations

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S5.9 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | — |
| **Enforced By** | CI — `prisma migrate diff` on every schema PR |

**Standard:**
The Prisma schema file (`schema.prisma`) is the authoritative definition of all PostgreSQL tables, columns, indexes, and relations. All schema changes go through `prisma migrate dev` (development) or `prisma migrate deploy` (production). Manual SQL DDL (`CREATE TABLE`, `ALTER TABLE`, `DROP COLUMN`) is forbidden outside of migration files. Every migration file is reviewed in the PR that introduces it.

**Rationale:**
Schema drift — where the database differs from what the application expects — is one of the most common causes of runtime errors. Prisma migrations maintain a complete history of every schema change and its order. Manual DDL bypasses this history, creating untracked drift.

**Anti-Patterns:**
- `AP-S5.9a` — Running `ALTER TABLE users ADD COLUMN phone VARCHAR(20)` directly on the database — the schema change is not in version control, not reproducible, and unknown to other developers.
- `AP-S5.9b` — Editing `schema.prisma` without generating a migration — the schema and the database diverge silently until the next `prisma migrate status` reveals the drift.

**Cross-References:** `S5.59` (migrations run before service starts), `CF-02` (raw SQL bypassing Prisma)

---

### S5.10 — Required Fields on Every PostgreSQL Table

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S5.10 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S5.9` (Prisma schema ownership) |
| **Enforced By** | CI — Prisma schema linter |

**Standard:**
Every Prisma model must define four base fields: `id String @id @default(cuid())`, `created_at DateTime @default(now())`, `updated_at DateTime @updatedAt`, `deleted_at DateTime?`. A Prisma schema linter in CI fails the build if any model is missing these fields. The `cuid()` function is used for IDs — not `autoincrement()`, not `uuid()`.

**Rationale:**
`cuid` IDs are safe to expose publicly (no sequential information), URL-safe, and sortable. The timestamp fields enable audit trails and time-based queries on every table. `deleted_at` enables soft delete across all models without per-model configuration.

**Anti-Patterns:**
- `AP-S5.10a` — `id Int @id @default(autoincrement())` — sequential integer IDs expose the total record count and enable enumeration attacks.
- `AP-S5.10b` — A model without `deleted_at` — hard deletes become the only option when soft delete is needed later, requiring a migration.

**Cross-References:** `S5.8` (soft delete), `S5.5` (cross-database refs use cuid)

---

### S5.11 — No SELECT * — Explicit `select` on Every Prisma Query

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S5.11 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S5.9` (Prisma as interface) |
| **Enforced By** | Code Review · ESLint/Pylint custom rule |

**Standard:**
Every `prisma.model.findMany()`, `findFirst()`, and `findUnique()` call includes an explicit `select` object listing only the fields required for that operation. Never call these methods without a `select` clause. This prevents accidental exposure of sensitive fields and reduces payload size.

**Rationale:**
A `prisma.user.findMany()` without `select` returns `password_hash`, `reset_token`, `refresh_token`, and every other sensitive field to whatever code calls it. The API contract between the database and the service layer should be as narrow as the operation requires.

**Anti-Patterns:**
- `AP-S5.11a` — `prisma.user.findMany()` without a `select` clause — returns all columns including password_hash, refresh tokens, and sensitive internal fields to the service layer.

**Cross-References:** `S3.8` (session callback — same principle), `S2.51` (response sanitisation)

---

### S5.12 — All Queries Filter `deleted_at: null` by Default

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S5.12 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S5.8` (soft delete), `S5.10` (required fields) |
| **Enforced By** | Prisma middleware · Code Review |

**Standard:**
Every query on a soft-deletable model includes `where: { deleted_at: null }` unless explicitly fetching deleted records for admin purposes. A Prisma middleware automatically appends this filter to all queries, providing a safety net. Queries that intentionally include soft-deleted records document this explicitly with a comment.

**Rationale:**
Without this filter, soft-deleted users can authenticate, soft-deleted scholarships appear in search results, and soft-deleted transactions appear in balance calculations. The middleware provides a system-level default; the standard requires explicit acknowledgement when the filter is intentionally bypassed.

**Anti-Patterns:**
- `AP-S5.12a` — A balance calculation query that includes soft-deleted transactions — produces incorrect balance totals that inflate the calculated balance.

**Cross-References:** `S5.8` (soft delete), `S5.22` (raw SQL must also filter deleted_at)

---

### S5.13 — Foreign Key Indexes on Every FK Field

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S5.13 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S5.9` (Prisma schema), `S5.10` (required fields) |
| **Enforced By** | CI — Prisma schema linter |

**Standard:**
Every foreign key field in the Prisma schema has an explicit `@@index` or `@index` annotation. Unindexed foreign keys cause full table scans on join queries. The Prisma schema linter in CI checks that all FK fields have indexes defined.

**Anti-Patterns:**
- `AP-S5.13a` — `user_id String` in a Scholarship model without `@@index([user_id])` — every query filtering by `user_id` performs a full table scan as scholarship data grows.

**Cross-References:** `S5.9` (Prisma schema), `S5.25` (index standards)

---

### S5.14 — Pagination on All List Queries — No Unbounded Results

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S5.14 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S2.39` (pagination in backend) |
| **Enforced By** | Code Review |

**Standard:**
Every Prisma query that returns a list of records includes `take` and `skip` (or cursor-based pagination). Default page size is 20 records. Maximum page size is 100 records. Never return an unbounded result set regardless of how few records currently exist. The `take` constraint is enforced at the Prisma query level — not by truncating an unbounded response.

**Anti-Patterns:**
- `AP-S5.14a` — `prisma.scholarship.findMany({ where: { status: 'ACTIVE' } })` without `take` — works correctly with 50 scholarships, causes memory exhaustion with 50,000.

**Cross-References:** `S2.39` (API pagination standard), `S5.19` (raw SQL also requires pagination)

---

### S5.15 — Transactions for Multi-Step Writes — `prisma.$transaction()`

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S5.15 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S5.9` (Prisma as interface) |
| **Enforced By** | Code Review |

**Standard:**
Any operation that writes to multiple tables must use `prisma.$transaction([])`. Never issue sequential writes without a transaction wrapper when partial failure would leave the database in an inconsistent state. This is especially critical for Reserve Bank deposit operations, FundsLink application submissions, role changes, and SyncUp pitch-to-subscription flows.

**Rationale:**
Sequential writes without transactions create a window where write 1 succeeds and write 2 fails. The database is left in a partial state with no clean recovery path. `prisma.$transaction` ensures both succeed or both roll back.

**Anti-Patterns:**
- `AP-S5.15a` — Sequential `prisma.deposit.create()` followed by `prisma.account.update()` without a transaction — a network error after the deposit creates an inconsistency where the deposit exists but the balance was not updated.

**Cross-References:** `S5.3` (financial data integrity), `S5.20` (raw SQL transactions)

---

### S5.16 — Prisma Singleton Client — Never Instantiate Per Request

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S5.16 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S5.9` (Prisma as interface) |
| **Enforced By** | Code Review |

**Standard:**
The Prisma client is instantiated once as a singleton and imported from a shared module (`src/lib/prisma.ts` in Next.js). A new `PrismaClient()` is never instantiated per-request or per-function. Multiple client instances exhaust the PostgreSQL connection pool.

**Anti-Patterns:**
- `AP-S5.16a` — `const prisma = new PrismaClient()` at the top of every API route file — each hot-reload or deployment creates new connections; the connection pool exhausts under normal traffic.

**Cross-References:** `S5.9` (Prisma ownership), `S2.37` (connection pool standards)

---

### S5.17 — Prisma Client Generates TypeScript Types — Never Cast or Override

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S5.17 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S5.9` (Prisma schema as source of truth) |
| **Enforced By** | TypeScript strict mode |

**Standard:**
Prisma's generated TypeScript types are used throughout the service layer. Casting query results with `as SomeType` is forbidden when the Prisma-generated type is available. If a custom type is needed, it is derived from Prisma types using `Prisma.UserGetPayload<...>` utilities.

**Anti-Patterns:**
- `AP-S5.17a` — `const user = (await prisma.user.findUnique(...)) as CustomUserType` — the TypeScript type assertion bypasses Prisma's type guarantees; schema changes cause runtime errors instead of compile-time errors.

**Cross-References:** `S5.9` (Prisma schema), `S1.48` (TypeScript strict mode)

---

### S5.18 — Beanie ODM for All MongoDB Access — Angular Stack

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S5.18 |
| **Priority**    | Critical |
| **Applies To**  | Angular Only |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S5.1` (three-database separation) |
| **Enforced By** | Code Review |

**Standard:**
All MongoDB access on the Angular stack uses the Beanie ODM. Direct PyMongo collection access is used only when Beanie's API is insufficient for a specific operation, with a comment explaining why. Beanie provides Pydantic model validation, async support, and type safety at the MongoDB boundary — identical in philosophy to Prisma at the PostgreSQL boundary.

**Anti-Patterns:**
- `AP-S5.18a` — `db["scholarship_content"].insert_one(doc)` without Beanie — bypasses Pydantic validation, loses type safety, and produces unvalidated data in MongoDB.

**Cross-References:** `S5.1` (MongoDB purpose), `S5.36` (MongoDB required fields)

---

## Part 3 — Raw SQL — Governed Use for Complex Queries (`S5.19`–`S5.24`)

Raw SQL is a first-class, governed tool in the KSDRILL SA database strategy. It is used where the ORM is insufficient or architecturally inappropriate. This is a professional engineering decision, not a shortcut.

---

### S5.19 — Raw SQL for Complex Queries That ORM Cannot Express Cleanly

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S5.19 |
| **Priority**    | Standard |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S5.9` (Prisma as primary), `S5.20` (raw SQL safety) |
| **Enforced By** | Code Review · Explicit comment requirement |

**Standard:**
Raw SQL via `prisma.$queryRaw` (TypeScript) or `db.execute(text(...))` (Python/SQLAlchemy) is the correct tool for: complex aggregates with `GROUP BY` and `HAVING`, recursive CTEs for hierarchical data, window functions (`ROW_NUMBER`, `RANK`, `LAG`, `LEAD`), `LATERAL JOIN` patterns, reporting queries with complex filters, and precision financial calculations requiring SQL-native decimal arithmetic. Every raw SQL block must include a comment explaining why Prisma is insufficient for this specific query.

**Rationale:**
Forcing complex aggregate or window function queries through an ORM produces either multiple round-trips to the database (N+1 patterns) or convoluted query builder chains that are harder to read than the equivalent SQL. The same logic that makes Tailwind insufficient for brand CSS makes ORM insufficient for complex analytics — the specialised tool is the right tool.

**Anti-Patterns:**
- `AP-S5.19a` — Raw SQL for a simple `WHERE id = ? AND deleted_at IS NULL` query — Prisma handles this correctly and provides type safety; raw SQL adds no value and loses type checking.
- `AP-S5.19b` — Raw SQL without a comment explaining why ORM is insufficient — every raw SQL block in the codebase must justify its existence.

**Cross-References:** `S5.9` (Prisma for standard queries), `S5.20` (raw SQL safety), `S5.21` (parameterisation)

---

### S5.20 — Raw SQL Wrapped in Transactions for Multi-Step Operations

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S5.20 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S5.19` (raw SQL use cases), `S5.15` (transaction governance) |
| **Enforced By** | Code Review |

**Standard:**
Raw SQL operations that involve multiple writes use `prisma.$transaction(async (tx) => { ... })` for interactive transactions, or explicit `BEGIN / COMMIT / ROLLBACK` when Prisma's transaction API is insufficient. Raw SQL writes that are not wrapped in a transaction are a code review block.

**Rationale:**
The transaction requirement applies equally to ORM writes and raw SQL writes. The tool changes but the atomicity requirement does not. Multi-step raw SQL writes without transactions are a financial integrity risk on Reserve Bank and FundsLink.

**Anti-Patterns:**
- `AP-S5.20a` — Sequential `prisma.$executeRaw` calls without a transaction wrapper — the first raw write succeeds; the second fails; the database is left in an inconsistent state with no rollback path.

**Cross-References:** `S5.15` (ORM transactions), `S5.3` (financial data integrity)

---

### S5.21 — Raw SQL Always Parameterised — Never String-Interpolated

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S5.21 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S5.19` (raw SQL use cases) |
| **Enforced By** | Code Review · Security audit · ESLint/Pylint |

**Standard:**
All raw SQL queries use parameterised inputs exclusively. `prisma.$queryRaw` uses the tagged template literal form (`Prisma.sql\`...\``) which automatically parameterises. Python raw SQL uses `text(query)` with bound parameters from SQLAlchemy — never f-string or `%`-formatted SQL. String interpolation into SQL is SQL injection — it is forbidden without exception.

**Rationale:**
SQL injection is the most common critical web application vulnerability. Parameterised queries are the absolute defence — parameters are never interpreted as SQL syntax regardless of their content. This is not a guideline; it is a security requirement.

**Anti-Patterns:**
- `AP-S5.21a` — `prisma.$queryRawUnsafe(\`SELECT * FROM users WHERE id = '${userId}'\`)` — direct string interpolation into SQL; `userId` can be `' OR '1'='1` and extract the entire table.
- `AP-S5.21b` — `f"SELECT * FROM deposits WHERE user_id = '{user_id}'"` in Python — identical vulnerability pattern in FastAPI.

**Cross-References:** `S5.19` (raw SQL use cases), `S2.49` (SQL injection in security middleware)

---

### S5.22 — Raw SQL Must Apply Soft Delete Filter — No Implicit Bypass

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S5.22 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S5.19` (raw SQL), `S5.12` (soft delete filter) |
| **Enforced By** | Code Review |

**Standard:**
Raw SQL queries that target soft-deletable tables must include `AND deleted_at IS NULL` (or `WHERE deleted_at IS NULL`) in the WHERE clause. Prisma middleware applies the soft delete filter to ORM queries automatically; raw SQL bypasses this middleware. The filter must be applied manually and explicitly.

**Rationale:**
The Prisma soft delete middleware is not invoked for `$queryRaw` or `$executeRaw`. A raw SQL query that omits the soft delete filter will include deleted records silently, producing incorrect aggregate results.

**Anti-Patterns:**
- `AP-S5.22a` — `SELECT SUM(amount) FROM deposits WHERE user_id = $1` without `AND deleted_at IS NULL` — includes soft-deleted deposits in the balance calculation, overstating the user's balance.

**Cross-References:** `S5.12` (soft delete filter standard), `S5.8` (soft delete)

---

### S5.23 — Raw SQL Results Validated with TypeScript/Pydantic Types

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S5.23 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S5.19` (raw SQL), `S5.21` (parameterised) |
| **Enforced By** | Code Review |

**Standard:**
Raw SQL query results in TypeScript are typed using `prisma.$queryRaw<T[]>` with an explicit TypeScript interface for the result shape. Python raw SQL results are validated through a Pydantic model. Raw SQL that returns `any[]` or `dict` without type validation bypasses the type safety that Prisma would otherwise provide.

**Anti-Patterns:**
- `AP-S5.23a` — `const result = await prisma.$queryRaw<any[]>(...)` — the type assertion `any[]` defeats the purpose of TypeScript; schema changes produce runtime errors instead of compile-time errors.

**Cross-References:** `S5.17` (Prisma types), `S1.48` (TypeScript strict mode)

---

### S5.24 — Raw SQL Isolated in Dedicated Query Functions — Never Inline in API Routes

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S5.24 |
| **Priority**    | Standard |
| **Applies To**  | Both Stacks |
| **Phase**       : Phase 1 — Core Architecture |
| **Depends On**  | `S5.19` (raw SQL), `S2.1` (service layer separation) |
| **Enforced By** | Code Review |

**Standard:**
Raw SQL queries are isolated in dedicated query functions within the service layer — not inline in API route handlers. Each raw SQL function has a descriptive name (`getStudentFundingMatchAggregates`), type annotations, and the explanatory comment required by S5.19. This makes raw SQL visible, reviewable, and testable in isolation.

**Anti-Patterns:**
- `AP-S5.24a` — Raw SQL written inline in a Next.js API route handler — not discoverable as raw SQL during review, not independently testable, not reusable.

**Cross-References:** `S5.19` (raw SQL with comment), `S2.1` (service layer)

---

## Part 4 — PostgreSQL Schema Standards (`S5.25`–`S5.32`)

---

### S5.25 — Indexes on All Query-Critical Fields

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S5.25 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S5.13` (FK indexes), `S5.9` (Prisma schema) |
| **Enforced By** | Schema Review · Query performance audit |

**Standard:**
All fields used in WHERE clauses of high-frequency queries have explicit indexes defined in the Prisma schema. Beyond FK fields (S5.13), index candidates include: email (unique index), status fields used in list queries, date fields used in range queries, and any composite index for multi-field query patterns.

**Anti-Patterns:**
- `AP-S5.25a` — `WHERE status = 'ACTIVE' AND created_at > ?` on the Scholarship table without a composite index on `(status, created_at)` — full table scan on every scholarship list query.

**Cross-References:** `S5.13` (FK indexes), `S5.9` (Prisma schema)

---

### S5.26–S5.32 — Additional PostgreSQL Standards

> **S5.26** — Never expose `password_hash`, `reset_token`, `refresh_token`, `deleted_at`, or `internal_notes` fields in any Prisma select query for API responses. These fields are read-only at the database access layer.

> **S5.27** — PostgreSQL enum types for all constrained value sets (status, role, type) — string columns for constrained values allow invalid values at the database level.

> **S5.28** — Decimal columns for all monetary values — never `Float`. `Decimal` preserves precision; `Float` introduces rounding errors on financial calculations.

> **S5.29** — `NOT NULL` constraints on all required fields — database-level constraints enforce data integrity independently of application-level validation.

> **S5.30** — `UNIQUE` constraints on fields that must be unique — `email`, `cuid` alternate keys, slug fields — enforce at the database level, not only in application code.

> **S5.31** — `CHECK` constraints on business-rule-constrained fields — `amount > 0` for deposits, `interest_rate BETWEEN 0 AND 1` for rates. Database enforces invariants independently of the application.

> **S5.32** — Connection pooling via PgBouncer on Railway — direct database connections from the application are pooled; unbounded direct connections exhaust PostgreSQL's connection limit under load.

---

## Part 5 — MongoDB & Beanie Standards (`S5.33`–`S5.44`)

MongoDB standards apply exclusively to Angular stack systems (FundsLink Academy, KSDRILL Reserve Bank).

---

### S5.33 — MongoDB for Document Data Only — Defined Exclusions Apply

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S5.33 |
| **Priority**    | Critical |
| **Applies To**  | Angular Only |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S5.1` (three-database separation), `S5.3` (financial → PostgreSQL) |
| **Enforced By** | Schema Review · Code Review |

**Standard:**
MongoDB stores: AI-generated scholarship reasoning, dynamic content with evolving schemas (tags, categories, descriptions), application logs and events, and feature-rich content not requiring cross-table joins. MongoDB never stores: financial transactions, account balances, authentication data, data requiring foreign key constraints, or vector embeddings. These exclusions are absolute.

**Anti-Patterns:**
- `AP-S5.33a` — Using MongoDB for scholarship application status tracking because "it's schemaless" — application status is relational data with foreign key constraints to the User and Scholarship tables; PostgreSQL is correct.

**Cross-References:** `S5.3` (financial — PostgreSQL only), `S5.4` (auth — PostgreSQL only), `S5.1`

---

### S5.34–S5.44 — MongoDB Operational Standards

> **S5.34** — Beanie document models include timestamps (`created_at`, `updated_at`) and soft delete (`deleted_at`) on every collection — mirrors the PostgreSQL required fields pattern (S5.10).

> **S5.35** — All Beanie queries include `deleted_at: None` in the filter — soft delete filter applied explicitly (MongoDB has no middleware equivalent to Prisma's).

> **S5.36** — MongoDB collection names are snake_case and plural — `scholarship_contents`, `application_logs`, `ai_reasoning_records`.

> **S5.37** — MongoDB indexes defined in Beanie model class using `Settings.indexes` — not created ad-hoc or manually in the database.

> **S5.38** — MongoDB documents that reference PostgreSQL entities use `pg_id: str` field storing the PostgreSQL `cuid` — per S5.5.

> **S5.39** — Beanie schemas validated with Pydantic v2 — the same validation library used for FastAPI request/response models.

> **S5.40** — Maximum document size awareness — documents larger than 1MB signal a design problem; split into multiple documents or move to object storage.

> **S5.41** — No transactions spanning PostgreSQL and MongoDB in a single operation — if cross-database atomicity is needed, the operation design must be reconsidered.

> **S5.42** — MongoDB connection string in Railway Secrets — never committed to version control.

> **S5.43** — MongoDB aggregation pipelines isolated in dedicated service functions with Pydantic result validation — same principle as raw SQL isolation (S5.24).

> **S5.44** — MongoDB write operations always await confirmation — never fire-and-forget writes to MongoDB from the service layer.

---

## Part 6 — ChromaDB Vector Store Standards (`S5.45`–`S5.52`)

ChromaDB standards apply exclusively to FundsLink Academy.

---

### S5.45 — ChromaDB for Vector Similarity Only — No Structured Data

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S5.45 |
| **Priority**    | Critical |
| **Applies To**  | Angular Only — FundsLink Only |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S5.1` (three-database separation) |
| **Enforced By** | Schema Review · Code Review |

**Standard:**
ChromaDB stores only vector embeddings and their associated semantic metadata (document chunk, source reference, embedding model). Structured data — user IDs, scholarship titles, amounts, dates — lives in PostgreSQL. ChromaDB metadata fields store only the PostgreSQL `cuid` reference needed to retrieve the full document from its authoritative source.

**Anti-Patterns:**
- `AP-S5.45a` — Storing scholarship amounts and eligibility criteria in ChromaDB metadata — duplicates PostgreSQL data; ChromaDB metadata is not the system of record.

**Cross-References:** `S5.1` (three-database separation), `S5.2` (PostgreSQL as system of record)

---

### S5.46–S5.52 — ChromaDB Operational Standards

> **S5.46** — ChromaDB runs as a separate Railway service with a persistent volume — never co-located with the FastAPI service; volume ensures embedding persistence across restarts.

> **S5.47** — The FastAPI AI service is the only service with write access to ChromaDB — other services are read-only; only the AI embedding pipeline creates or updates embeddings.

> **S5.48** — Similarity threshold minimum 0.7 for matching queries — results below 0.7 cosine similarity are discarded, not returned to the user.

> **S5.49** — ChromaDB collections named by content type and version — `scholarship_embeddings_v1`, `eligibility_documents_v1` — versioning enables migration to a new embedding model without downtime.

> **S5.50** — ChromaDB internal URL only — the ChromaDB Railway service has no public port; only the FastAPI service on the Railway internal network connects to it.

> **S5.51** — Embedding model is locked per collection — changing the embedding model requires a new collection and a re-embedding migration pipeline, not an in-place update.

> **S5.52** — ChromaDB reads in the AI service use `max_results` limits — unbounded similarity searches are forbidden.

---

## Part 7 — Cross-Database Integrity (`S5.53`–`S5.58`)

---

### S5.53 — Explicit Cross-Database Sync Is Tested

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S5.53 |
| **Priority**    | High |
| **Applies To**  | Angular Only |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S5.2` (PostgreSQL system of record), `S7.15` (cross-DB integration tests) |
| **Enforced By** | Integration test CI gate |

**Standard:**
Every operation that writes to multiple databases (PostgreSQL + MongoDB, PostgreSQL + ChromaDB) has an integration test verifying: (1) both writes succeed correctly, and (2) when the second write fails, the first write rolls back or is marked as needing retry. Cross-database sync failures are logged and alerted.

**Anti-Patterns:**
- `AP-S5.53a` — No integration test for the scholarship creation flow that writes to both PostgreSQL and MongoDB — the failure case (PostgreSQL succeeds, MongoDB fails) is untested and produces an orphaned PostgreSQL record.

**Cross-References:** `S7.15` (cross-DB integration test requirement), `S5.2` (PostgreSQL system of record)

---

### S5.54–S5.58 — Additional Cross-Database Standards

> **S5.54** — If a PostgreSQL record is soft-deleted, the corresponding MongoDB documents and ChromaDB embeddings are also soft-deleted in the same logical operation — referential integrity is maintained across database types.

> **S5.55** — The cross-database sync operation is idempotent — running it twice produces the same result as running it once; enables safe retry on failure.

> **S5.56** — Cross-database queries (retrieving a MongoDB document and its PostgreSQL entity) are performed as two separate queries joined at the application layer — never attempted through database-level mechanisms.

> **S5.57** — Background jobs that sync data between databases are monitored for failure and alert on missed runs (per C8 platform reliability standards).

> **S5.58** — A reconciliation script exists for each cross-database relationship that can detect and report orphaned records — run quarterly or after incidents.

---

## Part 8 — Migration Governance (`S5.59`–`S5.64`)

---

### S5.59 — Migrations Run Before Service Starts — Migration-First Deploy

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S5.59 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S5.9` (Prisma schema ownership), `S8.6` (zero-downtime deploys) |
| **Enforced By** | CI/CD deploy pipeline |

**Standard:**
Database migrations run as the first step of every production deployment, before the new service version starts. The deployment pipeline is: run `prisma migrate deploy` → health check migration success → deploy new service version. If migration fails, deployment stops and does not proceed. A new service version should never start against an unmigrated schema.

**Rationale:**
CF-13 (Common Failure Register): service starts before migration completes, writes occur against old schema, data corruption is possible during the window between service start and migration completion. Migration-first deploy eliminates this window.

**Cross-References:** `CF-13` (migration timing failure), `S8.6` (zero-downtime deploy), `S8.14` (prisma validate in CI)

---

### S5.60–S5.64 — Additional Migration Standards

> **S5.60** — All migrations are backward-compatible with the previous service version — enables zero-downtime rolling deploys where the old service runs briefly against the new schema.

> **S5.61** — Never delete a column in the same migration that removes it from the code — deprecate the column first (remove from code, keep in schema), then delete in a subsequent migration after the first migration has deployed successfully.

> **S5.62** — Migration files are never edited after they have been committed — a migration that has been run on any environment is immutable. Create a new migration to correct it.

> **S5.63** — `prisma migrate diff` runs in CI on every PR that changes `schema.prisma` — detects missing migration files before the PR is merged.

> **S5.64** — Staging migration is performed before production migration — staging is the validation environment for the migration plan.

---

## Anti-Patterns Index

| ID | Description | Violated Standard | Severity |
|----|-------------|-------------------|----------|
| `AP-S5.1a` | Financial data in MongoDB | S5.1 | Critical |
| `AP-S5.1b` | Vector embeddings in PostgreSQL JSONB | S5.1 | High |
| `AP-S5.2a` | MongoDB document created before PostgreSQL entity | S5.2 | High |
| `AP-S5.3a` | `deposits_collection` in MongoDB with financial fields | S5.3 | Critical |
| `AP-S5.4a` | Session table in MongoDB | S5.4 | Critical |
| `AP-S5.5a` | MongoDB ObjectId used as cross-database foreign reference | S5.5 | Critical |
| `AP-S5.6a` | Ad-hoc database decisions at implementation time | S5.6 | High |
| `AP-S5.7a` | Prisma client in Next.js client component | S5.7 | Critical |
| `AP-S5.8a` | `prisma.user.delete()` from user-facing endpoint | S5.8 | High |
| `AP-S5.9a` | Manual `ALTER TABLE` directly on database | S5.9 | Critical |
| `AP-S5.9b` | Editing `schema.prisma` without generating migration | S5.9 | High |
| `AP-S5.10a` | `@id @default(autoincrement())` integer IDs | S5.10 | High |
| `AP-S5.10b` | Model without `deleted_at` field | S5.10 | High |
| `AP-S5.11a` | `prisma.user.findMany()` without `select` clause | S5.11 | Critical |
| `AP-S5.12a` | Balance query including soft-deleted transactions | S5.12 | Critical |
| `AP-S5.13a` | Foreign key field without index annotation | S5.13 | High |
| `AP-S5.14a` | `findMany` without `take` limit | S5.14 | High |
| `AP-S5.15a` | Sequential writes without `prisma.$transaction()` | S5.15 | Critical |
| `AP-S5.16a` | `new PrismaClient()` per request or API route | S5.16 | High |
| `AP-S5.17a` | `as CustomUserType` cast on Prisma query result | S5.17 | High |
| `AP-S5.18a` | Direct PyMongo collection access without Beanie | S5.18 | High |
| `AP-S5.19a` | Raw SQL for simple WHERE clause Prisma handles | S5.19 | Standard |
| `AP-S5.19b` | Raw SQL without explanatory comment | S5.19 | Standard |
| `AP-S5.20a` | Sequential `$executeRaw` without transaction | S5.20 | Critical |
| `AP-S5.21a` | `$queryRawUnsafe` with string interpolation | S5.21 | Critical |
| `AP-S5.21b` | f-string SQL in Python FastAPI | S5.21 | Critical |
| `AP-S5.22a` | Raw SQL without `deleted_at IS NULL` filter | S5.22 | Critical |
| `AP-S5.23a` | `$queryRaw<any[]>` without typed result interface | S5.23 | High |
| `AP-S5.24a` | Raw SQL inline in API route handler | S5.24 | Standard |
| `AP-S5.25a` | Multi-field WHERE query without composite index | S5.25 | High |
| `AP-S5.33a` | Relational data with FK constraints in MongoDB | S5.33 | Critical |
| `AP-S5.45a` | Structured data stored in ChromaDB metadata | S5.45 | High |
| `AP-S5.53a` | No integration test for cross-database write operation | S5.53 | High |

---

## Cross-Constitution Dependency Map

**This constitution depends on:**
| Dependency | Reason |
|------------|--------|
| `C0 — Constitutional Order` | Amendment protocol, terminology |
| `C2 — Backend Constitution` | Service layer governs how databases are accessed (S2.1) |

**The following constitutions depend on this one:**
| Dependent | Reason |
|-----------|--------|
| `C2 — Backend Constitution` | Database access patterns enforced at backend service layer |
| `C3 — Auth Constitution` | Auth data storage assignment (S5.4) mandated by C3 |
| `C6 — Full-Stack Architecture` | DB access patterns and cross-stack data flows reference C5 |
| `C7 — Testing Constitution` | Test database standards and cross-DB integration test requirements |
| `C8 — Platform Reliability` | Migration governance in deployment pipeline (S5.59) |

---

## Amendment Log

| Version | Date | Change | Reason |
|---------|------|--------|--------|
| v1.0 | 2026-05-08 | Initial lock — rebuilt from Database Constitution v3.0. Raw SQL governance formalised as Part 3 (S5.19–S5.24) — raw SQL elevated to first-class governed tool alongside Prisma ORM. `prisma.$queryRaw` parameterisation (S5.21) and soft delete filter obligation for raw SQL (S5.22) added. Decimal column mandate for monetary values (S5.28) added. Terminology updated. Standard IDs introduced. | Full system rebuild + raw SQL governance formalisation. |

---

> **LOCKED — v1.0 — 2026-05-08**
>
> This document is locked. No standard may be added, removed, or modified
> without following the Amendment Protocol defined in C0 §8.
> Amendments take effect only after commit to `system-design-template`
> with a version bump and amendment log entry.
