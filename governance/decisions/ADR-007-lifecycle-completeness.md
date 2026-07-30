# ADR-007 — Lifecycle Completeness

---

| Attribute   | Value |
|-------------|-------|
| **ID**      | ADR-007 |
| **Date**    | 2026-07-30 |
| **Status**  | accepted |
| **Supersedes** | — |
| **Amends**  | ADR-005 (sequencing only — inserts a phase, changes no decision) |
| **Relates To** | S1.103–S1.107, S5.28, S7.25, S9.7, C05, C07, C09 |

---

## Context

Governova governs **construction**. Its 618 standards are overwhelmingly about how
code is written — layering, auth, queries, tests, deployment, operations. A gap
audit against two established bodies of practice (Sommerville's *Software
Engineering*, 10th ed.; Coronel & Rob's *Database Systems*) makes the shape of what
is missing precise:

| Discipline | Governova today |
|---|---|
| Requirements engineering | nothing — C09 gates features, it does not govern requirements |
| System modelling | nothing |
| Software evolution & maintenance | brownfield protocol only |
| Project planning, estimation, risk | nothing |
| Data design — ER, normalisation, integrity | nothing — C05 governs *queries*, not *schemas* |

**Requirements defects and data-model defects are the two most expensive failure
classes in software.** Neither can be refactored away later, and Governova is blind
to both. The canon puts numbers on it: a requirements error found after delivery
costs up to 100× one found during implementation; maintenance consumes 50–90% of
lifetime cost.

Two findings from the audit shape the decision.

**The canon independently validates standards we already hold.** The Repository
pattern is our `S1.104`. "Speculative generality" is our `AP-S1.107a`. "Duplicate
code" is our `S1.106`. Cohesion, coupling, and SOLID are our `S1.103`. Part 19 was
not invented — it was a rediscovery of established practice. That is a far stronger
position than an unsourced house style, and it is currently invisible.

**Requirements are lintable.** The canon specifies a *grammar*, not a philosophy:
`<Req ID> The <system> <shall|must|should> <function>`, with unique IDs, one idea per
requirement, quantified thresholds, and an explicit banned-word list (*fast*, *easy*,
*user-friendly*). That is deterministic. Nobody ships it.

---

## Decision

Extend Governova from a **construction** governor to a **lifecycle** governor, in
one sequenced phase, under six binding constraints.

### The scope

Four new core constitutions, each slotted into the existing phase model without
renumbering anything:

| ID | Constitution | Phase | Why there |
|----|--------------|-------|-----------|
| **C11** | Requirements Engineering | 0 — Foundation | Requirements precede the first line of code |
| **C12** | System Modelling | 1 — Core Architecture | Models are the design contract architecture is built from |
| **C13** | Software Evolution & Maintenance | 2 — Quality & Reliability | Maintainability is a reliability property |
| **C14** | Data Design | 1 — Core Architecture | Sits beside C05, which governs queries but not schemas |

Plus two engine capabilities and one schema change:

- **A requirements linter** — the grammar, as reliable-tier rules.
- **A schema-soundness analyser** — entity/referential integrity, normal forms, and
  design traps, from real schema files.
- **`Grounded In`** — an optional provenance field on every standard.

Project management (estimation, PERT/CPM, scheduling) becomes a **protocol, not a
constitution**. Most of it is context-dependent judgement that cannot be enforced or
evidenced; only risk ownership and estimate-versus-actual recording are checkable,
and those fold into C09. Writing forty unenforceable standards about scheduling would
damage the corpus, not extend it.

### The six constraints

**1. No standard without a named enforcement path.** Every standard added in this
phase declares, at the moment it is written, how compliance is determined: a
reliable-tier rule, a structural probe, the semantic tier, or an explicit
"review-only, and here is why nothing else is possible." The corpus already carries
501 unaddressed standards; the bottleneck is enforcement, not law.

**2. Enforcement coverage must rise, not fall.** Constitutional coverage is 7.9%
(43/544). Adding standards inflates the denominator, so a careless expansion *lowers*
the score while appearing to be progress. **At least 40% of the standards added in
this phase must be mechanically enforced at merge** — five times the corpus average.
A stage that cannot meet the bar ships fewer standards, not weaker checks.

**3. Nothing is copied.** The source material derives from copyrighted textbooks.
Ideas, methods, and practices are not copyrightable; expression is. Every standard is
written fresh in Governova's own voice, and `Grounded In` carries a **citation, never
an excerpt**. The source documents are not committed to this repository.

**4. Principles are model-agnostic; detection starts where it is decidable.**
The data-design material is classical relational. The *concerns* — redundancy causing
anomalies, referential consistency, identity — apply to document and wide-column
stores too, where denormalisation is a deliberate trade rather than an absent
concern. Standards are therefore written to name the concern universally, while
detection is implemented first where schemas are declarative. A constitution that
reads as though it were written in 1975 will be dismissed by the teams that most need
it.

**5. The conversion is done by hand once, and instrumented.** `master.md §14`
specifies a Mapping Engine that ingests an organisation's standards and emits a
CONSTITUTION-INDEX. Building that generally, before doing it concretely even once,
is speculative abstraction — which our own `AP-S1.107a` prohibits. So this phase
performs the conversion manually and **records the method as a protocol**, producing
the worked example the engine must later reproduce. The engine is built from
evidence, in a later phase.

**6. Existing standards gain provenance too.** `Grounded In` is not only for new
standards. Part 19, `S1.106`, `S1.107`, and the testing and design standards are
retro-cited. The claim being made is not "we wrote good rules" but "we converged
on established engineering practice, and here is where it is written down."

### Sequencing

This becomes **Phase 2**, inserted after ADR-005's Phase 1 (workstreams A + B,
complete) and before brownfield onboarding. ADR-005's Phase 2 (workstream C —
brownfield) becomes Phase 3, and Phase 3 (workstream D — Cloud) becomes Phase 4.
**No decision in ADR-005 changes; only the ordering.**

Brownfield adoption moves *behind* this work deliberately: onboarding an existing
system against a corpus that cannot discuss its requirements or its schema is a
weaker product than onboarding against one that can.

---

## Consequences

### What becomes easier

- Governova can answer the two questions it currently cannot: *did you build the
  right thing*, and *is your data model sound* — the two most expensive places to be
  wrong.
- Every standard becomes defensible to an architecture board or a regulator by
  citation rather than by assertion.
- The requirements linter and schema analyser are both **stack-independent
  differentiators**. They apply to a Django shop and a Spring shop equally, unlike
  most of the current rule set.

### What becomes harder

- The corpus grows by roughly 10%, and every one of those standards must arrive with
  its enforcement decided. That is slower per standard, deliberately.
- The schema analyser needs a parser per ecosystem (Prisma, SQL DDL, SQLAlchemy,
  Django, TypeORM). Each is a tax. Relational-first keeps the first one tractable.
- Requirements linting only works if requirements exist as files in a known format.
  C11 must therefore specify *where requirements live and how they are written* — a
  stronger claim on an adopting team than anything Governova currently makes.

### Constitutional alignment

Reinforces `S1.107` (the simplest correct solution — hence hand-conversion before
engine), `S1.106` (DRY — hence one provenance field rather than per-constitution
bibliographies), and `S9.7` (feature gate questions — hence the enforcement-path
constraint). Extends `C05` without amending it: C05 governs how data is *accessed*,
C14 governs how it is *structured*.

### Open questions deferred to later ADRs

- Whether `governova-types` and the Mapping Engine ship as separate products.
- How requirement IDs reconcile with an organisation's existing tracker (Jira, Azure
  DevOps) rather than replacing it.
- Whether non-relational schema soundness is decidable enough to enforce, or belongs
  permanently in the semantic tier.
