# ADR-002 — Maphophe Community System: Next.js Stack Assignment

---

| Attribute      | Value |
|----------------|-------|
| **ID**         | ADR-002 |
| **Date**       | 2026-05-08 |
| **Status**     | accepted |
| **Supersedes** | — |
| **Relates To** | `S6.1` (SEO-critical / content-driven) |

---

## Context

Maphophe Community System is a village-level governance platform for South African rural communities — announcements, trackable service requests, ward reporting, and community voting. The platform requires:

1. **SEO and discoverability** — Community announcements, ward notices, and governance updates must be discoverable by search engines. Residents searching for ward news or service request status must find the platform through organic search. SSR is a primary requirement, not an optimisation.
2. **Content-driven public pages** — Announcements, public service request statuses, and ward reports are publicly readable without authentication. Next.js App Router SSR/SSG handles this natively.
3. **Low-bandwidth optimisation** — Rural South African users on mobile data connections with entry-level devices (320px viewport, limited JavaScript budget). Next.js's built-in image optimisation, static generation, and minimal JavaScript payload fit this constraint. This is a primary design constraint per `S9.5`.
4. **Simple relational data model** — PostgreSQL only. No document data, no vector embeddings, no AI pipeline. A dedicated Python backend is not justified.
5. **Unified full-stack codebase** — NextAuth, API routes, and the frontend in one Vercel deployment keeps the operational surface minimal for a solo developer.

---

## Decision

**Maphophe Community System is assigned to the Next.js stack.**

Next.js App Router with SSR/SSG handles the SEO and content-driven requirements natively. The unified full-stack model minimises operational complexity. PostgreSQL via Prisma is the only database — no MongoDB, no ChromaDB needed for this system's data model.

The decision is immutable for the v1 lifetime of Maphophe Community System.

---

## Consequences

### What becomes easier
- SEO handled natively by Next.js SSR without Angular Universal overhead
- Vercel deployment: single project, zero backend infrastructure to manage
- NextAuth database sessions: simpler than JWT, instant revocation
- Low-bandwidth performance: Next.js image optimisation and ISR serve cached pages instantly
- Solo developer operational footprint: one codebase, one deployment, one platform

### What becomes harder
- Complex form workflows require more custom React implementation than Angular Reactive Forms
- No native Python ecosystem if AI features are added later (would require ADR amendment)

### Constitutional alignment
- S6.1 — SEO-critical criteria met: public-facing community content, search discoverability required
- S9.5 — African context constraint: low-bandwidth rural users as primary user population
- C0 §10 — Stack assignment registered

---

## Alternatives Considered

| Option | Why Rejected |
|--------|-------------|
| Angular + FastAPI | No SEO capability without Angular Universal (additional complexity). No AI or financial precision requirements justify the two-deployment overhead. The content-driven model clearly points to Next.js. |
| Next.js + separate FastAPI | No Python requirements exist for this system at v1. The additional Railway service is unjustified overhead. |

---

## Approved Deviations

*None — this system applies all constitutional standards without deviation at v1.0.*

**Special requirement documented here (not a deviation — a design constraint):**
Lighthouse mobile score target is ≥ 85 for Maphophe (above the constitutional minimum of 80 per S4.69) to meet the low-bandwidth rural user requirement.

---

> **Status: accepted — 2026-05-08**
> *Owner approval: Maluleke Kurhula Success*
