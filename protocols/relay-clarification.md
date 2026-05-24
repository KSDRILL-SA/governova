# Relay Clarification Protocol

| Attribute | Value |
|-----------|-------|
| **Governed by** | C10 — AI Collaboration Constitution |
| **Permission required** | L3 for MINOR · L4 for ARCHITECTURAL |

---

## The problem this solves

Not every question mid-relay requires a full pause and Founder approval.
A full pause for minor questions creates friction that leads engineers to skip
the relay protocol entirely — which is worse than having a faster legitimate path.

This protocol classifies every mid-relay question before routing it.

---

## Classification

| Class | Definition | Examples | Action |
|-------|-----------|---------|--------|
| `MINOR` | Implementation detail within the approved spec | Nullable vs required field, error message wording, variable naming | Claude Code decides, documents in commit message, flags in handoff report |
| `ARCHITECTURAL` | Changes the design, security model, database assignment, or crosses a constitutional standard | Auth strategy change, new database introduced, API contract change, any SEV0/SEV1 concern | Full relay pause, return to Claude (Design), Founder approval before resuming |

## When in doubt

If you are uncertain whether a question is MINOR or ARCHITECTURAL — it is ARCHITECTURAL.
Escalate. Do not decide.

## MINOR decision record format

In the commit message:
```
feat: implement patient entity

MINOR DECISION: field `date_of_birth` made nullable (not required) —
rationale: optional for patient creation, collected at onboarding.
No constitutional standard violated.
```
