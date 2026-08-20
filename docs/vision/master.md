# Governova

---

| Attribute | Value |
|-----------|-------|
| **Document** | Master Architecture & Vision Document |
| **Organisation** | KSDRILL SA |
| **Product** | Governova — AI Development Governance Platform |
| **Version** | v2.0 |
| **Status** | LOCKED |
| **Locked** | 2026-05-22 |
| **Supersedes** | v1.0 (corrected constitution mapping, four-phase model, four-layer architecture) |
| **Next Review** | 2026-08-22 |
| **Authors** | Maluleke Kurhula Success · Claude (Anthropic) |
| **Classification** | Foundational — Source of Truth |

---

> *"AI can build anything. It is us who must tell it exactly what to build, how to build it, what not to build, and who approves every decision. Governova is the system that makes that possible."*

---

## Table of Contents

| # | Section |
|---|---------|
| 1 | Vision Statement |
| 2 | The Problem |
| 3 | What Governova Is |
| 4 | Core Philosophy |
| 5 | The Four-Layer Architecture |
| 6 | Layer 1 — The Framework |
| 7 | Layer 2 — The Constitution Core |
| 8 | Layer 3 — The Implementation Bindings |
| 9 | Layer 4 — The Domain Extensions |
| 10 | The Phase Model |
| 11 | The Constitutional Hierarchy |
| 12 | The Governance Engine |
| 13 | System Knowledge Engine |
| 14 | Constitutional Mapping Engine |
| 15 | Intelligence Layer |
| 16 | Operating Modes |
| 17 | Product Surfaces |
| 18 | Outputs |
| 19 | Business Model |
| 20 | Reference Systems |
| 21 | Operational Governance |
| 22 | Repository Structure |
| 23 | Build Roadmap |
| 24 | The Lock |

---

## §1 — Vision Statement

Governova is the world's first AI development governance platform.

It is the constitutional layer between AI capability and enterprise trust. It defines exactly what every AI tool is permitted to do, how it must do it, what it must never do, and which decisions require human approval. It records every AI action in an immutable audit trail. It generates complete documentation for every file ever built. It translates governance standards into any organisation's own language.

The category Governova creates does not exist yet. Snyk owns security scanning. SonarQube owns code quality. Datadog owns observability. Nobody owns the answer to the question every enterprise is now asking: *"We are using AI to write production code. What governance is in place, and how do we prove it?"*

Governova owns that answer.

The long-term vision is for Governova to become the industry standard for AI development governance — the way ISO 27001 is the standard for information security and SOC2 is the standard for service organisation controls. Companies get Governova Certified. Regulators reference the Governova Score. Investors ask for it in due diligence. Enterprises require it from their vendors.

That is the destination. This document is the foundation.

---

## §2 — The Problem

### 2.1 The developer problem

AI coding tools can build a full authentication system in twenty minutes. The developer who asked for it cannot explain a single line of it. They do not know why the JWT is structured that way, what happens if the refresh token endpoint is hit twice simultaneously, or where exactly the system fails if Redis goes down. They know it works. Until it does not.

Worse: the AI achieved its own goal state, not the developer's desired state. It built something that passes tests. It did not build something that follows your security standards, your architectural patterns, your naming conventions, or your organisation's compliance requirements — because nobody told it exactly what those were.

The difference between `"build an auth page that returns an error when the password is wrong and looks nice"` and a constitutionally governed auth session is the difference between an outcome request the AI fills with guesses, and a specification where every decision is governed, documented, and pre-approved.

### 2.2 The enterprise problem

Enterprises have AI tools. They have no layer that tells those tools what to do, how to do it, what not to do, or who approves what. When something goes wrong in production and an AI engineer wrote that code, they cannot answer: "What exactly did we tell the AI to do? What did it decide on its own? Who approved that?"

The result: enterprises block AI entirely. Not because AI cannot build — but because there is no governance proof. Legal says no. Security says no. Compliance says no. The CTO has no answer for the board.

### 2.3 The five things every enterprise is missing right now

| Gap | Description |
|-----|-------------|
| No constitutional system | No formal definition of how AI must behave during development |
| No command specification | AI receives outcomes, not precise instructions with constraints |
| No permission model | No documented boundary between what AI can decide and what humans must approve |
| No audit trail | No record of every AI action taken in a build session |
| No relay model | No structured handoff protocol between AI tools and human engineers |

Governova fills all five gaps simultaneously.

---

## §3 — What Governova Is

Governova is a platform with seven product surfaces, one governance engine, a four-layer constitutional architecture, and a network intelligence layer — all working together to make AI development governable, auditable, and trustworthy at any scale.

It is not a linter. It is not a code reviewer. It is not a security scanner. It is the constitutional infrastructure that governs how AI reasons before it writes a single line of code, and documents everything it did after.

### 3.1 What it governs

Governova governs the AI development process itself — not just the output. It defines:

- Which standards apply to every decision an AI tool makes
- Which AI tool can propose, recommend, implement, or approve at each stage
- What constitutes a violation and how it is surfaced
- Who has authority to override a standard and how that override is recorded
- How the system responds when production incidents occur
- How standards evolve over time without losing their integrity

### 3.2 The one-line pitch

*"Every line of code AI builds for you — your engineers will understand it, know why it was built that way, know exactly what breaks it, and know exactly how to fix it. Against your own rules. In your own language."*

---

## §4 — Core Philosophy

### 4.1 The fundamental principle

AI is not the problem. Ungoverned AI is.

AI tools can generate correct, production-ready code at extraordinary speed. The failure mode is not in the generation — it is in the absence of constitutional boundaries that tell the AI what "correct" means for your specific system, your specific domain, and your specific organisation.

Governova's position: AI must be commanded with precision, not prompted with approximation.

### 4.2 The five governing principles

**Command, not prompt.** Every AI action operates under explicit constitutional standards. The AI does not decide how to handle token storage, session expiry, or error messages. The constitution decides. The AI implements the specification.

**Human authority is non-negotiable.** L4 decisions — Approve — are permanently and unconditionally human-only. An AI tool may propose, recommend, and implement. It never approves its own output for production.

**Everything is documented or it did not happen.** Every AI action, every standard applied, every violation caught, every human approval recorded — all of it enters the immutable audit trail. If it is not in the audit trail, it is not governed.

**Governance must be universal.** Governova's framework applies to any system in any domain on any stack. A fintech system and a healthcare system operate under different domain extensions but the same universal framework. The structure never changes. Only the standards change.

**The database grows with every project.** Every system governed by Governova strengthens the constitutional database for every system that follows. Violation patterns from one project become encoded anti-patterns for the next. This is the network effect moat.

---

## §5 — The Four-Layer Architecture

Governova's constitutional system is organised in four layers, each more specific than the one above it. This layering is what makes Governova genuinely universal while still being concrete enough to govern real systems.

```
LAYER 1 — FRAMEWORK         Universal primitives. Stack-agnostic. Domain-agnostic.
                            The format, phases, severity, permissions, hierarchy,
                            amendment protocol. Never changes regardless of stack.
        │
        ▼
LAYER 2 — CONSTITUTION CORE  Universal standards organised by phase (0–3).
                            What must be true for any system, stated as principle.
                            Example: "Every endpoint validates all input."
        │
        ▼
LAYER 3 — IMPLEMENTATION     Stack-specific bindings of the core standards.
                            How a principle is satisfied in a specific technology.
                            Example: "In FastAPI, satisfied by a Pydantic model."
        │
        ▼
LAYER 4 — DOMAIN EXTENSIONS  Domain-specific standards layered on top.
                            What a specific industry additionally requires.
                            Example: "Fintech: monetary values use Decimal, never float."
```

### 5.1 Why four layers

The original system was a single flat set of constitutions written for one specific dual-stack reality. That made it powerful for KSDRILL SA but not universal — an enterprise on a different stack would inherit irrelevant rules.

The four-layer split solves this. The **Framework** and **Constitution Core** are universal — they apply to every system ever built. The **Implementation** layer binds those universal standards to specific technologies. The **Domain** layer adds industry-specific depth. A team picks their layers; Governova compiles the exact subset that applies to them.

A Java/Spring team inherits the same Framework and Constitution Core as a Next.js team, writes or adopts a `spring-boot` implementation binding, and adds their domain extension. Same universal foundation. Different specific layers. That is what makes Governova infrastructure rather than a personal template.

### 5.2 How a project compiles its constitution

At initialisation, a project declares its stack and domain. Governova compiles the applicable layers into a single CONSTITUTION-INDEX:

```yaml
project:     fundslink-academy
stack:       angular-fastapi          # → implementation/angular + fastapi + prisma-postgresql + chromadb
domain:      [fintech, edtech]         # → domains/fintech + domains/edtech
mode:        personal                  # → protocols/modes/personal-mode

compiled:
  framework:        7 universal primitives
  constitution_core: 11 constitutions (all phases)
  implementation:    angular + fastapi + prisma-postgresql + chromadb bindings
  domains:           fintech + edtech extensions
```

This compiled index is the single source of constitutional truth for that project. It is what the relay loads, what the MCP server serves, and what the CI/CD enforcer validates against.

---

## §6 — Layer 1: The Framework

The framework is the set of universal primitives that govern everything else. These never change regardless of stack, domain, or organisation. They are the grammar of the entire system.

| Primitive | Definition |
|-----------|------------|
| **Format Specification** | The `S{C}.{N}` standard ID format, `AP-S{C}.{N}{letter}` anti-pattern format, and the required document structure for every constitution |
| **Phase Model** | The four-phase read and dependency order (Phase 0–3) that determines when each constitution applies |
| **Severity Model** | SEV0–SEV3 classification for violations and incidents |
| **Permission Model** | The L1–L4 AI permission levels, with L4 permanently human-only |
| **Conflict Resolution** | The constitutional hierarchy and the four-step protocol for resolving conflicts |
| **Amendment Protocol** | How standards are changed, audited, and versioned |

### 6.1 The Format Specification

Every standard follows this exact structure:

```
S{C}.{N} — {title}
Severity:     SEV0 | SEV1 | SEV2 | SEV3
Phase:        0 | 1 | 2 | 3
Applies To:   [scope — all systems / specific stack / specific domain]
Rule:         [the standard, stated as a requirement]
Rationale:    [why this standard exists]
Anti-pattern: AP-S{C}.{N}{letter} — [what failure looks like]
```

Standard IDs are permanent. Once assigned, an ID is never reused. Deprecated standards are marked `DEPRECATED` and retained with their deprecation record.

### 6.2 The Severity Model

| Level | Name | Meaning | Response |
|-------|------|---------|----------|
| SEV0 | Critical | Production down or data at risk | Immediate stop, runbook activation |
| SEV1 | High | Functional breakage, security gap | Relay pause, Founder approval required |
| SEV2 | Medium | Standard violation, non-critical | Flag in PR review, amendment required |
| SEV3 | Low | Style, convention, minor deviation | Lint warning, document in commit |

### 6.3 The Permission Model

Every AI tool operates under a defined permission level. Permission levels are non-negotiable and cannot be overridden by the AI itself.

| Level | Name | What the AI can do |
|-------|------|--------------------|
| L1 | Propose | Suggest architectural decisions, designs, approaches |
| L2 | Recommend | Produce detailed implementation plans with rationale |
| L3 | Implement | Write code, create files, make changes — within approved spec |
| L4 | Approve | **Human only. Always. No exceptions.** |

**L4 is permanently human-only.** No relay configuration, no prompt, no instruction can elevate an AI tool to L4. This is a hard framework constraint, not a setting.

---

## §7 — Layer 2: The Constitution Core

The constitution core is eleven universal constitutions, organised into four phases. These are the standards that apply to any system, stated as principles independent of any specific technology.

### 7.1 The eleven constitutions

| ID | Constitution | Phase | Paired Implementation |
|----|--------------|-------|----------------------|
| C0 | Constitutional Order | — (governs all) | None — references the Framework |
| C1 | Engineering Standards | Phase 0 | None — process & quality |
| C2 | Backend Constitution | Phase 1 | Yes — backend bindings |
| C3 | Auth Constitution | Phase 1 | Yes — auth bindings |
| C4 | Frontend Constitution | Phase 1 | Yes — frontend bindings |
| C5 | Database Constitution | Phase 1 | Yes — database bindings |
| C6 | Full-Stack Architecture | Phase 1 | None — integration document |
| C7 | Testing Constitution | Phase 2 | None |
| C8 | Platform Reliability | Phase 2 | None |
| C9 | Product & Feature | Phase 3 | None |
| C10 | AI Collaboration | Phase 3 | None |

### 7.2 What each constitution governs

**C0 — Constitutional Order.** The master document. Governs the governance system itself: the phase map, the constitutional hierarchy, the conflict resolution protocol, the cross-constitution dependency map, and the amendment protocol. Sits above the phases because it governs them all.

**C1 — Engineering Standards.** How work happens. Code quality, the 8-phase feature lifecycle, the feature proposal standard, self-review and PR standards, Git discipline, conventional commits, sprint governance, TypeScript and Python code quality, documentation standards. The Phase 0 foundation — read before any code is written.

**C2 — Backend Constitution.** Service architecture, API contracts, OpenAPI-first development, database access from backend services, performance, resilience, security middleware, observability. The universal principles; the stack-specific bindings (FastAPI) live in the implementation layer.

**C3 — Auth Constitution.** Authentication strategy, JWT lifecycle, RBAC, OAuth, session management, security baseline, audit logging. The highest domain authority in the conflict hierarchy because security failures are irreversible.

**C4 — Frontend Constitution.** Frontend architecture, mobile-first standards, state management, group-build methodology, layer build order. Universal principles; the Next.js and Angular bindings live in the implementation layer.

**C5 — Database Constitution.** Database assignment by data type, cross-database integrity, migration governance. Universal principles; the relational, document, and vector bindings live in the implementation layer.

**C6 — Full-Stack Architecture.** System topology, stack assignment framework for new systems, request flows, cross-stack communication, deployment coordination. An integration document that depends on and synthesises all of Phase 1 — it references the other Phase 1 standards rather than restating them.

**C7 — Testing Constitution.** Test strategy, toolchain assignment, coverage gates, unit/integration/E2E standards, test database governance, visual regression.

**C8 — Platform Reliability.** Deployment platforms, CI/CD pipeline standards, environment governance, observability, alert thresholds, the severity framework, rollback procedures, post-mortem protocol.

**C9 — Product & Feature.** Product vision, feature governance, MVP definitions, the 5-gate feature qualification, user feedback integration, roadmap governance.

**C10 — AI Collaboration.** AI role definitions, the L1–L4 permission boundaries, design-phase and build-phase AI workflows, the solo dev AI pair programming protocol, the CONSTITUTION-INDEX standard, AI anti-patterns.

---

## §8 — Layer 3: The Implementation Bindings

The implementation layer binds the universal core standards to specific technologies. Each binding shows how a universal principle is satisfied in a concrete stack.

### 8.1 The principle of binding

A core standard states what must be true. An implementation binding states how it is satisfied in a specific technology, and what failure looks like there.

```
CORE (universal):
S2.04 — Every endpoint must validate all input against a typed,
        declared schema before processing.

IMPLEMENTATION (fastapi):
S2.04/fastapi — Satisfied by a Pydantic model bound to every route
        parameter and request body. Raw dict access to request data
        is AP-S2.04a/fastapi.

IMPLEMENTATION (spring-boot, hypothetical future):
S2.04/spring — Satisfied by a @Valid annotated DTO with Bean Validation
        constraints. Accessing the raw request body is AP-S2.04a/spring.
```

Same principle. Different bindings. This is what makes the core genuinely universal.

### 8.2 The KSDRILL SA implementation bindings

These are the reference bindings, proven on the four flagship systems:

| Binding | Binds | For |
|---------|-------|-----|
| `nextjs` | C4 Frontend | Content-driven, SEO-critical systems |
| `angular` | C4 Frontend | Enterprise dashboards, financial systems |
| `fastapi` | C2 Backend | All backend services |
| `nextauth` | C3 Auth | Authentication across both stacks |
| `prisma-postgresql` | C5 Database | Relational, transactional data |
| `beanie-mongodb` | C5 Database | Document, flexible-schema data |
| `chromadb` | C5 Database | Vector data, AI/RAG pipelines |

### 8.3 The dual-stack reality

The KSDRILL SA reference implementation is deliberately dual-stack, governed by C6's stack assignment framework (S6.1–S6.7):

- **Next.js** — content-driven, SEO-critical, public-facing systems (Maphophe, SyncUp)
- **Angular + FastAPI** — enterprise dashboards, precision financial calculations, native Python AI pipelines (FundsLink Academy, KSDRILL Reserve Bank)

New systems are assigned a stack via the decision framework in the stack-assignment-matrix, with an ADR required for any non-default assignment.

---

## §9 — Layer 4: The Domain Extensions

Domain extensions add industry-specific standards on top of the universal core and implementation bindings. They encode the additional requirements a specific industry imposes.

### 9.1 Domain registry

| Domain | Additional Standards | Regulatory Basis | Reference System |
|--------|---------------------|------------------|------------------|
| Fintech | Monetary precision, transaction atomicity, fraud detection, audit depth | PCI-DSS, FICA, FATF | FundsLink, Reserve Bank |
| Govtech | Data sovereignty, public accessibility, procurement compliance | POPIA, GDPR-adjacent | Maphophe |
| Edtech | Minors' data, parental consent, educational records | FERPA, COPPA | FundsLink |
| SaaS/B2B | Multi-tenancy, billing integrity, RBAC depth | General | SyncUp |
| Healthtech | PHI handling, retention, anonymisation | HIPAA-equiv., NHI Act | Planned |
| E-commerce | Payment integrity, inventory, cart consistency | PCI-DSS, consumer protection | Planned |
| IoT/Embedded | Edge security, firmware, telemetry, update integrity | IEC 62443, ETSI EN 303 645 | Planned |
| AI/ML Systems | Model governance, drift detection, data pipeline integrity | EU AI Act, NIST AI RMF | Planned |

### 9.2 How domains grow

Domain extensions are the primary growth vector of the constitutional database. They can be contributed by domain experts through the governed contribution process (see §19.6). Every domain extension follows the same format specification as the core, undergoes conflict review against the universal core, and is published with contributor attribution and revenue share.

This is how the database goes from its current standards to thousands — not by writing everything, but by owning the contribution framework and the quality bar.

---

## §10 — The Phase Model

The four phases are the read order, the dependency order, and the failure order. They are the most important structural feature of the constitution core — a system that skips a phase fails in the way that phase was designed to prevent.

### 10.1 The four phases

**Phase 0 — Foundation.** *Read before any code is written, any branch is created, any environment is set up.* If skipped, no engineer shares a definition of "done," no code quality standard exists, and the first PR introduces patterns impossible to remove without a rewrite. Contains: C1.

**Phase 1 — Core Architecture.** *Read before the first line of application code.* If skipped, the system has no architectural boundaries, no auth strategy, no database assignment, no frontend governance. The first endpoint embeds patterns that corrupt every endpoint after it. Contains: C2, C3, C4, C5, C6.

**Phase 2 — Quality & Reliability.** *Read before any feature is considered production-ready.* If skipped, the system ships without a testing strategy, deployment governance, or incident response. The first production failure is uncontrolled, untraceable, and unrecoverable. Contains: C7, C8.

**Phase 3 — Product & Intelligence.** *Read before any feature roadmap decisions or AI-assisted development sessions.* These come last because they require all technical constitutions to be locked — product and AI governance decisions must be made against a stable technical foundation. Contains: C9, C10.

---

## §11 — The Constitutional Hierarchy

When two constitutions conflict, a strict hierarchy resolves it. The hierarchy governs conflicts — it does not imply importance.

### 11.1 Hierarchy, highest to lowest authority

```
C0  — Constitutional Order      ← Supreme authority. Governs the governance system.
C3  — Auth Constitution         ← Security decisions. Highest domain authority.
C2  — Backend Constitution      ← Architecture and API contract decisions.
C5  — Database Constitution     ← Data storage and integrity decisions.
C4  — Frontend Constitution     ← UI, client-side, and rendering decisions.
C6  — Full-Stack Architecture   ← Integration, stack assignment, and topology.
C1  — Engineering Standards     ← Process, workflow, and code quality decisions.
C7  — Testing Constitution      ← Quality validation and coverage decisions.
C8  — Platform Reliability      ← Deployment and operational decisions.
C9  — Product & Feature         ← Product scope and feature decisions.
C10 — AI Collaboration          ← AI governance and permission boundary decisions.
```

C9 and C10 sit at the bottom of conflict resolution because product and AI decisions must yield to technical correctness — not because they are unimportant.

### 11.2 The conflict resolution protocol

**Step 1 — Verify the conflict is real.** Check whether one constitution has a stack-scope qualifier that resolves the apparent conflict. Most apparent conflicts dissolve here — what looks like a contradiction is often two stack-specific standards for the same concern.

**Step 2 — Apply hierarchy.** The constitution higher in §11.1 governs. C3 overrides C4 on any decision touching authentication state. C2 overrides C6 on any API boundary decision. C5 overrides C2 on any data storage assignment.

**Step 3 — If hierarchy does not resolve it, the conflict is a genuine gap.** Open a constitutional amendment issue. Cite both conflicting standards. No implementation decision is made until the amendment resolves it. Do not improvise. Do not ask AI to decide.

**Step 4 — Document the resolution.** Update both affected constitutions' amendment logs. Update the Cross-Constitution Dependency Map if the dependency relationship changed.

---

## §12 — The Governance Engine

The governance engine is the central runtime of the platform. Every product surface connects to it. Every AI tool in the relay queries it.

### 12.1 Engine components

**Constitutional Store.** The live, versioned database of all active standards for a session — the compiled CONSTITUTION-INDEX (Framework + Core + Implementation + Domains). Queried in real time by every AI tool and every surface.

**Violation Detector.** A real-time scanner that monitors AI output, code diffs, and PR content against the active index. Violations are classified by severity, linked to their anti-pattern record, and surfaced through the appropriate channel.

**Relay State Machine.** Tracks the current position in the relay protocol for each session — which engineer is active, what standard was in effect at each decision, what handoff reports exist, whether abort conditions triggered.

**Audit Trail.** An immutable, append-only record of every AI action: timestamp, AI tool, permission level, standard in effect, decision made, whether it was permitted, and Founder approval status. Cannot be edited, only appended. The compliance evidence layer.

**System Knowledge Engine.** Generates the four-layer documentation (Why, How, Failure Map, Fix Guide) for every file. See §13.

**Mapping Engine.** Translates an enterprise's existing standards into a Governova CONSTITUTION-INDEX in their own language. See §14.

**Intelligence Layer.** The network effect, temporal governance, and pre-build risk assessment. See §15.

### 12.2 The build session lifecycle

```
1.  Load and compile CONSTITUTION-INDEX (Framework + Core + Implementation + Domains)
2.  Validate index integrity (all S{C}.{N} references resolve)
3.  Confirm active relay position and operating mode
4.  AI engineer activates at assigned permission level
5.  Standards served to AI tool via MCP server or static index
6.  AI operates, producing output governed by active standards
7.  Violation detector scans output in real time
8.  SEV0/SEV1 pause the relay; SEV2/SEV3 log and continue
9.  Handoff report generated at relay checkpoint
10. Founder reviews and approves — L4 checkpoint
11. Next engineer activates
12. On session close: audit trail sealed, System Bible updated
```

---

## §13 — System Knowledge Engine

The System Knowledge Engine answers the hardest question in AI-assisted development: *"I didn't write this code. How do I know what it does, why it was built this way, and what happens when it breaks?"*

### 13.1 Four documentation layers

Every file built under governance receives four documentation layers, generated in real time during the relay — not written after.

**Why Layer** (Claude, L1 design). Why this file exists, which standard authorised the decision, what problem it solves, what alternatives were rejected, what constraints govern it. The permanent record of design intent — this becomes the file's ADR linkage.

**How Layer** (Claude Code, L2/L3 build). For every function and integration point: a plain-language narrative of the logic and data flow. What happens when this runs, what it expects, what it returns, how it connects.

**Failure Map** (from the anti-patterns database). The specific ways this code can go wrong, drawn from the `AP-S{C}.{N}` catalogue — the exact failure signatures for this type of code in this domain and stack.

**Fix Guide** (from the runbook library). For each failure mode: diagnostic steps, which standard to check first, and the resolution path. When something breaks at 2am, the developer opens the Fix Guide — they do not reverse-engineer the code.

### 13.2 The System Bible

The aggregation of all four layers across all files forms the System Bible — a complete, living record generated automatically as a byproduct of the build. Surfaced via IDE hover overlay, web dashboard browser, and downloadable PDF for compliance packages.

System Bible completeness is tracked as a health metric. A file with no Why Layer has an unrecorded design decision — itself a governance gap.

---

## §14 — Constitutional Mapping Engine

The Mapping Engine solves enterprise adoption. Enterprises do not adopt foreign governance systems. They enhance their own.

### 14.1 The principle

Governova reads an enterprise's existing standards, maps its constitutional database to their language, fills their gaps with best practices from its database, and produces a CONSTITUTION-INDEX in the enterprise's own terminology, format, and structure. Their team reads the output and sees their own policies — made stronger.

### 14.2 The mapping process

```
1. Enterprise uploads existing standards (policy PDFs, coding standards, frameworks)
2. Parser extracts and structures rules into addressable units
3. Mapping runs against Governova's database:
   For every Governova standard:
     → Equivalent enterprise rule exists?  YES: map, adopt their language
     → No equivalent?                       NO:  surface gap, propose enhancement
4. Translation layer rewrites all standards into the enterprise's:
   naming conventions · document structure · terminology · compliance categories
5. Conflict detection surfaces genuine contradictions with resolution options:
   A: Override with enterprise policy (record exception)
   B: Adopt Governova standard (update enterprise policy)
   C: Merge (satisfy both simultaneously)
   → Decision recorded in amendment log with date, approver, rationale
6. Output: CONSTITUTION-INDEX in enterprise format, active in the relay
```

### 14.3 Constitutional exception recording

When an enterprise overrides a Governova standard, an exception record is created:

```
EXCEPTION-{ORG}-{DATE}
Standard:   S3.14 — Access token storage
Override:   Enterprise policy §4.2 — Session token in Redis
Rationale:  Legacy distributed session architecture requirement
Approved:   [CISO name], [date]
Review:     Quarterly — next review [date]
Risk:       Acknowledged — mitigated by [controls]
```

No exception is invisible. Every override is documented, approved, and scheduled for review.

---

## §15 — Intelligence Layer

The intelligence layer is the long-term competitive moat — it makes the database smarter every day, keeps standards current, and shifts governance from reactive to proactive.

### 15.1 Intelligence Network

Every governed project contributes anonymised, aggregated data — with consent and full transparency. The network learns violation patterns, relay performance, and amendment triggers across all projects. It produces violation pattern alerts, evidence-backed constitutional improvement proposals, and validated domain updates. Every project makes the database smarter for every project that follows. No competitor can replicate this without the user base.

### 15.2 Temporal Governance

Standards age. A framework's major version or an overnight CVE can invalidate a best practice. Temporal governance monitors framework changelogs, CVE databases, and dependency releases. When an external change may have invalidated a standard, it flags it for review. Standards past their review window are marked `UNVALIDATED` — still in effect, but surfaced as a governance risk.

### 15.3 Pre-build Risk Assessment

Before the first commit, Governova generates a constitutional risk report from the declared architecture, domain, and stack: the highest-risk areas, the standards that apply, the anti-patterns most likely to appear, and the runbooks to prepare. Governance at architecture time, not just review time.

---

## §16 — Operating Modes

A project declares an operating mode in its CONSTITUTION-INDEX. The mode changes which protocols are active and which outputs are generated — never the constitutional framework itself.

| Mode | For | Adds | Maps to |
|------|-----|------|---------|
| **Personal** | Solo developers | Full relay through one approver; solo AI pair-programming protocol | Free, Pro |
| **Team** | Small teams | Merge authority rules, multi-human violation reporting, multi-approver relay | Pro+ |
| **Enterprise** | Organisations | Mapping Engine, certification tracking, board reporting, exception recording | Max, Enterprise contracts |

---

## §17 — Product Surfaces

Seven surfaces. One engine. Every touchpoint in the development workflow.

### 17.1 IDE Extension (VS Code + Cursor)
The primary interface and entry point. Standards in the sidebar by active layer, inline violation highlights, relay step tracker, System Bible hover overlay, `.cursorrules` generator, session startup protocol.

### 17.2 JetBrains Plugin
The enterprise unlock — full feature parity for IntelliJ and WebStorm teams via the JetBrains Platform SDK.

### 17.3 CI/CD Enforcer
The tool that makes governance non-optional. A GitHub Action and GitLab CI equivalent running `governova validate` on every PR. SEV0/SEV1 block merge. SEV2 requires documented exception. New files require Why and How layers.

### 17.4 PR Guardian Bot
Reads every PR, runs it against the active index, leaves inline review comments with constitutional precision — citing the standard, the anti-pattern, the severity, and the correct pattern. Understands governance intent, not just patterns.

### 17.5 Web Dashboard
Project health (Governova Score, trend, violation heatmap), relay monitor, constitutional coverage, audit trail, System Bible completeness, team analytics.

### 17.6 CLI Tool
```
governova init                 governova generate cursorrules
governova validate             governova generate bible
governova validate --pre-commit governova report
governova score                governova relay status | abort
governova amend S3.14
```

### 17.7 Slack + Teams Bot
SEV0/SEV1 alerts, relay checkpoint notifications, daily governance digest, amendment notifications, temporal alerts.

### 17.8 REST + GraphQL API
Full access to index management, violation records, audit trail, relay state, score, System Bible, amendments. JWT with machine ID binding, rate limited per tier.

### 17.9 MCP Server
The most architecturally significant surface. Makes the constitutional database a live, queryable API that AI tools connect to at session start instead of reading static files. Tools: `get_standard`, `get_active_constitution`, `check_violation`, `get_anti_pattern`, `get_relay_state`, `log_ai_action`, `get_runbook`, `flag_temporal_review`. Standards updated centrally propagate to every active AI session immediately.

---

## §18 — Outputs

### 18.1 Governova Score (0–100)

| Factor | Weight |
|--------|--------|
| Violation rate (SEV0/1 weighted 5×, SEV2 2×, SEV3 1×) | 30% |
| Relay compliance | 25% |
| Constitutional coverage | 20% |
| Amendment discipline | 15% |
| Audit trail completeness | 10% |

Displayed in portfolios, job listings, investor data rooms, governance dashboards, vendor due diligence. Once the market cares about the score, Governova owns the metric.

### 18.2 Governova Certified

Maintain a score of 85+ for six consecutive months → publicly verifiable certification badge. The ISO 27001 equivalent for AI development governance.

| Tier | Threshold | Duration |
|------|-----------|----------|
| Standard | ≥ 85 for 6 months | Annual |
| Advanced | ≥ 92 for 6 months | Annual |
| Enterprise | ≥ 95 for 12 months | 2 years (full audit) |

### 18.3 Board-Level Governance Report

One page, plain English, auto-generated monthly, for non-technical stakeholders. Overall score and trend, red/amber/green per constitutional area, AI action volume, governance events, certification status. The report shown to the board, the regulator, and the Series B data room. Nobody else generates it automatically.

### 18.4 System Bible

The complete per-project four-layer documentation of every file. The output that transforms AI-generated code from a black box into fully understood, maintainable software.

---

## §19 — Business Model

### 19.1 Subscription tiers

> **Revised by `ADR-010` (2026-08-20).** The tier *prices* stand. What each tier *buys* was
> redefined, because the original table gated the local engine and `governova` v0.2.0 shipped
> to PyPI under MIT with every deterministic capability included — all 42 rules, the Score, the
> Board Report, the System Bible and the MCP server. **MIT cannot be revoked for what is
> already distributed**, so a Free tier limited to "3 critical anti-pattern alerts", and an
> MCP server sold at Max, describe a product that can no longer be built from here.

**The paid boundary is "needs a server we run", never "is valuable."**

| | |
|---|---|
| **Free forever — MIT, offline, unlimited projects** | Every deterministic rule and probe · Governova Score · Board-Level Governance Report · System Bible · CLI · MCP server · CI/CD gate · PR Guardian · `onboard` / `roadmap` / `convert` · the whole compiled constitution |
| **Governova Cloud — paid** | Intelligence Gateway (metered AI by effort tier) · Intelligence Network (§15.1) · hosted dashboard, history and trend · organisations, teams, seats, SSO · Certification programme (§18.2) · temporal governance feeds (§15.2) |

| Tier | Price | Seats | Cloud entitlement |
|------|-------|-------|-------------------|
| **Free** | $0 / forever | 1 | The complete local engine. No Cloud credits. |
| **Pro** | $9/mo · $89/yr | 1 | Gateway credits at Low/Medium effort · hosted history · dashboard |
| **Pro+** | $19/mo · $189/yr | 2 | Team mode · High effort · org management · API access |
| **Max** | $39/mo · $389/yr | 5 | Enterprise mode · Max effort · SSO · white-label · SLA |

Annual billing ~20% discount. **Seats are the billed unit; projects are never counted.**

### 19.2 Why there is no licence server

The previous model — feature flags from a licence server, machine-ID binding, concurrent-session
detection — is **retired by `ADR-010`**, and not only because the engine is MIT and cannot be
bound. It would punish the ordinary case (one engineer, a laptop and CI) to deter a copy that
`pip download` already permits, and it would make every deterministic result depend on a network
call that can fail.

**The engine must work perfectly with the Cloud unreachable.** That property is the product's
central claim: a governance tool nobody can independently verify is a governance tool nobody
should trust. Paid value lives in capabilities a laptop genuinely cannot provide — metered
inference, cross-project learning, hosted history, organisations — so it needs no gate to
protect it.

### 19.3 Certification programme
Annual fee separate from subscription. Three tiers. Renewal requires an active subscription. Revenue independent of subscription churn.

### 19.4 Enterprise contracts
Mapping Engine implementation, dedicated onboarding, custom domain constitutions, enterprise SLAs, compliance package generation, regulatory alignment. Custom pricing.

### 19.5 White-labeling
Agencies resell Governova under their own brand, pay the Max rate, keep the margin. They become the sales force.

### 19.6 Open source and community
Universal core constitutions published open source after battle-testing on the four reference systems. Domain and stack contributions accepted through a governed process with conflict review, attribution, and revenue share. How the database scales from hundreds of standards to thousands.

---

## §20 — Reference Systems

The four flagships are reference implementations — the first production systems built under full constitutional governance. They prove the framework, provide per-domain case studies, and seed the domain library with battle-tested standards. They are examples, not boundaries.

| System | Domain | Stack | Constitutional Focus |
|--------|--------|-------|----------------------|
| **FundsLink Academy** | Fintech + Edtech | Angular + FastAPI | Funding calculations (Decimal), FICA, educational data, LangChain/ChromaDB AI |
| **Maphophe Community System** | Govtech + Community | Next.js | POPIA, public data, SEO-critical content, accessibility |
| **KSDRILL Reserve Bank** | Fintech + Banking | Angular + FastAPI | Transaction atomicity, financial freeze protocol, banking compliance |
| **SyncUp** | Creator + SaaS | Next.js | Multi-tenancy, creator rights, content delivery, billing integrity |

Stack assignments are locked via ADR-001 through ADR-004 against the C6 stack-assignment framework.

---

## §21 — Operational Governance

### 21.1 Runbooks

| ID | Runbook | Trigger |
|----|---------|---------|
| RB-01 | SEV0 Response | Production down or data at risk |
| RB-02 | SEV1 Response | Functional breakage, security gap |
| RB-03 | Financial Freeze | Balance discrepancy detected |
| RB-04 | Database Migration | Migration failure or rollback |
| RB-05 | AI Degradation | AI pipeline failure during relay |
| RB-06 | Railway Deployment | Backend deployment incident |
| RB-07 | Vercel Rollback | Frontend deployment incident |
| RB-08 | Relay Abort | AI output diverges from design |

### 21.2 The relay protocol

```
[1] Claude (Design)        L1 → L2   Architecture, constitutional design, specification
[2] Claude Code (Build)    L2 → L3   Implementation, file creation, integration
[3] ChatGPT (Debug+Style)  L2 → L3   Debugging, UI refinement, cross-validation
[4] DeepSeek (Review)      L1 → L2   Code review, security analysis, logic audit
[5] Kimi (Optimise)        L2 → L3   Performance, accessibility, final polish
[F] Founder                L4        Approval at every handoff
```

**Relay abort.** Significant divergence stops the relay. State committed to a `relay-abort/` branch. Divergence documented in a GitHub Issue. Relay re-enters at Claude before resuming.

**Clarification fast-path.** Questions classified before routing: `MINOR` (Claude Code decides, documents in commit, flags at handoff) vs `ARCHITECTURAL` (full relay pause, Founder approval).

### 21.3 Amendment protocol
Every standard change is logged in `governance/changelog/amendments-log.md` with date, standard ID, change, rationale, and approver. Major amendments affecting multiple constitutions follow the major-amendment template and update all affected indexes and anti-patterns in the same PR.

---

## §22 — Repository Structure

```
governova/
├── README.md · CONTRIBUTING.md · CODE_OF_CONDUCT.md · SECURITY.md · LICENSE
├── docs/                               # all documentation
│   ├── vision/                         # master · product · strategy
│   ├── guides/                         # quickstart · ai-instructions
│   └── reference/                      # manifest (navigation map)
│
├── framework/                          # LAYER 1 — universal primitives
│   ├── format-specification.md · phase-model.md · severity-model.md
│   ├── permission-model.md · conflict-resolution.md · amendment-protocol.md
│
├── constitution/                       # LAYERS 2–4 — the standards database
│   ├── C00-constitutional-order.md     # governs all, references framework
│   ├── core/                           # LAYER 2 — universal, by phase
│   │   ├── phase-0-foundation/         (C01)
│   │   ├── phase-1-core-architecture/  (C02, C03, C04, C05, C06)
│   │   ├── phase-2-quality-reliability/(C07, C08)
│   │   └── phase-3-product-intelligence/(C09, C10)
│   ├── implementation/                 # LAYER 3 — stack bindings
│   │   ├── nextjs/ · angular/ · fastapi/ · nextauth/
│   │   └── prisma-postgresql/ · beanie-mongodb/ · chromadb/
│   ├── domains/                        # LAYER 4 — domain extensions
│   │   └── fintech/ · govtech/ · edtech/ · saas/
│   └── indexes/                        (standards · anti-patterns · quick-ref · stack-matrix)
│
├── protocols/                          # operational procedures
│   ├── relay-protocol.md · relay-clarification.md · relay-abort.md
│   ├── session-lifecycle.md · git-workflow.md
│   └── modes/ (personal · team · enterprise)
│
├── governance/                         # operational records
│   ├── runbooks/ (RB-01…RB-08)
│   ├── decisions/ (ADRs)
│   └── changelog/ (amendments-log.md)
│
├── platform/                           # the product
│   ├── engine/ (store · detector · relay-machine · audit · knowledge · mapping · intelligence)
│   └── surfaces/ (ide · jetbrains · cicd · pr-bot · dashboard · cli · slack-teams · mcp)
│
├── reference-systems/                  (fundslink · maphophe · reserve-bank · syncup)
├── templates/                          (constitution-index · adr · domain · implementation · ...)
└── scripts/                            (validate-integrity · compile-constitution · generate-bible)
```

---

## §23 — Build Roadmap

**Phase 0 — Foundation (current).** Migrate to the four-layer structure. Extract the framework layer. Split implementation bindings per stack. Add framework docs, QUICKSTART, amendments-log, relay-clarification, relay-abort, validation script.

**Phase 1 — First build.** Build all four reference systems under full governance. Dogfood the IDE extension and CLI alongside. Every relay session is a product test; every violation caught is content; every System Bible entry is proof.

**Phase 2 — Product launch.** GitHub Template repo. `governova` CLI on npm. VS Code + Cursor extension (free tier). `governova.dev` website. Lemon Squeezy payments. License server on Railway. FundsLink and SyncUp case studies as launch stories.

**Phase 3 — Growth.** CI/CD enforcer. PR Guardian Bot. Web dashboard. MCP server. Governova Score v1. First community domain contributions.

**Phase 4 — Enterprise.** JetBrains plugin. Mapping Engine. Board report generator. Certified programme. Intelligence Network v1. Temporal governance. Pre-build risk assessment.

**Phase 5 — Standard.** Automated framework monitoring. Contribution revenue share. Enterprise pilots. Open-source core. Governova as the recognised industry standard.

---

## §24 — The Lock

This section is the final, definitive statement of what Governova is. It is the source of truth.

**What Governova is.** The world's first AI development governance platform. A four-layer constitutional architecture — Framework, Core, Implementation, Domains — that tells AI tools exactly what to build, how to build it, what not to build, and who approves every decision, for any system, any domain, any stack, any scale.

**What problem it solves.** The gap between AI capability and enterprise trust. Enterprises block AI not because it is bad, but because there is no governance layer. Governova is that layer.

**What makes it different.** No other tool defines constitutional standards for AI behaviour before code is written, governs an AI relay with explicit permission levels, generates four-layer documentation for every file, translates standards into any organisation's language, records every AI action immutably, and produces a score, a certification, and a board report — all from one engine, for any system in any domain.

**What it becomes.** The industry standard for AI development governance. The way you cannot raise venture capital without a security audit, you will not ship AI-assisted production software to regulated industries without Governova Certification.

**The four layers.** Framework — Core — Implementation — Domains.

**The four phases.** Foundation — Core Architecture — Quality & Reliability — Product & Intelligence.

**The seven surfaces.** IDE extension — CI/CD enforcer — PR guardian bot — CLI — web dashboard — Slack/Teams bot — MCP server.

**The four outputs.** Governova Score — Governova Certified — Board-level report — System Bible.

**The one sentence.** *One framework. Every system. Every domain. Every scale.*

---

## Appendix A — ID Reference

| Prefix | Description |
|--------|-------------|
| `S{C}.{N}` | Standard — universal constitutional requirement |
| `S{C}.{N}/{stack}` | Implementation binding — stack-specific satisfaction of a standard |
| `AP-S{C}.{N}{letter}` | Anti-pattern — documented failure mode |
| `ADR-{NNN}` | Architecture Decision Record |
| `RB-{NN}` | Runbook |
| `EXCEPTION-{ORG}-{DATE}` | Constitutional exception |
| `TEMPORAL-ALERT` | Standard requiring review after external change |

## Appendix B — Score Classification

| Range | Classification |
|-------|----------------|
| 95–100 | Exemplary |
| 85–94 | Advanced (certified) |
| 75–84 | Proficient |
| 60–74 | Developing |
| 40–59 | Initial |
| 0–39 | Ungoverned |

## Appendix C — Constitution Map

| Phase | Constitutions |
|-------|---------------|
| Above all | C0 Constitutional Order |
| Phase 0 | C1 Engineering Standards |
| Phase 1 | C2 Backend · C3 Auth · C4 Frontend · C5 Database · C6 Full-Stack |
| Phase 2 | C7 Testing · C8 Platform Reliability |
| Phase 3 | C9 Product & Feature · C10 AI Collaboration |

*Implementation guides paired with: C2, C3, C4, C5.*

---

*This document is the master source of truth for Governova. When this document and an implementation conflict, this document wins. When it needs updating, it is amended through the constitutional amendment protocol — not edited informally.*

*Version 2.0 — Locked 2026-05-22 — KSDRILL SA*
