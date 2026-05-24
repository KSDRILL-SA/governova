# Claude Code — Governova Repository Restructure Instructions

---

| Attribute | Value |
|-----------|-------|
| **Document** | Full restructure and build instructions for Claude Code |
| **Target Repo** | `system-design-template` → `governova` |
| **Authored by** | Maluleke Kurhula Success |
| **Version** | v1.0 |
| **Session type** | Refactor — constitutional restructure |
| **Permission level** | L3 — Implement only. No constitutional decisions. |
| **Branch** | `refactor/governova-restructure` off `dev` |

---

> **Claude Code: Read this entire document before touching a single file.
> This is your complete operating instruction for this session.
> Do not deviate. Do not improvise. Do not make decisions not covered here.
> Every action you take must be traceable to a step in this document.**

---

## Part 1 — Context: What This Repo Is and What You Are Doing

This repository is the constitutional governance system for KSDRILL SA engineering work.
It is currently named `system-design-template` and structured as a flat template.

You are restructuring it into **Governova** — the world's first AI development governance
platform. Governova is not a personal template. It is a platform product with a four-layer
constitutional architecture, seven product surfaces, a governance engine, and an intelligence
layer. The full vision is documented in `GOVERNOVA-MASTER.md` which you will place at the
repo root as one of your first actions.

This restructure is a **pure refactor and scaffold**. You are:
- Creating new folders
- Moving existing files to their correct new locations
- Creating new files with specified content
- Updating root documents (README, MANIFEST, AI-INSTRUCTIONS)
- Writing stub READMEs for every new folder explaining what goes there

You are NOT:
- Changing the content of any existing constitution or implementation guide
- Making any constitutional decisions
- Renaming or modifying any `S{C}.{N}` standard IDs
- Altering runbook content
- Deciding anything not specified in these instructions

If anything is unclear, stop and flag it. Do not guess.

---

## Part 2 — Branch Setup

Before any file operations, set up the correct branch:

```bash
git checkout dev
git pull origin dev
git checkout -b refactor/governova-restructure
```

All work happens on `refactor/governova-restructure`.
Commit at the end of each Part (Parts 3–10) so progress is preserved.
Commit message format: `refactor: {description} — Governova restructure`

---

## Part 3 — Place the Master Document at Root

This is the first and most important file operation.

**Action:** Copy the `GOVERNOVA-MASTER.md` file into the repo root.

The content of `GOVERNOVA-MASTER.md` is the complete Governova vision document —
v2.0, locked 2026-05-22. It contains 24 sections covering the full platform architecture,
four-layer constitutional system, governance engine, product surfaces, business model,
and repository structure. It is the source of truth for everything in this repo.

Create `GOVERNOVA-MASTER.md` at the repo root with this exact header and then the full
document content (paste the content from the provided GOVERNOVA-MASTER.md):

```
governova/
└── GOVERNOVA-MASTER.md    ← source of truth, first file anyone reads
```

**Commit after this step:**
```bash
git add GOVERNOVA-MASTER.md
git commit -m "refactor: add GOVERNOVA-MASTER.md v2.0 at repo root"
```

---

## Part 4 — Create the Full Folder Structure

Create every folder listed below. Use `mkdir -p` for nested paths.
Every folder gets a `README.md` — content specified in Part 5.

```bash
# LAYER 1 — Framework
mkdir -p framework

# LAYER 2 — Constitution Core (by phase)
mkdir -p constitution/core/phase-0-foundation
mkdir -p constitution/core/phase-1-core-architecture
mkdir -p constitution/core/phase-2-quality-reliability
mkdir -p constitution/core/phase-3-product-intelligence

# LAYER 3 — Implementation bindings
mkdir -p constitution/implementation/nextjs
mkdir -p constitution/implementation/angular
mkdir -p constitution/implementation/fastapi
mkdir -p constitution/implementation/nextauth
mkdir -p constitution/implementation/prisma-postgresql
mkdir -p constitution/implementation/beanie-mongodb
mkdir -p constitution/implementation/chromadb

# LAYER 4 — Domain extensions
mkdir -p constitution/domains/fintech
mkdir -p constitution/domains/govtech
mkdir -p constitution/domains/edtech
mkdir -p constitution/domains/saas
mkdir -p constitution/domains/healthtech
mkdir -p constitution/domains/ecommerce
mkdir -p constitution/domains/iot
mkdir -p constitution/domains/ai-ml

# Indexes
mkdir -p constitution/indexes

# Protocols
mkdir -p protocols/modes

# Governance
mkdir -p governance/runbooks
mkdir -p governance/decisions
mkdir -p governance/changelog

# Platform — Engine
mkdir -p platform/engine/constitutional-store
mkdir -p platform/engine/violation-detector
mkdir -p platform/engine/relay-state-machine
mkdir -p platform/engine/audit-trail
mkdir -p platform/engine/system-knowledge-engine
mkdir -p platform/engine/mapping-engine
mkdir -p platform/engine/intelligence

# Platform — Surfaces
mkdir -p platform/surfaces/ide-extension
mkdir -p platform/surfaces/jetbrains-plugin
mkdir -p platform/surfaces/cicd-enforcer
mkdir -p platform/surfaces/pr-guardian-bot
mkdir -p platform/surfaces/web-dashboard
mkdir -p platform/surfaces/cli
mkdir -p platform/surfaces/slack-teams-bot
mkdir -p platform/surfaces/mcp-server

# Reference Systems
mkdir -p reference-systems/fundslink-academy
mkdir -p reference-systems/maphophe
mkdir -p reference-systems/ksdrill-reserve-bank
mkdir -p reference-systems/syncup

# Templates (already exists — will be expanded)
mkdir -p templates

# Scripts
mkdir -p scripts
```

**Commit after this step:**
```bash
git add -A
git commit -m "refactor: create full Governova folder structure"
```

---

## Part 5 — Write README.md for Every New Folder

Every folder must have a README explaining its purpose, what files belong there,
and the migration or build status. Use the exact content below for each.

---

### `framework/README.md`

```markdown
# Framework — Layer 1: Universal Primitives

This folder contains the universal primitives that govern everything in Governova.
These are stack-agnostic and domain-agnostic. They never change regardless of
which technology or industry a project uses.

The framework is what makes Governova universal. Every constitution, every
implementation binding, and every domain extension operates within these primitives.

## Files in this folder

| File | Purpose |
|------|---------|
| `format-specification.md` | The S{C}.{N} standard ID format, AP-S{C}.{N}{letter} anti-pattern format, and required document structure for every constitution |
| `phase-model.md` | The four-phase read and dependency order (Phase 0–3) |
| `severity-model.md` | SEV0–SEV3 classification for violations and incidents |
| `permission-model.md` | The L1–L4 AI permission levels — L4 permanently human-only |
| `conflict-resolution.md` | The constitutional hierarchy and four-step conflict resolution protocol |
| `amendment-protocol.md` | How standards are changed, audited, and versioned |

## Status
Files to be created. Content extracted from C00-constitutional-order.md during
the framework extraction phase of the restructure.
```

---

### `constitution/README.md`

```markdown
# Constitution — The Standards Database

This folder contains the complete Governova constitutional standards database,
organised in four layers:

| Layer | Folder | Description |
|-------|--------|-------------|
| Layer 2 | `core/` | Universal constitutions organised by phase — principles that apply to any system |
| Layer 3 | `implementation/` | Stack-specific bindings — how universal principles are satisfied in specific technologies |
| Layer 4 | `domains/` | Domain-specific extensions — what specific industries additionally require |
| Index | `indexes/` | Fast lookup: standards, anti-patterns, quick reference, stack matrix |

## C00 — Constitutional Order
`C00-constitutional-order.md` sits at this folder root — above the phases —
because it governs the phases themselves.

## How a project compiles its constitution
A project declares its stack and domain. Governova compiles:
Framework + Core (all phases) + Implementation (declared stack) + Domains (declared domain)
= the project's CONSTITUTION-INDEX

See GOVERNOVA-MASTER.md §5 for the full compilation model.
```

---

### `constitution/core/README.md`

```markdown
# Core — Layer 2: Universal Constitutions

Eleven constitutions organised into four phases. These state universal
principles — what must be true for any system, independent of any specific technology.

## The four phases

| Phase | Folder | Read Before |
|-------|--------|-------------|
| Phase 0 — Foundation | `phase-0-foundation/` | Any code is written |
| Phase 1 — Core Architecture | `phase-1-core-architecture/` | First line of application code |
| Phase 2 — Quality & Reliability | `phase-2-quality-reliability/` | Any feature is production-ready |
| Phase 3 — Product & Intelligence | `phase-3-product-intelligence/` | Any roadmap or AI session |

The phase order is the read order, the dependency order, and the failure order.
A system that skips a phase fails in the way that phase was designed to prevent.
```

---

### `constitution/core/phase-0-foundation/README.md`

```markdown
# Phase 0 — Foundation

**Read before: any code is written, any branch is created, any environment is set up.**

> If Phase 0 is skipped, no engineer shares a definition of "done," no code quality
> standard exists to enforce, and the first PR introduces patterns that become
> impossible to remove without a rewrite.

## Contents

| File | Constitution | Standards |
|------|--------------|-----------|
| `C01-engineering-standards.md` | Engineering Standards | How work happens: 8-phase feature lifecycle, Git discipline, PR process, code quality, TypeScript and Python standards, documentation |
```

---

### `constitution/core/phase-1-core-architecture/README.md`

```markdown
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
```

---

### `constitution/core/phase-2-quality-reliability/README.md`

```markdown
# Phase 2 — Quality & Reliability

**Read before: any feature is considered production-ready.**

> If Phase 2 is skipped, the system ships without a testing strategy, deployment
> governance, or incident response. The first production failure is uncontrolled,
> untraceable, and unrecoverable.

## Contents

| File | Constitution | Governs |
|------|--------------|---------|
| `C07-testing-constitution.md` | Testing | Test strategy, toolchain, coverage gates, unit/integration/E2E, test database |
| `C08-platform-reliability-constitution.md` | Platform Reliability | Deployment, CI/CD, environment governance, observability, alert thresholds, SEV framework, rollback |
```

---

### `constitution/core/phase-3-product-intelligence/README.md`

```markdown
# Phase 3 — Product & Intelligence

**Read before: any feature roadmap decisions or AI-assisted development sessions.**

> These come last because they require all technical constitutions to be locked.
> Product and AI governance decisions must be made against a stable technical foundation.

## Contents

| File | Constitution | Governs |
|------|--------------|---------|
| `C09-product-feature-constitution.md` | Product & Feature | Product vision, feature governance, MVP definitions, 5-gate qualification, roadmap |
| `C10-ai-collaboration-constitution.md` | AI Collaboration | AI role definitions, L1–L4 permission boundaries, relay protocols, CONSTITUTION-INDEX standard, AI anti-patterns |
```

---

### `constitution/implementation/README.md`

```markdown
# Implementation — Layer 3: Stack-Specific Bindings

This folder contains the implementation guides that bind universal core standards
to specific technologies. Each binding shows how a universal principle is satisfied
in a concrete stack, and what failure looks like there.

## The principle of binding

A core standard states what must be true (universal).
An implementation binding states how it is satisfied in a specific technology.

Example:
- Core (universal): S2.04 — Every endpoint validates all input against a typed schema.
- Implementation (fastapi): S2.04/fastapi — Satisfied by a Pydantic model bound to
  every route. Raw dict access is AP-S2.04a/fastapi.

## The KSDRILL SA reference bindings

| Folder | Binds | For |
|--------|-------|-----|
| `nextjs/` | C04 Frontend | Content-driven, SEO-critical systems (Maphophe, SyncUp) |
| `angular/` | C04 Frontend | Enterprise dashboards, financial systems (FundsLink, Reserve Bank) |
| `fastapi/` | C02 Backend | All backend services |
| `nextauth/` | C03 Auth | Authentication across both stacks |
| `prisma-postgresql/` | C05 Database | Relational, transactional data |
| `beanie-mongodb/` | C05 Database | Document, flexible-schema data |
| `chromadb/` | C05 Database | Vector data, AI/RAG pipelines |

## Migration status
Implementation guides from the original repo are migrated here:
- C02-backend-implementation.md → `fastapi/C02-backend-fastapi.md`
- C03-auth-implementation.md → `nextauth/C03-auth-nextauth.md`
- C04-frontend-implementation.md → split: `nextjs/C04-frontend-nextjs.md` + `angular/C04-frontend-angular.md`
- C05-database-implementation.md → split: `prisma-postgresql/C05-database-prisma.md` + `beanie-mongodb/C05-database-beanie.md` + `chromadb/C05-database-chromadb.md`

Note: The full split of C04 and C05 implementation guides by stack is a Phase 1
build task — for now, place the full guide in the primary stack folder and note
the split in the folder README.
```

---

### `constitution/domains/README.md`

```markdown
# Domains — Layer 4: Domain Extensions

Domain extensions add industry-specific standards on top of the universal core
and implementation bindings. They encode the additional requirements a specific
industry imposes.

## Registry

| Folder | Domain | Status | Reference System |
|--------|--------|--------|-----------------|
| `fintech/` | Financial technology | Active — seed from FundsLink + Reserve Bank | FundsLink, Reserve Bank |
| `govtech/` | Government technology | Active — seed from Maphophe | Maphophe |
| `edtech/` | Education technology | Active — seed from FundsLink | FundsLink |
| `saas/` | SaaS / B2B | Active — seed from SyncUp | SyncUp |
| `healthtech/` | Health technology | Planned | — |
| `ecommerce/` | E-commerce | Planned | — |
| `iot/` | IoT / Embedded | Planned | — |
| `ai-ml/` | AI / ML Systems | Planned | — |

## How domain extensions grow
Domain extensions are the primary growth vector of the constitutional database.
They can be contributed by domain experts via the process in CONTRIBUTING.md.
Every extension follows the same format specification as the core and undergoes
conflict review before publication.
```

---

### `constitution/indexes/README.md`

```markdown
# Indexes — Fast Lookup Layer

Fast navigation into the constitutional database. Read these before opening
a full constitution document.

## Files

| File | Purpose |
|------|---------|
| `standards-index.md` | Every standard across all constitutions, searchable by ID and topic |
| `anti-patterns-index.md` | Every anti-pattern across all constitutions |
| `quick-reference.md` | High-frequency standards grouped by concern |
| `stack-assignment-matrix.md` | Decision framework for assigning technology stacks to new systems |

## Migration
All four index files migrated from the original `indexes/` folder.
```

---

### `protocols/README.md`

```markdown
# Protocols — Operational Procedures

How the Governova governance system operates day-to-day. These are the
executable procedures that make the constitutional standards actionable.

## Files

| File | Purpose |
|------|---------|
| `relay-protocol.md` | The 5-engineer relay model — who does what, in what order, with what permissions |
| `relay-clarification.md` | MINOR vs ARCHITECTURAL fast-path — when to pause the relay and when to proceed |
| `relay-abort.md` | What to do when a relay diverges from the design mid-build |
| `session-lifecycle.md` | The 12-step build session from index load to audit trail seal |
| `git-workflow.md` | Branch model, commit convention, PR process, golden rules |
| `modes/` | Operating modes: personal, team, enterprise |

## Migration
- `workflow/ksdrill-sa-ai-workflow.md` → `protocols/relay-protocol.md`
- `workflow/git-workflow.md` → `protocols/git-workflow.md`
- `overlays/solo-dev-overlay.md` → `protocols/modes/personal-mode.md`
- `overlays/team-overlay.md` → `protocols/modes/team-mode.md`
```

---

### `protocols/modes/README.md`

```markdown
# Modes — Operating Modes

A project declares its operating mode in CONSTITUTION-INDEX.
The mode changes which protocols are active — never the constitutional framework.

| Mode | File | For | Tier |
|------|------|-----|------|
| Personal | `personal-mode.md` | Solo developers | Free, Pro |
| Team | `team-mode.md` | Small teams | Pro+ |
| Enterprise | `enterprise-mode.md` | Organisations | Max, Enterprise |

Enterprise mode is new — it activates the Mapping Engine, certification tracking,
board-level reporting, and constitutional exception recording.
```

---

### `governance/README.md`

```markdown
# Governance — Operational Records

The auditable records of every governance event in the system.
Runbooks respond to incidents. Decisions record architecture choices.
Changelog audits every standard amendment.

## Structure

| Folder | Contents |
|--------|---------|
| `runbooks/` | RB-01 through RB-08 — incident response procedures |
| `decisions/` | ADR-000 through ADR-NNN — architecture decision records |
| `changelog/` | `amendments-log.md` — every standard amendment audited |
```

---

### `governance/runbooks/README.md`

```markdown
# Runbooks — Incident Response Procedures

| ID | File | Trigger |
|----|------|---------|
| RB-01 | `RB-01-sev0-response.md` | Production down or data at risk |
| RB-02 | `RB-02-sev1-response.md` | Functional breakage, security gap |
| RB-03 | `RB-03-financial-freeze.md` | Balance discrepancy detected |
| RB-04 | `RB-04-database-migration.md` | Migration failure or rollback |
| RB-05 | `RB-05-ai-degradation.md` | AI pipeline failure during relay |
| RB-06 | `RB-06-railway-deployment.md` | Backend deployment incident |
| RB-07 | `RB-07-vercel-rollback.md` | Frontend deployment incident |
| RB-08 | `RB-08-relay-abort.md` | AI output diverges from design |

## Migration
RB-01 through RB-07 migrated from original `runbooks/` folder.
RB-08 is new — content specified in the new files section.
```

---

### `governance/decisions/README.md`

```markdown
# Decisions — Architecture Decision Records

Every significant architectural decision made across all systems.
ADRs record: the decision, alternatives considered, the standard that authorised
the chosen approach, and the engineer who made the recommendation.

## File naming
`ADR-{NNN}-{description}.md` — zero-padded three digits.

## Current ADRs
- ADR-000: Template
- ADR-001: FundsLink Academy stack selection
- ADR-002: Maphophe stack selection
- ADR-003: Reserve Bank stack selection
- ADR-004: SyncUp stack selection

## Migration
All ADRs migrated from original `adrs/` folder.
```

---

### `governance/changelog/README.md`

```markdown
# Changelog — Amendment Audit Trail

`amendments-log.md` is the immutable record of every constitutional amendment.
Every entry: date, standard ID, what changed, why, who approved.

This is the audit evidence that Governova's standards are actively maintained
and that every change was reviewed and approved — not edited informally.
```

---

### `platform/README.md`

```markdown
# Platform — The Product

The software that operates on Governova's constitutional database.
Organised into the engine (the runtime) and the surfaces (where developers interact).

## Engine
The central runtime. Every product surface connects to it.
See `engine/SPEC.md` for the full architecture specification.

## Surfaces
Seven surfaces. One engine. Every touchpoint in the development workflow.

| Surface | Description |
|---------|-------------|
| `ide-extension/` | VS Code + Cursor — primary developer interface |
| `jetbrains-plugin/` | IntelliJ + WebStorm — enterprise unlock |
| `cicd-enforcer/` | GitHub Actions + GitLab CI — makes governance non-optional |
| `pr-guardian-bot/` | GitHub + GitLab bot — constitutional PR review |
| `web-dashboard/` | Team and management interface |
| `cli/` | Terminal interface and automation |
| `slack-teams-bot/` | Organisational communication layer |
| `mcp-server/` | Live constitutional database API for AI tools |

## Status
All folders are spec-phase. SPEC.md files define what gets built.
Code is added into these folders as each surface is built.
```

---

### `platform/engine/README.md`

```markdown
# Engine — The Governance Runtime

The central runtime of the Governova platform.
Every product surface connects to it. Every AI tool in the relay queries it.

## Components

| Folder | Component | Purpose |
|--------|-----------|---------|
| `constitutional-store/` | Constitutional Store | Live versioned database of active standards per session |
| `violation-detector/` | Violation Detector | Real-time scanner for AP violations in code diffs and PR content |
| `relay-state-machine/` | Relay State Machine | Tracks relay position, handoffs, permission levels, abort conditions |
| `audit-trail/` | Audit Trail | Immutable append-only record of every AI action |
| `system-knowledge-engine/` | System Knowledge Engine | Generates Why/How/Failure/Fix layers for every file built |
| `mapping-engine/` | Mapping Engine | Translates enterprise standards into a Governova CONSTITUTION-INDEX |
| `intelligence/` | Intelligence Layer | Network effect, temporal governance, pre-build risk assessment |

See `SPEC.md` for the full engine architecture specification.
```

---

### `reference-systems/README.md`

```markdown
# Reference Systems — The Four Flagships

The four KSDRILL SA systems built under full Governova governance.
They are reference implementations — proof that the framework works,
per-domain case studies, and the seed of the domain constitution library.

They are examples. Not boundaries. Governova governs any system in any domain.

## Systems

| System | Domain | Stack | ADR |
|--------|--------|-------|-----|
| `fundslink-academy/` | Fintech + Edtech | Angular + FastAPI | ADR-001 |
| `maphophe/` | Govtech + Community | Next.js | ADR-002 |
| `ksdrill-reserve-bank/` | Fintech + Banking | Angular + FastAPI | ADR-003 |
| `syncup/` | Creator + SaaS | Next.js | ADR-004 |

## Contents per system
Each system folder contains:
- `context.md` — system context file (migrated from `system-contexts/`)
- `CONSTITUTION-INDEX.md` — compiled active constitution for this system
- `README.md` — system overview and governance status
```

---

For every other folder (`platform/engine/*/`, `platform/surfaces/*/`,
`constitution/implementation/*/`, `constitution/domains/*/`,
`reference-systems/*/`) — create a `README.md` with:

```markdown
# {Folder Name}

**Status:** {Spec phase / Planned / Active}

{One sentence describing what this folder will contain.}

See `platform/README.md` (or parent README) for context.
```

**Commit after this step:**
```bash
git add -A
git commit -m "refactor: add README.md to every Governova folder"
```

---

## Part 6 — Migrate All Existing Files

Move every existing file to its new location. Do not modify content.
Use `git mv` for all moves so git tracks the rename history.

```bash
# ── CONSTITUTIONS ────────────────────────────────────────

# C00 — stays at constitution root
git mv constitutions/C00-constitutional-order.md \
       constitution/C00-constitutional-order.md

# Phase 0
git mv constitutions/C01-engineering-standards.md \
       constitution/core/phase-0-foundation/C01-engineering-standards.md

# Phase 1 — constitutions
git mv constitutions/C02-backend-constitution.md \
       constitution/core/phase-1-core-architecture/C02-backend-constitution.md

git mv constitutions/C03-auth-constitution.md \
       constitution/core/phase-1-core-architecture/C03-auth-constitution.md

git mv constitutions/C04-frontend-constitution.md \
       constitution/core/phase-1-core-architecture/C04-frontend-constitution.md

git mv constitutions/C05-database-constitution.md \
       constitution/core/phase-1-core-architecture/C05-database-constitution.md

git mv constitutions/C06-fullstack-architecture-constitution.md \
       constitution/core/phase-1-core-architecture/C06-fullstack-architecture-constitution.md

# Phase 2
git mv constitutions/C07-testing-constitution.md \
       constitution/core/phase-2-quality-reliability/C07-testing-constitution.md

git mv constitutions/C08-platform-reliability-constitution.md \
       constitution/core/phase-2-quality-reliability/C08-platform-reliability-constitution.md

# Phase 3
git mv constitutions/C09-product-feature-constitution.md \
       constitution/core/phase-3-product-intelligence/C09-product-feature-constitution.md

git mv constitutions/C10-ai-collaboration-constitution.md \
       constitution/core/phase-3-product-intelligence/C10-ai-collaboration-constitution.md

# Phase 1 — implementation guides
git mv constitutions/C02-backend-implementation.md \
       constitution/implementation/fastapi/C02-backend-fastapi.md

git mv constitutions/C03-auth-implementation.md \
       constitution/implementation/nextauth/C03-auth-nextauth.md

git mv constitutions/C04-frontend-implementation.md \
       constitution/implementation/nextjs/C04-frontend-nextjs.md

git mv constitutions/C05-database-implementation.md \
       constitution/implementation/prisma-postgresql/C05-database-prisma.md

# ── INDEXES ─────────────────────────────────────────────

git mv indexes/standards-index.md      constitution/indexes/standards-index.md
git mv indexes/anti-patterns-index.md  constitution/indexes/anti-patterns-index.md
git mv indexes/quick-reference.md      constitution/indexes/quick-reference.md
git mv indexes/stack-assignment-matrix.md constitution/indexes/stack-assignment-matrix.md

# ── WORKFLOW → PROTOCOLS ────────────────────────────────

git mv workflow/ksdrill-sa-ai-workflow.md  protocols/relay-protocol.md
git mv workflow/git-workflow.md            protocols/git-workflow.md

# ── OVERLAYS → MODES ────────────────────────────────────

git mv overlays/solo-dev-overlay.md  protocols/modes/personal-mode.md
git mv overlays/team-overlay.md      protocols/modes/team-mode.md

# ── RUNBOOKS → GOVERNANCE/RUNBOOKS ──────────────────────

git mv runbooks/SEV0-response-runbook.md      governance/runbooks/RB-01-sev0-response.md
git mv runbooks/SEV1-response-runbook.md      governance/runbooks/RB-02-sev1-response.md
git mv runbooks/financial-freeze-runbook.md   governance/runbooks/RB-03-financial-freeze.md
git mv runbooks/database-migration-runbook.md governance/runbooks/RB-04-database-migration.md
git mv runbooks/ai-degradation-runbook.md     governance/runbooks/RB-05-ai-degradation.md
git mv runbooks/railway-deployment-runbook.md governance/runbooks/RB-06-railway-deployment.md
git mv runbooks/vercel-rollback-runbook.md    governance/runbooks/RB-07-vercel-rollback.md

# ── ADRS → GOVERNANCE/DECISIONS ─────────────────────────

git mv adrs/ADR-000-template.md         governance/decisions/ADR-000-template.md
git mv adrs/ADR-001-fundslink-stack.md  governance/decisions/ADR-001-fundslink-stack.md
git mv adrs/ADR-002-maphophe-stack.md   governance/decisions/ADR-002-maphophe-stack.md
git mv adrs/ADR-003-reserve-bank-stack.md governance/decisions/ADR-003-reserve-bank-stack.md
git mv adrs/ADR-004-syncup-stack.md     governance/decisions/ADR-004-syncup-stack.md

# ── SYSTEM CONTEXTS → REFERENCE SYSTEMS ─────────────────

git mv system-contexts/fundslink-context.md     reference-systems/fundslink-academy/context.md
git mv system-contexts/maphophe-context.md      reference-systems/maphophe/context.md
git mv system-contexts/reserve-bank-context.md  reference-systems/ksdrill-reserve-bank/context.md
git mv system-contexts/syncup-context.md        reference-systems/syncup/context.md

# ── TEMPLATES ────────────────────────────────────────────
# Templates stay in templates/ — no move needed

# ── REMOVE NOW-EMPTY OLD FOLDERS ────────────────────────
# Git will handle these automatically when all files are moved.
# Verify they are empty before removing:

rmdir constitutions adrs indexes overlays runbooks system-contexts workflow
# If rmdir fails (folder not empty), check for missed files before proceeding.
```

**Commit after this step:**
```bash
git add -A
git commit -m "refactor: migrate all existing files to Governova structure"
```

---

## Part 7 — Create New Files

Create the following new files that do not exist yet.
Content is fully specified below each file path.

---

### `framework/format-specification.md`

```markdown
# Format Specification — Universal Primitive

| Attribute | Value |
|-----------|-------|
| **Layer** | 1 — Framework |
| **Type** | Universal primitive |
| **Applies To** | Every standard, every constitution, every domain, every stack |

---

## Standard ID format

Every standard follows this exact structure:

\`\`\`
S{C}.{N} — {title}
Severity:     SEV0 | SEV1 | SEV2 | SEV3
Phase:        0 | 1 | 2 | 3
Applies To:   [all systems | specific stack | specific domain]
Rule:         [the requirement, stated positively]
Rationale:    [why this standard exists]
Anti-pattern: AP-S{C}.{N}{letter} — [what failure looks like]
\`\`\`

Where:
- `{C}` = constitution number (0–10, or domain/stack identifier)
- `{N}` = standard number within that constitution (sequential, no gaps)
- `{letter}` = anti-pattern variant (a, b, c... for multiple failure modes of one standard)

## ID permanence rule

Standard IDs are **permanent**. Once assigned, an ID is never reused.
A deprecated standard is marked `DEPRECATED` in its rule field and retained
with its deprecation record. It is never deleted. It is never reassigned.

## Implementation binding format

When a universal standard is bound to a specific stack:

\`\`\`
S{C}.{N}/{stack} — {title}
Binds:    S{C}.{N} in the universal core
Stack:    {stack name}
Satisfies by: [exactly how the standard is met in this technology]
Anti-pattern: AP-S{C}.{N}{letter}/{stack} — [stack-specific failure mode]
\`\`\`

## Document structure

Every constitution document must contain, in order:
1. Title block with: Document, Organisation, Version, Status, Locked date,
   Applies To, Phase, Paired With
2. Opening principle quote
3. Table of contents
4. Sections with standards in S{C}.{N} format
5. Amendment log at the end
```

---

### `framework/phase-model.md`

```markdown
# Phase Model — Universal Primitive

| Attribute | Value |
|-----------|-------|
| **Layer** | 1 — Framework |
| **Type** | Universal primitive |
| **Source** | Extracted from C00-constitutional-order.md §6 |

---

The four phases are the read order, the dependency order, and the failure order.

| Phase | Name | Read Before | If Skipped |
|-------|------|-------------|------------|
| 0 | Foundation | Any code is written | No shared definition of done; first PR embeds unremovable patterns |
| 1 | Core Architecture | First line of application code | No boundaries, no auth, no database assignment; first endpoint corrupts all |
| 2 | Quality & Reliability | Any feature is production-ready | Ships without testing strategy, deployment governance, or incident response |
| 3 | Product & Intelligence | Any roadmap or AI session | Product decisions made against unstable technical foundation |

## Phase dependency

Phase 1 depends on Phase 0.
Phase 2 depends on Phase 1.
Phase 3 depends on Phase 2.

C6 (Full-Stack Architecture) is in Phase 1 but depends on all other Phase 1
constitutions — it synthesises C2, C3, C4, C5 rather than introducing new standards.
```

---

### `framework/severity-model.md`

```markdown
# Severity Model — Universal Primitive

| Level | Name | Meaning | Response |
|-------|------|---------|----------|
| SEV0 | Critical | Production down or data at risk | Immediate stop · runbook activation · all hands |
| SEV1 | High | Functional breakage or security gap | Relay pause · Founder approval required |
| SEV2 | Medium | Standard violation, non-critical | Flag in PR review · amendment or documented exception |
| SEV3 | Low | Style, convention, minor deviation | Lint warning · document in commit message |

## Violation weighting in Governova Score

| Severity | Score weight |
|----------|-------------|
| SEV0 | 5× |
| SEV1 | 5× |
| SEV2 | 2× |
| SEV3 | 1× |

## SEV0 trigger conditions (non-exhaustive)

- Production database unreachable
- Balance discrepancy detected in financial system
- Authentication bypass detected
- Data exfiltration pattern detected
- Deployment has corrupted production state
```

---

### `framework/permission-model.md`

```markdown
# Permission Model — Universal Primitive

| Level | Name | What the AI engineer may do |
|-------|------|-----------------------------|
| L1 | Propose | Suggest architectural decisions, designs, approaches |
| L2 | Recommend | Produce detailed implementation plans with cited standard IDs |
| L3 | Implement | Write code, create files, make changes — within approved spec only |
| L4 | Approve | **Human only. Always. No exceptions.** |

## The L4 rule

L4 is permanently human-only. It cannot be delegated.
It cannot be elevated by prompt, by instruction, or by configuration.
Any AI tool that approves its own output has committed a SEV1 violation.

## AI engineer permission assignments

| Engineer | Permission | Notes |
|----------|-----------|-------|
| Claude | L1, L2 | Design and recommendation only. Never builds. |
| Claude Code | L2, L3 | Builds. Cannot approve its own output. |
| ChatGPT | L1, L2, L3 | Debug, UI, adversarial review |
| DeepSeek | L1, L2 | Reasoning and algorithm analysis |
| Kimi | L1 | Experimental — proposals only |
| Founder | L4 | Every handoff checkpoint. Cannot be skipped. |
```

---

### `framework/conflict-resolution.md`

```markdown
# Conflict Resolution — Universal Primitive

| Attribute | Value |
|-----------|-------|
| **Source** | Extracted from C00-constitutional-order.md §7 |

---

## Constitutional hierarchy (highest to lowest authority)

\`\`\`
C0  — Constitutional Order      ← Supreme. Governs the governance system.
C3  — Auth Constitution         ← Security decisions. Highest domain authority.
C2  — Backend Constitution      ← Architecture and API contract decisions.
C5  — Database Constitution     ← Data storage and integrity decisions.
C4  — Frontend Constitution     ← UI, client-side, and rendering decisions.
C6  — Full-Stack Architecture   ← Integration, stack assignment, topology.
C1  — Engineering Standards     ← Process, workflow, code quality.
C7  — Testing Constitution      ← Quality validation and coverage.
C8  — Platform Reliability      ← Deployment and operational decisions.
C9  — Product & Feature         ← Product scope and feature decisions.
C10 — AI Collaboration          ← AI governance and permission boundaries.
\`\`\`

The hierarchy governs conflicts — not importance.
C9 and C10 are last because product and AI decisions must yield to technical correctness.

## Four-step resolution protocol

**Step 1 — Verify the conflict is real.**
Check whether one constitution has a stack-scope qualifier that resolves the apparent
conflict. Most apparent conflicts dissolve at this step.

**Step 2 — Apply hierarchy.**
The constitution higher in the hierarchy governs.

**Step 3 — If hierarchy does not resolve it, it is a genuine gap.**
Open a constitutional amendment issue. Cite both conflicting standards.
No implementation decision is made until resolved.
Do not improvise. Do not ask AI to decide.

**Step 4 — Document the resolution.**
Update both affected constitutions' amendment logs.
```

---

### `framework/amendment-protocol.md`

```markdown
# Amendment Protocol — Universal Primitive

| Attribute | Value |
|-----------|-------|
| **Source** | Extracted from C00-constitutional-order.md §8 |

---

## When an amendment is required

| Requires amendment | Does NOT require amendment |
|--------------------|---------------------------|
| Adding a new standard | Fixing a typo (editorial — commit directly) |
| Removing a standard | Updating a code example in an implementation guide |
| Changing a standard's scope | Adding a system context file |
| Changing a standard's severity | Adding a new runbook |
| Restructuring a constitution | Adding a new ADR |
| Any change to C0 | Updating a template |

## Solo dev amendment protocol (3 steps)

**Step 1 — Document the gap.** Create a GitHub Issue tagged `constitutional-amendment`.
Include: which constitution, which standard ID, why the current standard is insufficient,
the proposed new standard text in full. Evidence required.

**Step 2 — AI adversarial review.** Paste the amendment to Claude:
*"Review this constitutional amendment for unintended consequences, cross-constitution
conflicts, and whether the evidence justifies the change."*
Paste Claude's response to a second AI for a challenge.
Document both responses in the GitHub Issue.

**Step 3 — 24-hour personal review.** The amendment sits for 24 hours minimum.
No exceptions.

## Amendment log entry format

Every approved amendment is recorded in `governance/changelog/amendments-log.md`:

\`\`\`
| Date | Standard ID | Change | Rationale | Approved by |
|------|-------------|--------|-----------|-------------|
| YYYY-MM-DD | S{C}.{N} | [what changed] | [why] | [Founder] |
\`\`\`
```

---

### `governance/changelog/amendments-log.md`

```markdown
# Amendments Log — Constitutional Audit Trail

> Every standard amendment is recorded here. This is an append-only audit trail.
> No entry is ever edited or deleted.

---

| Attribute | Value |
|-----------|-------|
| **Document** | Constitutional Amendments Log |
| **Version** | v1.0 |
| **Status** | Active — append only |
| **Created** | 2026-05-22 |

---

## Amendment Record

| Date | Standard ID | Constitution | Change | Rationale | Approved by |
|------|-------------|--------------|--------|-----------|-------------|
| 2026-05-22 | — | All | Initial Governova restructure — no standards changed, only repo structure | Governova v2.0 architecture | Maluleke Kurhula Success |

---

*This log is the compliance evidence that Governova's standards are actively maintained
and that every change was reviewed and approved through the amendment protocol.*
```

---

### `protocols/relay-clarification.md`

```markdown
# Relay Clarification Protocol

| Attribute | Value |
|-----------|-------|
| **Governed by** | C10 — AI Collaboration Constitution |
| **Permission required** | L3 for MINOR · L4 for ARCHITECTURAL |

---

## The problem this solves

Not every question mid-relay requires a full pause and Founder approval.
A full pause for minor questions creates friction that leads engineers to skip
the relay protocol entirely — which is worse than having a faster legitimate path.

This protocol classifies every mid-relay question before routing it.

---

## Classification

| Class | Definition | Examples | Action |
|-------|-----------|---------|--------|
| `MINOR` | Implementation detail within the approved spec | Nullable vs required field, error message wording, variable naming | Claude Code decides, documents in commit message, flags in handoff report |
| `ARCHITECTURAL` | Changes the design, security model, database assignment, or crosses a constitutional standard | Auth strategy change, new database introduced, API contract change, any SEV0/SEV1 concern | Full relay pause, return to Claude (Design), Founder approval before resuming |

## When in doubt

If you are uncertain whether a question is MINOR or ARCHITECTURAL — it is ARCHITECTURAL.
Escalate. Do not decide.

## MINOR decision record format

In the commit message:
\`\`\`
feat: implement patient entity

MINOR DECISION: field `date_of_birth` made nullable (not required) —
rationale: optional for patient creation, collected at onboarding.
No constitutional standard violated.
\`\`\`
```

---

### `protocols/relay-abort.md`

```markdown
# Relay Abort Protocol — RB-08

| Attribute | Value |
|-----------|-------|
| **Severity** | SEV1 |
| **Trigger** | AI output diverges significantly from Claude's approved design |
| **Governed by** | C10 — AI Collaboration Constitution |

---

## Trigger conditions

Activate this protocol when any of the following are true:

- Claude Code has built files or structure not present in Claude's design spec
- Claude Code has made an ARCHITECTURAL decision without Founder approval
- The output contradicts a constitutional standard (any severity)
- The relay position is ambiguous and cannot be recovered without redesign
- A SEV0 violation is detected in Claude Code's output

## Protocol steps

**Step 1 — Stop immediately.**
Claude Code stops all build activity. No further files are created or modified.

**Step 2 — Commit current state to abort branch.**
\`\`\`bash
git add -A
git commit -m "relay-abort: state at point of divergence — [brief description]"
git checkout -b relay-abort/[session-date]-[brief-description]
git push origin relay-abort/[session-date]-[brief-description]
\`\`\`

**Step 3 — Document the divergence.**
Open a GitHub Issue in the Governova repo:
- Title: `[RELAY ABORT] [brief description]`
- Tag: `relay-abort`, `constitutional-review`
- Body: Which design spec was being followed, what divergence occurred,
  which standard was violated or which decision was made without authority,
  the commit hash of the abort state.

**Step 4 — Founder reviews.**
Founder reviews the abort branch and the GitHub Issue.
Two outcomes: (A) Divergence is acceptable — create amendment and continue.
(B) Divergence is not acceptable — relay re-enters at Claude (Design) for redesign.

**Step 5 — Re-enter relay at Claude (Design).**
Before resuming, Claude reads the abort Issue and the original design spec.
Claude produces a revised design spec that resolves the divergence.
Founder approves. Relay resumes at Step 1 from the relay protocol.
```

---

### `protocols/modes/enterprise-mode.md`

```markdown
# Enterprise Mode — Operating Mode

| Attribute | Value |
|-----------|-------|
| **Mode** | Enterprise |
| **Activates** | Mapping Engine · Certification tracking · Board reporting · Exception recording |
| **Tier** | Max · Enterprise contracts |
| **Adds to** | Team mode (enterprise mode is a superset) |

---

## What enterprise mode activates

**Constitutional Mapping Engine.** The enterprise's existing standards are ingested,
mapped to Governova's constitutional database, and a CONSTITUTION-INDEX is produced
in the enterprise's own language and format. See GOVERNOVA-MASTER.md §14.

**Certification tracking.** The Governova Score is monitored against certification
thresholds (≥85 for Standard, ≥92 for Advanced, ≥95 for Enterprise).
Certification readiness is surfaced in the web dashboard.

**Board-level governance report.** Auto-generated monthly. One page. Plain English.
Red/amber/green per constitutional area. AI action volume. Governance events.

**Constitutional exception recording.** When the enterprise overrides a Governova
standard, the exception is formally recorded with date, approver, rationale, and
scheduled review date. No exception is invisible.

**Multi-approver relay.** The L4 approval checkpoint can be distributed across
multiple named approvers with defined authority domains. Requires a documented
approval matrix in the CONSTITUTION-INDEX.

---

## CONSTITUTION-INDEX additions for enterprise mode

\`\`\`yaml
mode: enterprise
approval_matrix:
  security_decisions: [CISO name]
  architecture_decisions: [CTO name]
  production_releases: [Engineering Lead name]
certification_target: advanced
constitutional_exceptions: []  # populated as exceptions are recorded
board_report: monthly
\`\`\`
```

---

### `governance/changelog/amendments-log.md` (already specified above)

---

### `platform/engine/SPEC.md`

```markdown
# Governova Engine — Architecture Specification

| Attribute | Value |
|-----------|-------|
| **Document** | Engine Architecture Specification |
| **Status** | Spec phase — pre-build |
| **Version** | v1.0 |

---

## Overview

The governance engine is the central runtime of the Governova platform.
Every product surface connects to it. Every AI tool in the relay queries it.

## Seven components

| Component | Folder | Purpose |
|-----------|--------|---------|
| Constitutional Store | `constitutional-store/` | Live versioned database of active standards per session |
| Violation Detector | `violation-detector/` | Real-time AP violation scanning |
| Relay State Machine | `relay-state-machine/` | Relay position, handoffs, permissions, abort conditions |
| Audit Trail | `audit-trail/` | Immutable append-only record of every AI action |
| System Knowledge Engine | `system-knowledge-engine/` | Generates Why/How/Failure/Fix per file |
| Mapping Engine | `mapping-engine/` | Enterprise standard translation |
| Intelligence | `intelligence/` | Network effect, temporal governance, pre-build risk |

## Technology stack (planned)

- Runtime: FastAPI (Python)
- Database: PostgreSQL (constitutional store, audit trail)
- Cache: Redis (active session index, relay state)
- Queue: BullMQ (violation scanning, Bible generation jobs)
- Hosting: Railway

## Build order

1. Constitutional Store + Violation Detector (core — everything else depends on these)
2. Relay State Machine + Audit Trail (governance layer)
3. System Knowledge Engine (documentation layer)
4. Mapping Engine (enterprise layer)
5. Intelligence (network layer — requires user base)

## API contract (draft)

\`\`\`
GET  /standard/{id}                 → StandardRecord
GET  /constitution/{project_id}     → CompiledIndex
POST /violation/check               → ViolationReport
GET  /anti-pattern/{id}             → AntiPatternRecord
GET  /relay/{session_id}/state      → RelayState
POST /audit/log                     → AuditEntry
GET  /runbook/{incident_type}       → RunbookContent
POST /temporal/flag/{standard_id}   → TemporalFlag
\`\`\`
```

---

### `scripts/validate-integrity.py`

```python
#!/usr/bin/env python3
"""
Governova — Constitutional Integrity Validator
Checks that every S{C}.{N} and AP-S{C}.{N}{letter} reference in the repo
resolves to a real standard in the constitution core.

Usage:
  python scripts/validate-integrity.py
  python scripts/validate-integrity.py --strict   (fails on SEV3 gaps)

Exit codes:
  0 — All references resolve
  1 — Unresolved references found
  2 — Script error
"""

import os
import re
import sys
import argparse
from pathlib import Path


STANDARD_PATTERN = re.compile(r'\bS(\d+)\.(\d+)\b')
ANTI_PATTERN_PATTERN = re.compile(r'\bAP-S(\d+)\.(\d+)([a-z])\b')
CONSTITUTION_DIR = Path('constitution/core')
SCAN_DIRS = [
    'constitution',
    'protocols',
    'governance',
    'framework',
    'reference-systems',
    'templates',
]


def extract_defined_standards(constitution_dir: Path) -> set[str]:
    """Extract all S{C}.{N} IDs defined in constitution files."""
    defined = set()
    for md_file in constitution_dir.rglob('*.md'):
        content = md_file.read_text(encoding='utf-8')
        for match in STANDARD_PATTERN.finditer(content):
            # Only count definitions (lines starting with S{C}.{N})
            line_start = content.rfind('\n', 0, match.start()) + 1
            line = content[line_start:content.find('\n', match.end())]
            if line.strip().startswith(f'S{match.group(1)}.{match.group(2)}'):
                defined.add(f'S{match.group(1)}.{match.group(2)}')
    return defined


def extract_references(scan_dirs: list[str]) -> dict[str, list[tuple[str, int]]]:
    """Extract all S{C}.{N} references with their file and line number."""
    references = {}
    for scan_dir in scan_dirs:
        for md_file in Path(scan_dir).rglob('*.md'):
            content = md_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            for line_num, line in enumerate(lines, 1):
                for match in STANDARD_PATTERN.finditer(line):
                    std_id = f'S{match.group(1)}.{match.group(2)}'
                    if std_id not in references:
                        references[std_id] = []
                    references[std_id].append((str(md_file), line_num))
    return references


def main():
    parser = argparse.ArgumentParser(description='Validate Governova constitutional integrity')
    parser.add_argument('--strict', action='store_true', help='Fail on any unresolved reference')
    args = parser.parse_args()

    print('Governova Constitutional Integrity Validator')
    print('=' * 50)

    if not CONSTITUTION_DIR.exists():
        print(f'ERROR: Constitution directory not found: {CONSTITUTION_DIR}')
        sys.exit(2)

    print(f'Scanning defined standards in {CONSTITUTION_DIR}...')
    defined = extract_defined_standards(CONSTITUTION_DIR)
    print(f'Found {len(defined)} defined standards.')

    print(f'Scanning references in {SCAN_DIRS}...')
    references = extract_references(SCAN_DIRS)
    print(f'Found {len(references)} unique standard references.')

    unresolved = {sid: locs for sid, locs in references.items() if sid not in defined}

    if not unresolved:
        print('\n✓ All references resolve. Integrity check passed.')
        sys.exit(0)

    print(f'\n✗ {len(unresolved)} unresolved references found:')
    for std_id, locations in sorted(unresolved.items()):
        print(f'\n  {std_id} — not found in constitution core')
        for filepath, line_num in locations[:3]:  # show first 3 occurrences
            print(f'    {filepath}:{line_num}')
        if len(locations) > 3:
            print(f'    ... and {len(locations) - 3} more')

    sys.exit(1)


if __name__ == '__main__':
    main()
```

---

### `QUICKSTART.md`

```markdown
# Governova — Quick Start

> **10 steps from zero to first governed commit on a new project.**

---

## Prerequisites

- This repo cloned: `git clone https://github.com/MALULEKE-KS/governova.git`
- Your project repo initialised with `main` and `dev` branches
- Python 3.11+ (for the integrity validator)

---

## Step 1 — Identify your domain and stack

Consult `constitution/indexes/stack-assignment-matrix.md`.
Decide: which domain(s) apply? Which stack?

KSDRILL SA reference assignments:
- Content/SEO system → Next.js
- Enterprise/financial/AI system → Angular + FastAPI

---

## Step 2 — Create your CONSTITUTION-INDEX

Copy the template:
```bash
cp templates/CONSTITUTION-INDEX-template.md your-project/CONSTITUTION-INDEX.md
```

Fill in:
- `project:` your project name
- `domain:` your domain(s)
- `stack:` your stack(s)
- `mode:` personal | team | enterprise

---

## Step 3 — Read Phase 0 before writing a line of code

```bash
cat constitution/core/phase-0-foundation/C01-engineering-standards.md
```

No code until Phase 0 is read. No exceptions.

---

## Step 4 — Read Phase 1 before the first application file

Read in order:
1. `constitution/core/phase-1-core-architecture/C02-backend-constitution.md`
2. `constitution/implementation/fastapi/C02-backend-fastapi.md` (if using FastAPI)
3. `constitution/core/phase-1-core-architecture/C03-auth-constitution.md`
4. `constitution/implementation/nextauth/C03-auth-nextauth.md`
5. `constitution/core/phase-1-core-architecture/C04-frontend-constitution.md`
6. Your stack's frontend implementation guide
7. `constitution/core/phase-1-core-architecture/C05-database-constitution.md`
8. Your stack's database implementation guide(s)
9. `constitution/core/phase-1-core-architecture/C06-fullstack-architecture-constitution.md`

---

## Step 5 — Validate the integrity of your constitution index

```bash
python scripts/validate-integrity.py
```

All references must resolve before the first build session.

---

## Step 6 — Read Phase 2 before marking anything production-ready

```bash
cat constitution/core/phase-2-quality-reliability/C07-testing-constitution.md
cat constitution/core/phase-2-quality-reliability/C08-platform-reliability-constitution.md
```

---

## Step 7 — Read Phase 3 before AI sessions or roadmap decisions

```bash
cat constitution/core/phase-3-product-intelligence/C09-product-feature-constitution.md
cat constitution/core/phase-3-product-intelligence/C10-ai-collaboration-constitution.md
cat protocols/relay-protocol.md
```

---

## Step 8 — Set up your relay

Confirm which AI engineer is active. Load AI-INSTRUCTIONS.md + your CONSTITUTION-INDEX.
The relay reads `constitution/C00-constitutional-order.md` as the master reference.

---

## Step 9 — Create your first Issue and branch

```bash
# Create Issue in GitHub first (#1 — setup project architecture)
git checkout dev
git pull origin dev
git checkout -b feature/1-setup-architecture
```

---

## Step 10 — Build under the relay

Follow `protocols/relay-protocol.md` for every build session.
Every decision is documented. Every violation is caught before commit.
Every file gets its System Bible entry.

---

*You are now governed.*
```

---

### `CONTRIBUTING.md`

```markdown
# Contributing to Governova

Governova's constitutional database grows through governed contributions.
Domain and stack constitutions can be contributed by domain experts.

## What can be contributed

- **Domain constitutions** — industry-specific extensions (e.g., healthtech, e-commerce)
- **Stack implementation bindings** — how universal standards are satisfied in a specific technology

## What cannot be contributed

- Changes to the universal core (C00–C10)
- Changes to the framework primitives
- Changes to the permission model or relay protocol

These are maintained exclusively by KSDRILL SA.

## Contribution process

1. Fork the Governova repository
2. Create a branch: `contribution/{domain-or-stack}-constitution`
3. Write your constitution following `framework/format-specification.md` exactly
4. Include for each standard: ID, severity, phase, applies-to, rule, rationale, anti-pattern
5. Write a conflict analysis against the universal core (which standards does your
   domain extension interact with? Do any conflict?)
6. Open a pull request with the tag `domain-contribution` or `stack-contribution`
7. The Governova review process runs adversarial AI review + conflict check
8. Approved contributions are merged and the contributor is enrolled in revenue share

## Quality bar

A contribution that fails adversarial AI review is returned for revision.
A contribution with unresolved conflicts against the universal core is not merged.
A contribution without evidence (regulatory basis, production experience, case study)
is not considered.

Evidence is required. Personal preference is not evidence.
```

---

### `governance/runbooks/RB-08-relay-abort.md`

```markdown
# RB-08 — Relay Abort Runbook

| Attribute | Value |
|-----------|-------|
| **ID** | RB-08 |
| **Trigger** | AI output diverges significantly from approved design |
| **Severity** | SEV1 |
| **Governed by** | C10 · protocols/relay-abort.md |

---

## When to activate

- Claude Code has built files not present in Claude's design spec
- Claude Code has made an ARCHITECTURAL decision without Founder approval
- The output contradicts a constitutional standard
- The relay position is ambiguous and unrecoverable
- A SEV0 violation is detected in Claude Code's output

## Response steps

**Step 1 — Stop.** No further files created or modified.

**Step 2 — Commit abort state.**
```bash
git add -A
git commit -m "relay-abort: [brief description of divergence]"
git checkout -b relay-abort/$(date +%Y-%m-%d)-[description]
git push origin relay-abort/$(date +%Y-%m-%d)-[description]
```

**Step 3 — Open GitHub Issue.**
Title: `[RELAY ABORT] [brief description]`
Tags: `relay-abort` `constitutional-review`
Body: Original design spec reference · divergence description · standard violated ·
abort commit hash.

**Step 4 — Founder review.**

**Step 5 — Re-enter relay at Claude (Design).**
Claude reads abort Issue + original spec.
Claude produces revised spec.
Founder approves.
Relay resumes from Step 1.

## Recovery time target
SEV1 — resolve within the same build session where possible.
```

---

**Commit after this step:**
```bash
git add -A
git commit -m "refactor: create all new Governova files — framework, protocols, governance, platform, scripts"
```

---

## Part 8 — Update Root Documents

### Update `README.md` — complete replacement

Replace the entire `README.md` content with:

```markdown
# Governova

> *"AI can build anything. It is us who must tell it exactly what to build,
> how to build it, what not to build, and who approves every decision."*

[![Status](https://img.shields.io/badge/Status-LOCKED-red)](GOVERNOVA-MASTER.md)
[![Version](https://img.shields.io/badge/Version-v2.0-blue)](GOVERNOVA-MASTER.md)
[![Constitutions](https://img.shields.io/badge/Constitutions-11-purple)](constitution/core/)
[![Phases](https://img.shields.io/badge/Phases-4-teal)](framework/phase-model.md)
[![Locked](https://img.shields.io/badge/Locked-2026--05--22-orange)](GOVERNOVA-MASTER.md)

---

**Governova** is the world's first AI development governance platform.
The constitutional layer between AI capability and enterprise trust.

[→ Read the full vision: GOVERNOVA-MASTER.md](GOVERNOVA-MASTER.md)

---

## What it is

Governova tells AI tools exactly what to build, how to build it, what not to build,
and who approves every decision — for any system, any domain, any stack, any scale.
It records every AI action in an immutable audit trail and generates complete
documentation for every file ever built.

## Four-layer architecture

| Layer | Folder | Description |
|-------|--------|-------------|
| 1 — Framework | `framework/` | Universal primitives: format, phases, severity, permissions, hierarchy |
| 2 — Core | `constitution/core/` | 11 constitutions across 4 phases — universal standards as principles |
| 3 — Implementation | `constitution/implementation/` | Stack-specific bindings of core standards |
| 4 — Domains | `constitution/domains/` | Industry-specific extensions |

## Quick start

```bash
# Clone alongside your project
git clone https://github.com/MALULEKE-KS/governova.git

# First — read the master document
cat GOVERNOVA-MASTER.md

# Start a new governed project
cat QUICKSTART.md
```

## Repository structure

```
governova/
├── GOVERNOVA-MASTER.md          # Source of truth — read this first
├── QUICKSTART.md                # 10-step new project setup
├── framework/                   # Layer 1: universal primitives
├── constitution/                # Layers 2–4: the standards database
│   ├── C00-constitutional-order.md
│   ├── core/                    # By phase (Phase 0–3)
│   ├── implementation/          # Stack bindings
│   ├── domains/                 # Domain extensions
│   └── indexes/                 # Fast lookup
├── protocols/                   # How the system operates
├── governance/                  # Operational records
│   ├── runbooks/                # RB-01 – RB-08
│   ├── decisions/               # ADRs
│   └── changelog/               # Amendment audit trail
├── platform/                    # The product (engine + surfaces)
├── reference-systems/           # 4 flagship implementations
├── templates/                   # Instantiation templates
└── scripts/                     # validate-integrity · compile-constitution
```

---

*Built by Maluleke Kurhula Success · KSDRILL SA · 2026*
```

---

### Update `AI-INSTRUCTIONS.md`

Update the following sections only — do not change constitutional content:

**Section: "What This Repo Is"** — Update paragraph 1:

Replace:
> `system-design-template` is the constitutional governance system...

With:
> `governova` is the constitutional governance system for all KSDRILL SA engineering work
> and the foundation of the Governova AI development governance platform. It contains 11
> constitutions organised in 4 phases across a 4-layer architecture, 4 implementation
> guides, framework primitives, protocols, runbooks, and reference system contexts.
> Full platform vision: `GOVERNOVA-MASTER.md`.

**Section: "Where files are now"** — Add after the relay table:

```markdown
## Repository structure

All files follow the Governova four-layer structure.
Read `MANIFEST.md` for the complete navigation map.
Read `GOVERNOVA-MASTER.md` for the full platform vision.

Key paths:
- Constitutions: `constitution/core/phase-{N}-{name}/`
- Implementation guides: `constitution/implementation/{stack}/`
- Relay protocol: `protocols/relay-protocol.md`
- Session lifecycle: `protocols/session-lifecycle.md`
- Runbooks: `governance/runbooks/RB-{NN}-*.md`
- System contexts: `reference-systems/{system}/context.md`
```

---

### Update `MANIFEST.md`

The MANIFEST needs a full rewrite to reflect the new structure. This is a large file
so rewrite it section by section. The key structural changes:

1. **Session Reading Order table** — update all file paths to new locations:
   - `workflow/ksdrill-sa-ai-workflow.md` → `protocols/relay-protocol.md`
   - `constitutions/C{N}-*.md` → `constitution/core/phase-{N}-{name}/C{NN}-*.md`
   - `indexes/` → `constitution/indexes/`
   - `system-contexts/{system}-context.md` → `reference-systems/{system}/context.md`

2. **File Clusters** — reorganise by the new folder structure:
   - Cluster 0: Session Entry (AI-INSTRUCTIONS, MANIFEST, GOVERNOVA-MASTER)
   - Cluster 1: Framework Layer
   - Cluster 2: Governance Root (C00)
   - Clusters 3–6: Phase 0–3 constitutions
   - Cluster 7: Implementation bindings
   - Cluster 8: Domain extensions
   - Cluster 9: Indexes
   - Cluster 10: Protocols
   - Cluster 11: Governance (runbooks, decisions, changelog)
   - Cluster 12: Platform (engine spec, surfaces)
   - Cluster 13: Reference Systems
   - Cluster 14: Templates + Scripts

3. **Complete File Index** — update every path to its new location.

4. **Add GOVERNOVA-MASTER.md** to Cluster 0 (Session Entry) as the second file read,
   after AI-INSTRUCTIONS.md.

**Commit after this step:**
```bash
git add -A
git commit -m "refactor: update README, AI-INSTRUCTIONS, MANIFEST to Governova structure"
```

---

## Part 9 — Add Missing Templates

Create these templates that the platform needs:

### `templates/domain-constitution-template.md`

```markdown
# {Domain Name} Domain Constitution

| Attribute | Value |
|-----------|-------|
| **Document** | {Domain} Domain Constitution |
| **Layer** | 4 — Domain Extension |
| **Extends** | Universal Core (C00–C10) |
| **Regulatory basis** | {regulations this domain is based on} |
| **Contributed by** | {author} |
| **Version** | v1.0 |
| **Status** | DRAFT |

---

> *{Opening principle for this domain}*

---

## Domain overview

{What this domain covers and why it needs additional governance.}

## Standards

### D-{DOMAIN}.1 — {Standard title}

| Field | Value |
|-------|-------|
| **Severity** | SEV{0-3} |
| **Applies To** | {all systems in domain / specific stack} |
| **Rule** | {The requirement} |
| **Rationale** | {Why this domain requires this beyond the universal core} |
| **Anti-pattern** | AP-D-{DOMAIN}.1a — {What failure looks like} |

---

## Conflict analysis

{List every universal core standard this domain extension interacts with
and confirm there are no conflicts. If there are apparent conflicts, resolve them.}

| Core Standard | Interaction | Resolved? |
|---------------|-------------|-----------|
| S{C}.{N} | {how they interact} | Yes — {resolution} |
```

---

### `templates/implementation-guide-template.md`

```markdown
# {Stack Name} Implementation Guide — C{N} {Constitution Name}

| Attribute | Value |
|-----------|-------|
| **Document** | C{N} {Constitution} — {Stack} Implementation Bindings |
| **Layer** | 3 — Implementation |
| **Binds** | `constitution/core/phase-{N}-{name}/C{NN}-{name}-constitution.md` |
| **Stack** | {Stack name and version} |
| **Version** | v1.0 |

---

## How to use this guide

This guide shows how each universal standard from C{N} is satisfied in {stack}.
Read the constitution first. Then read this guide for the stack-specific patterns.

## Standard bindings

### S{C}.{N}/{stack} — {Standard title}

**Universal rule (from C{N}):**
> {Exact text of the universal standard}

**{Stack} binding:**
{Exactly how this standard is satisfied in this technology.
Include code patterns, file locations, configuration.}

**{Stack} anti-pattern:**
`AP-S{C}.{N}a/{stack}` — {What failure looks like specifically in this stack}
```

---

**Commit after this step:**
```bash
git add -A
git commit -m "refactor: add domain and implementation guide templates"
```

---

## Part 10 — Final Verification

Run these checks before opening the PR:

```bash
# 1. Verify the full structure exists
find . -type d | sort | grep -v '.git'

# 2. Confirm no old folders remain
ls constitutions/ 2>/dev/null && echo "ERROR: constitutions/ still exists" || echo "OK"
ls adrs/ 2>/dev/null && echo "ERROR: adrs/ still exists" || echo "OK"
ls indexes/ 2>/dev/null && echo "ERROR: indexes/ still exists" || echo "OK"
ls overlays/ 2>/dev/null && echo "ERROR: overlays/ still exists" || echo "OK"
ls runbooks/ 2>/dev/null && echo "ERROR: runbooks/ still exists" || echo "OK"
ls system-contexts/ 2>/dev/null && echo "ERROR: system-contexts/ still exists" || echo "OK"
ls workflow/ 2>/dev/null && echo "ERROR: workflow/ still exists" || echo "OK"

# 3. Confirm all constitutions are in their phase folders
ls constitution/core/phase-0-foundation/
ls constitution/core/phase-1-core-architecture/
ls constitution/core/phase-2-quality-reliability/
ls constitution/core/phase-3-product-intelligence/

# 4. Confirm GOVERNOVA-MASTER.md is at root
ls GOVERNOVA-MASTER.md && echo "OK" || echo "ERROR: GOVERNOVA-MASTER.md missing"

# 5. Run integrity validator
python scripts/validate-integrity.py

# 6. Count total files
find . -name "*.md" | grep -v '.git' | wc -l
```

Expected after restructure:
- All 7 old folders removed
- All 15 original constitution files in their phase folders
- GOVERNOVA-MASTER.md at root
- All README.md files in every new folder
- framework/ has 6 new documents
- governance/changelog/amendments-log.md exists
- protocols/relay-clarification.md and relay-abort.md exist
- scripts/validate-integrity.py exists
- QUICKSTART.md and CONTRIBUTING.md at root

**Final commit:**
```bash
git add -A
git commit -m "refactor: Governova restructure complete — v2.0 — all parts verified"
```

---

## Part 11 — Open Pull Request

```bash
git push origin refactor/governova-restructure
```

Open PR on GitHub:
- **Title:** `refactor: Governova v2.0 restructure — four-layer constitutional architecture`
- **Base:** `dev`
- **Body:**

```
Closes #[issue number if one exists]

## What this PR does
Full restructure of system-design-template into the Governova platform architecture.

## Changes
- Renames repo identity from system-design-template to Governova
- Adds GOVERNOVA-MASTER.md v2.0 at root (the complete platform vision and source of truth)
- Creates four-layer constitutional architecture: framework/ · constitution/ · protocols/ · governance/
- Migrates all 15 constitutions to phase-organised folders (Phase 0–3)
- Migrates implementation guides to constitution/implementation/{stack}/
- Migrates runbooks to governance/runbooks/ with RB-NN naming
- Migrates ADRs to governance/decisions/
- Migrates system contexts to reference-systems/{system}/context.md
- Migrates indexes to constitution/indexes/
- Migrates workflow and overlays to protocols/ and protocols/modes/
- Creates platform/ folder structure for the product (engine + surfaces)
- Creates framework/ layer with 6 universal primitive documents
- Creates new protocols: relay-clarification, relay-abort, enterprise-mode
- Adds amendments-log.md, QUICKSTART.md, CONTRIBUTING.md
- Adds validate-integrity.py script
- Adds README.md to every folder
- Updates AI-INSTRUCTIONS.md, README.md, MANIFEST.md

## Constitutional note
No standard content (S{C}.{N} rules) was changed.
This is a pure structural refactor. Standards are identical, locations have changed.

## Verification
- [ ] All 7 old folders removed
- [ ] All constitutions in phase folders
- [ ] GOVERNOVA-MASTER.md at root
- [ ] validate-integrity.py passes
- [ ] All README.md files present
```

**After Founder (L4) approves PR — merge to `dev` using squash merge.**

---

## Summary: What you will have when done

```
governova/                           ← renamed identity
├── GOVERNOVA-MASTER.md              ← THE SOURCE OF TRUTH
├── QUICKSTART.md                    ← 10-step new project setup
├── CONTRIBUTING.md                  ← domain contribution process
├── AI-INSTRUCTIONS.md               ← updated for new paths
├── MANIFEST.md                      ← complete rewritten navigation map
├── README.md                        ← Governova public face
├── framework/                       ← 6 universal primitive documents (NEW)
├── constitution/
│   ├── C00-constitutional-order.md
│   ├── core/                        ← 11 constitutions by phase (MIGRATED)
│   ├── implementation/              ← 4 implementation guides (MIGRATED + split)
│   ├── domains/                     ← 4 active domains (NEW)
│   └── indexes/                     ← 4 indexes (MIGRATED)
├── protocols/                       ← relay + git + modes (MIGRATED + NEW)
├── governance/
│   ├── runbooks/                    ← 8 runbooks (MIGRATED + RB-08 NEW)
│   ├── decisions/                   ← 5 ADRs (MIGRATED)
│   └── changelog/                   ← amendments-log (NEW)
├── platform/                        ← engine SPEC + 8 surfaces (NEW)
├── reference-systems/               ← 4 system contexts (MIGRATED)
├── templates/                       ← existing + 2 new templates
└── scripts/                         ← validate-integrity.py (NEW)
```

---

*These instructions are the complete operating spec for this Claude Code session.
Everything you need is here. Nothing is left to interpretation.*

*Maluleke Kurhula Success · KSDRILL SA · Governova v2.0 · 2026-05-22*
MASTERDOC