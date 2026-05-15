# C0 — Constitutional Order

---

| Attribute          | Value                                                              |
|--------------------|--------------------------------------------------------------------|
| **Document**       | C0 — Constitutional Order                                          |
| **Organisation**   | KSDRILL SA                                                         |
| **Version**        | v1.0                                                               |
| **Status**         | LOCKED                                                             |
| **Locked**         | 2026-05-08                                                         |
| **Next Review**    | 2026-08-08                                                         |
| **Applies To**     | All Systems · Both Stacks · Solo Dev · Team                        |
| **Paired With**    | — (Master Document — governs all, paired with nothing)             |

---

> *"Build constitutions in the order your system would fail without them."*

---

## Opening Statement

The Constitutional Order is the document that makes all other documents possible. It does
not govern code, architecture, or process directly. It governs the governance system itself —
defining what constitutions exist, in what order they apply, how they relate to each other,
how they change, and what authority each one holds.

Every KSDRILL SA system — whether built solo or in a team, whether Next.js or Angular,
whether a flagship product or a future system yet to be designed — operates under the same
eleven constitutions in the same four phases. The stack changes. The domain changes. The
constitutional framework does not.

This document is the first document read and the last document changed. It is the
constitutional foundation upon which all technical decisions are made, all standards are
referenced, and all amendments are governed. When this document and another constitution
conflict, this document wins. When two constitutions conflict with each other, the resolution
protocol defined in this document governs the outcome.

No system begins development without this document being read. No amendment to any
constitution is valid without following the protocol defined here. No AI tool participating
in a build session operates without the boundaries defined here being active.

---

## Table of Contents

| Section | Title | Page Anchor |
|---------|-------|-------------|
| §1 | The Golden Rule | [§1](#1--the-golden-rule) |
| §2 | Terminology System | [§2](#2--terminology-system) |
| §3 | Standard Format Specification | [§3](#3--standard-format-specification) |
| §4 | Document Structure Specification | [§4](#4--document-structure-specification) |
| §5 | Constitution Register | [§5](#5--constitution-register) |
| §6 | Phase Map | [§6](#6--phase-map) |
| §7 | Constitutional Hierarchy & Conflict Resolution | [§7](#7--constitutional-hierarchy--conflict-resolution) |
| §8 | Amendment Protocol | [§8](#8--amendment-protocol) |
| §9 | Cross-Constitution Dependency Map | [§9](#9--cross-constitution-dependency-map) |
| §10 | Stack Assignment Summary | [§10](#10--stack-assignment-summary) |
| §11 | Pre-Build Constitutional Checklist | [§11](#11--pre-build-constitutional-checklist) |
| §12 | Review Calendar | [§12](#12--review-calendar) |
| §13 | Common Failure Register | [§13](#13--common-failure-register) |
| §14 | Amendment Log | [§14](#14--amendment-log) |

---

## §1 — The Golden Rule

> **Immutable. Cannot be amended. Cannot be overridden by any constitution, any team
> decision, or any AI recommendation.**

> *"Build constitutions in the order your system would fail without them."*

Phase 0 constitutions come first because without engineering discipline and code standards,
nothing else holds. Phase 1 follows because without a working architecture, authentication,
frontend, and database, there is nothing to test or deploy. Phase 2 adds quality and
reliability gates. Phase 3 adds product intelligence and AI governance.

Violating this order — building features before establishing architecture, deploying before
establishing incident response, writing code before reading relevant constitutions — is the
root cause of every rewrite situation in software history. The constitutional order is the
systemic defence against that outcome.

This rule applies identically to both stacks, all four flagship systems, all future systems,
solo development, and team development. No exception has ever been justified. No exception
will be entertained.

---

## §2 — Terminology System

All constitutions use this terminology exclusively. Legacy terms from previous versions
(Rules, Forbidden Patterns) are retired. Consistency in terminology is what makes the
constitutional system machine-readable, human-scannable, and auditable across documents.

---

### 2.1 — Primary Terms

| Term | Symbol | Lives In | Definition |
|------|--------|----------|------------|
| **Standard** | `S{C}.{N}` | All constitutions | A governing statement — what the system must do and why. Non-optional. Present tense. Active voice. |
| **Anti-Pattern** | `AP-S{C}.{N}{letter}` | All constitutions | A named, described, and cross-referenced violation of a standard. |
| **Practice** | `P{C}.{N}` | Implementation guides only | The operational how — commands, code patterns, file locations that satisfy a standard. |
| **Adaptation** | `A{N}` | Solo-dev overlay only | How a process standard applies when working without a team. |
| **Extension** | `E{N}` | Team overlay only | Additional requirements a standard carries in a multi-person team context. |

---

### 2.2 — Standard ID Format

```
S{C}.{N}
│   │
│   └── Sequence number within this constitution (1, 2, 3 … no leading zeros)
└────── Constitution number (0 through 10)
```

**Examples:**

| ID | Reads As |
|----|----------|
| `S2.13` | Backend Constitution (C2), standard 13 |
| `S3.1` | Auth Constitution (C3), standard 1 |
| `S4.81` | Frontend Constitution (C4), standard 81 |
| `S10.5` | AI Collaboration Constitution (C10), standard 5 |

**Anti-Pattern ID format:**

```
AP-S{C}.{N}{letter}
```

| ID | Reads As |
|----|----------|
| `AP-S2.13a` | First anti-pattern of Backend standard 13 |
| `AP-S3.14b` | Second anti-pattern of Auth standard 14 |

**Practice ID format** (implementation guides only):

```
P{C}.{N}
```

| ID | Reads As |
|----|----------|
| `P2.13` | Practice paired with standard S2.13 |
| `P3.14` | Practice paired with standard S3.14 |

---

### 2.3 — Priority Levels

| Priority | Meaning | Consequence of Violation |
|----------|---------|--------------------------|
| **Critical** | System breaks, security fails, or data integrity is compromised if violated | PR blocked. Build fails. No exceptions, no workarounds. |
| **High** | Quality degrades significantly or architectural integrity erodes | PR flagged. Must be resolved before merge. No exceptions. |
| **Standard** | Expected professional practice across all KSDRILL SA systems | Code review enforced. Documented deviation requires rationale. |
| **Guidance** | Recommended but adapts to context and system complexity | Deviation acceptable with documented rationale in PR. |

---

### 2.4 — Deprecated Terms

These terms are retired as of v1.0. They must not appear in any new constitutional document.

| Deprecated Term | Replaced By | Reason |
|-----------------|-------------|--------|
| Rule / R01 | Standard / `S{C}.{N}` | "Rule" implies rigid compliance culture over engineering reasoning |
| Forbidden Pattern / FP01 | Anti-Pattern / `AP-S{C}.{N}{letter}` | "Anti-Pattern" is engineering-native and implies we've seen this fail |
| "It's a rule that..." | "Per `S{C}.{N}`..." | Citing the standard ID makes it traceable and auditable |
| "The constitution says..." | "`S{C}.{N}` states..." | Precision prevents ambiguity about which constitution and which standard |

---

## §3 — Standard Format Specification

Every standard in every constitution is written in this exact format. No exceptions.
Consistency across all documents enables AI navigation, human scanning, and constitutional
auditing without needing to learn a new format per document.

---

### 3.1 — The Standard Block

````markdown
### S{C}.{N} — {Title}

| Attribute       | Value                                            |
|-----------------|--------------------------------------------------|
| **ID**          | S{C}.{N}                                         |
| **Priority**    | Critical / High / Standard / Guidance            |
| **Applies To**  | Both Stacks / Next.js Only / Angular Only        |
| **Phase**       | Phase {N} — {Name}                               |
| **Depends On**  | `S{C}.{N}` ({one-line description}) / —          |
| **Enforced By** | CI / ESLint / Code Review / Manual Audit / —     |

**Standard:**
The governing statement. What the system must do. Present tense. Active voice.
No implementation detail — only what must be true, always.

**Rationale:**
Why this standard exists. What breaks without it. Real production consequence,
not abstract principle. References real system behaviour where possible.

**Anti-Patterns:**
- `AP-S{C}.{N}a` — What the violation looks like and the specific failure it causes
- `AP-S{C}.{N}b` — Second violation pattern, if applicable

**Cross-References:** `S{C}.{N}` (reason), `S{C}.{N}` (reason)
````

---

### 3.2 — Standard Writing Rules

These rules govern how standards are written, not what they govern. Adherence to these rules
is what makes the constitutional system internally consistent.

**SR-1 — Brevity in the Standard field.**
The Standard field is one to three sentences maximum. If it requires more, the standard
covers too much and must be split into two standards.

**SR-2 — Production consequence in the Rationale field.**
The Rationale field must answer: *"What production failure does this prevent?"* If the
rationale cannot answer that question, the standard needs redesigning before it is added.

**SR-3 — Minimum one anti-pattern per standard.**
A standard without an anti-pattern is unenforceable. If you cannot name what violates it,
the standard is too vague to be useful.

**SR-4 — Direct dependencies only in Cross-References.**
Cross-References list only standards this one cannot function correctly without. Not every
related standard — only direct dependencies. Over-referencing creates noise.

**SR-5 — Applies To is always explicit.**
Never assumed. A standard that does not say "Next.js Only" or "Angular Only" applies to
both stacks without exception.

**SR-6 — No implementation in constitutions.**
The word "how" belongs in implementation guides. Constitutions answer "what" and "why."
If a standard block contains a code snippet, a file path, or a command, that content
belongs in the paired implementation guide, not the constitution.

---

## §4 — Document Structure Specification

Every constitution follows this skeleton in this order. Every implementation guide follows
the parallel structure below. No document deviates from its structure without a constitutional
amendment.

---

### 4.1 — Constitution Structure

```
1.  Document Identity Block       — header table (format defined in §4.3)
2.  Opening Quote                 — one sentence, the philosophical soul of this constitution
3.  Opening Statement             — 3–5 paragraphs: what this governs, why it exists,
                                    what it does NOT govern, how it relates to other constitutions
4.  Table of Contents             — linked, with section name and standard range
5.  Parts                         — each part is a cohesive theme (4–8 standards per part)
    ├── Part opening paragraph    — 2–3 sentences: what this part covers and why these
    │                               standards belong together
    └── Standards                 — each in the S{C}.{N} block format from §3
6.  Anti-Patterns Index           — all APs from this constitution in one flat scannable table
7.  Cross-Constitution Dependency Map
    ├── "This constitution depends on:" with reason per dependency
    └── "The following constitutions depend on this one:" with reason per dependent
8.  Amendment Log                 — table: version | date | change | reason
9.  Lock Statement                — format defined in §4.4
```

---

### 4.2 — Implementation Guide Structure

```
1.  Document Identity Block       — same format as constitutions (§4.3)
2.  Opening Statement             — how to use this guide, relationship to paired constitution,
                                    what this guide contains vs what the constitution contains
3.  Table of Contents
4.  Practice Sections             — each section paired 1:1 with a constitution part
    └── P{C}.{N} blocks           — commands, code patterns, file locations, step-by-step
5.  Code Examples                 — complete, runnable, with constitutional citation in comments
6.  Common Failure Patterns       — what goes wrong in practice and how to fix it
7.  Tools & Commands Reference    — quick-lookup table for the most used commands
8.  Amendment Log
9.  Lock Statement
```

---

### 4.3 — Document Identity Block Format

Every document opens with this table, no exceptions. Fields are always populated — never
left blank, never marked "N/A."

```markdown
| Attribute          | Value                                              |
|--------------------|----------------------------------------------------|
| **Document**       | C{N} — {Full Constitution Name}                    |
| **Organisation**   | KSDRILL SA                                         |
| **Version**        | v1.0                                               |
| **Status**         | LOCKED                                             |
| **Locked**         | 2026-05-08                                         |
| **Next Review**    | 2026-08-08                                         |
| **Applies To**     | {scope — e.g., Both Stacks / Next.js Only}         |
| **Paired With**    | {implementation guide name, or — if none}          |
```

---

### 4.4 — Lock Statement Format

Every document closes with this block, formatted exactly as shown.

```markdown
---

> **LOCKED — v1.0 — 2026-05-08**
>
> This document is locked. No standard may be added, removed, or modified
> without following the Amendment Protocol defined in C0 §8.
> Amendments take effect only after commit to `system-design-template`
> with a version bump and amendment log entry.
```

---

### 4.5 — Part Header Format

Every part within a constitution opens with this format.

```markdown
## Part {N} — {Part Name} (`S{C}.{start}`–`S{C}.{end}`)

{2–3 sentences. What this part covers. Why these standards belong together.
What builds on these standards in other constitutions.}
```

---

## §5 — Constitution Register

The canonical source of truth for all constitutions, their phases, paired documents, and
status. This register is updated on every constitutional amendment that changes the document
set. Standard count ranges (`S{C}.N`) are finalised per constitution upon that document's
lock date and back-filled here.

---

### 5.1 — Core Constitutions

| # | Constitution | Phase | Standards | Count | Paired With | Status |
|---|---|---|---|---|---|---|
| **C0** | Constitutional Order | Master | §1–§14 | — | — | LOCKED |
| **C1** | Engineering Standards | Phase 0 | S1.1–S1.97 | 97 | — | LOCKED |
| **C2** | Backend Constitution | Phase 1 | S2.1–S2.80 | 80 | C2 Backend Implementation Guide | LOCKED |
| **C3** | Auth Constitution | Phase 1 | S3.1–S3.36 | 36 | C3 Auth Implementation Guide | LOCKED |
| **C4** | Frontend Constitution | Phase 1 | S4.1–S4.82 | 82 | C4 Frontend Implementation Guide | LOCKED |
| **C5** | Database Constitution | Phase 1 | S5.1–S5.64 | 64 | C5 Database Implementation Guide | LOCKED |
| **C6** | Full-Stack Architecture | Phase 1 | S6.1–S6.44 | 44 | — | LOCKED |
| **C7** | Testing Constitution | Phase 2 | S7.1–S7.43 | 43 | — | LOCKED |
| **C8** | Platform Reliability | Phase 2 | S8.1–S8.82 | 82 | — | LOCKED |
| **C9** | Product & Feature | Phase 3 | S9.1–S9.30 | 30 | — | LOCKED |
| **C10** | AI Collaboration | Phase 3 | S10.1–S10.36 | 36 | — | LOCKED |

> **System total: 594 unique standards across 11 constitutions.**
> Every standard has exactly one home constitution. Cross-references do not imply shared
> ownership. No overlap. No footnotes.

---

### 5.2 — Supporting Documents

| Category | Documents | Purpose |
|----------|-----------|---------|
| **Implementation Guides** | C2, C3, C4, C5 implementation guides | How-to paired with each core Phase 1 constitution |
| **Overlays** | `solo-dev-overlay.md`, `team-overlay.md` | Process adaptations by operating mode |
| **Indexes** | `standards-index.md`, `anti-patterns-index.md`, `stack-assignment-matrix.md`, `quick-reference.md` | AI and human fast-navigation layer |
| **Templates** | `feature-proposal-template.md`, `incident-report-template.md`, `post-mortem-template.md`, `sprint-retro-template.md` | Mandatory document templates |
| **Runbooks** | `SEV0-response-runbook.md`, `SEV1-response-runbook.md`, `railway-deployment-runbook.md`, `vercel-rollback-runbook.md`, `database-migration-runbook.md`, `financial-freeze-runbook.md`, `ai-degradation-runbook.md` | Step-by-step operational response procedures |
| **System Contexts** | `fundslink-context.md`, `maphophe-context.md`, `reserve-bank-context.md`, `syncup-context.md` | Per-system AI session startup files |
| **ADRs** | `ADR-000-template.md` + per-decision ADR files | Architecture Decision Records |

---

## §6 — Phase Map

---

### Phase 0 — Foundation

> *If Phase 0 is skipped, no engineer on the project shares a definition of "done," no code
> quality standard exists to enforce, and the first PR introduces patterns that become
> impossible to remove without a rewrite.*

**Read before: any code is written, any branch is created, any environment is set up.**

| Constitution | What It Governs |
|---|---|
| **C1 — Engineering Standards** | How we work, how we write code, the 8-phase feature lifecycle, the feature proposal standard, self-review and PR standards, Git discipline, conventional commits, sprint governance, TypeScript and Python code quality, documentation standards |

---

### Phase 1 — Core Architecture

> *If Phase 1 is skipped or partially read, the system has no architectural boundaries, no
> auth strategy, no database assignment, and no frontend governance. The first endpoint will
> embed patterns that corrupt every endpoint that follows it.*

**Read before: the first line of application code.**

| Constitution | What It Governs |
|---|---|
| **C2 — Backend Constitution** | Service architecture, API contracts, OpenAPI-first development, database access from backend services, performance, resilience, security middleware, observability, FastAPI specifics |
| **C3 — Auth Constitution** | Authentication strategy per stack, NextAuth.js governance, JWT lifecycle, RBAC, OAuth, session management, security baseline, audit logging |
| **C4 — Frontend Constitution** | Frontend architecture, mobile-first standards, state management, Angular and Next.js specific standards, group-build methodology, layer build order |
| **C5 — Database Constitution** | Database assignment by data type, PostgreSQL and Prisma standards, MongoDB and Beanie standards, ChromaDB standards, cross-database integrity, migration governance |
| **C6 — Full-Stack Architecture** | Dual-stack system topology, stack assignment framework for new systems, request flows per stack, cross-stack communication, deployment coordination, ADR process |

---

### Phase 2 — Quality & Reliability

> *If Phase 2 is skipped, the system ships without a testing strategy, without deployment
> governance, and without incident response capability. The first production failure will be
> uncontrolled, untraceable, and unrecoverable.*

**Read before: any feature is considered production-ready.**

| Constitution | What It Governs |
|---|---|
| **C7 — Testing Constitution** | Test strategy, toolchain assignment per stack, coverage gates, unit/integration/E2E standards, test database governance, visual regression |
| **C8 — Platform Reliability Constitution** | Deployment platforms, CI/CD pipeline standards, environment governance, observability consolidation, alert thresholds, severity framework, rollback procedures, post-mortem protocol |

---

### Phase 3 — Product & Intelligence

> *Phase 3 constitutions govern what gets built and how intelligence participates in
> building it. They are last because they require all technical constitutions to be locked —
> product and AI governance decisions must be made against a stable technical foundation.*

**Read before: any feature roadmap decisions or AI-assisted development sessions.**

| Constitution | What It Governs |
|---|---|
| **C9 — Product & Feature Constitution** | Product vision, feature governance, MVP definitions, 5-gate feature qualification, user feedback integration, roadmap governance, Crown Jewel designation |
| **C10 — AI Collaboration Constitution** | AI role definitions, AI permission boundaries (L1–L4), design-phase AI workflow, build-phase AI workflow, solo dev AI pair programming protocol, CONSTITUTION-INDEX.md standard, AI anti-patterns |

---

## §7 — Constitutional Hierarchy & Conflict Resolution

---

### 7.1 — Hierarchy (Highest to Lowest Authority)

```
C0  — Constitutional Order          ← Supreme authority. Governs the governance system.
C3  — Auth Constitution             ← Security decisions. Highest domain authority.
C2  — Backend Constitution          ← Architecture and API contract decisions.
C5  — Database Constitution         ← Data storage and integrity decisions.
C4  — Frontend Constitution         ← UI, client-side, and rendering decisions.
C6  — Full-Stack Architecture       ← Integration, stack assignment, and topology.
C1  — Engineering Standards         ← Process, workflow, and code quality decisions.
C7  — Testing Constitution          ← Quality validation and coverage decisions.
C8  — Platform Reliability          ← Deployment and operational decisions.
C9  — Product & Feature             ← Product scope and feature decisions.
C10 — AI Collaboration              ← AI governance and permission boundary decisions.
```

The hierarchy governs conflicts — it does not imply importance. C9 and C10 are at the
bottom of conflict resolution order because product and AI decisions must yield to
technical correctness, not because product decisions are unimportant.

---

### 7.2 — Conflict Resolution Protocol

When two constitutions appear to conflict on a decision, the following protocol resolves it.
Do not implement until the conflict is resolved.

**Step 1 — Verify the conflict is real.**
Check whether one constitution has a stack-scope qualifier (Next.js Only / Angular Only)
that resolves the apparent conflict. Most apparent conflicts dissolve at this step — what
looks like a contradiction is often two stack-specific standards for the same concern.

**Step 2 — Apply hierarchy.**
The constitution higher in §7.1 governs. C3 (Auth) overrides C4 (Frontend) on any
decision touching authentication state. C2 (Backend) overrides C6 (Full-Stack
Architecture) on any API boundary decision. C5 (Database) overrides C2 (Backend) on any
data storage assignment question.

**Step 3 — If hierarchy does not resolve it, the conflict is a genuine gap.**
Open a constitutional amendment issue in `system-design-template`. Cite both conflicting
standards. No implementation decision is made until the amendment resolves the conflict.
Do not improvise a solution. Do not ask AI to decide.

**Step 4 — Document the resolution.**
Update both affected constitutions' amendment logs. Update the Cross-Constitution
Dependency Map in C0 §9 if the dependency relationship changed. Commit to
`system-design-template`.

---

### 7.3 — The Auth Override Rule

C3 Auth Constitution holds supreme authority over all security-touching decisions regardless
of constitutional hierarchy position. If any other constitution, implementation guide,
overlay, or AI recommendation appears to authorise a pattern that C3 prohibits, C3 governs.
Always. No vote. No discussion.

**The canonical example:** Any document stating "access token in localStorage" conflicts with
C3's in-memory storage standard. C3 wins. The conflicting document is amended. C3 is not.
This is not negotiable and not subject to the amendment protocol — it is the Auth Override
Rule, which is itself immutable.

---

## §8 — Amendment Protocol

---

### 8.1 — When an Amendment Is Required

An amendment is required for any change that affects the meaning, scope, or enforcement of
an existing standard, or that adds or removes standards from any constitution.

| Requires Amendment | Does NOT Require Amendment |
|---|---|
| Adding a new standard | Fixing a typo or grammatical error (editorial fix — commit directly) |
| Removing an existing standard | Updating a code example in an implementation guide |
| Changing a standard's scope (e.g., Both → Next.js Only) | Adding a new system context file |
| Changing a standard's priority level | Adding a new runbook |
| Restructuring a constitution's parts | Adding a new ADR |
| Merging or splitting constitutions | Adding an entry to the Common Failure Register |
| Changing the stack assignment of a standard | Updating a template document |
| Any change to C0 itself | — |

---

### 8.2 — Solo Dev Amendment Protocol

**Step 1 — Document the gap.**
Create a GitHub Issue in `system-design-template` tagged `constitutional-amendment`.
Include: (1) which constitution, (2) which standard ID, (3) why the current standard is
insufficient or incorrect, (4) the proposed new standard text in full. Evidence is required.
Build learnings, post-mortems, and production incidents are valid evidence. Personal
preference is not evidence and will not sustain an amendment.

**Step 2 — AI adversarial review.**
Paste the proposed amendment to Claude with the prompt: *"Review this constitutional
amendment for unintended consequences, cross-constitution conflicts, and whether the evidence
justifies the change."* Paste Claude's response to a second AI and request a challenge.
Document both responses in the GitHub Issue. An amendment that survives adversarial AI
review is ready for personal review. One that does not survive requires redesign.

**Step 3 — 24-hour personal review period.**
The amendment sits for 24 hours minimum after the adversarial review. No exceptions.
This period exists to prevent reactive amendments driven by frustration with a current build
problem. If the amendment still seems necessary after 24 hours, it is necessary.

**Step 4 — Approve and commit.**
Approve with documented reasoning in the GitHub Issue. Commit to `system-design-template`
with all of the following: version bump to the affected constitution, updated amendment log
entry in that constitution, updated C0 register if the standard count changes,
cross-constitution updates wherever the changed standard is referenced.
Close the GitHub Issue with the commit hash as reference.

---

### 8.3 — Team Amendment Protocol

**Step 1 — Document the gap.** Identical to solo Step 1. Evidence required.

**Step 2 — 48-hour open review.**
Post the GitHub Issue to the team channel. Any team member may comment with supporting
evidence or counterarguments during this window. Cross-constitution impacts are identified
as a team — an amendment to one constitution frequently requires changes to others.

**Step 3 — Approve and commit.**
Owner approval only: Maluleke Kurhula Success. No amendment is committed without the
owner's explicit written approval in the GitHub Issue. Commit structure is identical to
solo Step 4.

---

### 8.4 — Version Bump Rules

| Change Type | Bump | Example |
|---|---|---|
| Add a standard | Minor | v1.0 → v1.1 |
| Clarify standard language without changing meaning | Minor | v1.0 → v1.1 |
| Add stack-specific detail to an existing standard | Minor | v1.0 → v1.1 |
| Add an anti-pattern to an existing standard | Minor | v1.0 → v1.1 |
| Remove a standard | Major | v1.x → v2.0 |
| Change a standard's scope | Major | v1.x → v2.0 |
| Change a standard's priority level | Major | v1.x → v2.0 |
| Restructure a constitution's parts | Major | v1.x → v2.0 |
| Merge or split a constitution | Major | v1.x → v2.0 |

Every version bump requires an amendment log entry with: what changed, why it changed,
and the effective date. The amendment log is appended — never edited retroactively.

---

## §9 — Cross-Constitution Dependency Map

When a constitution is amended, every constitution in its dependents list must be reviewed
for required updates. This map is the starting point for that review.

```
C0 — Constitutional Order
├── Depended on by: ALL (C1 through C10)
└── Depends on: Nothing. C0 is the root.

C1 — Engineering Standards
├── Depends on: C0 (governance framework, terminology, amendment protocol)
└── Depended on by: All constitutions — feature lifecycle and Git standards
                    are referenced across all process-touching standards

C2 — Backend Constitution
├── Depends on: C0, C3 (auth middleware integration), C5 (database access from services)
└── Depended on by: C6 (request flows use backend standards),
                    C7 (API testing shapes),
                    C8 (deployment and observability standards)

C3 — Auth Constitution
├── Depends on: C0, C2 (service layer hosts auth middleware),
│              C5 (auth data lives in PostgreSQL — S5 assignment)
└── Depended on by: C2 (auth middleware in backend),
                    C4 (route guards and auth state on frontend),
                    C6 (auth per stack in integration flows),
                    C7 (auth test requirements),
                    C8 (security alerts and auth incident response)

C4 — Frontend Constitution
├── Depends on: C0, C3 (route guards use auth state),
│              C6 (stack assignment determines which frontend standards apply)
└── Depended on by: C6 (browser-side request flows),
                    C7 (frontend testing standards and toolchain)

C5 — Database Constitution
├── Depends on: C0, C2 (backend service layer governs how DB is accessed)
└── Depended on by: C2 (DB standards enforced at backend layer),
                    C3 (auth data storage assignment),
                    C6 (DB access patterns in integration architecture),
                    C7 (test database standards),
                    C8 (migration governance in deployment pipeline)

C6 — Full-Stack Architecture Constitution
├── Depends on: C0, C2, C3, C4, C5 (references all core constitutions in integration flows)
└── Depended on by: C7 (testing per stack references integration topology),
                    C8 (deployment coordination references stack topology)

C7 — Testing Constitution
├── Depends on: C0, C2 (API test shapes), C3 (auth test requirements),
│              C4 (frontend toolchain), C5 (test database standards)
└── Depended on by: C8 (CI gate — all tests must pass before production deploy)

C8 — Platform Reliability Constitution
├── Depends on: C0, C2 (deployment standards), C5 (migration governance),
│              C6 (deployment coordination), C7 (tests-pass CI gate)
└── Depended on by: C9 (MVP done criteria includes production deployment),
                    C10 (incident response is an AI permission boundary)

C9 — Product & Feature Constitution
├── Depends on: C0, all Phase 0–2 constitutions
│              (feature decisions must be technically feasible against all standards)
└── Depended on by: Nothing. C9 is the product crown jewel — terminal node.

C10 — AI Collaboration Constitution
├── Depends on: C0, ALL (AI must know every standard to not violate any of them)
└── Depended on by: Nothing. C10 is a governance addition — terminal node.
```

---

## §10 — Stack Assignment Summary

The stack decision is made once, at system design time, and is immutable for the lifetime
of that system's major version. It is driven by system requirements against defined criteria
— never by framework preference, team familiarity, or trend.

---

### 10.1 — Stack Assignment Decision Framework

| Requirement | Assigned Stack | Primary Standard |
|---|---|---|
| SEO-critical, content-driven, public-facing pages requiring SSR or SSG | **Next.js** | S6.1 |
| Enterprise-grade multi-role dashboards with complex form workflows | **Angular + FastAPI** | S6.2 |
| Precision-critical financial calculations requiring strict type safety | **Angular + FastAPI** | S6.3 |
| AI-powered features natively requiring Python (LangChain, RAG, embeddings) | **Angular + FastAPI** | S6.4 |
| WebSocket-heavy real-time features as a core platform concern | **Next.js** | S2.22 |
| Internal tools, admin panels, or simple CRUD systems | **Either stack** — complexity evaluation required via ADR | S6.5 |
| Future or unrecognised system type | **ADR required** — evaluated against rubric in C6 Part 1 | S6.6 |

**Decision flow priority order:** SEO requirement → Financial precision → Native Python AI
requirement → Dashboard complexity → Default to Next.js.

Every new system — including future systems not yet conceived — requires an Architecture
Decision Record (ADR) stored in `adrs/` before development begins. No system starts
without a locked ADR and a registered system context file.

---

### 10.2 — Locked Stack Assignments

| System | Stack | Rationale |
|---|---|---|
| **FundsLink Academy** | Angular + FastAPI | AI-powered, enterprise dashboards, financial precision, PostgreSQL + MongoDB + ChromaDB |
| **KSDRILL Reserve Bank** | Angular + FastAPI | Financial precision-critical, enterprise dashboards, complex RBAC across multiple roles |
| **Maphophe Community** | Next.js | Content-driven, public-facing, SEO-critical, geographic data integration |
| **SyncUp Creator Platform** | Next.js | Content-driven, SEO-critical, creator-facing, media-rich pages |

These assignments are immutable without a Major version amendment to C6 and a new ADR.

---

## §11 — Pre-Build Constitutional Checklist

This checklist is completed before development begins on any system and before any feature
group begins within a sprint. It is not optional and is not a formality. Every unchecked
item is a build blocker.

---

### 11.1 — System-Level Checklist (Complete Once Per System)

```
PHASE 0 — ENGINEERING STANDARDS
[ ] C1 read in full — all parts, all standards
[ ] Operating mode confirmed: SOLO or TEAM
[ ] Correct overlay loaded: solo-dev-overlay.md or team-overlay.md
[ ] System context file created in system-contexts/{system}-context.md
[ ] Build phase confirmed and documented in system context file
[ ] CONSTITUTION-INDEX.md created in project workspace (S10.4)

PHASE 1 — CORE ARCHITECTURE
[ ] Stack assignment confirmed — ADR written and committed to adrs/
[ ] C2 Backend Constitution read — stack-specific standards identified
[ ] C3 Auth Constitution read — auth strategy confirmed for this stack
[ ] C4 Frontend Constitution read — stack-specific standards identified
[ ] C5 Database Constitution read — database assignment documented for all data types
[ ] C6 Full-Stack Architecture read — request flows and deployment coordination understood
[ ] OpenAPI contract drafted before any endpoint code (S2.7)

PHASE 2 — QUALITY & RELIABILITY
[ ] C7 Testing Constitution read — toolchain confirmed for this stack
[ ] C8 Platform Reliability read — deployment platform confirmed, monitoring planned
[ ] Three environments confirmed: development · staging · production
[ ] CI/CD pipeline planned — all gates defined

PHASE 3 — PRODUCT & INTELLIGENCE
[ ] C9 Product & Feature read — MVP definition confirmed, 5-gate questions answered
[ ] C10 AI Collaboration read — AI workflow mode confirmed (SOLO or TEAM)
[ ] AI permission boundaries active and understood
[ ] CONSTITUTION-INDEX.md loaded in editor before first session
```

---

### 11.2 — Feature-Level Checklist (Complete Per Feature, Every Sprint)

```
PRE-CODE GATE — Phase 0 of Feature Lifecycle (S1.27)
[ ] Feature proposal written using feature-proposal-template.md (all 7 fields)
[ ] Proposal reviewed: AI adversarial review (SOLO) or team discussion (TEAM)
[ ] Proposal approved — GitHub Issue opened and self-assigned
[ ] Full data flow traced for this feature without writing code
[ ] Constitutional standards relevant to this feature identified by ID
[ ] All layers involved identified: frontend / service / API / database
[ ] Database(s) touched confirmed correct per S5.1 assignment criteria
[ ] OpenAPI contract written if this feature adds or changes any endpoint

BUILD GATE — Before PR Is Opened (S1.45)
[ ] Self-review checklist completed — all 4 quadrants passed
[ ] Tests written alongside implementation — not after (S7.1)
[ ] CI fully green locally before PR is opened
[ ] No console.log, debugger, or commented-out code present
[ ] Layer build order followed: interface → service → component → UI (S4.81)
[ ] One commit per layer — not one giant commit at end of feature
[ ] PR description completed using pr-description-template (all fields)
[ ] Screenshots attached for any UI change
```

---

## §12 — Review Calendar

Constitutional reviews are scheduled, not ad-hoc. A review confirms that existing standards
are still correct and sufficient, or produces evidence for an amendment. A scheduled review
that finds no gaps produces a single log entry: *"Reviewed — no changes required."*

| Review Type | Frequency | Scope | Trigger |
|---|---|---|---|
| **Quarterly Review** | Every 3 months | All constitutions — check for gaps, outdated standards, version drift | Calendar. Next: 2026-08-08 |
| **Post-Mortem Review** | After every SEV0 or SEV1 incident | Constitutions governing the affected system layer | Incident post-mortem completion |
| **Post-Sprint Review** | After each sprint retrospective | C1 (process), C9 (product) | Sprint retrospective |
| **Stack Addition Review** | When a new system begins | C6 (stack assignment), C0 (register update) | New system ADR creation |
| **Post-Feature-Group Review** | After a feature group ships | Constitutions governing that feature group's layers | Feature group completion sign-off |

---

## §13 — Common Failure Register

The Common Failure Register maps known failure patterns — drawn from production incidents,
post-mortems, and documented build problems — to their violated standard, consequence,
severity, and recovery path.

This register is the operational memory of the constitutional system. Every entry is
evidence that the corresponding standard is critical. Every post-mortem that identifies a
new failure pattern produces a new entry. The register grows — it is never pruned.

---

### 13.1 — How to Read This Register

| Column | Meaning |
|--------|---------|
| **ID** | Unique failure reference — use in post-mortems and amendment issues |
| **Failure** | What was observed — the symptom, not the root cause |
| **Violated Standard** | The standard that was absent or ignored |
| **Consequence** | What broke or could break — production impact |
| **Severity** | SEV0–SEV3 classification per C8 severity framework |
| **Recovery** | How to resolve — runbook reference where applicable |

---

### 13.2 — Register

| ID | Failure | Violated Standard | Consequence | Severity | Recovery |
|----|---------|-------------------|-------------|----------|----------|
| **CF-01** | Access token stored in localStorage | `AP-S3.14a` | XSS attack can steal the token — 15-minute attack window with no revocation capability | SEV1 | Move to Angular in-memory store. Rotate all active sessions. Alert in Sentry. |
| **CF-02** | Raw SQL bypassing Prisma in production service | `AP-S2.13a` | Schema migrations break silently. Writes are untracked. TypeScript type safety lost at the query boundary. | SEV2 | Replace with Prisma query. Run `prisma migrate status`. Audit all recent writes from that service. |
| **CF-03** | Financial transaction data written to MongoDB | `AP-S5.3a` | No ACID guarantees. Balance inconsistency possible. Data integrity cannot be verified. | SEV0 | Freeze financial operations (financial-freeze-runbook). Audit MongoDB writes. Migrate to PostgreSQL. |
| **CF-04** | Direct push to main branch bypassing PR | `AP-S1.T16a` | Unreviewed code in production. No rollback commit point. No CI gate was executed. | SEV1 | Revert commit on main. Restore branch protection rules. Write post-mortem. |
| **CF-05** | Feature built and submitted as PR without a proposal | `AP-S1.27a` | Scope creep. Untested edge cases. No acceptance criteria. PR unmergeable without retroactive proposal. | SEV3 | Proposal written retroactively. PR held until proposal approved and GitHub Issue linked. |
| **CF-06** | PR opened without completing self-review checklist | `AP-S1.45a` | console.log in production. Unused imports. Architecture violations unspotted by author. Review cycle wasted. | SEV3 | PR returned to author. Self-review checklist completed before review cycle restarts. |
| **CF-07** | Authentication data stored in MongoDB | `AP-S3.2a` | No ACID guarantees on session data. Race condition in token validation possible. Session inconsistency. | SEV0 | Freeze auth operations. Migrate auth data to PostgreSQL. Full auth audit. |
| **CF-08** | Angular browser calling FastAPI directly, bypassing Next.js proxy | `AP-S2.2a` | CORS violation. Security boundary broken. Internal API key exposed to browser. | SEV1 | Block direct endpoint at network level. Route through Next.js API route as proxy. |
| **CF-09** | `any` type used in TypeScript production code | `AP-S1.Q2a` | Type safety removed at that boundary. Runtime errors that TypeScript would have caught at compile time reach production. | SEV3 | Replace with `unknown` + type guard. ESLint rule enforces going forward. |
| **CF-10** | Tests written after the feature PR, not alongside | `AP-S7.1a` | Tests written to match broken implementation, not correct behaviour. Coverage gates never catch the real defect. | SEV3 | Tests rewritten against acceptance criteria from the feature proposal. Not against the code. |
| **CF-11** | Endpoint implemented before OpenAPI contract was written | `AP-S2.7a` | Frontend blocked mid-sprint. Contract written after implementation breaks Zod and Pydantic parity. Both ends require rework. | SEV2 | Sprint blocked. Contract written and reviewed before implementation resumes. |
| **CF-12** | Stack changed mid-build without a constitutional amendment | `AP-S1.4a` | Architectural integrity destroyed. Constitutional standards apply incorrectly. System is in an undefined state. | SEV0 | Stop all development immediately. Constitutional review. Amendment or full revert to last known good state. |
| **CF-13** | Database migration deployed after service started, not before | `AP-S5.Na` | Service runs against old schema. Startup errors. Possible data corruption in writes during the window. | SEV1 | Rollback service to previous version. Run migration. Re-deploy service. Validate data integrity. |
| **CF-14** | AI output accepted as a constitutional amendment without following §8 protocol | `AP-S10.6a` | Constitution drifts from its own amendment protocol. Unreviewed standard change enters the codebase silently. | SEV2 | Revert the change. Open proper amendment issue in system-design-template. Follow §8 protocol fully. |
| **CF-15** | Production deploy executed without staging validation | `AP-S8.Ia` | Untested code in production. No validation gate executed. Unknown failure surface exposed to users. | SEV1 | Rollback production to previous version. Deploy to staging. Validate fully. Promote to production. |

---

## §14 — Amendment Log

| Version | Date | Change | Reason |
|---------|------|--------|--------|
| v1.0 | 2026-05-08 | Initial lock — full rebuild of the KSDRILL SA constitutional system. HTML → Markdown. New terminology system (Standards, Anti-Patterns, Practices). Constitution-scoped standard ID format (`S{C}.{N}`). Solo/team split moved to overlays only. C1 formed by merging Team & Process + Code Quality + MentorConnect workflow. C6 formed by merging Full System Design + Full-Stack Integration. C8 formed by merging Infrastructure + Incident Response. C10 AI Collaboration added as new Phase 3 constitution with five-engineer relay model (Claude, Claude Code, ChatGPT, DeepSeek, Kimi). Implementation guides for C2, C3, C4, C5 at full depth. Auth localStorage regression (CF-01) fixed in C3 S3.14. API versioning gap addressed in C2 S2.76–S2.80. Observability consolidated into C8. Tailwind+Custom CSS dual-tool philosophy formalised in C4. ORM+Raw SQL dual-tool philosophy formalised in C5. ADRs for all four flagship systems locked. CONSTITUTION-INDEX.md template added. AI Engineer Workflow constitutionalized in workflow/. §5 standard counts populated: 594 total unique standards across C1–C10. | Full system rebuild — version reset. |

---

> **LOCKED — v1.0 — 2026-05-08**
>
> This document is locked. No section, standard, format specification, protocol, or register
> entry may be added, removed, or modified without following the Amendment Protocol defined
> in §8 of this document.
>
> The Constitutional Order is the supreme document of the KSDRILL SA governance system.
> All other constitutions derive their authority from this document. All amendments to all
> other constitutions are subject to the principles, hierarchy, and protocol defined here.
>
> Amendments take effect only after commit to `system-design-template` with a version bump,
> amendment log entry, and all required cross-constitution updates.
