# CONSTITUTION-INDEX — {System Name}

> **This file is required in every project workspace before any Claude Code (Cursor) build session begins.**
> **Per S10.21 — load this file into Cursor context at the start of every session.**
> **Per S10.23 — update this file at the start of every sprint.**

---

| Attribute        | Value |
|------------------|-------|
| **System**       | {FundsLink Academy / Maphophe Community / KSDRILL Reserve Bank / SyncUp Creator Platform} |
| **Stack**        | Angular + FastAPI / Next.js |
| **Build Phase**  | Phase {N} — {description} |
| **Active Group** | G{N} — {Group 1: Core / Group 2: Supporting} |
| **Operating Mode** | SOLO / TEAM |
| **Overlay**      | `solo-dev-overlay.md` / `team-overlay.md` |
| **Last Updated** | {YYYY-MM-DD} |
| **Sprint**       | Sprint {N} — {goal} |

---

## Active Feature

**Feature:** {feature name}
**Proposal:** GitHub Issue #{N}
**Layers completed:** Interface ✅ / Service ⬜ / Component ⬜ / UI ⬜
**Branch:** `feat/{feature-name}`

---

## Critical Standards for This Session

> List the 15–20 most relevant standards for this system's current build phase and active feature.
> Use `indexes/standards-index.md` to find IDs. Not all 300+ — the focused, actionable set.

### Security — Always Active (C3)

| Standard | What It Governs | Why Critical Now |
|----------|----------------|-----------------|
| `S3.1` | One auth strategy per system — stack determines strategy | Stack is locked — never deviate |
| `S3.14` | **Access token in Angular memory — NEVER localStorage** | Angular stack — CF-01 if violated |
| `S3.15` | HTTP interceptor with refresh deduplication | Interceptor under build / active |
| `S3.22` | Ownership verification on every user-owned resource | Every protected endpoint |

### Database — Always Active (C5)

| Standard | What It Governs | Why Critical Now |
|----------|----------------|-----------------|
| `S5.3` | **Financial data in PostgreSQL only — never MongoDB** | Reserve Bank / FundsLink financial data |
| `S5.11` | Explicit `select` on every Prisma query | Every DB read |
| `S5.12` | `deleted_at: null` filter on all queries | Every DB query |
| `S5.15` | Transactions for multi-step writes | Any write touching >1 table |
| `S5.21` | **Raw SQL always parameterised — never string-interpolated** | Any raw SQL in this feature |
| `S5.28` | **Decimal columns for monetary values — never Float** | Financial system only |

### Backend — Current Feature (C2)

| Standard | What It Governs | Why Critical Now |
|----------|----------------|-----------------|
| `S2.1` | Business logic in service layer only | Every endpoint |
| `S2.7` | OpenAPI contract before endpoint code | New endpoints in this feature |
| `S2.19` | Standard response shape `{ success, data, error }` | Every API response |
| `S2.23` | Zod/Pydantic validation on every API boundary | Every input |

### Frontend — Current Feature (C4)

| Standard | What It Governs | Why Critical Now |
|----------|----------------|-----------------|
| `S4.13` | Tailwind for layout and responsive utilities | All styling |
| `S4.14` | Custom CSS for brand identity | Brand-specific visual work |
| `S4.53` | OnPush change detection — all Angular components | Every component |
| `S4.55` | Angular services for all API calls | No HTTP in components |
| `S4.79` | **Layer build order: Interface → Service → Component → UI** | Active feature build |
| `S4.80` | One commit per layer | Git discipline |

### Testing — Always Active (C7)

| Standard | What It Governs | Why Critical Now |
|----------|----------------|-----------------|
| `S7.1` | Tests written alongside code — same PR | Every layer |
| `S7.7` | Every service function has a unit test | Service layer under build |
| `S7.11` | Auth tests: 200, 401, 403 per protected endpoint | Any new endpoints |

---

## Approved Deviations (ADRs)

> List any approved constitutional deviations for this system. If none, leave empty.

| Standard | Deviation | ADR Reference | Approved Alternative |
|----------|-----------|---------------|---------------------|
| — | No approved deviations at v1.0 | — | — |

---

## Current Sprint — Commit Log

> Track layer commits for the active feature. Update as each layer is committed.

| Layer | Commit Hash | Commit Message | Status |
|-------|-------------|----------------|--------|
| Interface / Types | — | `feat(types): add {feature} interfaces` | ⬜ |
| Service layer | — | `feat(service): add {feature} service` | ⬜ |
| Smart component | — | `feat(component): add {feature} container` | ⬜ |
| UI / Presentational | — | `feat(ui): add {feature} presentational components` | ⬜ |
| Tests | — | `test({feature}): add unit and integration tests` | ⬜ |

---

## Critical Anti-Patterns for This System

> The 5–8 most dangerous anti-patterns given this system's stack and current phase.

### Angular + FastAPI (FundsLink / Reserve Bank)

| AP | What It Looks Like | Consequence |
|----|-------------------|-------------|
| `AP-S3.14a` | `localStorage.setItem('access_token', token)` | XSS vulnerability — CF-01 |
| `AP-S5.3a` | Financial data written to MongoDB collection | No ACID — CF-03 — SEV0 |
| `AP-S5.21a` | `` `SELECT * FROM users WHERE id = '${userId}'` `` | SQL injection |
| `AP-S5.21b` | `f"SELECT * FROM accounts WHERE id = '{account_id}'"` | SQL injection (Python) |
| `AP-S4.53a` | `changeDetection: ChangeDetectionStrategy.Default` | Performance degradation at scale |
| `AP-S4.55a` | `this.http.get('/api/...')` inside Angular component | Untestable, untraceable |
| `AP-S6.29a` | Angular Vercel deployed before FastAPI Railway on breaking change | 404 errors on new endpoints |

### Next.js (Maphophe / SyncUp)

| AP | What It Looks Like | Consequence |
|----|-------------------|-------------|
| `AP-S3.6a` | `localStorage.setItem('session', token)` | XSS vulnerability — CF-01 |
| `AP-S3.5a` | `session: { strategy: 'jwt' }` in NextAuth | Unrevocable sessions |
| `AP-S4.28a` | `useState(null) + useEffect(() => fetch(...))` | No loading/error/cache |
| `AP-S5.11a` | `prisma.user.findMany()` without `select` | Exposes password_hash |
| `AP-S5.15a` | Sequential writes without `prisma.$transaction()` | Partial write corruption |
| `AP-S2.7a` | Endpoint coded before OpenAPI contract written | Frontend blocked — CF-11 |

---

## Open Issues

> Track anything that needs Founder attention or constitutional review.

| Issue | Type | Status |
|-------|------|--------|
| — | — | — |

---

## Relay Status

| Step | Engineer | Status | Handoff Report |
|------|----------|--------|----------------|
| Design | Claude | ⬜ / ✅ | GitHub Issue #{N} |
| Build | Claude Code | ⬜ / ✅ | — |
| Debug/Style | ChatGPT | ⬜ / ✅ | — |
| Logic (if needed) | DeepSeek | ⬜ / N/A | — |
| Experiment (if needed) | Kimi | ⬜ / N/A | — |

---

> *Update this file at the start of every sprint and every session.*
> *Per S10.21 — Claude Code does not begin without this file loaded in Cursor.*
> *Per S10.23 — A stale index is equivalent to no index.*
