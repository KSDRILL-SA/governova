# Build Lifecycle — Protocol

| Attribute | Value |
|-----------|-------|
| **Type** | Operational protocol |
| **Status** | Active |
| **Governed By** | C00 §6 (phases), C01 (engineering), C10 (AI collaboration) |
| **Composes** | `framework/phase-model.md` · `protocols/relay-protocol.md` · `protocols/frameworks/ai-review-challenge-framework.md` · GOVERNOVA-MASTER §12.2 |
| **Applies To** | Any system · any stack · any sector |

---

> *Two principles govern this protocol:*
> 1. **"Make it exist first, then make it beautiful later."** Lay the foundation, get it
>    working and correct, then harden on top of it. Beauty without a foundation is rework.
> 2. **"Build smart, not hard."** Governova does not merely solve a problem — it enforces the
>    *single simplest, lightest, best-recommended* solution. If there is an easier correct way,
>    that is the way. Complexity that is not required is a violation.

---

## §1 — The build is ordered and dependency-first

Nothing is built all at once. A system is built in dependency order, and the **core that
everything depends on is built first** — so every later layer builds on stable ground and the
workflow is faster, not slower. Teams may build in parallel *only* behind the core.

| Order | Stage | Why it comes first |
|-------|-------|--------------------|
| 0 | **Foundation** — stack decision, project structure, environment setup | No code is correct before the stack and structure are decided (ADR-recorded). |
| 1 | **Database** | Schema and data model are the contract every other layer reads and writes. |
| 2 | **Auth** | Identity and access boundaries gate every endpoint and view. |
| 3 | **Backend / services** | Business logic lives here — built against the DB + auth contracts. |
| 4 | **Frontend** | Consumes the backend contract; never the reverse. |
| 5 | **Everything after** | Integrations, reporting, AI features — built on a stable core. |

This maps onto the four constitutional phases (`framework/phase-model.md`): Foundation (Phase 0),
Core Architecture incl. DB/auth/backend/frontend (Phase 1), Quality & Reliability (Phase 2),
Product & Intelligence (Phase 3). **A later stage never begins until the stage it depends on has
completed its full lifecycle loop (§2).**

## §2 — The per-stage lifecycle loop

Every stage runs the same five-step loop. A stage is not "done" when it is built — it is done
when it has passed the loop.

```
   ┌─────────┐   ┌──────────┐   ┌───────────────┐   ┌──────────────────┐   ┌─────────┐
   │  BUILD  │ → │  HARDEN  │ → │  SELF-REVIEW  │ → │  EXTERNAL-REVIEW  │ → │ HANDOFF │
   └─────────┘   └──────────┘   └───────────────┘   └──────────────────┘   └─────────┘
   make it       catch gaps,    builder checks      a different engineer    next stage
   exist         edge cases     their own work      catches blind spots     briefed
```

1. **Build.** Implement the stage to the active standards, at the smallest correct scope
   ("build smart, not hard"). Make it exist and be correct.
2. **Harden.** Review what was built for gaps, edge cases, and failure modes; make behaviour
   *predictable, controlled, and reduced in surface*. Every known limitation is documented; every
   known failure mode gets a Fix Guide entry (GOVERNOVA-MASTER §13). This is the "make it
   beautiful" pass — and it happens *after* the foundation exists, never before.
3. **Self-review.** The engineer who built the stage reviews and fixes it against the standards.
   Necessary but insufficient — a builder reviews in the light of what they intended.
4. **External-review.** A *different* engineer (AI or human) who did **not** build the stage
   reviews it. This step exists precisely to catch what the builder cannot see — the builder
   judges by why they built it that way; the external reviewer judges by the standards alone.
   This is the `ai-review-challenge-framework` applied as a mandatory gate, not an option.
5. **Handoff.** A handoff brief is produced for the next stage's engineer (§3).

SEV0/SEV1 findings at any step pause the relay (GOVERNOVA-MASTER §12.2); SEV2/SEV3 are logged and
the loop continues.

## §3 — Handoffs are generated, then refined

Before a stage begins, **Governova generates the engineer's handoff** — because it knows every
rule from Phase 00 to now, it cannot mislead. A handoff states:

- **What** to build, and **what not to touch**.
- **Why** (the standards and decisions that authorise and constrain it).
- **Where** it lives (modules, boundaries) and **from what** it builds (the contracts it depends on).
- The **active permission level** and the relay position (`protocols/relay-protocol.md` §4.5).

The receiving engineer may edit the handoff if something is missing or wrong; Governova then
updates and refines it so it stays consistent with the constitution. The handoff is the single
source of guidance for the stage — no engineer builds without one.

## §4 — Why this is faster, not slower

Dependency-first order means no layer is ever built against a moving contract. The hardening and
dual-review gates catch defects in the stage where they are cheapest to fix, before later stages
build on them. The handoff removes the most expensive cost in AI-assisted development — an
engineer operating without grounding. *Exist first, harden second, hand off clean.*
