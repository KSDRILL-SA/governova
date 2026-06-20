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
```

Where:
- `{C}` = constitution number (0–10, or domain/stack identifier)
- `{N}` = standard number within that constitution (sequential, no gaps)
- `{letter}` = anti-pattern variant (a, b, c... for multiple failure modes of one standard)

## ID permanence rule

Standard IDs are **permanent**. Once assigned, an ID is never reused.
A deprecated standard is marked `DEPRECATED` in its rule field and retained
with its deprecation record. It is never deleted. It is never reassigned.

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
