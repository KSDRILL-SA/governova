# Phase 2 — Lifecycle Completeness

| Attribute | Value |
|-----------|-------|
| **Decision** | `governance/decisions/ADR-007-lifecycle-completeness.md` |
| **Status** | Planned — ready to implement |
| **Sequenced** | After Phase 1 (ADR-005 workstreams A + B, complete), before brownfield |
| **Source material** | Sommerville *Software Engineering* 10e (SU1–SU9) · Coronel & Rob *Database Systems* (Ch01–Ch09) — **not committed to this repository** |

> Read ADR-007 first. It carries the reasoning; this document carries the work.
> Every stage below is independently shippable through branch → issue → PR → merge.

---

## The bar this phase is held to

Three numbers decide whether this phase succeeded. They are not aspirations.

| Metric | Now | Required after |
|---|---|---|
| Constitutional coverage | 7.9% (43/544) | **≥ 9%** — it must *rise* despite the denominator growing |
| New standards mechanically enforced at merge | — | **≥ 40%** |
| Governova Score | 78 (C) | **≥ 78** — no regression |

If a stage cannot meet the 40% bar, **it ships fewer standards, not weaker checks.**
Writing law nobody can verify is how a governance corpus rots, and this project has
already paid for that lesson twice — `S1.104` declaring reliable-tier rules that did
not exist, and `S8.84` demanding a CVE gate the repository did not run.

---

## Stage 0 — Method and provenance

**Ships:** the `Grounded In` field, the extraction tooling, the conversion protocol.
**Nothing else can start until this is merged** — every later stage writes standards
that use it.

### 0.1 · `Grounded In` provenance

Add an optional `grounded_in: list[str]` to the `Standard` model, parsed from a
`**Grounded In:**` block, rendered by `governova standard`, and carried into the
compiled index.

A **citation, never an excerpt** — `Sommerville, Software Engineering 10e, ch.4` is
a citation; a paragraph of Sommerville is a copyright violation. A validator check
rejects any `Grounded In` value longer than a short reference line.

Then **retro-cite what already exists**: `S1.103`–`S1.107`, `S1.106`, `S7.25`, and
the design standards in C06. The claim this phase makes is not *"we wrote good
rules"* but *"we converged on established practice — here is where it is written
down."* That claim is only credible if the existing corpus carries it too.

### 0.2 · Extraction tooling

`scripts/governova_ingest/` — deterministic text extraction from PDF and legacy
`.doc`, so the conversion is reproducible rather than a one-time manual act. A
working extractor exists in the session scratchpad and should be brought in and
tested, not rewritten from scratch.

**The source documents are not committed.** The tool takes a path; the corpus lives
outside the repository. `.gitignore` must exclude the source folder explicitly so it
cannot be added by accident.

### 0.3 · The conversion protocol

`protocols/practice-to-standard.md` — how a body of practice becomes constitutional
law. This is the worked method the Mapping Engine (`master.md §14`) must later
reproduce, and writing it now is what makes that engine buildable from evidence
rather than from imagination.

At minimum it records: how a teaching concept is narrowed to a testable requirement;
how the enforcement path is chosen; how anti-patterns are derived from the failure
the concept prevents; how provenance is cited; and what is rejected and why.

**Exit criteria:** `Grounded In` compiles, validates, and renders · at least 10
existing standards retro-cited · extraction reproducible from a clean checkout ·
protocol merged.

---

## Stage 1 — C11 Requirements Engineering · *the headline*

**Ships:** the constitution, the requirements format, and the linter.
**Why first:** highest novelty, cheapest to build (text rules — no parsers), stack-
independent, and it addresses the most expensive defect class in software.

### 1.1 · The format specification

The linter is worthless if requirements are not machine-readable. C11 must specify
**where requirements live and how they are written** — this is the strongest claim
Governova will make on an adopting team, and it needs to be light enough to accept:

```
requirements/
  REQ-001-authentication.md
```

Each requirement, from the canon's grammar:

```
<Req ID> The <system> <modal verb> <function>.

shall  → mandatory          must → mandatory and critical
should → recommended        may  → optional
```

### 1.2 · The linter — reliable tier

These are deterministic. They are the phase's proof that requirements engineering can
be mechanised at all:

| Check | Detects |
|---|---|
| Grammar | A requirement not matching `<ID> The <system> <modal> <function>` |
| Vague terms | `fast`, `easy`, `user-friendly`, `intuitive`, `efficient`, `robust`, `seamless`, `appropriate` |
| Unique IDs | Duplicate or missing requirement ID |
| One idea | Conjunctions joining two obligations — `and`, `as well as`, `also` |
| Unquantified NFR | A performance/availability requirement with no number |
| Passive voice | "shall be validated" with no named actor |
| Modal absent | A requirement with no obligation verb at all |

**Every rule needs a negative test.** A legitimate requirement that merely *contains*
the word "fast" in a quoted string must not fire. The negative case is the deliverable;
the positive is the easy half.

### 1.3 · The standards

Grounded in the canon's nine characteristics — Clear, Complete, Consistent, Feasible,
Specific, Testable, Traceable, Modifiable, Verifiable — plus the RE process
(elicitation, analysis, specification, validation) and requirements management
(change control, versioning, volatility).

Target **12–16 standards**, of which **at least 7 mechanically enforced**.

Do *not* write a standard for every slide. Elicitation technique selection is
judgement; "every requirement has an acceptance criterion" is checkable. Write the
second kind, and route the first to the semantic tier or leave it out.

**Exit criteria:** `governova requirements lint` runs · ≥7 rules with positive and
negative tests · zero false positives against a realistic sample · coverage does not
fall.

---

## Stage 2 — C14 Data Design + the schema-soundness analyser · *the deepest moat*

**Ships:** the constitution and the analyser.
**Why second:** the strongest technical differentiator, but it needs a parser per
ecosystem, so it follows the cheaper win.

C05 governs how data is *accessed*. C14 governs how it is *structured*. Nothing in
the corpus currently asks whether a schema is sound.

### 2.1 · The analyser — reliable tier

Every one of these is a decidable property of a schema, not an opinion:

| Check | Grounded in |
|---|---|
| Entity integrity — PK present, unique, non-nullable | Relational model |
| Referential integrity — every FK resolves to a real key | Relational model |
| 1NF — repeating groups, multi-valued or CSV-in-a-column attributes | Normalisation |
| 2NF — partial dependency on part of a composite key | Normalisation |
| 3NF — transitive dependency | Normalisation |
| Unresolved M:N — a many-to-many with no bridge entity | ER modelling |
| Fan trap — a specific shape in the relationship graph | Advanced modelling |
| Redundant relationship — a cycle in the ER graph | Advanced modelling |
| Time-variant data with no temporal key | Advanced modelling |

**Start with Prisma and SQL DDL.** They are declarative, widely used, and already
present in the implementation registry. SQLAlchemy, Django, and TypeORM follow only
once the rule set has proven itself — a parser per ecosystem is a permanent tax, and
paying it five times before the rules are validated is the wrong order.

2NF and 3NF need functional dependencies, which a schema does not fully declare.
**Infer conservatively and report `unknown` rather than guess** — the standing rule
from `governova_evidence` applies here exactly. A false 3NF violation on a
deliberately denormalised reporting table would destroy trust in the whole analyser.

### 2.2 · The standards and the DBLC

Per ADR-007 constraint 4, standards name the concern universally and detection starts
relational. Denormalisation in a document store is a *deliberate trade* — C14 should
require that the trade be **recorded**, not prohibited.

The canon states it plainly: *"The SDLC traces the history of an information system.
The DBLC traces the history of a database system... the two life cycles conform to
the same basic phases."* Our build-lifecycle treats the database as one *stage*.
C14 gives it its own cycle — conceptual → logical → physical design, with gates —
and `governova handoff` gains DBLC stage briefs.

Target **14–18 standards**, of which **at least 8 mechanically enforced**.

**Exit criteria:** analyser runs against a real Prisma schema and real DDL · finds
seeded violations · **zero findings on a correct schema** · unknowns reported as
unknown.

---

## Stage 3 — C12 System Modelling

Governova has no modelling standards at all. The value here is not "draw UML" — it is
**when a model is required, which views, and whether the model still matches the code.**

Mostly semantic and structural tier. Structural probes are available for: a model
artifact exists for each declared architectural component; models are versioned with
the code rather than living in a wiki; a model changed in the same PR as the interface
it describes.

Target **8–12 standards**. Lower mechanical ratio is acceptable *here specifically*,
provided Stages 1 and 2 carry the phase above 40% overall. Say so explicitly in the PR
rather than quietly missing the bar.

---

## Stage 4 — C13 Software Evolution & Maintenance

Extends the brownfield protocol into a full lifecycle stage. The canon supplies
Lehman's laws (continuing change, increasing complexity, declining quality), four
maintenance types (corrective, adaptive, perfective, preventive), reengineering versus
refactoring, and five named code smells.

Note the overlap already present: "duplicate code" is `S1.106`, "speculative
generality" is `AP-S1.107a`. **Retro-cite rather than duplicate.** Two standards
saying the same thing is worse than one, and `S1.106` is itself the standard against
it.

Genuinely new and enforceable: technical debt must be *recorded* rather than merely
felt; every change carries an impact analysis; a legacy system has a recorded
maintain/reengineer/replace decision; maintenance type is classified on every change.

Target **10–14 standards**, **at least 5 mechanically enforced** — the debt register
and change classification are both structurally checkable.

---

## Stage 5 — Traceability closure

**The capability nobody has operationalised**, and it is only possible because the
prior stages exist: requirement IDs from Stage 1, standard IDs already, tests and
commits already.

Detect, in **both** directions:

- a requirement with no implementing code
- a requirement with **no test** — the one that matters most
- **code with no requirement** — scope creep, made visible
- a requirement changed after its tests were written
- a test referencing a requirement that no longer exists

Ships as `governova trace`, feeding the Governova Score. The industry has discussed
traceability for forty years and never mechanised it, because it required a system
that simultaneously knew about standards, requirements, code, and tests. **We will be
the first system that does.**

---

## Stage 6 — Project governance protocol *(smallest, last)*

Not a constitution — see ADR-007. `protocols/project-governance.md` covering planning,
estimation, scheduling, and risk as *practice*, plus **at most 3–5 standards folded
into C09** where they are genuinely checkable: every identified risk has a named owner
and a mitigation; estimates are recorded and compared against actuals; a project has a
recorded closure record.

Estimation *calibration* — drift between estimate and actual, measured over time — is
the only part of project management that is both mechanisable and valuable. Everything
else is judgement, and standards about judgement are unenforceable by construction.

---

## Sequencing and dependencies

```
Stage 0  Method + provenance          ── blocks everything
   │
   ├── Stage 1  C11 Requirements ────────┐
   │      (linter · headline)            │
   │                                     ├── Stage 5  Traceability
   ├── Stage 2  C14 Data Design          │      (needs Stage 1 IDs)
   │      (schema analyser · moat)       │
   │                                     │
   ├── Stage 3  C12 Modelling ───────────┘
   │
   ├── Stage 4  C13 Evolution
   │
   └── Stage 6  Project protocol
```

Stages 1–4 are independent of each other and may be reordered or parallelised.
**Stage 0 blocks all of them. Stage 5 requires Stage 1.**

---

## What this phase is actually claiming

Three things no other system does:

1. **A requirements linter bound to constitutional standards, blocking in CI.**
2. **Schema soundness — normalisation, integrity, design traps — as a merge gate.**
3. **Bidirectional requirement ↔ code ↔ test traceability, mechanically enforced.**

And one thing that makes the rest defensible: **every standard cites its grounding in
established engineering canon.** Governova stops being a vendor's opinion and becomes
the executable form of what the discipline already agreed on.

---

## Traps specific to this phase

1. **Do not mine 19 documents into 300 standards.** Coverage is a ratio. Three hundred
   unenforced standards would take it from 7.9% to roughly 5% — the score would fall,
   correctly, and the corpus would be diluted. The constraint in ADR-007 exists for
   this reason.
2. **Do not copy text.** Ideas are not copyrightable; expression is. Cite, never excerpt.
3. **Do not write a standard per slide.** Teaching material explains; standards are
   testable requirements. Most slides become no standard at all, and that is correct.
4. **Do not duplicate existing standards.** The canon overlaps Part 19 substantially.
   Retro-cite instead — and note that adding a second standard saying the same thing
   would violate `S1.106`.
5. **Do not let the schema analyser guess.** A false 3NF finding on a deliberately
   denormalised table destroys trust in every other check it makes. Report `unknown`.
6. **Do not commit the source material.** 26 MB of third-party `.doc`/`.pdf` that is
   not ours to redistribute, in git forever.
