# Project Governance Protocol

| Attribute | Value |
|-----------|-------|
| **Document** | Project Governance — planning, estimation, scheduling, and risk as practice |
| **Layer** | Protocol (operationalises the constitution) |
| **Governed By** | C9 — Product & Feature (`S9.31`–`S9.33`) · C0 §8 (amendment protocol) |
| **Applies To** | Every Governova-governed project · any stack · solo or team |
| **Status** | Active |
| **Paired With** | `governance/decisions/ADR-007-lifecycle-completeness.md` · `protocols/build-lifecycle.md` |

---

> *"An estimate nobody checked against reality is not an estimate. It is a wish with a number on it."*

---

## Why this is a protocol and not a constitution

ADR-007 considered making project management the fifth constitution of Phase 2 and
**refused**. The reasoning is worth keeping visible, because the temptation returns
whenever someone reads a project-management chapter:

Planning, estimation, and scheduling are overwhelmingly **context-dependent judgement**.
The right sprint length for a two-person team is wrong for a forty-person programme. The
right estimation technique for well-understood work is wrong for research. A constitution
of forty standards about scheduling would be enforced by nobody, evidenced by nothing, and
would inflate the denominator of every coverage metric in this system while lowering the
score — which is exactly the failure ADR-007's enforcement constraint exists to prevent.

**Three things in this discipline are genuinely checkable**, and only those became
standards (`S9.31`–`S9.33`): a risk carries an owner and a mitigation, an estimate is
recorded against its actual, and a completed project records what it delivered against
what it planned.

Everything else in this document is **practice** — recorded so it can be followed, taught,
and improved, and deliberately not made law.

---

## §1 — Planning

### 1.1 What a plan is for

A plan is not a prediction. It is a **shared model of intent** that makes disagreement
visible early, while it is still cheap. Its value is almost entirely in the conversations
it forces, and almost none of it is in the dates.

The practical test of a plan is not whether it came true. It is whether, when it stopped
being true, **anybody noticed**.

### 1.2 The minimum plan

Any project, at any size, records four things before work begins:

| Element | Question it answers |
|---|---|
| **Scope** | What is in, and — more usefully — what is explicitly out |
| **Sequence** | What must happen before what, and why |
| **Assumptions** | What must be true for this plan to hold |
| **Risks** | What could make it false (see §3) |

Assumptions are the element most often skipped and the one that pays back most. A plan
whose assumptions are unwritten cannot be invalidated — it can only be *missed*, which
looks like a failure of execution rather than a change in the world.

### 1.3 Dependency-first sequencing

Governova's own build order is dependency-first: `protocols/build-lifecycle.md` and the
Golden Rule in `C0 §1` — *build constitutions in the order your system would fail without
them*. The same logic governs project sequencing. Work that unblocks other work goes first,
even when work that demonstrates progress is more attractive to show.

---

## §2 — Estimation

### 2.1 Estimate in ranges, commit in decisions

A single-point estimate communicates a confidence nobody has. A range communicates the
uncertainty, which is the actual information. The commitment a business needs is not "it
will take eleven days" but "we will decide at day eight whether to continue".

### 2.2 Calibration is the whole point

**Estimation accuracy is not a talent. It is a feedback loop**, and it is the only part of
project management that is both mechanisable and valuable — which is why `S9.32` is a
standard and the rest of this section is not.

A team that records estimates and never compares them to actuals is not estimating; it is
guessing repeatedly and learning nothing. The comparison costs minutes and is the only
input that improves the next estimate.

What to record, per unit of work:

```
id            the tracked item
estimate      the range, and its unit
actual        what it took, in the same unit
recorded_at   when the actual was known
```

That is enough to compute drift over time, which is the number worth looking at. Individual
misses are noise. **A consistent direction is a signal**, and it is usually a signal about
scope discovery rather than about speed.

### 2.3 What not to do with estimates

- **Do not use them as commitments** without saying so. An estimate promoted to a deadline
  without a conversation is how estimates stop being honest, permanently: once a number can
  be held against someone, the number optimises for safety rather than accuracy.
- **Do not compare people by them.** The moment estimates are performance data, calibration
  data stops existing.
- **Do not re-estimate to match the remaining time.** That is not planning; it is recording
  a decision that has already been made, in a field that claims to be a forecast.

---

## §3 — Risk

### 3.1 A risk without an owner is an observation

`S9.31` requires each identified risk to carry a named owner and a stated mitigation, and
that is the entire mechanism. A risk register listing dangers with nobody attached is a
document that makes a team feel prepared while changing nothing about what happens.

**The owner is a person, not a team.** "The platform team" owns nothing; a queue owns
nothing. If it cannot be named, the risk is unowned and should be recorded as such —
honestly — rather than assigned to a group as a formality.

### 3.2 What a risk entry carries

| Field | Purpose |
|---|---|
| **Description** | What could happen, stated as an event rather than a worry |
| **Consequence** | What it costs if it happens |
| **Likelihood** | Rough, and honestly rough — a number here implies precision nobody has |
| **Owner** | The named person accountable for watching it |
| **Mitigation** | What is being done now to reduce it |
| **Trigger** | The observable signal that it is happening |

The **trigger** is the field most often omitted and the one that decides whether the
register is useful. A risk with no trigger is watched by nobody, because nobody knows what
watching would consist of.

### 3.3 Review cadence

A risk register that is written once is a historical document. It is reviewed on a stated
schedule, and entries are **closed explicitly** — either the risk occurred and was handled,
or it stopped being plausible. Silent removal destroys the record of what a team was
worried about and why they stopped, which is the part that is useful later.

---

## §4 — Scheduling

### 4.1 Critical path, without the ceremony

Formal critical-path and PERT analysis are worth knowing and rarely worth doing at the
scale most teams operate. What is always worth doing is the one question they exist to
answer: **which piece of work, if it slips, moves the end date?**

That question can be answered on a whiteboard in ten minutes. Answering it changes what a
team works on first, which is the entire value of the technique.

### 4.2 Slack is a design decision

A schedule with no slack is a schedule that assumes nothing goes wrong, which is an
assumption every project has falsified. Slack is not laziness in the plan; it is where the
plan absorbs the risks in §3 without renegotiating everything downstream.

### 4.3 Scope, schedule, quality

When a project is late, exactly three things can move: **scope**, **schedule**, or
**quality**. The first two are decisions somebody makes. **The third is what happens when
nobody makes one** — and it is invisible for months, then permanent.

Governova exists in large part to make the third one visible: a corpus of standards, and
gates that fail, are the mechanism by which "we quietly lowered quality" becomes a decision
someone has to take deliberately rather than a thing that simply occurs.

---

## §5 — Closure

`S9.33` requires a completed project to record what it delivered against what it planned.
The record is short and answers four questions:

1. **What was delivered**, against what was planned.
2. **What changed**, and when it was decided — scope added, scope dropped, dates moved.
3. **Which assumptions held**, and which did not (§1.2).
4. **What the estimation drift was** (§2.2), and what it suggests about the next estimate.

This is not a retrospective, which is about how the team worked. It is about how the
**plan** performed, and it is the only input that makes the next plan better. A team that
never closes projects formally begins each one from the same starting knowledge as the
last.

---

## §6 — What this protocol deliberately does not do

Recorded per `protocols/practice-to-standard.md §7`, following the precedent of `C13 §5`
and `C12 §4`.

| Not standardised | Why |
|---|---|
| Sprint length, cadence, ceremony set | Context-dependent; correct answer differs by team size and work type |
| Estimation technique (points, hours, t-shirts) | The technique is irrelevant; the calibration loop (`S9.32`) is what matters |
| Team structure and role definitions | Organisational, not engineering; already partly held by `protocols/modes/` |
| Formal PERT / critical-path analysis | Worth knowing, rarely worth doing at the scale most teams operate |
| Velocity as a governed metric | Becomes a target the moment it is governed, and stops measuring anything |
| Deadline setting | A business decision. Governova governs what happens to *quality* when it is missed, not what the date should be |

**Six items, each of which would have been an enforceable-sounding standard and an
unenforceable real one.** ADR-007's constraint is that a stage unable to meet the
enforcement bar ships fewer standards, not weaker checks. This protocol is that constraint
applied to an entire discipline.

---

*A plan's job is to be wrong in a way somebody notices. Everything here is in service of
noticing.*
