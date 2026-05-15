# Maphophe Community System — System Context

---

| Attribute          | Value |
|--------------------|-------|
| **System**         | Maphophe Community System |
| **Stack**          | Next.js |
| **Build Phase**    | Phase 0 — Design (Q3 2026 — pending FundsLink MVP) |
| **Current Group**  | — (not yet started) |
| **Operating Mode** | SOLO |
| **Active Overlay** | `overlays/solo-dev-overlay.md` |
| **ADR**            | `adrs/ADR-002-maphophe-stack.md` |
| **Lock Date**      | 2026-05-08 |

---

## Problem Statement

Rural South African villages have no digital infrastructure — no traceable governance, no way to submit service requests, no way to hold ward administrators accountable for service delivery.

## Primary Workflow

Resident creates account → submits service request → ward admin reviews → resident sees status

## v1 Done When

A resident can submit a service request and see its progress through the ward admin process in production.

---

## Build Pre-condition

Maphophe build begins only after FundsLink Academy MVP has been live in production for at least 2 weeks with no SEV0/SEV1 incidents. (S9.16)

---

## Active Constitutions

All 11 constitutions apply. Stack-specific scope:
- C3: Next.js auth path (S3.5–S3.12)
- C4: Next.js standards (shadcn/ui, TanStack Query, Zustand)
- C5: PostgreSQL only (no MongoDB, no ChromaDB)
- C6: Next.js topology (S6.12)
- C7: Jest + RTL + Playwright (S7.2)
- C8: Vercel unified deployment (S8.1)

---

## v1 Feature Set

| # | Feature | Group | Status |
|---|---------|-------|--------|
| 1 | Authentication (registration, NextAuth sessions) | G1 | — |
| 2 | Public announcements (ward news, notices) | G2 | — |
| 3 | Service request submission | G1 | — |
| 4 | Request status tracking | G1 | — |

**Total: 4 features** — within v1 limit.

---

## Special Design Constraints (S9.5)

- **Low bandwidth first:** PWA, offline-ready, minimum data usage per page load
- **Feature phone accessibility:** 320px is not aspirational — it's the primary device
- **Lighthouse mobile score ≥ 85** (above the S4.69 minimum of 80)
- **Service worker** for offline announcement viewing

---

## Database Assignment

| Data Type | Database | Standard |
|-----------|----------|----------|
| All data | PostgreSQL only | S5.1 — no MongoDB, no ChromaDB for this system |

---

## Critical Standards for This System

| Standard | Why Critical for Maphophe |
|----------|--------------------------|
| `S3.5–S3.12` | Next.js NextAuth database sessions |
| `S4.2` | 320px mobile-first — rural users on entry-level phones |
| `S4.10` | Visual regression at 320px — non-negotiable |
| `S4.69` | Lighthouse ≥ 85 for low-bandwidth compliance |
| `S9.5` | African context: offline capability, low data usage |

---

*Last updated: 2026-05-08*
