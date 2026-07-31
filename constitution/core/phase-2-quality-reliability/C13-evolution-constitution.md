# C13 — Software Evolution & Maintenance Constitution

---

| Attribute          | Value                                                              |
|--------------------|--------------------------------------------------------------------|
| **Document**       | C13 — Software Evolution & Maintenance                             |
| **Organisation**   | KSDRILL SA                                                         |
| **Version**        | v1.0                                                               |
| **Status**         | LOCKED                                                             |
| **Locked**         | 2026-07-31                                                         |
| **Next Review**    | 2026-10-31                                                         |
| **Applies To**     | All Systems · Both Stacks · Solo Dev · Team · every system past its first release |
| **Paired With**    | `protocols/brownfield-adoption.md`                                 |

---

> *"Maintenance is not what happens after the project. It is the project, for most of its life."*

---

## Opening Statement

Every constitution before this one governs a system being **built**. This one governs the
far longer period in which it is **changed** — which consumes the majority of a system's
lifetime cost, and which the rest of this corpus addressed only through a brownfield
adoption protocol for systems arriving from outside.

The canon's central observation is that evolution is not optional. A system in use is
changed because it is used: new demands arrive from the environment it succeeded in, and
a system that stops changing stops being used. From that follow the two properties this
constitution exists to govern — **complexity increases unless work is done to reduce it**,
and **perceived quality declines unless the system is adapted to a changing environment**.
Both are consequences of ordinary success, not of poor engineering, which is why neither
is prevented by any standard about how code is written.

**This constitution deliberately adds nothing that the corpus already holds.** Duplicate
code is `S1.106`. Speculative generality is `AP-S1.107a`. Cohesion and coupling are
`S1.103`. Incremental, non-breaking conversion is `S6.45`; characterisation tests before
refactoring are `S1.101`. Those standards were retro-cited to this same body of practice
in Stage 0, and **a second standard saying the same thing would be worse than one** —
`S1.106` is itself the standard against that. What follows is only what was genuinely
missing.

**Five of eleven standards are mechanically checked at merge.** The remainder are
review-only and each says why in its own text.

---

## Table of Contents

| Part | Title | Standards |
|------|-------|-----------|
| §1 | Debt Is Recorded, Not Felt | S13.1–S13.3 |
| §2 | Change Is Classified and Assessed | S13.4–S13.6 |
| §3 | Removal Is Announced | S13.7–S13.8 |
| §4 | Legacy Systems Carry a Decision | S13.9–S13.11 |
| §5 | Standards This Constitution Does Not Restate | — |
| §6 | Anti-Patterns Index | — |
| §7 | Amendment Log | — |

---

## §1 — Debt Is Recorded, Not Felt

Technical debt that exists only as a feeling cannot be prioritised, budgeted, or argued
for. It is paid anyway — in interest, by whoever is unlucky.

---

### S13.1 — A Deferred Decision Is Recorded Where Work Is Tracked

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S13.1 |
| **Priority**    | High |
| **Applies To**  | All Stacks · every system past its first release |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S1.85` (ADRs document significant decisions) |
| **Enforced By** | reliable-tier rule — `AP-S13.1a` (in-code marker with no tracked reference) |

**Standard:**
A decision deferred in code — a shortcut, a known limitation, a temporary workaround —
carries a reference to the tracked item that records it. A bare marker is not a record.

**Rationale:**
`TODO` without a reference is a note to a person who has left. It is invisible to
planning, absent from every estimate, and discovered by whoever next opens the file — who
has no way to learn whether it is a week old or five years old, whether it still applies,
or whether removing it breaks something. Debt that is only visible to people already
reading the line is debt nobody can decide about.

**Anti-Patterns:**
- `AP-S13.1a` — A `TODO`, `FIXME`, `HACK`, or `XXX` marker carrying no reference to a tracked item, so the deferred decision exists only where someone happens to read it.

**Grounded In:**
- Sommerville, *Software Engineering* 10e — ch. 9, Software Evolution (maintenance prediction)

---

### S13.2 — The System Maintains a Debt Register

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S13.2 |
| **Priority**    | Standard |
| **Applies To**  | All Stacks · every system past its first release |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S13.1` |
| **Enforced By** | structural probe — a debt register exists and is reachable |

**Standard:**
The system keeps one place where known debt is listed with its cost and its consequence —
a register in the repository, or a labelled set in the tracker the team already uses.

**Rationale:**
Per-item records answer *what* is owed and never *how much*. Without one aggregate view,
debt is negotiated one item at a time against features, which it loses every time, because
the cost of any single item is small and the cost of all of them is the thing nobody is
looking at.

**Anti-Patterns:**
- `AP-S13.2a` — Debt tracked only as scattered individual items with no aggregate view, so its total is never visible and it is negotiated away one item at a time.

**Grounded In:**
- Sommerville, *Software Engineering* 10e — ch. 9, Software Evolution (maintenance prediction)

---

### S13.3 — Dead Code Is Deleted, Not Commented Out

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S13.3 |
| **Priority**    | Standard |
| **Applies To**  | All Stacks · all systems under version control |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S1.106` (shared code is shared) |
| **Enforced By** | reliable-tier rule — `AP-S13.3a` (commented-out code) |

**Standard:**
Code that is no longer wanted is deleted. Version control is the record of what it was.

**Rationale:**
Commented-out code is read by everyone and understood by nobody. It cannot be compiled,
tested, linted, or refactored, so it silently rots while remaining prominent enough that
the next reader must decide whether it matters — a decision they have no information to
make. The history it is preserving is already preserved, with an author and a date and a
reason, in the thing whose entire purpose is preserving it.

**Anti-Patterns:**
- `AP-S13.3a` — Executable code retained as a comment instead of deleted, so it is neither maintained nor removed and every later reader must decide afresh whether it matters.

**Grounded In:**
- Sommerville, *Software Engineering* 10e — ch. 9, Software Evolution (code smells)

---

## §2 — Change Is Classified and Assessed

---

### S13.4 — Every Change Declares Its Maintenance Type

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S13.4 |
| **Priority**    | Standard |
| **Applies To**  | All Stacks · every system past its first release |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S1.19` (conventional commit format) |
| **Enforced By** | structural probe — maintenance profile derived from commit types |

**Standard:**
Every change is classifiable as **corrective** (repairing a defect), **adaptive**
(responding to a changed environment), **perfective** (adding or improving capability), or
**preventive** (reducing future cost). The classification is derived from the change's
declared type rather than recorded separately.

**Rationale:**
Without classification, the question *"where is our effort actually going"* has no answer,
and it is the question that decides whether a system is being invested in or bailed out. A
team spending most of its effort correctively is not choosing that; it is discovering it,
usually too late to change the trajectory.

Derived rather than recorded on purpose: a second field a human must fill in is a second
field that drifts, and `S1.19` already requires the first one.

**Anti-Patterns:**
- `AP-S13.4a` — Changes landing with no classifiable type, so the split between fixing, adapting, extending, and preventing is unmeasurable and the system's trajectory is invisible.

**Grounded In:**
- Sommerville, *Software Engineering* 10e — ch. 9, Software Evolution (maintenance types)

---

### S13.5 — A Change to Shared Structure Carries an Impact Analysis

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S13.5 |
| **Priority**    | High |
| **Applies To**  | All Stacks · every change to an interface, schema, or contract others depend on |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S14.13` (three design stages) · `S11.3` (requirements reach code) |
| **Enforced By** | review — impact is a claim about *consumers*, which a repository cannot enumerate |

**Standard:**
A change to a published interface, a shared schema, or a data contract records what
depends on it and what each dependant must do.

**Rationale:**
The cost of a change to shared structure is almost never in the change. It is in the
consumers, and they are discovered in production by whoever they belong to. An impact
analysis moves that discovery to before the merge, which is the only point at which the
change is still cheap.

This is **review-only and the reason is worth stating**: the dependants of a published
interface generally live in other repositories, other teams, or other organisations.
Nothing this engine can read enumerates them, and a check that inspected only this
repository would report a clean result for exactly the changes that hurt most.

**Anti-Patterns:**
- `AP-S13.5a` — A published interface or shared schema changed with no record of what depends on it, so consumers discover the break in production and the cost lands on whoever owns them.

**Grounded In:**
- Sommerville, *Software Engineering* 10e — ch. 9, Software Evolution (change impact analysis)

---

### S13.6 — Complexity Is Actively Reduced

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S13.6 |
| **Priority**    | Standard |
| **Applies To**  | All Stacks · every system past its first release |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S1.107` (the simplest correct solution) · `S13.2` |
| **Enforced By** | review — the canon's own claim is that this trend is only visible over time |

**Standard:**
Preventive work that reduces structural complexity is scheduled deliberately, not left to
occur as a side effect of feature work.

**Rationale:**
Complexity increases as a system evolves **unless work is done to reduce it**. This is a
property of change itself, not of careless engineering: each change is locally reasonable
and the accumulation is not. Because no single change is where the problem appears, no
review of a single change can catch it, and preventive work that is never scheduled is
never done — it loses to every feature, individually, forever.

Review-only because the trend is measurable only over a period longer than any one merge,
and a per-merge check would either fire on everything or on nothing.

**Anti-Patterns:**
- `AP-S13.6a` — Preventive work left entirely to opportunism, so structural complexity accumulates through changes that are each individually reasonable.

**Grounded In:**
- Sommerville, *Software Engineering* 10e — ch. 9, Software Evolution (Lehman's laws)

---

## §3 — Removal Is Announced

---

### S13.7 — Deprecation States When Removal Happens

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S13.7 |
| **Priority**    | High |
| **Applies To**  | All Stacks · every published interface |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S13.5` · `S8.87` (temporal governance of the external surface) |
| **Enforced By** | reliable-tier rule — `AP-S13.7a` (deprecation with no stated removal) |

**Standard:**
A deprecation marker states when the thing is removed — a version or a date. A deprecation
with no end is a label, not a plan.

**Rationale:**
An open-ended deprecation gives a consumer no reason to act, so none does. The marker
accumulates, the old path is maintained indefinitely alongside the new one, and the cost
of the migration is paid forever rather than once. Removing it later without a stated date
then breaks consumers who were, reasonably, waiting to be told.

**Anti-Patterns:**
- `AP-S13.7a` — A deprecation marker with no version or date for removal, so no consumer has a reason to migrate and both paths are maintained indefinitely.

**Grounded In:**
- Sommerville, *Software Engineering* 10e — ch. 9, Software Evolution (software maintenance)

---

### S13.8 — A Removal Is Preceded by a Deprecation Period

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S13.8 |
| **Priority**    | High |
| **Applies To**  | All Stacks · every published interface |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S13.7` |
| **Enforced By** | review — a *removal* is the absence of code, which no line-scan can observe |

**Standard:**
A published interface is deprecated, and the stated period elapses, before it is removed.
Removal without that sequence is a breaking change and is governed as one.

**Rationale:**
Consumers cannot migrate from something they were never told was going away. The
deprecation period is not politeness — it is the only mechanism by which the cost of a
removal is distributed over time rather than delivered to every consumer simultaneously
on the day it ships.

Review-only for a structural reason: a removal is an *absence*, and the reliable tier
scans lines that exist. Detecting it needs a diff of the published surface against its
previous release, which is a release-time comparison rather than a merge-time one.

**Anti-Patterns:**
- `AP-S13.8a` — A published interface removed without a prior deprecation period, delivering the migration cost to every consumer at once on the day it ships.

**Grounded In:**
- Sommerville, *Software Engineering* 10e — ch. 9, Software Evolution (software maintenance)

---

## §4 — Legacy Systems Carry a Decision

---

### S13.9 — Every Legacy System Has a Recorded Disposition

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S13.9 |
| **Priority**    | High |
| **Applies To**  | All Stacks · every system inherited or maintained past its design life |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S1.85` · `protocols/brownfield-adoption.md` |
| **Enforced By** | review — the disposition is a business judgement, recorded as an ADR |

**Standard:**
A legacy system carries a recorded decision to **maintain**, **reengineer**, **replace**,
or **retire** it, with the business value and system quality that decision rests on. The
decision is revisited on a stated schedule.

**Rationale:**
The default for a legacy system is *continue as before*, and it is a default nobody
chooses — it is what happens when no one decides. That is how systems of low business
value and low quality are maintained for a decade at full cost, and how systems of high
business value are replaced because nobody wrote down that they were working.

**Anti-Patterns:**
- `AP-S13.9a` — A legacy system maintained by default with no recorded disposition, so continuation is never a decision anyone made and never comes up for review.

**Grounded In:**
- Sommerville, *Software Engineering* 10e — ch. 9, Software Evolution (legacy system management)

---

### S13.10 — Reengineering Preserves Behaviour Before Improving It

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S13.10 |
| **Priority**    | Critical |
| **Applies To**  | All Stacks · every reengineering effort |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S1.101` (characterisation tests) · `S6.45` (incremental, non-breaking conversion) |
| **Enforced By** | review — the paired standards above carry the mechanical part |

**Standard:**
Reengineering changes how a system is built without changing what it does. Behaviour is
pinned before structure is altered, and any intended change in behaviour is a separate,
separately reviewed change.

**Rationale:**
Reengineering and feature work performed together are indistinguishable in review and in
bisection. When something breaks — and it does — nobody can tell whether the structural
change or the behavioural one caused it, so the safe response is reverting both, which
discards the reengineering that was probably fine.

This standard exists to *name the separation*; the mechanical enforcement lives in the
standards it depends on, and duplicating them here would violate `S1.106`.

**Anti-Patterns:**
- `AP-S13.10a` — Structural change and behavioural change delivered in one indivisible unit, so a regression cannot be attributed and the only safe response discards both.

**Grounded In:**
- Sommerville, *Software Engineering* 10e — ch. 9, Software Evolution (reengineering)

---

### S13.11 — Perceived Quality Is Measured, Not Assumed

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S13.11 |
| **Priority**    | Standard |
| **Applies To**  | All Stacks · every system past its first release |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S13.4` · `S8.87` |
| **Enforced By** | review — a *trend* needs a history of measurements this engine does not retain |

**Standard:**
A system tracks at least one measure of how well it is serving its users over time, and
reviews it on a stated schedule.

**Rationale:**
Perceived quality declines unless a system is adapted to its changing environment — and
the decline is invisible from inside, because nothing about the system changed. The
environment did. A team without a measure over time concludes the system is fine, because
every individual signal it has says so, right up until users leave.

Review-only because a trend requires retained measurements across releases, and this
engine deliberately holds no state between runs.

**Anti-Patterns:**
- `AP-S13.11a` — A system with no measure of user-perceived quality over time, so environmental decline is invisible until it is expressed as attrition.

**Grounded In:**
- Sommerville, *Software Engineering* 10e — ch. 9, Software Evolution (Lehman's laws)

---

## §5 — Standards This Constitution Does Not Restate

The canon this constitution derives from overlaps the corpus substantially. Each item
below was considered for C13 and **deliberately not written**, because the corpus already
holds it and two standards saying the same thing is worse than one — `S1.106` being itself
the standard against that.

| Concept in the canon | Already held by | Cited since |
|---|---|---|
| Duplicated code | `S1.106` | Stage 0 retro-citation |
| Speculative generality | `AP-S1.107a` | Stage 0 retro-citation |
| Cohesion and coupling | `S1.103` | Stage 0 retro-citation |
| Characterisation tests before refactoring | `S1.101` | `protocols/brownfield-adoption.md` |
| Incremental, non-breaking conversion | `S6.45` | `protocols/brownfield-adoption.md` |
| Per-step reversibility | `S8.83` | `protocols/brownfield-adoption.md` |
| Decay of the external surface | `S8.87` | `protocols/external-governance.md` |

Recording the rejections is required by `protocols/practice-to-standard.md §7`. Without
it, the same discarded idea returns every time somebody re-reads the source.

---

## §6 — Anti-Patterns Index

| ID | Anti-Pattern | Violated Standard | Priority |
|----|-------------|-------------------|----------|
| AP-S13.1a | A debt marker with no reference to a tracked item | S13.1 | High |
| AP-S13.2a | Debt tracked only as scattered items with no aggregate view | S13.2 | Standard |
| AP-S13.3a | Executable code retained as a comment instead of deleted | S13.3 | Standard |
| AP-S13.4a | Changes landing with no classifiable maintenance type | S13.4 | Standard |
| AP-S13.5a | Shared structure changed with no record of what depends on it | S13.5 | High |
| AP-S13.6a | Preventive work left entirely to opportunism | S13.6 | Standard |
| AP-S13.7a | A deprecation marker with no stated removal | S13.7 | High |
| AP-S13.8a | A published interface removed with no prior deprecation period | S13.8 | High |
| AP-S13.9a | A legacy system maintained by default with no recorded disposition | S13.9 | High |
| AP-S13.10a | Structural and behavioural change delivered in one indivisible unit | S13.10 | Critical |
| AP-S13.11a | No measure of user-perceived quality over time | S13.11 | Standard |

---

## §7 — Amendment Log

| Version | Date | Change | Reason |
|---------|------|--------|--------|
| v1.0 | 2026-07-31 | Initial lock — eleven standards governing the period in which a system is *changed* rather than built (ADR-007 Stage 4). §1 debt recorded not felt (S13.1–S13.3), §2 change classified and assessed (S13.4–S13.6), §3 removal announced (S13.7–S13.8), §4 legacy disposition (S13.9–S13.11). **Five are mechanically checked at merge**; the other six are review-only and each states why in its own rationale. §5 records the seven concepts from the same body of practice that were **deliberately not written**, because the corpus already holds them. Core count 647→658. | Every constitution before this governed a system being built. Maintenance consumes the majority of a system's lifetime cost and was addressed only by a brownfield protocol. Complexity increases and perceived quality declines as consequences of ordinary success rather than poor engineering — which is why no standard about how code is written prevents either, and why they needed a constitution of their own. |

---

> **LOCKED — v1.0 — 2026-07-31**
>
> This document is locked. No standard may be added, removed, or modified without
> following the Amendment Protocol in C0 §8.
>
> **§5 is part of this document's contract.** The concepts listed there are held elsewhere
> in the corpus and must not be restated here. A future amendment that adds one of them to
> C13 is a violation of `S1.106` by the constitution that contains it.
