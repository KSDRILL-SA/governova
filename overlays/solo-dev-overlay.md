# Solo Dev Overlay — KSDRILL SA

---

| Attribute       | Value |
|-----------------|-------|
| **Document**    | Solo Dev Overlay |
| **Version**     | v1.0 |
| **Applies To**  | All Systems · Solo Operating Mode |
| **Overlay For** | C1 Engineering Standards — process standards only |

---

## What This Overlay Does

Constitutional standards are universal — they do not change based on operating mode. This overlay adapts **process standards** (how the work is organised and reviewed) for solo development context. The technical standards (S2.* through S10.*) apply identically regardless of mode.

This overlay is loaded after `AI-INSTRUCTIONS.md` and the system context file. It is active when the system context file shows `Operating Mode: SOLO`.

---

## Process Standard Adaptations

### S1.27 — Feature Proposal Review

| Standard Requirement | Solo Adaptation |
|---------------------|----------------|
| 24h open review period with team input | AI adversarial review (S10.3): Claude produces proposal → second AI stress-tests → document both responses → 24h personal review → self-approve with written reasoning in GitHub Issue |
| Evidence required | Same — build learnings, post-mortems, user research |
| Proposal format | Same — `templates/feature-proposal-template.md` |

### S1.28 — PR Description

| Standard Requirement | Solo Adaptation |
|---------------------|----------------|
| 2 reviewers assigned | Self-review checklist (S1.45) fully completed + AI code review session (S10.27) documented in PR description |
| All fields required | Same |

### S1.30 — 2-Approval Merge Rule

| Standard Requirement | Solo Adaptation |
|---------------------|----------------|
| 2 human approvals required | Self-review checklist (all 4 quadrants passed) + AI code review session (S10.27) documented + 24h cooling period before merge to main |
| Squash merge | Same |
| Clean commit message | Same |

### S1.12 — Async Standup

| Standard Requirement | Solo Adaptation |
|---------------------|----------------|
| Team-posted daily standup | Written dev log: `docs/dev-log/YYYY-MM-DD.md` — 3 questions: (1) What did I complete? (2) What am I working on today? (3) What is blocking me? |
| Visibility to team | Commit to main daily or reference in session start with Claude (S10.29) |

### S1.13 — Blocker Escalation

| Standard Requirement | Solo Adaptation |
|---------------------|----------------|
| Raise to team within 4 hours | Document in dev log + create GitHub Issue + tag for next session + Claude consulted on unblocking approach |
| Team response expected | Claude adversarial review of the blocker |

### Amendment Protocol (C0 §8)

| Team Requirement | Solo Fast-Path |
|-----------------|----------------|
| 48h open review | 24h personal review (solo equivalent) |
| Team discussion | AI adversarial review (S10.3) + document both outputs in GitHub Issue |
| Owner approval | Self-approve with documented evidence and reasoning |
| Same format | Same — GitHub Issue, commit, version bump, amendment log |

---

## Solo Dev Self-Review Checklist (S1.45 expanded)

Before opening any PR, complete all four quadrants:

**Quadrant 1 — Architecture**
- [ ] Does this change stay within the approved design in `CONSTITUTION-INDEX.md`?
- [ ] Are the correct layers involved? (Interface → Service → Component → UI per S4.79)
- [ ] Is business logic in the service layer, not the UI? (S2.1, S4.12)
- [ ] Does the database assignment match S5.1? (PostgreSQL for financial/auth, MongoDB for documents, ChromaDB for vectors)
- [ ] If this adds an endpoint, was the OpenAPI contract written first? (S2.7)

**Quadrant 2 — Code Quality**
- [ ] TypeScript strict — no `any` types? (S1.48)
- [ ] Explicit `select` on every Prisma query? (S5.11)
- [ ] `deleted_at: null` filter on all queries? (S5.12)
- [ ] Raw SQL is parameterised with comment? (S5.21, S5.19)
- [ ] No `console.log` in production code? (S4.27)
- [ ] All Zod/Pydantic validation on API boundaries? (S2.23)
- [ ] Decimal (not Float) for any monetary values? (S5.28)

**Quadrant 3 — Commits & Git**
- [ ] One commit per layer? (S4.80)
- [ ] Conventional commit format? (S1.17)
- [ ] No secret values in any committed file? (S3.20, CF-04)
- [ ] Branch is up to date with main?

**Quadrant 4 — Functionality & Tests**
- [ ] Tests written alongside the code in this PR? (S7.1, CF-10)
- [ ] Service function unit tests: success path + failure path? (S7.7)
- [ ] Auth tests: 200, 401, 403 for every protected endpoint? (S7.11)
- [ ] CI is green locally before opening PR?

**AI Review Step (S10.27)**
- [ ] Diff reviewed by Claude with constitutional violation prompt?
- [ ] Claude's review result documented in PR description?

---

## Solo Dev Session Template

Copy this at the start of every development session:

```markdown
## Session Start — {date}

**System:** {name}
**Sprint:** {N} — {goal}
**Active Feature:** {feature name}
**Active Group:** G{N}

**Previous session outcome:**
{from dev log — what was completed, what is in progress}

**Blockers from previous session:**
{any GitHub Issues opened for blockers}

**Today's goal:**
{specific, completable in this session}

**Constitutional context check:**
- [ ] AI-INSTRUCTIONS.md loaded
- [ ] system-contexts/{system}-context.md read
- [ ] CONSTITUTION-INDEX.md loaded in editor
- [ ] Operating mode: SOLO — solo-dev-overlay.md active
```

---

## Solo Dev AI Session Startup Prompt

Paste this to Claude at the start of every design/review session:

```
You are operating in SOLO dev mode for KSDRILL SA.
Read AI-INSTRUCTIONS.md and system-contexts/{system}-context.md.
The solo-dev-overlay.md is active.

I am working on: {description of today's task}
Active feature: {feature name} (C1 S1.27 proposal: {link})
Current layer: {Interface / Service / Component / UI}

Before we proceed:
1. Confirm CONSTITUTION-INDEX.md is loaded (S10.21)
2. Identify the 3-5 most critical standards for today's task
3. Flag any constitutional violations in the current codebase if I paste a diff

Ready to begin.
```

---

*v1.0 — 2026-05-08 | Governed by C1, C0 §8.2, C10 Part 5*
