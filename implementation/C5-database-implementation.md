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

## P5.1 — Prisma Setup and Singleton Client (S5.9, S5.16)

### Installation

```bash
npm install prisma @prisma/client
npx prisma init
```

### Singleton Client (`src/lib/prisma.ts`) — S5.16

```typescript
import { PrismaClient } from "@prisma/client"

const globalForPrisma = globalThis as unknown as { prisma: PrismaClient }

export const prisma =
  globalForPrisma.prisma ??
  new PrismaClient({
    log: process.env.NODE_ENV === "development" ? ["query", "error"] : ["error"],
  })

if (process.env.NODE_ENV !== "production") globalForPrisma.prisma = prisma
```

### Soft Delete Middleware (S5.12)

```typescript
// Automatically appends deleted_at: null to all queries
prisma.$use(async (params, next) => {
  const softDeleteModels = ["User", "Student", "Application", "Scholarship", "Account"]
  
  if (softDeleteModels.includes(params.model ?? "")) {
    if (params.action === "findUnique" || params.action === "findFirst") {
      params.action = "findFirst"
      params.args.where = { ...params.args.where, deleted_at: null }
    }
    if (params.action === "findMany") {
      params.args.where = { ...params.args.where, deleted_at: null }
    }
  }
  return next(params)
})
```

---

## P5.2 — Required Table Pattern (S5.10)

```prisma
// Every model follows this pattern exactly
model Scholarship {
  id         String    @id @default(cuid())
  created_at DateTime  @default(now())
  updated_at DateTime  @updatedAt
  deleted_at DateTime?

  // Domain fields below
  title      String
  amount     Decimal   @db.Decimal(19, 4)  // S5.28 — Decimal, never Float
  status     ScholarshipStatus @default(ACTIVE)

  // Foreign keys with explicit indexes (S5.13)
  funder_id  String
  funder     Funder  @relation(fields: [funder_id], references: [id])

  @@index([funder_id])
  @@index([status])  // S5.25 — index query-critical fields
}

enum ScholarshipStatus {
  ACTIVE
  PAUSED
  CLOSED
}
```

---

## P5.3 — Explicit Select Pattern (S5.11)

```typescript
// ✅ Correct — explicit select
const user = await prisma.user.findUnique({
  where: { id: userId, deleted_at: null },  // S5.12
  select: {
    id: true,
    email: true,
    name: true,
    role: true,
    // Never: password_hash, reset_token, deleted_at
  },
})

// ❌ Wrong — no select (returns all fields including secrets)
// const user = await prisma.user.findUnique({ where: { id: userId } })
```

---

## P5.4 — Transaction Pattern (S5.15)

```typescript
// Multi-step write using prisma.$transaction
async function submitApplication(studentId: string, scholarshipId: string) {
  return prisma.$transaction([
    prisma.application.create({
      data: { student_id: studentId, scholarship_id: scholarshipId },
    }),
    prisma.student.update({
      where: { id: studentId },
      data: { application_count: { increment: 1 } },
    }),
    prisma.auditLog.create({
      data: {
        user_id: studentId,
        event: "application_submitted",
        metadata: { scholarship_id: scholarshipId },
      },
    }),
  ])
}
```

---

## P5.5 — Raw SQL for Complex Queries (S5.19, S5.21, S5.22)

```typescript
// S5.19 — Raw SQL for window function (ORM cannot express this cleanly)
// S5.21 — Parameterised via Prisma.sql tagged template
// S5.22 — Includes deleted_at IS NULL
// S5.24 — Isolated in dedicated service function

import { Prisma } from "@prisma/client"

// Result type for raw SQL output (S5.23)
interface ScholarshipRanking {
  id: string
  title: string
  amount: string
  rank: number
}

export async function getScholarshipRankingsByAmount(funderId: string): Promise<ScholarshipRanking[]> {
  // Comment explains why ORM is insufficient: ROW_NUMBER() window function
  // cannot be expressed cleanly in Prisma's query builder without raw SQL
  return prisma.$queryRaw<ScholarshipRanking[]>(Prisma.sql`
    SELECT
      id,
      title,
      amount::text,
      ROW_NUMBER() OVER (
        PARTITION BY funder_id
        ORDER BY amount DESC
      ) AS rank
    FROM "Scholarship"
    WHERE funder_id = ${funderId}  -- Parameterised (S5.21)
      AND deleted_at IS NULL       -- Soft delete filter (S5.22)
    ORDER BY rank
  `)
}
```

### Python Raw SQL (FastAPI) — S5.21

```python
from sqlalchemy import text
from decimal import Decimal

# S5.19 — Raw SQL for complex aggregate (SUM with conditional)
# S5.21 — Parameterised with bound parameters (never f-string)
# S5.22 — Includes deleted_at IS NULL
async def get_account_balance_summary(user_id: str, db) -> dict:
    """
    Raw SQL used because SQLAlchemy ORM cannot express the conditional
    SUM aggregate as cleanly as this SQL without multiple round-trips.
    """
    result = await db.execute(
        text("""
            SELECT
              a.id,
              a.balance,
              COALESCE(SUM(CASE WHEN t.type = 'DEPOSIT' THEN t.amount ELSE 0 END), 0) AS total_deposits,
              COALESCE(SUM(CASE WHEN t.type = 'WITHDRAWAL' THEN t.amount ELSE 0 END), 0) AS total_withdrawals
            FROM accounts a
            LEFT JOIN transactions t ON t.account_id = a.id AND t.deleted_at IS NULL
            WHERE a.user_id = :user_id  -- Bound parameter (S5.21)
              AND a.deleted_at IS NULL   -- Soft delete filter (S5.22)
            GROUP BY a.id, a.balance
        """),
        {"user_id": user_id}  # Bound parameters prevent SQL injection
    )
    row = result.mappings().one()
    return {
        "id": row["id"],
        "balance": Decimal(row["balance"]),  # S5.28 — Decimal
        "total_deposits": Decimal(row["total_deposits"]),
        "total_withdrawals": Decimal(row["total_withdrawals"]),
    }
```

---

## P5.6 — Beanie MongoDB Setup (S5.18) — Angular Stack

```python
from beanie import Document, init_beanie
from pydantic import Field
from datetime import datetime
from typing import Optional

class ScholarshipContent(Document):
    """
    AI-generated scholarship reasoning content.
    References PostgreSQL scholarship via pg_id (S5.5).
    """
    pg_id: str          # PostgreSQL cuid reference (S5.5)
    title: str
    ai_reasoning: str
    tags: list[str] = []
    
    # Required fields mirroring PostgreSQL pattern (S5.34)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = None  # Soft delete (S5.34)

    class Settings:
        name = "scholarship_contents"
        indexes = [
            "pg_id",  # S5.37 — indexes defined in Beanie model
        ]

# Startup initialization
async def init_mongodb():
    await init_beanie(
        database=motor_client.scholarship_db,
        document_models=[ScholarshipContent]
    )

# S5.35 — Always filter deleted_at: None
async def get_content_by_pg_id(pg_id: str) -> Optional[ScholarshipContent]:
    return await ScholarshipContent.find_one(
        ScholarshipContent.pg_id == pg_id,
        ScholarshipContent.deleted_at == None  # S5.35
    )
```

---

## P5.7 — Prisma Schema Linter Configuration (S5.10, S5.13)

Create `.prisma-lint.json`:

```json
{
  "rules": {
    "require-field": {
      "models": "*",
      "fields": ["id", "created_at", "updated_at", "deleted_at"]
    },
    "field-order": {
      "order": ["id", "created_at", "updated_at", "deleted_at"]
    },
    "require-index-for-foreign-key": true
  }
}
```

Add to CI (`ci.yml`):
```yaml
- name: Lint Prisma schema
  run: npx prisma-lint
```

---

## P5.8 — Tools & Commands Reference

| Task | Command |
|------|---------|
| Create migration | `npx prisma migrate dev --name {description}` |
| Deploy migration (prod) | `npx prisma migrate deploy` |
| Check migration status | `npx prisma migrate status` |
| Validate schema | `npx prisma validate` |
| Generate Prisma client | `npx prisma generate` |
| Open Prisma Studio | `npx prisma studio` |
| Diff schema vs DB | `npx prisma migrate diff --from-schema-datamodel prisma/schema.prisma --to-schema-datasource` |
| Seed database | `npx prisma db seed` |
| Reset test DB | `npx prisma migrate reset --force` (test only — never production) |

---

## Amendment Log

| Version | Date | Change | Reason |
|---------|------|--------|--------|
| v1.0 | 2026-05-08 | Initial lock | Raw SQL patterns (P5.5) added with parameterisation examples for both TypeScript and Python. Decimal column pattern (P5.2) documented. Beanie soft delete pattern (P5.6) aligned with S5.35. |

---

> **LOCKED — v1.0 — 2026-05-08**
