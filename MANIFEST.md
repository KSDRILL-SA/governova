# Governova — Repository Manifest

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
| **2** | `GOVERNOVA-MASTER.md` | First session on a new project, or when platform context is needed |
| **3** | `reference-systems/{system}/context.md` | Before any build session on a specific system |
| **4** | `protocols/relay-protocol.md` | When confirming relay position or handoff protocol |
| **5** | `constitution/indexes/quick-reference.md` | When navigating a specific concern (auth, database, deploy) |
| **6** | `constitution/indexes/standards-index.md` | When auditing standards compliance or finding a standard ID |
| **7** | `constitution/indexes/anti-patterns-index.md` | When checking for known violation patterns |
| **8** | `constitution/C00-constitutional-order.md` | First onboarding, or when a constitutional conflict arises |
| **9** | Constitution cluster for today's domain *(see clusters below)* | Before any code in that domain |
| **10** | Implementation guide in the same cluster | When writing code in that domain |

---

## File Clusters

Clusters group every file that belongs together. Read the whole cluster before switching to another cluster. Implementation guides are always read alongside their paired constitution — never in isolation.

---

### Cluster 0 — Session Entry (Read Every Session)

| File | Purpose |
|------|---------|
| `AI-INSTRUCTIONS.md` | AI role definitions, permission levels, session startup protocol, navigation hierarchy, citation format |
| `GOVERNOVA-MASTER.md` | Complete platform vision — four-layer architecture, product surfaces, business model, reference systems |
| `MANIFEST.md` | This file. Complete repo map. |

---

### Cluster 1 — Framework Layer (Universal Primitives)

| File | Purpose |
|------|---------|
| `framework/format-specification.md` | S{C}.{N} standard ID format, AP anti-pattern format, required document structure |
| `framework/phase-model.md` | Four-phase read and dependency order (Phase 0–3) |
| `framework/severity-model.md` | SEV0–SEV3 classification for violations and incidents |
| `framework/permission-model.md` | L1–L4 AI permission levels — L4 permanently human-only |
| `framework/conflict-resolution.md` | Constitutional hierarchy and four-step conflict resolution protocol |
| `framework/amendment-protocol.md` | How standards are changed, audited, and versioned |

---

### Cluster 2 — Governance Root

| File | Purpose |
|------|---------|
| `constitution/C00-constitutional-order.md` | Master document. Governs all other constitutions. Terminology, hierarchy, amendment protocol, common failure register. |

---

### Cluster 3 — Phase 0: Foundation

| File | Purpose |
|------|---------|
| `constitution/core/phase-0-foundation/C01-engineering-standards.md` | Standards governing how work is done: 8-phase feature lifecycle, Git discipline, PR process, code quality, TypeScript and Python standards, documentation |
| `protocols/modes/personal-mode.md` | Process adaptations when operating as a solo developer |
| `protocols/modes/team-mode.md` | Additional process requirements in a multi-person team |
| `protocols/modes/enterprise-mode.md` | Enterprise mode — Mapping Engine, certification tracking, board reporting |

---

### Cluster 4 — Phase 1: Backend

| File | Purpose |
|------|---------|
| `constitution/core/phase-1-core-architecture/C02-backend-constitution.md` | Universal backend standards: service architecture, OpenAPI-first API contracts, performance, resilience, security middleware |
| `constitution/implementation/fastapi/C02-backend-fastapi.md` | FastAPI-specific implementation of C02 standards |

---

### Cluster 5 — Phase 1: Authentication

| File | Purpose |
|------|---------|
| `constitution/core/phase-1-core-architecture/C03-auth-constitution.md` | Universal auth standards: auth strategy, JWT lifecycle, RBAC, OAuth, session management, audit logging |
| `constitution/implementation/nextauth/C03-auth-nextauth.md` | NextAuth-specific implementation of C03 standards |

---

### Cluster 6 — Phase 1: Frontend

| File | Purpose |
|------|---------|
| `constitution/core/phase-1-core-architecture/C04-frontend-constitution.md` | Universal frontend standards: mobile-first, state management, group-build methodology, layer build order |
| `constitution/implementation/nextjs/C04-frontend-nextjs.md` | Next.js-specific implementation of C04 standards |

---

### Cluster 7 — Phase 1: Database

| File | Purpose |
|------|---------|
| `constitution/core/phase-1-core-architecture/C05-database-constitution.md` | Universal database standards: database assignment by data type, cross-database integrity, migration governance |
| `constitution/implementation/prisma-postgresql/C05-database-prisma.md` | Prisma + PostgreSQL implementation of C05 standards |

---

### Cluster 8 — Phase 1: Full-Stack Integration

| File | Purpose |
|------|---------|
| `constitution/core/phase-1-core-architecture/C06-fullstack-architecture-constitution.md` | System topology, dual-stack assignment, request flows, cross-stack communication |
| `constitution/indexes/stack-assignment-matrix.md` | Decision framework for assigning technology stacks to new systems |

---

### Cluster 9 — Phase 2: Quality & Reliability

| File | Purpose |
|------|---------|
| `constitution/core/phase-2-quality-reliability/C07-testing-constitution.md` | Test strategy, toolchain, coverage gates, unit/integration/E2E, test database governance |
| `constitution/core/phase-2-quality-reliability/C08-platform-reliability-constitution.md` | Deployment, CI/CD, environment governance, observability, alert thresholds, SEV framework, rollback |

---

### Cluster 10 — Phase 3: Product & Intelligence

| File | Purpose |
|------|---------|
| `constitution/core/phase-3-product-intelligence/C09-product-feature-constitution.md` | Product vision, feature governance, MVP definitions, 5-gate qualification, roadmap governance |
| `constitution/core/phase-3-product-intelligence/C10-ai-collaboration-constitution.md` | AI role definitions, L1–L4 permission boundaries, relay protocols, CONSTITUTION-INDEX standard, AI anti-patterns |

---

### Cluster 11 — Implementation Bindings

| File | Purpose |
|------|---------|
| `constitution/implementation/angular/` | Angular implementation binding for C04 Frontend |
| `constitution/implementation/beanie-mongodb/` | Beanie + MongoDB implementation for C05 Database |
| `constitution/implementation/chromadb/` | ChromaDB implementation for C05 Database (vector) |

---

### Cluster 12 — Indexes

| File | Purpose |
|------|---------|
| `constitution/indexes/quick-reference.md` | High-frequency standards grouped by concern |
| `constitution/indexes/standards-index.md` | Every standard across all constitutions, searchable by ID and topic |
| `constitution/indexes/anti-patterns-index.md` | Every anti-pattern across all constitutions |
| `constitution/indexes/stack-assignment-matrix.md` | Stack decision framework |

---

### Cluster 13 — Protocols

| File | Purpose |
|------|---------|
| `protocols/relay-protocol.md` | 5-engineer relay model — who does what, in what order, with what permissions |
| `protocols/relay-clarification.md` | MINOR vs ARCHITECTURAL classification — when to pause the relay |
| `protocols/relay-abort.md` | What to do when a relay diverges from the design mid-build |
| `protocols/git-workflow.md` | Branch model, commit convention, PR process, golden rules |

---

### Cluster 14 — Governance: Runbooks

| File | Trigger |
|------|---------|
| `governance/runbooks/RB-01-sev0-response.md` | Production down or data at risk |
| `governance/runbooks/RB-02-sev1-response.md` | Functional breakage, security gap |
| `governance/runbooks/RB-03-financial-freeze.md` | Balance discrepancy detected |
| `governance/runbooks/RB-04-database-migration.md` | Migration failure or rollback |
| `governance/runbooks/RB-05-ai-degradation.md` | AI pipeline failure during relay |
| `governance/runbooks/RB-06-railway-deployment.md` | Backend deployment incident |
| `governance/runbooks/RB-07-vercel-rollback.md` | Frontend deployment incident |
| `governance/runbooks/RB-08-relay-abort.md` | AI output diverges from design |

---

### Cluster 15 — Governance: Decisions

| File | Purpose |
|------|---------|
| `governance/decisions/ADR-000-template.md` | Template for all ADRs |
| `governance/decisions/ADR-001-fundslink-stack.md` | FundsLink Academy — Angular + FastAPI |
| `governance/decisions/ADR-002-maphophe-stack.md` | Maphophe — Next.js |
| `governance/decisions/ADR-003-reserve-bank-stack.md` | KSDRILL Reserve Bank — Angular + FastAPI |
| `governance/decisions/ADR-004-syncup-stack.md` | SyncUp — Next.js |
| `governance/changelog/amendments-log.md` | Immutable constitutional amendment audit trail |

---

### Cluster 16 — Reference Systems

| File | Purpose |
|------|---------|
| `reference-systems/fundslink-academy/context.md` | FundsLink Academy system context |
| `reference-systems/maphophe/context.md` | Maphophe system context |
| `reference-systems/ksdrill-reserve-bank/context.md` | KSDRILL Reserve Bank system context |
| `reference-systems/syncup/context.md` | SyncUp system context |

---

### Cluster 17 — Platform (Engine + Surfaces)

| File | Purpose |
|------|---------|
| `platform/engine/SPEC.md` | Governance engine architecture specification |
| `platform/surfaces/ide-extension/` | VS Code + Cursor IDE extension spec |
| `platform/surfaces/cicd-enforcer/` | GitHub Actions CI/CD enforcer spec |
| `platform/surfaces/pr-guardian-bot/` | PR review bot spec |
| `platform/surfaces/cli/` | `governova` CLI spec |
| `platform/surfaces/mcp-server/` | MCP server spec |

---

### Cluster 18 — Templates & Scripts

| File | Purpose |
|------|---------|
| `templates/CONSTITUTION-INDEX-template.md` | Per-project AI session index template |
| `templates/feature-proposal-template.md` | S1.27 feature proposal |
| `templates/domain-constitution-template.md` | Domain extension contribution template |
| `templates/implementation-guide-template.md` | Stack binding contribution template |
| `scripts/validate-integrity.py` | Constitutional integrity validator — checks all S{C}.{N} references resolve |

---

## Complete File Index

### Root

| File | Purpose |
|------|---------|
| `README.md` | Public face of the Governova repo |
| `GOVERNOVA-MASTER.md` | Master vision document — source of truth |
| `AI-INSTRUCTIONS.md` | AI session instructions — read first every session |
| `MANIFEST.md` | This file |
| `QUICKSTART.md` | 10-step new project setup |
| `CONTRIBUTING.md` | Domain and stack contribution process |
| `LICENSE` | MIT licence |

### framework/

| File | Purpose |
|------|---------|
| `format-specification.md` | S{C}.{N} format, AP format, document structure |
| `phase-model.md` | Four-phase read and dependency order |
| `severity-model.md` | SEV0–SEV3 classification |
| `permission-model.md` | L1–L4 permission levels |
| `conflict-resolution.md` | Constitutional hierarchy and resolution protocol |
| `amendment-protocol.md` | Standard change, audit, versioning |

### constitution/

| File | Purpose |
|------|---------|
| `C00-constitutional-order.md` | Master — governs all constitutions |

### constitution/core/phase-0-foundation/

| File | Purpose |
|------|---------|
| `C01-engineering-standards.md` | Engineering process and code quality standards |

### constitution/core/phase-1-core-architecture/

| File | Purpose |
|------|---------|
| `C02-backend-constitution.md` | Universal backend standards |
| `C03-auth-constitution.md` | Universal auth standards |
| `C04-frontend-constitution.md` | Universal frontend standards |
| `C05-database-constitution.md` | Universal database standards |
| `C06-fullstack-architecture-constitution.md` | System topology and integration |

### constitution/core/phase-2-quality-reliability/

| File | Purpose |
|------|---------|
| `C07-testing-constitution.md` | Testing strategy and coverage standards |
| `C08-platform-reliability-constitution.md` | Deployment and reliability standards |

### constitution/core/phase-3-product-intelligence/

| File | Purpose |
|------|---------|
| `C09-product-feature-constitution.md` | Product and feature governance standards |
| `C10-ai-collaboration-constitution.md` | AI governance and permission boundaries |

### constitution/implementation/

| File | Purpose |
|------|---------|
| `fastapi/C02-backend-fastapi.md` | FastAPI binding for C02 |
| `nextauth/C03-auth-nextauth.md` | NextAuth binding for C03 |
| `nextjs/C04-frontend-nextjs.md` | Next.js binding for C04 |
| `prisma-postgresql/C05-database-prisma.md` | Prisma + PostgreSQL binding for C05 |

### constitution/indexes/

| File | Purpose |
|------|---------|
| `standards-index.md` | All standards — searchable by ID and topic |
| `anti-patterns-index.md` | All anti-patterns |
| `quick-reference.md` | High-frequency standards by concern |
| `stack-assignment-matrix.md` | Stack selection decision framework |

### protocols/

| File | Purpose |
|------|---------|
| `relay-protocol.md` | 5-engineer relay model |
| `relay-clarification.md` | MINOR vs ARCHITECTURAL classification |
| `relay-abort.md` | Relay abort procedure |
| `git-workflow.md` | Branch model, commits, PR process |
| `modes/personal-mode.md` | Solo developer operating mode |
| `modes/team-mode.md` | Team operating mode |
| `modes/enterprise-mode.md` | Enterprise operating mode |

### governance/runbooks/

| File | Trigger |
|------|---------|
| `RB-01-sev0-response.md` | Production down |
| `RB-02-sev1-response.md` | Functional breakage |
| `RB-03-financial-freeze.md` | Balance discrepancy |
| `RB-04-database-migration.md` | Migration failure |
| `RB-05-ai-degradation.md` | AI pipeline failure |
| `RB-06-railway-deployment.md` | Backend deployment incident |
| `RB-07-vercel-rollback.md` | Frontend deployment incident |
| `RB-08-relay-abort.md` | Relay divergence |

### governance/decisions/

| File | System |
|------|--------|
| `ADR-000-template.md` | Template |
| `ADR-001-fundslink-stack.md` | FundsLink Academy |
| `ADR-002-maphophe-stack.md` | Maphophe |
| `ADR-003-reserve-bank-stack.md` | KSDRILL Reserve Bank |
| `ADR-004-syncup-stack.md` | SyncUp |

### governance/changelog/

| File | Purpose |
|------|---------|
| `amendments-log.md` | Immutable amendment audit trail |

### reference-systems/

| File | Purpose |
|------|---------|
| `fundslink-academy/context.md` | FundsLink Academy system context |
| `maphophe/context.md` | Maphophe system context |
| `ksdrill-reserve-bank/context.md` | KSDRILL Reserve Bank system context |
| `syncup/context.md` | SyncUp system context |

### platform/

| File | Purpose |
|------|---------|
| `engine/SPEC.md` | Governance engine architecture specification |

### templates/

| File | Purpose |
|------|---------|
| `CONSTITUTION-INDEX-template.md` | Per-project AI session index |
| `feature-proposal-template.md` | S1.27 feature proposal |
| `incident-report-template.md` | Incident documentation |
| `post-mortem-template.md` | Post-mortem template |
| `sprint-retro-template.md` | Sprint retrospective |
| `domain-constitution-template.md` | Domain extension contribution |
| `implementation-guide-template.md` | Stack binding contribution |

### scripts/

| File | Purpose |
|------|---------|
| `validate-integrity.py` | Constitutional integrity validator |

---

*Governova — v2.0 — Maluleke Kurhula Success · KSDRILL SA · 2026*
