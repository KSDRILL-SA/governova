# C10 — AI Collaboration Constitution

---

| Attribute          | Value                                                              |
|--------------------|--------------------------------------------------------------------|
| **Document**       | C10 — AI Collaboration Constitution                                |
| **Organisation**   | KSDRILL SA                                                         |
| **Version**        | v1.0                                                               |
| **Status**         | LOCKED                                                             |
| **Locked**         | 2026-05-08                                                         |
| **Next Review**    | 2026-08-08                                                         |
| **Applies To**     | All Systems · Both Stacks · Solo Dev · Team                        |
| **Paired With**    | `AI-INSTRUCTIONS.md` (AI entry point for every session)            |

---

> *"AI is the most powerful engineering collaborator ever created. It requires the same governance as any other collaborator: clear roles, explicit boundaries, and human accountability for every decision."*

---

## Opening Statement

AI tools are not auxiliary — they are active participants in the KSDRILL SA engineering process. Claude conducts architectural reviews. Cursor writes implementation code. A second AI stress-tests proposals. These tools participate in every phase of development: design, implementation, testing, and incident analysis. Governing them is not optional.

This constitution is new. Nothing in the previous constitutional system addressed AI governance because AI tools were not yet first-class engineering participants when those documents were written. The world has changed. This constitution is the governance layer for that change.

This constitution is last in phase order (Phase 3) and last in the dependency chain — it depends on all other constitutions because AI must know every standard across all constitutions to not violate any of them. Its position at the end is structural: AI governance decisions require a stable technical foundation, and it would be architecturally incorrect to define AI permission boundaries before the standards those boundaries reference are locked.

This constitution defines: what roles AI tools play in the workflow, what authority each role carries, what AI is permitted and forbidden from doing, how AI participates in solo and team development, what must be true about every build session (the `CONSTITUTION-INDEX.md` standard), and the anti-patterns that signal AI is being used incorrectly.

The core principle is permanent: **AI may propose, recommend, and implement. AI may never approve. Approval — of standards changes, security decisions, stack assignments, and production actions — is a human responsibility that cannot be delegated to any AI tool regardless of its capability.**

---

## Table of Contents

| Part | Title | Standards |
|------|-------|-----------|
| Part 1 | AI Role Definitions | S10.1–S10.7 |
| Part 2 | Permission Boundaries — L1 to L4 | S10.8–S10.14 |
| Part 3 | Design Phase AI Workflow | S10.15–S10.20 |
| Part 4 | Build Phase AI Workflow — CONSTITUTION-INDEX.md | S10.21–S10.26 |
| Part 5 | Solo Dev AI Pair Programming Protocol | S10.27–S10.32 |
| Part 6 | Team AI Governance | S10.33–S10.36 |
| Anti-Patterns Index | — | AP-S10.* |
| Cross-Constitution Dependency Map | — | — |
| Amendment Log | — | — |

---

## Part 1 — AI Role Definitions (`S10.1`–`S10.7`)

Each AI tool in the workflow has a defined role. The role determines what the tool is asked to do and what authority its output carries. Using an AI tool outside its defined role is a governance violation.

---

### S10.1 — Primary Architect (Claude) — Proposes, Cannot Approve

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S10.1 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 3 — Product & Intelligence |
| **Depends On**  | `C0 §8` (amendment protocol) |
| **Enforced By** | Session protocol (S10.15) |

**Standard:**
Claude (primary session AI) acts as the Primary Architect in design sessions. It analyses requirements, proposes architecture, cites constitutional standards, identifies gaps and violations, and produces design documents. It cannot approve its own proposals. All architectural proposals from Claude are subject to adversarial review (S10.3) and human approval before implementation begins.

**Rationale:**
A proposer who also approves their own proposals has no review. The Primary Architect role is valuable precisely because it can generate and articulate architectural options at speed — the review role must be separate to preserve that value.

**Anti-Patterns:**
- `AP-S10.1a` — "Claude said the architecture is correct, so we can start building" — Claude proposed the architecture; Claude cannot validate it. Adversarial review and human approval are required before any implementation.

**Cross-References:** `S10.3` (Devil's Advocate role), `S10.8` (L4 approval is human-only)

---

### S10.2 — In-Editor AI (Cursor/Copilot) — Builder, Implements Approved Designs Only

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S10.2 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 3 — Product & Intelligence |
| **Depends On**  | `S10.4` (CONSTITUTION-INDEX.md), `S10.21` (build phase protocol) |
| **Enforced By** | Build session protocol |

**Standard:**
In-editor AI (Cursor, GitHub Copilot) acts as the Builder. It implements designs that have been approved through the design phase. It may not deviate from the architecture defined in `CONSTITUTION-INDEX.md` without flagging the deviation for human review. It follows the layer build order (S4.79) and uses conventional commits (S1.17).

**Rationale:**
In-editor AI optimises for code generation speed. Without the `CONSTITUTION-INDEX.md` constraint, it generates code aligned with general patterns rather than the specific constitutional standards governing this system. The constraint makes the builder work within the approved design.

**Anti-Patterns:**
- `AP-S10.2a` — Starting a Cursor build session without loading `CONSTITUTION-INDEX.md` — Cursor generates code without constitutional context, producing implementations that violate stack-specific standards.

**Cross-References:** `S10.4` (CONSTITUTION-INDEX.md), `S10.21` (build phase entry requirement)

---

### S10.3 — Devil's Advocate AI — Challenges Primary Proposals

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S10.3 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 3 — Product & Intelligence |
| **Depends On**  | `S10.1` (Primary Architect role) |
| **Enforced By** | Design session protocol (S10.15) |

**Standard:**
A second AI (different session, different context window from the Primary Architect) is used to stress-test architectural proposals before human approval. The Devil's Advocate is given the proposal and asked explicitly: "What are the weakest assumptions? What failure modes are not addressed? What constitutional standards does this potentially violate?" Its output challenges — it does not override — the Primary Architect's proposal.

**Rationale:**
An architectural proposal reviewed only by the AI that generated it has no second opinion. A proposal that survives a Devil's Advocate challenge is more likely to hold up in implementation. The human then reviews the proposal and the challenge together.

**Anti-Patterns:**
- `AP-S10.3a` — Asking the same Claude conversation to be both Primary Architect and Devil's Advocate — the context window anchors to its initial position; genuine adversarial review requires a fresh context.

**Cross-References:** `S10.1` (Primary Architect), `C0 §8.2` (solo amendment protocol uses adversarial review)

---

### S10.4–S10.7 — Additional Role Standards

> **S10.4** — Document Analyst AI (large context window): loads complete constitutional documents to find inconsistencies, version drift, cross-reference gaps, and gaps in standard coverage. Used for constitutional reviews and pre-build audits. Reads and reports — makes no decisions.

> **S10.5** — Sanity Check AI: receives targeted questions with specific context. Validates specific technical decisions against a narrow scope. Used for: "Is this Prisma query correctly handling the soft delete filter?" Never used for broad architectural decisions.

> **S10.6** — Every AI session begins with the AI reading `AI-INSTRUCTIONS.md` and the relevant system context file before any technical discussion begins. An AI session that begins with a technical question before loading context operates without constitutional grounding.

> **S10.7** — AI roles are not assigned to specific tools permanently — they are assigned per session based on the task. Claude is not always the Primary Architect; for a stress-test session, Claude may be the Devil's Advocate.

---

## Part 2 — Permission Boundaries (`S10.8`–`S10.14`)

The permission boundary framework governs what AI is authorised to do independently versus what requires human action.

---

### S10.8 — L4 Approval Is Human-Only — Always

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S10.8 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 3 — Product & Intelligence |
| **Depends On**  | `C0 §8` (amendment protocol) |
| **Enforced By** | Session protocol · Human review |

**Standard:**
The highest permission level (L4 — Approve) is permanently and exclusively reserved for humans. AI cannot approve: constitutional amendments, security architecture decisions, production deployments, stack assignments, database migrations in production, or any decision that changes the system in a way that cannot be automatically reversed. This boundary is immutable — it cannot be amended by any constitutional process.

**Rationale:**
The ability to approve irreversible or high-consequence decisions must rest with accountable humans. AI tools have no accountability, no liability, and no stake in the outcome. The value AI provides (speed, pattern recognition, recall) is not diminished by this boundary — it is enhanced by having a clear human accountability layer above it.

**Anti-Patterns:**
- `AP-S10.8a` — "Claude reviewed the security decision and approved it, so we can proceed" — Claude reviewed and recommended; a human must approve. There is no scenario where Claude's review constitutes approval.

**Cross-References:** `C0 §8` (amendment protocol — human approval required), `S3.36` (security changes require human review)

---

### S10.9–S10.14 — Permission Level Definitions

| Level | Category | AI Permission | Examples |
|-------|----------|--------------|---------|
| **L1 — Propose** | Unconstrained generation | AI freely proposes any technical direction | Architecture options, code patterns, constitutional gap analysis |
| **L2 — Recommend** | Citation-gated | AI recommends with standard citation — human evaluates | "Per S2.7 (OpenAPI-first), I recommend..." |
| **L3 — Implement** | Design-gated | AI implements approved, documented design — human reviews | Cursor building a service function against `CONSTITUTION-INDEX.md` |
| **L4 — Approve** | Human-only | AI cannot approve | Constitutional amendments, production deploys, security decisions, stack assignments |

> **S10.9** — L1 proposals require no citation — they are generating options. L2 recommendations must cite the specific standard ID that supports the recommendation (`S2.7`, `S3.14`, etc.). An L2 recommendation without a standard citation is an L1 proposal dressed as a recommendation.

> **S10.10** — L3 implementation requires: the design is documented in `CONSTITUTION-INDEX.md`, the design was approved by a human (L4), and the implementation follows the layer build order (S4.79). A Cursor session that starts implementing without an approved design is L1 masquerading as L3.

> **S10.11** — Security decisions (auth strategy, token storage, role definitions, CORS configuration) are always L4 — human approval required regardless of how clear the AI's recommendation is.

> **S10.12** — Database schema changes are always L4 — schema changes require human review of the migration, the rollback plan, and the backward compatibility assessment (S5.59–S5.64).

> **S10.13** — AI recommendations that contradict a constitutional standard are flagged, not silently complied with. The AI states: "This recommendation conflicts with `S3.14` (access token in Angular memory). Following the recommendation would require a constitutional amendment per C0 §8."

> **S10.14** — When AI detects a potential constitutional violation in existing code, it flags the violation and the violated standard — it does not silently work around the violation by generating compliant wrappers that obscure the underlying problem.

---

## Part 3 — Design Phase AI Workflow (`S10.15`–`S10.20`)

The design phase is the most valuable use of AI in the engineering workflow. It is the phase where architectural decisions have the highest leverage and the lowest cost to change. These standards govern how AI participates in the design phase.

---

### S10.15 — Design Phase Follows Three-Phase Protocol — Outside Editor First

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S10.15 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 3 — Product & Intelligence |
| **Depends On**  | `S1.1` (design first), `S10.1`–`S10.5` (role definitions) |
| **Enforced By** | Session protocol |

**Standard:**
The design phase follows this three-step sequence before any code is written:

**Phase 1 — Outside the editor (Claude primary):**
1. Load `AI-INSTRUCTIONS.md` + system context + relevant constitutions
2. Present the feature requirements to Claude (Primary Architect role)
3. Claude generates architectural proposal with standard citations
4. Adversarial review: second AI (Devil's Advocate) stress-tests the proposal
5. Human reviews both outputs, makes final architectural decision

**Phase 2 — Validate and align:**
1. `CONSTITUTION-INDEX.md` in the project is updated with the approved design
2. Relevant constitutional standards are confirmed against the design
3. OpenAPI contract drafted (if feature adds endpoints — S2.7)
4. Database schema reviewed or updated (if feature modifies schema)
5. Human confirms: "Design is locked, ready to implement"

**Phase 3 — Inside the editor (Cursor/Builder):**
1. Load `CONSTITUTION-INDEX.md` in Cursor context
2. Follow layer build order: interfaces → service → component → UI (S4.79)
3. One commit per layer (S4.80)
4. Tests written alongside each layer (S7.1)

**Anti-Patterns:**
- `AP-S10.15a` — Claude → Cursor directly, skipping adversarial review and design validation — implements an unreviewed proposal; constitutional violations discovered in code review are expensive to fix.

**Cross-References:** `S1.1` (design first), `S10.3` (Devil's Advocate), `S10.4` (CONSTITUTION-INDEX.md)

---

### S10.16–S10.20 — Additional Design Phase Standards

> **S10.16** — The design session document (Claude's proposal, Devil's Advocate's challenge, and human resolution) is saved to a `decisions/` folder in the project or as a GitHub Issue comment. Design decisions are not ephemeral chat — they are documented decisions.

> **S10.17** — Constitutional gaps identified during design (a situation not covered by any existing standard) are documented as constitutional amendment proposals following C0 §8, not solved by improvisation.

> **S10.18** — When AI proposes a design that requires a stack deviation, it must immediately flag the constitutional amendment required: "This proposal would require an amendment to `S4.1` (framework assignment) per C0 §8."

> **S10.19** — AI-generated architecture diagrams, data flow descriptions, and system topology descriptions are treated as proposals (L1) — never as approved designs until a human confirms them.

> **S10.20** — The design phase is not skipped for "small" features. A feature that touches authentication, database schema, or the API contract is not small — it requires the full design phase protocol.

---

## Part 4 — Build Phase — CONSTITUTION-INDEX.md Standard (`S10.21`–`S10.26`)

---

### S10.21 — CONSTITUTION-INDEX.md Required in Every Project Workspace

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S10.21 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 3 — Product & Intelligence |
| **Depends On**  | `C0 §11` (pre-build checklist includes this) |
| **Enforced By** | Pre-build checklist · Build session entry check |

**Standard:**
Every project has a `CONSTITUTION-INDEX.md` file in its root. This file is the AI's in-project constitutional reference. It is loaded into the editor AI's context at the start of every build session. Without it, the builder AI has no constitutional context and generates code against general patterns rather than this system's specific standards.

**Rationale:**
The constitutional system is stored in `system-design-template`, not in the application repository. The `CONSTITUTION-INDEX.md` bridges the gap — it is the project's declared subset of relevant standards, current ADRs, and approved deviations. It makes the constitutional system actionable inside the editor.

**Anti-Patterns:**
- `AP-S10.21a` — Starting a Cursor build session without loading `CONSTITUTION-INDEX.md` — Cursor generates code without constitutional context; stack-specific standards (OnPush, interceptor deduplication, Decimal types) are silently violated.

**Cross-References:** `C0 §11` (pre-build checklist), `S10.2` (builder role requires CONSTITUTION-INDEX.md)

---

### S10.22 — CONSTITUTION-INDEX.md — Required Sections

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S10.22 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 3 — Product & Intelligence |
| **Depends On**  | `S10.21` (file existence) |
| **Enforced By** | Pre-build review |

**Standard:**
`CONSTITUTION-INDEX.md` must contain these sections:

```markdown
# CONSTITUTION-INDEX — {System Name}

## System Identity
- System: {name}
- Stack: Next.js / Angular+FastAPI
- Build Phase: Phase {N} — {description}
- Active Group: G{N} — {description}
- Operating Mode: SOLO / TEAM

## Active Constitutional Standards
List of S{C}.{N} IDs most relevant to the current build group,
with one-line descriptions. Not all 300+ standards — the 15–20
most critical for this system's current architectural complexity.

## Approved Deviations (ADRs)
Any ADR that approves a deviation from a standard, with the
standard ID, ADR reference, and approved alternative.

## Current Sprint
Sprint {N}: {goal}
Active tickets: {list}
Active feature proposal: {link}

## Critical Anti-Patterns for This System
The 5–8 most dangerous anti-patterns for this specific system
given its stack and current build phase.
```

**Anti-Patterns:**
- `AP-S10.22a` — `CONSTITUTION-INDEX.md` that lists all 300+ standards — unreadable and uncurated; the point is a focused, buildable subset, not a copy of the full constitutional system.

**Cross-References:** `S10.21` (file existence), `system-contexts/` (system context file provides the inputs)

---

### S10.23–S10.26 — Additional Build Phase Standards

> **S10.23** — `CONSTITUTION-INDEX.md` is updated at the start of every sprint with the current sprint goal, active feature, and active feature group. A stale index from a previous sprint is equivalent to no index.

> **S10.24** — The builder AI (Cursor) explicitly acknowledges `CONSTITUTION-INDEX.md` at the start of the session. If Cursor does not acknowledge it, the file was not loaded correctly — reload and verify before proceeding.

> **S10.25** — Code generated by the builder AI is reviewed by the human for constitutional compliance before committing. The layer build order (S4.79) ensures each commit is reviewable at the layer level.

> **S10.26** — Build sessions that run longer than 4 hours without a commit should reset context: commit what is working, reload `CONSTITUTION-INDEX.md`, and start a fresh session. Context window degradation over long sessions produces lower-quality, less constitutionally aligned output.

---

## Part 5 — Solo Dev AI Pair Programming Protocol (`S10.27`–`S10.32`)

Solo development with AI is a distinct operating mode. These standards define how AI fills the roles that teammates provide in a team context.

---

### S10.27 — AI as Second Code Reviewer in Solo Mode

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S10.27 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 3 — Product & Intelligence |
| **Depends On**  | `S10.1` (Claude role), `solo-dev-overlay.md` |
| **Enforced By** | Solo dev PR protocol |

**Standard:**
In solo development, before merging any non-trivial PR to main, the diff is reviewed by Claude with the prompt: "Review this code for constitutional violations, anti-patterns from the relevant constitution, and any deviations from the approved design in `CONSTITUTION-INDEX.md`. Cite the specific standard for any issue identified." The review result is documented in the PR description. This is not optional — it is the substitute for the second human reviewer required in team mode.

**Rationale:**
Code review by another person exists because the author of the code has blind spots. In solo mode, those blind spots are not covered by a teammate. Claude-as-reviewer specifically fills that role — it has no author bias and has deep familiarity with the constitutional standards.

**Anti-Patterns:**
- `AP-S10.27a` — Merging to main without the AI code review session documented in the PR — the solo-dev 2-reviewer substitute was skipped; unreviewed code enters the main branch.

**Cross-References:** `solo-dev-overlay.md` (S1.30 solo adaptation), `S1.45` (author self-review checklist)

---

### S10.28–S10.32 — Additional Solo Mode Standards

> **S10.28** — AI as proposal reviewer: feature proposals (S1.27) in solo mode are reviewed by Claude using adversarial review (S10.3) before self-approval. The review is documented in the GitHub Issue for the feature.

> **S10.29** — AI as standup accountability: at the start of every session, the dev log from the previous session is presented to Claude: "Review this dev log. What blockers were identified? What was the plan? Has the plan been followed?" This replaces the team standup accountability mechanism.

> **S10.30** — AI as SEV classifier in incident response: when a production issue is detected, Claude is given the symptom description and asked to classify the severity and suggest the runbook. Claude suggests — the human classifies and acts.

> **S10.31** — AI as constitutional amendment evaluator: before the 24-hour personal review period (C0 §8.2), Claude reviews the proposed amendment for unintended consequences and cross-constitution conflicts. Claude's output is documented in the amendment GitHub Issue.

> **S10.32** — AI output in solo mode is documented, not ephemeral. Review sessions, proposal adversarial reviews, and amendment evaluations are documented in GitHub Issues or dev log entries. Undocumented AI interactions provide no audit trail and no knowledge transfer.

---

## Part 6 — Team AI Governance (`S10.33`–`S10.36`)

> **S10.33** — In team mode, AI recommendations require a human to evaluate and cite the standard basis before the recommendation is actioned. "Claude said to do this" is never sufficient justification in a team PR review.

> **S10.34** — AI code review sessions (S10.27) are additive in team mode — they supplement human review, not replace it. The 2-approval rule (S1.30) remains a 2-human-approval rule. AI review is a third review, not a substitute.

> **S10.35** — Team members using AI tools document which AI tools were used in significant design decisions in the PR description. This enables the team to evaluate whether the constitutional AI workflow was followed.

> **S10.36** — AI tools are not given access to production credentials, production database connections, or production Railway/Vercel dashboards. AI operates on code and design — not on live production systems.

---

## Anti-Patterns Index

| ID | Description | Violated Standard | Severity |
|----|-------------|-------------------|----------|
| `AP-S10.1a` | "Claude said it's correct, we can start building" | S10.1 | Critical |
| `AP-S10.2a` | Cursor build session started without loading CONSTITUTION-INDEX.md | S10.2 | Critical |
| `AP-S10.3a` | Same Claude session used for both proposal and adversarial review | S10.3 | High |
| `AP-S10.6a` | AI session starts with technical question before loading AI-INSTRUCTIONS.md | S10.6 | High |
| `AP-S10.8a` | "Claude approved the security decision" | S10.8 | Critical |
| `AP-S10.9a` | L2 recommendation without standard citation | S10.9 | Standard |
| `AP-S10.10a` | L3 implementation started without approved design | S10.10 | Critical |
| `AP-S10.11a` | Auth architecture decided without human L4 approval | S10.11 | Critical |
| `AP-S10.13a` | AI silently complies with constitutional violation | S10.13 | Critical |
| `AP-S10.15a` | Claude → Cursor directly, skipping adversarial review | S10.15 | Critical |
| `AP-S10.21a` | Build session started without CONSTITUTION-INDEX.md | S10.21 | Critical |
| `AP-S10.22a` | CONSTITUTION-INDEX.md lists all 300+ standards | S10.22 | Standard |
| `AP-S10.27a` | PR merged to main without AI code review documented | S10.27 | High |

---

## Cross-Constitution Dependency Map

**This constitution depends on:**
| Dependency | Reason |
|------------|--------|
| `C0 — Constitutional Order` | Amendment protocol, terminology — AI operates within C0 governance |
| `ALL (C1–C9)` | AI must know every standard across all constitutions to flag violations and cite standards correctly |

**The following constitutions depend on this one:**
| Dependent | Reason |
|-----------|--------|
| *None* — C10 is a terminal node. It governs the AI tools that assist with all other constitutions. |

---

## Amendment Log

| Version | Date | Change | Reason |
|---------|------|--------|--------|
| v1.0 | 2026-05-08 | Initial lock — new constitution with no predecessor. Built from MentorConnect AIStack methodology, KSDRILL SA AI workflow experience, and the master design review plan. Three-phase design workflow formalised (S10.15). CONSTITUTION-INDEX.md standard formalised (S10.21–S10.22). Permission boundary framework L1–L4 formalised (S10.9–S10.14). Solo dev AI protocol formalised (S10.27–S10.32). | New constitution — governs a new class of actor that did not have governance in the previous constitutional system. |

---

> **LOCKED — v1.0 — 2026-05-08**
>
> This document is locked. No standard may be added, removed, or modified
> without following the Amendment Protocol defined in C0 §8.
> Amendments take effect only after commit to `system-design-template`
> with a version bump and amendment log entry.
>
> C10 is the final constitution. It governs the AI tools that help build everything else.
> The boundary it holds — AI proposes, AI implements, humans approve — is not a limitation.
> It is the design.
