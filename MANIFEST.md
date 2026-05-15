# KSDRILL SA — Repository Manifest

> **This is the AI navigation spine. Read this file once to understand the complete repo
> structure, every file's purpose, its cluster, and the exact reading order for any session
> type. No searching required.**

---

## How to Use This Manifest

- **Quick session startup**: follow the [Session Reading Order](#session-reading-order) table top-to-bottom — stop at the row that matches your task
- **Cluster navigation**: files that belong together are grouped in the [File Clusters](#file-clusters) section — read all files in a cluster before moving to the next
- **Full repo scan**: use the [Complete File Index](#complete-file-index) — every file, one line, no omissions

---

## Session Reading Order

| Step | File | When to Stop Here |
|------|------|-------------------|
| **1** | `AI-INSTRUCTIONS.md` | Every session. No exception. Read this first. |
| **2** | `system-contexts/{system}-context.md` | Before any build session on a specific system |
| **3** | `workflow/ksdrill-sa-ai-workflow.md` | When confirming relay position or handoff protocol |
| **4** | `indexes/quick-reference.md` | When navigating a specific concern (auth, database, deploy) |
| **5** | `indexes/standards-index.md` | When auditing standards compliance or finding a standard ID |
| **6** | `indexes/anti-patterns-index.md` | When checking for known violation patterns |
| **7** | `constitutions/C0-constitutional-order.md` | First onboarding, or when a constitutional conflict arises |
| **8** | Constitution cluster for today's domain *(see clusters below)* | Before any code in that domain |
| **9** | Implementation guide in the same cluster | When writing code in that domain |

---

## File Clusters

Clusters group every file that belongs together. Read the whole cluster before switching to another cluster. Implementation guides are always read alongside their paired constitution — never in isolation.

---

### Cluster 0 — Session Entry (Read Every Session)

| File | Purpose |
|------|---------|
| `AI-INSTRUCTIONS.md` | AI role definitions, permission levels, session startup protocol, navigation hierarchy, citation format |
| `MANIFEST.md` | This file. Complete repo map. |

---

### Cluster 1 — Governance Root

| File | Purpose |
|------|---------|
| `constitutions/C0-constitutional-order.md` | Master document. Governs all other constitutions. Terminology, hierarchy, amendment protocol, common failure register. |

---

### Cluster 2 — Engineering Standards (Phase 0)

| File | Purpose |
|------|---------|
| `constitutions/C1-engineering-standards.md` | 97 standards governing how work is done: feature lifecycle, Git discipline, PR process, code quality, TypeScript and Python quality, documentation |
| `overlays/solo-dev-overlay.md` | Process adaptations when operating without a team |
| `overlays/team-overlay.md` | Additional process requirements in a multi-person team |

---

### Cluster 3 — Backend (Phase 1)

| File | Purpose |
|------|---------|
| `constitutions/C2-backend-constitution.md` | 80 standards: service architecture, OpenAPI-first API contracts, database access from services, performance, resilience, security middleware, FastAPI specifics |
| `constitutions/C2-backend-implementation.md` | Practices P2.N: commands, code patterns, file locations that satisfy C2 standards |

---

### Cluster 4 — Authentication (Phase 1)

| File | Purpose |
|------|---------|
| `constitutions/C3-auth-constitution.md` | 36 standards: auth strategy per stack, NextAuth.js governance, JWT lifecycle, RBAC, split token storage, session management, audit logging |
| `constitutions/C3-auth-implementation.md` | Practices P3.N: auth implementation patterns, token handling code, session setup |

---

### Cluster 5 — Frontend (Phase 1)

| File | Purpose |
|------|---------|
| `constitutions/C4-frontend-constitution.md` | 82 standards: mobile-first, state management, Angular and Next.js specifics, group-build methodology, layer build order |
| `constitutions/C4-frontend-implementation.md` | Practices P4.N: Angular and Next.js code patterns, layer build commands, component structure |

---

### Cluster 6 — Database (Phase 1)

| File | Purpose |
|------|---------|
| `constitutions/C5-database-constitution.md` | 64 standards: database assignment by data type, PostgreSQL + Prisma, MongoDB + Beanie, ChromaDB, migration governance, cross-database integrity |
| `constitutions/C5-database-implementation.md` | Practices P5.N: migration commands, ORM patterns, seed scripts, query examples |

---

### Cluster 7 — Full-Stack Architecture (Phase 1)

| File | Purpose |
|------|---------|
| `constitutions/C6-fullstack-architecture-constitution.md` | 44 standards: dual-stack topology, stack assignment framework, request flows per stack, cross-stack communication, ADR process |

---

### Cluster 8 — Quality & Reliability (Phase 2)

| File | Purpose |
|------|---------|
| `constitutions/C7-testing-constitution.md` | 43 standards: test strategy, toolchain per stack, coverage gates, unit/integration/E2E, test database governance |
| `constitutions/C8-platform-reliability-constitution.md` | 82 standards: CI/CD pipeline, environment governance, observability, alert thresholds, severity framework, rollback, post-mortem |

---

### Cluster 9 — Product & AI Governance (Phase 3)

| File | Purpose |
|------|---------|
| `constitutions/C9-product-feature-constitution.md` | 30 standards: product vision, 5-gate feature qualification, MVP definitions, roadmap governance, Crown Jewel designation |
| `constitutions/C10-ai-collaboration-constitution.md` | 36 standards: AI role definitions, permission levels L1–L4, design-phase and build-phase AI workflow, solo dev AI pair programming, AI anti-patterns |

---

### Cluster 10 — Fast Navigation Indexes

> Read index entries first. Open full constitutions only when the index is insufficient.

| File | Purpose |
|------|---------|
| `indexes/quick-reference.md` | Standards organised by concern: auth, database, deployment, testing, incidents |
| `indexes/standards-index.md` | Every standard across C1–C10 with one-line description and priority |
| `indexes/anti-patterns-index.md` | Every anti-pattern across all constitutions — fast violation checking |
| `indexes/stack-assignment-matrix.md` | Stack assignment criteria and locked assignments for all four systems |

---

### Cluster 11 — Operational Runbooks

> Use only when an operational event is active. Do not read speculatively.

| File | Purpose | When |
|------|---------|------|
| `runbooks/SEV0-response-runbook.md` | SEV0 incident response: immediate steps, escalation | Active SEV0 |
| `runbooks/SEV1-response-runbook.md` | SEV1 incident response | Active SEV1 |
| `runbooks/financial-freeze-runbook.md` | Freeze financial ops on Reserve Bank or FundsLink | CF-03 or CF-07 |
| `runbooks/railway-deployment-runbook.md` | Railway backend deployment procedure | Deploying backend |
| `runbooks/vercel-rollback-runbook.md` | Vercel frontend rollback procedure | Rolling back frontend |
| `runbooks/database-migration-runbook.md` | Database migration execution procedure | Running migrations |
| `runbooks/ai-degradation-runbook.md` | Responding to AI tool degradation during a build session | AI tool failure |

---

### Cluster 12 — Workflow & Relay

| File | Purpose |
|------|---------|
| `workflow/ksdrill-sa-ai-workflow.md` | Complete AI engineer relay: handoff protocol Parts A–D, repo verification checklist, relay diagram |

---

### Cluster 13 — System Contexts

> One file per system. Load the correct one at session startup before any build work.

| File | System | Stack |
|------|--------|-------|
| `system-contexts/fundslink-context.md` | FundsLink Academy | Angular + FastAPI |
| `system-contexts/maphophe-context.md` | Maphophe Community | Next.js |
| `system-contexts/reserve-bank-context.md` | KSDRILL Reserve Bank | Angular + FastAPI |
| `system-contexts/syncup-context.md` | SyncUp Creator Platform | Next.js |

---

### Cluster 14 — Architecture Decision Records

| File | Purpose |
|------|---------|
| `adrs/ADR-000-template.md` | Template for new ADRs |
| `adrs/ADR-001-fundslink-stack.md` | FundsLink Academy stack decision |
| `adrs/ADR-002-maphophe-stack.md` | Maphophe Community stack decision |
| `adrs/ADR-003-reserve-bank-stack.md` | KSDRILL Reserve Bank stack decision |
| `adrs/ADR-004-syncup-stack.md` | SyncUp Creator Platform stack decision |

---

### Cluster 15 — Document Templates

| File | Purpose |
|------|---------|
| `templates/feature-proposal-template.md` | Mandatory before any feature build (S1.27) |
| `templates/incident-report-template.md` | Incident documentation template |
| `templates/post-mortem-template.md` | Post-mortem template (required after every SEV0/SEV1) |
| `templates/sprint-retro-template.md` | Sprint retrospective template |
| `templates/CONSTITUTION-INDEX-template.md` | Template for `CONSTITUTION-INDEX.md` in each project workspace (S10.21) |

---

## Complete File Index

Every file in this repository. No omissions. Sorted by reading priority.

| # | File | Cluster | Purpose |
|---|------|---------|---------|
| 01 | `AI-INSTRUCTIONS.md` | Entry | AI session startup — read every session |
| 02 | `MANIFEST.md` | Entry | This file — repo map and reading graph |
| 03 | `README.md` | Entry | Human-facing overview |
| 04 | `constitutions/C0-constitutional-order.md` | Governance | Master constitution — supreme authority |
| 05 | `constitutions/C1-engineering-standards.md` | Phase 0 | 97 engineering process and code quality standards |
| 06 | `overlays/solo-dev-overlay.md` | Phase 0 | Solo dev process adaptations |
| 07 | `overlays/team-overlay.md` | Phase 0 | Team process extensions |
| 08 | `constitutions/C2-backend-constitution.md` | Phase 1 — Backend | 80 backend architecture standards |
| 09 | `constitutions/C2-backend-implementation.md` | Phase 1 — Backend | Backend code patterns and commands |
| 10 | `constitutions/C3-auth-constitution.md` | Phase 1 — Auth | 36 authentication standards |
| 11 | `constitutions/C3-auth-implementation.md` | Phase 1 — Auth | Auth implementation patterns |
| 12 | `constitutions/C4-frontend-constitution.md` | Phase 1 — Frontend | 82 frontend architecture standards |
| 13 | `constitutions/C4-frontend-implementation.md` | Phase 1 — Frontend | Frontend code patterns and layer build |
| 14 | `constitutions/C5-database-constitution.md` | Phase 1 — Database | 64 database assignment and governance standards |
| 15 | `constitutions/C5-database-implementation.md` | Phase 1 — Database | Migration commands and ORM patterns |
| 16 | `constitutions/C6-fullstack-architecture-constitution.md` | Phase 1 — Full-Stack | 44 stack topology and integration standards |
| 17 | `constitutions/C7-testing-constitution.md` | Phase 2 | 43 testing strategy and coverage gate standards |
| 18 | `constitutions/C8-platform-reliability-constitution.md` | Phase 2 | 82 deployment, CI/CD, observability, incident standards |
| 19 | `constitutions/C9-product-feature-constitution.md` | Phase 3 | 30 product governance and feature qualification standards |
| 20 | `constitutions/C10-ai-collaboration-constitution.md` | Phase 3 | 36 AI role, permission, and workflow standards |
| 21 | `indexes/quick-reference.md` | Index | Standards by concern — fastest navigation |
| 22 | `indexes/standards-index.md` | Index | All standards with IDs and one-line descriptions |
| 23 | `indexes/anti-patterns-index.md` | Index | All anti-patterns for fast violation checking |
| 24 | `indexes/stack-assignment-matrix.md` | Index | Stack assignment criteria and locked decisions |
| 25 | `workflow/ksdrill-sa-ai-workflow.md` | Workflow | AI engineer relay, handoff protocol, verification checklist |
| 26 | `system-contexts/fundslink-context.md` | System Context | FundsLink Academy build context |
| 27 | `system-contexts/maphophe-context.md` | System Context | Maphophe Community build context |
| 28 | `system-contexts/reserve-bank-context.md` | System Context | KSDRILL Reserve Bank build context |
| 29 | `system-contexts/syncup-context.md` | System Context | SyncUp Creator Platform build context |
| 30 | `adrs/ADR-000-template.md` | ADR | ADR template |
| 31 | `adrs/ADR-001-fundslink-stack.md` | ADR | FundsLink stack decision record |
| 32 | `adrs/ADR-002-maphophe-stack.md` | ADR | Maphophe stack decision record |
| 33 | `adrs/ADR-003-reserve-bank-stack.md` | ADR | Reserve Bank stack decision record |
| 34 | `adrs/ADR-004-syncup-stack.md` | ADR | SyncUp stack decision record |
| 35 | `templates/feature-proposal-template.md` | Template | Feature proposal (required before build — S1.27) |
| 36 | `templates/incident-report-template.md` | Template | Incident report document |
| 37 | `templates/post-mortem-template.md` | Template | Post-mortem document (SEV0/SEV1 — S8.77) |
| 38 | `templates/sprint-retro-template.md` | Template | Sprint retrospective document |
| 39 | `templates/CONSTITUTION-INDEX-template.md` | Template | CONSTITUTION-INDEX.md for project workspaces (S10.21) |
| 40 | `runbooks/SEV0-response-runbook.md` | Runbook | SEV0 response steps |
| 41 | `runbooks/SEV1-response-runbook.md` | Runbook | SEV1 response steps |
| 42 | `runbooks/financial-freeze-runbook.md` | Runbook | Financial operations freeze |
| 43 | `runbooks/railway-deployment-runbook.md` | Runbook | Railway deployment procedure |
| 44 | `runbooks/vercel-rollback-runbook.md` | Runbook | Vercel rollback procedure |
| 45 | `runbooks/database-migration-runbook.md` | Runbook | Database migration execution |
| 46 | `runbooks/ai-degradation-runbook.md` | Runbook | AI tool degradation response |

---

## Reading Clusters — Visual Map

```
AI-INSTRUCTIONS.md  ←─── ALWAYS FIRST
       │
       ▼
system-contexts/{system}-context.md  ←─── BEFORE EVERY BUILD SESSION
       │
       ▼
MANIFEST.md (this file)  ←─── orientation pass, then follow clusters
       │
       ├── CLUSTER 1: Governance Root
       │     C0-constitutional-order.md
       │
       ├── CLUSTER 2: Phase 0 — Engineering Standards
       │     C1-engineering-standards.md
       │     overlays/solo-dev-overlay.md  OR  overlays/team-overlay.md
       │
       ├── CLUSTER 3+4+5+6+7: Phase 1 — Core Architecture
       │     C2-backend-constitution.md  ←→  C2-backend-implementation.md
       │     C3-auth-constitution.md     ←→  C3-auth-implementation.md
       │     C4-frontend-constitution.md ←→  C4-frontend-implementation.md
       │     C5-database-constitution.md ←→  C5-database-implementation.md
       │     C6-fullstack-architecture-constitution.md
       │
       ├── CLUSTER 8: Phase 2 — Quality & Reliability
       │     C7-testing-constitution.md
       │     C8-platform-reliability-constitution.md
       │
       ├── CLUSTER 9: Phase 3 — Product & AI Governance
       │     C9-product-feature-constitution.md
       │     C10-ai-collaboration-constitution.md
       │
       ├── CLUSTER 10: Fast Navigation Indexes (use before opening full constitutions)
       │     indexes/quick-reference.md
       │     indexes/standards-index.md
       │     indexes/anti-patterns-index.md
       │     indexes/stack-assignment-matrix.md
       │
       └── CLUSTERS 11–15: Operational, Contextual, Reference
             runbooks/   workflow/   system-contexts/   adrs/   templates/
```

---

*This manifest is updated whenever a file is added, removed, or renamed. It is the single
source of truth for repository navigation. When in doubt about what to read next, return here.*
