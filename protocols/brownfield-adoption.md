# Brownfield Adoption Standard — Onboarding & Converting Existing Systems

| Attribute | Value |
|-----------|-------|
| **Document** | Brownfield Adoption Standard — existing-system onboarding, gap analysis & non-breaking conversion |
| **Layer** | Protocol (operationalises the constitution) |
| **Governed By** | C1 — Engineering Standards · C6 — Full-Stack Architecture · C8 — Platform Reliability |
| **Applies To** | Every existing system adopted into Governova · any stack · any domain · any organisation |
| **Status** | Active |
| **Paired With** | `protocols/github-workflow.md` · `constitution/indexes/stack-assignment-matrix.md` · GOVERNOVA-MASTER.md §14 (Mapping Engine) |

---

> *"Governova does not only govern systems built from scratch. It takes a system that already exists — however it was built — and converts it, without breaking anything, into the best and most complete version of itself."*

Greenfield is the easy half. **Most systems that need governance already exist.** This standard defines how Governova onboards a running, real-world system and brings it to full constitutional compliance **incrementally and non-destructively** — fixing what was never done right, covering every edge case, never breaking what already works.

---

## §1 — The Two Foundational Guarantees

Every brownfield adoption is bound by two non-negotiable guarantees:

1. **Non-breaking.** No conversion step may change observable behaviour of a working system unless that behaviour is itself the defect being fixed. Existing functionality is preserved at every step. There is no "big-bang rewrite."
2. **Complete.** Adoption is not finished when the system "mostly" complies. It is finished when every applicable standard is either satisfied, or carries a recorded, approved exception (`EXCEPTION-{ORG}-{DATE}`, GOVERNOVA-MASTER.md §14.3). Nothing is silently skipped.

These mirror the universal principles: *everything is documented or it did not happen*, and *human authority is non-negotiable* — a brownfield exception is an L4 decision.

---

## §2 — The Adoption Lifecycle (6 Phases)

```
0 INVENTORY  →  1 GAP ANALYSIS  →  2 REMEDIATION PLAN  →  3 SAFE CONVERSION  →  4 EDGE CASES  →  5 CONTINUOUS COMPLIANCE
```

### Phase 0 — Inventory & Baseline
Capture what actually exists before changing anything.
- Detect stack(s), frameworks, services, datastores, and **external dependencies** (see `external-governance` coverage).
- Map the repository structure, build/test/deploy pipelines, and environments.
- Record the **starting state** — including the current test coverage and a snapshot/tag for rollback (`baseline/pre-adoption`).

### Phase 1 — Constitutional Gap Analysis
Assess the system against its compiled `CONSTITUTION-INDEX` (Framework + Core + Implementation for the detected stack + Domains).
- For every applicable `S{C}.{N}`: **satisfied**, **violated**, or **not-applicable**.
- Each violation is classified by severity (SEV0–SEV3) and linked to its anti-pattern `AP-S{C}.{N}{letter}`.
- Output: a **baseline Governova Score**, a gap report, and a violation heatmap. This is the system's honest starting line — and the proof of improvement later.

### Phase 2 — Risk-Ranked Remediation Plan
Convert gaps into an ordered, safe plan.
- Sequence by **risk and dependency**, not by severity alone: a SEV1 gap whose fix is risky may be staged behind characterization tests first.
- **Security gaps (C3) are surfaced first** but fixed under the Auth Override discipline (C0 §7.3) — never rushed.
- Each remediation becomes a tracked issue → branch → PR (`protocols/github-workflow.md`). One gap (or one cohesive cluster) per PR. Never a sweeping rewrite.

### Phase 3 — Safe (Non-Breaking) Conversion
The heart of the standard. Every change preserves behaviour.
- **Characterization tests first.** Before refactoring untested code, write tests that pin its *current* behaviour. Refactor only once behaviour is pinned. (Proposed `S1.101`.)
- **Strangler-fig over rewrite.** Introduce the compliant path alongside the legacy path; migrate traffic incrementally; remove the legacy path only when the new one is proven.
- **Behaviour-preserving steps.** Each PR is small, reversible, green on all checks, and individually deployable.
- **Feature-flag risky cutovers** and keep the matching rollback runbook ready (`governance/runbooks/`).

### Phase 4 — Edge-Case Handling
Brownfield is where the edge cases live (§4). Each is identified, governed, and resolved or formally excepted — never ignored.

### Phase 5 — Continuous Compliance
- Backfill the **System Bible** (Why/How/Failure/Fix) for converted files as they are touched — documentation as a byproduct, retroactively.
- Track the Governova Score trend from baseline upward.
- Remaining gaps that cannot yet be fixed carry an approved exception with a scheduled review date.

---

## §3 — Greenfield vs Brownfield (What Changes)

| Concern | Greenfield | Brownfield |
|---------|-----------|------------|
| Starting point | Empty repo | Running system with real users/data |
| Standards applied | From the first commit | Retroactively, by gap analysis |
| Primary risk | Wrong pattern embedded early | **Breaking working behaviour during conversion** |
| Test posture | Tests written with the code | **Characterization tests written before refactor** |
| Change unit | Feature | Behaviour-preserving remediation step |
| "Done" | Feature ships compliant | Every gap satisfied or formally excepted |
| Score | Starts high | Starts at the honest baseline, climbs |

The **framework and constitution do not change** — only the *order of application* (retroactive) and the *safety discipline* (non-breaking) differ.

---

## §4 — Edge-Case Register (non-exhaustive)

| Edge case | Governed handling |
|-----------|-------------------|
| No tests / untested behaviour | Characterization tests before any refactor (`S1.101` proposed) |
| Undocumented or accidental behaviour | Pin via tests; treat as spec until an L4 decision changes it |
| Legacy / unsupported framework version | Temporal governance flags it; remediation plan schedules a governed upgrade |
| Mixed or multiple stacks in one system | Compile a multi-stack CONSTITUTION-INDEX; apply each stack's bindings to its part |
| Partially-migrated / in-flight refactor | Adopt current state as baseline; do not fight an in-progress migration — fold it into the plan |
| Vendored / third-party code in-tree | Govern the integration boundary, not the vendor's internals (external-governance) |
| Generated code | Govern the generator config + output contract, not the generated artifact line-by-line |
| Monorepo / many services | Per-package CONSTITUTION-INDEX; Score rolls up per service |
| Production data / migrations involved | Database migration runbook (`RB-04`); never a destructive migration without rollback |
| Hard external constraints (compliance, contracts) | Recorded exception with rationale, approver, review date |

---

## §5 — Outputs of an Adoption

1. **Baseline report** — starting Governova Score + gap heatmap (the honest starting line).
2. **Remediation roadmap** — risk-ranked, issue-tracked plan.
3. **A series of small, non-breaking PRs** — each green, reversible, individually deployable.
4. **Backfilled System Bible** — explanation generated as files are converted.
5. **Exception register** — every unfixable gap recorded and scheduled for review.
6. **Rising Score trend** — provable improvement from baseline to compliant.

---

## §6 — Platform Support (where this is automated)

The adoption lifecycle is the human-and-AI protocol. The platform automates parts of it:

- **Gap analysis** — the engine's Violation Detector runs the full `CONSTITUTION-INDEX` against the existing codebase to produce the baseline (`platform/engine/violation-detector/`).
- **Pre-build / pre-adoption risk assessment** — GOVERNOVA-MASTER.md §15.3.
- **Mapping Engine** — for organisations with their *own* existing standards, maps them to the Governova index in their language (§14) so adoption enhances their policies rather than replacing them.
- **System Knowledge Engine** — backfills the four documentation layers for converted files.

---

## §7 — Constitutional Mapping & Proposed Standards

Governed by C1 (engineering discipline), C6 (architecture/stack assignment for the detected stack), and C8 (reliability — safe change, rollback).

Proposed backing standards (pending C0 §8 ratification — L4), logged in `governance/changelog/amendments-log.md`:

| Proposed ID | Title |
|-------------|-------|
| `S1.101` (proposed) | Characterization tests pin current behaviour before any brownfield refactor |
| `S6.45` (proposed) | Brownfield adoption is incremental and non-breaking — no big-bang rewrite; strangler-fig migration |
| `S8.83` (proposed) | Every brownfield conversion step is individually reversible with a ready rollback path |
| `S1.102` (proposed) | Adoption is complete only when every applicable standard is satisfied or carries an approved exception |

Until ratified, this document is operational guidance with the force of an active protocol; the standards above are proposals for Founder (L4) ratification.
