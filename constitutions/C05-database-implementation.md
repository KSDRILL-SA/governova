# C5 — Database Implementation Guide

---

| Attribute          | Value                                                              |
|--------------------|--------------------------------------------------------------------|
| **Document**       | C5 — Database Implementation Guide                                 |
| **Organisation**   | KSDRILL SA                                                         |
| **Version**        | v1.0                                                               |
| **Status**         | LOCKED                                                             |
| **Locked**         | 2026-05-08                                                         |
| **Next Review**    | 2026-08-08                                                         |
| **Applies To**     | Both Stacks                                                        |
| **Paired With**    | C5 — Database Constitution                                         |

---

> *"A standard tells you what must be true. This guide tells you how to make it true."*

---

## Opening Statement

This guide is the operational companion to C5. Every practice satisfies a specific C5 standard. The constitution contains the why. This guide contains the how — schemas, queries, patterns, and step-by-step procedures for PostgreSQL + Prisma, raw SQL, MongoDB + Beanie, and ChromaDB.

Read the constitution to understand what must be true about the database layer. Use this guide when building it.

---

## Table of Contents

| Section | Title |
|---------|-------|
| P5.1 | Installation and Singleton Client |
| P5.2 | Complete Prisma Schema — All Systems |
| P5.3 | Prisma Middleware — Soft Delete Filter |
| P5.4 | Explicit Select Pattern |
| P5.5 | Pagination — Cursor-Based and Offset |
| P5.6 | Transaction Pattern — Multi-Step Writes |
| P5.7 | Raw SQL — Governed Patterns with Full Safety |
| P5.8 | Beanie MongoDB Setup and Patterns |
| P5.9 | ChromaDB Client — FundsLink AI Pipeline |
| P5.10 | Cross-Database Sync Pattern |
| P5.11 | Migration Workflow |
| P5.12 | Prisma Schema Linter CI Configuration |
| P5.13 | Tools & Commands Reference |

---

## P5.1 — Installation and Singleton Client (S5.9, S5.16)

```bash
npm install prisma @prisma/client
npx prisma init --datasource-provider postgresql
```

### Singleton Client (`src/lib/prisma.ts`) — S5.16

```typescript
import { PrismaClient } from "@prisma/client"

// Prevent multiple instances in Next.js hot-reload (S5.16)
const globalForPrisma = globalThis as unknown as { prisma: PrismaClient }

export const prisma =
  globalForPrisma.prisma ??
  new PrismaClient({
    log: process.env.NODE_ENV === "development"
      ? ["query", "warn", "error"]
      : ["warn", "error"],
  })

if (process.env.NODE_ENV !== "production") globalForPrisma.prisma = prisma
```

---

## P5.2 — Complete Prisma Schema — All Systems (S5.9, S5.10, S5.13)

```prisma
// schema.prisma
// Every model follows the required field pattern (S5.10)
// Every FK has an explicit index (S5.13)
// Monetary fields use Decimal (S5.28)

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

// ─── SHARED ENUMS ─────────────────────────────────────────────────────────────

enum Role {
  USER
  ADMIN
  // Next.js systems
  CREATOR        // SyncUp only
  WARD_ADMIN     // Maphophe only
  // Angular systems
  STUDENT        // FundsLink only
  FUNDER         // FundsLink only
  ACCOUNT_HOLDER // Reserve Bank only
}

// ─── SHARED AUTH MODELS (Both Stacks) ─────────────────────────────────────────

model User {
  id            String    @id @default(cuid())
  created_at    DateTime  @default(now())
  updated_at    DateTime  @updatedAt
  deleted_at    DateTime?

  email         String    @unique
  email_verified DateTime?
  password_hash String?
  name          String?
  image         String?
  role          Role      @default(USER)

  // NextAuth tables — Next.js stack only
  sessions      Session[]
  accounts      Account[]

  // JWT tables — Angular stack only
  refresh_tokens RefreshToken[]

  // Shared
  audit_logs    AuditLog[]
  feature_flags FeatureFlagOverride[]

  @@index([email])
  @@index([role])
}

model Session {
  id            String   @id @default(cuid())
  created_at    DateTime @default(now())
  updated_at    DateTime @updatedAt

  session_token String   @unique
  user_id       String
  expires       DateTime

  user          User     @relation(fields: [user_id], references: [id], onDelete: Cascade)

  @@index([user_id])
  @@index([session_token])
  @@index([expires])
}

model Account {
  id                  String  @id @default(cuid())
  created_at          DateTime @default(now())
  updated_at          DateTime @updatedAt

  user_id             String
  type                String
  provider            String
  provider_account_id String
  refresh_token       String? @db.Text
  access_token        String? @db.Text
  expires_at          Int?
  token_type          String?
  scope               String?
  id_token            String? @db.Text

  user                User    @relation(fields: [user_id], references: [id], onDelete: Cascade)

  @@unique([provider, provider_account_id])
  @@index([user_id])
}

model RefreshToken {
  id          String    @id @default(cuid())
  created_at  DateTime  @default(now())

  token_hash  String    @unique
  user_id     String
  expires_at  DateTime
  revoked_at  DateTime?
  replaced_by String?

  user        User      @relation(fields: [user_id], references: [id], onDelete: Cascade)

  @@index([user_id])
  @@index([token_hash])
  @@index([expires_at])
}

// Immutable — no deleted_at (S3.33)
model AuditLog {
  id         String   @id @default(cuid())
  created_at DateTime @default(now())

  user_id    String?
  event      String
  ip_address String?
  user_agent String?
  metadata   Json?

  user       User?    @relation(fields: [user_id], references: [id])

  @@index([user_id])
  @@index([event])
  @@index([created_at])
}

model VerificationToken {
  id         String   @id @default(cuid())
  created_at DateTime @default(now())

  identifier String
  token      String   @unique
  expires    DateTime

  @@unique([identifier, token])
  @@index([token])
  @@index([expires])
}

model SystemConfig {
  id         String   @id @default(cuid())
  created_at DateTime @default(now())
  updated_at DateTime @updatedAt

  key        String   @unique
  value      Json

  @@index([key])
}

model FeatureFlag {
  id          String   @id @default(cuid())
  created_at  DateTime @default(now())
  updated_at  DateTime @updatedAt

  key         String   @unique
  enabled     Boolean  @default(false)
  description String?

  overrides   FeatureFlagOverride[]
  @@index([key])
}

model FeatureFlagOverride {
  id          String   @id @default(cuid())
  created_at  DateTime @default(now())

  flag_id     String
  user_id     String
  enabled     Boolean

  flag        FeatureFlag @relation(fields: [flag_id], references: [id])
  user        User        @relation(fields: [user_id], references: [id])

  @@unique([flag_id, user_id])
  @@index([flag_id])
  @@index([user_id])
}

// ─── FUNDSLINK ACADEMY ────────────────────────────────────────────────────────

model Student {
  id              String    @id @default(cuid())
  created_at      DateTime  @default(now())
  updated_at      DateTime  @updatedAt
  deleted_at      DateTime?

  user_id         String    @unique
  institution     String
  qualification   String
  year_of_study   Int
  gpa             Decimal   @db.Decimal(4, 2) // S5.28 — Decimal for academic scores

  applications    Application[]

  @@index([user_id])
  @@index([institution])
}

model Scholarship {
  id          String           @id @default(cuid())
  created_at  DateTime         @default(now())
  updated_at  DateTime         @updatedAt
  deleted_at  DateTime?

  title       String
  description String           @db.Text
  amount      Decimal          @db.Decimal(19, 4)   // S5.28 — Decimal
  min_gpa     Decimal          @db.Decimal(4, 2)
  funder_id   String
  status      ScholarshipStatus @default(ACTIVE)

  applications Application[]

  @@index([funder_id])
  @@index([status])
  @@index([min_gpa])
}

enum ScholarshipStatus { ACTIVE PAUSED CLOSED }

model Application {
  id             String            @id @default(cuid())
  created_at     DateTime          @default(now())
  updated_at     DateTime          @updatedAt
  deleted_at     DateTime?

  student_id     String
  scholarship_id String
  motivation     String            @db.Text
  status         ApplicationStatus @default(PENDING)
  reference      String            @unique @default(cuid())

  student        Student       @relation(fields: [student_id], references: [id])
  scholarship    Scholarship   @relation(fields: [scholarship_id], references: [id])

  @@index([student_id])
  @@index([scholarship_id])
  @@index([status])
}

enum ApplicationStatus { PENDING UNDER_REVIEW APPROVED REJECTED }

// ─── KSDRILL RESERVE BANK ─────────────────────────────────────────────────────

model Account {
  id           String    @id @default(cuid())
  created_at   DateTime  @default(now())
  updated_at   DateTime  @updatedAt
  deleted_at   DateTime?

  user_id      String    @unique
  balance      Decimal   @db.Decimal(19, 4) @default(0) // S5.28 — NEVER Float
  account_no   String    @unique @default(cuid())

  goals        SavingsGoal[]
  transactions Transaction[]

  @@index([user_id])
  @@index([account_no])
}

model SavingsGoal {
  id           String    @id @default(cuid())
  created_at   DateTime  @default(now())
  updated_at   DateTime  @updatedAt
  deleted_at   DateTime?

  account_id   String
  title        String
  target       Decimal   @db.Decimal(19, 4) // S5.28
  saved        Decimal   @db.Decimal(19, 4) @default(0)
  deadline     DateTime?
  status       GoalStatus @default(ACTIVE)

  account      Account   @relation(fields: [account_id], references: [id])

  @@index([account_id])
  @@index([status])
}

enum GoalStatus { ACTIVE COMPLETED CANCELLED }

model Transaction {
  id           String          @id @default(cuid())
  created_at   DateTime        @default(now())
  updated_at   DateTime        @updatedAt
  deleted_at   DateTime?

  account_id   String
  amount       Decimal         @db.Decimal(19, 4) // S5.28 — NEVER Float
  type         TransactionType
  reference    String          @unique @default(cuid())
  note         String?

  account      Account         @relation(fields: [account_id], references: [id])

  @@index([account_id])
  @@index([type])
  @@index([created_at])
}

enum TransactionType { DEPOSIT WITHDRAWAL INTEREST ADJUSTMENT }

// S5.27 — Check constraints enforced at database level
// Add via migration: ALTER TABLE "Transaction" ADD CONSTRAINT "amount_positive" CHECK (amount > 0);

// ─── MAPHOPHE COMMUNITY SYSTEM ────────────────────────────────────────────────

model ServiceRequest {
  id          String               @id @default(cuid())
  created_at  DateTime             @default(now())
  updated_at  DateTime             @updatedAt
  deleted_at  DateTime?

  resident_id String
  title       String
  description String               @db.Text
  category    RequestCategory
  status      ServiceRequestStatus @default(SUBMITTED)
  ward        String

  @@index([resident_id])
  @@index([status])
  @@index([ward])
  @@index([category])
}

enum RequestCategory  { WATER ELECTRICITY ROADS SANITATION SAFETY OTHER }
enum ServiceRequestStatus { SUBMITTED IN_REVIEW IN_PROGRESS RESOLVED CLOSED }

// ─── SYNCUP CREATOR PLATFORM ──────────────────────────────────────────────────

model Pitch {
  id           String       @id @default(cuid())
  created_at   DateTime     @default(now())
  updated_at   DateTime     @updatedAt
  deleted_at   DateTime?

  sender_id    String
  recipient_id String
  title        String
  summary      String       @db.Text
  status       PitchStatus  @default(PENDING)

  messages     NegotiationMessage[]

  @@index([sender_id])
  @@index([recipient_id])
  @@index([status])
}

enum PitchStatus { PENDING NEGOTIATING ACCEPTED DECLINED EXPIRED }

model NegotiationMessage {
  id         String   @id @default(cuid())
  created_at DateTime @default(now())
  updated_at DateTime @updatedAt
  deleted_at DateTime?

  pitch_id   String
  author_id  String
  content    String   @db.Text
  sequence   Int      // 1–10 enforced by service layer + DB check

  pitch      Pitch    @relation(fields: [pitch_id], references: [id])

  @@index([pitch_id])
  @@index([author_id])
  @@index([sequence])
}
```

---

## P5.3 — Prisma Soft Delete Middleware (S5.12)

```typescript
// src/lib/prisma.ts — add after client instantiation

const SOFT_DELETE_MODELS = [
  "User", "Student", "Scholarship", "Application",
  "Account", "SavingsGoal", "Transaction",
  "ServiceRequest", "Pitch", "NegotiationMessage",
] as const

// S5.12 — Auto-append deleted_at: null to all queries on soft-delete models
prisma.$use(async (params, next) => {
  if (!SOFT_DELETE_MODELS.includes(params.model as any)) return next(params)

  const writeActions = ["delete", "deleteMany"]
  const readActions  = ["findUnique", "findFirst", "findMany", "findRaw", "aggregate", "groupBy", "count"]

  if (writeActions.includes(params.action)) {
    // Convert hard delete to soft delete
    params.action = params.action === "delete" ? "update" : "updateMany"
    params.args.data = { deleted_at: new Date() }
  }

  if (readActions.includes(params.action)) {
    params.args ??= {}
    params.args.where ??= {}
    // Append soft delete filter (unless explicitly querying deleted records)
    if (!params.args.where.deleted_at) {
      params.args.where.deleted_at = null
    }
  }

  return next(params)
})
```

---

## P5.4 — Explicit Select Pattern (S5.11)

```typescript
// ✅ Correct — explicit select, filtered (S5.11, S5.12)
const user = await prisma.user.findUnique({
  where: { id: userId },          // deleted_at: null appended by middleware (S5.12)
  select: {
    id:             true,
    email:          true,
    name:           true,
    role:           true,
    email_verified: true,
    image:          true,
    // Never include: password_hash, deleted_at, internal tokens
  },
})

// ✅ Correct — list with pagination (S5.14)
const scholarships = await prisma.scholarship.findMany({
  where:  { status: "ACTIVE" },   // deleted_at: null auto-appended
  select: { id: true, title: true, amount: true, status: true },
  orderBy: { created_at: "desc" },
  take:   20,   // S5.14 — always paginate
  skip:   page * 20,
})

// ❌ Wrong — never do this
// const users = await prisma.user.findMany()  // returns ALL fields, ALL records including deleted
```

---

## P5.5 — Pagination — Cursor-Based and Offset (S5.14, S2.39)

### Cursor-based pagination (preferred for infinite scroll)

```typescript
// src/lib/db/scholarship-queries.ts
import { prisma } from "@/lib/prisma"
import { Prisma } from "@prisma/client"

const PAGE_SIZE = 20

export async function getScholarshipsPage(cursor?: string) {
  const scholarships = await prisma.scholarship.findMany({
    where:  { status: "ACTIVE" }, // S5.12 — deleted_at: null auto-appended
    select: { id: true, title: true, amount: true, status: true, created_at: true },
    orderBy: { created_at: "desc" },
    take:   PAGE_SIZE + 1,                // fetch one extra to detect next page
    ...(cursor && {
      cursor:  { id: cursor },
      skip:    1,                         // skip the cursor item itself
    }),
  })

  const hasMore  = scholarships.length > PAGE_SIZE
  const items    = hasMore ? scholarships.slice(0, PAGE_SIZE) : scholarships
  const nextCursor = hasMore ? items[items.length - 1].id : undefined

  return { items, nextCursor, hasMore }
}
```

### Offset pagination (for paginated tables with page numbers)

```typescript
export async function getApplicationsPage(studentId: string, page: number) {
  const take = 20
  const skip = page * take

  const [items, total] = await prisma.$transaction([
    prisma.application.findMany({
      where:   { student_id: studentId }, // S5.12 auto-filters deleted
      select:  { id: true, status: true, reference: true, created_at: true },
      orderBy: { created_at: "desc" },
      take,
      skip,
    }),
    prisma.application.count({ where: { student_id: studentId } }),
  ])

  return {
    items,
    total,
    page,
    pageCount:  Math.ceil(total / take),
    hasNext:    skip + take < total,
    hasPrev:    page > 0,
  }
}
```

---

## P5.6 — Transaction Pattern — Multi-Step Writes (S5.15)

```typescript
// Reserve Bank: deposit + balance update + audit log — all-or-nothing (S5.15, S5.3)
export async function processDeposit(
  accountId: string,
  userId: string,
  amount: Decimal,
  note?: string,
): Promise<{ transaction: Transaction; newBalance: Decimal }> {

  const result = await prisma.$transaction(async (tx) => {
    // 1. Lock the account row (prevent race conditions on balance)
    const account = await tx.$queryRaw<Array<{ balance: string }>>(
      Prisma.sql`SELECT balance FROM "Account" WHERE id = ${accountId} FOR UPDATE`
    )
    if (!account[0]) throw new Error("Account not found")

    const currentBalance = new Decimal(account[0].balance)
    const newBalance     = currentBalance.plus(amount)

    // 2. Create transaction record
    const transaction = await tx.transaction.create({
      data: { account_id: accountId, amount, type: "DEPOSIT", note },
    })

    // 3. Update balance atomically
    await tx.account.update({
      where: { id: accountId },
      data:  { balance: newBalance },
    })

    // 4. Audit log
    await tx.auditLog.create({
      data: {
        user_id:   userId,
        event:     "deposit_processed",
        metadata:  { account_id: accountId, amount: amount.toString(), new_balance: newBalance.toString() },
      },
    })

    return { transaction, newBalance }
  })

  return result
}
```

---

## P5.7 — Raw SQL — Governed Patterns (S5.19, S5.20, S5.21, S5.22, S5.23, S5.24)

### TypeScript — Prisma tagged template (S5.21 — parameterised via Prisma.sql)

```typescript
// src/lib/db/analytics-queries.ts
// S5.24 — Raw SQL isolated in dedicated service function
import { Prisma, prisma } from "@/lib/prisma"

// S5.23 — Typed result interface
interface ScholarshipMatchResult {
  scholarship_id:   string
  title:            string
  amount:           string   // Decimal serialised as string
  eligibility_score: number
  rank:             number
}

/**
 * Raw SQL used because: window function ROW_NUMBER() OVER(ORDER BY score DESC)
 * cannot be expressed cleanly in Prisma's query builder without raw SQL.
 * Prisma.sql tagged template handles parameterisation automatically (S5.21).
 */
export async function getRankedScholarshipsForStudent(
  studentGpa: number,
  institutionDomain: string,
  limit = 10,
): Promise<ScholarshipMatchResult[]> {
  // S5.21 — Prisma.sql template literal prevents SQL injection
  // S5.22 — deleted_at IS NULL included explicitly (middleware doesn't apply to $queryRaw)
  return prisma.$queryRaw<ScholarshipMatchResult[]>(Prisma.sql`
    SELECT
      s.id                                                  AS scholarship_id,
      s.title,
      s.amount::text,
      ROUND(
        (CASE WHEN ${studentGpa}::numeric >= s.min_gpa THEN 0.6 ELSE 0.0 END)
        + (CASE WHEN s.institution_domain = ${institutionDomain} THEN 0.4 ELSE 0.0 END),
        4
      )                                                     AS eligibility_score,
      ROW_NUMBER() OVER (ORDER BY
        (CASE WHEN ${studentGpa}::numeric >= s.min_gpa THEN 0.6 ELSE 0.0 END) +
        (CASE WHEN s.institution_domain = ${institutionDomain} THEN 0.4 ELSE 0.0 END)
        DESC
      )                                                     AS rank
    FROM "Scholarship" s
    WHERE s.deleted_at IS NULL          -- S5.22 — raw SQL must filter soft-deletes explicitly
      AND s.status = 'ACTIVE'
    ORDER BY eligibility_score DESC
    LIMIT ${limit}
  `)
}
```

### Python FastAPI — SQLAlchemy text() (S5.21 — bound parameters)

```python
# app/db/queries/balance_analytics.py
# S5.24 — Raw SQL isolated in dedicated module
from decimal import Decimal
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional


async def get_account_balance_summary(
    user_id: str,
    db: AsyncSession,
) -> Optional[dict]:
    """
    Raw SQL used because: conditional SUM aggregates with FILTER clause
    are cleaner and more performant as SQL than as ORM with Python post-processing.
    S5.21 — all user inputs are bound parameters, never f-string formatted.
    S5.22 — deleted_at IS NULL included on all tables.
    """
    result = await db.execute(
        text("""
            SELECT
                a.id,
                a.balance::text                                       AS balance,
                COALESCE(
                    SUM(t.amount) FILTER (WHERE t.type = 'DEPOSIT'),
                    0
                )::text                                               AS total_deposits,
                COALESCE(
                    SUM(t.amount) FILTER (WHERE t.type = 'WITHDRAWAL'),
                    0
                )::text                                               AS total_withdrawals,
                COUNT(t.id) FILTER (WHERE t.type = 'DEPOSIT')        AS deposit_count
            FROM accounts a
            LEFT JOIN transactions t
                   ON t.account_id = a.id
                  AND t.deleted_at IS NULL    -- S5.22 — explicit soft-delete filter
            WHERE a.user_id   = :user_id     -- S5.21 — bound parameter
              AND a.deleted_at IS NULL        -- S5.22
            GROUP BY a.id, a.balance
        """),
        {"user_id": user_id},               # S5.21 — bound, never f-string
    )

    row = result.mappings().one_or_none()
    if not row:
        return None

    # S5.23 — validate result types
    return {
        "id":               row["id"],
        "balance":          Decimal(row["balance"]),      # S5.28 — Decimal
        "total_deposits":   Decimal(row["total_deposits"]),
        "total_withdrawals": Decimal(row["total_withdrawals"]),
        "deposit_count":    int(row["deposit_count"]),
    }


async def get_interest_projection(
    account_id: str,
    annual_rate: Decimal,
    months: int,
    db: AsyncSession,
) -> dict:
    """
    Compound interest calculation done in PostgreSQL for decimal precision.
    Raw SQL because: PostgreSQL's POWER() with Decimal types avoids Python
    float precision issues entirely. S5.21 — all parameters are bound.
    """
    result = await db.execute(
        text("""
            SELECT
                balance::text                                                 AS principal,
                (balance * POWER(1 + :monthly_rate, :months) - balance)::text AS interest,
                (balance * POWER(1 + :monthly_rate, :months))::text           AS projected_balance
            FROM accounts
            WHERE id         = :account_id   -- S5.21 — bound parameter
              AND deleted_at IS NULL          -- S5.22
        """),
        {
            "account_id":    account_id,
            "monthly_rate":  float(annual_rate / 12),  # PostgreSQL needs float for POWER()
            "months":        months,
        },
    )

    row = result.mappings().one()
    return {
        "principal":          Decimal(row["principal"]),
        "interest":           Decimal(row["interest"]),
        "projected_balance":  Decimal(row["projected_balance"]),
    }
```

---

## P5.8 — Beanie MongoDB Setup and Patterns (S5.18, S5.33–S5.44)

### Installation

```bash
pip install beanie motor
```

### Document models

```python
# app/db/mongodb/models.py
from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime
from typing import Optional, ClassVar
from pymongo import IndexModel, ASCENDING


class ScholarshipContent(Document):
    """
    AI-generated scholarship reasoning content.
    References PostgreSQL via pg_id (S5.5, S5.38).
    S5.34 — timestamps and soft delete mirror PostgreSQL pattern.
    """
    # S5.5 — PostgreSQL cuid reference, never ObjectId
    pg_id:       Indexed(str)         # type: ignore[valid-type]
    title:       str
    ai_reasoning: str
    tags:        list[str] = Field(default_factory=list)
    source_url:  Optional[str] = None

    # S5.34 — required fields matching PostgreSQL pattern
    created_at:  datetime = Field(default_factory=datetime.utcnow)
    updated_at:  datetime = Field(default_factory=datetime.utcnow)
    deleted_at:  Optional[datetime] = None  # S5.8 — soft delete

    class Settings:
        name    = "scholarship_contents"   # S5.36 — snake_case plural
        indexes = [                        # S5.37 — indexes in model
            IndexModel([("pg_id",    ASCENDING)], unique=True),
            IndexModel([("tags",     ASCENDING)]),
            IndexModel([("deleted_at", ASCENDING)]),
        ]


class ApplicationLog(Document):
    """Application processing events for audit and analytics."""
    pg_application_id: Indexed(str)  # type: ignore[valid-type]  # S5.5
    event:    str
    actor_id: Optional[str] = None
    metadata: dict = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None

    class Settings:
        name    = "application_logs"
        indexes = [
            IndexModel([("pg_application_id", ASCENDING)]),
            IndexModel([("event",             ASCENDING)]),
            IndexModel([("created_at",        ASCENDING)]),
        ]
```

### Initialisation

```python
# app/db/mongodb/client.py
import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.db.mongodb.models import ScholarshipContent, ApplicationLog


async def init_mongodb() -> None:
    client = AsyncIOMotorClient(os.environ["MONGODB_URL"])
    await init_beanie(
        database=client.get_database(),
        document_models=[ScholarshipContent, ApplicationLog],
    )
```

### Queries with soft delete filter (S5.35)

```python
# app/db/mongodb/scholarship_content_repo.py
from typing import Optional
from app.db.mongodb.models import ScholarshipContent


async def get_content_by_pg_id(pg_id: str) -> Optional[ScholarshipContent]:
    # S5.35 — always filter deleted_at: None explicitly (no middleware in Beanie)
    return await ScholarshipContent.find_one(
        ScholarshipContent.pg_id == pg_id,
        ScholarshipContent.deleted_at == None,  # noqa: E711
    )


async def get_contents_by_tags(tags: list[str]) -> list[ScholarshipContent]:
    # S5.35 — soft delete filter on every query
    return await ScholarshipContent.find(
        {"tags": {"$in": tags}, "deleted_at": None}
    ).to_list()


async def soft_delete_content(pg_id: str) -> bool:
    # S5.8 — soft delete, never hard delete
    from datetime import datetime
    result = await ScholarshipContent.find_one(
        ScholarshipContent.pg_id == pg_id,
        ScholarshipContent.deleted_at == None,  # noqa: E711
    )
    if not result:
        return False
    result.deleted_at = datetime.utcnow()
    await result.save()
    return True
```

---

## P5.9 — ChromaDB Client — FundsLink AI Pipeline (S5.45–S5.52)

### Installation

```bash
pip install chromadb openai langchain langchain-openai
```

### ChromaDB client (S5.50 — internal Railway URL only)

```python
# app/db/chromadb/client.py
import os
import chromadb
from functools import lru_cache


@lru_cache(maxsize=1)
def get_chroma_client() -> chromadb.HttpClient:
    # S5.50 — internal Railway URL, never public internet
    return chromadb.HttpClient(
        host=os.environ["CHROMADB_HOST"],  # Railway internal hostname
        port=int(os.environ.get("CHROMADB_PORT", "8000")),
    )


def get_scholarship_collection(version: str = "v1") -> chromadb.Collection:
    # S5.49 — versioned collection name
    return get_chroma_client().get_or_create_collection(
        name=f"scholarship_embeddings_{version}",
        metadata={"hnsw:space": "cosine"},
    )
```

### Embedding pipeline

```python
# app/db/chromadb/scholarship_embedder.py
import os
from typing import Optional
from langchain_openai import OpenAIEmbeddings
from app.db.chromadb.client import get_scholarship_collection

embeddings_model = OpenAIEmbeddings(
    model="text-embedding-3-small",
    api_key=os.environ["OPENAI_API_KEY"],
)


async def embed_scholarship(
    pg_scholarship_id: str,   # S5.5 — PostgreSQL cuid as reference
    title: str,
    description: str,
    tags: list[str],
) -> None:
    collection = get_scholarship_collection()

    document_text = f"{title}\n{description}\nTags: {', '.join(tags)}"
    embedding     = await embeddings_model.aembed_query(document_text)

    collection.upsert(
        ids=[pg_scholarship_id],   # S5.5 — cuid as ChromaDB document ID
        embeddings=[embedding],
        documents=[document_text],
        metadatas=[{               # S5.45 — only reference IDs in metadata, no duplicated structured data
            "pg_id": pg_scholarship_id,
            "title": title,        # minimal metadata for display only
        }],
    )


async def find_matching_scholarships(
    student_profile: str,
    limit: int = 10,
    min_similarity: float = 0.7,  # S5.48 — minimum 0.7 threshold
) -> list[dict]:
    collection = get_scholarship_collection()

    query_embedding = await embeddings_model.aembed_query(student_profile)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(limit, 50),  # S5.52 — bounded result set
    )

    # S5.48 — filter by minimum similarity threshold
    matched = []
    for i, distance in enumerate(results["distances"][0]):
        similarity = 1 - distance  # cosine distance → similarity
        if similarity >= min_similarity:
            matched.append({
                "pg_id":      results["metadatas"][0][i]["pg_id"],
                "similarity": round(similarity, 4),
            })

    return matched
```

---

## P5.10 — Cross-Database Sync Pattern (S5.53–S5.55)

```python
# app/services/scholarship_service.py
# Cross-database write: PostgreSQL + MongoDB + ChromaDB
# S5.53 — integration tests verify both success and failure paths

from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.mongodb.scholarship_content_repo import ScholarshipContent
from app.db.chromadb.scholarship_embedder import embed_scholarship
from app.db.prisma import prisma


async def create_scholarship_with_ai_content(
    title: str,
    description: str,
    amount: Decimal,
    min_gpa: Decimal,
    ai_reasoning: str,
    tags: list[str],
    funder_id: str,
) -> dict:
    """
    Creates a scholarship across three databases in the correct order.
    PostgreSQL is created first (system of record — S5.2).
    MongoDB and ChromaDB receive the PostgreSQL ID as their reference (S5.5).
    Failures after PostgreSQL commit are logged for reconciliation (S5.55).
    """
    # Step 1 — PostgreSQL (system of record, S5.2)
    scholarship = await prisma.scholarship.create({
        "data": {
            "title":       title,
            "description": description,
            "amount":      amount,
            "min_gpa":     min_gpa,
            "funder_id":   funder_id,
            "status":      "ACTIVE",
        }
    })
    pg_id = scholarship.id  # cuid from PostgreSQL

    # Step 2 — MongoDB (AI-generated content, S5.33)
    try:
        mongo_doc = ScholarshipContent(
            pg_id=pg_id,    # S5.5 — PostgreSQL cuid reference
            title=title,
            ai_reasoning=ai_reasoning,
            tags=tags,
        )
        await mongo_doc.insert()
    except Exception as e:
        # S5.53 — log failure for reconciliation (S5.58)
        await prisma.auditLog.create({
            "data": {
                "event":    "cross_db_sync_failure",
                "metadata": {"step": "mongodb", "pg_id": pg_id, "error": str(e)},
            }
        })
        raise RuntimeError(f"MongoDB sync failed for scholarship {pg_id}: {e}")

    # Step 3 — ChromaDB (vector embeddings, S5.45)
    try:
        await embed_scholarship(
            pg_scholarship_id=pg_id,
            title=title,
            description=description,
            tags=tags,
        )
    except Exception as e:
        # S5.53 — log failure; ChromaDB can be re-synced without data loss
        await prisma.auditLog.create({
            "data": {
                "event":    "cross_db_sync_failure",
                "metadata": {"step": "chromadb", "pg_id": pg_id, "error": str(e)},
            }
        })
        # ChromaDB failure is non-fatal — scholarship is still usable without AI matching
        # S5.57 — background reconciliation job will re-embed

    return {"id": pg_id, "title": title, "amount": str(amount)}
```

---

## P5.11 — Migration Workflow (S5.59–S5.64)

### Development cycle

```bash
# 1. Edit schema.prisma — add/modify models

# 2. Generate and apply migration
npx prisma migrate dev --name describe_what_changed
# e.g.: npx prisma migrate dev --name add_savings_goal_model

# 3. Verify migration was applied
npx prisma migrate status

# 4. Regenerate Prisma client
npx prisma generate
```

### Production deployment (S5.59 — migrations BEFORE service start)

```bash
# In Railway deploy command (not start command):
npx prisma migrate deploy && node dist/server.js

# Or in GitHub Actions deploy-production.yml:
# - name: Run migrations
#   run: npx prisma migrate deploy
# - name: Start service  (only runs if migration succeeded)
#   if: success()
#   run: railway up
```

### Two-phase column removal (S5.61)

```bash
# Phase 1 — Remove from code, keep in schema (sprint N)
# In service layer: stop reading/writing the column
# In schema.prisma: add @deprecated annotation comment but keep the column
npx prisma migrate dev --name deprecate_old_field_from_code
# Deploy Phase 1. Let it run for one full sprint.

# Phase 2 — Remove from schema (sprint N+1, after Phase 1 is stable)
# In schema.prisma: remove the field entirely
npx prisma migrate dev --name remove_old_field_column
npx prisma migrate deploy  # Deploy to production
```

### Migration rollback

```bash
# Mark failed migration as rolled back
npx prisma migrate resolve --rolled-back 20260508120000_migration_name

# Verify
npx prisma migrate status

# Redeploy previous service version
railway redeploy  # previous Railway build
```

---

## P5.12 — Prisma Schema Linter CI Configuration (S5.10, S5.13)

### Install

```bash
npm install --save-dev @mmkal/prisma-lint
```

### `.prisma-lint.json`

```json
{
  "rules": {
    "require-field": {
      "models": "*",
      "fields": [
        { "name": "id",         "type": "String", "attributes": ["@id", "@default(cuid())"] },
        { "name": "created_at", "type": "DateTime", "attributes": ["@default(now())"] },
        { "name": "updated_at", "type": "DateTime", "attributes": ["@updatedAt"] },
        { "name": "deleted_at", "type": "DateTime?" }
      ]
    },
    "no-implicit-foreign-key": {
      "description": "Every FK field must have an explicit @@index or @index"
    },
    "field-order": {
      "order": ["id", "created_at", "updated_at", "deleted_at", "*"]
    }
  }
}
```

### `ci.yml` — schema validation step

```yaml
- name: Validate Prisma schema
  run: |
    npx prisma validate
    npx prisma-lint

- name: Check for missing migrations
  if: contains(github.event.head_commit.modified, 'prisma/schema.prisma')
  run: npx prisma migrate diff --from-schema-datamodel prisma/schema.prisma --to-schema-datasource
```

---

## P5.13 — Tools & Commands Reference

| Task | Command |
|------|---------|
| Create migration | `npx prisma migrate dev --name {description}` |
| Deploy migration (staging/prod) | `npx prisma migrate deploy` |
| Check migration status | `npx prisma migrate status` |
| Validate schema | `npx prisma validate` |
| Lint schema | `npx prisma-lint` |
| Generate Prisma client | `npx prisma generate` |
| Open Prisma Studio | `npx prisma studio` |
| Schema diff (detect drift) | `npx prisma migrate diff --from-schema-datamodel prisma/schema.prisma --to-schema-datasource` |
| Seed database | `npx prisma db seed` |
| Reset test DB (test only) | `npx prisma migrate reset --force` — **never in production** |
| Rollback failed migration | `npx prisma migrate resolve --rolled-back {migration_name}` |
| MongoDB connection test | `python -c "from motor.motor_asyncio import AsyncIOMotorClient; import asyncio; asyncio.run(AsyncIOMotorClient(MONGO_URL).admin.command('ping'))"` |
| ChromaDB heartbeat | `curl http://chromadb-internal:8000/api/v1/heartbeat` |
| Check embedding count | `python -c "from app.db.chromadb.client import get_scholarship_collection; print(get_scholarship_collection().count())"` |

---

## Common Failure Patterns

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `deleted_at` records appearing in queries | Raw SQL without `AND deleted_at IS NULL` | Add explicit filter per S5.22 |
| `PrismaClient` connection pool exhausted | New instance per request | Use singleton (S5.16) |
| Balance calculation off by floating point | `Float` column instead of `Decimal` | Migrate to `Decimal @db.Decimal(19,4)` (S5.28) |
| MongoDB document references broken | ObjectId used instead of PostgreSQL cuid | Update reference field to store `pg_id: str` (S5.5) |
| ChromaDB results below threshold included | No `min_similarity` filter | Add `if similarity >= 0.7` filter (S5.48) |
| Schema drift in production | Migration skipped before deploy | Enforce `prisma migrate deploy` in deploy pipeline before service start (S5.59) |
| Beanie query returns deleted docs | Missing `deleted_at == None` filter | Add explicitly on every Beanie query (S5.35) |
| f-string SQL in Python | Developer unfamiliarity | Use `text(query)` with `{"param": value}` dict always (S5.21) |

---

## Amendment Log

| Version | Date | Change | Reason |
|---------|------|--------|--------|
| v1.0 | 2026-05-08 | Initial lock — full depth implementation guide. Complete Prisma schema for all 4 systems (P5.2). Soft delete middleware (P5.3). Cursor-based and offset pagination (P5.5). Reserve Bank financial transaction pattern with Decimal (P5.6). Full raw SQL patterns for both TypeScript and Python with parameterisation examples (P5.7). Beanie MongoDB setup with soft-delete queries (P5.8). ChromaDB embedding pipeline (P5.9). Cross-database sync pattern (P5.10). Two-phase column removal migration pattern (P5.11). | Expanded from thin initial version to full production-ready guide. |

---

> **LOCKED — v1.0 — 2026-05-08**
>
> This document is locked. No practice may be added, removed, or modified
> without following the Amendment Protocol defined in C0 §8.
> Any practice change that would cause a constitutional standard to be violated
> requires a constitutional amendment to C5 first, then an update here.
