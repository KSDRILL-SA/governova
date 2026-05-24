# SyncUp Creator Platform — System Context

---

| Attribute          | Value |
|--------------------|-------|
| **System**         | SyncUp Creator Platform |
| **Stack**          | Next.js |
| **Build Phase**    | Phase 0 — Design (Q1 2027 — pending Reserve Bank MVP) |
| **Current Group**  | — (not yet started) |
| **Operating Mode** | SOLO |
| **Active Overlay** | `overlays/solo-dev-overlay.md` |
| **ADR**            | `adrs/ADR-004-syncup-stack.md` |
| **Lock Date**      | 2026-05-08 |

---

## Problem Statement

Creators waste enormous time in unstructured DM negotiations with no formal process, no clear outcome, and no record of what was agreed.

## Primary Workflow

Creator discovers another creator → sends structured pitch → negotiation completes within 10 messages → outcome recorded

## v1 Done When

A creator can send a pitch and receive a response through the structured negotiation flow in production.

---

## Build Pre-condition

SyncUp build begins only after KSDRILL Reserve Bank MVP has been live for at least 2 weeks with no SEV0/SEV1 incidents. (S9.16)

---

## Active Constitutions

All 11 constitutions apply. Stack-specific scope:
- C3: Next.js auth path (S3.5–S3.12)
- C4: Next.js standards (TanStack Query, Zustand, shadcn/ui)
- C5: PostgreSQL + Redis (no MongoDB, no ChromaDB)
- C6: Next.js topology (S6.12)
- C7: Jest + RTL + Playwright (S7.2)
- C8: Vercel deployment (S8.1)

---

## v1 Feature Set

| # | Feature | Group | Status |
|---|---------|-------|--------|
| 1 | Authentication (NextAuth, Google + GitHub OAuth) | G1 | — |
| 2 | Creator profiles | G1 | — |
| 3 | Structured pitch submission | G1 | — |
| 4 | 10-message negotiation engine | G1 | — |

**Total: 4 features** — within v1 limit.

---

## Special Architecture Notes

- **10-message negotiation limit** enforced at the database level (CHECK constraint) + service layer
- **Negotiation timer:** BullMQ + Redis job auto-closes negotiations after 48h of inactivity
- **Privacy controls:** Creator can set visibility of pitch outcomes

---

## Database Assignment

| Data Type | Database | Standard |
|-----------|----------|----------|
| Users, creators, pitches, negotiations, outcomes | PostgreSQL | S5.1 |
| BullMQ negotiation timer jobs | Redis | — |

---

*Last updated: 2026-05-08*
