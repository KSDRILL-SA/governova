# Phase 1 — Core Architecture

**Read before: the first line of application code.**

> If Phase 1 is skipped, the system has no architectural boundaries, no auth strategy,
> no database assignment, no frontend governance. The first endpoint embeds patterns
> that corrupt every endpoint that follows it.

## Contents

| File | Constitution | Governs |
|------|--------------|---------|
| `C02-backend-constitution.md` | Backend | Service architecture, API contracts, OpenAPI-first, performance, resilience, security middleware |
| `C03-auth-constitution.md` | Auth | Auth strategy, JWT lifecycle, RBAC, OAuth, session management, security baseline |
| `C04-frontend-constitution.md` | Frontend | Frontend architecture, mobile-first, state management, group-build methodology |
| `C05-database-constitution.md` | Database | Database assignment by data type, cross-database integrity, migration governance |
| `C06-fullstack-architecture-constitution.md` | Full-Stack Architecture | System topology, dual-stack assignment, request flows, cross-stack communication |

## Note on implementation guides
C02, C03, C04, C05 each have a paired implementation guide.
Implementation guides live in `constitution/implementation/` — not here.
Read the constitution first, then the implementation guide for your stack.
