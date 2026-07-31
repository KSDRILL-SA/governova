# C11 — Requirements Engineering Constitution

---

| Attribute          | Value                                                              |
|--------------------|--------------------------------------------------------------------|
| **Document**       | C11 — Requirements Engineering                                     |
| **Organisation**   | KSDRILL SA                                                         |
| **Version**        | v1.0                                                               |
| **Status**         | LOCKED                                                             |
| **Locked**         | 2026-07-31                                                         |
| **Next Review**    | 2026-10-31                                                         |
| **Applies To**     | All Systems · Both Stacks · Solo Dev · Team                        |
| **Paired With**    | — (universal; no stack binding)                                    |

---

> *"The most expensive defect is the one that ships working exactly as specified."*

---

## Opening Statement

Every other constitution governs **how** a system is built. This one governs whether the
right system is being built at all.

That gap was not an oversight of emphasis — it was a blind spot with a price. A defect in
a requirement survives every gate the rest of this corpus provides. It passes review,
because the code matches the request. It passes testing, because the tests assert the
requested behaviour. It passes deployment, because nothing is broken. It is discovered by
a user, months later, and by then the cost of correction is not the cost of the change but
the cost of everything built on top of it.

C11 does not make Governova the owner of your requirements. Requirements live where your
team already keeps them — a tracker, a document, a conversation — and demanding they move
before this corpus will say anything would be the largest claim this system makes on an
adopting team, and the wrong one. **Governova defines an interchange format and reads
that**, the way it reads CycloneDX rather than owning a dependency graph (ADR-007
addendum).

The consequence is a graduated bar. A team exposing nothing is **unassessed, not in
violation** — every standard here degrades to `unknown` rather than accusing a team of
failing something it never had the chance to demonstrate. A team citing requirement
identifiers in tests and commit trailers gets traceability at no cost. A team exporting a
manifest from its own tracker gets the whole constitution.

**This constitution is unusual in the corpus: eleven of its twelve standards are
mechanically checked at merge.** That is not a coincidence — it is ADR-007 constraint 1
applied without exception. Requirements engineering has been treated as a discipline of
judgement for forty years, and most of it is. But a measurable part of it is a *grammar*,
and a grammar is decidable. The judgement was never the part that was failing.

---

## Table of Contents

| Part | Title | Standards |
|------|-------|-----------|
| §1 | Requirements Are Reachable and Traceable | S11.1–S11.4 |
| §2 | Requirements Are Well Formed | S11.5–S11.8 |
| §3 | Requirements Are Verifiable | S11.9–S11.11 |
| §4 | Requirements Are Managed | S11.12 |
| §5 | Anti-Patterns Index | — |
| §6 | Amendment Log | — |

---

## §1 — Requirements Are Reachable and Traceable

The foundation. A requirement nobody can find is not a requirement — it is a memory, and
memories are not auditable.

---

### S11.1 — Requirements Are Reachable by the Toolchain

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S11.1 |
| **Priority**    | High |
| **Applies To**  | All Stacks · all systems |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.27` (feature lifecycle) · `S9.7` (feature gate questions) |
| **Enforced By** | `governova requirements status` · structural probe (`governova_requirements`) |

**Standard:**
A system's requirements are reachable by its toolchain — as identifiers cited from code,
tests, and commit trailers, or as a manifest in the published interchange format. How they
are authored and where they are stored remains the team's choice; that they can be read is
not.

**Rationale:**
Requirements held only in a tracker nobody links to, or in a conversation nobody recorded,
cannot be traced, tested against, or audited. Every downstream guarantee in this
constitution rests on being able to name what was asked for. A system whose requirements
are unreachable cannot demonstrate that it built the right thing, however well it built
what it built.

**Anti-Patterns:**
- `AP-S11.1a` — Requirements existing only as tickets, chat messages, or verbal agreement, with nothing in the repository linking any change to any of them.

**Grounded In:**
- Sommerville, *Software Engineering* 10e — ch. 4, Requirements Engineering

---

### S11.2 — Requirement Identifiers Are Unique and Permanent

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S11.2 |
| **Priority**    | High |
| **Applies To**  | All Stacks · all systems |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S11.1` |
| **Enforced By** | requirements linter — `duplicate-id` |

**Standard:**
Each requirement carries one identifier, no identifier names two requirements, and an
identifier is never reused once retired.

**Rationale:**
An identifier naming two requirements makes every trace built on it ambiguous, and the
ambiguity is silent — both requirements appear linked, and a reviewer reading either sees
a satisfied reference. A reused identifier is worse: it silently reassigns the evidence
of one requirement to another, so tests written for the retired requirement appear to
verify the new one.

**Anti-Patterns:**
- `AP-S11.2a` — The same requirement identifier appearing on two requirements, or reassigned to a new requirement after the original was withdrawn.

**Grounded In:**
- Sommerville, *Software Engineering* 10e — ch. 4, Requirements Engineering

---

### S11.3 — Every Requirement Reaches Implementing Code

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S11.3 |
| **Priority**    | Standard |
| **Applies To**  | All Stacks · all systems |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S11.1` |
| **Enforced By** | `governova requirements trace` — `requirement-without-implementation` |

**Standard:**
Every requirement a system declares is cited by the code that implements it. A requirement
that no artifact references is either unbuilt or untraceable, and the system records which.

**Rationale:**
A requirement with no implementing code is invisible to everyone except the person who
remembers it. It surfaces at release as a missing feature nobody scheduled, or at audit as
a commitment nobody can evidence. The check costs nothing and is the only mechanical answer
to "did we actually build all of it".

**Anti-Patterns:**
- `AP-S11.3a` — A requirement carried in the manifest release after release with nothing in the repository referencing it, and no record of it having been descoped.

**Grounded In:**
- Sommerville, *Software Engineering* 10e — ch. 4, Requirements Engineering

---

### S11.4 — Every Requirement Is Verified by a Test That Cites It

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S11.4 |
| **Priority**    | Critical |
| **Applies To**  | All Stacks · all systems |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S11.1` · `S7.7` (service unit tests) |
| **Enforced By** | `governova requirements trace` — `requirement-without-test` |

**Standard:**
Every requirement is verified by at least one test that names it. The citation is part of
the test — in its name, a comment, or an annotation — so the link survives refactoring and
is readable by tooling.

**Rationale:**
A requirement with no test is an assumption. Nothing detects when it stops being true: a
refactor silently removes the behaviour, every test still passes, and the regression is
found by the user who depended on it. Coverage percentages do not answer this question —
a suite can be at 90% coverage and verify nothing anybody asked for.

**Anti-Patterns:**
- `AP-S11.4a` — A requirement implemented and shipped with no test citing its identifier, so its regression is undetectable by the suite.

**Grounded In:**
- Sommerville, *Software Engineering* 10e — ch. 8, Software Testing (acceptance testing)

---

## §2 — Requirements Are Well Formed

The canon specifies a grammar, not a philosophy. This part is that grammar, and it is
decidable.

---

### S11.5 — Every Requirement States an Obligation

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S11.5 |
| **Priority**    | High |
| **Applies To**  | All Stacks · all systems with readable requirement text |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S11.1` |
| **Enforced By** | requirements linter — `modal-absent` |

**Standard:**
Every requirement uses exactly one obligation verb — `shall` (mandatory), `must` (mandatory
and critical), `should` (recommended), or `may` (optional).

**Rationale:**
A statement with no obligation verb does not say whether it binds anyone. "The system
authenticates users" describes; it does not require. At the point of a trade-off — the only
point at which a requirement matters — nobody can tell whether it was negotiable, and the
answer is decided by whoever is under the most schedule pressure.

**Anti-Patterns:**
- `AP-S11.5a` — A descriptive sentence recorded as a requirement, with no obligation verb, leaving its bindingness to be inferred under pressure.

**Grounded In:**
- Sommerville, *Software Engineering* 10e — ch. 4, Requirements Engineering

---

### S11.6 — Every Requirement Follows the Canonical Grammar

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S11.6 |
| **Priority**    | Standard |
| **Applies To**  | All Stacks · all systems with readable requirement text |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S11.5` |
| **Enforced By** | requirements linter — `grammar` |

**Standard:**
A requirement reads `<subject> <obligation verb> <function>` — a named subject, one
obligation verb, and the behaviour required of it.

**Rationale:**
A fixed shape is what makes a requirement machine-readable and comparable. Free-form prose
hides missing subjects and missing behaviour behind fluent sentences, and a requirement
whose subject is absent cannot be assigned to a component or to a person.

**Anti-Patterns:**
- `AP-S11.6a` — A requirement whose subject is missing or implied, so no component owns it and no test knows what to exercise.

**Grounded In:**
- Sommerville, *Software Engineering* 10e — ch. 4, Requirements Engineering

---

### S11.7 — One Obligation per Requirement

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S11.7 |
| **Priority**    | Standard |
| **Applies To**  | All Stacks · all systems with readable requirement text |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S11.5` · `S1.3` (single concern) |
| **Enforced By** | requirements linter — `two-obligations` |

**Standard:**
A requirement expresses one obligation. Two obligations joined by a conjunction are two
requirements and are recorded as two, each with its own identifier.

**Rationale:**
A compound requirement cannot be partially satisfied on the record: implementing half of it
leaves the whole marked incomplete, or — far more commonly — the whole marked complete.
Its test verifies one clause and the other silently never ships. Splitting them costs one
identifier and makes both states visible.

**Anti-Patterns:**
- `AP-S11.7a` — A requirement joining two obligations with "and", so its status cannot distinguish half-built from built.

**Grounded In:**
- Sommerville, *Software Engineering* 10e — ch. 4, Requirements Engineering

---

### S11.8 — Every Obligation Names Its Actor

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S11.8 |
| **Priority**    | Standard |
| **Applies To**  | All Stacks · all systems with readable requirement text |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S11.6` |
| **Enforced By** | requirements linter — `passive-actor` |

**Standard:**
A requirement names the component responsible for meeting it. Passive obligations that
name no actor are not accepted.

**Rationale:**
"Credentials shall be validated" binds nobody. Every component assumes another one does it,
which is how an authorisation check ends up implemented nowhere — each layer trusting a
neighbour that was trusting it back. Naming the actor converts a requirement into an
assignment.

**Anti-Patterns:**
- `AP-S11.8a` — A passive requirement ("shall be validated", "shall be logged") with no named component, so responsibility is diffused across every layer and held by none.

**Grounded In:**
- Sommerville, *Software Engineering* 10e — ch. 4, Requirements Engineering

---

## §3 — Requirements Are Verifiable

A requirement nobody can measure cannot be met, only argued about.

---

### S11.9 — Requirements Contain No Unverifiable Terms

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S11.9 |
| **Priority**    | High |
| **Applies To**  | All Stacks · all systems with readable requirement text |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S11.6` |
| **Enforced By** | requirements linter — `vague-term` |

**Standard:**
A requirement states the property it requires, not an impression of it. Terms whose
satisfaction cannot be demonstrated — *fast*, *easy*, *user-friendly*, *intuitive*,
*efficient*, *robust*, *seamless*, *appropriate* — are replaced by the measurable property
they were standing in for.

**Rationale:**
An unverifiable term makes a requirement permanently disputable: no evidence can settle it,
so it is settled by whoever is more senior or more insistent. It is also the most common
way a requirement passes review — everyone agrees the system should be fast, which is
precisely why agreeing to it commits nobody to anything.

**Anti-Patterns:**
- `AP-S11.9a` — A requirement resting on an unverifiable adjective, so no test can be written for it and no evidence can close it.

**Grounded In:**
- Sommerville, *Software Engineering* 10e — ch. 4, Requirements Engineering

---

### S11.10 — Every Measurable Requirement Carries a Threshold

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S11.10 |
| **Priority**    | High |
| **Applies To**  | All Stacks · all systems with readable requirement text |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S11.9` |
| **Enforced By** | requirements linter — `unquantified` |

**Standard:**
A requirement naming a measurable property — latency, throughput, availability, capacity,
recovery time — states its threshold and the condition under which it is measured.

**Rationale:**
"High availability" is a budget request, not a requirement. Without a number there is no
point at which the system is finished and no point at which it has regressed, so the
property is engineered to whatever was convenient and discovered to be insufficient in
production. The condition matters as much as the number: 99.9% measured yearly and 99.9%
measured monthly are different systems.

**Anti-Patterns:**
- `AP-S11.10a` — A non-functional requirement naming a measurable property with no figure attached, leaving both "done" and "regressed" undefined.

**Grounded In:**
- Sommerville, *Software Engineering* 10e — ch. 4, Requirements Engineering

---

### S11.11 — Declared Metadata Agrees With the Requirement Text

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S11.11 |
| **Priority**    | Standard |
| **Applies To**  | All Stacks · all systems exporting a requirements manifest |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S11.5` |
| **Enforced By** | requirements linter — `obligation-mismatch` |

**Standard:**
Where a requirement's obligation is declared as a field as well as written in its
statement, the two agree.

**Rationale:**
Two sources for the same fact will disagree eventually, and the disagreement is silent:
a tracker export labelling a `should` as mandatory produces a report that over-states
what the system is committed to, and nobody reads both fields. The mismatch is a defect in
the export the team cannot otherwise see.

**Anti-Patterns:**
- `AP-S11.11a` — An exported requirement whose obligation field contradicts the obligation verb in its own statement, so the report and the text bind differently.

**Grounded In:**
- Sommerville, *Software Engineering* 10e — ch. 4, Requirements Engineering

---

## §4 — Requirements Are Managed

---

### S11.12 — Requirement Change Is Recorded Where the Requirement Lives

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S11.12 |
| **Priority**    | Standard |
| **Applies To**  | All Stacks · all systems |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S11.2` |
| **Enforced By** | review — see rationale; no mechanical path exists and none is claimed |

**Standard:**
When a requirement changes, the change is recorded against that requirement's identifier
where the requirement lives, with what changed and why. Requirements are amended, never
silently replaced.

**Rationale:**
A requirement that changes without a record makes every artifact citing it ambiguous —
a test written against the old text still passes, still cites the same identifier, and now
verifies something nobody asked for. This is the one standard here with **no mechanical
enforcement, and the reason is worth stating rather than hiding**: Governova reads the
requirement set as it is *now*. It does not hold the history, because the history lives in
the tracker the team owns and calling that tracker would require credentials and network
access this engine does not take. A check that cannot see the previous version cannot
detect that a version was replaced, and a check that guessed would return `satisfied` for
a repository it never examined.

**Anti-Patterns:**
- `AP-S11.12a` — A requirement's text edited in place with no record, leaving tests and code citing an identifier whose meaning has changed underneath them.

**Grounded In:**
- Sommerville, *Software Engineering* 10e — ch. 4, Requirements Engineering (requirements management)

---

## §5 — Anti-Patterns Index

| ID | Anti-Pattern | Violated Standard | Priority |
|----|-------------|-------------------|----------|
| AP-S11.1a | Requirements reachable only as tickets, chat, or verbal agreement | S11.1 | High |
| AP-S11.2a | One identifier naming two requirements, or reused after retirement | S11.2 | High |
| AP-S11.3a | A declared requirement nothing in the repository implements | S11.3 | Standard |
| AP-S11.4a | A requirement shipped with no test citing it | S11.4 | Critical |
| AP-S11.5a | A descriptive sentence recorded as a requirement | S11.5 | High |
| AP-S11.6a | A requirement with a missing or implied subject | S11.6 | Standard |
| AP-S11.7a | Two obligations joined into one requirement | S11.7 | Standard |
| AP-S11.8a | A passive obligation naming no responsible component | S11.8 | Standard |
| AP-S11.9a | A requirement resting on an unverifiable adjective | S11.9 | High |
| AP-S11.10a | A measurable property with no threshold | S11.10 | High |
| AP-S11.11a | Declared obligation contradicting the statement | S11.11 | Standard |
| AP-S11.12a | A requirement edited in place with no record of the change | S11.12 | Standard |

---

## §6 — Amendment Log

| Version | Date | Change | Reason |
|---------|------|--------|--------|
| v1.0 | 2026-07-31 | Initial lock — twelve standards establishing requirements engineering as constitutional law (ADR-007 Stage 1). §1 reachability and traceability (S11.1–S11.4), §2 grammar (S11.5–S11.8), §3 verifiability (S11.9–S11.11), §4 management (S11.12). Eleven of twelve are mechanically checked at merge by `governova_requirements`, which shipped **before** this document so that no standard here declares an enforcement path that does not exist. S11.12 is review-only and says why in its own rationale. Core count 618→630. | Governova governed construction and could not say whether the right system was being built — the one defect class that survives every other gate in the corpus, because the code matches the request, the tests assert the request, and nothing is broken. |

---

> **LOCKED — v1.0 — 2026-07-31**
>
> This document is locked. No standard may be added, removed, or modified without
> following the Amendment Protocol in C0 §8.
>
> Governova does not own your requirements. This constitution governs their form and
> their traceability, never their storage. A team that exposes nothing is **unassessed,
> not in violation** — every standard here degrades to `unknown` rather than accusing a
> team of failing something it never had the chance to demonstrate.
