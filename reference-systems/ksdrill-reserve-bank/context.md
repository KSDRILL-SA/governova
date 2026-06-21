# KSDRILL Reserve Bank — System Context

---

| Attribute          | Value |
|--------------------|-------|
| **System**         | KSDRILL Reserve Bank |
| **Stack**          | Angular + FastAPI |
| **Build Phase**    | Phase 0 — Design (Q4 2026 — pending Maphophe MVP) |
| **Current Group**  | — (not yet started) |
| **Operating Mode** | SOLO |
| **Active Overlay** | `overlays/solo-dev-overlay.md` |
| **ADR**            | `adrs/ADR-003-reserve-bank-stack.md` |
| **Lock Date**      | 2026-05-08 |

---

## Problem Statement

Most savings tools are passive — they track savings but do not enforce discipline. South Africans have one of the lowest savings rates in the world because no tool makes saving structured and non-negotiable.

## Primary Workflow

User creates account → sets savings goal → makes first deposit → sees balance and projected interest

## v1 Done When

A user can create an account, make a deposit, and see their balance and interest calculation in production.

---

## Build Pre-condition

Reserve Bank build begins only after Maphophe MVP has been live in production for at least 2 weeks with no SEV0/SEV1 incidents. (S9.16)

---

## Active Constitutions

All 11 constitutions apply. Stack-specific scope:
- C3: Angular+FastAPI auth path (S3.13–S3.20)
- C4: Angular standards (S4.52–S4.60)
- C5: PostgreSQL + MongoDB + Redis (no ChromaDB)
- C6: Angular+FastAPI topology (S6.13), deploy order (S6.29)
- C8: Railway for FastAPI (S8.2)

---

## v1 Feature Set

| # | Feature | Group | Status |
|---|---------|-------|--------|
| 1 | Authentication | G1 | — |
| 2 | Account creation and management | G1 | — |
| 3 | Deposit submission and tracking | G1 | — |
| 4 | Savings goals | G1 | — |
| 5 | Interest view (calculated, not accrued in v1) | G2 | — |

**Total: 5 features** — within v1 limit.

---

## Financial Integrity Requirements (CRITICAL)

| Requirement | Standard |
|-------------|----------|
| All financial data in PostgreSQL — never MongoDB | S5.3 |
| Decimal columns for all monetary values | S5.28 |
| Python Decimal arithmetic in FastAPI — never JavaScript float | S6.3 |
| Transactions for all multi-step writes | S5.15 |
| Financial incidents are automatic SEV0 | S8.50 |
| Financial freeze runbook ready | `runbooks/financial-freeze-runbook.md` |
| 100% branch coverage on financial calculation code | S7.29 |
| Financial test values use Decimal, never float | S7.38 |

---

## Database Assignment

| Data Type | Database | Standard |
|-----------|----------|----------|
| Users, auth, accounts, balances, transactions, goals | PostgreSQL | S5.3, S5.4 |
| Application logs, deposit history summaries | MongoDB | S5.33 |
| BullMQ job queues (deposit schedule jobs) | Redis | — |

---

*Last updated: 2026-05-08*
