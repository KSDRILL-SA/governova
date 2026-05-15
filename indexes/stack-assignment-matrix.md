# Stack Assignment Matrix — KSDRILL SA

> **Decision framework for assigning technology stacks to systems.**  
> Read against C6 Part 1 (S6.1–S6.7) and C0 §10.

---

## Assignment Decision Flow

```
Does the system require SEO or SSR for public content?
  YES → Next.js

Does the system require enterprise dashboards with complex forms?
  YES → Angular + FastAPI

Does the system require precision financial calculations?
  YES → Angular + FastAPI (Python Decimal — S6.3)

Does the system require a native Python AI pipeline (LangChain, RAG, ChromaDB)?
  YES → Angular + FastAPI (S6.4)

Is it a simple internal tool, admin panel, or basic CRUD system?
  EITHER stack — ADR required (S6.5)

Future/unrecognised system type?
  ADR required against this rubric (S6.6)

Default when all else equal:
  → Next.js
```

---

## Locked System Assignments

| System | Stack | ADR | Rationale Standards |
|--------|-------|-----|---------------------|
| **FundsLink Academy** | Angular + FastAPI | `adrs/ADR-001-fundslink-stack.md` | S6.2 (enterprise dashboards), S6.4 (LangChain/ChromaDB AI), S6.3 (funding calculations) |
| **Maphophe Community System** | Next.js | `adrs/ADR-002-maphophe-stack.md` | S6.1 (content-driven, SEO-critical, public-facing) |
| **KSDRILL Reserve Bank** | Angular + FastAPI | `adrs/ADR-003-reserve-bank-stack.md` | S6.2 (enterprise dashboards, complex RBAC), S6.3 (financial precision — Decimal) |
| **SyncUp Creator Platform** | Next.js | `adrs/ADR-004-syncup-stack.md` | S6.1 (content-driven, SEO-critical, creator-facing) |

> These assignments are immutable. Changing them requires a Major amendment to C6 and a new ADR. See CF-12.

---

## Technology Differences by Stack

| Concern | Next.js Stack | Angular + FastAPI Stack | Standard |
|---------|--------------|------------------------|---------|
| Frontend framework | Next.js App Router + React | Angular standalone | S4.1 |
| Backend | Next.js API Routes (built-in) | FastAPI (Python, Railway) | S6.12, S6.13 |
| Auth strategy | NextAuth.js — database sessions | RS256 JWT — FastAPI issues | S3.1, S3.5, S3.13 |
| Token storage | HttpOnly session cookie | Refresh: HttpOnly cookie; Access: Angular memory | S3.6, S3.14 |
| State management | TanStack Query + Zustand | Angular Signals + RxJS | S4.28, S4.30 |
| Forms | React Hook Form + Zod | Angular Reactive Forms | S4.46, S4.47 |
| DB (primary) | PostgreSQL via Prisma | PostgreSQL via Prisma | S5.9 |
| DB (document) | Not used | MongoDB via Beanie | S5.18 |
| DB (vector) | Not used | ChromaDB (FundsLink only) | S5.45 |
| Unit tests | Jest + RTL | Vitest + Angular utilities | S7.2 |
| Frontend deploy | Vercel | Vercel (separate project) | S8.1, S8.3 |
| Backend deploy | Vercel (built-in) | Railway | S8.1, S8.2 |

---

## Criteria Rubric for New Systems

When a new system is being evaluated, score it against these criteria:

| Criterion | Score → Next.js | Score → Angular+FastAPI |
|-----------|----------------|------------------------|
| SEO requirement (public pages, discoverability) | +3 | 0 |
| SSR/SSG required for performance/indexing | +3 | 0 |
| Enterprise multi-role dashboard with complex forms | 0 | +3 |
| Precision financial calculations required | 0 | +3 |
| Python AI (LangChain, PyTorch, embeddings) required | 0 | +3 |
| React ecosystem preference / existing Next.js team | +1 | 0 |
| Dedicated Python data team exists | 0 | +1 |

**Decision:** Higher score wins. Tie → default to Next.js. ADR documents the scoring.

---

*Last updated: v1.0 — 2026-05-08 | Governed by C6 S6.1–S6.7*
