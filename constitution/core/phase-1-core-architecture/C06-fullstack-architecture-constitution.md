# C6 — Full-Stack Architecture Constitution

---

| Attribute          | Value                                                              |
|--------------------|--------------------------------------------------------------------|
| **Document**       | C6 — Full-Stack Architecture Constitution                          |
| **Organisation**   | KSDRILL SA                                                         |
| **Version**        | v1.0                                                               |
| **Status**         | LOCKED                                                             |
| **Locked**         | 2026-05-08                                                         |
| **Next Review**    | 2026-08-08                                                         |
| **Applies To**     | Both Stacks · All Systems                                          |
| **Paired With**    | — (Integration document — no implementation guide)                 |

---

> *"One system. Two stacks. Zero drift. The architecture is decided once and defended always."*

---

## Opening Statement

The Full-Stack Architecture Constitution governs the topology of the complete KSDRILL SA system — how the two stacks are defined, how new systems are assigned to a stack, how the frontend and backend communicate across the stack boundary, how deployments are coordinated, and how architectural decisions are recorded for future reference.

This constitution is the result of merging two previously separate documents — the Full System Design and the Full-Stack Integration Constitution — into a single authoritative source. Those two documents covered the same system from different angles and diverged in version references, request flow descriptions, and auth token storage specifications. The merge eliminates the drift and the cross-reference ambiguity.

This constitution depends on all Phase 1 constitutions (C2, C3, C4, C5) and synthesises them into an integrated view. It does not restate the standards defined in those constitutions — it references them. When C6 and another Phase 1 constitution appear to conflict, the other constitution governs per the hierarchy in C0 §7.

This document contains the decisions a system architect must make before any engineer writes the first line of code: which stack, which deployment topology, which request flow, how auth traverses the stack. Once these decisions are locked in an ADR, they are immutable for the lifetime of that system's major version.

---

## Table of Contents

| Part | Title | Standards |
|------|-------|-----------|
| Part 1 | Stack Assignment Framework | S6.1–S6.7 |
| Part 2 | ADR Process & Template | S6.8–S6.11 |
| Part 3 | System Topology — Dual Stack | S6.12–S6.17 |
| Part 4 | Request Flows per Stack | S6.18–S6.24 |
| Part 5 | Cross-Stack Communication | S6.25–S6.28 |
| Part 6 | Deployment Coordination | S6.29–S6.33 |
| Part 7 | Tech Stack Reference | S6.34–S6.38 |
| Part 8 | Flagship System Register | S6.39–S6.42 |
| Part 9 | Cross-Constitution Architecture Map | S6.43–S6.44 |
| Anti-Patterns Index | — | AP-S6.* |
| Cross-Constitution Dependency Map | — | — |
| Amendment Log | — | — |

---

## Part 1 — Stack Assignment Framework (`S6.1`–`S6.7`)

The stack assignment decision is made once per system at design time. It is driven by system requirements against defined criteria. It is immutable for the lifetime of that system's major version. No mid-build stack changes — see CF-12.

---

### S6.1 — SEO-Critical or Content-Driven Systems Use Next.js

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S6.1 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `C0 §10` (stack assignment summary) |
| **Enforced By** | Architecture Review · ADR process (S6.8) |

**Standard:**
Systems where SEO is a primary requirement — public-facing pages, content-driven platforms, platforms requiring server-side rendering or static generation for discoverability — are assigned to the Next.js stack. The Next.js App Router with SSR/SSG is the correct technical choice for SEO-critical systems; Angular SPA is not.

**Rationale:**
Angular is a client-side SPA framework. Without additional SSR infrastructure (Angular Universal), Angular pages are not indexable by search engines. Next.js was built for SSR and SSG — it handles SEO concerns natively without additional configuration.

**Anti-Patterns:**
- `AP-S6.1a` — Building a content-driven, SEO-critical community platform with Angular — the platform is invisible to search engines without complex SSR setup that adds maintenance cost.

**Cross-References:** `C0 §10` (locked assignments), `S6.8` (ADR documents the decision)

---

### S6.2 — Enterprise Dashboards or Financial Precision Systems Use Angular+FastAPI

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S6.2 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `C0 §10`, `S6.8` (ADR) |
| **Enforced By** | Architecture Review · ADR process |

**Standard:**
Systems requiring enterprise-grade multi-role dashboards with complex form workflows, precision financial calculations, or AI-powered features requiring a native Python backend are assigned to the Angular+FastAPI stack. Angular's Reactive Forms, strict TypeScript, OnPush change detection, and RxJS composition suit complex enterprise UI. FastAPI's Python runtime enables native LangChain, NumPy, and financial precision libraries.

**Anti-Patterns:**
- `AP-S6.2a` — Building a complex financial calculation system with Next.js JavaScript — JavaScript floating point cannot provide the decimal precision that financial regulation requires; Python's `Decimal` library via FastAPI is the correct tool.

**Cross-References:** `C0 §10` (locked assignments), `S6.3` (financial precision criterion), `S6.4` (Python AI criterion)

---

### S6.3 — Precision Financial Calculations Require FastAPI Python Backend

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S6.3 |
| **Priority**    | Critical |
| **Applies To**  | Angular Only |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S6.2`, `S5.3` (financial data in PostgreSQL) |
| **Enforced By** | Architecture Review |

**Standard:**
Any system where financial precision is a core requirement — interest calculations, deposit schedules, currency conversions, balance reconciliation — uses Python FastAPI with the `Decimal` library for all monetary arithmetic. JavaScript `number` floating-point arithmetic is forbidden for financial calculations. This is a hard technical constraint, not a preference.

**Anti-Patterns:**
- `AP-S6.3a` — `0.1 + 0.2` in JavaScript for financial calculations — IEEE 754 floating point produces `0.30000000000000004`; financial systems require exact decimal arithmetic.

**Cross-References:** `S6.2` (Angular+FastAPI assignment), `S5.28` (Decimal columns in PostgreSQL)

---

### S6.4 — AI-Powered Features Requiring Python Use Angular+FastAPI

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S6.4 |
| **Priority**    | Critical |
| **Applies To**  | Angular Only |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S6.2` |
| **Enforced By** | Architecture Review |

**Standard:**
Systems with AI features that natively require Python — LangChain pipelines, RAG implementations, vector similarity via ChromaDB, PyTorch or HuggingFace inference — use the Angular+FastAPI stack. The Python AI ecosystem does not have equivalent JavaScript implementations for production use; using Node.js wrappers introduces fragility and performance overhead.

**Anti-Patterns:**
- `AP-S6.4a` — Implementing a LangChain RAG pipeline via a Node.js wrapper called from Next.js — the wrapper adds network overhead, version mismatch risk, and loses access to the full Python AI ecosystem.

**Cross-References:** `S6.2` (Angular+FastAPI), `S5.45` (ChromaDB — FundsLink)

---

### S6.5 — Simple Systems May Use Either Stack — ADR Required

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S6.5 |
| **Priority**    | Standard |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S6.8` (ADR process) |
| **Enforced By** | Architecture Review · ADR |

**Standard:**
Internal tools, admin panels, and simple CRUD systems that do not require SEO, financial precision, or Python AI may use either stack. The decision requires an ADR evaluating: team familiarity, existing infrastructure alignment, expected complexity growth, and maintenance cost. The decision is documented and immutable.

**Cross-References:** `S6.8` (ADR process), `S6.6` (flexible stack)

---

### S6.6 — Future Systems Require ADR — Rubric Evaluation Mandatory

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S6.6 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S6.8` (ADR process), `C0 §10` |
| **Enforced By** | Pre-build checklist (C0 §11) |

**Standard:**
Every new system — including systems not yet conceived — requires a completed Architecture Decision Record evaluating stack assignment against the rubric criteria (S6.1–S6.5) before development begins. No system starts without a locked ADR and a registered system context file. The ADR is committed to `adrs/` in `system-design-template`.

**Anti-Patterns:**
- `AP-S6.6a` — Starting development on a new system "in the same stack as the last one" without an ADR — the new system's requirements may differ; the assumption is unvalidated.

**Cross-References:** `S6.8` (ADR process), `C0 §11` (pre-build checklist)

---

### S6.7 — Stack Assignment Is Immutable — No Mid-Build Changes

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S6.7 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S6.6` (ADR locks the decision) |
| **Enforced By** | Architecture Review · C0 amendment protocol |

**Standard:**
The stack assignment is locked at ADR creation and immutable for the lifetime of that system's major version. Changing stack mid-build requires: a new ADR superseding the previous, a C6 Major amendment, and written justification for why the original ADR criteria no longer apply. CF-12 documents the consequence of stack changes without this process.

**Anti-Patterns:**
- `AP-S6.7a` — "We'll switch to Next.js because the Angular build is complex" mid-sprint — the complexity is an architectural problem to solve, not a reason to change the stack assignment; a stack change mid-build invalidates all auth, database, and testing decisions made to that point.

**Cross-References:** `CF-12` (Common Failure Register — stack change without amendment = SEV0)

---

## Part 2 — ADR Process & Template (`S6.8`–`S6.11`)

Architecture Decision Records document every significant architectural decision — stack assignment, database assignment, external service selection, and approved deviations from constitutional standards.

---

### S6.8 — Every Significant Architectural Decision Requires an ADR

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S6.8 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S1.27` (design-first) |
| **Enforced By** | Pre-build checklist · Code Review |

**Standard:**
Architecture Decision Records are created for: new system stack assignment, database technology selection for a new data entity class, external service integration (new payment provider, new auth provider, new AI service), and any approved deviation from a constitutional standard. ADRs are stored in `adrs/` in `system-design-template` as `ADR-{NNN}-{short-title}.md`.

**Anti-Patterns:**
- `AP-S6.8a` — Integrating a new external payment API without an ADR — the decision rationale and alternatives considered are lost; the decision appears to be arbitrary to future engineers.

**Cross-References:** `S6.6` (every new system requires an ADR), `S1.27` (design-first)

---

### S6.9–S6.11 — ADR Standards

> **S6.9** — ADR status values: `proposed` (under review), `accepted` (locked), `superseded` (replaced by newer ADR with reference), `deprecated` (decision no longer applies). An ADR is never deleted — it is superseded or deprecated.

> **S6.10** — ADR template fields: Title, Date, Status, Context (the forces at play), Decision (what was decided and why), Consequences (what becomes easier and harder), Alternatives Considered (options evaluated and why rejected). All fields are required.

> **S6.11** — Approved constitutional deviations are documented in both the ADR and the system context file — the deviation is visible to AI assistants reading the context file before build sessions.

---

## Part 3 — System Topology — Dual Stack (`S6.12`–`S6.17`)

The KSDRILL SA system operates two parallel stacks. These are not alternatives — they are distinct architectures serving different system requirements simultaneously.

---

### S6.12 — Next.js Stack Topology

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S6.12 |
| **Priority**    | Critical |
| **Applies To**  | Next.js Only |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S6.1`, `S3.5` (NextAuth), `S5.9` (Prisma) |
| **Enforced By** | Architecture Review |

**Standard:**
The Next.js stack is a unified full-stack architecture. Frontend (React, App Router, Tailwind + Custom CSS), API layer (Next.js API Routes under `/api/v1/`), and authentication (NextAuth.js with Prisma Adapter) are co-deployed in one Vercel project. The backend is not a separate server — it is the API route layer within the same deployment. Database: PostgreSQL via Prisma only.

**Systems:** Maphophe Community System, SyncUp Creator Platform.

```
Browser
  ↓ HTTPS
Next.js Frontend (React · App Router · Tailwind + Custom CSS)
  ↓ ALL requests through /api/v1/* (S2.2 — single gateway)
Next.js API Routes ←── NextAuth.js (S3.5 — database sessions)
  ↓
Service Layer (S2.1 — business logic)
  ↓
Prisma ORM + Raw SQL (S5.9, S5.19)
  ↓
PostgreSQL + Redis/BullMQ (where applicable)
```

**Anti-Patterns:**
- `AP-S6.12a` — Browser calling a FastAPI backend from a Next.js system — the Next.js stack has no FastAPI; this indicates stack confusion.

**Cross-References:** `S6.1` (assignment), `S2.2` (single gateway), `S3.5` (database sessions)

---

### S6.13 — Angular+FastAPI Stack Topology

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S6.13 |
| **Priority**    | Critical |
| **Applies To**  | Angular Only |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S6.2`, `S3.13` (RS256 JWT), `S5.9` (Prisma) |
| **Enforced By** | Architecture Review |

**Standard:**
The Angular+FastAPI stack is a decoupled enterprise architecture. Frontend (Angular, TypeScript strict, Tailwind + Custom CSS) deploys separately from Backend (FastAPI, Python) on separate platforms. They communicate via authenticated REST. Database: PostgreSQL + MongoDB + Redis (all stacks); ChromaDB (FundsLink only).

**Systems:** FundsLink Academy, KSDRILL Reserve Bank.

```
Browser
  ↓ HTTPS
Angular Frontend (TypeScript strict · Tailwind + Custom CSS · Reactive Forms)
  ↓ HTTP REST + Bearer JWT (S3.15 — HTTP interceptor)
FastAPI Backend (Python) ←── JWT Auth Middleware (S3.17)
  ↓ splits:
Prisma ORM + Raw SQL → PostgreSQL
Beanie ODM → MongoDB (AI content, logs)
LangChain → ChromaDB (FundsLink AI service only)
  ↓
BullMQ + Redis (Reserve Bank scheduled jobs)
```

**Anti-Patterns:**
- `AP-S6.13a` — Angular component calling Next.js API routes — Angular systems have no Next.js backend; this is a cross-stack confusion indicating incorrect stack assignment.

**Cross-References:** `S6.2` (assignment), `S3.13` (JWT), `S3.15` (interceptor), `CF-08` (direct API bypass)

---

### S6.14 — The Two Stacks Never Share Services — No Cross-Stack API Calls

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S6.14 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S6.12`, `S6.13` |
| **Enforced By** | Network review · Code Review |

**Standard:**
A Next.js system never calls a FastAPI service. An Angular system never calls a Next.js API route. The two stacks are independently complete. Data that needs to flow between systems (future requirement) uses a dedicated integration layer or event bus — never direct cross-stack HTTP calls.

**Rationale:**
Cross-stack service calls create coupling between independently deployed systems. A Next.js deployment depending on a Railway FastAPI service creates a single point of failure for the Next.js system that negates the independence of the deployment topology.

**Anti-Patterns:**
- `AP-S6.14a` — Maphophe (Next.js) calling FundsLink's FastAPI endpoint for shared scholarship data — creates a runtime dependency on a separately deployed service; both systems are affected by either system's outage.

**Cross-References:** `S6.12` (Next.js topology), `S6.13` (Angular topology)

---

### S6.15–S6.17 — Additional Topology Standards

> **S6.15** — Each system has exactly one primary API gateway. Next.js systems: `/api/v1/` routes. Angular systems: FastAPI at the Railway internal URL. No secondary API surfaces.

> **S6.16** — Both stacks use the same BullMQ + Redis pattern for background jobs — Next.js uses Vercel cron for simple jobs, BullMQ for queue-based workflows. Angular+FastAPI uses Railway Redis with BullMQ for all scheduled and queued operations.

> **S6.17** — Internal service-to-service calls (within the Angular stack: FastAPI to ChromaDB, FastAPI to MongoDB) use Railway internal networking — never public internet routing for internal traffic.

---

## Part 4 — Request Flows per Stack (`S6.18`–`S6.24`)

Request flows document the exact path of a request from browser to database and back. These are the authoritative reference for understanding how auth, validation, and data access work together.

---

### S6.18 — Next.js Authenticated Request Flow

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S6.18 |
| **Priority**    | Critical |
| **Applies To**  | Next.js Only |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S6.12` (Next.js topology), `S3.5`–`S3.7` (auth) |
| **Enforced By** | Architecture Review · Integration tests |

**Standard:**
Every authenticated Next.js request follows this exact flow:

```
1. Browser sends HTTPS request with HttpOnly session cookie
2. Next.js middleware (S3.7) verifies session cookie via NextAuth
3. Session invalid → redirect to /auth/login with callbackUrl
4. Session valid → request proceeds to API route handler
5. API route handler independently verifies session (S3.7 — double layer)
6. Handler extracts user ID and role from session object
7. Service function called with verified user context
8. Service: validate input with Zod (S2.23)
9. Service: authorise (S3.21 — role check) + verify ownership (S3.22)
10. Service: call Prisma ORM or raw SQL (S5.9, S5.19)
11. Service: Prisma includes deleted_at filter (S5.12) + explicit select (S5.11)
12. Service: build response using standard shape (S2.19)
13. API route: return standard JSON response
14. Browser: TanStack Query updates cache; component re-renders
```

**Anti-Patterns:**
- `AP-S6.18a` — Service function performing auth check instead of route handler — auth is a route entry concern per S3.23.

**Cross-References:** `S3.7` (middleware), `S2.19` (response shape), `S5.11` (explicit select)

---

### S6.19 — Angular+FastAPI Authenticated Request Flow

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S6.19 |
| **Priority**    | Critical |
| **Applies To**  | Angular Only |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S6.13` (Angular topology), `S3.13`–`S3.17` (JWT auth) |
| **Enforced By** | Architecture Review · Integration tests |

**Standard:**
Every authenticated Angular+FastAPI request follows this exact flow:

```
1. Angular component calls service method
2. Angular service calls HTTP client
3. HTTP interceptor (S3.15) attaches: Bearer {access_token} + X-Request-ID
4. FastAPI receives request
5. FastAPI Depends(get_current_user): decode RS256 (S3.13) → check JTI deny-list (S3.18) → query User
6. User not found or deleted_at set → 401
7. Depends(require_role(Role)): check role (S3.17)
8. Wrong role → 403
9. Route handler called with authenticated user
10. Service: validate input with Pydantic (S2.23)
11. Service: verify resource ownership (S3.22)
12. Service: Prisma ORM or raw SQL (S5.9, S5.19)
13. Service: build response using Pydantic model (S2.19)
14. FastAPI: return standard JSON
15. Angular interceptor: 401 → trigger silent refresh (S3.15 deduplication)
16. Angular service: update Signal state; component re-renders (S4.30)
```

**Anti-Patterns:**
- `AP-S6.19a` — Access token stored in localStorage — directly violates S3.14; interceptor reads from Angular memory.

**Cross-References:** `S3.14` (in-memory token — not localStorage), `S3.15` (interceptor deduplication), `S3.17` (FastAPI Depends())

---

### S6.20–S6.24 — Additional Request Flow Standards

> **S6.20** — The `X-Request-ID` header is generated by the interceptor (Angular) or Next.js middleware for every request. FastAPI includes it in the structured log entry. Sentry captures it in the frontend error context. This enables full cross-system request tracing (S2.60).

> **S6.21** — Error responses in both stacks use the standard error shape defined in S2.19 — `{ success: false, error: { code, message, details? } }`.

> **S6.22** — API versioning: `/api/v1/` prefix on all routes. When v2 is introduced per S2.76–S2.80, v1 remains live. No request routing changes in the frontend during v1/v2 coexistence.

> **S6.23** — Health check endpoints at `/api/health` (Next.js) and `/health` (FastAPI) return 200 with database connectivity status. These are the endpoints monitored by Better Stack (S8.10).

> **S6.24** — WebSocket connections (SyncUp real-time features, Reserve Bank live balance) are managed as separate connection types — they do not go through the standard REST request flow.

---

## Part 5 — Cross-Stack Communication (`S6.25`–`S6.28`)

The two stacks do not communicate directly. These standards govern the exceptional cases where data-level coordination between stack contexts is needed.

---

### S6.25 — No Direct Cross-Stack HTTP Calls Between Systems

Per S6.14 — restated here for emphasis. No system in the Next.js stack calls an endpoint in the Angular+FastAPI stack or vice versa. This is an architectural boundary.

---

### S6.26–S6.28 — Cross-Stack Communication Standards

> **S6.26** — Future cross-system data sharing uses a shared PostgreSQL read replica or an explicit integration API with its own ADR — never direct service-to-service HTTP calls between stacks.

> **S6.27** — Shared authentication between stacks (a user authenticated in Next.js accessing an Angular system) is not supported in v1. Each system has its own independent auth. Cross-system SSO is a future ADR decision.

> **S6.28** — If business logic requires data from both stacks simultaneously, the feature design is incorrect — re-evaluate the feature boundaries per C9 feature governance before implementing.

---

## Part 6 — Deployment Coordination (`S6.29`–`S6.33`)

---

### S6.29 — Angular Stack Deploy Order: FastAPI First, Angular Second

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S6.29 |
| **Priority**    | Critical |
| **Applies To**  | Angular Only |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S8.16` (Angular deploy coordination in CI) |
| **Enforced By** | CI/CD pipeline |

**Standard:**
When deploying breaking API changes on the Angular stack: (1) Deploy FastAPI to Railway first, wait for health check success. (2) Only if FastAPI deploy succeeds, deploy Angular to Vercel. If FastAPI deploy fails, Angular deploy is skipped — the old Angular version continues calling the old API. This prevents Angular calling API endpoints that don't exist yet.

**Anti-Patterns:**
- `AP-S6.29a` — Deploying Angular before FastAPI when adding new API endpoints — Angular calls the new endpoint before it exists; users see 404 errors until FastAPI deploy completes.

**Cross-References:** `S8.16` (CI coordination standard), `S8.4` (preview deployments)

---

### S6.30–S6.33 — Additional Deployment Standards

> **S6.30** — Database migration runs before service start on every deployment (S5.59) — this applies to both stacks.

> **S6.31** — Preview deployments for Angular stack PRs that change the API update the Railway staging environment — the Angular preview deployment is tested against the staged FastAPI, not against production.

> **S6.32** — Rollback procedure per stack: Next.js — Vercel one-click rollback to previous deployment. Angular — Vercel rollback for frontend + Railway redeploy previous build for FastAPI + migration rollback if schema changed. Per runbooks.

> **S6.33** — Environment variable changes require coordination — an env var added to FastAPI that Angular reads must be deployed to both Railway Secrets and Vercel environment simultaneously.

---

## Part 7 — Tech Stack Reference (`S6.34`–`S6.38`)

The locked technology choices for both stacks. Deviations require an ADR and a constitutional amendment.

---

### S6.34 — Locked Technology Stack — Next.js Systems

| Layer | Technology | Governs |
|-------|-----------|---------|
| Frontend | Next.js 14+ App Router, React 18+, TypeScript strict | C4 |
| Styling | Tailwind CSS + Custom CSS Modules | C4 |
| Components | shadcn/ui as base library | C4 |
| State (server) | TanStack Query v5 | C4 |
| State (client) | Zustand v4 | C4 |
| Forms | React Hook Form + Zod | C4 |
| Auth | NextAuth.js v5 with Prisma Adapter | C3 |
| API | Next.js API Routes under `/api/v1/` | C2 |
| Database | PostgreSQL via Prisma ORM + Raw SQL | C5 |
| Background jobs | BullMQ + Redis (SyncUp) | C2 |
| Testing | Jest + RTL + Playwright | C7 |
| Deployment | Vercel | C8 |
| Monitoring | Sentry + Better Stack + Vercel Analytics | C8 |

---

### S6.35 — Locked Technology Stack — Angular+FastAPI Systems

| Layer | Technology | Governs |
|-------|-----------|---------|
| Frontend | Angular 17+ standalone, TypeScript strict | C4 |
| Styling | Tailwind CSS + Custom CSS (component styles) | C4 |
| State | Angular Signals + RxJS | C4 |
| Forms | Angular Reactive Forms | C4 |
| Auth (FE) | JWT in Angular memory + HTTP interceptor | C3 |
| Auth (BE) | FastAPI RS256 JWT issuance + Depends() | C3 |
| API | FastAPI (Python) under `/api/v1/` | C2 |
| Database (relational) | PostgreSQL via Prisma ORM + Raw SQL | C5 |
| Database (document) | MongoDB via Beanie ODM | C5 |
| Vector store | ChromaDB (FundsLink only) | C5 |
| AI pipeline | LangChain + Python (FundsLink only) | C2 |
| Background jobs | BullMQ + Redis (Reserve Bank) | C2 |
| Testing | Vitest + Angular utilities + Playwright + pytest | C7 |
| Deployment (FE) | Vercel | C8 |
| Deployment (BE) | Railway | C8 |
| Monitoring | Sentry + Better Stack + Railway Metrics | C8 |

---

### S6.36–S6.38 — Tech Stack Standards

> **S6.36** — New library additions require a PR comment explaining: why existing stack cannot solve the problem, bundle size impact, maintenance status, and constitutional compatibility. Libraries that introduce a second solution for a problem the locked stack already solves are rejected.

> **S6.37** — Technology version upgrades are handled as a dedicated sprint task — not as part of a feature PR. Major version upgrades require an ADR.

> **S6.38** — The tech stack reference table in this section is updated on every version upgrade of a locked technology — the document is the source of truth for what version is in use.

---

## Part 8 — Flagship System Register (`S6.39`–`S6.42`)

---

### S6.39 — FundsLink Academy

| Attribute | Value |
|-----------|-------|
| **Stack** | Angular + FastAPI |
| **Build Phase** | Phase 1 (Q2 2026 — Active) |
| **Primary Problem** | 342,000+ students excluded from education funding yearly |
| **Primary Workflow** | Student creates profile → submits application → receives AI-matched funding options |
| **v1 Done When** | A student can apply and receive at least one matched funding opportunity end-to-end |
| **Databases** | PostgreSQL + MongoDB + ChromaDB |
| **AI** | LangChain RAG pipeline, ChromaDB embeddings, eligibility matching |
| **ADR** | `adrs/ADR-001-fundslink-stack.md` |

---

### S6.40 — Maphophe Community System

| Attribute | Value |
|-----------|-------|
| **Stack** | Next.js |
| **Build Phase** | Phase 1 (Q3 2026) |
| **Primary Problem** | Rural villages have no digital governance infrastructure |
| **Primary Workflow** | Resident creates account → submits service request → ward admin reviews → resident sees status |
| **v1 Done When** | A resident can submit a service request and see its progress |
| **Databases** | PostgreSQL only |
| **ADR** | `adrs/ADR-002-maphophe-stack.md` |

---

### S6.41 — KSDRILL Reserve Bank

| Attribute | Value |
|-----------|-------|
| **Stack** | Angular + FastAPI |
| **Build Phase** | Phase 2 (Q4 2026) |
| **Primary Problem** | Most savings tools are passive — no discipline enforcement |
| **Primary Workflow** | User creates account → sets savings goal → makes first deposit → sees goal progress and projected interest |
| **v1 Done When** | A user can create an account, make a deposit, and see their balance and interest calculation |
| **Databases** | PostgreSQL + MongoDB + Redis |
| **ADR** | `adrs/ADR-003-reserve-bank-stack.md` |

---

### S6.42 — SyncUp Creator Platform

| Attribute | Value |
|-----------|-------|
| **Stack** | Next.js |
| **Build Phase** | Phase 3 (Q1 2027) |
| **Primary Problem** | Creators waste time in unstructured DM negotiations with no formal process |
| **Primary Workflow** | Creator discovers another creator → sends structured pitch → negotiation completes within 10 messages → outcome recorded |
| **v1 Done When** | A creator can send a pitch and receive a response through the structured negotiation flow |
| **Databases** | PostgreSQL + Redis (BullMQ for negotiation timers) |
| **ADR** | `adrs/ADR-004-syncup-stack.md` |

---

## Part 9 — Cross-Constitution Architecture Map (`S6.43`–`S6.44`)

---

### S6.43 — Constitution Interaction Map

This map shows which constitution governs each architectural concern. When building a feature, identify which concern it touches and read the relevant constitution.

| Concern | Constitution | Standard Range |
|---------|-------------|---------------|
| Stack assignment | C6 | S6.1–S6.7 |
| API contract design | C2 | S2.11–S2.22 |
| Authentication strategy | C3 | S3.1–S3.12 (NJ) / S3.13–S3.20 (ANG) |
| Token storage | C3 | S3.6 (NJ) / S3.14 (ANG) |
| Route protection | C3 + C4 | S3.7/S3.19 + S4.54 |
| Frontend state | C4 | S4.28–S4.45 |
| Form validation | C4 | S4.46–S4.51 |
| Database assignment | C5 | S5.1–S5.8 |
| ORM queries | C5 | S5.9–S5.18 |
| Raw SQL queries | C5 | S5.19–S5.24 |
| Schema design | C5 | S5.25–S5.32 |
| Integration request flow | C6 | S6.18–S6.19 |
| Deployment order | C6 + C8 | S6.29 + S8.16 |
| Test strategy | C7 | S7.1–S7.6 |
| CI/CD pipeline | C8 | S8.9–S8.16 |
| Incident response | C8 | S8.17–S8.38 |
| Feature governance | C9 | S9.7–S9.13 |
| AI workflow | C10 | S10.1–S10.28 |

---

### S6.44 — MVP Build Checklist — Phase 1 Completion Gate

Before any Phase 2 work begins on a system, the following must be complete:

```
PHASE 1 COMPLETION GATE
[ ] Stack ADR committed to adrs/ and locked
[ ] System context file created in system-contexts/{system}-context.md
[ ] CONSTITUTION-INDEX.md created in project workspace (S10.4)
[ ] OpenAPI contract drafted for all v1 endpoints (S2.7)
[ ] Auth implementation complete and tested (C3)
[ ] Primary user workflow implemented end-to-end
[ ] All database schemas migrated (S5.9, S5.59)
[ ] All v1 API endpoints live and returning standard response shape (S2.19)
[ ] Angular HTTP interceptor tested with deduplication (S3.15, S7.12) — Angular only
[ ] Visual regression tests passing at 320/375/390px (S4.10, S7.19)
[ ] Coverage gate passing (S7.25)
[ ] Preview deployment functional and reviewed
```

---

## Anti-Patterns Index

| ID | Description | Violated Standard | Severity |
|----|-------------|-------------------|----------|
| `AP-S6.1a` | Content-driven platform built with Angular | S6.1 | Critical |
| `AP-S6.2a` | Financial precision system built with Next.js JavaScript | S6.2 | Critical |
| `AP-S6.3a` | `0.1 + 0.2` JavaScript for financial calculations | S6.3 | Critical |
| `AP-S6.4a` | LangChain via Node.js wrapper in Next.js | S6.4 | High |
| `AP-S6.6a` | New system started without ADR | S6.6 | Critical |
| `AP-S6.7a` | Stack changed mid-build without amendment | S6.7 | Critical |
| `AP-S6.8a` | External API integrated without ADR | S6.8 | Standard |
| `AP-S6.12a` | Browser calling FastAPI from Next.js system | S6.12 | Critical |
| `AP-S6.13a` | Angular component calling Next.js API routes | S6.13 | Critical |
| `AP-S6.14a` | Next.js system calling Angular stack FastAPI | S6.14 | Critical |
| `AP-S6.18a` | Auth check in service function instead of route handler | S6.18 | High |
| `AP-S6.19a` | Access token in localStorage in Angular flow | S6.19 | Critical |
| `AP-S6.29a` | Angular deployed before FastAPI on breaking API change | S6.29 | High |

---

## Cross-Constitution Dependency Map

**This constitution depends on:**
| Dependency | Reason |
|------------|--------|
| `C0 — Constitutional Order` | Amendment protocol, stack assignment summary (§10), conflict resolution |
| `C2 — Backend Constitution` | Service layer and API standards referenced in request flows |
| `C3 — Auth Constitution` | Auth flows are core to the request flow specifications here |
| `C4 — Frontend Constitution` | Frontend behaviour in request flows depends on C4 standards |
| `C5 — Database Constitution` | Database access patterns referenced in both stack topologies |

**The following constitutions depend on this one:**
| Dependent | Reason |
|-----------|--------|
| `C7 — Testing Constitution` | Testing per stack references integration topology defined here |
| `C8 — Platform Reliability` | Deployment coordination and rollback procedures reference stack topology |

---

## Amendment Log

| Version | Date | Change | Reason |
|---------|------|--------|--------|
| v1.0 | 2026-05-08 | Initial lock — rebuilt from Full System Design v2.0 + Full-Stack Integration Constitution v1.0. localStorage token storage regression fixed in S6.19 (access token: Angular memory, not localStorage). ADR process formalised in Part 2. Stack assignment framework formalised as S6.1–S6.7. Request flows updated to reflect v1.0 standard IDs. Tech stack tables consolidated. | Full system rebuild — two documents merged into one authoritative source. |

---

> **LOCKED — v1.0 — 2026-05-08**
>
> This document is locked. No standard may be added, removed, or modified
> without following the Amendment Protocol defined in C0 §8.
> Amendments take effect only after commit to `system-design-template`
> with a version bump and amendment log entry.
