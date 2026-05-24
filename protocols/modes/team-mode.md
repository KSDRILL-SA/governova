# Team Overlay — KSDRILL SA

---

| Attribute       | Value |
|-----------------|-------|
| **Document**    | Team Overlay |
| **Version**     | v1.0 |
| **Applies To**  | All Systems · Team Operating Mode |
| **Overlay For** | C1 Engineering Standards — process standards |

---

## What This Overlay Does

In team mode, constitutional standards apply in full without adaptation. This overlay documents the team-specific process extensions — the additional requirements that multi-person collaboration imposes on the base constitutional standards.

Load this overlay when the system context file shows `Operating Mode: TEAM`.

---

## Team Process Extensions

### S1.27 — Feature Proposal (Team Extensions)

- Proposals are posted to the team channel with a 48h review window
- Cross-constitution impacts are identified as a team — one person's amendment frequently requires changes to multiple constitutions
- Any team member may comment with supporting evidence or counterarguments
- Owner approval: Maluleke Kurhula Success signs off on every approved proposal

### S1.30 — 2-Approval Merge Rule (Full)

- Two human approvals required — no AI review substitutes
- Both reviewers must be different people from the PR author
- AI code review (S10.34) is additive — a third review, not a substitute
- Reviews must cite the standard for any issue raised: "This violates S3.14 (access token storage)" not "This looks wrong"

### S1.12 — Standup (Team)

- Daily async standup posted to team channel by 10:00 AM
- Format: What I completed / What I'm working on today / What is blocking me
- Blockers unresolved for 4+ hours are escalated to a GitHub Issue and tagged for the team

### Amendment Protocol (C0 §8.3 — Team Full)

- 48h open review in team channel — not reducible
- Cross-constitution impacts require team review across all affected constitutions
- Owner approval: Maluleke Kurhula Success explicitly approves in the GitHub Issue
- Commit structure: version bump + amendment log + all cross-constitution updates in a single PR

---

## Team PR Review Standards

Every PR reviewer in team mode:

1. **Reads the full diff** — not just the changed file
2. **Cites the standard** for every issue raised — `"Per S5.11 (explicit select), this query needs a select clause"`
3. **Tests the change locally** for any PR touching auth, database schema, or the primary user workflow
4. **Approves with evidence** — "LGTM — self-review checklist confirmed complete, AI review documented, all four layers committed separately"

---

## Team AI Collaboration (C10 §6)

- AI review is additive — it supplements human review, never replaces it
- "Claude reviewed and approved" is never a justification in a team PR — Claude reviewed (L2); humans approve (L4)
- AI tools used in significant design decisions are documented in the PR description
- No AI tool is given access to production credentials, production database, or production deployment dashboards

---

*v1.0 — 2026-05-08 | Governed by C1, C0 §8.3, C10 Part 6*
