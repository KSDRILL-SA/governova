# FundsLink Academy — System Context

---

| Attribute          | Value |
|--------------------|-------|
| **System**         | FundsLink Academy |
| **Stack**          | Angular + FastAPI |
| **Build Phase**    | Phase 1 — Core Architecture · Stages 00–03 ✅ DONE · **Stage 04 (frontend) DESIGNED — ready to build** |
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
| 1 | Authentication (registration, login, JWT) | G1 | ✅ DONE (Stage 02; G2 + hardened + DB-integrated) |
| 2 | Student profile creation | G1 | ✅ DONE (Stage 03; SA-ID AES-GCM + blind index, document pipeline) |
| 3 | Scholarship application submission | G1 | ✅ DONE (Stage 03; state machine + eligibility pre-screen, Human-Final) |
| 4 | AI-matched funding options (advisory) | G1 | ✅ DONE (Stage 03; advisory matching — local heuristic + ChromaDB/Mongo seams; real model = ADR-0007 v1.x) |
| 5 | Application status tracking | G2 | ✅ DONE (Stage 03; tracking + outbox notifications) |

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
"Post-phase verification" rule. (Stage 02 met ST-2.1/2.2/2.3/2.9 + D-015; Stage 03 met ST-1.2/1.3/2.3/2.4/2.6/3.1/3.4 + D-001/004/006/010/011/014.)

## Approved Deviations
| Deviation | Why | Scope |
|-----------|-----|-------|
| import-linter `allow_indirect_imports = true` on the layering contract | The rule's intent is *direct* imports — a service must not import a DB driver itself; the canonical service→repository→DB chain is an expected indirect import. A direct DB-driver import in a service is still caught (verified). | Stage 02 (first service) |
| Contract (S2.7) expanded with auth endpoints beyond the original 4 | Founder-approved (L4) "fill all gaps": MFA enrol/activate, email-verify(+resend), forgot/reset/change-password — shapes proposed in their PRs. | Stage 02 |
| `EMAIL_VERIFICATION_REQUIRED` config flag (default off) | S3.12 configurable verification mode; off until the email provider is live so v1 flows are unbroken. | Stage 02 |

## Constitutional Amendments (this system's contributions to the template)
Both ratified by the Founder (L4) on 2026-06-15 via the C0 §8 protocol (24h sit satisfied, adversarial + cross-constitution review documented in the amendment issue) and committed to `system-design-template`.
| # | Amendment | Status |
|---|-----------|--------|
| A-1 | **C5** — "Ledger tables are immutable; corrections are reversing entries" (MASTER-SPEC §16.2) | ✅ RATIFIED (L4, 2026-06-15) → **C5 v1.1, S5.65** (Part 9 — Financial Ledger Integrity). Enforce at the v1.5 ledger build. |
| A-2 | **C10** — post-phase verification against the system's stress-test audit (ST) + scenario rulings (D-NNN), mandatory before any handoff (generic — all KSDRILL systems) | ✅ RATIFIED (L4, 2026-06-15) → **C10 v1.1, S10.37** (Part 7 — Relay Handoff Verification). |
| A-3 | **C10** — phase-status-sync: on gate completion, update EVERY living doc before the handoff so the next engineer never reads a contradicting "next stage" (S10.38) | ✅ RATIFIED (L4, 2026-06-20) → **C10 v1.2, S10.38** (Part 7 — Relay Handoff Verification). |
| A-4 | **C1/C8** — reproducible deps: a committed lockfile + frozen install in CI (`uv sync --frozen` / equivalent); the gate fails on lock↔manifest drift | ✅ RATIFIED (L4, 2026-06-20) → **C1 v1.1, S1.98** (Part 17 — Dependency & Build Reproducibility); enforced as a C8 pipeline gate. |
| A-5 | **C4/C10** — design-package-first frontend: the full design (structure · tokens · components · navigation · marketing · handoff) is documented + Founder-ratified BEFORE the build session | ✅ RATIFIED (L4, 2026-06-20) → **C4 v1.1, S4.83** (Part 11 — Design-First). |
| A-6 | **C10** — AI integration via Ports & Adapters: advisory-only + human-final, grounded (no hallucinated entities), cost-fused, eval-gated, local-first/POPIA (FundsLink ADR-0007 generalised) | ✅ RATIFIED (L4, 2026-06-20) → **C10 v1.2, S10.39** (Part 8 — AI Feature Integration). |

---

*Last updated: 2026-06-20 (Stage 03 complete — 6 backend modules G3, migrations →0018, eligibility + hardening passes, contract 32 ops; Stage 04 frontend DESIGN PACKAGE complete + Founder-ratified, ready to build; AI-Enablement ratified as the system's ADR-0007 for v1.x. Template contributions A-3…A-6 RATIFIED L4 2026-06-20 and applied — S1.98 (C1 v1.1), S4.83 (C4 v1.1), S10.38 + S10.39 (C10 v1.2)).*
