# Standards Index — KSDRILL SA Constitutional System

> **Index-first navigation.** Find the standard ID here, then open the full constitution only when deep rationale is needed.

---

## C0 — Constitutional Order

| ID | Title | Priority |
|----|-------|----------|
| `C0 §2` | Terminology System — Standards, Anti-Patterns, Practices | — |
| `C0 §3` | Standard Format Specification — the universal S block | — |
| `C0 §7` | Constitutional Hierarchy & Conflict Resolution | — |
| `C0 §7.3` | Auth Override Rule — C3 beats all on security decisions | — |
| `C0 §8` | Amendment Protocol — solo and team | — |
| `C0 §10` | Stack Assignment Summary — locked system assignments | — |
| `C0 §11` | Pre-Build Constitutional Checklist | — |
| `C0 §13` | Common Failure Register (CF-01–CF-15) | — |

---

## C1 — Engineering Standards

| ID | Title | Priority |
|----|-------|----------|
| `S1.1` | Design first, then build | Critical |
| `S1.2` | Build what exists in a working state | Critical |
| `S1.3` | One system at a time | Critical |
| `S1.4` | Stack assignment is immutable | Critical |
| `S1.5` | Engineering is a discipline, not a craft | High |
| `S1.6–S1.10` | Sprint & Planning standards | High |
| `S1.11–S1.15` | Communication standards (standups, blockers, async) | Standard |
| `S1.16` | Branch protection — no direct push to main | Critical |
| `S1.17` | Conventional commits — type: scope: description | High |
| `S1.18–S1.24` | Git branching and sync procedures | High |
| `S1.25–S1.26` | Constitutional governance in process | Critical |
| `S1.27` | Feature lifecycle — 8-phase with gate checks | Critical |
| `S1.28–S1.30` | PR description, review assignment, 2-approval merge | Critical |
| `S1.31–S1.40` | Feature lifecycle phases 1–8 detail | High |
| `S1.41–S1.44` | Non-negotiable engineering standards (7 Laws) | Critical |
| `S1.45` | Author self-review checklist — 4 quadrants | Critical |
| `S1.46` | PR description template — all fields required | High |
| `S1.47` | Review response protocol | Standard |
| `S1.48–S1.56` | TypeScript standards — strict mode, no `any` | Critical |
| `S1.57–S1.63` | Python standards — type hints, Pydantic | High |
| `S1.64–S1.69` | File & module structure | Standard |
| `S1.70–S1.74` | Linting & formatting (ESLint, Prettier, Black) | High |
| `S1.75–S1.82` | Code review standards | High |
| `S1.83–S1.87` | Documentation standards | Standard |
| `S1.88–S1.92` | Angular-specific quality standards | Critical |
| `S1.93–S1.97` | Git recovery procedures | High |

---

## C2 — Backend Constitution

| ID | Title | Priority |
|----|-------|----------|
| `S2.1` | Business logic lives exclusively in the service layer | Critical |
| `S2.2` | Single API gateway — all requests through `/api/v1/` | Critical |
| `S2.3–S2.6` | Service layer architecture standards | Critical |
| `S2.7` | OpenAPI contract drafted before any endpoint code | Critical |
| `S2.8–S2.10` | Extension-first backend design | High |
| `S2.11–S2.18` | API contract & design (versioning, naming, methods) | Critical |
| `S2.19` | Standard response shape — `{ success, data, error }` | Critical |
| `S2.20–S2.22` | Response shape standards (pagination, error codes) | High |
| `S2.23` | Zod/Pydantic validation on every API boundary | Critical |
| `S2.24–S2.27` | Validation layer detail | High |
| `S2.28–S2.35` | Database access from backend (ORM + raw SQL) | Critical |
| `S2.36–S2.41` | Performance standards (N+1, caching, pagination) | High |
| `S2.42–S2.48` | Resilience & error handling (circuit breaker, retries) | Critical |
| `S2.49–S2.55` | Security standards (RBAC, SQL injection, secrets) | Critical |
| `S2.56–S2.62` | Observability (structured logs, Sentry, X-Request-ID) | High |
| `S2.63–S2.69` | FastAPI-specific standards | Critical |
| `S2.70–S2.75` | Next.js API Route standards | Critical |
| `S2.76–S2.80` | API versioning governance | High |

---

## C3 — Auth Constitution

| ID | Title | Priority |
|----|-------|----------|
| `S3.1` | One auth strategy per system, determined by stack | Critical |
| `S3.2` | All auth data in PostgreSQL — never MongoDB | Critical |
| `S3.3` | bcrypt at minimum cost factor 12 | Critical |
| `S3.4` | Three-layer rate limiting on all auth endpoints | Critical |
| `S3.5` | NextAuth database sessions — never JWT sessions (Next.js) | Critical |
| `S3.6` | HttpOnly session cookies — never localStorage (Next.js) | Critical |
| `S3.7` | Middleware-based route protection + independent API verification | Critical |
| `S3.8` | Session callback — safe fields only | High |
| `S3.9` | Session lifetime — environment configurable | Standard |
| `S3.10` | OAuth through NextAuth exclusively | Critical |
| `S3.11` | CSRF protection never disabled | Critical |
| `S3.12` | Email verification — configurable mode, 24h expiry | High |
| `S3.13` | RS256-signed JWT issued by FastAPI | Critical |
| **`S3.14`** | **Split token storage — refresh in cookie, access in Angular MEMORY** | **Critical** |
| `S3.15` | HTTP interceptor with refresh deduplication | Critical |
| `S3.16` | Refresh rotation with replay detection | Critical |
| `S3.17` | FastAPI Depends() for JWT validation | High |
| `S3.18` | Logout — revoke, deny-list, BroadcastChannel all tabs | High |
| `S3.19` | Angular route guards — UX only, server is authoritative | Standard |
| `S3.20` | Secrets in Railway Secrets exclusively | Critical |
| `S3.21` | Roles as database enums — never string literals | Critical |
| `S3.22` | Ownership verification on every user-owned resource | Critical |
| `S3.23` | Authorisation at route entry — not in business logic | High |
| `S3.24` | Least privilege default — minimum role on account creation | High |
| `S3.25` | Role change audit trail — immutable history | High |
| `S3.26` | OAuth provider configuration — database-backed | Standard |
| `S3.27` | Institutional email domain validation | Standard |
| `S3.28` | HTTPS only in production, HSTS enforced | Critical |
| `S3.29` | CORS locked to known origins — no wildcard in production | Critical |
| `S3.30` | Password reset — time-limited, single-use, enumeration-proof | High |
| `S3.31` | Security headers on all responses | High |
| `S3.32` | Password strength validation and breach detection | Standard |
| `S3.33` | Universal auth event logging — every event, every system | Critical |
| `S3.34` | Security alerts on threat indicators | High |
| `S3.35` | Session invalidation on password change — all devices | Critical |
| `S3.36` | Cross-constitution review — auth changes need multi-layer review | Critical |

---

## C4 — Frontend Constitution

| ID | Title | Priority |
|----|-------|----------|
| `S4.1` | Framework assignment determined by stack | Critical |
| `S4.2` | Mobile-first baseline — 320px mandatory | Critical |
| `S4.3` | One adaptive system — never two separate builds | Critical |
| `S4.4` | Smart/container and presentational component separation | Critical |
| `S4.5` | Brand always visible — minimum 20px logo | Critical |
| `S4.6` | Navigation — horizontal desktop, structured mobile | Critical |
| `S4.7` | Hero sections use min-height, never fixed height | High |
| `S4.8` | Sticky headers shrink on scroll | High |
| `S4.9` | No page-level horizontal scroll | High |
| `S4.10` | Visual regression tests at 320/375/390px on every UI PR | Critical |
| `S4.11` | Async state has three states: loading, error, success | Critical |
| `S4.12` | No business logic in UI components | Critical |
| `S4.13` | **Tailwind for layout, spacing, and responsive utilities** | Critical |
| `S4.14` | **Custom CSS for brand identity and complex visual patterns** | Critical |
| `S4.15` | No duplication between Tailwind and custom CSS | High |
| `S4.16` | Design tokens as CSS custom properties | High |
| `S4.17` | No emojis in UI code — Lucide icons first | High |
| `S4.18` | Touch targets — 44×44px mobile, 32×32px desktop | Critical |
| `S4.19` | Full keyboard accessibility | Critical |
| `S4.20` | Body text minimum 16px | High |
| `S4.21` | WCAG 2.1 AA colour contrast — 4.5:1 | Critical |
| `S4.22` | Respect `prefers-reduced-motion` | High |
| `S4.23` | ARIA labels on icon-only interactive elements | High |
| `S4.24` | Skeleton loaders preferred over spinners | Standard |
| `S4.25` | Zod validation on every API response (Next.js) | Critical |
| `S4.26` | Angular validators on all API responses | Critical |
| `S4.27` | No `console.log` in production | High |
| `S4.28` | TanStack Query for server state (Next.js) | Critical |
| `S4.29` | Zustand for client state (Next.js) | High |
| `S4.30` | Angular Signals for reactive state | Critical |
| `S4.46` | React Hook Form + Zod for all forms (Next.js) | Critical |
| `S4.47` | Angular Reactive Forms — no template-driven | Critical |
| `S4.48` | Client-side validation is UX, server-side is authoritative | Critical |
| `S4.52` | Standalone components preferred (Angular) | High |
| `S4.53` | OnPush change detection on all components (Angular) | Critical |
| `S4.54` | Angular route guards — UX only (per C3) | Standard |
| `S4.55` | Angular services for all API calls — no HTTP in components | Critical |
| `S4.56` | Vitest for Angular unit tests — never Karma | Critical |
| `S4.65` | Sentry frontend integration | Critical |
| `S4.66` | Error boundaries on every route | High |
| `S4.71` | Feature groups define build sequence | Critical |
| `S4.79` | **Layer build order: Interface → Service → Component → UI** | Critical |
| `S4.80` | One commit per layer | High |

---

## C5 — Database Constitution

| ID | Title | Priority |
|----|-------|----------|
| `S5.1` | Three-database separation — one purpose per type | Critical |
| `S5.2` | PostgreSQL is the system of record | Critical |
| `S5.3` | **Financial data in PostgreSQL only — never MongoDB** | Critical |
| `S5.4` | Authentication data in PostgreSQL only | Critical |
| `S5.5` | Cross-database references use PostgreSQL cuid | Critical |
| `S5.6` | Database selection documented at design time | High |
| `S5.7` | No direct database access from frontend | High |
| `S5.8` | Soft delete on all databases — never hard delete | High |
| `S5.9` | Prisma schema is the single source of truth | Critical |
| `S5.10` | Required fields on every table (id, created_at, updated_at, deleted_at) | Critical |
| `S5.11` | No SELECT * — explicit select on every Prisma query | Critical |
| `S5.12` | All queries filter `deleted_at: null` by default | Critical |
| `S5.13` | Foreign key indexes on every FK field | Critical |
| `S5.14` | Pagination on all list queries — no unbounded results | Critical |
| `S5.15` | Transactions for multi-step writes | Critical |
| `S5.16` | Prisma singleton client | High |
| `S5.17` | Prisma-generated TypeScript types — never cast | High |
| `S5.18` | Beanie ODM for all MongoDB access (Angular) | Critical |
| `S5.19` | **Raw SQL for complex queries ORM cannot express cleanly** | Standard |
| `S5.20` | Raw SQL wrapped in transactions for multi-step operations | Critical |
| `S5.21` | **Raw SQL always parameterised — never string-interpolated** | Critical |
| `S5.22` | Raw SQL must apply soft delete filter — no implicit bypass | Critical |
| `S5.23` | Raw SQL results validated with TypeScript/Pydantic types | High |
| `S5.24` | Raw SQL isolated in dedicated query functions | Standard |
| `S5.25` | Indexes on all query-critical fields | High |
| `S5.27` | PostgreSQL enums for constrained value sets | High |
| `S5.28` | **Decimal columns for monetary values — never Float** | Critical |
| `S5.33` | MongoDB for document data only — defined exclusions apply | Critical |
| `S5.45` | ChromaDB for vector similarity only | Critical |
| `S5.59` | Migrations run before service starts | Critical |

---

## C6 — Full-Stack Architecture Constitution

| ID | Title | Priority |
|----|-------|----------|
| `S6.1` | SEO-critical systems → Next.js | Critical |
| `S6.2` | Enterprise dashboards / financial precision → Angular+FastAPI | Critical |
| `S6.3` | Financial calculations require Python FastAPI | Critical |
| `S6.4` | Python AI (LangChain/RAG) → Angular+FastAPI | Critical |
| `S6.5` | Simple systems — either stack, ADR required | Standard |
| `S6.6` | Every new system requires ADR | Critical |
| `S6.7` | Stack assignment is immutable | Critical |
| `S6.8` | Every significant architectural decision requires ADR | High |
| `S6.12` | Next.js stack topology | Critical |
| `S6.13` | Angular+FastAPI stack topology | Critical |
| `S6.14` | Two stacks never share services | Critical |
| `S6.18` | Next.js authenticated request flow | Critical |
| `S6.19` | Angular+FastAPI authenticated request flow | Critical |
| `S6.29` | Angular deploy order: FastAPI first, Angular second | Critical |
| `S6.34` | Locked technology stack — Next.js | Reference |
| `S6.35` | Locked technology stack — Angular+FastAPI | Reference |

---

## C7 — Testing Constitution

| ID | Title | Priority |
|----|-------|----------|
| `S7.1` | Tests written alongside code — never after | Critical |
| `S7.2` | Test runner locked by stack — cannot be mixed | Critical |
| `S7.3` | Test the behaviour, not the implementation | Critical |
| `S7.4` | Tests are independent — no shared mutable state | Critical |
| `S7.5` | Test names describe behaviour in plain English | High |
| `S7.6` | Critical paths on every PR, full suite nightly | High |
| `S7.7` | Every service function has a unit test | Critical |
| `S7.8` | Angular: TestBed + fixture assertions | Critical |
| `S7.9` | Next.js: RTL — no Enzyme | Critical |
| `S7.10` | API integration tests use real test database | Critical |
| `S7.11` | Auth routes tested for authenticated and unauthenticated states | Critical |
| `S7.12` | Angular HTTP interceptor tests with deduplication | Critical |
| `S7.13` | Mocks reset between tests | High |
| `S7.14` | MSW for API mocking in Next.js | High |
| `S7.15` | Cross-database write operations have integration tests | High |
| `S7.16` | No snapshot tests — explicit assertions only | High |
| `S7.17` | Playwright for E2E — both stacks | Critical |
| `S7.18` | E2E covers every critical path | Critical |
| `S7.19` | Visual regression at 320/375/390px | Critical |
| `S7.20` | axe-core accessibility CI gate | High |
| `S7.25` | Coverage gates — Next.js 70%, Angular 75%, Python 80% | Critical |
| `S7.31` | pytest + pytest-asyncio for all FastAPI tests | Critical |
| `S7.38` | Financial calculation tests use Decimal not float | Critical |
| `S7.39` | Separate test database — never test against production | Critical |

---

## C8 — Platform Reliability Constitution

| ID | Title | Priority |
|----|-------|----------|
| `S8.1` | Vercel for all Next.js deployments | Critical |
| `S8.2` | Railway for FastAPI — never Vercel serverless | Critical |
| `S8.3` | Angular frontend on Vercel — separate from FastAPI | Critical |
| `S8.5` | Three environments — Development, Staging, Production | Critical |
| `S8.6` | Zero-downtime deploys | Critical |
| `S8.9` | GitHub Actions for all CI | Critical |
| `S8.10` | CI runs in under 5 minutes | Critical |
| `S8.11` | Automatic staging deploy on main merge | Critical |
| `S8.12` | Production deploy is manual and gated | Critical |
| `S8.17` | `docker-compose up` — full stack in one command | Critical |
| `S8.24` | Three isolated environments (separate databases) | Critical |
| `S8.31` | Structured JSON logging — mandatory fields | Critical |
| `S8.32` | Sentry for error tracking — frontend and backend | Critical |
| `S8.33` | Better Stack uptime monitoring — 60-second checks | High |
| `S8.47` | Severity framework — SEV0/SEV1/SEV2/SEV3 definitions | Reference |
| `S8.48` | Every incident classified within 5 minutes | Critical |
| `S8.49` | SEV0: restore first, investigate second | Critical |
| `S8.50` | Reserve Bank financial incidents are automatic SEV0 | Critical |
| `S8.67–S8.72` | Rollback procedures | Critical |
| `S8.77` | Post-mortem required for all SEV0/SEV1 | Critical |

---

## C9 — Product & Feature Constitution

| ID | Title | Priority |
|----|-------|----------|
| `S9.1` | Every platform solves a real problem felt by real people | Critical |
| `S9.2` | The primary user workflow is sacred | Critical |
| `S9.3` | Sequential build — one system fully before next | Critical |
| `S9.4` | Design-first — architecture locked before first line of code | Critical |
| `S9.5` | African context is a design constraint | High |
| `S9.7` | 5 gate questions — every feature must pass all five | Critical |
| `S9.8` | Feature groups — G1/G2/G3/G4 classification | Critical |
| `S9.9` | v1 contains maximum 6 features | Critical |
| `S9.10` | Feature flags for all features beyond initial v1 | Critical |
| `S9.14` | MVP done = primary workflow in production | Critical |

---

## C10 — AI Collaboration Constitution

| ID | Title | Priority |
|----|-------|----------|
| `S10.1` | Primary Architect (Claude) — proposes, cannot approve | Critical |
| `S10.2` | Builder (Cursor) — implements approved designs only | Critical |
| `S10.3` | Devil's Advocate — challenges primary proposals | High |
| `S10.6` | Every AI session reads AI-INSTRUCTIONS.md first | Critical |
| `S10.8` | **L4 Approval is human-only. Always.** | Critical |
| `S10.9–10.14` | L1/L2/L3/L4 permission boundary definitions | Critical |
| `S10.15` | Design phase three-step protocol | Critical |
| `S10.21` | CONSTITUTION-INDEX.md required in every project | Critical |
| `S10.22` | CONSTITUTION-INDEX.md required sections | Critical |
| `S10.27` | AI as second code reviewer in solo mode | Critical |

---

*Last updated: v1.0 — 2026-05-08*
