# Practice-to-Standard Conversion Protocol

| Attribute | Value |
|-----------|-------|
| **Document** | Practice-to-Standard — how a body of established practice becomes constitutional law |
| **Layer** | Protocol (operationalises the constitution) |
| **Governed By** | C0 — Constitutional Order (§3 format, §8 amendment protocol) |
| **Applies To** | Every standard derived from a source outside this repository |
| **Status** | Active |
| **Paired With** | `governance/decisions/ADR-007-lifecycle-completeness.md` · `scripts/governova_ingest/` · `framework/format-specification.md` |

---

> *"Most of what you read becomes no standard at all. That is the protocol working, not failing."*

---

## Why this document exists

`GOVERNOVA-MASTER.md §14` specifies a **Mapping Engine**: something that ingests an
organisation's existing standards and emits a CONSTITUTION-INDEX. Building that
generally, before doing it concretely even once, is speculative abstraction — which
`AP-S1.107a` prohibits by name.

So ADR-007 constraint 5 requires the opposite order: perform the conversion **by hand**,
and write down the method while doing it. This document is that method. It is the worked
example the Mapping Engine must later reproduce, which is what makes that engine
buildable from evidence rather than from imagination.

It is also the honest answer to *"where did this standard come from?"* — asked by an
architecture board, an auditor, or a contributor who thinks a standard is wrong.

---

## §1 — What may be converted

A source is eligible when it is **established practice**: a discipline's accumulated
answer to a recurring problem, published and citable. Textbooks, standards bodies,
published post-mortems, and an organisation's own written engineering standards all
qualify.

A source is **not** eligible merely because it is written down. A vendor's marketing, a
blog post asserting a preference, and an internal habit nobody wrote down are not
established practice, and converting them produces house style wearing a citation.

### The copyright boundary — non-negotiable

**Ideas, methods, and practices are not copyrightable. Expression is.**

| Permitted | Forbidden |
|---|---|
| Reading a source and stating the requirement in Governova's own words | Copying a sentence, a definition, or a list verbatim |
| Citing author, work, edition, and chapter | Reproducing a paragraph in `Grounded In` or anywhere else |
| Naming a concept the source names (*normalisation*, *coupling*) | Reproducing the source's explanation of it |
| Holding the source outside the repository and reading it with tooling | Committing the source, or extracted text from it |

These documents are compiled, published, and shipped inside a distributed package, so an
excerpt here is a licensing defect in **every consumer's dependency tree** — not an
untidy line in ours. `C0 §3.2 SR-7` bounds a `Grounded In` entry at 120 characters and
`governova validate` rejects anything longer. That bound *is* this rule, mechanised.

---

## §2 — Reading the source reproducibly

A conversion nobody can repeat is an assertion. `scripts/governova_ingest/` exists so
that reading the source is a reproducible act:

```bash
uv run governova-ingest <path-to-corpus>                       # summary + digests
uv run governova-ingest <path-to-corpus> --out <dir> --manifest <file.json>
```

Three properties matter, and each is a rule rather than a convenience.

1. **The corpus lives outside the repository.** The tool takes a path. `.gitignore`
   excludes the conventional location explicitly so it cannot be added by accident.
2. **Extraction is deterministic.** The same document yields byte-identical text on
   every run and platform.
3. **The manifest digests the *extracted text*, not the source bytes.** It can therefore
   be published and compared while the corpus stays private — which is what lets a later
   reader confirm they are reading what the standard's author read.

Extracted text is **working material for an author**. It is never committed, and it is
never the thing a standard is written from by paraphrase. Read it, understand the
practice, close it, then write the requirement.

---

## §3 — Narrowing a teaching concept to a testable requirement

Source material **explains**. A standard **requires**. Most of what you read supports the
second without becoming it.

Apply four filters in order. A concept must survive all four.

**F1 — Is it a requirement, or is it an explanation?**
*"Cohesion measures how strongly the elements of a module belong together"* is an
explanation. *"A module has one reason to change"* is a requirement. Explanations become
`Rationale` at most, never `Standard`.

**F2 — Can it be violated?**
If you cannot describe what breaking it looks like, `C0 §3.2 SR-3` cannot be satisfied —
there is no anti-pattern to write — and the standard is too vague to be useful. Write the
anti-pattern first if you are unsure; if it will not come, the standard is not ready.

**F3 — Is it decidable by someone other than its author?**
*"Choose the appropriate elicitation technique"* is judgement: two competent engineers
will disagree and both be right. *"Every requirement has an acceptance criterion"* is
decidable. Judgement calls are excluded — not deferred, excluded — because a standard
that cannot be adjudicated becomes a lever for whoever is arguing hardest.

**F4 — Does the corpus already hold it?**
Search before writing. The canon overlaps existing standards substantially: the
Repository pattern is `S1.104`, duplicate code is `S1.106`, speculative generality is
`AP-S1.107a`, cohesion and coupling are `S1.103`. **A second standard saying the same
thing is worse than one**, and `S1.106` is itself the standard against it. When the
corpus already holds it, **retro-cite the existing standard and write nothing new.**

### The 300-standard trap

Nineteen documents could yield three hundred standards. They must not.

Coverage is a ratio, so unenforced standards inflate the denominator and **lower** the
score while looking like progress. ADR-007 constraint 2 requires at least **40%** of
standards added in Phase 2 to be mechanically enforced at merge — five times the corpus
average. A stage that cannot meet the bar **ships fewer standards, not weaker checks**.

Most of what you read should become **no standard at all**. That is the protocol working.

---

## §4 — Choosing the enforcement path *before* writing the standard

ADR-007 constraint 1: **no standard without a named enforcement path**, decided at the
moment it is written and recorded in `Enforced By`. The corpus already carries 501
unaddressed standards; the bottleneck is enforcement, not law.

| Path | Choose when | Cost of choosing wrongly |
|---|---|---|
| **Reliable tier** (`governova_checks`) | A low-false-positive textual signature exists | A lossy pattern trades the gate's trustworthiness for a coverage number |
| **Structural probe** (`governova_evidence`) | It is a deterministic fact about the repository | — |
| **Analyser** (requirements linter, schema analyser) | The property is decidable from a declarative artifact | A wrong finding on correct work destroys trust in every other finding |
| **Semantic tier** | Meaning must be read, and a wrong answer is advisory only | Silent inertness — verify the tier actually reaches its endpoint before relying on it |
| **Review only** | Nothing mechanical is possible — **and you say why, in the standard** | An unfalsifiable claim of enforcement |

Two rules govern this table.

**Never declare a path that does not exist.** `S1.104` declared reliable-tier enforcement
before any rule existed. `S8.84` demanded a CVE gate this repository did not run. Both
were found by auditing Governova against its own standards, and both are exactly what
constraint 1 exists to prevent. **Write the check in the same change as the standard.**

**A check that cannot determine an answer returns `unknown`, never `satisfied`.** A false
`satisfied` silently retires a standard nobody will examine again. Where the source is
richer than what a team exposes — requirements held in a tracker Governova cannot see, a
schema whose functional dependencies are not declared — the answer is `unknown`, and it
is never a violation.

**Never grade against a rubric wider than the standard cites.** If a check needs to
accept more than the standard allows, amend the standard first. Law first, check second,
never the reverse.

---

## §5 — Deriving anti-patterns from the failure the concept prevents

Every practice exists because something went wrong repeatedly. That failure is the
anti-pattern, and it is usually stated more plainly in the source than the practice is.

1. Ask what the practice **prevents** — not what it recommends.
2. State the failure as something an engineer does, in the present tense, concretely
   enough to be recognised in a diff.
3. Give it `AP-S{C}.{N}{letter}` under its parent standard.
4. If the failure cannot be described, return to **F2** — the standard is not ready.

Write the anti-pattern before the rationale. A rationale that cannot name a production
consequence fails `C0 §3.2 SR-2`, and the anti-pattern is where that consequence lives.

---

## §6 — Citing provenance

`Grounded In` carries the citation. `C0 §3.1` defines the block; `C0 §3.2 SR-7` governs
its content.

```markdown
**Grounded In:**
- Sommerville, *Software Engineering* 10e — ch. 4, Requirements Engineering
- Coronel & Rob, *Database Systems* — Normalization of Database Tables
```

**Cite at a granularity you have actually verified.** This is not pedantry — it was a
finding. In the Phase 2 corpus, the Sommerville study units name their chapter numbers
explicitly and consistently, so a chapter number is verifiable and is cited. The database
material does **not**: two documents in the same corpus both identify as "Chapter 5",
because chapter numbering moved between editions. Citing a number there would assert
something unverified, so those citations name the **chapter title**, which is stable
across editions and confirmed in the source.

When you cannot verify a locator, cite the coarser one that you can. A correct coarse
citation is defensible; a precise wrong one destroys the credibility of every other
citation beside it.

**A citation is not evidence of compliance.** It records where a requirement is
established. Whether *this* repository satisfies it is a separate question, answered by
the enforcement path and counted by constitutional coverage.

---

## §7 — Recording what was rejected, and why

The rejections are the most valuable output of a conversion, and the part a later reader
cannot reconstruct. Without them the same discarded idea returns every time somebody
re-reads the source.

Record, in the amendment issue or the PR body:

- **Concepts read and deliberately not converted**, with the filter they failed
  (F1–F4). *"Elicitation technique selection — F3, judgement."*
- **Concepts the corpus already held**, with the standard retro-cited instead.
  *"Duplicate code — already `S1.106`; retro-cited, not duplicated."*
- **Standards cut to meet the enforcement bar**, and what would let them return.
- **Anything refused on the copyright boundary.**

This mirrors the `S1.19` amendment, where `harden` was considered and **refused** in the
same change that added `govern` and `decision`. Recording the refusal is what
distinguishes reasoning from convenience — and it is the test the Mapping Engine will
eventually have to pass.

---

## §8 — The conversion checklist

Before opening the amendment:

- [ ] Source is established practice, and eligible under §1
- [ ] Extraction is reproducible; corpus is outside the repository and gitignored
- [ ] Nothing verbatim: no excerpt in the standard, the rationale, or `Grounded In`
- [ ] Every candidate survived F1–F4; the corpus was searched for duplicates first
- [ ] Each standard names an enforcement path that **exists in the same change**
- [ ] ≥ 40% of standards added are mechanically enforced at merge
- [ ] Each standard carries a rationale naming a production consequence (SR-2)
- [ ] Each standard carries at least one anti-pattern (SR-3)
- [ ] `Grounded In` cites at a verified granularity, within 120 characters (SR-7)
- [ ] Existing standards the source validates are **retro-cited, not duplicated**
- [ ] Rejections recorded, with the filter each failed
- [ ] `C0 §8` followed: version bump, amendment log entry, count reconciled

---

*A conversion that cannot be repeated, cannot be audited, and cannot say what it
rejected is not a conversion. It is an opinion with a bibliography.*
