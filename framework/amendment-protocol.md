# Amendment Protocol — Universal Primitive

| Attribute | Value |
|-----------|-------|
| **Source** | Extracted from C00-constitutional-order.md §8 |

---

## When an amendment is required

| Requires amendment | Does NOT require amendment |
|--------------------|---------------------------|
| Adding a new standard | Fixing a typo (editorial — commit directly) |
| Removing a standard | Updating a code example in an implementation guide |
| Changing a standard's scope | Adding a system context file |
| Changing a standard's severity | Adding a new runbook |
| Restructuring a constitution | Adding a new ADR |
| Any change to C0 | Updating a template |

## Solo dev amendment protocol (3 steps)

**Step 1 — Document the gap.** Create a GitHub Issue tagged `constitutional-amendment`.
Include: which constitution, which standard ID, why the current standard is insufficient,
the proposed new standard text in full. Evidence required.

**Step 2 — AI adversarial review.** Paste the amendment to Claude:
*"Review this constitutional amendment for unintended consequences, cross-constitution
conflicts, and whether the evidence justifies the change."*
Paste Claude's response to a second AI for a challenge.
Document both responses in the GitHub Issue.

**Step 3 — 24-hour personal review.** The amendment sits for 24 hours minimum.
No exceptions.

## Amendment log entry format

Every approved amendment is recorded in `governance/changelog/amendments-log.md`:

```
| Date | Standard ID | Change | Rationale | Approved by |
|------|-------------|--------|-----------|-------------|
| YYYY-MM-DD | S{C}.{N} | [what changed] | [why] | [Founder] |
```
