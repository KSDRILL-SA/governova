# Governova — Repository Manifest

> **This is the AI navigation spine. Read this file once to understand the complete repo
> structure, every file's purpose, its cluster, and the exact reading order for any session
> type. No searching required.**

---

## How to Use This Manifest

- **Quick session startup**: follow the [Session Reading Order](#session-reading-order) table top-to-bottom — stop at the row that matches your task
- **Cluster navigation**: files that belong together are grouped in the [File Clusters](#file-clusters) section — read all files in a cluster before moving to the next
- **Full repo scan**: use the [Complete File Index](#complete-file-index) — every file, one line

The repository follows the Governova four-layer architecture (Framework · Core · Implementation · Domains). Full vision: `GOVERNOVA-MASTER.md`.

---

## Session Reading Order

| Step | File | When to Stop Here |
|------|------|-------------------|
| **1** | `AI-INSTRUCTIONS.md` | Every session. No exception. Read this first. |
| **2** | `GOVERNOVA-MASTER.md` | First onboarding, or when platform context is needed |
| **3** | `reference-systems/{system}/context.md` | Before any build session on a specific system |
| **4** | `protocols/relay-protocol.md` | When confirming relay position or handoff protocol |
| **5** | `constitution/indexes/quick-reference.md` | When navigating a specific concern (auth, database, deploy) |
| **6** | `constitution/indexes/standards-index.md` | When auditing compliance or finding a standard ID |
| **7** | `constitution/indexes/anti-patterns-index.md` | When checking for known violation patterns |
| **8** | `constitution/C00-constitutional-order.md` | First onboarding, or when a constitutional conflict arises |
| **9** | Phase cluster for today's work *(see clusters below)* | Before any code in that domain |
| **10** | Implementation binding for your stack | When writing code in that domain |

---

## File Clusters

Clusters group every file that belongs together. Read the whole cluster before switching. A constitution and its stack binding are always read together — the constitution first, then the binding.

---

### Cluster 0 — Session Entry (Read Every Session)

| File | Purpose |
|------|---------|
| `AI-INSTRUCTIONS.md` | AI roles, permission levels, session startup protocol, navigation, citation format |
| `MANIFEST.md` | This file. Complete repo map. |
| `GOVERNOVA-MASTER.md` | Platform vision and source of truth (companions: `GOVERNOVA-PRODUCT.md`, `GOVERNOVA-STRATEGY.md`) |

---

### Cluster 1 — Framework (Layer 1: Universal Primitives)

| File | Purpose |
|------|---------|
| `framework/format-specification.md` | S{C}.{N} / AP-S{C}.{N}{letter} format and document structure |
| `framework/phase-model.md` | The four-phase read/dependency/failure order |
| `framework/severity-model.md` | SEV0–SEV3 classification and score weighting |
| `framework/permission-model.md` | L1–L4 permission levels; L4 permanently human-only |
| `framework/conflict-resolution.md` | Constitutional hierarchy + four-step protocol + Auth Override |
| `framework/amendment-protocol.md` | How standards change, are audited, and versioned |

---

### Cluster 2 — Governance Root

| File | Purpose |
|------|---------|
| `constitution/C00-constitutional-order.md` | Master document. Governs all other constitutions. Hierarchy, amendment protocol, common failure register. |

---

### Cluster 3 — Phase 0: Foundation

| File | Purpose |
|------|---------|
| `constitution/core/phase-0-foundation/C01-engineering-standards.md` | 98 standards: feature lifecycle, Git discipline, PR process, code quality, TypeScript/Python quality, documentation |
| `protocols/modes/personal-mode.md` | Process adaptations when operating solo |
| `protocols/modes/team-mode.md` | Additional process requirements in a team |

---

### Cluster 4 — Phase 1: Core Architecture

| File | Purpose |
|------|---------|
| `constitution/core/phase-1-core-architecture/C02-backend-constitution.md` | 80 standards: service architecture, OpenAPI-first, performance, resilience, security middleware |
| `constitution/core/phase-1-core-architecture/C03-auth-constitution.md` | 36 standards: auth strategy, JWT lifecycle, RBAC, split token storage, session management |
| `constitution/core/phase-1-core-architecture/C04-frontend-constitution.md` | 83 standards: mobile-first, state management, group-build methodology, layer build order |
| `constitution/core/phase-1-core-architecture/C05-database-constitution.md` | 65 standards: database assignment by data type, cross-database integrity, migration governance |
| `constitution/core/phase-1-core-architecture/C06-fullstack-architecture-constitution.md` | 44 standards: dual-stack topology, stack assignment framework, request flows, ADR process |

---

### Cluster 5 — Phase 2: Quality & Reliability

| File | Purpose |
|------|---------|
| `constitution/core/phase-2-quality-reliability/C07-testing-constitution.md` | 43 standards: test strategy, toolchain, coverage gates, unit/integration/E2E, test DB |
| `constitution/core/phase-2-quality-reliability/C08-platform-reliability-constitution.md` | 82 standards: CI/CD, environment governance, observability, alert thresholds, SEV framework, rollback |

---

### Cluster 6 — Phase 3: Product & Intelligence

| File | Purpose |
|------|---------|
| `constitution/core/phase-3-product-intelligence/C09-product-feature-constitution.md` | 30 standards: product vision, 5-gate qualification, MVP definitions, roadmap governance |
| `constitution/core/phase-3-product-intelligence/C10-ai-collaboration-constitution.md` | 39 standards: AI roles, L1–L4 permissions, relay workflow, CONSTITUTION-INDEX, AI anti-patterns |

---

### Cluster 7 — Implementation Bindings (Layer 3)

> Read the paired constitution first, then the binding for your stack.

| File | Binds | Stack |
|------|-------|-------|
| `constitution/implementation/fastapi/C02-backend-fastapi.md` | C02 | FastAPI (all backends) |
| `constitution/implementation/nextauth/C03-auth-nextauth.md` | C03 | NextAuth |
| `constitution/implementation/nextjs/C04-frontend-nextjs.md` | C04 | Next.js (full guide; angular split pending) |
| `constitution/implementation/prisma-postgresql/C05-database-prisma.md` | C05 | Prisma/PostgreSQL (full guide; beanie + chromadb split pending) |

---

### Cluster 8 — Domain Extensions (Layer 4)

> Active domains seed from the reference systems. See `constitution/domains/README.md`.

| Folder | Domain | Status |
|--------|--------|--------|
| `constitution/domains/fintech/` | Fintech | Active (FundsLink, Reserve Bank) |
| `constitution/domains/govtech/` | Govtech | Active (Maphophe) |
| `constitution/domains/edtech/` | Edtech | Active (FundsLink) |
| `constitution/domains/saas/` | SaaS/B2B | Active (SyncUp) |
| `constitution/domains/{healthtech,ecommerce,iot,ai-ml}/` | Planned | — |

---

### Cluster 9 — Fast Navigation Indexes

> Read index entries first. Open full constitutions only when the index is insufficient.

| File | Purpose |
|------|---------|
| `constitution/indexes/quick-reference.md` | Standards by concern: auth, database, deployment, testing, incidents |
| `constitution/indexes/standards-index.md` | Every standard across C1–C10 with one-line description |
| `constitution/indexes/anti-patterns-index.md` | Every anti-pattern — fast violation checking |
| `constitution/indexes/stack-assignment-matrix.md` | Stack assignment criteria and locked assignments |

---

### Cluster 10 — Protocols

| File | Purpose |
|------|---------|
| `protocols/relay-protocol.md` | AI engineer relay: handoff protocol Parts A–D, repo verification, relay diagram |
| `protocols/relay-clarification.md` | MINOR vs ARCHITECTURAL fast-path |
| `protocols/relay-abort.md` | Procedure when a relay diverges mid-build |
| `protocols/git-workflow.md` | Branch model, commit convention, PR process, golden rules |
| `protocols/modes/{personal,team,enterprise}-mode.md` | Operating modes |
| `protocols/frameworks/ai-assisted-software-development-workflow.md` | 8-step AI-assisted lifecycle (loadable SKILL.md) |
| `protocols/frameworks/ai-review-challenge-framework.md` | 3 review layers + challenge questions (loadable SKILL.md) |

---

### Cluster 11 — Governance (Runbooks · Decisions · Changelog)

| File | Purpose | When |
|------|---------|------|
| `governance/runbooks/RB-01-sev0-response.md` | SEV0 incident response | Active SEV0 |
| `governance/runbooks/RB-02-sev1-response.md` | SEV1 incident response | Active SEV1 |
| `governance/runbooks/RB-03-financial-freeze.md` | Freeze financial ops | Balance discrepancy |
| `governance/runbooks/RB-04-database-migration.md` | Migration execution | Running migrations |
| `governance/runbooks/RB-05-ai-degradation.md` | AI tool degradation response | AI tool failure |
| `governance/runbooks/RB-06-railway-deployment.md` | Railway backend deployment | Deploying backend |
| `governance/runbooks/RB-07-vercel-rollback.md` | Vercel frontend rollback | Rolling back frontend |
| `governance/runbooks/RB-08-relay-abort.md` | Relay abort response | Relay divergence |
| `governance/decisions/ADR-000…004` | Architecture decision records | — |
| `governance/decisions/RESTRUCTURE-v2.0.md` | The v2.0 four-layer restructure instruction (executed record) | — |
| `governance/changelog/amendments-log.md` | Append-only amendment audit trail | — |

---

### Cluster 12 — Platform (The Product)

> Spec-phase. `SPEC.md` files define what gets built. The IDE extension is the wedge (built first).

| File / Folder | Purpose |
|---------------|---------|
| `platform/engine/SPEC.md` | Engine architecture: 7 components, stack, build order, API contract |
| `platform/engine/{constitutional-store,violation-detector,relay-state-machine,audit-trail,system-knowledge-engine,mapping-engine,intelligence}/` | Engine components |
| `platform/surfaces/{ide-extension,jetbrains-plugin,cicd-enforcer,pr-guardian-bot,web-dashboard,cli,slack-teams-bot,mcp-server}/` | The 8 product surfaces |

---

### Cluster 13 — Reference Systems

> One folder per flagship. Load the correct `context.md` at session startup.

| File | System | Stack |
|------|--------|-------|
| `reference-systems/fundslink-academy/context.md` | FundsLink Academy | Angular + FastAPI |
| `reference-systems/maphophe/context.md` | Maphophe Community | Next.js |
| `reference-systems/ksdrill-reserve-bank/context.md` | KSDRILL Reserve Bank | Angular + FastAPI |
| `reference-systems/syncup/context.md` | SyncUp Creator Platform | Next.js |

---

### Cluster 14 — Templates & Scripts

| File | Purpose |
|------|---------|
| `templates/CONSTITUTION-INDEX-template.md` | Per-project compiled constitution index (S10.21) |
| `templates/feature-proposal-template.md` | Mandatory before any feature build (S1.27) |
| `templates/incident-report-template.md` | Incident documentation |
| `templates/post-mortem-template.md` | Post-mortem (required after SEV0/SEV1) |
| `templates/sprint-retro-template.md` | Sprint retrospective |
| `templates/domain-constitution-template.md` | Layer 4 domain extension authoring |
| `templates/implementation-guide-template.md` | Layer 3 stack binding authoring |
| `scripts/validate-integrity.py` | Validates every S{C}.{N} reference resolves (600 standards) |

---

## Reading Clusters — Visual Map

```
AI-INSTRUCTIONS.md  ←─── ALWAYS FIRST
       │
       ▼
GOVERNOVA-MASTER.md  ←─── platform context
       │
       ▼
reference-systems/{system}/context.md  ←─── BEFORE EVERY BUILD SESSION
       │
       ▼
MANIFEST.md (this file)  ←─── orientation, then follow clusters
       │
       ├── CLUSTER 1: framework/  (Layer 1 primitives)
       ├── CLUSTER 2: constitution/C00-constitutional-order.md
       ├── CLUSTER 3: Phase 0 — C01  + protocols/modes/
       ├── CLUSTER 4: Phase 1 — C02 C03 C04 C05 C06
       │     paired bindings in constitution/implementation/{stack}/
       ├── CLUSTER 5: Phase 2 — C07 C08
       ├── CLUSTER 6: Phase 3 — C09 C10
       ├── CLUSTER 9: constitution/indexes/  (use before full constitutions)
       └── CLUSTERS 10–14: protocols/  governance/  platform/  reference-systems/  templates/  scripts/
```

---

*This manifest is updated whenever a file is added, removed, or renamed. It is the single
source of truth for repository navigation. When in doubt about what to read next, return here.*
