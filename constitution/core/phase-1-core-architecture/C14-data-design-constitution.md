# C14 — Data Design Constitution

---

| Attribute          | Value                                                              |
|--------------------|--------------------------------------------------------------------|
| **Document**       | C14 — Data Design                                                  |
| **Organisation**   | KSDRILL SA                                                         |
| **Version**        | v1.0                                                               |
| **Status**         | LOCKED                                                             |
| **Locked**         | 2026-07-31                                                         |
| **Next Review**    | 2026-10-31                                                         |
| **Applies To**     | All Systems · Both Stacks · Solo Dev · Team · any system with persistent data |
| **Paired With**    | C5 — Database Constitution (C5 governs access; C14 governs structure) |

---

> *"A query can be rewritten on a Tuesday. A schema cannot."*

---

## Opening Statement

C5 governs how data is **accessed** — queries, transactions, clients, migrations. Nothing
in this corpus asked whether the thing being accessed is **sound**.

That gap had a shape: Governova could tell you a query was unparameterised and could not
tell you the table it queried had no primary key. It could demand a transaction around two
writes and not notice that the two rows they touched could never be told apart.

Data-model defects belong to the same class as requirements defects, and for the same
reason: **they are not refactored away.** A badly named function is a morning's work. A
missing key is every row already written under it, every foreign key pointing at it, every
report built on it, and every integration that learned its shape. The cost of correcting a
schema is not the cost of the change — it is the cost of everything standing on it.

Two commitments run through this document.

**Principles are model-agnostic; detection starts where it is decidable.** The relational
canon is where these concerns were named, but they are not relational concerns.
Redundancy causing anomalies, referential consistency, and identity apply to document and
wide-column stores too — where denormalisation is a **deliberate trade rather than an
absent concern**. So every standard here names the concern universally, and `C14` requires
that a trade be *recorded*, never that it be prohibited. A constitution that reads as
though it were written in 1975 will be dismissed by the teams that most need it.

**What cannot be decided is not asserted.** Second and third normal form are properties of
*functional dependencies*, which a schema does not declare. The analyser backing this
constitution returns them as `unknown` and `S14.7` says so in its own text. A false
normalisation verdict on a deliberately denormalised reporting table would discredit every
other finding beside it, and the corpus does not spend that credit.

**Nine of fourteen standards are mechanically checked at merge** by `governova_schema`,
which shipped before this document so that no standard here declares an enforcement path
that does not exist.

---

## Table of Contents

| Part | Title | Standards |
|------|-------|-----------|
| §1 | Identity | S14.1–S14.3 |
| §2 | Referential Integrity | S14.4–S14.5 |
| §3 | Normalisation and Deliberate Denormalisation | S14.6–S14.8 |
| §4 | Relationship Modelling | S14.9–S14.11 |
| §5 | Time-Variant Data | S14.12 |
| §6 | The Database Life Cycle | S14.13–S14.14 |
| §7 | Anti-Patterns Index | — |
| §8 | Amendment Log | — |

---

## §1 — Identity

If a row cannot be told apart from another, nothing else in this document can be enforced.

---

### S14.1 — Every Entity Is Identifiable

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S14.1 |
| **Priority**    | Critical |
| **Applies To**  | All Stacks · every entity in every store |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S5.10` (required fields on every table) |
| **Enforced By** | `governova schema` — `no-primary-key` |

**Standard:**
Every entity declares a key that identifies exactly one instance of it. A collection whose
members cannot be distinguished from one another is not an entity.

**Rationale:**
Without identity there is no update — only a filter that might match one row or nine. No
other entity can reference this one, because a reference needs something to point at.
Duplicates cannot be prevented, because duplication cannot be defined. Every guarantee
below this one assumes it, which is why it is the first standard in the document.

**Anti-Patterns:**
- `AP-S14.1a` — An entity with no declared key, so its rows can be duplicated, cannot be individually updated, and cannot be referenced.

**Grounded In:**
- Coronel & Rob, *Database Systems* — The Relational Database Model (entity integrity)

---

### S14.2 — No Part of a Key Is Optional

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S14.2 |
| **Priority**    | Critical |
| **Applies To**  | All Stacks · every entity in every store |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S14.1` |
| **Enforced By** | `governova schema` — `nullable-primary-key` |

**Standard:**
No attribute participating in an entity's key is nullable.

**Rationale:**
A null does not equal another null, so a nullable key attribute makes identity undecidable
exactly when it matters — two rows with a null in the same position are neither the same
nor different. Uniqueness silently stops being enforced, and the constraint that appears
to guarantee identity guarantees nothing.

**Anti-Patterns:**
- `AP-S14.2a` — A key whose attributes permit null, so uniqueness stops being enforced for precisely the rows where identity is least certain.

**Grounded In:**
- Coronel & Rob, *Database Systems* — The Relational Database Model (entity integrity)

---

### S14.3 — Keys Are Stable and Carry No Business Meaning

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S14.3 |
| **Priority**    | High |
| **Applies To**  | All Stacks · every entity in every store |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S14.1` · `S5.5` (cross-database references) |
| **Enforced By** | review — a key's *stability* is a claim about the future, which no schema states |

**Standard:**
An entity's key does not change over the entity's lifetime, and its value encodes no
business fact that could change independently of identity.

**Rationale:**
A key that carries meaning inherits that meaning's volatility. An email address, a
national identifier, a product code, a registration number — each is unique until an
organisation restructures, a person marries, or a regulator reissues the format. When the
value changes, every reference to it is either rewritten across the whole system or
silently left pointing at something that no longer exists.

This standard is **review-only and the reason is worth stating rather than hiding**:
stability is a claim about how a value will behave in future, and a schema declares no
such thing. A check could see that a key is a string; it cannot see that the string is a
person's email. Asserting otherwise would be a guess about meaning.

**Anti-Patterns:**
- `AP-S14.3a` — A business value used as a key — email, national id, product code — so that a change to the fact rewrites or orphans every reference to the entity.

**Grounded In:**
- Coronel & Rob, *Database Systems* — Advanced Data Modeling (primary key guidelines)

---

## §2 — Referential Integrity

A reference that cannot be relied upon is worse than no reference: it is relied upon.

---

### S14.4 — Every Reference Resolves

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S14.4 |
| **Priority**    | Critical |
| **Applies To**  | All Stacks · every entity in every store |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S14.1` · `S5.13` (foreign key indexes) |
| **Enforced By** | `governova schema` — `dangling-foreign-key` |

**Standard:**
Every attribute that references another entity names an entity that exists in the model.
Where the store enforces referential constraints, the reference is declared to it rather
than maintained in application code alone.

**Rationale:**
An unresolvable reference is a constraint nobody is checking. The column accumulates
values pointing at nothing, and the first thing to discover this is a join that silently
returns fewer rows than the reader expected — a wrong answer, delivered confidently, with
no error anywhere.

**Anti-Patterns:**
- `AP-S14.4a` — A foreign key naming an entity that does not exist in the model, so the constraint is unenforceable and the column fills with values pointing at nothing.

**Grounded In:**
- Coronel & Rob, *Database Systems* — The Relational Database Model (referential integrity)

---

### S14.5 — Every Reference Points at a Key

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S14.5 |
| **Priority**    | High |
| **Applies To**  | All Stacks · every entity in every store |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S14.4` |
| **Enforced By** | `governova schema` — `foreign-key-to-non-key` |

**Standard:**
A reference targets an attribute that identifies exactly one instance — a primary key or a
declared unique attribute. It never targets a merely descriptive attribute.

**Rationale:**
A reference to a non-unique attribute is a reference to *a set*. The join that follows it
multiplies rows rather than resolving one, and the result is an aggregate that is too
large by an amount nobody can predict. Because the schema still looks like it has a
relationship, this reads as a data problem for months before it is recognised as a design
one.

**Anti-Patterns:**
- `AP-S14.5a` — A reference targeting a descriptive attribute rather than a key, so a join resolves to many rows and every aggregate over it is silently inflated.

**Grounded In:**
- Coronel & Rob, *Database Systems* — The Relational Database Model (referential integrity)

---

## §3 — Normalisation and Deliberate Denormalisation

---

### S14.6 — An Attribute Holds One Value

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S14.6 |
| **Priority**    | High |
| **Applies To**  | All Stacks · every entity in every store |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S14.1` |
| **Enforced By** | `governova schema` — `repeating-group` · **advisory**, see rationale |

**Standard:**
An attribute holds a single value of its type, not a list, a delimited string, or a
repeating group. Where a store offers a list-valued attribute and it is used deliberately,
`S14.8` applies.

**Rationale:**
A list inside an attribute cannot be constrained, referenced, indexed for membership, or
counted without parsing. Adding a member is a read-modify-write of the whole value, which
makes two concurrent additions lose one. The elements are data the database has been told
to treat as text.

The check is **advisory rather than blocking**, and that is the point of ADR-007
constraint 4: a list-valued attribute is a repeating group under the relational model and
a correct, considered choice in plenty of real schemas. The concern is universal; the
verdict belongs to the designer who knows whether the trade was made on purpose.

**Anti-Patterns:**
- `AP-S14.6a` — Multiple values packed into one attribute — a CSV string, a delimited list — so membership cannot be queried, constrained, or referenced without parsing.

**Grounded In:**
- Coronel & Rob, *Database Systems* — Normalization of Database Tables (first normal form)

---

### S14.7 — Third Normal Form Is the Default

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S14.7 |
| **Priority**    | High |
| **Applies To**  | All Stacks · every transactional entity |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S14.6` |
| **Enforced By** | review — **the analyser reports `unknown` here by design; see rationale** |

**Standard:**
An entity that records transactional state is normalised to third normal form unless
`S14.8` records why it is not: every non-key attribute depends on the key, the whole key,
and nothing but the key.

**Rationale:**
Un-normalised structure produces update anomalies — the same fact stored in many rows,
corrected in some of them. That is not a performance concern; it is a correctness one,
and it produces data that disagrees with itself while every constraint still passes.

**This standard is deliberately not mechanically enforced, and that is a finding rather
than a gap.** Second and third normal form are properties of *functional dependencies*,
and a schema does not declare them. Deciding that `city` depends on `postcode` means
reading meaning out of column names, and being wrong about that on a deliberately
denormalised reporting table would discredit every other check the analyser makes. So
`governova schema` returns these questions as `unknown` with the reason attached, rather
than answering them. Undemonstrated compliance is uncounted, exactly as an auditor treats
it.

**Anti-Patterns:**
- `AP-S14.7a` — A transactional entity storing the same fact in many rows, so a correction applied to some of them leaves the data disagreeing with itself while every constraint still passes.

**Grounded In:**
- Coronel & Rob, *Database Systems* — Normalization of Database Tables

---

### S14.8 — Denormalisation Is Recorded, Never Assumed

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S14.8 |
| **Priority**    | High |
| **Applies To**  | All Stacks · every store, relational or otherwise |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S14.7` · `S1.85` (ADRs document significant decisions) |
| **Enforced By** | review — no check can distinguish a recorded trade from an unrecorded one; see rationale |

**Standard:**
Where a model departs from normalised structure — a duplicated attribute, an embedded
document, a list-valued attribute, a wide denormalised read model — the departure is
recorded with what it buys, what it costs, and how the duplicated fact is kept consistent.
Denormalisation is a decision, not a default.

**Rationale:**
This is the standard that makes the rest of `§3` usable outside a relational store.
Denormalisation is frequently correct: it is how document stores model aggregates and how
read models are made fast. **What is never correct is denormalising by accident**, because
then nobody owns the consistency of the duplicated fact and no reader can tell a
considered trade from an oversight.

An unrecorded departure also defeats review permanently. The next engineer sees
duplication, cannot tell whether it was deliberate, and either propagates it or removes
the thing that was holding a performance requirement together.

**Anti-Patterns:**
- `AP-S14.8a` — Duplicated or embedded data with no record of the trade, so a later reader cannot distinguish a deliberate optimisation from an oversight and no one owns keeping the copies consistent.

**Grounded In:**
- Coronel & Rob, *Database Systems* — Normalization of Database Tables (denormalisation)

---

## §4 — Relationship Modelling

---

### S14.9 — A Many-to-Many Relationship Has a Bridge Entity

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S14.9 |
| **Priority**    | High |
| **Applies To**  | All Stacks · every model with many-to-many associations |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S14.1` · `S14.4` |
| **Enforced By** | `governova schema` — `unresolved-many-to-many` · **advisory** |

**Standard:**
A many-to-many association is modelled as an explicit bridge entity with its own key. It
is not left for a tool to synthesise.

**Rationale:**
The association itself has attributes, and they arrive later without exception — when the
membership started, who granted it, what role it confers, whether it is still active. An
implicit join table has nowhere to put them, so adding the first one is a migration
against a table nobody designed, whose name, key, and indexes were chosen by a generator.

**Anti-Patterns:**
- `AP-S14.9a` — A many-to-many left implicit, so the association can carry no attributes of its own and the first one required forces a migration against a generated table.

**Grounded In:**
- Coronel & Rob, *Database Systems* — Entity-Relationship (ER) Modeling (M:N resolution)

---

### S14.10 — Fan Traps Are Resolved or Documented

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S14.10 |
| **Priority**    | Standard |
| **Applies To**  | All Stacks · every model with branching one-to-many relationships |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S14.4` |
| **Enforced By** | `governova schema` — `fan-trap` · **advisory** |

**Standard:**
Where one entity is the parent of two or more one-to-many relationships, the model records
that joining the children through the parent does not produce a valid combined result.

**Rationale:**
The shape is legitimate and common — a customer with invoices and with payments. The trap
is that a query joining both through the customer multiplies invoices by payments, and the
total it reports is not wrong-looking, just wrong. Nothing errors. The number is simply
too large, by a factor that varies per customer, and it will be believed.

The structure is not a defect, so the standard asks for the hazard to be known rather than
for the model to change.

**Anti-Patterns:**
- `AP-S14.10a` — Two one-to-many children joined through their shared parent, producing a silently inflated aggregate that raises no error and is believed.

**Grounded In:**
- Coronel & Rob, *Database Systems* — Advanced Data Modeling (fan traps)

---

### S14.11 — One Fact Has One Path

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S14.11 |
| **Priority**    | Standard |
| **Applies To**  | All Stacks · every model |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S14.4` |
| **Enforced By** | `governova schema` — `redundant-relationship` · **advisory** |

**Standard:**
Where two entities are related both directly and through a third, the shortcut is recorded
as a deliberate denormalisation under `S14.8` or removed.

**Rationale:**
Two paths to the same fact can disagree, and nothing in the model prevents it — an order
linked to a customer directly *and* through its account will eventually name two different
customers. The shortcut is often a real optimisation, which is why the standard asks for
the trade to be recorded rather than for the edge to be deleted. What it forbids is a
second path nobody decided to create.

**Anti-Patterns:**
- `AP-S14.11a` — The same fact reachable by two relationship paths with nothing keeping them in agreement, so the model can assert two different answers to one question.

**Grounded In:**
- Coronel & Rob, *Database Systems* — Advanced Data Modeling (redundant relationships)

---

## §5 — Time-Variant Data

---

### S14.12 — History Is Keyed by Time

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S14.12 |
| **Priority**    | High |
| **Applies To**  | All Stacks · every entity recording state over time |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S14.1` · `S5.65` (ledger immutability) |
| **Enforced By** | `governova schema` — `time-variant-without-temporal-key` · **advisory** |

**Standard:**
An entity that records how something changed over time includes a temporal attribute in
its key, so that two states of the same subject can coexist.

**Rationale:**
Time-variant data keyed only by its subject can hold exactly one version of it. The second
version either overwrites the first — history silently lost, with the columns that were
supposed to record it still present and now meaningless — or violates the key. A price
history that cannot hold two prices is a price.

**Anti-Patterns:**
- `AP-S14.12a` — An entity carrying validity or version attributes whose key omits them, so each new state overwrites the previous one and the history the columns promise is never actually retained.

**Grounded In:**
- Coronel & Rob, *Database Systems* — Advanced Data Modeling (time-variant data)

---

## §6 — The Database Life Cycle

The canon is explicit that a database has its own life cycle running alongside the
system's: *the SDLC traces the history of an information system; the DBLC traces the
history of a database system, and the two conform to the same basic phases.* Our
build lifecycle treats the database as one stage of a build. It is a cycle of its own.

---

### S14.13 — The Model Passes Three Design Stages

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S14.13 |
| **Priority**    | Standard |
| **Applies To**  | All Stacks · every system with persistent data |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S5.6` (database selection documented at design time) · `S11.1` (requirements reachable) |
| **Enforced By** | review — a design *stage* leaves no artifact a schema file can be checked against |

**Standard:**
A data model is designed in three distinct stages before it is built: **conceptual** —
which entities exist and how they relate, independent of any product; **logical** —
attributes, keys, and normalisation, independent of any engine; **physical** — types,
indexes, partitioning, and storage for the chosen engine. Each stage is completed before
the next begins.

**Rationale:**
Collapsing the stages is how engine features become the model. Starting at physical design
produces entities shaped by what was convenient to index rather than by what the business
actually distinguishes, and that shape then outlives the engine that suggested it. Keeping
conceptual design free of product and logical design free of engine is what makes a model
portable, reviewable by people who do not know the engine, and stable when the engine
changes.

**Anti-Patterns:**
- `AP-S14.13a` — A schema authored directly in the engine's DDL with no conceptual or logical model, so entity boundaries were decided by indexing convenience and cannot be reviewed by anyone who does not know the engine.

**Grounded In:**
- Coronel & Rob, *Database Systems* — Database Design (the database life cycle)

---

### S14.14 — Physical Design Is Recorded Against What It Optimises

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S14.14 |
| **Priority**    | Standard |
| **Applies To**  | All Stacks · every system with persistent data |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S14.13` · `S5.25` (indexes on query-critical fields) |
| **Enforced By** | review — an index's *purpose* exists nowhere a schema file can be read from |

**Standard:**
Every physical-design decision — an index, a partition, a materialised view, a storage
choice — records the access pattern it serves.

**Rationale:**
An index with no recorded purpose cannot be removed. Nobody knows which query depends on
it, so it survives every review, is maintained on every write forever, and accumulates
alongside the others. The cost is invisible because it is paid in write latency rather
than in anything a dashboard names, and the only honest way to retire one is to know what
it was for.

**Anti-Patterns:**
- `AP-S14.14a` — An index or partition with no recorded access pattern, so it can never be safely removed and is paid for on every write indefinitely.

**Grounded In:**
- Coronel & Rob, *Database Systems* — Database Design (physical design)

---

## §7 — Anti-Patterns Index

| ID | Anti-Pattern | Violated Standard | Priority |
|----|-------------|-------------------|----------|
| AP-S14.1a | An entity with no declared key | S14.1 | Critical |
| AP-S14.2a | A key whose attributes permit null | S14.2 | Critical |
| AP-S14.3a | A business value used as a key | S14.3 | High |
| AP-S14.4a | A reference naming an entity that does not exist | S14.4 | Critical |
| AP-S14.5a | A reference targeting a descriptive attribute | S14.5 | High |
| AP-S14.6a | Multiple values packed into one attribute | S14.6 | High |
| AP-S14.7a | A transactional entity storing one fact in many rows | S14.7 | High |
| AP-S14.8a | Duplicated or embedded data with no record of the trade | S14.8 | High |
| AP-S14.9a | A many-to-many left implicit | S14.9 | High |
| AP-S14.10a | Two one-to-many children joined through their shared parent | S14.10 | Standard |
| AP-S14.11a | The same fact reachable by two disagreeing paths | S14.11 | Standard |
| AP-S14.12a | History whose key omits its temporal attribute | S14.12 | High |
| AP-S14.13a | A schema authored directly in DDL with no logical model | S14.13 | Standard |
| AP-S14.14a | An index or partition with no recorded access pattern | S14.14 | Standard |

---

## §8 — Amendment Log

| Version | Date | Change | Reason |
|---------|------|--------|--------|
| v1.0 | 2026-07-31 | Initial lock — fourteen standards establishing data-model soundness as constitutional law (ADR-007 Stage 2). §1 identity (S14.1–S14.3), §2 referential integrity (S14.4–S14.5), §3 normalisation and deliberate denormalisation (S14.6–S14.8), §4 relationship modelling (S14.9–S14.11), §5 time-variant data (S14.12), §6 the database life cycle (S14.13–S14.14). **Nine of fourteen are mechanically checked at merge** by `governova_schema`, which shipped in #157 **before** this document so that no standard declares an enforcement path that does not exist. S14.3, S14.7, S14.8, S14.13, and S14.14 are review-only and each states why in its own rationale — S14.7's reason is the load-bearing one: normal form is a property of functional dependencies, which a schema does not declare. Core count 630→644. | C5 governed how data is *accessed* and nothing asked whether the thing being accessed was *sound*. Governova could report an unparameterised query and not that the table it queried had no primary key. Data-model defects are not refactored away: the cost of correcting a schema is the cost of everything already standing on it. |

---

> **LOCKED — v1.0 — 2026-07-31**
>
> This document is locked. No standard may be added, removed, or modified without
> following the Amendment Protocol in C0 §8.
>
> **Principles here are model-agnostic; detection begins where it is decidable.**
> Denormalisation is required to be *recorded* (`S14.8`), never prohibited — it is how
> document stores model aggregates and how read models are made fast. What is forbidden is
> denormalising by accident, because then nobody owns the consistency of the duplicated
> fact.
>
> **What cannot be decided is not asserted.** `S14.7` is enforced by review because normal
> form is a property of functional dependencies, which no schema declares. The analyser
> returns `unknown` and says why. Undemonstrated compliance is uncounted, exactly as an
> auditor treats it.
