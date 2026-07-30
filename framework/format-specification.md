# Format Specification — Universal Primitive

| Attribute | Value |
|-----------|-------|
| **Layer** | 1 — Framework |
| **Type** | Universal primitive |
| **Applies To** | Every standard, every constitution, every domain, every stack |

---

## Standard ID format

Every standard follows this exact structure:

```
S{C}.{N} — {title}
Severity:     SEV0 | SEV1 | SEV2 | SEV3
Phase:        0 | 1 | 2 | 3
Applies To:   [all systems | specific stack | specific domain]
Rule:         [the requirement, stated positively]
Rationale:    [why this standard exists]
Anti-pattern: AP-S{C}.{N}{letter} — [what failure looks like]
Grounded In:  [author, work, edition — chapter]   (optional)
```

Where:
- `{C}` = constitution number (0–10, or domain/stack identifier)
- `{N}` = standard number within that constitution (sequential, no gaps)
- `{letter}` = anti-pattern variant (a, b, c... for multiple failure modes of one standard)

## Provenance

`Grounded In` is the only optional element of a standard, and the only one that points
outside the corpus. It records where a requirement is already established in the
engineering canon, so a standard is defensible by citation rather than by assertion.
An absent `Grounded In` means the standard is unsourced, not that it is unfounded.

Each entry is a **citation, never an excerpt** (C0 §3.2 SR-7): author, work, edition,
chapter — never the source's own words. Ideas and methods are not copyrightable;
expression is, and these documents are compiled and shipped inside a published package.
`governova validate` rejects any entry longer than 120 characters, which is the
mechanical form of that boundary.

## ID permanence rule

Standard IDs are **permanent**. Once assigned, an ID is never reused.
A deprecated standard is marked `DEPRECATED` in its rule field and retained
with its deprecation record. It is never deleted. It is never reassigned.

## Domain standard ID format (Layer 4)

A domain extension adds industry-specific standards **on top of** the universal core.
Domain standards carry their own namespace so that a domain can never consume a core
constitution number, and so a community-contributed domain is distinguishable from
ratified core law at a glance:

```
D-{DOMAIN}.{N} — {title}
Extends:      S{C}.{N} — the core standard(s) this builds on (mandatory)
Applies To:   [all systems in domain | specific stack]
Rule:         [the additional requirement the industry imposes]
Rationale:    [why the core alone is insufficient here]
Anti-pattern: AP-D-{DOMAIN}.{N}{letter} — [what failure looks like]
```

Where `{DOMAIN}` is the upper-case domain identifier from the registry in
`constitution/domains/README.md` (e.g. `FINTECH`, `GOVTECH`).

Domain standards use the **same block shape** as core standards — attribute table plus
`**Standard:**` / `**Rationale:**` / `**Anti-Patterns:**` labelled blocks, and the same
optional `**Grounded In:**` — so one format governs Layer 2 and Layer 4. Two rules are
specific to Layer 4:

1. **Every domain standard declares `**Extends:**`** — at least one core standard it
   builds on. A domain standard with no anchor cannot be conflict-checked against the
   core, and is a sign the standard belongs in Layer 2 instead.
2. **A domain may raise a floor the core sets, never lower one.** Every document ends
   with a conflict-analysis table naming each core standard it interacts with and the
   resolution.

Domains have no phase and no hierarchy rank: a domain extends the whole core rather
than sitting at one point within it.

## Implementation binding format

When a universal standard is bound to a specific stack:

```
S{C}.{N}/{stack} — {title}
Binds:    S{C}.{N} in the universal core
Stack:    {stack name}
Satisfies by: [exactly how the standard is met in this technology]
Anti-pattern: AP-S{C}.{N}{letter}/{stack} — [stack-specific failure mode]
```

## Document structure

Every constitution document must contain, in order:
1. Title block with: Document, Organisation, Version, Status, Locked date,
   Applies To, Phase, Paired With
2. Opening principle quote
3. Table of contents
4. Sections with standards in S{C}.{N} format
5. Amendment log at the end
