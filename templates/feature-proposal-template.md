# Feature Proposal — {Feature Name}

---

| Attribute       | Value |
|-----------------|-------|
| **System**      | {FundsLink / Maphophe / Reserve Bank / SyncUp} |
| **Sprint**      | Sprint {N} |
| **Group**       | G{N} — {Group 1: Core / Group 2: Supporting / Group 3: Secondary} |
| **Proposed by** | {Name} |
| **Date**        | {YYYY-MM-DD} |
| **Status**      | Draft / Under Review / Approved / Rejected |
| **GitHub Issue** | # |

---

## Field 1 — User Problem Statement

*Describe the problem this feature solves. Plain English. Written from the perspective of the user experiencing the problem — not the engineer solving it. One to three sentences maximum.*

---

## Field 2 — Primary Workflow Impact

*How does this feature affect the primary user workflow (S9.2)? Is it a G1 (core), G2 (supporting), G3 (secondary), or G4 (nice-to-have) feature? Why?*

---

## Field 3 — 5 Gate Questions (S9.7)

| Gate | Question | Answer | Pass/Fail |
|------|----------|--------|-----------|
| Q1 | Does a real user need this to complete the primary workflow? | | |
| Q2 | Does removing this feature break the primary workflow or core value? | | |
| Q3 | Can this be designed, built, and tested within 2–4 weeks? | | |
| Q4 | Does the OpenAPI contract exist? Is the DB schema defined? | | |
| Q5 | Has a real user (not the builder) confirmed they need this? | | |

*Any "Fail" defers this feature to v2.*

---

## Field 4 — Acceptance Criteria

*What does "done" look like for this feature? Written as user-observable behaviours. Numbered list. These become the test cases.*

1.
2.
3.

---

## Field 5 — Stack & Database Impact (S9.11)

**New database tables/collections:** {List or "none"}

**New API endpoints:** {List or "none"}
- Each endpoint pushes toward the v1 endpoint limit (max 15 per stack)

**New background jobs:** {List or "none"}

**New external services:** {List or "none"}

**Prisma schema changes:** {Yes/No — if Yes, migration planned?}

---

## Field 6 — Constitutional Standards Applicable

*List the standard IDs most relevant to implementing this feature. Use `indexes/standards-index.md` to find them.*

| Standard | Relevance |
|----------|-----------|
| `S{C}.{N}` | {why relevant} |

---

## Field 7 — AI Adversarial Review (Solo Mode per S10.28)

**Claude's proposal summary:**

*Paste Claude's architectural recommendation for this feature here.*

**Devil's Advocate challenge:**

*Paste the second AI's challenge response here.*

**Resolution:**

*Document how the challenge was resolved and the final design decision.*

---

## Approval

**Decision:** Approved / Rejected / Deferred to v2

**Reason:** {If rejected or deferred, explain why}

**Approved by:** Maluleke Kurhula Success

**Date:** {YYYY-MM-DD}

---

> *This proposal governs the feature. Any implementation that deviates from the acceptance criteria or constitutional standards identified here requires a new proposal revision.*
