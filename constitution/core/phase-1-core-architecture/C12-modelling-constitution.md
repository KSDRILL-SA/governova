# C12 — System Modelling Constitution

---

| Attribute          | Value                                                              |
|--------------------|--------------------------------------------------------------------|
| **Document**       | C12 — System Modelling                                             |
| **Organisation**   | KSDRILL SA                                                         |
| **Version**        | v1.0                                                               |
| **Status**         | LOCKED                                                             |
| **Locked**         | 2026-07-31                                                         |
| **Next Review**    | 2026-10-31                                                         |
| **Applies To**     | All Systems · Both Stacks · Solo Dev · Team                        |
| **Paired With**    | C11 — Requirements Engineering · C06 — Full-Stack Architecture     |

---

> *"A model that no longer matches the system is not documentation. It is a rumour."*

---

## Opening Statement

C11 governs what a system is required to do. C06 governs the architecture built to do it.
Between the two sits the work of deciding **what the system actually is** — its boundary,
its interactions, its structure, and how it behaves over time — and the corpus governed
none of it.

This constitution is not about drawing diagrams. Anybody can draw a diagram, and most
organisations have hundreds nobody trusts. It governs the three questions that decide
whether modelling is worth doing at all: **when a model is required, which views it must
carry, and whether it still tells the truth.**

The third is the one that matters. A model is believed in proportion to how authoritative
it looks and maintained in proportion to how easy it is to change, and those two forces
point in opposite directions. The result is the most common artifact in enterprise
software: a confident, detailed, beautifully rendered picture of a system that has not
existed for two years. It is worse than no model, because a reader with no model asks
someone.

**Four of nine standards are mechanically checked at merge — a lower ratio than any other
constitution in this phase, and deliberately so.** ADR-007 permits it here specifically,
on the condition that it is stated rather than quietly missed. Two things about that
number are worth being plain about:

- The plan for this stage anticipated *"mostly semantic and structural tier"*. **The
  semantic tier reaches nothing by default** (ADR-008), so the semantic half of that plan
  is unavailable and no standard here pretends otherwise.
- Modelling is a discipline where much of the value is genuinely in judgement. Which views
  a system needs is a decision about that system. Writing checkable-sounding standards
  about it would produce law that is enforced by nobody and believed by no one — the exact
  failure this phase's enforcement constraint exists to prevent.

**So this constitution ships nine standards rather than the twelve the plan allowed.** It
takes fewer standards over weaker checks, as ADR-007 requires.

---

## Table of Contents

| Part | Title | Standards |
|------|-------|-----------|
| §1 | A Model Is an Artifact, Not a Picture | S12.1–S12.3 |
| §2 | Which Views a System Carries | S12.4–S12.6 |
| §3 | A Model Tells the Truth or Is Removed | S12.7–S12.9 |
| §4 | Standards This Constitution Does Not Restate | — |
| §5 | Anti-Patterns Index | — |
| §6 | Amendment Log | — |

---

## §1 — A Model Is an Artifact, Not a Picture

---

### S12.1 — A System Boundary Is Modelled Before Its First External Interface

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S12.1 |
| **Priority**    | High |
| **Applies To**  | All Stacks · every system with an external dependency or consumer |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S11.1` (requirements reachable) · `S6.8` (architectural decisions recorded) |
| **Enforced By** | structural probe — a context model artifact exists in the repository |

**Standard:**
Before a system exposes or consumes its first external interface, it carries a model of
its boundary: what is inside the system, what is outside, and what crosses.

**Rationale:**
The boundary is the one architectural decision that cannot be deferred, because every
subsequent decision assumes an answer to it. Teams that never state it discover they held
different answers at integration time — the expensive moment, when both sides are built.
A boundary model is also the only artifact that makes "out of scope" a statement about the
system rather than an opinion about a ticket.

**Anti-Patterns:**
- `AP-S12.1a` — External interfaces built with no model of what is inside the system and what is outside it, so scope is negotiated per-ticket and integration reveals that no two people held the same boundary.

**Grounded In:**
- Sommerville, *Software Engineering* 10e — ch. 5, System Modeling (context models)

---

### S12.2 — Models Are Versioned With the Code They Describe

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S12.2 |
| **Priority**    | High |
| **Applies To**  | All Stacks · all systems |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S12.1` |
| **Enforced By** | structural probe — model artifacts present under version control |

**Standard:**
A model lives in the repository alongside what it describes, and changes through the same
review as the code. A model held only in a wiki, a shared drive, or a diagramming service
is not part of the system.

**Rationale:**
A model outside version control cannot be reviewed with the change that invalidates it,
cannot be reverted with a revert, and cannot be found by anybody who was not told where it
is. It also has no author and no date that survives, so a reader cannot judge its age —
which is the only fact they need most.

**Anti-Patterns:**
- `AP-S12.2a` — Models held outside version control, so they cannot be reviewed alongside the change that invalidates them and a reader cannot tell how old they are.

**Grounded In:**
- Sommerville, *Software Engineering* 10e — ch. 5, System Modeling

---

### S12.3 — A Model Is Expressed in a Form That Diffs

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S12.3 |
| **Priority**    | Standard |
| **Applies To**  | All Stacks · all systems |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S12.2` |
| **Enforced By** | structural probe — model artifacts are diffable text, not opaque binaries |

**Standard:**
Models are authored in a text format whose changes are legible in a diff. An exported
image may accompany a model; it is never the model.

**Rationale:**
A model that cannot be diffed cannot be reviewed, and a change nobody can review is a
change nobody does review. The practical consequence is that the model stops changing:
correcting it requires opening a separate tool, so the correction is deferred, and the
model drifts from the system in the one direction it never recovers from.

**Anti-Patterns:**
- `AP-S12.3a` — A model kept only as an opaque binary or exported image, so a change to it is invisible in review and correcting it requires leaving the repository.

**Grounded In:**
- Sommerville, *Software Engineering* 10e — ch. 5, System Modeling

---

## §2 — Which Views a System Carries

The canon distinguishes four perspectives. A system does not need all of them; it needs to
have **decided** which it needs.

---

### S12.4 — The Views a System Maintains Are Declared

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S12.4 |
| **Priority**    | Standard |
| **Applies To**  | All Stacks · all systems |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S12.1` · `S6.8` |
| **Enforced By** | review — which views a system needs is a judgement about that system |

**Standard:**
A system records which modelling views it maintains — **context**, **interaction**,
**structural**, **behavioural** — and why the others are not maintained.

**Rationale:**
Undeclared modelling produces two failures that look opposite and share a cause. Either
every view is attempted, most are abandoned half-finished, and readers cannot tell the
abandoned from the current; or no view is maintained and each engineer models privately,
in their head, differently. Naming the set converts modelling from an aspiration into a
commitment with a scope.

Review-only for a reason worth stating: which views a system needs depends on what the
system does. A check that demanded all four would be wrong for most systems, and one that
demanded any would be satisfied by the least useful.

**Anti-Patterns:**
- `AP-S12.4a` — Modelling attempted with no declared set of views, so abandoned diagrams sit indistinguishable from current ones and no reader can tell which to trust.

**Grounded In:**
- Sommerville, *Software Engineering* 10e — ch. 5, System Modeling

---

### S12.5 — Every Cross-Boundary Flow Has an Interaction Model

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S12.5 |
| **Priority**    | High |
| **Applies To**  | All Stacks · every flow crossing a system or trust boundary |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S12.1` · `S2.2` (layers communicate through defined contracts) |
| **Enforced By** | review — a *flow* spans systems this repository cannot enumerate |

**Standard:**
A flow that crosses a system boundary or a trust boundary carries a model of the
interaction: who initiates it, what passes, in what order, and what happens when a step
fails.

**Rationale:**
Cross-boundary failure modes are the ones nobody owns. Inside a system, a broken call is
somebody's bug; across a boundary, each side believes the other handles it, and the
resulting gap is discovered by a user. The ordering matters as much as the content —
most integration defects are not wrong data but right data at the wrong time.

Review-only because the other side of a boundary is, by definition, not in this
repository. A check confined to one repository would report a clean result for exactly the
flows that fail.

**Anti-Patterns:**
- `AP-S12.5a` — A cross-boundary flow with no modelled sequence or failure path, so each side assumes the other handles the failure and neither does.

**Grounded In:**
- Sommerville, *Software Engineering* 10e — ch. 5, System Modeling (interaction models)

---

### S12.6 — An Entity With a Lifecycle Has a Behavioural Model

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S12.6 |
| **Priority**    | Standard |
| **Applies To**  | All Stacks · every entity with more than two states |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S14.12` (history is keyed by time) |
| **Enforced By** | review — a lifecycle's *legality* is domain meaning, not a shape in the code |

**Standard:**
An entity that moves through states carries a model of those states and the transitions
permitted between them, including which transitions are forbidden.

**Rationale:**
State machines that exist only as scattered conditionals permit every transition nobody
explicitly prevented. The forbidden transitions are the point — a refunded order that
becomes shippable, a cancelled subscription that renews, an approved document that returns
to draft carrying its approval. Each is legal in code and illegal in the business, and the
gap is invisible until it happens.

Review-only because which transitions are illegal is domain meaning. Nothing in a
repository distinguishes a missing transition from a forbidden one.

**Anti-Patterns:**
- `AP-S12.6a` — An entity's lifecycle existing only as scattered conditionals, so every transition nobody explicitly prevented is permitted, including the ones the business forbids.

**Grounded In:**
- Sommerville, *Software Engineering* 10e — ch. 5, System Modeling (behavioural models)

---

## §3 — A Model Tells the Truth or Is Removed

---

### S12.7 — A Model Changes With the Contract It Describes

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S12.7 |
| **Priority**    | Critical |
| **Applies To**  | All Stacks · every system carrying both a model and a published contract |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S12.2` · `S13.5` (impact analysis on shared structure) |
| **Enforced By** | structural probe — model artifacts are not older than the contracts they describe |

**Standard:**
When a published contract changes — an API specification, a schema, an interface
definition — the models describing it change in the same review or are recorded as no
longer describing it.

**Rationale:**
Model drift is not a documentation problem; it is a **correctness** problem with a delay.
Every reader who trusts a stale model makes a decision on false information, and the more
authoritative the model looks the more expensive the decision. Because nothing fails when
a model goes stale, the drift is discovered only when somebody acts on it.

**Anti-Patterns:**
- `AP-S12.7a` — A published contract changed with its models left untouched, so every reader who trusts them makes decisions on a description of a system that no longer exists.

**Grounded In:**
- Sommerville, *Software Engineering* 10e — ch. 5, System Modeling

---

### S12.8 — A Model Names What It Realises

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S12.8 |
| **Priority**    | Standard |
| **Applies To**  | All Stacks · all systems |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S11.1` · `S12.4` |
| **Enforced By** | review — a model's *subject* is meaning, which no artifact declares mechanically |

**Standard:**
A model names the requirements or the architectural decision it realises. A model that
explains nothing in particular explains nothing.

**Rationale:**
This is where modelling earns its place: it is the bridge between what was asked for and
what was built, and a model attached to neither is decoration. The practical test is
deletion — nobody can decide whether a model may be deleted without knowing what it was
for, so unattached models are never deleted and accumulate until the set as a whole is
distrusted.

**Anti-Patterns:**
- `AP-S12.8a` — A model naming neither a requirement nor a decision, so nobody can judge whether it is still needed and it survives every review by default.

**Grounded In:**
- Sommerville, *Software Engineering* 10e — ch. 5, System Modeling

---

### S12.9 — A Model That No Longer Holds Is Corrected or Deleted

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S12.9 |
| **Priority**    | High |
| **Applies To**  | All Stacks · all systems |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S12.7` · `S13.3` (dead code is deleted) |
| **Enforced By** | review — whether a model still *holds* is a comparison only a reader can make |

**Standard:**
A model discovered not to match the system is corrected, or deleted with a note of what
replaced it. It is not left in place with a caveat.

**Rationale:**
A model marked "may be out of date" is read by everyone as authoritative anyway, because
the caveat is at the top and the detail is everywhere else. Retaining it costs what a wrong
model costs and buys what no model buys. Deleting it is the honest act: a reader with no
model asks someone, and gets a true answer.

**Anti-Patterns:**
- `AP-S12.9a` — A known-stale model retained behind a disclaimer, so it keeps the authority of documentation while carrying none of the accuracy.

**Grounded In:**
- Sommerville, *Software Engineering* 10e — ch. 5, System Modeling

---

## §4 — Standards This Constitution Does Not Restate

Recorded per `protocols/practice-to-standard.md §7`, and following the precedent C13 §5
set. Each was considered for C12 and **deliberately not written**, because the corpus
already holds it.

| Concept in the canon | Already held by |
|---|---|
| Contract written before implementation | `S2.11` (OpenAPI contract before any endpoint) |
| Layers communicate only through defined contracts | `S2.2` |
| Significant architectural decisions are recorded | `S6.8` (ADR required) |
| Stack topology is documented | `S6.12`, `S6.13` |
| Data models pass conceptual → logical → physical | `S14.13` |
| Requirements are the input to design | `S11.1`, `S11.3` |

A second standard saying the same thing is worse than one, and `S1.106` is itself the
standard against it.

---

## §5 — Anti-Patterns Index

| ID | Anti-Pattern | Violated Standard | Priority |
|----|-------------|-------------------|----------|
| AP-S12.1a | External interfaces built with no boundary model | S12.1 | High |
| AP-S12.2a | Models held outside version control | S12.2 | High |
| AP-S12.3a | A model kept only as an opaque binary or image | S12.3 | Standard |
| AP-S12.4a | Modelling attempted with no declared set of views | S12.4 | Standard |
| AP-S12.5a | A cross-boundary flow with no modelled sequence or failure path | S12.5 | High |
| AP-S12.6a | A lifecycle existing only as scattered conditionals | S12.6 | Standard |
| AP-S12.7a | A contract changed with its models left untouched | S12.7 | Critical |
| AP-S12.8a | A model naming neither a requirement nor a decision | S12.8 | Standard |
| AP-S12.9a | A known-stale model retained behind a disclaimer | S12.9 | High |

---

## §6 — Amendment Log

| Version | Date | Change | Reason |
|---------|------|--------|--------|
| v1.0 | 2026-07-31 | Initial lock — nine standards governing system modelling (ADR-007 Stage 3). §1 a model is an artifact not a picture (S12.1–S12.3), §2 which views a system carries (S12.4–S12.6), §3 a model tells the truth or is removed (S12.7–S12.9). **Four are mechanically checked at merge by structural probes**; five are review-only and each states why in its own rationale. §4 records six concepts deliberately not written because the corpus already holds them. **Nine standards rather than the twelve the plan allowed**: ADR-007 permits a lower mechanical ratio here specifically, and requires that a stage unable to meet the bar ships fewer standards rather than weaker checks. Core count 658→667. | C11 governs what a system must do and C06 governs the architecture built to do it; the corpus governed nothing about deciding what the system *is*. The plan for this stage anticipated the semantic tier, which reaches nothing by default (ADR-008), so the standards here are backed by structural probes or are honestly review-only. Modelling is also a discipline where much of the value is genuinely judgement — writing checkable-sounding standards about which views a system needs would produce law enforced by nobody. |

---

> **LOCKED — v1.0 — 2026-07-31**
>
> This document is locked. No standard may be added, removed, or modified without
> following the Amendment Protocol in C0 §8.
>
> **This constitution carries the lowest mechanical ratio in Phase 2, deliberately and on
> the record.** ADR-007 permits it here specifically, on condition that it is stated rather
> than quietly missed. Five standards are review-only because their subject is judgement or
> lives outside this repository, and each says so in its own rationale rather than claiming
> an enforcement path that does not exist.
