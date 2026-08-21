# C10 — AI Collaboration Constitution

---

| Attribute          | Value                                                              |
|--------------------|--------------------------------------------------------------------|
| **Document**       | C10 — AI Collaboration Constitution                                |
| **Organisation**   | KSDRILL SA                                                         |
| **Version**        | v1.2                                                               |
| **Status**         | LOCKED                                                             |
| **Locked**         | 2026-05-08                                                         |
| **Next Review**    | 2026-08-08                                                         |
| **Applies To**     | All Systems · Both Stacks · Solo Dev · Team                        |
| **Paired With**    | `AI-INSTRUCTIONS.md` · `workflow/ksdrill-sa-ai-workflow.md`        |

---

> *"AI is the most powerful engineering collaborator ever created. It requires the same governance as any other collaborator: clear roles, explicit boundaries, and human accountability for every decision."*

---

## Opening Statement

AI tools are not auxiliary — they are active participants in the KSDRILL SA engineering process. KSDRILL SA operates with five AI engineers in a linear relay: Claude (Principal Architect), Claude Code (Senior Engineer), ChatGPT (Debugger + UI Engineer), DeepSeek (Reasoning Engine), and Kimi (Experimental Lab Engineer). Each has a defined role, clear ownership, and explicit permission boundaries. No two engineers work simultaneously. The Founder approves every handoff. This is not a preference — it is the operating model.

This constitution is new. Nothing in the previous constitutional system addressed AI governance because AI tools were not yet first-class engineering participants when those documents were written. The world has changed. This constitution is the governance layer for that change.

This constitution is last in phase order (Phase 3) and last in the dependency chain — it depends on all other constitutions because AI must know every standard across all constitutions to not violate any of them. Its position at the end is structural: AI governance decisions require a stable technical foundation, and it would be architecturally incorrect to define AI permission boundaries before the standards those boundaries reference are locked.

This constitution defines: the five AI engineer roles and their permission boundaries, the relay workflow and Founder approval gate, what AI is permitted and forbidden from doing, the CONSTITUTION-INDEX.md standard, the Handoff Protocol, and the anti-patterns that signal AI is being used incorrectly.

The operational detail of how these standards are applied in practice — the relay diagram, the full Handoff Protocol (Parts A–D), the Repo Verification checklist, the engineer-specific briefing formats — lives in `workflow/ksdrill-sa-ai-workflow.md`. This constitution governs the principles. The workflow document governs the execution.

The core principle is permanent: **AI may propose, recommend, and implement. AI may never approve. Approval — of standards changes, security decisions, stack assignments, production actions, and relay handoffs — is a human responsibility that cannot be delegated to any AI tool regardless of its capability.**

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
| Part 7 | Relay Handoff Verification | S10.37–S10.38 |
| Part 8 | AI Feature Integration | S10.39 |
| Anti-Patterns Index | — | AP-S10.* |
| Cross-Constitution Dependency Map | — | — |
| Amendment Log | — | — |

---

## Part 1 — AI Role Definitions (`S10.1`–`S10.7`)

KSDRILL SA operates five AI engineers in a fixed relay. Each has a designated role, defined ownership, and permission boundaries. The relay order is immutable. The Founder approval gate at every handoff is non-negotiable. Full operational detail lives in `workflow/ksdrill-sa-ai-workflow.md`.

Using an AI engineer outside their defined role — or advancing the relay without Founder approval — is a governance violation.

---

### S10.1 — Engineer 01: Claude — Principal Architect (L1/L2)

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S10.1 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 3 — Product & Intelligence |
| **Depends On**  | `C0 §8` (amendment protocol), `S10.8` (Founder approval gate) |
| **Enforced By** | Relay protocol · Founder review |

**Standard:**
Claude is the first engineer on every task and the relay entry point. It operates at permission levels L1 (Propose) and L2 (Recommend with standard citation). Claude designs the full system — architecture, database schema, auth strategy, API contracts, frontend structure, and engineering governance — and produces a design document before any build work begins. Claude cannot approve its own proposals (L4 is Founder-only). All design outputs are subject to adversarial review (S10.3) before Founder approval is sought. Claude also serves as the Devil's Advocate in a separate, fresh session when stress-testing proposals.

**Rationale:**
Nothing moves to build until Claude has designed it and the Founder has approved. A designer who also approves skips the review that protects the entire relay. Claude's value is in architectural precision and constitutional recall — the approval step must remain human to preserve accountability.

**Anti-Patterns:**
- `AP-S10.1a` — "Claude said the architecture is correct, so we can start building" — Claude proposed; Claude cannot validate. Adversarial review and Founder approval are required before Claude Code begins.

**Cross-References:** `S10.3` (adversarial review), `S10.8` (L4 Founder-only), `workflow/ksdrill-sa-ai-workflow.md §2`

---

### S10.2 — Engineer 02: Claude Code — Senior Engineer (L3)

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S10.2 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 3 — Product & Intelligence |
| **Depends On**  | `S10.1` (design must be approved before Claude Code begins), `S10.21` (CONSTITUTION-INDEX.md) |
| **Enforced By** | Build session protocol · Founder approval before relay advances |

**Standard:**
Claude Code operates inside Cursor (Agent Mode) at permission level L3 (Implement). It builds the full system from Claude's Founder-approved design. It may not deviate from the architecture in `CONSTITUTION-INDEX.md` without flagging the deviation to the Founder. It follows the layer build order (S4.79), commits one layer at a time (S4.80), and writes tests alongside every implementation layer (S7.1). Claude Code owns: backend, database, auth, API, and repo-wide feature implementation.

**Rationale:**
The builder optimises for execution speed. The `CONSTITUTION-INDEX.md` constraint is what keeps that speed pointed at the right target — the approved, constitutional design. Without it, fast code generation produces fast constitutional violations.

**Anti-Patterns:**
- `AP-S10.2a` — Starting a Cursor build session without loading `CONSTITUTION-INDEX.md` — Claude Code generates code without constitutional context; stack-specific standards are silently violated.
- `AP-S10.2b` — Claude Code making architectural decisions that were not in Claude's approved design — L3 implements, it does not design. Architectural gaps are flagged to the Founder, not self-resolved.

**Cross-References:** `S10.21` (CONSTITUTION-INDEX.md), `S4.79` (layer build order), `S7.1` (tests alongside), `workflow/ksdrill-sa-ai-workflow.md §2`

---

### S10.3 — Engineer 03: ChatGPT — Debugger, UI Engineer & Adversarial Reviewer (L1/L2/L3)

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S10.3 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 3 — Product & Intelligence |
| **Depends On**  | `S10.2` (comes after Claude Code in relay for UI/debug work) |
| **Enforced By** | Relay protocol |

**Standard:**
ChatGPT serves two roles depending on where in the relay it is called. **In the relay (third position):** it handles UI styling (Tailwind utilities, Custom CSS brand work per S4.13/S4.14), debugging (stack traces, runtime errors, Docker issues, CI/CD failures), fast implementation assistance, and DevOps fixes. **As adversarial reviewer (design phase):** it operates in a separate fresh session with no prior design context and stress-tests Claude's architectural proposals — "What are the weakest assumptions? What constitutional standards does this potentially violate?" — before the Founder approves. In the adversarial role, ChatGPT challenges but does not override Claude's output.

**Rationale:**
Adversarial review from a fresh context is genuine — a second session of the same Claude conversation is anchored to its prior reasoning and cannot provide genuine challenge. ChatGPT in a fresh context provides real independent pressure on the proposal. In the relay, ChatGPT's UI and debug ownership means Claude Code never has to compromise implementation velocity on styling or debugging work.

**Anti-Patterns:**
- `AP-S10.3a` — Asking Claude to perform adversarial review of its own proposal in the same conversation — not a genuine second opinion; use ChatGPT in a fresh session.
- `AP-S10.3b` — Giving ChatGPT full architectural redesign authority during the debug phase — ChatGPT fixes and styles; it does not redesign. Architecture changes go back to Claude.

**Cross-References:** `S10.1` (Claude's design is what ChatGPT connects to), `S10.8` (L4 Founder-only — ChatGPT cannot approve), `workflow/ksdrill-sa-ai-workflow.md §2`

---

### S10.4 — Engineer 04: DeepSeek — Reasoning & Algorithm Engine (L1/L2)

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S10.4 |
| **Priority**    | Standard |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 3 — Product & Intelligence |
| **Depends On**  | `S10.8` (Founder reviews DeepSeek output before it enters codebase) |
| **Enforced By** | Relay protocol — called only when task requires targeted logic |

**Standard:**
DeepSeek operates at L1 (Propose) and L2 (Recommend) for targeted, well-scoped reasoning tasks: algorithms and data structures, math-heavy logic, financial calculation patterns, coding challenge solutions, and fast targeted prototyping. DeepSeek is called only when the specific task requires its specialisation — it is not on every task by default. Its output is reviewed by the Founder before any part of it enters the codebase. Financial calculation output from DeepSeek must use `Decimal` types, not `float` (`S5.28`, `S7.38`), regardless of what DeepSeek generates.

**Anti-Patterns:**
- `AP-S10.4a` — DeepSeek output entered into the codebase without Founder review — L1/L2 output is a proposal; it requires review before becoming implementation.

**Cross-References:** `S5.28` (Decimal for financial values), `S7.38` (Decimal in tests), `workflow/ksdrill-sa-ai-workflow.md §2`

---

### S10.5 — Engineer 05: Kimi — Experimental Lab Engineer (L1 only)

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S10.5 |
| **Priority**    | Standard |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 3 — Product & Intelligence |
| **Depends On**  | `S10.8` (all Kimi output is L1 — Founder reviews before any use) |
| **Enforced By** | Relay protocol — called only when explicit Founder intent |

**Standard:**
Kimi is the last engineer in the relay and operates exclusively at L1 (Propose). It handles large-context reasoning (loading an entire codebase for inconsistency detection), autonomous coding experiments (proof of concept, not production), multi-step code generation at scale, and AI swarm-style tasks. Kimi output is experimental and not production-safe by default. No Kimi output enters the codebase without explicit Founder review. Kimi is called only with explicit Founder intent — it is never the default choice for any task category already covered by Claude, Claude Code, ChatGPT, or DeepSeek.

**Anti-Patterns:**
- `AP-S10.5a` — Kimi output used as production implementation without Founder review — Kimi operates at L1 only; its output is a proposal, not a deliverable.

**Cross-References:** `S10.8` (L4 Founder-only), `workflow/ksdrill-sa-ai-workflow.md §2`

---

### S10.6 — Relay Standard: The Founder Is the Only Approval Gate

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S10.6 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 3 — Product & Intelligence |
| **Depends On**  | `S10.8` (L4 human-only) |
| **Enforced By** | Relay protocol |

**Standard:**
The relay baton is held by the Founder at every handoff point. No AI engineer advances the relay to the next engineer autonomously. No AI engineer self-routes. Every transition — Claude → Claude Code, Claude Code → ChatGPT, and every subsequent step — requires explicit Founder decision after reviewing the preceding engineer's handoff report (per `workflow/ksdrill-sa-ai-workflow.md §4.5 Part B`). The relay stops if the Founder does not approve. It does not continue.

**Anti-Patterns:**
- `AP-S10.6a` — An AI engineer declaring "Next: Claude Code should build X" and proceeding as if that instruction constitutes approval — the instruction identifies the next step; only the Founder can activate it.

**Cross-References:** `S10.8` (L4 Founder-only), `workflow/ksdrill-sa-ai-workflow.md §4`

---

### S10.7 — Session Entry Requirement: AI-INSTRUCTIONS.md First

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S10.7 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 3 — Product & Intelligence |
| **Depends On**  | — |
| **Enforced By** | Handoff Protocol Part A |

**Standard:**
Every AI session — regardless of which engineer is operating — begins with reading `AI-INSTRUCTIONS.md` and the system context file for the active project (`system-contexts/{system}-context.md`) before any technical work begins. An AI session that starts with a technical question before loading constitutional context operates without grounding. For Claude Code in Cursor, `CONSTITUTION-INDEX.md` is loaded in addition to the above (S10.21).

**Anti-Patterns:**
- `AP-S10.7a` — Claude Code session opened in Cursor with "build me a login endpoint" as the first input — no constitutional context loaded; the implementation is ungrounded.

**Cross-References:** `S10.21` (CONSTITUTION-INDEX.md for Claude Code), `workflow/ksdrill-sa-ai-workflow.md §4.5 Part A`

---

## Part 1b — Relay Handoff Protocol Standards

These standards govern the handoff mechanics. The full operational procedure lives in `workflow/ksdrill-sa-ai-workflow.md §4.5`. These standards are the constitutional backing for that procedure.

> **S10.6a** — Every engineer delivers a Handoff Report before closing their session. A session that ends without a handoff report is a protocol violation. The Founder cannot approve a handoff they have not received.

> **S10.6b** — Every incoming engineer performs Repo Verification before starting work. Verification must confirm that what the previous engineer claimed matches what actually exists in the repo. For Claude Code: verification includes confirming `CONSTITUTION-INDEX.md` is current for the active sprint (`S10.23`).

> **S10.6c** — Verification failure stops the relay immediately. The incoming engineer delivers a Verification Failure Report and awaits Founder decision. No self-routing. No self-repair. No proceeding.

> **S10.6d** — The full build history travels with every handoff. Every engineer in the relay knows what all previous engineers built, decided, and handed forward. Context collapse across engineers is a relay failure, not an acceptable trade-off for speed.

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
- `AP-S10.8b` — AI output accepted as a constitutional amendment — the standard already names constitutional amendments among the decisions L4 reserves to humans, and an amendment that entered the corpus on an engine's authority cannot be un-ratified by discovering that later.

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
>
> **Anti-Patterns:**
> - `AP-S10.9a` — L2 recommendation made without citing a standard ID — an uncited recommendation carries the authority of the constitution while resting on nothing that can be checked against it.

> **S10.10** — L3 implementation requires: the design is documented in `CONSTITUTION-INDEX.md`, the design was approved by a human (L4), and the implementation follows the layer build order (S4.79). A Cursor session that starts implementing without an approved design is L1 masquerading as L3.
>
> **Anti-Patterns:**
> - `AP-S10.10a` — L3 implementation started without approved documented design — the approval gate is skipped rather than refused, so the first review of the design happens against code already written to it.

> **S10.11** — Security decisions (auth strategy, token storage, role definitions, CORS configuration) are always L4 — human approval required regardless of how clear the AI's recommendation is.
>
> **Anti-Patterns:**
> - `AP-S10.11a` — Auth/security architecture decided without Founder L4 approval — the clarity of a recommendation is not evidence for it, and a security decision taken without an accountable human is unowned at exactly the point where ownership matters most.

> **S10.12** — Database schema changes are always L4 — schema changes require human review of the migration, the rollback plan, and the backward compatibility assessment (S5.59–S5.64).
>
> **Anti-Patterns:**
> - `AP-S10.12a` — A schema change taken at a lower authority level — the migration, the rollback plan and the backward-compatibility assessment are approved by whoever wrote them, and the one review that could have caught an irreversible change never happens.

> **S10.13** — AI recommendations that contradict a constitutional standard are flagged, not silently complied with. The AI states: "This recommendation conflicts with `S3.14` (access token in Angular memory). Following the recommendation would require a constitutional amendment per C0 §8."
>
> **Anti-Patterns:**
> - `AP-S10.13a` — AI silently complies with a constitutional violation instead of flagging it — compliance without objection is indistinguishable from the standard having been checked and found satisfied, which is the one failure a governance layer must never produce.

> **S10.14** — When AI detects a potential constitutional violation in existing code, it flags the violation and the violated standard — it does not silently work around the violation by generating compliant wrappers that obscure the underlying problem.
>
> **Anti-Patterns:**
> - `AP-S10.14a` — A detected violation worked around by a compliant wrapper — the wrapper passes review, the original defect is now harder to find than before it was noticed, and the standard reads as satisfied.

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
>
> **Anti-Patterns:**
> - `AP-S10.16a` — A design session left in chat — the challenge, the resolution and the reasoning are unrecoverable a week later, so the same design is re-argued from the beginning by whoever inherits it.

> **S10.17** — Constitutional gaps identified during design (a situation not covered by any existing standard) are documented as constitutional amendment proposals following C0 §8, not solved by improvisation.
>
> **Anti-Patterns:**
> - `AP-S10.17a` — A gap in the standards solved by improvisation — the improvisation becomes precedent without ever being reviewed, and the corpus grows a rule nobody voted for.

> **S10.18** — When AI proposes a design that requires a stack deviation, it must immediately flag the constitutional amendment required: "This proposal would require an amendment to `S4.1` (framework assignment) per C0 §8."
>
> **Anti-Patterns:**
> - `AP-S10.18a` — A proposal that needs a deviation presented without naming the amendment it requires — the deviation is approved as a design decision, and the standard it breaks is discovered only when a check fires against it.

> **S10.19** — AI-generated architecture diagrams, data flow descriptions, and system topology descriptions are treated as proposals (L1) — never as approved designs until a human confirms them.
>
> **Anti-Patterns:**
> - `AP-S10.19a` — A generated diagram treated as an approved design — the build proceeds against a topology no human confirmed, and the first review of it is the incident.

> **S10.20** — The design phase is not skipped for "small" features. A feature that touches authentication, database schema, or the API contract is not small — it requires the full design phase protocol.
>
> **Anti-Patterns:**
> - `AP-S10.20a` — The design phase skipped because a feature looked small — a change touching authentication, schema or the API contract goes straight to build, and the size judgement is what turns out to be wrong.

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
The constitutional system is stored in `governova`, not in the application repository. The `CONSTITUTION-INDEX.md` bridges the gap — it is the project's declared subset of relevant standards, current ADRs, and approved deviations. It makes the constitutional system actionable inside the editor.

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
>
> **Anti-Patterns:**
> - `AP-S10.23a` — A stale sprint index carried forward — it names last sprint's goal and last sprint's active feature, which is worse than no index because it is followed with confidence.

> **S10.24** — The builder AI (Cursor) explicitly acknowledges `CONSTITUTION-INDEX.md` at the start of the session. If Cursor does not acknowledge it, the file was not loaded correctly — reload and verify before proceeding.
>
> **Anti-Patterns:**
> - `AP-S10.24a` — A session started without confirming the index loaded — the assistant works from whatever it last held, and the mismatch is invisible until output arrives against the wrong sprint.

> **S10.25** — Code generated by the builder AI is reviewed by the human for constitutional compliance before committing. The layer build order (S4.79) ensures each commit is reviewable at the layer level.
>
> **Anti-Patterns:**
> - `AP-S10.25a` — Generated code committed without a compliance review — the layer build order exists precisely so each commit is reviewable, and skipping the review discards the only benefit that ordering buys.

> **S10.26** — Build sessions that run longer than 4 hours without a commit should reset context: commit what is working, reload `CONSTITUTION-INDEX.md`, and start a fresh session. Context window degradation over long sessions produces lower-quality, less constitutionally aligned output.
>
> **Anti-Patterns:**
> - `AP-S10.26a` — A build session run for hours with no commit — context degrades across the session, so the least aligned output is produced at the end and lands in the same uncommitted pile as the good work.

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
>
> **Anti-Patterns:**
> - `AP-S10.28a` — A solo-mode proposal self-approved with no adversarial review — the only check on a single author's reasoning is that author, and the proposal that most needed challenging is the one nobody challenged.

> **S10.29** — AI as standup accountability: at the start of every session, the dev log from the previous session is presented to Claude: "Review this dev log. What blockers were identified? What was the plan? Has the plan been followed?" This replaces the team standup accountability mechanism.
>
> **Anti-Patterns:**
> - `AP-S10.29a` — A session started without reviewing the previous dev log — the blockers recorded last time are rediscovered rather than resolved, and the plan drifts with nothing reporting the drift.

> **S10.30** — AI as SEV classifier in incident response: when a production issue is detected, Claude is given the symptom description and asked to classify the severity and suggest the runbook. Claude suggests — the human classifies and acts.
>
> **Anti-Patterns:**
> - `AP-S10.30a` — A severity assigned without a human confirming it — the classification determines the response, so a wrong one routes a live incident to the wrong runbook at the moment speed matters most.

> **S10.31** — AI as constitutional amendment evaluator: before the 24-hour personal review period (C0 §8.2), Claude reviews the proposed amendment for unintended consequences and cross-constitution conflicts. Claude's output is documented in the amendment GitHub Issue.
>
> **Anti-Patterns:**
> - `AP-S10.31a` — An amendment entering its review period without a conflict evaluation — cross-constitution contradictions are ratified into law, and the corpus now says two incompatible things with equal authority.

> **S10.32** — AI output in solo mode is documented, not ephemeral. Review sessions, proposal adversarial reviews, and amendment evaluations are documented in GitHub Issues or dev log entries. Undocumented AI interactions provide no audit trail and no knowledge transfer.
>
> **Anti-Patterns:**
> - `AP-S10.32a` — A review session left undocumented — the reasoning cannot be cited in a later dispute and cannot be handed to anyone, so the work produced value once and none of it compounds.

---

## Part 6 — Team AI Governance (`S10.33`–`S10.36`)

> **S10.33** — In team mode, AI recommendations require a human to evaluate and cite the standard basis before the recommendation is actioned. "Claude said to do this" is never sufficient justification in a team PR review.
>
> **Anti-Patterns:**
> - `AP-S10.33a` — A recommendation actioned without a human citing the standard behind it — the justification is the source rather than the reasoning, and the pull request records no basis anyone can check.

> **S10.34** — AI code review sessions (S10.27) are additive in team mode — they supplement human review, not replace it. The 2-approval rule (S1.30) remains a 2-human-approval rule. AI review is a third review, not a substitute.
>
> **Anti-Patterns:**
> - `AP-S10.34a` — A review session counted toward the two-approval rule — the number of approvals is unchanged on paper and reduced by one in fact, which is the precise failure the rule exists to prevent.

> **S10.35** — Team members using AI tools document which AI tools were used in significant design decisions in the PR description. This enables the team to evaluate whether the constitutional AI workflow was followed.
>
> **Anti-Patterns:**
> - `AP-S10.35a` — Tooling used in a significant design decision left out of the pull request description — the team cannot assess whether the workflow was followed, because the record does not say what was involved.

> **S10.36** — AI tools are not given access to production credentials, production database connections, or production Railway/Vercel dashboards. AI operates on code and design — not on live production systems.
>
> **Anti-Patterns:**
> - `AP-S10.36a` — Production credentials, database connections or deployment dashboards exposed to tooling — a system scoped to code and design acquires the ability to act on live infrastructure, and no control anywhere assumes it can.

---

## Part 7 — Relay Handoff Verification (`S10.37`)

> A phase is not "done" because the build is green — it is done when it has been checked against the adversary. This part adds a verification precondition to the S10.6 handoff: every phase is proven against the system's own adversarial findings before the baton is passed to the next engineer.

### S10.37 — Post-Phase Adversarial Verification Before Handoff

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S10.37 |
| **Priority**    | Critical |
| **Applies To**  | All Systems · Both Stacks · Solo Dev · Team |
| **Phase**       | Phase 3 — Product & Intelligence |
| **Depends On**  | `S10.6` (Founder approval gate / Handoff Protocol), `C7` (testing — verification is a testing act) |
| **Enforced By** | The engineer at handoff; checked by the Founder at the S10.6 gate |

**Standard:**
Before delivering the S10.6 phase handoff, the engineer verifies the completed phase against the system's own adversarial findings — its stress-test / red-team audit (the `ST-x` register) and its scenario-and-decision log (`D-NNN`) — and records in the handoff report the specific ids the phase satisfies, plus any deliberately deferred to a later phase with the reason. A handoff that does not document this verification is incomplete and is not accepted at the S10.6 gate. Where a system has no such audit yet, producing one is a deliverable of the first phase that introduces adversarial surface.

**Rationale:**
Green tests prove the build does what the builder expected; they do not prove it survives what an attacker or an edge case will do. The adversarial audit (ST) and the scenario rulings (D-NNN) are where a system records the failure modes it has reasoned about. Checking each phase against them at the handoff boundary — while the work is fresh, and before the next engineer builds on top — is the cheapest place to catch the regression of a known risk. This makes "verified against the adversary" a relay invariant, not a per-engineer habit.

**Anti-Patterns:**
- `AP-S10.37a` — Phase handoff delivered with no citation of the system's ST/D findings — the build may silently regress a risk the system already reasoned about, and "tests pass" is offered in place of adversarial verification.

**Cross-References:** `S10.6` (handoff is the only approval gate), `S10.27` (AI second-reviewer in solo mode), `C7` (Testing Constitution — verification mechanics), `S1.45` (author self-review checklist).

---

### S10.38 — Phase-Status Sync Across All Living Docs Before Handoff

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S10.38 |
| **Priority**    | Critical |
| **Applies To**  | All Systems · Both Stacks · Solo Dev · Team |
| **Phase**       | Phase 3 — Product & Intelligence |
| **Depends On**  | `S10.6` (handoff gate), `S10.37` (post-phase verification), `S10.23` (CONSTITUTION-INDEX currency) |
| **Enforced By** | The engineer at handoff; checked by the Founder at the S10.6 gate |

**Standard:**
The moment a phase gate passes, and before the S10.6 handoff, the engineer updates EVERY living doc so they all agree on what is done and what is next. The next engineer must never read a contradicting "next stage" — misinformation across living docs causes the next engineer to act on the wrong target. In the same handoff, update: the canonical phase-status record (the `CONSTITUTION-INDEX.md` / system-context status table — the source of truth), every navigation/index doc and its counts (a docs index, README, manifest), the next stage's session prompt or brief, and the new handoff itself. Sealed historical handoffs are point-in-time records and are never rewritten — a new handoff is added instead. A handoff that leaves any living doc pointing at the wrong stage is incomplete and is not accepted at the S10.6 gate.

**Rationale:**
A handoff is only as trustworthy as the least-current document the next engineer might open. When the status table says "Stage N done, Stage N+1 next" but a README, manifest, or session prompt still points at Stage N, the next engineer can pick up the wrong target and build on a false premise. Synchronising all living docs at the gate — while the work is fresh — keeps the documentation a single coherent truth and removes a whole class of relay error.

**Anti-Patterns:**
- `AP-S10.38a` — Handoff delivered with the status table updated but a README / manifest / session prompt still naming the previous stage as "next" — the next engineer can act on stale guidance; the living docs no longer agree.

**Cross-References:** `S10.6` (handoff gate), `S10.37` (post-phase verification — the paired pre-handoff check), `S10.23` (CONSTITUTION-INDEX currency), `S1.45` (author self-review).

---

## Part 8 — AI Feature Integration (`S10.39`)

> Parts 1–7 govern AI as the *engineer building* the system. This part governs AI as a *feature inside* the system — a model serving users. The standard below is the discipline for shipping a trustworthy AI feature, especially in systems that handle money or serve vulnerable people.

### S10.39 — Trustworthy AI Feature Integration

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S10.39 |
| **Priority**    | Critical |
| **Applies To**  | All Systems · Both Stacks · Solo Dev · Team |
| **Phase**       | Phase 3 — Product & Intelligence |
| **Depends On**  | `C5` (store isolation — money/PII placement), `C7` (testing/eval), `C9` (product gates), `S10.8` (human-only approval) |
| **Enforced By** | Design review · the CI eval gate · the S10.6 handoff |

**Standard:**
An AI feature (matching, ranking, generation, extraction, recommendation, an agent) integrates via **Ports & Adapters** — the model sits behind an abstract port so it can be swapped without touching business logic — and MUST satisfy all six:
1. **Advisory-only + human-final** — the AI never makes a consequential decision (funding, eligibility, moderation, money movement); a human makes it, and that authority is enforced in the deepest practical layer (e.g. a database trigger), not just the UI.
2. **Grounded** — the model may reference only real, retrieved entities; it may never invent one. Every cited entity is validated against the system of record before the output is shown or stored; a failed validation drops the AI output, never the underlying record.
3. **Cost-fused** — every paid call passes a spend circuit breaker (budget in config) and a per-actor quota (counted in a cache store, never a money value); breaker-open degrades to a fallback, never an error.
4. **Eval-gated** — no model or prompt ships without passing a curated golden-set evaluation (quality + a grounding/safety check), run in CI; a regression fails the build.
5. **Privacy-first** — local/on-host by default; minimise PII sent to any external model; exclude sensitive categories (counselling, health) from AI inputs entirely; external processing is consent-gated.
6. **Versioned + auditable** — every AI output carries its `model_version` and `prompt_version`; prompts are versioned like any other governed artifact.

**Rationale:**
For a system that funds vulnerable people or handles money, the measure of a good AI feature is not model size — it is trustworthiness. These six make the trust *structural*: it never decides, never hallucinates an entity, never leaks data, never runs away with cost, never regresses silently, and is always traceable. Ports & Adapters makes the model a controlled, swappable component rather than a load-bearing dependency, so the safety rails are proven before a real (paid, privacy-sensitive) model is introduced.

**Anti-Patterns:**
- `AP-S10.39a` — An AI feature that decides, or surfaces an entity it invented, or calls a paid model with no breaker/quota/eval gate — any one of these ships an untrustworthy AI.

**Cross-References:** `C5` (store isolation — money/PII placement), `C7` (eval mechanics), `C9` (product feature gates), `S10.8` (human-only approval).

---

### S10.40 — Mode-Based Merge Authority — AI Never Merges a Sensitive Change

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S10.40 |
| **Priority**    | Critical |
| **Applies To**  | All Stacks · solo and team |
| **Phase**       | Phase 3 — Product & Intelligence |
| **Depends On**  | `S10.8` (human-only approval / L4), permission model |
| **Enforced By** | `protocols/github-workflow.md` §6 · branch protection |

**Standard:**
Merge authority follows the operating mode. **Solo:** auto-merge (or founder manual merge) is permitted for speed once checks pass. **Team:** human review and human-only merge after the required approvals. In **both** modes, an AI engineer **never** holds L4 merge authority over a sensitive change — constitutional amendments, security/auth, and production releases are always merged deliberately by a human. The permanent human-only L4 boundary (S10.8) is preserved regardless of automation.

**Rationale:**
Solo developers need speed; teams need review — the framework serves both without changing the process, only the authority. The one invariant across modes is that automation never lets an AI approve its own sensitive output into production, which would breach the L4 boundary that makes the whole system trustworthy.

**Anti-Patterns:**
- `AP-S10.40a` — An AI tool (or an auto-merge configured to act as one) merging a constitutional, security, or production change without human approval.

**Cross-References:** `protocols/github-workflow.md` §6, `S10.8` (human-only L4), `S1.99` (workflow order), `framework/permission-model.md`.

---

## Anti-Patterns Index

| ID | Description | Violated Standard | Severity |
|----|-------------|-------------------|----------|
| `AP-S10.1a` | "Claude said it's correct, we can start building" — adversarial review + Founder approval skipped | S10.1 | Critical |
| `AP-S10.2a` | Claude Code session opened without CONSTITUTION-INDEX.md loaded in Cursor | S10.2 | Critical |
| `AP-S10.2b` | Claude Code making architectural decisions not in Claude's approved design | S10.2 | Critical |
| `AP-S10.3a` | Same Claude session used for both proposal and adversarial review | S10.3 | High |
| `AP-S10.3b` | ChatGPT given full architectural redesign authority during debug phase | S10.3 | High |
| `AP-S10.4a` | DeepSeek output entered into codebase without Founder review | S10.4 | High |
| `AP-S10.5a` | Kimi output used as production implementation without Founder review | S10.5 | High |
| `AP-S10.6a` | AI engineer declares next step and proceeds without Founder activation | S10.6 | Critical |
| `AP-S10.7a` | AI session opened with technical question before AI-INSTRUCTIONS.md loaded | S10.7 | High |
| `AP-S10.8a` | "Claude approved the security decision" — Claude cannot hold L4 | S10.8 | Critical |
| `AP-S10.9a` | L2 recommendation made without citing a standard ID | S10.9 | Standard |
| `AP-S10.10a` | L3 implementation started without approved documented design | S10.10 | Critical |
| `AP-S10.11a` | Auth/security architecture decided without Founder L4 approval | S10.11 | Critical |
| `AP-S10.13a` | AI silently complies with constitutional violation instead of flagging | S10.13 | Critical |
| `AP-S10.15a` | Claude → Claude Code directly, skipping adversarial review and Founder approval | S10.15 | Critical |
| `AP-S10.21a` | Build session started without CONSTITUTION-INDEX.md in Cursor context | S10.21 | Critical |
| `AP-S10.22a` | CONSTITUTION-INDEX.md lists all 300+ standards instead of curated active set | S10.22 | Standard |
| `AP-S10.27a` | PR merged to main without AI code review session documented | S10.27 | High |
| `AP-S10.37a` | Phase handoff delivered without citing the system's ST/D adversarial findings | S10.37 | Critical |
| `AP-S10.38a` | Handoff with the status table updated but a README/manifest/session-prompt still naming the previous stage as "next" | S10.38 | Critical |
| `AP-S10.39a` | An AI feature that decides, hallucinates an entity, or calls a paid model with no breaker/quota/eval gate | S10.39 | Critical |

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
| v1.0 | 2026-05-08 | Initial lock — new constitution with no predecessor. Five AI engineer relay model formalised (S10.1–S10.7): Claude (Principal Architect), Claude Code (Senior Engineer), ChatGPT (Debugger+UI+Adversarial Reviewer), DeepSeek (Reasoning Engine), Kimi (Experimental Lab). Founder approval gate at every relay handoff formalised as S10.6 (L4 human-only extension). Relay Handoff Protocol backing standards added (S10.6a–S10.6d). Three-phase design workflow formalised (S10.15). CONSTITUTION-INDEX.md standard formalised (S10.21–S10.22). Permission boundary framework L1–L4 formalised (S10.9–S10.14). Solo dev AI protocol formalised (S10.27–S10.32). Operational workflow detail extracted to `workflow/ksdrill-sa-ai-workflow.md`. | Five-engineer relay model formalised from KSDRILL-SA_AI_Engineer_Workflow.md. Full constitutional alignment including L1–L4 mapping per engineer, standard cross-references, and Founder approval gate. |
| v1.1 | 2026-06-15 | **Added Part 7 — Relay Handoff Verification (S10.37 — Post-Phase Adversarial Verification Before Handoff):** before the S10.6 handoff, the engineer verifies the phase against the system's stress-test audit (ST-x) and scenario-decision log (D-NNN), citing the ids satisfied/deferred in the handoff report; an unverified handoff is not accepted. Anti-pattern AP-S10.37a added. Count 36→37. (C0 §8 amendment A-2; evidence: FundsLink Stage-02 hardening caught 7 ST-2 gaps that green tests had passed; adversarial + cross-constitution review in the amendment issue; Founder L4 approval 2026-06-15.) | Green tests prove intent, not survival. Verifying each phase against the system's own adversarial findings at the handoff boundary makes it a relay invariant, not a per-engineer habit. |
| v1.2 | 2026-06-20 | **Added S10.38 (Phase-Status Sync) to Part 7** — on gate completion, before the handoff, every living doc is synced so none names a contradicting "next stage"; sealed handoffs are never rewritten. **Added Part 8 — AI Feature Integration (S10.39 — Trustworthy AI Feature Integration):** AI features integrate via Ports & Adapters and must be advisory-only + human-final, grounded, cost-fused, eval-gated, privacy-first, and versioned/auditable. Anti-patterns AP-S10.38a/AP-S10.39a added. Count 37→39. (C0 §8 amendments A-3 + A-6; FundsLink Stage 03/04 evidence generalised — phase-status drift across living docs, and the ADR-0007 trustworthy-AI pattern; Founder L4 approval 2026-06-20.) | Living docs must agree at every handoff, and an AI feature serving vulnerable people must be trustworthy by construction — never deciding, never hallucinating, never leaking, never running away with cost. |

| v1.3 | 2026-06-21 | **Added S10.40 — Mode-Based Merge Authority; AI never merges a sensitive change.** Solo auto-merge / team human-only; the permanent human-only L4 boundary holds in both modes. Anti-pattern AP-S10.40a added. Count 39→40. (C0 §8 amendment; operating-practice governance; Founder L4 approval 2026-06-21.) | The framework must serve solo speed and team review without ever letting automation merge an AI's own sensitive change into production — preserving the L4 boundary (S10.8). |

---

> **LOCKED — v1.3 — 2026-06-21** (amended; originally locked v1.0 2026-05-08)
>
> This document is locked. No standard may be added, removed, or modified
> without following the Amendment Protocol defined in C0 §8.
> Amendments take effect only after commit to `governova`
> with a version bump and amendment log entry.
>
> C10 is the final constitution. It governs the AI tools that help build everything else.
> The boundary it holds — AI proposes, AI implements, humans approve — is not a limitation.
> It is the design.
