# Conflict Resolution — Universal Primitive

| Attribute | Value |
|-----------|-------|
| **Source** | Extracted from C00-constitutional-order.md §7 |

---

## Constitutional hierarchy (highest to lowest authority)

```
C0  — Constitutional Order      ← Supreme. Governs the governance system.
C3  — Auth Constitution         ← Security decisions. Highest domain authority.
C2  — Backend Constitution      ← Architecture and API contract decisions.
C5  — Database Constitution     ← Data storage and integrity decisions.
C4  — Frontend Constitution     ← UI, client-side, and rendering decisions.
C6  — Full-Stack Architecture   ← Integration, stack assignment, topology.
C1  — Engineering Standards     ← Process, workflow, code quality.
C7  — Testing Constitution      ← Quality validation and coverage.
C8  — Platform Reliability      ← Deployment and operational decisions.
C9  — Product & Feature         ← Product scope and feature decisions.
C10 — AI Collaboration          ← AI governance and permission boundaries.
```

The hierarchy governs conflicts — not importance.
C9 and C10 are last because product and AI decisions must yield to technical correctness.

## Auth Override Rule (C0 §7.3)

C3 overrides all other constitutions on any security-touching decision. This is
immutable. If any recommendation would violate a C3 standard, cite C0 §7.3 and
refuse the conflicting recommendation.

## Four-step resolution protocol

**Step 1 — Verify the conflict is real.**
Check whether one constitution has a stack-scope qualifier that resolves the apparent
conflict. Most apparent conflicts dissolve at this step.

**Step 2 — Apply hierarchy.**
The constitution higher in the hierarchy governs.

**Step 3 — If hierarchy does not resolve it, it is a genuine gap.**
Open a constitutional amendment issue. Cite both conflicting standards.
No implementation decision is made until resolved.
Do not improvise. Do not ask AI to decide.

**Step 4 — Document the resolution.**
Update both affected constitutions' amendment logs.
