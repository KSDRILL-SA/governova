# Quick Reference — KSDRILL SA Constitutional System

> **The fastest path to the right standard.** Organised by concern, not by constitution.

---

## Authentication

| Question | Standard | Constitution |
|----------|----------|-------------|
| Which auth strategy for Next.js? | S3.1, S3.5 | C3 |
| Which auth strategy for Angular? | S3.1, S3.13 | C3 |
| Where does the access token go on Angular? | **S3.14 — Angular memory, NOT localStorage** | C3 |
| Where does the refresh token go? | S3.14 — HttpOnly cookie | C3 |
| Where is auth data stored in the database? | S3.2, S5.4 — PostgreSQL only | C3, C5 |
| How is role enforcement done? | S3.21, S3.22, S3.23 | C3 |
| What happens on logout? | S3.18 — revoke, deny-list, BroadcastChannel | C3 |
| What happens on password change? | S3.35 — invalidate ALL sessions | C3 |
| How are auth changes reviewed? | S3.36 — backend + frontend review required | C3 |
| Auth Override Rule? | C0 §7.3 — C3 beats all other constitutions on security | C0 |

---

## Database

| Question | Standard | Constitution |
|----------|----------|-------------|
| Where does financial data go? | **S5.3 — PostgreSQL ONLY** | C5 |
| Where does auth data go? | S5.4 — PostgreSQL only | C5 |
| Where does AI-generated content go? | S5.1, S5.33 — MongoDB (Angular only) | C5 |
| Where do vector embeddings go? | S5.45 — ChromaDB (FundsLink only) | C5 |
| What's the primary ORM? | S5.9 — Prisma | C5 |
| When to use raw SQL? | S5.19 — complex aggregates, CTEs, window functions, financial precision | C5 |
| Is raw SQL ever OK? | Yes — S5.19. Must be parameterised (S5.21), commented, and in a service function (S5.24) | C5 |
| SQL injection prevention? | **S5.21 — always parameterised, never string-interpolated** | C5 |
| Can you use `SELECT *`? | Never — S5.11 — explicit `select` required | C5 |
| What's required on every table? | S5.10 — id (cuid), created_at, updated_at, deleted_at | C5 |
| Can you hard-delete records? | Never in production — S5.8 — soft delete only | C5 |
| What type for monetary columns? | **S5.28 — Decimal, never Float** | C5 |
| When do migrations run? | S5.59 — before service starts, never after | C5 |

---

## Frontend

| Question | Standard | Constitution |
|----------|----------|-------------|
| Styling philosophy? | **S4.13 (Tailwind for layout) + S4.14 (Custom CSS for brand) — both first-class** | C4 |
| What viewport is the mobile baseline? | S4.2 — 320px | C4 |
| What framework for Maphophe/SyncUp? | S4.1 — Next.js | C4 |
| What framework for FundsLink/Reserve Bank? | S4.1 — Angular | C4 |
| State management for server data (Next.js)? | S4.28 — TanStack Query | C4 |
| State management for client state (Next.js)? | S4.29 — Zustand | C4 |
| State management (Angular)? | S4.30 — Angular Signals + RxJS | C4 |
| Forms (Next.js)? | S4.46 — React Hook Form + Zod | C4 |
| Forms (Angular)? | S4.47 — Reactive Forms | C4 |
| Change detection (Angular)? | S4.53 — OnPush always | C4 |
| Layer build order? | **S4.79 — Interface → Service → Component → UI** | C4 |
| How many commits per feature? | S4.80 — one commit per layer minimum | C4 |
| Async state rendering? | S4.11 — loading + error + success always | C4 |

---

## API Design

| Question | Standard | Constitution |
|----------|----------|-------------|
| Contract first or code first? | **S2.7 — OpenAPI contract before any endpoint code** | C2 |
| What's the response shape? | S2.19 — `{ success, data?, error? }` | C2 |
| Validation on API boundaries? | S2.23 — Zod (Next.js) / Pydantic (FastAPI) | C2 |
| Versioning? | S2.76 — `/api/v1/` prefix, versioning governance defined | C2 |
| Business logic belongs where? | **S2.1 — service layer exclusively** | C2 |
| Single gateway? | S2.2 — all requests through `/api/v1/` | C2 |

---

## Stack Assignment

| System | Stack | Governs |
|--------|-------|---------|
| FundsLink Academy | Angular + FastAPI | S6.2, S6.4 |
| Maphophe Community | Next.js | S6.1 |
| KSDRILL Reserve Bank | Angular + FastAPI | S6.2, S6.3 |
| SyncUp Creator Platform | Next.js | S6.1 |
| Future system (SEO-critical) | Next.js | S6.1 |
| Future system (Enterprise / Financial / AI) | Angular + FastAPI | S6.2 |
| Future system (unclear) | ADR required | S6.6 |

---

## Testing

| Question | Standard | Constitution |
|----------|----------|-------------|
| When are tests written? | **S7.1 — alongside the code, same PR** | C7 |
| What runner for Next.js? | S7.2 — Jest + RTL | C7 |
| What runner for Angular? | S7.2 — Vitest + Angular utilities | C7 |
| What runner for Python? | S7.2 — pytest + pytest-asyncio | C7 |
| What E2E tool? | S7.17 — Playwright (both stacks) | C7 |
| Coverage minimums? | S7.25 — Next.js 70%, Angular 75%, Python 80% | C7 |
| Visual regression at which widths? | S7.19 — 320/375/390px | C7 |
| Auth tests required? | S7.11 — 200, 401, 403 for every protected endpoint | C7 |
| Financial calculation test values? | **S7.38 — Decimal, never float** | C7 |

---

## Deployment

| Question | Standard | Constitution |
|----------|----------|-------------|
| Next.js deploys where? | S8.1 — Vercel | C8 |
| FastAPI deploys where? | **S8.2 — Railway (never Vercel serverless)** | C8 |
| Angular frontend deploys where? | S8.3 — Vercel (separate project from FastAPI) | C8 |
| Deploy order for Angular stack? | S6.29 / S8.16 — FastAPI first, Angular second | C6, C8 |
| How many environments? | S8.5 — Development, Staging, Production | C8 |
| How to get to production? | S8.12 — manual, gated, requires approval | C8 |
| How to rollback? | S8.67–S8.72 — Vercel one-click / Railway redeploy | C8 |
| CI time limit? | S8.10 — under 5 minutes | C8 |

---

## AI Collaboration

| Question | Standard | Constitution |
|----------|----------|-------------|
| What's the first file AI reads? | `AI-INSTRUCTIONS.md` — S10.6 | C10 |
| Can AI approve a decision? | **Never — S10.8 — L4 is human-only always** | C10 |
| What file is required in project before building? | S10.21 — `CONSTITUTION-INDEX.md` | C10 |
| Three-phase design workflow? | S10.15 — Outside editor → Validate → Build | C10 |
| Solo dev: second code reviewer? | S10.27 — Claude reviews diff before merge | C10 |
| Can AI approve a constitutional amendment? | Never — S10.8 — amendment requires human approval per C0 §8 | C10 |

---

## Incident Response

| Question | Standard | Constitution |
|----------|----------|-------------|
| Financial data integrity incident severity? | **S8.50 — Automatic SEV0. Freeze operations immediately.** | C8 |
| First action in SEV0? | S8.49 — Restore service first, investigate second | C8 |
| Classification time limit? | S8.48 — 5 minutes | C8 |
| Status updates frequency? | S8.54 — every 30 minutes during active SEV0/SEV1 | C8 |
| Post-mortem required? | S8.77 — every SEV0 and SEV1 | C8 |
| Reserve Bank financial freeze? | S8.50 — `DEPOSITS_ENABLED=false`, `WITHDRAWALS_ENABLED=false` | C8 |

---

*Last updated: v1.0 — 2026-05-08*
