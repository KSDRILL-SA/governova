# Anti-Patterns Index — KSDRILL SA Constitutional System

> **Quick violation reference.** Use this index to identify constitutional violations during code review, AI review sessions, and post-mortems.

---

## How to Read This Index

| Column | Meaning |
|--------|---------|
| **ID** | Anti-pattern identifier — cite in reviews and post-mortems |
| **Anti-Pattern** | What the violation looks like |
| **Violated Standard** | The standard being broken |
| **Severity** | Build impact if not corrected |
| **CF** | Common Failure Register entry if this is a known failure mode |

---

## C1 — Engineering Standards

| ID | Anti-Pattern | Violated Standard | Severity |
|----|-------------|-------------------|----------|
| `AP-S1.4a` | Stack changed mid-build without constitutional amendment | S1.4 | Critical |
| `AP-S1.T16a` | Direct push to main bypassing PR | S1.16 | Critical |
| `AP-S1.27a` | Feature built without a proposal | S1.27 | High |
| `AP-S1.45a` | PR opened without completing self-review checklist | S1.45 | High |
| `AP-S1.Q2a` | `any` type used in TypeScript production code | S1.48 | High |

---

## C2 — Backend Constitution

| ID | Anti-Pattern | Violated Standard | Severity | CF |
|----|-------------|-------------------|----------|----|
| `AP-S2.1a` | Business logic in API route handler instead of service layer | S2.1 | Critical | — |
| `AP-S2.2a` | Angular browser calling FastAPI directly, bypassing Next.js proxy | S2.2 | Critical | CF-08 |
| `AP-S2.7a` | Endpoint implemented before OpenAPI contract written | S2.7 | Critical | CF-11 |
| `AP-S2.13a` | Raw SQL bypassing Prisma for standard operations without comment | S2.28 | High | CF-02 |
| `AP-S2.19a` | Non-standard response shape — not `{ success, data, error }` | S2.19 | High | — |
| `AP-S2.22a` | Unbounded list response without pagination | S2.19 | High | — |
| `AP-S2.23a` | API boundary without Zod/Pydantic validation | S2.23 | Critical | — |
| `AP-S2.49a` | CORS wildcard `*` in production | S2.49 | Critical | — |
| `AP-S2.55a` | Secret committed to version control | S2.55 | Critical | CF-04 |

---

## C3 — Auth Constitution

| ID | Anti-Pattern | Violated Standard | Severity | CF |
|----|-------------|-------------------|----------|----|
| `AP-S3.1a` | NextAuth.js in an Angular+FastAPI system | S3.1 | Critical | — |
| `AP-S3.2a` | Session data stored in MongoDB | S3.2 | Critical | CF-07 |
| `AP-S3.3b` | SHA-256 for password storage | S3.3 | Critical | — |
| `AP-S3.5a` | `session: { strategy: "jwt" }` in NextAuth | S3.5 | Critical | — |
| `AP-S3.6a` | NextAuth session token in localStorage | S3.6 | Critical | CF-01 |
| `AP-S3.7a` | Middleware-only auth without independent API route verification | S3.7 | Critical | — |
| `AP-S3.13a` | HS256 instead of RS256 for JWT | S3.13 | Critical | — |
| **`AP-S3.14a`** | **Access token in localStorage (Angular)** | **S3.14** | **Critical** | **CF-01** |
| `AP-S3.15a` | Refresh without concurrent request deduplication | S3.15 | Critical | — |
| `AP-S3.16a` | Refresh rotation without replay detection | S3.16 | Critical | — |
| `AP-S3.19a` | Angular route guard treated as security boundary | S3.19 | Critical | — |
| `AP-S3.20a` | `.env` with actual secret values committed | S3.20 | Critical | CF-04 |
| `AP-S3.21a` | Hardcoded role string `=== "admin"` | S3.21 | High | — |
| `AP-S3.22a` | Role check without ownership verification | S3.22 | Critical | — |
| `AP-S3.29a` | CORS wildcard `*` in production | S3.29 | Critical | — |
| `AP-S3.30a` | "Email not found" distinguishable from "Link sent" on reset | S3.30 | High | — |
| `AP-S3.33b` | AuditLog table with `deleted_at` column | S3.33 | Critical | — |
| `AP-S3.35a` | Sessions survive password change | S3.35 | Critical | — |

---

## C4 — Frontend Constitution

| ID | Anti-Pattern | Violated Standard | Severity |
|----|-------------|-------------------|----------|
| `AP-S4.2a` | `hidden md:block` on primary content | S4.2 | High |
| `AP-S4.4a` | API call inside a presentational component | S4.4 | Critical |
| `AP-S4.7a` | `height: 100vh` on hero sections (iOS breaks) | S4.7 | High |
| `AP-S4.10a` | Visual regression CI at 1280px only | S4.10 | High |
| `AP-S4.11a` | Blank rendering during in-flight requests | S4.11 | High |
| `AP-S4.12a` | Business logic in UI components | S4.12 | Critical |
| `AP-S4.14a` | Brand colours via Tailwind `arbitrary values` `bg-[#hex]` | S4.14 | High |
| `AP-S4.14b` | Custom CSS for layout concerns Tailwind covers | S4.14 | Standard |
| `AP-S4.15a` | Both Tailwind and custom CSS defining same property | S4.15 | High |
| `AP-S4.18a` | Icon button with 16px tap target | S4.18 | Critical |
| `AP-S4.19a` | `*:focus { outline: none }` in global CSS | S4.19 | Critical |
| `AP-S4.21a` | Low-contrast text for aesthetics | S4.21 | Critical |
| `AP-S4.25a` | API response used without Zod validation | S4.25 | Critical |
| `AP-S4.28a` | `useState` + `useEffect` for server state | S4.28 | Critical |
| `AP-S4.46a` | `useState` per field for form state | S4.46 | Critical |
| `AP-S4.47a` | `[(ngModel)]` template-driven form | S4.47 | Critical |
| `AP-S4.53a` | `ChangeDetectionStrategy.Default` on Angular component | S4.53 | Critical |
| `AP-S4.54a` | Angular route guard treated as security boundary | S4.54 | Critical |
| `AP-S4.55a` | `HttpClient` calls directly in Angular component | S4.55 | Critical |
| `AP-S4.79a` | UI-first layer build order | S4.79 | Critical |
| `AP-S4.79b` | One giant commit for all four layers | S4.79 | High |

---

## C5 — Database Constitution

| ID | Anti-Pattern | Violated Standard | Severity | CF |
|----|-------------|-------------------|----------|----|
| **`AP-S5.1a`** | **Financial data in MongoDB** | **S5.1** | **Critical** | **CF-03** |
| `AP-S5.2a` | MongoDB document created before PostgreSQL entity | S5.2 | High | — |
| `AP-S5.3a` | `deposits_collection` in MongoDB with financial fields | S5.3 | Critical | CF-03 |
| `AP-S5.4a` | Session/auth table in MongoDB | S5.4 | Critical | CF-07 |
| `AP-S5.7a` | Prisma client in Next.js client component | S5.7 | Critical | — |
| `AP-S5.9a` | `ALTER TABLE` run directly on database | S5.9 | Critical | — |
| `AP-S5.10a` | `@id @default(autoincrement())` integer IDs | S5.10 | High | — |
| `AP-S5.11a` | `prisma.user.findMany()` without `select` | S5.11 | Critical | — |
| `AP-S5.12a` | Balance query including soft-deleted records | S5.12 | Critical | — |
| `AP-S5.15a` | Sequential writes without `prisma.$transaction()` | S5.15 | Critical | — |
| `AP-S5.16a` | `new PrismaClient()` per request | S5.16 | High | — |
| `AP-S5.19a` | Raw SQL for simple WHERE clause Prisma handles cleanly | S5.19 | Standard | — |
| `AP-S5.19b` | Raw SQL without explanatory comment | S5.19 | Standard | — |
| **`AP-S5.21a`** | **`$queryRawUnsafe` with string interpolation (SQL injection)** | **S5.21** | **Critical** | — |
| **`AP-S5.21b`** | **f-string SQL in Python FastAPI** | **S5.21** | **Critical** | — |
| `AP-S5.22a` | Raw SQL without `deleted_at IS NULL` filter | S5.22 | Critical | — |
| `AP-S5.28a` | `Float` column type for monetary values | S5.28 | Critical | — |

---

## C6 — Full-Stack Architecture

| ID | Anti-Pattern | Violated Standard | Severity | CF |
|----|-------------|-------------------|----------|----|
| `AP-S6.1a` | Content-driven platform built with Angular | S6.1 | Critical | — |
| `AP-S6.2a` | Financial precision system with Next.js JavaScript | S6.2 | Critical | — |
| `AP-S6.3a` | `0.1 + 0.2` JavaScript for financial calculations | S6.3 | Critical | — |
| `AP-S6.6a` | New system started without ADR | S6.6 | Critical | — |
| `AP-S6.7a` | Stack changed mid-build without constitutional amendment | S6.7 | Critical | CF-12 |
| `AP-S6.12a` | Browser calling FastAPI from Next.js system | S6.12 | Critical | CF-08 |
| `AP-S6.13a` | Angular component calling Next.js API routes | S6.13 | Critical | — |
| `AP-S6.14a` | Next.js system calling Angular stack FastAPI | S6.14 | Critical | — |
| `AP-S6.19a` | Access token in localStorage in Angular request flow | S6.19 | Critical | CF-01 |
| `AP-S6.29a` | Angular deployed before FastAPI on breaking API change | S6.29 | High | — |

---

## C7 — Testing Constitution

| ID | Anti-Pattern | Violated Standard | Severity | CF |
|----|-------------|-------------------|----------|----|
| `AP-S7.1a` | Separate test tickets written after features | S7.1 | Critical | CF-10 |
| `AP-S7.2a` | Karma + Jasmine in Angular | S7.2 | Critical | — |
| `AP-S7.3a` | Asserting on private component property | S7.3 | High | — |
| `AP-S7.4a` | Shared mutable state between test cases | S7.4 | Critical | — |
| `AP-S7.10a` | Mocked Prisma client for integration tests | S7.10 | Critical | — |
| `AP-S7.11a` | Protected endpoint tested only for success | S7.11 | Critical | — |
| `AP-S7.12a` | No test for concurrent 401 deduplication | S7.12 | Critical | — |
| `AP-S7.16a` | `toMatchSnapshot()` for component testing | S7.16 | High | — |
| `AP-S7.17a` | Cypress in any KSDRILL SA project | S7.17 | High | — |
| `AP-S7.19a` | Visual regression at 1280px only | S7.19 | Critical | — |
| `AP-S7.38a` | Float comparison in financial calculation tests | S7.38 | Critical | — |
| `AP-S7.39a` | Staging database URL in integration tests | S7.39 | Critical | — |

---

## C8 — Platform Reliability

| ID | Anti-Pattern | Violated Standard | Severity | CF |
|----|-------------|-------------------|----------|----|
| `AP-S8.2a` | FastAPI deployed to Vercel serverless | S8.2 | Critical | — |
| `AP-S8.12a` | Automatic production deploy on main merge | S8.12 | Critical | CF-15 |
| `AP-S8.24a` | Staging and production share same database | S8.24 | Critical | — |
| `AP-S8.31a` | Unstructured plain-text logs in production | S8.31 | High | — |
| `AP-S8.77a` | No post-mortem after SEV0 | S8.77 | Critical | — |

---

## C9 — Product & Feature

| ID | Anti-Pattern | Violated Standard | Severity |
|----|-------------|-------------------|----------|
| `AP-S9.2a` | Admin dashboard before primary workflow complete | S9.2 | Critical |
| `AP-S9.3a` | Second system started before first MVP ships | S9.3 | Critical |
| `AP-S9.7a` | Gate questions skipped for "obviously needed" feature | S9.7 | Critical |
| `AP-S9.9a` | G3/G4 features added to v1 | S9.9 | Critical |
| `AP-S9.14a` | MVP declared done in staging | S9.14 | High |

---

## C10 — AI Collaboration

| ID | Anti-Pattern | Violated Standard | Severity |
|----|-------------|-------------------|----------|
| `AP-S10.1a` | "Claude said it's correct, we can start building" | S10.1 | Critical |
| `AP-S10.2a` | Cursor build session without CONSTITUTION-INDEX.md | S10.2 | Critical |
| `AP-S10.3a` | Same Claude session for proposal AND adversarial review | S10.3 | High |
| `AP-S10.6a` | AI session starts with tech question before AI-INSTRUCTIONS.md | S10.6 | High |
| `AP-S10.8a` | "Claude approved the security decision" | S10.8 | Critical |
| `AP-S10.14a` | AI output accepted as constitutional amendment | S10.14 | Critical |
| `AP-S10.15a` | Claude → Cursor directly, skipping adversarial review | S10.15 | Critical |
| `AP-S10.21a` | Build session started without CONSTITUTION-INDEX.md | S10.21 | Critical |
| `AP-S10.27a` | PR merged to main without AI code review documented | S10.27 | High |

---

## Common Failure Register Quick Reference

| CF ID | Failure | Severity | Constitution |
|-------|---------|----------|-------------|
| CF-01 | Access token in localStorage | SEV1 | C3 S3.14 |
| CF-02 | Raw SQL bypassing Prisma for standard operations | SEV2 | C5 S5.9 |
| CF-03 | Financial transaction data in MongoDB | SEV0 | C5 S5.3 |
| CF-04 | Direct push to main bypassing PR | SEV1 | C1 S1.16 |
| CF-05 | Feature built without proposal | SEV3 | C1 S1.27 |
| CF-06 | PR opened without self-review checklist | SEV3 | C1 S1.45 |
| CF-07 | Authentication data in MongoDB | SEV0 | C3 S3.2 |
| CF-08 | Angular browser calling FastAPI directly | SEV1 | C2 S2.2 |
| CF-09 | `any` type in TypeScript production code | SEV3 | C1 S1.48 |
| CF-10 | Tests written after the feature PR | SEV3 | C7 S7.1 |
| CF-11 | Endpoint implemented before OpenAPI contract | SEV2 | C2 S2.7 |
| CF-12 | Stack changed mid-build without amendment | SEV0 | C6 S6.7 |
| CF-13 | Database migration deployed after service started | SEV1 | C5 S5.59 |
| CF-14 | AI output accepted as constitutional amendment | SEV2 | C10 S10.8 |
| CF-15 | Production deploy without staging validation | SEV1 | C8 S8.12 |

---

*Last updated: v1.0 — 2026-05-08*
