# FundsLink Academy — System Context

---

| Attribute          | Value |
|--------------------|-------|
| **System**         | FundsLink Academy |
| **Stack**          | Angular + FastAPI |
| **Build Phase**    | Phase 1 — Core Architecture · Stages 00/01/02 ✅ DONE · **Stage 03 (backend) NEXT** |
| **Current Group**  | G1 — Core (primary workflow) |
| **Operating Mode** | SOLO |
| **Active Overlay** | `overlays/solo-dev-overlay.md` |
| **ADR**            | `adrs/ADR-001-fundslink-stack.md` |
| **Lock Date**      | 2026-05-08 |

---

## Problem Statement

342,000+ South African students are excluded from education funding every year because the funding application process is fragmented, inaccessible, and impossible to navigate without institutional support.

## Primary Workflow

Student creates profile → submits application → receives AI-matched funding options

## v1 Done When

A student can apply and receive at least one matched funding opportunity end-to-end in production.

---

## Active Constitutions

All 11 constitutions apply (C0–C10). Stack-specific scope:
- C3: Angular+FastAPI auth path (S3.13–S3.20)
- C4: Angular standards (S4.52–S4.60) apply in addition to both-stacks standards
- C5: PostgreSQL + MongoDB + ChromaDB all active
- C6: Angular+FastAPI topology (S6.13), deploy order (S6.29)
- C7: Vitest + pytest (S7.2)
- C8: Railway for FastAPI (S8.2), Vercel for Angular (S8.3)

---

## v1 Feature Set (max 6 — S9.9)

| # | Feature | Group | Status |
|---|---------|-------|--------|
| 1 | Authentication (registration, login, JWT) | G1 | ✅ DONE (Stage 02, gate G2 + hardened + DB-integrated) |
| 2 | Student profile creation | G1 | — (Stage 03) |
| 3 | Scholarship application submission | G1 | — |
| 4 | AI-powered eligibility matching (LangChain + ChromaDB) | G1 | — |
| 5 | Application status tracking | G2 | — |

**Total: 5 features** — within v1 limit.

---

## Database Assignment

| Data Type | Database | Standard |
|-----------|----------|----------|
| Users, auth, roles, sessions | PostgreSQL | S5.4 |
| Scholarship applications, funding amounts | PostgreSQL | S5.3 |
| AI-generated scholarship reasoning, tags | MongoDB | S5.33 |
| Scholarship document embeddings, RAG context | ChromaDB | S5.45 |

---

## Critical Standards for This System

| Standard | Why Critical for FundsLink |
|----------|--------------------------|
| `S3.13–S3.20` | Angular+FastAPI JWT auth — entire auth stack |
| `S3.14` | Access token in Angular memory — NOT localStorage |
| `S3.15` | HTTP interceptor with deduplication |
| `S5.3` | Funding amounts in PostgreSQL only — never MongoDB |
| `S5.21` | Raw SQL parameterisation — financial queries |
| `S5.28` | Decimal for funding amounts — never Float |
| `S5.45–S5.52` | ChromaDB standards — AI matching |
| `S6.29` | FastAPI deploys before Angular — always |
| `S7.12` | Interceptor deduplication test — critical for dashboard |
| `S7.37` | LangChain tests use pre-computed embeddings |
| `S8.51` | AI degradation — graceful fallback to manual application |

---

## Environment Variables Required

| Variable | Service | Notes |
|----------|---------|-------|
| `DATABASE_URL` | Railway (FastAPI) | PostgreSQL connection |
| `MONGODB_URL` | Railway (FastAPI) | MongoDB connection |
| `CHROMADB_URL` | Railway (FastAPI) | Internal Railway URL only |
| `REDIS_URL` | Railway (FastAPI) | Token deny-list, circuit breaker |
| `RS256_PRIVATE_KEY` | Railway (FastAPI) | JWT signing |
| `RS256_PUBLIC_KEY` | Railway (FastAPI) | JWT verification |
| `BCRYPT_ROUNDS` | Railway (FastAPI) | Default: 12 |
| `CORS_ALLOWED_ORIGINS` | Railway (FastAPI) | Angular Vercel URL |
| `SENTRY_DSN` | Railway + Vercel | Error tracking |
| `OPENAI_API_KEY` | Railway (FastAPI) | Embedding model |

---

## Post-phase verification (mandatory — Stage 02 onward)
Before each handoff, the engineer verifies the phase satisfies the adversarial results in the
app's `docs/audits/stress-test-audit.md` (ST-1…6) + edge rulings in
`docs/product/scenarios-and-decisions.md` (D-NNN), citing the ids. See the app CONSTITUTION-INDEX
"Post-phase verification" rule. (Stage 02 met ST-2.1/2.2/2.3/2.9 + D-015.)

## Approved Deviations
| Deviation | Why | Scope |
|-----------|-----|-------|
| import-linter `allow_indirect_imports = true` on the layering contract | The rule's intent is *direct* imports — a service must not import a DB driver itself; the canonical service→repository→DB chain is an expected indirect import. A direct DB-driver import in a service is still caught (verified). | Stage 02 (first service) |
| Contract (S2.7) expanded with auth endpoints beyond the original 4 | Founder-approved (L4) "fill all gaps": MFA enrol/activate, email-verify(+resend), forgot/reset/change-password — shapes proposed in their PRs. | Stage 02 |
| `EMAIL_VERIFICATION_REQUIRED` config flag (default off) | S3.12 configurable verification mode; off until the email provider is live so v1 flows are unbroken. | Stage 02 |

## Open Constitutional Amendment Proposals
| # | Proposal | Status |
|---|----------|--------|
| A-1 | **C5** — "Ledger tables are immutable; corrections are reversing entries" (MASTER-SPEC §16.2) | PROPOSED — ratify before v1.5 ledger build (C0 §8) |
| A-2 | **C7/C10** — make post-phase verification against the system's stress-test audit (ST) + scenario rulings (D-NNN) a *generic* mandatory standard before any handoff | PROPOSED by sole engineer — awaiting Founder C0 §8 ratification |

---

*Last updated: 2026-06-15 (Stage 02 complete; sole-operator mode — Founder collapsed the relay).*
