# ADR-004 — SyncUp Creator Platform: Next.js Stack Assignment

---

| Attribute      | Value |
|----------------|-------|
| **ID**         | ADR-004 |
| **Date**       | 2026-05-08 |
| **Status**     | accepted |
| **Supersedes** | — |
| **Relates To** | `S6.1` (SEO-critical / content-driven) |

---

## Context

SyncUp Creator Platform is a structured collaboration platform for creators — template-based pitches, 10-message negotiation limits, privacy controls, and outcome recording. The platform requires:

1. **SEO and creator discovery** — creator profiles, collaboration outcomes, and platform reputation are discoverable through search. A creator searching "structured pitch platform South Africa" must find SyncUp. SSR for creator profile pages is a primary requirement.
2. **Content-driven creator profiles** — public creator profiles with portfolio work, pitch history, and collaboration outcomes are public-facing pages that benefit from SSR/SSG for performance and indexability.
3. **Real-time negotiation engine** — the 10-message negotiation flow uses WebSocket connections for real-time message delivery. Next.js with BullMQ handles negotiation timer management (auto-close after 48h inactivity) natively.
4. **Media-rich pages** — creator portfolios with images and videos require Next.js's built-in image optimisation and lazy loading.
5. **Simple, focused data model** — PostgreSQL for all relational data, Redis for BullMQ negotiation queues. No Python AI pipeline, no MongoDB, no ChromaDB required at v1.
6. **Unified full-stack** — NextAuth sessions, API routes, and frontend in one Vercel deployment.

---

## Decision

**SyncUp Creator Platform is assigned to the Next.js stack.**

Next.js App Router SSR handles creator profile discoverability and media-rich pages natively. The 10-message negotiation engine is a core product feature, not a complexity justifying a separate backend. BullMQ + Redis on Vercel handles the negotiation timer jobs. The unified codebase keeps the operational footprint appropriate for the system's complexity.

The decision is immutable for the v1 lifetime of SyncUp.

---

## Consequences

### What becomes easier
- Creator profile SEO handled natively with SSR
- Next.js image optimisation for portfolio media
- NextAuth handles creator authentication with Google + GitHub OAuth (S3.26)
- Single Vercel deployment: zero Railway infrastructure
- BullMQ + Redis manages negotiation timers within the same deployment context

### What becomes harder
- If AI-powered creator matching is added post-v1, a new ADR must evaluate whether Python AI requirements justify migrating or adding a FastAPI service
- Complex negotiation state management requires careful TanStack Query design

### Constitutional alignment
- S6.1 — SEO-critical criteria met: public creator profiles, platform content, search discoverability
- C0 §10 — Stack assignment registered

---

## Alternatives Considered

| Option | Why Rejected |
|--------|-------------|
| Angular + FastAPI | No financial precision requirement. No Python AI requirement at v1. Two-deployment overhead not justified. Content-driven creator profiles clearly indicate Next.js. |
| Next.js + separate real-time service | Negotiation WebSockets can be handled within Next.js API routes. A separate service is over-engineering for v1's 10-message limit constraint. |

---

## Approved Deviations

*None — this system applies all constitutional standards without deviation at v1.0.*

**Future ADR trigger:**
If post-v1 roadmap includes AI-powered creator compatibility matching (NLP-based), a new ADR (ADR-005) must evaluate whether a FastAPI Python service is required, and whether it can be added alongside the existing Next.js stack without a constitutional amendment.

---

> **Status: accepted — 2026-05-08**
> *Owner approval: Maluleke Kurhula Success*
