# ADR-003 — KSDRILL Reserve Bank: Angular + FastAPI Stack Assignment

---

| Attribute      | Value |
|----------------|-------|
| **ID**         | ADR-003 |
| **Date**       | 2026-05-08 |
| **Status**     | accepted |
| **Supersedes** | — |
| **Relates To** | `S6.2` (Enterprise/Financial), `S6.3` (Financial Precision) |

---

## Context

KSDRILL Reserve Bank is a structured digital savings platform enforcing deposit schedules, savings goals, interest tracking, and lock periods. It is the highest-stakes system in the KSDRILL SA portfolio. The platform requires:

1. **Financial decimal precision — non-negotiable** — account balances, deposit amounts, interest rates, and goal progress calculations must use exact decimal arithmetic. JavaScript `number` floating-point produces incorrect results for financial operations. Python's `Decimal` type via FastAPI is the correct technical choice. This is a hard technical constraint, not a preference (`S6.3`).
2. **Enterprise-grade multi-role dashboard** — account holders, administrators, and auditors each have distinct dashboards with complex form workflows, transaction history views, and goal management interfaces. Angular Reactive Forms and OnPush change detection handle this complexity correctly.
3. **Complex RBAC** — multiple roles (`ACCOUNT_HOLDER`, `ADMIN`, `AUDITOR`) with fine-grained permission boundaries. FastAPI's `Depends()` injection provides the cleanest RBAC implementation.
4. **Scheduled background jobs** — deposit schedules, interest calculations, and maturity notifications run on BullMQ + Redis queues. Railway manages this infrastructure natively alongside the FastAPI service.
5. **Financial incident protocol** — any balance inconsistency is automatic SEV0 (`S8.50`). The `DEPOSITS_ENABLED` and `WITHDRAWALS_ENABLED` feature flags must be settable instantly without a deployment. Database-driven feature flags + FastAPI handles this.
6. **Not SEO-critical** — Reserve Bank is a private financial platform. Users access it via direct login. Search engine discoverability is not a requirement.

---

## Decision

**KSDRILL Reserve Bank is assigned to the Angular + FastAPI stack.**

The financial precision requirement (`S6.3`) alone mandates FastAPI Python. Angular handles the enterprise dashboard complexity. The combination provides the precision, RBAC depth, and operational control that a financial platform requires.

The decision is immutable for the v1 lifetime of KSDRILL Reserve Bank. This is the highest-stakes immutability in the system — a stack change here would invalidate all financial calculation logic and require a complete rewrite of the precision-critical service layer.

---

## Consequences

### What becomes easier
- Python `Decimal` arithmetic eliminates all floating-point financial calculation risk
- FastAPI `Depends()` provides clean, auditable RBAC for all financial endpoints
- Railway manages PostgreSQL, MongoDB, Redis, and the FastAPI service in one platform
- Angular Reactive Forms handle the complex goal-setting and deposit-scheduling forms
- Feature flag instant toggle (database-driven) for financial freeze protocol

### What becomes harder
- Two-deployment coordination (Vercel + Railway) per S6.29
- JWT auth complexity vs NextAuth session simplicity
- Financial incident response requires the most rigorous testing of any system (100% branch coverage on financial logic per S7.29)

### Constitutional alignment
- S6.2 — Enterprise dashboard criteria met: multi-role financial dashboards
- S6.3 — Financial precision criteria met: this is the definitional case for S6.3
- S8.50 — Financial incident protocol formalised: automatic SEV0 for any balance inconsistency
- S5.3 — All financial data in PostgreSQL — no exceptions, no MongoDB for financial records
- S5.28 — Decimal columns for all monetary values

---

## Alternatives Considered

| Option | Why Rejected |
|--------|-------------|
| Next.js | JavaScript `number` type cannot provide financial decimal precision. This is a disqualifying constraint. |
| Angular + Next.js API routes | No Python runtime available. Financial precision via `decimal.js` library is a workaround, not a solution — it lacks the ecosystem maturity and regulatory credibility of Python's `Decimal`. |

---

## Approved Deviations

*None — this system applies all constitutional standards without deviation at v1.0.*

**Additional requirements beyond constitutional minimums:**
- Test coverage: 100% branch coverage on all financial calculation functions (S7.29)
- `DEPOSITS_ENABLED` and `WITHDRAWALS_ENABLED` feature flags must exist before v1 launch
- Financial freeze runbook (`runbooks/financial-freeze-runbook.md`) must be tested in staging before v1 launch

---

> **Status: accepted — 2026-05-08**
> *Owner approval: Maluleke Kurhula Success*
