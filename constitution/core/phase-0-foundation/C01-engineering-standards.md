# C1 — Engineering Standards Constitution

---

| Attribute          | Value                                                              |
|--------------------|--------------------------------------------------------------------|
| **Document**       | C1 — Engineering Standards Constitution                            |
| **Organisation**   | KSDRILL SA                                                         |
| **Version**        | v1.5                                                               |
| **Status**         | LOCKED                                                             |
| **Locked**         | 2026-05-08 (originally); last amended 2026-07-30                   |
| **Next Review**    | 2026-08-08                                                         |
| **Applies To**     | All Systems · Both Stacks · Solo Dev · Team                        |
| **Paired With**    | — (Process and quality document — no implementation guide)         |

---

> *"The engineer who cannot explain every decision they made is not an engineer —
> they are a typist with a compiler."*

---

## Opening Statement

Engineering Standards is the first constitution read and the foundation upon which every
other constitution rests. It governs two things that must be true before a single line of
application code is written: how engineers work together (or alone), and how code is
written regardless of who writes it or which system it belongs to.

This constitution does not govern architecture, database choices, authentication strategy,
or deployment. Those are governed by Phase 1 and Phase 2 constitutions. What this
constitution governs is the discipline that makes those constitutions enforceable in
practice — the sprint cadence, the feature lifecycle, the Git workflow, the code quality
baseline, and the communication standards that turn a set of technical rules into a
functioning engineering system.

This document is the result of merging three previously separate documents — the Team &
Process Constitution, the Code Quality Constitution, and the engineering workflow
intelligence extracted from the MentorConnect team collaboration system — into a single
authoritative source. These three were always read together. Keeping them separate created
split-brain on the question every engineer must answer before opening a PR: *"Is this done?"*
This constitution answers that question completely.

This constitution applies identically to solo development and team development. Where the
process implementation differs between contexts, the solo-dev-overlay and team-overlay
documents provide the adaptation. The standards themselves do not branch.

---

## Table of Contents

| Part | Title | Standards |
|------|-------|-----------|
| Part 1 | Build Philosophy | S1.1–S1.5 |
| Part 2 | Sprint & Planning | S1.6–S1.10 |
| Part 3 | Communication Standards | S1.11–S1.15 |
| Part 4 | Git & Branching | S1.16–S1.24 |
| Part 5 | Constitutional Governance | S1.25–S1.26 |
| Part 6 | Feature Lifecycle | S1.27–S1.40 |
| Part 7 | Non-Negotiable Engineering Standards | S1.41–S1.44 |
| Part 8 | Author Quality Gates | S1.45–S1.47 |
| Part 9 | TypeScript Standards | S1.48–S1.56 |
| Part 10 | Python Standards | S1.57–S1.63 |
| Part 11 | File & Module Structure | S1.64–S1.69 |
| Part 12 | Linting & Formatting | S1.70–S1.74 |
| Part 13 | Code Review Standards | S1.75–S1.82 |
| Part 14 | Documentation Standards | S1.83–S1.87 |
| Part 15 | Angular-Specific Quality | S1.88–S1.92 |
| Part 16 | Git Recovery Procedures | S1.93–S1.97 |
| Part 17 | Dependency & Build Reproducibility | S1.98 |


---

## Part 1 — Build Philosophy (`S1.1`–`S1.5`)

Build philosophy standards define the mindset under which all other standards operate.
They are not abstract principles — they are engineering decisions that determine whether
a system is buildable, debuggable, and maintainable after the first sprint.

---

### S1.1 — Design First, Then Build

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.1 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | — |
| **Enforced By** | Feature Lifecycle gate (S1.27) · Code Review |

**Standard:**
No application code is written before the design for that feature or system is complete,
reviewed, and approved. Design includes: user flows, module boundaries, database schema,
API contracts, and component interfaces. A feature proposal that cannot answer all seven
fields of the proposal template (S1.29) is not a complete design.

**Rationale:**
Code written before design is complete embeds the designer's assumptions into the
implementation. Those assumptions are expensive to reverse once they exist as running code.
Every rewrite situation traces back to implementation that began before the design was
validated.

**Anti-Patterns:**
- `AP-S1.1a` — Opening a feature branch before the proposal is approved and a GitHub Issue is linked.
- `AP-S1.1b` — Writing "exploratory code" to understand the design in a feature branch.

**Cross-References:** `S1.27` (feature proposal gate), `S2.7` (OpenAPI before endpoint), `S4.81` (layer build order)

---

### S1.2 — Understand Before Implementing

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.2 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.1` (design first) |
| **Enforced By** | Feature Lifecycle gate check (S1.28) |

**Standard:**
Before writing code for any feature, the engineer must be able to trace the complete data
flow — from user interaction through frontend, service layer, API, database, and back —
without referring to code. The engineer must know which layers are involved, which
databases are touched and why, and where each piece of logic belongs. If this trace
cannot be completed, the feature is not understood and must not be implemented.

**Rationale:**
An engineer who cannot trace the data flow before coding will embed that confusion into
the implementation — logic in the wrong layer, wrong database, violated boundaries.
These decisions are far harder to fix than they are to get right at design time.

**Anti-Patterns:**
- `AP-S1.2a` — Starting implementation with intent to figure out the data flow as you go.
- `AP-S1.2b` — Asking AI to decide where logic belongs without being able to evaluate the answer against constitutional layer standards.

**Cross-References:** `S1.28` (gate check questions), `S2.1` (backend layer separation), `S4.1` (frontend architecture)

---

### S1.3 — One Concern Per Unit

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.3 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.2` (understand before implementing) |
| **Enforced By** | Code Review · ESLint · Semantic tier |

**Standard:**
Every unit of code — function, component, service, module, branch, commit, and PR — has
exactly one concern. A function that does two things is two functions. A commit that
touches two features is two commits. A PR that covers two concerns is two PRs.

**Rationale:**
Single-concern units are independently testable, deployable, and debuggable. When a
production failure occurs, the failure surface of a single-concern unit is predictable.
Mixed-concern units produce failures whose root cause is untraceable without reading the
entire unit.

**Anti-Patterns:**
- `AP-S1.3a` — A PR that adds a feature and fixes an unrelated bug.
- `AP-S1.3b` — A service function that queries the database AND formats AND logs.
- `AP-S1.3c` — A commit message using "and" to describe what changed.

**Cross-References:** `S1.16` (one concern per branch), `S1.33` (one concern per commit), `S1.36` (one concern per PR)

---

### S1.4 — Stack Decisions Are Immutable Within a Major Version

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.4 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S6.1` (stack assignment standard) |
| **Enforced By** | Constitutional Order §10 · ADR process |

**Standard:**
Once a stack is assigned to a system via the ADR process, that assignment is immutable
for the lifetime of that system's major version. No framework, library, language, or
architecture pattern may be changed mid-build without a Major constitutional amendment
to C6, a new ADR, and a full constitutional review.

**Rationale:**
Stack changes mid-build invalidate the constitutional standards applied to every prior
decision. A system that starts as Angular and switches to Next.js mid-sprint is not
correctly governed by either set of standards. Every prior architectural decision must
be re-evaluated. This is a rewrite, not a refactor.

**Anti-Patterns:**
- `AP-S1.4a` — "We'll just use Next.js for this one feature" on an Angular system.
- `AP-S1.4b` — Switching frameworks because a new version was released or someone has more experience elsewhere.

**Cross-References:** `S6.1` (stack assignment), `S6.5` (ADR process), `CF-12` (common failure)

---

### S1.5 — Controlled Imperfection Over Incomplete Perfection

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.5 |
| **Priority**    | Standard |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | — |
| **Enforced By** | Code Review · Retrospective |

**Standard:**
A working, tested, constitutional system with known limitations is always preferred over
an incomplete system that attempts perfection. Failures must be predictable, traceable,
and documented. The goal is not zero defects — it is zero surprises. Every known
limitation is documented. Every known failure mode has a runbook. Every incident produces
a post-mortem that improves the system.

**Rationale:**
The pursuit of perfection before shipping produces systems that never ship and teams that
lose confidence. Controlled imperfection means the system is in production, failures are
caught by monitoring, and each incident makes the system stronger through the closed-loop
learning process.

**Anti-Patterns:**
- `AP-S1.5a` — Holding a passing, tested feature from production because it is not "fully polished."
- `AP-S1.5b` — Skipping the post-mortem because "we already fixed it."

**Cross-References:** `S8.39` (post-mortem protocol), `S9.8` (MVP definition)


---

## Part 2 — Sprint & Planning (`S1.6`–`S1.10`)

Sprint standards govern the rhythm of delivery. They define how work is structured, how
capacity is measured, and how the team — or solo developer — maintains velocity without
accumulating invisible debt.

---

### S1.6 — Sprint Duration Is Fixed at Two Weeks

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.6 |
| **Priority**    | Standard |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | — |
| **Enforced By** | GitHub Project Board · Sprint Retrospective |

**Standard:**
Every sprint runs for exactly two weeks. Sprint duration does not change based on scope,
deadline pressure, or team size. If scope cannot fit in two weeks, it is reduced — not
the sprint length.

**Anti-Patterns:**
- `AP-S1.6a` — Extending a sprint because tickets are incomplete. Incomplete tickets roll over.
- `AP-S1.6b` — Running a one-week sprint for "urgent delivery."

**Cross-References:** `S1.7` (ticket sizing), `S1.10` (retrospective)

---

### S1.7 — Tickets Are Sized Before Sprint Start

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.7 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.6` (fixed sprint duration) |
| **Enforced By** | Sprint Planning · GitHub Issues |

**Standard:**
Every ticket committed to a sprint is sized before the sprint begins using T-shirt sizes:
XS (half a day), S (one day), M (two to three days), L (requires breakdown — not accepted
as a single ticket). An L ticket signals that S1.1 (Design First) was not followed.

**Anti-Patterns:**
- `AP-S1.7a` — Accepting an L ticket into a sprint as-is.
- `AP-S1.7b` — Sizing tickets during the sprint rather than before.

**Cross-References:** `S1.6` (sprint duration), `S1.29` (proposal — where sizing originates)

---

### S1.8 — Sprint Capacity Is Explicitly Set

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.8 |
| **Priority**    | Standard |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.7` (ticket sizing) |
| **Enforced By** | Sprint Planning |

**Standard:**
Sprint capacity is set at the start of each sprint based on available working days,
accounting for known leave, public holidays, and recurring overhead. Total ticket sizes
committed must not exceed capacity. Reserve minimum 20% for review, constitutional
compliance, and unexpected complexity. Overcommitment is a planning failure.

**Anti-Patterns:**
- `AP-S1.8a` — Assuming 100% capacity is available for feature development.
- `AP-S1.8b` — Adding tickets mid-sprint without removing equivalent capacity.

---

### S1.9 — Blockers Are Raised Within Four Hours

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.9 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.11` (async standup) |
| **Enforced By** | Communication Standards · Team Channel |

**Standard:**
Any blocker — technical, constitutional, dependency, or access — is raised within four
hours of being identified. A blocker is anything that prevents progress for more than two
hours. Blockers are never held until the next standup. In solo context, blockers are
documented in the dev log and a GitHub Issue is created immediately.

**Anti-Patterns:**
- `AP-S1.9a` — Continuing to work around a blocker without raising it.
- `AP-S1.9b` — Raising a blocker in a private message rather than the team channel.

**Cross-References:** `S1.11` (standup), `S1.12` (correct channel)

---

### S1.10 — Sprint Retrospective Is Mandatory

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.10 |
| **Priority**    | Standard |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.6` (sprint completion) |
| **Enforced By** | Sprint-retro-template · Post-sprint review |

**Standard:**
Every sprint ends with a retrospective using the sprint-retro-template addressing: what
shipped, what did not ship and why, one process improvement to carry forward, and whether
any constitutional gaps were identified. Constitutional gaps are converted into GitHub
Issues for the amendment protocol.

**Anti-Patterns:**
- `AP-S1.10a` — Skipping the retrospective because "everything went fine."
- `AP-S1.10b` — Conducting a retrospective without documenting the outcome.

**Cross-References:** `S1.5` (controlled imperfection), `C0 §8` (amendment protocol)

---

## Part 3 — Communication Standards (`S1.11`–`S1.15`)

Communication standards define how information moves through the team and how the solo
developer maintains the discipline of explicit communication — even with themselves.
Silent assumptions are the primary cause of misaligned implementations.

---

### S1.11 — Async Standup Replaces Synchronous Daily Meetings

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.11 |
| **Priority**    | Standard |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | — |
| **Enforced By** | Team Channel · Dev Log (solo) |

**Standard:**
Daily standups are conducted asynchronously. Every working day, each engineer posts three
standup answers: (1) What did I complete since the last standup? (2) What am I working
on today? (3) What is blocking me? Posted at the start of the working day. In solo
context, written in `docs/dev-log/YYYY-MM-DD.md`.

**Anti-Patterns:**
- `AP-S1.11a` — Posting standup at end of day as a summary of completed work.
- `AP-S1.11b` — Skipping standup because "nothing changed."

**Cross-References:** `S1.9` (blocker escalation), `S1.12` (communication channels)

---

### S1.12 — Communication Channels Are Purpose-Defined

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.12 |
| **Priority**    | Standard |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | — |
| **Enforced By** | Team Process |

**Standard:**
Each channel has a defined purpose. Architectural decisions live in GitHub Issues or PR
comments — never in direct messages. Blockers go to the team channel immediately. Code
questions go to the PR thread. Direct messages are for personal, non-technical
communication only. In solo context, all decisions are in GitHub Issues or the dev log.

**Anti-Patterns:**
- `AP-S1.12a` — Resolving a review disagreement via DM without documenting in the PR thread.
- `AP-S1.12b` — Making an architectural decision in chat without capturing it in GitHub.

**Cross-References:** `S1.9` (blocker channel), `C0 §8` (amendment decisions in GitHub)

---

### S1.13 — Technical Disagreements Are Resolved With Evidence

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.13 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.12` (correct channel) |
| **Enforced By** | Code Review · Constitutional Hierarchy |

**Standard:**
Technical disagreements are resolved by citing the relevant constitutional standard. If a
standard exists that governs the disputed decision, the standard resolves the dispute —
no further discussion. If no standard exists, an amendment proposal is opened. Preference,
seniority, and volume of argument are not valid resolution mechanisms.

**Anti-Patterns:**
- `AP-S1.13a` — Overriding a standard because a senior engineer disagrees with it.
- `AP-S1.13b` — Leaving a technical disagreement unresolved in a PR thread.

**Cross-References:** `C0 §7` (conflict resolution), `C0 §8` (amendment protocol)

---

### S1.14 — Review Response Time Is 24 Hours

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.14 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.47` (review response protocol) |
| **Enforced By** | Team Process |

**Standard:**
All review requests — PR reviews and proposal reviews — receive a response within 24 hours.
A response is an acknowledgement of receipt and a timeline for the full review. Silence
for more than 24 hours is a process failure that blocks the submitter's sprint progress.

**Anti-Patterns:**
- `AP-S1.14a` — Waiting to review a PR until a synchronous meeting happens.
- `AP-S1.14b` — Reviewing a PR weeks after it was opened.

**Cross-References:** `S1.47` (author response protocol), `S1.75` (reviewer standards)

---

### S1.15 — Decisions Are Documented Before They Are Implemented

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.15 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.12` (correct channel) |
| **Enforced By** | ADR Process · GitHub Issues · Code Review |

**Standard:**
Every significant technical decision — stack assignment, database choice, library
selection, architecture pattern — is documented in a GitHub Issue or ADR before it is
implemented. "Significant" is defined as: any decision that would require a constitutional
amendment to reverse.

**Anti-Patterns:**
- `AP-S1.15a` — A significant decision implemented before it is written down — the reasoning exists only in the head of whoever made it, and reversing it later costs an amendment nobody can argue against a record that was never kept.

**Cross-References:** `S6.5` (ADR process), `S1.85` (ADR standard), `C0 §8` (amendment)


---

## Part 4 — Git & Branching (`S1.16`–`S1.24`)

Git standards define how code moves from a developer's machine to the main branch. A clean
Git history is a debugging tool. A structured commit log is a deployment audit trail.

---

### S1.16 — Branch Naming Follows Conventional Format

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.16 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.3` (one concern per branch) |
| **Enforced By** | CI Branch Name Check · Code Review |

**Standard:**
All branches follow the format `{type}/{scope}-{short-description}`. Valid types: `feat`,
`fix`, `chore`, `docs`, `refactor`, `test`, `hotfix`. The scope matches the system or
module. The description is lowercase, hyphenated, 50 characters maximum.

**Correct examples:**
```
feat/auth-jwt-refresh-rotation
fix/dashboard-mobile-overflow
hotfix/financial-calc-rounding-error
```

**Anti-Patterns:**
- `AP-S1.16a` — Branch named `my-feature`, `fix`, `dev/test` — no type prefix or descriptive scope.
- `AP-S1.16b` — Branch name containing "and" — signals multiple concerns.

**Cross-References:** `S1.3` (one concern), `S1.19` (conventional commits)

---

### S1.17 — Main Branch Is Always Deployable

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.17 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.22` (squash merge), `S7.1` (tests pass) |
| **Enforced By** | Branch Protection Rules · CI Pipeline |

**Standard:**
The `main` branch is protected and always in a deployable state. Direct pushes to `main`
are disabled at the repository level. Every change enters through a reviewed, CI-passing
PR. The CI pipeline gates must include: lint, type-check, unit tests, and integration
tests. A `main` branch that fails CI is a SEV1 incident.

**Anti-Patterns:**
- `AP-S1.17a` — Disabling branch protection "temporarily" to push a hotfix directly.
- `AP-S1.17b` — Merging a PR while CI is failing with intent to "fix it next commit."

**Cross-References:** `S1.22` (squash merge), `S1.24` (hotfix process), `CF-04`

---

### S1.18 — Branch Lifetime Is One Feature or Fix

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.18 |
| **Priority**    | Standard |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.3` (one concern per branch) |
| **Enforced By** | Code Review · Post-merge cleanup (S1.23) |

**Standard:**
A branch exists for exactly one feature, fix, or chore. Created from `main`, developed
against, merged via PR, and immediately deleted both remotely and locally. Long-lived
feature branches signal a feature that was not scoped correctly or a PR not reviewed
within the 24-hour standard.

**Anti-Patterns:**
- `AP-S1.18a` — A branch accumulating more than one sprint's worth of commits.
- `AP-S1.18b` — Keeping a merged branch alive "in case we need to reference it."

**Cross-References:** `S1.3` (one concern), `S1.23` (post-merge cleanup)

---

### S1.19 — Commits Follow Conventional Commit Format

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.19 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.3` (one concern per commit) |
| **Enforced By** | Structural probe (`governova evidence`) · Commitlint where configured |

**Standard:**
Every commit follows: `{type}({scope}): {description}` — present tense, imperative mood,
lowercase. Valid types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `style`,
`perf`, `ci`, `govern`, `decision`. Commit messages do not use "and" — if "and" is
needed, there are too many concerns in the commit.

Two types name governance acts that change no code and therefore fit none of the others:

| Type | Use |
|------|-----|
| `govern` | A constitutional amendment — ratifying, amending, or repealing a standard. |
| `decision` | Recording an architectural decision (an ADR). |

Security work is **not** a type. A change that closes a vulnerability is a `fix`; work
that reduces exposure without fixing a defect is a `chore` or a `refactor`.

**Correct examples:**
```
feat(auth): add refresh token rotation on every request
fix(student-service): correct GPA calculation rounding
refactor(scholarship-model): extract eligibility scoring logic
chore(deps): upgrade Prisma to 5.12.0
govern: ratify Part 19 — Architectural Discipline (S1.103–S1.107)
decision: platform architecture — 3-plane model (ADR-005)
```

**Anti-Patterns:**
- `AP-S1.19a` — Messages: `"updates"`, `"fix stuff"`, `"wip"`, `"temp"`.
- `AP-S1.19b` — One giant commit per feature containing all layers.
- `AP-S1.19c` — Past tense: `"added refresh token"` — correct form: `"add refresh token"`.

**Cross-References:** `S1.3` (one concern), `S1.33` (commit per layer)

---

### S1.20 — First Push Uses Upstream Tracking

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.20 |
| **Priority**    | Standard |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.16` (branch naming) |
| **Enforced By** | Git Workflow · Developer Practice |

**Standard:**
The first push from a new local branch always uses: `git push -u origin {branch-name}`.
Subsequent pushes use `git push` only. This establishes upstream tracking and eliminates
the class of Git errors produced by missing `-u` on first push.

**Anti-Patterns:**
- `AP-S1.20a` — Using `git push origin {branch-name}` on every push without establishing tracking.

**Cross-References:** `S1.16` (branch naming), `S1.21` (branch sync)

---

### S1.21 — Main Sync Before PR Submission

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.21 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.17` (main always deployable) |
| **Enforced By** | PR Checklist · CI |

**Standard:**
Before opening a PR, sync the feature branch with latest `main`. Procedure: push current
branch → switch to `main` → `git pull` → switch back to feature branch → `git merge main`
→ resolve conflicts locally → push the updated branch. A PR opened against a stale `main`
produces untrustworthy CI results.

**Anti-Patterns:**
- `AP-S1.21a` — Opening a PR and investigating CI failures before syncing main first.

**Cross-References:** `S1.17` (main deployable state), `S1.46` (PR description)

---

### S1.22 — Squash Merge Is the Mandatory Merge Strategy

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.22 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.19` (conventional commits), `S1.17` (clean main) |
| **Enforced By** | GitHub Repository Settings · PR Merge Button |

**Standard:**
All PRs are merged using squash merge. The squash commit message is written manually at
merge time in conventional commit format — not auto-generated from the PR title. Merge
commits and rebase merges are disabled at the repository level.

**Rationale:**
Squash merge keeps `main`'s history clean, linear, and meaningful. Each commit represents
one complete, reviewed, deployable change. Regular merge commits produce a tangled history
that is difficult to bisect during incident investigation.

**Anti-Patterns:**
- `AP-S1.22a` — Using the auto-generated squash message from GitHub.
- `AP-S1.22b` — Using merge commit to "preserve the feature branch history."

**Cross-References:** `S1.19` (commit format), `S1.23` (post-merge cleanup)

---

### S1.23 — Post-Merge Cleanup Is Mandatory

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.23 |
| **Priority**    | Standard |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.22` (squash merge complete) |
| **Enforced By** | Developer Practice · GitHub Branch Auto-delete |

**Standard:**
Immediately after PR merge, execute in full: (1) Delete remote branch on GitHub — enable
auto-delete in repo settings. (2) Switch local to `main`. (3) `git pull`. (4) Delete
local feature branch: `git branch -d {branch}`. (5) Verify feature in staging before
closing the GitHub Issue.

**Anti-Patterns:**
- `AP-S1.23a` — Skipping local branch deletion.
- `AP-S1.23b` — Closing the GitHub Issue before verifying in staging.

**Cross-References:** `S1.22` (squash merge), `S1.40` (staging verification)

---

### S1.24 — Hotfixes Follow an Abbreviated But Complete Process

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.24 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.16` (branch naming), `S1.17` (main protection) |
| **Enforced By** | Incident Response Protocol · Branch Protection |

**Standard:**
A hotfix uses a `hotfix/` branch created from `main`. Skips the proposal requirement and
24-hour review wait — does NOT skip self-review checklist, CI gate, or PR review. Minimum
one approval required before merge even during a production incident. Post-mortem written
within 24 hours after merge per S8.39.

**Anti-Patterns:**
- `AP-S1.24a` — Pushing directly to `main` during a production incident.
- `AP-S1.24b` — Skipping the post-mortem because the hotfix resolved the incident.

**Cross-References:** `S1.17` (main protection), `S1.45` (self-review), `S8.39` (post-mortem), `CF-04`

---

## Part 5 — Constitutional Governance (`S1.25`–`S1.26`)

Constitutional governance standards define how engineers engage with the constitutional
system itself — how they read it, reference it, and contribute to its evolution.

---

### S1.25 — Constitutions Are Read Before Each Phase Begins

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.25 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `C0 §11` (pre-build checklist) |
| **Enforced By** | Pre-Build Checklist · Code Review |

**Standard:**
Every constitution relevant to the current build phase is read in full before development
begins for that phase. The pre-build checklist in C0 §11 is the verification mechanism.
Engineers re-read amended sections before any sprint that touches the amended standard's domain.

**Anti-Patterns:**
- `AP-S1.25a` — Reading only the parts of a constitution that seem relevant.
- `AP-S1.25b` — Reading constitutions once at project start and never again after amendments.

**Cross-References:** `C0 §11` (pre-build checklist), `C0 §6` (phase map)

---

### S1.26 — Constitutional Gaps Are Raised, Not Improvised

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.26 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `C0 §8` (amendment protocol) |
| **Enforced By** | Code Review · Retrospective |

**Standard:**
When a decision is not covered by any existing constitutional standard, the engineer does
not improvise. They document the gap in a GitHub Issue tagged `constitutional-amendment`,
implement the most conservative option available under existing standards, and flag the
gap in their PR description.

**Anti-Patterns:**
- `AP-S1.26a` — Making an ungoverned technical decision without raising it as a gap.
- `AP-S1.26b` — Asking AI to fill a constitutional gap without raising an amendment.

**Cross-References:** `C0 §8` (amendment protocol), `S10.6` (AI cannot fill gaps)


---

## Part 6 — Feature Lifecycle (`S1.27`–`S1.40`)

The Feature Lifecycle is the most operationally detailed part of this constitution. It
defines the exact 8-phase journey every feature takes from idea to production. No feature
skips phases. No phase has optional steps. The Phase 0 gate check — the "do not touch
code yet" checkpoint — is the single most failure-preventing standard in this constitution.

---

### S1.27 — Feature Lifecycle Has Eight Mandatory Phases

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.27 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.1` (design first), `S1.2` (understand first) |
| **Enforced By** | Feature Proposal Review · PR Checklist · Code Review |

**Standard:**
Every feature — regardless of size, priority, or urgency — completes all eight phases in
sequence. No phase is skipped.

| # | Phase | Gate |
|---|-------|------|
| 0 | Receive & Understand | Gate check questions answered without code |
| 1 | Proposal | All 7 fields complete and approved |
| 2 | Branch Setup | Branch created after approval only |
| 3 | Implement in Layer Order | Interface → Service → Component → UI |
| 3B | Commit Per Layer | One commit per layer — not one giant commit |
| 4 | Self-Review | All 4 quadrants of checklist complete |
| 5 | PR Submission | All PR fields complete, screenshots attached |
| 6 | Review Cycle | Author responds within 24 hours |
| 7 | Merge & Close | Squash merge, cleanup, staging verification |

A feature that skips Phase 0 and Phase 1 is a PR that is automatically rejected
regardless of code quality.

**Anti-Patterns:**
- `AP-S1.27a` — Opening a branch before Phase 1 (proposal) is approved.
- `AP-S1.27b` — Combining all layers into one commit at the end instead of committing per layer.

**Cross-References:** `S1.28`–`S1.40` (each phase defined), `S1.45` (self-review — Phase 4)

---

### S1.28 — Phase 0: Gate Check Questions Are Mandatory

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.28 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.27` (lifecycle), `S1.2` (understand) |
| **Enforced By** | Feature Proposal Review |

**Standard:**
Before writing a single line of code or opening a branch, the engineer answers all gate
check questions without referring to existing code. If any cannot be answered, the feature
is not understood and Phase 1 cannot begin:

1. Can I trace the complete data flow from user interaction to database and back?
2. Do I know which layers are involved and in what sequence?
3. Do I know which database(s) this feature touches, and can I cite the S5 standard that justifies each choice?
4. Do I know where this logic does NOT belong, and can I cite the standard that governs the boundary?
5. Do I know what the error, loading, and empty states look like?
6. Do I know the acceptance criteria — how will I confirm this feature works?

**Anti-Patterns:**
- `AP-S1.28a` — Answering "yes" to the gate check without being able to provide the specific answer.

**Cross-References:** `S1.27` (lifecycle), `S1.2` (understand before implementing), `S5.1` (database assignment)

---

### S1.29 — Phase 1: Feature Proposal Uses the Mandatory Template

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.29 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.28` (gate check passed) |
| **Enforced By** | Proposal Review · PR Rejection Protocol |

**Standard:**
Every feature begins with a written proposal using `feature-proposal-template.md`. All
seven fields are required. A proposal with missing fields is returned without review.

| Field | Requirement |
|---|---|
| **Feature Name** | One-line identifier — matches the GitHub Issue title |
| **Problem Statement** | What user problem this solves. No solution language. |
| **Proposed Solution** | Plain English implementation plan. No code. |
| **Architecture Map** | Which systems, services, layers, and components are involved |
| **Data Models** | Which models are consumed or created. Schema changes noted. |
| **Edge Cases** | Error states, loading states, empty states, boundary conditions |
| **Acceptance Criteria** | Measurable conditions that confirm the feature is complete |

**Anti-Patterns:**
- `AP-S1.29a` — Proposal with placeholder text ("TBD", "N/A", "see code") in any field.
- `AP-S1.29b` — Proposal written after the code — text matching implementation is evidence of this.

**Cross-References:** `S1.27` (lifecycle), `S1.28` (gate check), `templates/feature-proposal-template.md`

---

### S1.30 — Phase 1: Proposal Approval Before GitHub Issue Opens

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.30 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.29` (proposal complete) |
| **Enforced By** | Team Process · Solo Overlay Protocol |

**Standard:**
A proposal must receive approval before a GitHub Issue is opened and before a branch is
created. In team context: 24-hour discussion window, revisions if required, one senior
approval confirms readiness. In solo context: AI adversarial review per solo-dev-overlay.
Immutable order: proposal → review → approval → issue → branch.

**Anti-Patterns:**
- `AP-S1.30a` — Creating the GitHub Issue and branch simultaneously with the proposal "to save time."

**Cross-References:** `S1.29` (proposal), `S1.31` (branch setup), `solo-dev-overlay.md`

---

### S1.31 — Phase 2: Branch Created After Approval Only

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.31 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.30` (proposal approved) |
| **Enforced By** | Git Workflow |

**Standard:**
Feature branch is created only after proposal approval and GitHub Issue is open. Created
from `main`, named per S1.16, immediately pushed with `git push -u origin {branch-name}`
(S1.20) and linked to the Issue.

**Anti-Patterns:**
- `AP-S1.31a` — Creating a branch from another feature branch rather than from `main`.

**Cross-References:** `S1.16` (branch naming), `S1.20` (first push), `S1.30` (approval)

---

### S1.32 — Phase 3: Implementation Follows Layer Order

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.32 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S1.31` (branch exists), `S4.81` (layer order) |
| **Enforced By** | Code Review · Commit History |

**Standard:**
Implementation follows the constitutional layer order without deviation.

**Next.js stack:** TypeScript interface / Zod schema → API route / service function → React smart component → React presentational component → tests.

**Angular + FastAPI stack:** Pydantic model → FastAPI route and service → Angular service → Angular smart component → Angular presentational component → tests.

UI is always last. Tests are written alongside each layer as it is completed — not after all layers exist.

**Rationale:**
Building UI first produces components that drive data shape decisions — which is backwards.
The data contract defines what the system stores and transmits. The service layer defines
how it moves. The component layer defines how it is presented. Reversing this order
corrupts the data contract.

**Anti-Patterns:**
- `AP-S1.32a` — Building the UI component first because "it's easier to see what you're building."
- `AP-S1.32b` — Writing all tests at the end after all layers are complete.

**Cross-References:** `S4.81` (layer build order — frontend), `S1.33` (commit per layer), `S7.1` (tests alongside)

---

### S1.33 — Phase 3B: One Commit Per Layer

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.33 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.32` (layer order), `S1.19` (conventional commits) |
| **Enforced By** | Commit History · Code Review |

**Standard:**
After each layer is complete and its tests are passing, a commit is written before
proceeding to the next layer. A feature with five layers produces a minimum of five
commits. The commit history of a feature branch is a readable log of how the feature
was built, layer by layer.

**Anti-Patterns:**
- `AP-S1.33a` — `git add .` at the end of the feature — all layers collapsed into one commit.
- `AP-S1.33b` — Committing a layer before its tests are passing.

**Cross-References:** `S1.19` (commit format), `S1.32` (layer order)

---

### S1.34 — Phase 4: Self-Review Is Completed Before PR Is Opened

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.34 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.45` (self-review checklist) |
| **Enforced By** | PR Description (self-review confirmation field) |

**Standard:**
The self-review checklist (S1.45) is completed in full before the PR is opened. The PR
description includes confirmation that all four quadrants were completed. A PR opened
without self-review completion is returned to the author immediately, before any code
review begins.

**Anti-Patterns:**
- `AP-S1.34a` — Submitting a PR with the intent that reviewers will catch what the author missed.

**Cross-References:** `S1.45` (checklist), `S1.46` (PR description), `S1.75` (reviewer standards)

---

### S1.35 — Phase 5: PR Description Uses the Mandatory Template

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.35 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.34` (self-review complete) |
| **Enforced By** | PR Template · Code Review |

**Standard:**
Every PR is submitted using the full PR description template (S1.46). All required fields
are populated. Screenshots are attached for every change that affects the UI. Linked
GitHub Issue uses `Closes #N` syntax. A PR with missing fields or missing screenshots
for a UI change is returned before review begins.

**Anti-Patterns:**
- `AP-S1.35a` — Leaving any PR description field empty or with placeholder text.
- `AP-S1.35b` — Omitting screenshots for a UI change.

**Cross-References:** `S1.46` (PR template), `S1.34` (self-review gate)

---

### S1.36 — Phase 5: One Concern Per PR

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.36 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.3` (one concern per unit) |
| **Enforced By** | Code Review |

**Standard:**
Every PR addresses exactly one concern. A PR that addresses two concerns is split into
two PRs before review begins. If the title requires "and" to be accurate, the PR has
multiple concerns.

**Anti-Patterns:**
- `AP-S1.36a` — "While I was in the file, I also fixed…" bundled into the current PR.

**Cross-References:** `S1.3` (one concern), `S1.16` (one concern per branch)

---

### S1.37 — Phase 6: Review Response Within 24 Hours

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.37 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.47` (review response protocol) |
| **Enforced By** | Team Process · PR Protocol |

**Standard:**
The PR author responds to every review comment within 24 hours with one of: (1) fix
addressed — "Done in `{commit-hash}`", (2) request for clarification, or (3) flag for
synchronous discussion. Silence for more than 24 hours is treated as a blocked PR and
escalated as a blocker per S1.9.

**Anti-Patterns:**
- `AP-S1.37a` — Fixing a review comment without responding in the PR thread.
- `AP-S1.37b` — Arguing a review comment in the PR thread.

**Cross-References:** `S1.47` (response protocol), `S1.14` (24-hour standard)

---

### S1.38 — Phase 6: Review Comments Are Categorised Before Acting

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.38 |
| **Priority**    | Standard |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.37` (review response) |
| **Enforced By** | Review Response Protocol |

**Standard:**
Before addressing any review comments, the author reads all and categorises each as:
(1) **Must Fix** — constitutional violation or functional defect, always addressed.
(2) **Suggestion** — improvement evaluated by author with reasoning.
(3) **Nitpick** — style preference, at author's discretion.
Constitutional violations are always Must Fix — no discretion.

**Anti-Patterns:**
- `AP-S1.38a` — Treating all review comments as Must Fix, over-implementing reviewer preferences.
- `AP-S1.38b` — Treating a constitutional violation comment as a Nitpick to avoid rework.

**Cross-References:** `S1.37` (response timing), `S1.76` (reviewer categorisation)

---

### S1.39 — Phase 7: Merge Requires All Gates Passed

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.39 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.22` (squash merge), `S1.75` (approvals) |
| **Enforced By** | GitHub Repository Settings |

**Standard:**
A PR is merged only after: all Must Fix review comments resolved, all CI checks pass,
required approvals received (team: minimum two; solo: solo-dev-overlay protocol satisfied),
and squash commit message written in conventional commit format. Merging without all three
conditions is a process failure regardless of urgency.

**Anti-Patterns:**
- `AP-S1.39a` — A merge taken with an unresolved Must Fix, a red check or missing approval because the change was urgent — urgency is exactly the condition under which the gates were designed to hold, so they are waived at the only moment they matter.

**Cross-References:** `S1.22` (squash merge), `S1.75` (approval standard), `S1.23` (post-merge cleanup)

---

### S1.40 — Phase 7: Staging Verification Before Issue Close

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.40 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.39` (merge complete), `S1.23` (cleanup) |
| **Enforced By** | PR Close Protocol · Deployment Pipeline |

**Standard:**
After merge and post-merge cleanup, the merged feature is verified in staging before the
GitHub Issue is closed. Verification confirms: feature works end-to-end with real data,
no regressions visible in adjacent features, acceptance criteria from the proposal met.
Staging verification is the definition of done — not the PR merge.

**Anti-Patterns:**
- `AP-S1.40a` — Closing the GitHub Issue immediately on merge before staging deployment completes.

**Cross-References:** `S1.23` (cleanup), `S1.29` (acceptance criteria), `S8.1` (staging environment)


---

## Part 7 — Non-Negotiable Engineering Standards (`S1.41`–`S1.44`)

These four standards are the engineering floor — the minimum bar below which no code may
fall and be merged into any KSDRILL SA system.

---

### S1.41 — Every Feature Is Tested Before It Is Merged

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.41 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S7.1` (test alongside implementation) |
| **Enforced By** | CI Coverage Gate · Code Review |

**Standard:**
Every feature that adds or modifies behaviour has tests covering that behaviour before
the PR is opened. Unit tests for business logic, integration tests for API contracts,
E2E tests for user-facing flows — at coverage ratios defined in C7. A PR with no tests
for new behaviour is returned to the author.

**Anti-Patterns:**
- `AP-S1.41a` — "I'll add tests in a follow-up PR." Tests are part of the feature, not a separate deliverable.

**Cross-References:** `S7.1` (testing standard), `S1.32` (tests alongside layers)

---

### S1.42 — Every Commit Is Purposeful

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.42 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.19` (conventional commits), `S1.33` (commit per layer) |
| **Enforced By** | Commitlint · Code Review |

**Standard:**
Every commit in a PR represents a deliberate, complete, passing unit of work. WIP commits,
checkpoint commits, and "just pushing to save" commits are not present when a PR is
submitted. If WIP commits exist, they are squashed locally before the PR opens.

**Anti-Patterns:**
- `AP-S1.42a` — WIP commits: `"wip"`, `"temp save"`, `"checkpoint"` — squash before PR.
- `AP-S1.42b` — Fix-typo commit instead of amending: `"fix typo in previous commit"` — amend instead.

**Cross-References:** `S1.19` (commit format), `S1.33` (commit per layer)

---

### S1.43 — Code Is Reviewed Before It Reaches Main

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.43 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.17` (main protection), `S1.75` (review standard) |
| **Enforced By** | Branch Protection · Required Reviewers |

**Standard:**
Every change to `main` is reviewed by at least one engineer who did not write the change.
Team context: minimum two approvals from engineers who reviewed the code — not just
approved the PR. Solo context: solo-dev-overlay AI review protocol and 24-hour cooling
period. No change bypasses review for any reason.

**Anti-Patterns:**
- `AP-S1.43a` — Self-approving a PR in a team context.
- `AP-S1.43b` — "It's just a one-line change" bypassing review.

**Cross-References:** `S1.75` (reviewer standards), `S1.17` (main protection)

---

### S1.44 — No Production Code Contains Debug Artifacts

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.44 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.45` (self-review checklist) |
| **Enforced By** | ESLint `no-console` rule · Self-review checklist |

**Standard:**
No code merged to `main` contains `console.log`, `console.error`, `debugger`, `print()`
for debugging, commented-out code blocks, or `TODO` comments without an associated GitHub
Issue number. Caught by self-review (S1.45) and ESLint. The linting rule violation fails CI.

**Anti-Patterns:**
- `AP-S1.44a` — `console.log` left in code because "it's useful for debugging."
- `AP-S1.44b` — Commented-out code with "remove this later" note.

**Cross-References:** `S1.45` (self-review), `S1.70` (ESLint configuration)

---

## Part 8 — Author Quality Gates (`S1.45`–`S1.47`)

Author quality gates are satisfied by the PR author before any reviewer sees the code.
They transform code review from a first-pass quality check into a genuine second layer.

---

### S1.45 — Self-Review Checklist Has Four Mandatory Quadrants

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.45 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.34` (self-review phase) |
| **Enforced By** | PR Description Template · Code Review |

**Standard:**
Before opening any PR, the author completes all four quadrants. Every item is checked.
The PR description confirms completion.

**Quadrant 1 — Architecture**
```
[ ] Service layer used — no direct backend calls from UI components
[ ] Smart / presentational component separation maintained
[ ] No business logic in UI template or markup layer
[ ] Code placed in the correct constitutional layer per S1.32
[ ] Correct system / package placement in the monorepo
```

**Quadrant 2 — Code Quality**
```
[ ] No `any` types — all variables and parameters strictly typed
[ ] No unused imports, variables, or dead code
[ ] No console.log, debugger, or print() for debugging
[ ] All error, loading, and empty states handled and tested
[ ] No magic numbers — all constants named and documented
```

**Quadrant 3 — Commits**
```
[ ] All commits follow conventional commit format (S1.19)
[ ] Each commit covers exactly one layer or concern
[ ] No WIP, temp, or checkpoint commits in the PR
[ ] No merge commits from main in the branch history
[ ] Branch name matches feature and follows S1.16 format
```

**Quadrant 4 — Functionality**
```
[ ] Feature works end-to-end in the browser with real data
[ ] Tested manually against all acceptance criteria from the proposal
[ ] Responsive layout verified if any UI was changed
[ ] No regressions visible in adjacent features
[ ] All CI checks pass locally before PR is opened
```

**Anti-Patterns:**
- `AP-S1.45a` — Opening a PR with intent to complete self-review during the review cycle.
- `AP-S1.45b` — Treating the checklist as a formality and checking boxes without performing the checks.

**Cross-References:** `S1.34` (self-review phase), `S1.46` (PR template confirms), `S1.44` (debug artifacts)

---

### S1.46 — PR Description Uses the Mandatory Template

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.46 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.45` (self-review complete) |
| **Enforced By** | PR Template · Code Review |

**Standard:**
Every PR is submitted with all required fields populated. Screenshots attached for every
PR that modifies any UI element.

| Field | Requirement |
|---|---|
| **Title** | Conventional commit format: `{type}({scope}): {description}` |
| **Linked Issue** | `Closes #N` — auto-closes GitHub Issue on merge |
| **What Changed** | Bullet list of every component, service, model, or route modified |
| **Why It Changed** | References the approved proposal — links to the GitHub Issue |
| **How to Test** | Step-by-step reproduction from a clean browser state |
| **Screenshots** | Before and after for every UI change — mandatory |
| **Self-Review Confirmed** | Checkbox: "I have completed the self-review checklist (S1.45)" |
| **Constitutional Compliance** | Citation of all relevant standards that govern this PR's changes |

**Anti-Patterns:**
- `AP-S1.46a` — PR description "see the code" for the What Changed field.
- `AP-S1.46b` — Screenshots missing for a UI PR.

**Cross-References:** `S1.45` (self-review), `S1.35` (PR submission phase)

---

### S1.47 — Review Response Protocol Is Followed by the Author

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.47 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.37` (response within 24 hours) |
| **Enforced By** | PR Protocol · Team Process |

**Standard:**
When a review cycle begins, the author follows this protocol in order:
(1) Read ALL comments before addressing any — categorise per S1.38.
(2) Address Must Fix items first — commit with: `fix({scope}): address review — {description}`.
(3) Respond to each resolved comment: `Done in {commit-hash} — {one-line explanation}`.
(4) Re-request review from the same reviewers after all Must Fix items resolved.
(5) For disagreements: discuss synchronously first, then document the resolution in the PR thread.

**Anti-Patterns:**
- `AP-S1.47a` — Pushing a fix commit without responding in the PR thread.
- `AP-S1.47b` — Re-requesting review before all Must Fix items are resolved.
- `AP-S1.47c` — Arguing a review comment in the PR thread instead of going synchronous.

**Cross-References:** `S1.37` (response timing), `S1.38` (categorisation), `S1.75` (reviewer obligations)


---

## Part 9 — TypeScript Standards (`S1.48`–`S1.56`)

TypeScript standards govern all `.ts` and `.tsx` files across both stacks. Strict mode
is not a configuration option — it is the baseline.

---

### S1.48 — TypeScript Strict Mode Is Non-Negotiable

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.48 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | — |
| **Enforced By** | `tsconfig.json` strict: true · CI type-check |

**Standard:**
All TypeScript runs under `strict: true` in `tsconfig.json`. This enables `noImplicitAny`,
`strictNullChecks`, `strictFunctionTypes`, `strictPropertyInitialization`, and all other
strict flags. No TypeScript configuration disables any strict flag. Systems are not
initialised without strict mode active from the first commit.

**Anti-Patterns:**
- `AP-S1.48a` — Setting `"strict": false` or disabling individual strict flags to resolve type errors.
- `AP-S1.48b` — Using `@ts-ignore` or `@ts-expect-error` without a GitHub Issue reference.

**Cross-References:** `S1.49` (no any), `S1.50` (explicit return types)

---

### S1.49 — The `any` Type Is Prohibited in Production Code

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.49 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.48` (strict mode) |
| **Enforced By** | ESLint `@typescript-eslint/no-explicit-any` · CI |

**Standard:**
The `any` type is never used in production TypeScript code. When the type is genuinely
unknown, `unknown` is used with an appropriate type guard before the value is used. When
working with third-party libraries that return `any`, the boundary is typed immediately
at the point of use.

**Anti-Patterns:**
- `AP-S1.49a` — `const data: any = response.json()` — use `unknown` and validate with Zod.
- `AP-S1.49b` — Casting to `any` to resolve a type error: `(value as any).property`.

**Cross-References:** `S1.48` (strict mode), `CF-09`

---

### S1.50 — All Functions Have Explicit Return Types

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.50 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.48` (strict mode) |
| **Enforced By** | ESLint `@typescript-eslint/explicit-function-return-type` |

**Standard:**
All functions — including arrow functions in service files and API handlers — have explicit
return type annotations. The return type is the contract of the function — it must be
explicit, not inferred.

**Anti-Patterns:**
- `AP-S1.50a` — Relying on TypeScript's return type inference for service functions.

**Cross-References:** `S1.48` (strict mode), `S1.49` (no any)

---

### S1.51 — Interfaces Over Type Aliases for Object Shapes

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.51 |
| **Priority**    | Standard |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | — |
| **Enforced By** | ESLint `@typescript-eslint/consistent-type-definitions` |

**Standard:**
Object shapes are defined using `interface`, not `type`. The `type` keyword is used for:
union types, intersection types, utility types, and type aliases for primitives. Consistent
pattern across all systems — `interface` for objects, `type` for everything else.

**Anti-Patterns:**
- `AP-S1.51a` — Object shapes declared with `type` instead of `interface` — declaration merging and extension behave differently between the two, and the codebase acquires two conventions for the same thing with no rule for choosing.

---

### S1.52 — Zod Schemas Validate All External Data Boundaries

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.52 |
| **Priority**    | Critical |
| **Applies To**  | Next.js Stack |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S2.7` (OpenAPI contract first) |
| **Enforced By** | Code Review · API Layer Validation |

**Standard:**
All data entering from external sources — HTTP request bodies, query parameters, env
variables, third-party API responses — is validated with a Zod schema at the boundary.
Zod schemas are generated from the OpenAPI contract, not written manually. Unvalidated
external data never reaches business logic or database writes.

**Anti-Patterns:**
- `AP-S1.52a` — Accessing `req.body.fieldName` without Zod parsing.
- `AP-S1.52b` — Writing Zod schemas manually that diverge from the OpenAPI contract.

**Cross-References:** `S2.7` (OpenAPI), `S1.58` (Pydantic — Angular stack equivalent)

---

### S1.53 — Enums Use Const Assertions or String Literal Unions

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.53 |
| **Priority**    | Standard |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.48` (strict mode) |
| **Enforced By** | ESLint · Code Review |

**Standard:**
TypeScript `enum` keyword is avoided. Constant value sets use either `const` assertions
(`as const`) or string literal union types. TypeScript enums produce runtime JavaScript
objects with inconsistent behaviour. String literal unions are tree-shakeable and produce
no runtime output.

**Anti-Patterns:**
- `AP-S1.53a` — `enum Role { Admin = 'ADMIN' }` — use `type Role = 'ADMIN' | 'USER'`.

---

### S1.54 — Null and Undefined Are Distinguished

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.54 |
| **Priority**    | Standard |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.48` (strict null checks) |
| **Enforced By** | Code Review · TypeScript Strict |

**Standard:**
`null` means "intentionally absent." `undefined` means "not yet set." Functions that can
return no value return `undefined`. Optional interface fields use `?`. Fields explicitly
cleared use `| null`. The two are never interchanged.

**Anti-Patterns:**
- `AP-S1.54a` — `null` and `undefined` used interchangeably — the distinction between deliberately cleared and never set is erased, so a consumer cannot tell an intentional blank from a value that has not arrived yet.

---

### S1.55 — Generics Are Named Descriptively

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.55 |
| **Priority**    | Guidance |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | — |
| **Enforced By** | Code Review |

**Standard:**
Generic type parameters use descriptive names that communicate their role. In service and
model code: `TEntity`, `TResponse`, `TPayload`, `TFilter`. Single letter `T` is acceptable
only in utility types where the abstraction is so total that no meaningful name exists.

**Anti-Patterns:**
- `AP-S1.55a` — `function fetchAll<T>(url: string)` in a service — use `TEntity`.

---

### S1.56 — Path Aliases Replace Relative Import Chains

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.56 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | — |
| **Enforced By** | `tsconfig.json` paths · ESLint import resolver |

**Standard:**
Imports never use relative path chains of more than one level deep (`../`). All cross-module
imports use configured TypeScript path aliases (`@/components/...`, `@/services/...`).
Path aliases are configured in `tsconfig.json` and mirrored in the bundler configuration.

**Anti-Patterns:**
- `AP-S1.56a` — `import { X } from '../../../services/x.service'` — use `@/services/x.service`.

---

## Part 10 — Python Standards (`S1.57`–`S1.63`)

Python standards govern all `.py` files in FastAPI services across the Angular + FastAPI stack.

---

### S1.57 — Python 3.11+ Type Hints Are Mandatory

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.57 |
| **Priority**    | Critical |
| **Applies To**  | Angular Stack |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | — |
| **Enforced By** | mypy · CI type-check |

**Standard:**
All Python functions, methods, and class attributes in FastAPI services have complete type
annotations using Python 3.11+ syntax. Return types are always annotated. mypy runs in
strict mode in CI and all type errors are resolved before merge — not suppressed.

**Anti-Patterns:**
- `AP-S1.57a` — Unannotated function parameters in any FastAPI service.
- `AP-S1.57b` — `# type: ignore` without a GitHub Issue reference.

**Cross-References:** `S1.58` (Pydantic models), `S2.9` (FastAPI architecture)

---

### S1.58 — Pydantic Models Validate All Request and Response Bodies

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.58 |
| **Priority**    | Critical |
| **Applies To**  | Angular Stack |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S2.7` (OpenAPI contract first) |
| **Enforced By** | FastAPI Type Checking · Code Review |

**Standard:**
All FastAPI request bodies and response models are Pydantic v2 `BaseModel` subclasses.
Raw `dict` parameters are never used as request or response types in production endpoints.
Pydantic models are defined before the endpoint is implemented — they are the contract.

**Anti-Patterns:**
- `AP-S1.58a` — `async def create_student(data: dict) -> dict:` — use Pydantic models.
- `AP-S1.58b` — Defining the Pydantic model after writing the endpoint logic.

**Cross-References:** `S2.7` (OpenAPI), `S1.52` (Zod — Next.js equivalent)

---

### S1.59 — FastAPI Dependency Injection Is Used for Shared Concerns

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.59 |
| **Priority**    | High |
| **Applies To**  | Angular Stack |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S2.9` (FastAPI architecture) |
| **Enforced By** | Code Review |

**Standard:**
Database sessions, authentication dependencies, and request-scoped shared resources are
provided through FastAPI's `Depends()`. Direct instantiation of shared resources inside
route handlers is prohibited. Every route handler declares its dependencies explicitly
through the function signature.

**Anti-Patterns:**
- `AP-S1.59a` — Creating a database session inside the route handler function body.
- `AP-S1.59b` — Calling the authentication check function directly inside the handler.

**Cross-References:** `S2.9` (FastAPI architecture), `S3.22` (auth dependency injection)

---

### S1.60 — Async/Await Is Used for All I/O Operations

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.60 |
| **Priority**    | High |
| **Applies To**  | Angular Stack |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S1.57` (type hints) |
| **Enforced By** | Code Review |

**Standard:**
All FastAPI route handlers and service functions performing I/O — database queries, HTTP
requests, file operations — are defined with `async def` and use `await` for every I/O
call. Synchronous I/O inside async functions blocks the event loop.

**Anti-Patterns:**
- `AP-S1.60a` — Synchronous database driver inside an async FastAPI handler.
- `AP-S1.60b` — `requests.get()` inside an async handler — use `httpx.AsyncClient`.

---

### S1.61 — Python Imports Follow Isort Standard

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.61 |
| **Priority**    | Standard |
| **Applies To**  | Angular Stack |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | — |
| **Enforced By** | isort · CI |

**Standard:**
Imports ordered: (1) standard library, (2) third-party packages, (3) local application
imports. Each group separated by a blank line. isort is configured and runs as part of
the pre-commit hook and CI pipeline. Import order is never manually managed.

**Anti-Patterns:**
- `AP-S1.61a` — Python import order maintained by hand — every author orders differently, the diff on an unrelated change includes an import reshuffle, and review attention is spent on it.

---

### S1.62 — Ruff Is the Python Linter and Formatter

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.62 |
| **Priority**    | Standard |
| **Applies To**  | Angular Stack |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | — |
| **Enforced By** | Ruff · CI |

**Standard:**
Ruff is the single linting and formatting tool for all Python code. Black, Flake8, and
Pylint are not used. Ruff configuration lives in `pyproject.toml`. Line length is 88
characters. All violations block merge.

**Anti-Patterns:**
- `AP-S1.62a` — A second Python linter or formatter introduced beside the configured one — two tools disagree about the same file, and the last one to run decides, which makes the outcome depend on hook ordering.

---

### S1.63 — Docstrings Are Required for Public Functions and Classes

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.63 |
| **Priority**    | Standard |
| **Applies To**  | Angular Stack |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.57` (type hints) |
| **Enforced By** | Code Review · Ruff D rules |

**Standard:**
All public functions, methods, and classes have Google-style docstrings describing: what
the function does (not how), parameters, return value, and exceptions raised. Private
functions (prefixed with `_`) use docstrings when logic is non-obvious.

**Anti-Patterns:**
- `AP-S1.63a` — A public function with no docstring, or one describing how it works rather than what it does — the caller must read the implementation to use it, and the docstring drifts from the code with nothing reporting it.

---

## Part 11 — File & Module Structure (`S1.64`–`S1.69`)

Consistent file and module structure makes every KSDRILL SA system navigable by every
engineer and every AI tool without requiring system-specific orientation.

---

### S1.64 — File Names Are Lowercase and Hyphenated

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.64 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | — |
| **Enforced By** | ESLint `check-file` · Code Review |

**Standard:**
All TypeScript source files use lowercase names with hyphens as word separators. No
camelCase, PascalCase, or underscores in TypeScript file names. Angular component files
follow Angular CLI naming (`user-profile.component.ts`). Python files use underscores
per Python convention (`user_service.py`).

**Anti-Patterns:**
- `AP-S1.64a` — `UserProfile.tsx`, `userProfile.tsx`, `user_profile.tsx` in TypeScript — use `user-profile.tsx`.

---

### S1.65 — Each File Has a Single Export Responsibility

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.65 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.3` (one concern per unit) |
| **Enforced By** | Code Review |

**Standard:**
Each file has one primary export — one component, one service, one model, one utility.
Barrel files (`index.ts`) are permitted only at package or module boundaries, not within
feature directories. A file with multiple primary exports is a file that should be split.

**Anti-Patterns:**
- `AP-S1.65a` — Single file exporting `UserService`, `UserHelpers`, and `UserConstants` — three files.

---

### S1.66 — Module Boundaries Are Respected

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.66 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S1.65` (file responsibility) |
| **Enforced By** | ESLint module boundary rules · Code Review |

**Standard:**
Modules import only from their public API. Direct imports from internal paths of another
module are prohibited. Cross-module dependencies follow the dependency graph defined in
the system's architecture. Circular dependencies are not permitted.

**Anti-Patterns:**
- `AP-S1.66a` — `import from '../../auth/internal/token-validator'` from outside the auth module.

---

### S1.67 — Constants Are Named and Centralised

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.67 |
| **Priority**    | Standard |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | — |
| **Enforced By** | Code Review · ESLint `no-magic-numbers` |

**Standard:**
Magic numbers and magic strings do not appear in production code. All constant values
are named, typed, and placed in a dedicated constants file (`{module}.constants.ts` or
`constants.py`). The constant name communicates the meaning — not the value.

**Anti-Patterns:**
- `AP-S1.67a` — `if (score > 65)` — use `if (score > MINIMUM_PASSING_SCORE)`.
- `AP-S1.67b` — `setTimeout(fn, 900000)` — use `setTimeout(fn, SESSION_TIMEOUT_MS)`.

---

### S1.68 — Environment Variables Are Validated at Startup

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.68 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S8.20` (environment configuration) |
| **Enforced By** | Startup validation · CI environment check |

**Standard:**
All required environment variables are validated at service startup — before the service
accepts any requests. Missing or malformed variables cause an immediate startup failure
with a clear error message. Services that start with invalid configuration fail loudly —
not silently with undefined behaviour at runtime.

**Anti-Patterns:**
- `AP-S1.68a` — Reading `process.env.DATABASE_URL` inline at the point of use without startup validation.

**Cross-References:** `S8.20` (environment configuration)

---

### S1.69 — Test Files Are Co-located with Source Files

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.69 |
| **Priority**    | Standard |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S7.1` (testing standard) |
| **Enforced By** | Testing Constitution C7 · Code Review |

**Standard:**
Unit test files are co-located with the source file they test, named
`{source-file}.test.ts` or `{source-file}.spec.ts`. Integration and E2E tests live in
dedicated `__tests__/` or `e2e/` directories at the system root.

**Anti-Patterns:**
- `AP-S1.69a` — Unit tests filed away from the source they cover — a file is moved or deleted and its tests are left behind, still passing, testing something that no longer exists.

---

## Part 12 — Linting & Formatting (`S1.70`–`S1.74`)

Linting and formatting standards eliminate style debates from code review. Code style is
a configuration setting — not a discussion.

---

### S1.70 — ESLint and Prettier Are Configured and Enforced in CI

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.70 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | — |
| **Enforced By** | CI Lint Gate · Pre-commit Hooks |

**Standard:**
ESLint and Prettier are installed and configured from the first commit. ESLint
configuration includes: `@typescript-eslint/recommended`, `no-console`, `no-debugger`,
`no-unused-vars`, `no-magic-numbers`, and `import/no-relative-parent-imports`. Prettier
handles all formatting decisions. Both run in CI and all violations fail the build.

**Anti-Patterns:**
- `AP-S1.70a` — Disabling an ESLint rule in configuration to suppress errors — fix the code, not the rule.

---

### S1.71 — Pre-Commit Hooks Enforce Lint and Format Before Commit

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.71 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.70` (ESLint/Prettier configured) |
| **Enforced By** | Husky · lint-staged |

**Standard:**
Husky and lint-staged run ESLint and Prettier on every staged file before a commit is
allowed. A commit that fails lint or format cannot be created. This prevents violations
from entering branch history.

**Anti-Patterns:**
- `AP-S1.71a` — Pre-commit hooks absent or bypassed — violations enter branch history, and cleaning them up later produces a formatting commit that touches everything and hides the change underneath it.

---

### S1.72 — Code Review Does Not Address Style

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.72 |
| **Priority**    | Standard |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.70` (tools configured) |
| **Enforced By** | Review Standards |

**Standard:**
Style comments — indentation, spacing, quote style, line length — are not left in code
review. These are resolved by Prettier automatically. A review comment about style signals
the pre-commit hook or CI lint gate is not configured correctly. Review comments are
reserved for: constitutional violations, architecture decisions, logic errors, test
coverage gaps, and security concerns.

**Anti-Patterns:**
- `AP-S1.72a` — A style comment written in review — it costs a round trip on something the tooling should have settled, and it signals the hook or the lint gate is not configured, which is the defect actually worth reporting.

---

### S1.73 — Line Length Is 100 Characters for TypeScript, 88 for Python

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.73 |
| **Priority**    | Standard |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.70` (Prettier), `S1.62` (Ruff) |
| **Enforced By** | Prettier (TS) · Ruff (Python) |

**Standard:**
TypeScript and TSX files: 100-character line length. Python files: 88-character line
length (Ruff/Black standard). Both configured in the tool configuration files — never
manually managed.

**Anti-Patterns:**
- `AP-S1.73a` — Line length maintained by hand rather than by configuration — it holds until the first author who has not memorised the number, and the reflow lands in an unrelated pull request.

---

### S1.74 — Import Order Is Enforced Automatically

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.74 |
| **Priority**    | Standard |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.70` (ESLint), `S1.61` (isort for Python) |
| **Enforced By** | ESLint `import/order` (TS) · isort (Python) |

**Standard:**
TypeScript import order: (1) Node built-ins, (2) external packages, (3) internal packages
via path aliases, (4) relative imports within the same module. Each group separated by
a blank line. Configured in ESLint — never manually enforced.

**Anti-Patterns:**
- `AP-S1.74a` — TypeScript import order enforced by convention rather than by the linter — the ordering is correct in files written by people who remember it, and the exceptions are invisible until someone looks.

---

## Part 13 — Code Review Standards (`S1.75`–`S1.82`)

Code review standards govern the reviewer's obligations. Reviewers who have read these
standards produce reviews that improve code quality.

---

### S1.75 — Reviewers Evaluate Substance, Not Style

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.75 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.72` (style handled by tools) |
| **Enforced By** | Review Culture |

**Standard:**
Reviewers focus on: constitutional compliance, architecture correctness, logic errors,
test coverage adequacy, security concerns, and performance implications. Style comments
are not written. A review comment that cannot be tied to a standard, a logic error, or
a security concern is not a blocking comment.

**Anti-Patterns:**
- `AP-S1.75a` — A blocking comment that cannot be tied to a standard, a logic error or a security concern — the author is required to satisfy the reviewer's preference, and review authority stops resting on anything reviewable.

**Cross-References:** `S1.72` (no style comments), `S1.38` (comment categorisation)

---

### S1.76 — Review Comments Are Categorised at Point of Writing

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.76 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.38` (author's categorisation) |
| **Enforced By** | Review Culture |

**Standard:**
Reviewers prefix every comment with its category: `[Must Fix]`, `[Suggestion]`, or
`[Nitpick]`. `[Must Fix]` comments cite the constitutional standard violated. A
`[Must Fix]` without a standard citation is reclassified as `[Suggestion]` unless the
reviewer provides a specific rationale.

**Anti-Patterns:**
- `AP-S1.76a` — Leaving a critical security comment as `[Nitpick]` to avoid conflict.

**Cross-References:** `S1.38` (author categorisation), `S1.75` (reviewer focus)

---

### S1.77 — Approval Means the Reviewer Has Read the Code

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.77 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | — |
| **Enforced By** | Review Culture |

**Standard:**
A GitHub PR approval means the reviewer has: read every line of code in the diff, run the
feature locally against real data, verified the tests are testing the right behaviour, and
confirmed constitutional compliance. Team context: two such approvals required before merge.

**Anti-Patterns:**
- `AP-S1.77a` — Approving a PR after reading the description and the first two files.
- `AP-S1.77b` — Approving a PR because a senior engineer already approved it — the second approval must be independent.

---

### S1.78 — Reviewers Check for Constitutional Violations First

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.78 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.25` (constitutions read) |
| **Enforced By** | Review Culture |

**Standard:**
The first pass of every code review checks constitutional compliance. The reviewer
identifies which constitutions are relevant (from the PR's constitutional compliance
field), reads the relevant standards, and verifies the code against them before reviewing
logic, architecture, or style.

**Anti-Patterns:**
- `AP-S1.78a` — Review that starts with logic and never reaches compliance — the violation is approved on its merits, and the standard is discovered only when a check fires against code that already shipped.

**Cross-References:** `S1.25` (constitutions read), `S1.76` (categorisation)

---

### S1.79 — Reviewer Notes Adjacent Problems as Separate Issues

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.79 |
| **Priority**    | Standard |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | — |
| **Enforced By** | Review Culture |

**Standard:**
Reviewers who notice existing code problems adjacent to the PR's changes create separate
GitHub Issues — they do not fix them in the PR being reviewed, and they do not ignore
them. A review is an opportunity to improve the broader codebase.

**Anti-Patterns:**
- `AP-S1.79a` — An adjacent problem fixed inside the pull request under review, or noticed and dropped — the first makes the change unreviewable, the second wastes the one moment somebody was looking at that code.

---

### S1.80 — Constructive Criticism Is the Only Acceptable Tone

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.80 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | — |
| **Enforced By** | Engineering Culture |

**Standard:**
Review comments address the code — never the author. Comments explain why a change is
needed and suggest an alternative where possible. Comments that cannot pass the test of
"would I be comfortable if the author read this aloud in a team meeting?" are not written.

**Anti-Patterns:**
- `AP-S1.80a` — "This is wrong." Correct form: "[Must Fix] Per `S2.13`, Prisma must be used for all relational queries. Raw SQL at line 47 bypasses this — refactor to `prisma.user.findMany()`."

---

### S1.81 — Re-Review Is Requested After All Must-Fix Items Are Resolved

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.81 |
| **Priority**    | Standard |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.47` (author response protocol) |
| **Enforced By** | PR Protocol |

**Standard:**
After all `[Must Fix]` items are resolved and committed, the author explicitly re-requests
review from the original reviewers via the GitHub review request button. Reviewers are not
expected to monitor PRs for new commits. A PR with resolved Must Fix items that has not
been re-requested is a stalled PR.

**Anti-Patterns:**
- `AP-S1.81a` — Must Fix items resolved without re-requesting review — reviewers do not watch merged-into branches for new commits, so the pull request stalls with everyone believing it is with someone else.

---

### S1.82 — Draft PRs Signal Work in Progress

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.82 |
| **Priority**    | Standard |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | — |
| **Enforced By** | GitHub Draft PR Feature |

**Standard:**
A PR not ready for review is opened as a Draft PR. Draft PRs are not reviewed until the
author converts them to ready. WIP code submitted as a ready PR to "get early feedback"
wastes reviewer time on code that will change before reaching review-ready state.

**Anti-Patterns:**
- `AP-S1.82a` — Work in progress opened as a ready pull request to get early feedback — reviewer time is spent on code that is going to change, and the real review arrives when everyone has already read it once.

---

## Part 14 — Documentation Standards (`S1.83`–`S1.87`)

Documentation standards define what is documented, where, and at what level of detail.
Documentation is the mechanism by which the constitutional system outlasts any individual
engineer.

---

### S1.83 — Public APIs Are Documented at the OpenAPI Level

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.83 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S2.7` (OpenAPI contract first) |
| **Enforced By** | OpenAPI Validation · Code Review |

**Standard:**
Every public API endpoint is documented in the OpenAPI specification with: a description
of the endpoint's purpose, all request parameters and body fields with types and
constraints, all response shapes for all response codes (200, 400, 401, 403, 404, 422,
500), and example request and response values. The OpenAPI spec is the documentation —
no separate tool is maintained in parallel.

**Anti-Patterns:**
- `AP-S1.83a` — Documenting an API endpoint only in code comments or Notion. OpenAPI spec is canonical.

---

### S1.84 — README Files Are Maintained at the System Root

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.84 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | — |
| **Enforced By** | Code Review · PR Checklist |

**Standard:**
Every KSDRILL SA system has a README at the repository root containing: system purpose,
stack and architecture overview (with constitutional references), local development setup
(step-by-step), environment variable list (names only — never values), and links to the
relevant system context file in the constitutional repository. The README is updated in
any PR that changes setup, architecture, or environment configuration.

**Anti-Patterns:**
- `AP-S1.84a` — A system with no README, or one that was not updated when setup changed — the documented steps fail on a fresh machine, and the only working knowledge of how to run the system is in one person's shell history.

---

### S1.85 — ADRs Document Significant Technical Decisions

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.85 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S1.15` (decisions documented before implemented) |
| **Enforced By** | ADR Process · S6.5 |

**Standard:**
Every significant architectural decision not covered by an existing constitutional standard
is documented in an ADR using `ADR-000-template.md`. ADRs are committed to the `adrs/`
directory in `governova`. The ADR captures: the decision, the context, the
options considered, the rationale for the chosen option, and the consequences.

**Anti-Patterns:**
- `AP-S1.85a` — A significant architectural decision left undocumented because no standard covers it — the gap in the corpus becomes a gap in the record, and the decision is inherited with no way to tell what it was weighed against.

**Cross-References:** `S1.15` (document before implement), `S6.5` (ADR process)

---

### S1.86 — Inline Comments Explain Why, Not What

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.86 |
| **Priority**    | Standard |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | — |
| **Enforced By** | Code Review |

**Standard:**
Inline comments explain the reasoning behind a decision — why the code does what it does,
not a description of what the code does. Comments that reference constitutional compliance
cite the standard ID: `// Per S2.13 — Prisma is the source of truth for relational data`.

**Anti-Patterns:**
- `AP-S1.86a` — `// Loop through all students` above a for loop — the code says this.
- `AP-S1.86b` — Commented-out code with an explanation — delete it, Git history preserves it.

---

### S1.87 — CONSTITUTION-INDEX.md Is Maintained in Every Project Workspace

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.87 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S10.4` (CONSTITUTION-INDEX standard in C10) |
| **Enforced By** | C10 AI Collaboration · Pre-Build Checklist |

**Standard:**
Every project workspace contains a `CONSTITUTION-INDEX.md` at the root before the first
AI-assisted development session. This file lists: which constitutions apply, which
standards are most critical for the current system, the current build phase and group,
and any approved deviations. Updated at every sprint boundary. An AI session begun
without `CONSTITUTION-INDEX.md` present is a non-compliant session.

**Anti-Patterns:**
- `AP-S1.87a` — A workspace with no index, or one carried over from the previous sprint — the session runs against the wrong standards with full confidence, which is worse than running against none.

**Cross-References:** `S10.4` (CONSTITUTION-INDEX standard), `C10` (AI collaboration)

---

## Part 15 — Angular-Specific Quality (`S1.88`–`S1.92`)

Angular-specific quality standards govern the Angular codebase in the Angular + FastAPI
stack. These complement the universal TypeScript standards with Angular-specific patterns.

---

### S1.88 — Angular Standalone Components Are Mandatory

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.88 |
| **Priority**    | Critical |
| **Applies To**  | Angular Stack |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | — |
| **Enforced By** | Angular ESLint · Code Review |

**Standard:**
All Angular components, directives, and pipes are created as standalone (Angular 17+).
NgModules are not used in new code. All new components are generated with the Angular CLI
`--standalone` flag as the default.

**Anti-Patterns:**
- `AP-S1.88a` — Creating a component with `@NgModule` declarations.

---

### S1.89 — Angular Signals Are Used for Local State

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.89 |
| **Priority**    | High |
| **Applies To**  | Angular Stack |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S1.88` (standalone components) |
| **Enforced By** | Code Review |

**Standard:**
Angular Signals are used for local component state management. `BehaviorSubject` and
manual RxJS subscriptions for local state are not used in new components. RxJS is retained
for: HTTP requests, complex async composition across multiple streams, and interoperability
with libraries that return Observables.

**Anti-Patterns:**
- `AP-S1.89a` — `BehaviorSubject` and manual subscriptions used for local state in new components — teardown becomes the author's responsibility on every one of them, and the component that forgets leaks a listener per mount.

---

### S1.90 — Reactive Forms Are Used for All Form Implementations

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.90 |
| **Priority**    | Critical |
| **Applies To**  | Angular Stack |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | — |
| **Enforced By** | Angular ESLint · Code Review |

**Standard:**
All Angular forms use Reactive Forms (`FormGroup`, `FormControl`, `FormBuilder`).
Template-driven forms are not used in any KSDRILL SA Angular system. Reactive Forms
provide typed form controls (Angular 14+), deterministic validation, easier testing, and
explicit state management aligned with the smart/presentational component pattern.

**Anti-Patterns:**
- `AP-S1.90a` — Using `ngModel` for two-way data binding in forms.

---

### S1.91 — OnPush Change Detection Is the Default

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.91 |
| **Priority**    | High |
| **Applies To**  | Angular Stack |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S1.88` (standalone), `S1.89` (Signals) |
| **Enforced By** | Angular ESLint · Code Review |

**Standard:**
All Angular components use `ChangeDetectionStrategy.OnPush` as the default. Default
change detection is not used in new components. OnPush combined with Signals and
Observables with the `async` pipe provides optimal rendering performance and predictable
change detection cycles.

**Anti-Patterns:**
- `AP-S1.91a` — A new component left on default change detection — the whole tree is checked on every event, and the cost is invisible in development and unavoidable on the devices this product exists to serve.

---

### S1.92 — Angular Services Are Provided at Root Level

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.92 |
| **Priority**    | High |
| **Applies To**  | Angular Stack |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S1.59` (dependency injection) |
| **Enforced By** | Angular ESLint · Code Review |

**Standard:**
All Angular services use `providedIn: 'root'` in their `@Injectable` decorator unless
there is a specific, documented reason for component-level provision. Root-level provision
creates singleton services that are tree-shakeable. Services that maintain state are always
singletons — component-level provision creates new instances per component and breaks
shared state.

**Anti-Patterns:**
- `AP-S1.92a` — A stateful service provided at component level with no documented reason — each component gets its own instance, so shared state silently is not shared and the symptom is data that disagrees with itself.

---

## Part 16 — Git Recovery Procedures (`S1.93`–`S1.97`)

Git recovery procedures define the correct actions for the five most common Git mistakes.
These procedures exist because mistakes happen — what the constitutional system controls
is how they are recovered from.

---

### S1.93 — Recovery: Committed to Main Accidentally

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.93 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.17` (main protection) |
| **Enforced By** | Git Recovery Protocol |

**Standard:**
If a commit was made directly to `main` (only possible if branch protection was bypassed):
(1) Do NOT push. (2) `git log --oneline -5` — identify the commit hash. (3) `git reset HEAD~1` — unstage the commit, keeping changes as working directory modifications. (4) Create a proper feature branch. (5) Stage the changes onto the new branch. (6) Commit and push normally. If already pushed to `main`, escalate as a SEV1 incident — do not force-push without team coordination.

**Anti-Patterns:**
- `AP-S1.93a` — A commit made straight to `main` and then pushed — the recovery stops being local and becomes a shared-history problem, which is why the standard's first instruction is not to push.

**Cross-References:** `S1.17` (main protection), `CF-04`

---

### S1.94 — Recovery: Pushed to the Wrong Branch

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.94 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | — |
| **Enforced By** | Git Recovery Protocol |

**Standard:**
If commits were pushed to the wrong branch: (1) Create the correct branch from `main`. (2) `git cherry-pick {commit-hash}` — apply commits to the correct branch. (3) Push the correct branch. (4) Delete commits from the wrong branch using `git reset`. (5) If the wrong branch is shared: communicate the reset in the team channel before executing.

**Anti-Patterns:**
- `AP-S1.94a` — Commits removed from a shared wrong branch with no warning — everyone who pulled the old history now has commits that no longer exist upstream, and each of them resolves it differently.

---

### S1.95 — Recovery: Created Branch from Wrong Base

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.95 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.31` (branch created from main) |
| **Enforced By** | Git Recovery Protocol |

**Standard:**
If a feature branch was created from another feature branch instead of `main`: (1) Identify commits belonging only to the new feature. (2) Create a correct branch from `main`. (3) `git cherry-pick` the feature-only commits onto the correct branch. (4) Abandon the incorrectly-based branch — close any open PR, delete the branch, open a new PR from the correct branch.

**Anti-Patterns:**
- `AP-S1.95a` — A branch left based on another feature branch — its pull request diff carries the parent's commits, so review covers changes twice and merging one branch silently merges part of the other.

---

### S1.96 — Recovery: Staged Wrong Files

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.96 |
| **Priority**    | Standard |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | — |
| **Enforced By** | Git Recovery Protocol |

**Standard:**
If wrong files were staged before a commit: (1) `git reset HEAD {file}` — unstage specific files without losing changes. (2) `git diff --staged` — verify the staging area contains only intended files. (3) Commit only when staging area is correct. If the commit was already made: `git reset HEAD~1` to unstage, then re-stage correctly.

**Anti-Patterns:**
- `AP-S1.96a` — A commit made without checking what is staged — unrelated files enter the history, and a later revert of that commit takes changes nobody associated with it.

---

### S1.97 — Recovery: Wrong Commit Message Written

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.97 |
| **Priority**    | Standard |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.19` (conventional commits) |
| **Enforced By** | Git Recovery Protocol |

**Standard:**
If the most recent commit message is incorrect: (1) `git commit --amend -m "{correct message}"` — rewrites the most recent commit message. (2) If already pushed: `git push --force-with-lease origin {branch-name}` — force-push only to your own feature branch, never to `main` or a shared branch. `--force-with-lease` is the only acceptable force-push flag. `--force` is prohibited.

**Anti-Patterns:**
- `AP-S1.97a` — A message corrected by force-pushing without the lease flag — a colleague's commits pushed in the interval are overwritten with no warning, which is the outcome the lease flag exists to refuse.

---

## Part 17 — Dependency & Build Reproducibility (`S1.98`)

---

### S1.98 — Reproducible Dependency Installs (Lockfile + Frozen CI)

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.98 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.16`–`S1.24` (Git discipline — the lockfile is committed and reviewed) |
| **Enforced By** | CI install step (frozen) · code review of lockfile changes |

**Standard:**
Dependency installs must be reproducible. A committed lockfile pins the full transitive dependency tree, and CI installs **frozen** — `uv sync --frozen` (Python), `npm ci` / `pnpm install --frozen-lockfile` (Node), or the stack equivalent — and the build FAILS if the lockfile and the manifest have drifted. The build can never silently resolve a different dependency tree than the one that was reviewed. Adding or upgrading a dependency means editing the manifest AND regenerating the lockfile in the same PR; an editable/unpinned install (`pip install -e`, an un-lockfiled `npm install`) is never the CI install path.

**Rationale:**
An unpinned install resolves "latest compatible" at build time, so a transitive upgrade can turn a green PR into a red `main` hours later with nothing in the diff to explain it. A committed lockfile plus a frozen CI install makes the dependency tree a reviewed, versioned artifact — the same inputs produce the same build on every machine and every day. Drift-detection at install is the cheapest place to catch a manifest/lockfile mismatch.

**Anti-Patterns:**
- `AP-S1.98a` — CI installs with a non-frozen command (or an editable install) so a transitive bump silently changes the build — the tree that ran in CI is not the tree that was reviewed.

**Cross-References:** `S1.16`–`S1.24` (Git discipline), `C8` (CI/CD pipeline — the frozen install is a pipeline gate).

---

## Part 18 — Operating-Practice & Adoption Governance (`S1.99`–`S1.102`)

---

### S1.99 — Branch → Issue → PR → Merge, With Full Metadata

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.99 |
| **Priority**    | Critical |
| **Applies To**  | All Stacks · solo and team |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.1` (no branch before approval), `S1.16`–`S1.24` (Git discipline) |
| **Enforced By** | `protocols/github-workflow.md` · repository/issue settings |

**Standard:**
Every unit of work follows the order **branch → issue → PR → merge**. Every issue and PR carries full metadata before it is considered tracked: type, milestone, project, labels, and an assignee; the PR links its issue with `Closes #N`. A bare PR — no linked issue, missing metadata — is a violation and is corrected before merge.

**Rationale:**
Untracked, metadata-less PRs destroy traceability: during the v2.0 restructure, PRs opened without issues or metadata could not be reconstructed into a governed history. Mandatory metadata makes every change attributable to a tracked, classified, owned unit of work.

**Anti-Patterns:**
- `AP-S1.99a` — Opening a PR with no linked issue or missing type/milestone/project/labels/assignee.

**Cross-References:** `protocols/github-workflow.md`, `S10.40` (merge authority by mode).

---

### S1.100 — No AI References on the GitHub Metadata Surface

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.100 |
| **Priority**    | Critical |
| **Applies To**  | All Stacks · all repositories |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.19` (conventional commits) |
| **Enforced By** | `protocols/github-workflow.md` §2 · review · history scrub when breached |

**Standard:**
No AI references appear anywhere on the GitHub metadata surface: commit messages and bodies, co-authors/contributors, PR titles and bodies, issue text, branch names, and file names. All authorship is attributed to the human author. A breach is corrected before merge; an already-merged breach is scrubbed by history rewrite. This rule governs the metadata surface only — the constitutions' governed *content* may still describe an AI engineer relay.

**Rationale:**
Governova governs AI development; its own history must stand as human-authored and professional. A `Cursor Agent` co-author and named AI tools were found in `main` history — exactly the credibility liability an AI-governance product cannot carry.

**Anti-Patterns:**
- `AP-S1.100a` — A `Co-Authored-By` AI trailer, AI tool name, or AI bot co-author in any commit, PR, issue, branch, or filename.

**Cross-References:** `protocols/github-workflow.md` §2, `protocols/git-workflow.md` (history-rewrite mechanics).

---

### S1.101 — Characterization Tests Before Any Brownfield Refactor

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.101 |
| **Priority**    | Critical |
| **Applies To**  | All Stacks · existing-system adoption |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `C7` (Testing) |
| **Enforced By** | `protocols/brownfield-adoption.md` §2 |

**Standard:**
Before refactoring untested code in an existing (brownfield) system, characterization tests that pin the code's **current** behaviour are written first. Refactoring proceeds only once behaviour is pinned, so a behaviour-preserving change can be proven behaviour-preserving.

**Rationale:**
Refactoring untested legacy code is the single most common way an adoption breaks a working system. Pinning behaviour first converts an unknowable change into a verifiable one.

**Anti-Patterns:**
- `AP-S1.101a` — Refactoring untested legacy code with no characterization test pinning prior behaviour.

**Cross-References:** `protocols/brownfield-adoption.md`, `S6.45`, `S8.83`.

---

### S1.102 — Adoption Is Complete Only When Satisfied or Excepted

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.102 |
| **Priority**    | Standard |
| **Applies To**  | All Stacks · existing-system adoption |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.101` |
| **Enforced By** | `protocols/brownfield-adoption.md` §1 |

**Standard:**
A brownfield adoption is complete only when every applicable standard is either satisfied or carries a recorded, approved exception (`EXCEPTION-{ORG}-{DATE}`). "Mostly compliant" is not complete; nothing is silently skipped.

**Rationale:**
Silent partial adoption produces a system that looks governed but isn't — the most dangerous outcome, because it carries false assurance. An explicit exception register keeps every remaining gap visible and scheduled.

**Anti-Patterns:**
- `AP-S1.102a` — Declaring adoption "done" with unsatisfied standards and no recorded exceptions.

**Cross-References:** `protocols/brownfield-adoption.md`, GOVERNOVA-MASTER.md §14.3 (exception recording).

---

## Part 19 — Architectural Discipline (`S1.103`–`S1.107`)

Universal architectural discipline — applicable to any stack, any sector. These standards
make separation of concerns, data-access boundaries, configuration hygiene, reuse, and
simplicity first-class constitutional law rather than convention.

---

### S1.103 — Logic Lives in Its Layer

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.103 |
| **Priority**    | High |
| **Applies To**  | All Stacks · all systems |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.2` (logic placement) · `S1.3` (single concern) |
| **Enforced By** | review · semantic tier · `protocols/build-lifecycle.md` |

**Standard:**
Business logic lives only in the service/domain layer. Presentation (UI, components, views), transport (routes, controllers, handlers), and data-access layers contain no business rules — they delegate to services. Each layer has one responsibility and does not reach across boundaries.

**Rationale:**
Logic in the wrong layer cannot be tested, reused, or replaced independently — it couples a business rule to a screen or an endpoint. A button that contains a calculation cannot be reused, and a route that decides policy cannot be governed.

**Anti-Patterns:**
- `AP-S1.103a` — A business rule (calculation, authorization decision, workflow) implemented inside a UI component, route handler, or data-access call instead of a service.

**Grounded In:**
- Sommerville, *Software Engineering* 10e — ch. 6, Architectural Design (layered style; cohesion and coupling)

---

### S1.104 — Data Access Through Repositories

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.104 |
| **Priority**    | High |
| **Applies To**  | All Stacks · all systems with persistence |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.103` · `S2.28` (query discipline) |
| **Enforced By** | review · semantic tier · reliable-tier rules (raw-SQL detection) |

**Standard:**
Persistence is reached only through a repository / data-access layer. No raw database client, ORM call, or query is issued directly from UI, routes, or service logic — they call repository methods that own the data contract.

**Rationale:**
Scattered direct data access makes the data contract un-auditable and un-changeable; one schema change then ripples through the whole codebase. A repository boundary makes persistence swappable and testable, and is the single place data rules are enforced.

**Anti-Patterns:**
- `AP-S1.104a` — A database/ORM call (raw SQL, `prisma.*`, `psycopg2`, `$queryRaw`) issued outside a repository — from a route, a service, or the UI.

**Grounded In:**
- Sommerville, *Software Engineering* 10e — ch. 6, Architectural Design (repository pattern)
- Coronel & Rob, *Database Systems* — Database Design (the database serves the information system)

---

### S1.105 — No Hardcoded Configuration or Magic Values

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.105 |
| **Priority**    | High |
| **Applies To**  | All Stacks · all systems |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S2.10` (config & secrets) · `S1.103` |
| **Enforced By** | review · semantic tier · reliable-tier rules (secret/DSN detection) |

**Standard:**
Values that vary by environment, or that carry meaning, are named and sourced from configuration or named constants — never inlined as literals in code. Secrets are configuration, never literals.

**Rationale:**
A hardcoded value is a deployment-time decision frozen into source: changing it requires a code change and redeploy, and a magic number with no name cannot be understood or audited.

**Anti-Patterns:**
- `AP-S1.105a` — An environment-specific value, credential, URL, threshold, or magic number inlined as a literal instead of named configuration.

---

### S1.106 — Don't Repeat Yourself; Shared Code Is Shared

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.106 |
| **Priority**    | Standard |
| **Applies To**  | All Stacks · all systems |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.3` (single concern) |
| **Enforced By** | review · semantic tier |

**Standard:**
Logic, types, and constants used in more than one place live once in a shared module/library and are imported. Necessary duplication is justified in a comment; unnecessary duplication is forbidden.

**Rationale:**
Copy-pasted logic drifts — a fix applied to one copy and missed in another is a class of bug that does not exist when there is a single source. Shared definitions keep meaning consistent across the system.

**Anti-Patterns:**
- `AP-S1.106a` — The same logic, type, or constant copy-pasted across modules instead of extracted into a shared library.

**Grounded In:**
- Sommerville, *Software Engineering* 10e — ch. 9, Software Evolution (duplicate code)

---

### S1.107 — The Simplest Correct Solution

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S1.107 |
| **Priority**    | Standard |
| **Applies To**  | All Stacks · all systems |
| **Phase**       | Phase 0 — Foundation |
| **Depends On**  | `S1.5` (controlled imperfection) · `protocols/build-lifecycle.md` |
| **Enforced By** | review · semantic tier |

**Standard:**
Among solutions that satisfy the requirement and the standards, the simplest and lightest one is the required one. Abstraction, indirection, or generality that no current requirement or standard demands is not added. *Build smart, not hard; make it exist first, then make it beautiful later.*

**Rationale:**
Unrequired complexity is permanent cost — it must be read, tested, and maintained forever to serve a need that may never arrive. The best solution solves the problem and nothing more.

**Anti-Patterns:**
- `AP-S1.107a` — Speculative abstraction, premature optimization, or polish added before the foundation exists and passes its lifecycle loop.

**Grounded In:**
- Sommerville, *Software Engineering* 10e — ch. 9, Software Evolution (speculative generality)

---

## Anti-Patterns Index

All anti-patterns from C1 in one scannable table for fast reference during code review
and constitutional auditing.

| ID | Anti-Pattern | Violated Standard | Priority |
|----|-------------|-------------------|----------|
| AP-S1.1a | Opening a feature branch before proposal is approved | S1.1 | Critical |
| AP-S1.1b | "Exploratory code" written in a feature branch | S1.1 | Critical |
| AP-S1.2a | Starting implementation to figure out data flow as you go | S1.2 | Critical |
| AP-S1.2b | Asking AI to decide layer placement without evaluating the answer | S1.2 | Critical |
| AP-S1.3a | PR that adds a feature and fixes an unrelated bug | S1.3 | High |
| AP-S1.3b | Service function that queries, formats, and logs in one function | S1.3 | High |
| AP-S1.3c | Commit message using "and" to describe changes | S1.3 | High |
| AP-S1.4a | Using Next.js for one feature on an Angular system | S1.4 | Critical |
| AP-S1.4b | Stack change for preference or familiarity reasons | S1.4 | Critical |
| AP-S1.5a | Holding a passing, tested feature from production for polish | S1.5 | Standard |
| AP-S1.5b | Skipping post-mortem because the issue was already fixed | S1.5 | Standard |
| AP-S1.6a | Extending a sprint because tickets are incomplete | S1.6 | Standard |
| AP-S1.6b | Running a one-week sprint for "urgent delivery" | S1.6 | Standard |
| AP-S1.7a | Accepting an L-sized ticket into a sprint as-is | S1.7 | High |
| AP-S1.7b | Sizing tickets during the sprint | S1.7 | High |
| AP-S1.8a | Assuming 100% capacity is available for feature work | S1.8 | Standard |
| AP-S1.8b | Adding tickets mid-sprint without removing equivalent capacity | S1.8 | Standard |
| AP-S1.9a | Working around a blocker without raising it | S1.9 | High |
| AP-S1.9b | Raising a blocker in a private message | S1.9 | High |
| AP-S1.10a | Skipping retrospective because "everything went fine" | S1.10 | Standard |
| AP-S1.10b | Retrospective conducted without documenting the outcome | S1.10 | Standard |
| AP-S1.11a | Posting standup at end of day as a summary | S1.11 | Standard |
| AP-S1.11b | Skipping standup because "nothing changed" | S1.11 | Standard |
| AP-S1.12a | Resolving review disagreement via DM without PR thread record | S1.12 | Standard |
| AP-S1.12b | Architectural decision made in chat without GitHub capture | S1.12 | Standard |
| AP-S1.13a | Overriding a standard because a senior engineer disagrees | S1.13 | High |
| AP-S1.13b | Technical disagreement left unresolved in a PR thread | S1.13 | High |
| AP-S1.14a | Waiting for a meeting to review a PR | S1.14 | High |
| AP-S1.14b | Reviewing a PR weeks after it was opened | S1.14 | High |
| AP-S1.16a | Branch named without type prefix or descriptive scope | S1.16 | High |
| AP-S1.16b | Branch name containing "and" | S1.16 | High |
| AP-S1.17a | Disabling branch protection to push a hotfix directly | S1.17 | Critical |
| AP-S1.17b | Merging a PR while CI is failing | S1.17 | Critical |
| AP-S1.18a | Branch accumulating more than one sprint's commits | S1.18 | Standard |
| AP-S1.18b | Keeping a merged branch alive "for reference" | S1.18 | Standard |
| AP-S1.19a | Commit messages: "updates", "fix stuff", "wip", "temp" | S1.19 | High |
| AP-S1.19b | One giant commit containing all feature layers | S1.19 | High |
| AP-S1.19c | Past tense commit messages ("added" instead of "add") | S1.19 | Standard |
| AP-S1.20a | Full `git push origin {name}` on every push without establishing tracking | S1.20 | Standard |
| AP-S1.21a | Opening PR and investigating CI failures before syncing main | S1.21 | High |
| AP-S1.22a | Using auto-generated squash message from GitHub | S1.22 | Critical |
| AP-S1.22b | Merge commit to preserve feature branch history | S1.22 | Critical |
| AP-S1.23a | Skipping local branch deletion after merge | S1.23 | Standard |
| AP-S1.23b | Closing GitHub Issue before staging verification | S1.23 | High |
| AP-S1.24a | Direct push to `main` during a production incident | S1.24 | Critical |
| AP-S1.24b | Skipping post-mortem because the hotfix resolved the incident | S1.24 | High |
| AP-S1.25a | Reading only the parts of a constitution that seem relevant | S1.25 | Critical |
| AP-S1.25b | Reading constitutions once and never re-reading after amendments | S1.25 | Critical |
| AP-S1.26a | Making ungoverned technical decision without raising a gap | S1.26 | High |
| AP-S1.26b | Asking AI to fill a constitutional gap without an amendment | S1.26 | High |
| AP-S1.27a | Opening a branch before proposal is approved | S1.27 | Critical |
| AP-S1.27b | All layers in one commit at end instead of per-layer commits | S1.27 | High |
| AP-S1.28a | Answering gate check "yes" without demonstrating the answer | S1.28 | Critical |
| AP-S1.29a | Proposal with placeholder text in any field | S1.29 | Critical |
| AP-S1.29b | Proposal written after the code | S1.29 | Critical |
| AP-S1.30a | Creating Issue and branch simultaneously with the proposal | S1.30 | Critical |
| AP-S1.31a | Branch created from another feature branch instead of main | S1.31 | High |
| AP-S1.32a | Building UI component before data interface | S1.32 | Critical |
| AP-S1.32b | Tests written after all layers are complete | S1.32 | Critical |
| AP-S1.33a | `git add .` at the end of the feature — all layers in one commit | S1.33 | High |
| AP-S1.33b | Committing a layer before its tests pass | S1.33 | High |
| AP-S1.34a | Submitting PR with intent that reviewers catch what author missed | S1.34 | Critical |
| AP-S1.35a | PR description field empty or with placeholder text | S1.35 | High |
| AP-S1.35b | Screenshots missing for a UI change | S1.35 | High |
| AP-S1.36a | "While I was in the file, I also fixed…" bundled into PR | S1.36 | Critical |
| AP-S1.37a | Fixing a review comment without responding in the PR thread | S1.37 | High |
| AP-S1.37b | Arguing a review comment in the PR thread | S1.37 | High |
| AP-S1.38a | Treating all review comments as Must Fix | S1.38 | Standard |
| AP-S1.38b | Treating a constitutional violation as a Nitpick | S1.38 | High |
| AP-S1.40a | Closing GitHub Issue immediately on merge before staging completes | S1.40 | High |
| AP-S1.41a | "I'll add tests in a follow-up PR" | S1.41 | Critical |
| AP-S1.42a | WIP commits in PR: "wip", "temp save", "checkpoint" | S1.42 | High |
| AP-S1.42b | Fix-typo commit instead of amending the previous commit | S1.42 | Standard |
| AP-S1.43a | Self-approving a PR in a team context | S1.43 | Critical |
| AP-S1.43b | "It's just a one-line change" bypassing review | S1.43 | Critical |
| AP-S1.44a | `console.log` left in merged code | S1.44 | High |
| AP-S1.44b | Commented-out code with "remove this later" note | S1.44 | High |
| AP-S1.45a | Opening PR with intent to complete self-review during review cycle | S1.45 | Critical |
| AP-S1.45b | Treating the self-review checklist as a formality | S1.45 | Critical |
| AP-S1.46a | PR description "see the code" for the What Changed field | S1.46 | High |
| AP-S1.46b | Screenshots missing for a UI PR | S1.46 | High |
| AP-S1.47a | Fix commit without responding in the PR thread | S1.47 | High |
| AP-S1.47b | Re-requesting review before all Must Fix items are resolved | S1.47 | High |
| AP-S1.47c | Arguing a review comment in the PR thread | S1.47 | High |
| AP-S1.48a | `"strict": false` in tsconfig | S1.48 | Critical |
| AP-S1.48b | `@ts-ignore` without a GitHub Issue reference | S1.48 | High |
| AP-S1.49a | `const data: any = response.json()` | S1.49 | Critical |
| AP-S1.49b | Casting to `any` to resolve a type error | S1.49 | Critical |
| AP-S1.50a | Relying on inferred return types for service functions | S1.50 | High |
| AP-S1.52a | `req.body.fieldName` accessed without Zod parsing | S1.52 | Critical |
| AP-S1.52b | Zod schemas written manually, diverging from OpenAPI contract | S1.52 | High |
| AP-S1.53a | TypeScript `enum` keyword for constant value sets | S1.53 | Standard |
| AP-S1.55a | Single-letter generic `T` in service function signatures | S1.55 | Guidance |
| AP-S1.56a | `../../../services/...` relative import chain | S1.56 | High |
| AP-S1.57a | Unannotated Python function parameters | S1.57 | Critical |
| AP-S1.57b | `# type: ignore` without a GitHub Issue reference | S1.57 | High |
| AP-S1.58a | `async def create_student(data: dict)` — raw dict parameter | S1.58 | Critical |
| AP-S1.58b | Pydantic model defined after the endpoint logic | S1.58 | Critical |
| AP-S1.59a | Database session created inside route handler body | S1.59 | High |
| AP-S1.59b | Authentication check called directly inside the handler | S1.59 | High |
| AP-S1.60a | Synchronous database driver inside async FastAPI handler | S1.60 | High |
| AP-S1.60b | `requests.get()` inside an async handler | S1.60 | High |
| AP-S1.64a | `UserProfile.tsx` or `userProfile.tsx` file names in TypeScript | S1.64 | High |
| AP-S1.65a | Single file exporting multiple primary concerns | S1.65 | High |
| AP-S1.66a | Importing from internal paths of another module | S1.66 | Critical |
| AP-S1.67a | `if (score > 65)` — magic number in business logic | S1.67 | Standard |
| AP-S1.67b | `setTimeout(fn, 900000)` — magic number | S1.67 | Standard |
| AP-S1.68a | `process.env.DATABASE_URL` read inline without startup validation | S1.68 | Critical |
| AP-S1.70a | ESLint rule disabled in configuration to suppress errors | S1.70 | Critical |
| AP-S1.76a | Critical security comment marked as Nitpick to avoid conflict | S1.76 | Critical |
| AP-S1.77a | Approving PR after reading description and first two files only | S1.77 | Critical |
| AP-S1.77b | Approving PR because a senior engineer already approved it | S1.77 | Critical |
| AP-S1.80a | Review comment: "This is wrong." without standard citation | S1.80 | High |
| AP-S1.83a | API endpoint documented in Notion instead of OpenAPI spec | S1.83 | Critical |
| AP-S1.86a | `// Loop through all students` — comment describes the code | S1.86 | Standard |
| AP-S1.86b | Commented-out code left with an explanation comment | S1.86 | Standard |
| AP-S1.88a | Angular component created with `@NgModule` declarations | S1.88 | Critical |
| AP-S1.90a | `ngModel` used for two-way data binding in Angular forms | S1.90 | Critical |
| AP-S1.98a | CI installs non-frozen (or editable) so a transitive bump silently changes the build | S1.98 | Critical |
| AP-S1.99a | PR with no linked issue or missing type/milestone/project/labels/assignee | S1.99 | Critical |
| AP-S1.100a | AI trailer, AI tool name, or AI bot co-author in a commit, PR, issue, branch, or filename | S1.100 | Critical |
| AP-S1.101a | Refactoring untested legacy code with no characterization test pinning prior behaviour | S1.101 | Critical |
| AP-S1.102a | Declaring adoption "done" with unsatisfied standards and no recorded exceptions | S1.102 | Standard |

---

## Cross-Constitution Dependency Map

**C1 depends on:**
- `C0` — Constitutional Order: governance framework, terminology, amendment protocol,
  standard ID format, pre-build checklist
- `C3` — Auth Constitution: auth boundary standards referenced in self-review Quadrant 1
- `C7` — Testing Constitution: test-alongside-implementation (S1.32, S1.33, S1.41)

**The following constitutions depend on C1:**
- `C2` Backend: feature lifecycle and Git standards apply to all backend development
- `C3` Auth: feature lifecycle and code quality standards apply to all auth code
- `C4` Frontend: layer build order (S4.81) depends on S1.32; Git standards apply
- `C5` Database: feature lifecycle applies to all schema and migration work
- `C6` Full-Stack Architecture: engineering standards apply to all stack decisions
- `C7` Testing: test discipline in C1 (S1.32, S1.33, S1.41) is the process layer
- `C8` Platform Reliability: hotfix process (S1.24) referenced in incident runbooks
- `C9` Product & Feature: feature lifecycle (S1.27–S1.40) delivers every product feature
- `C10` AI Collaboration: all engineering process standards define the context in which
  AI participates — AI must know C1 fully to operate correctly

---

## Amendment Log

| Version | Date | Change | Reason |
|---------|------|--------|--------|
| v1.0 | 2026-05-08 | Initial lock — merged from Team & Process Constitution v3.0, Code Quality Constitution v3.0, and MentorConnect team workflow intelligence | Version reset. Three documents unified into one Engineering Standards Constitution. MentorConnect 8-phase feature lifecycle added (S1.27–S1.40). Author quality gates formalised (S1.45–S1.47). Self-review checklist with 4 quadrants (S1.45). PR description template (S1.46). Review response protocol (S1.47). Git recovery procedures added (S1.93–S1.97). First-push upstream tracking (S1.20). Branch sync procedure (S1.21). Squash merge mandate (S1.22). Post-merge cleanup (S1.23). |
| v1.1 | 2026-06-20 | **Added Part 17 — Dependency & Build Reproducibility (S1.98 — Reproducible Dependency Installs):** a committed lockfile pins the full transitive tree and CI installs frozen (`uv sync --frozen` / `npm ci` / equivalent), failing on lock↔manifest drift; editable/unpinned installs are never the CI path. Anti-pattern AP-S1.98a added. Count 97→98. (C0 §8 amendment A-4; FundsLink Stage-00 hardening evidence generalised — an editable `pip install -e` let a transitive bump red a previously-green main; migrated to `uv` + `--frozen`; Founder L4 approval 2026-06-20.) | An unpinned install resolves at build time, so a transitive upgrade can red a previously-green main with nothing in the diff. A lockfile + frozen CI install makes the dependency tree a reviewed, versioned artifact. |

| v1.2 | 2026-06-21 | **Added Part 18 — Operating-Practice & Adoption Governance (S1.99–S1.102):** S1.99 branch→issue→PR→merge with full issue/PR metadata; S1.100 no-AI-references rule on the GitHub metadata surface; S1.101 characterization tests before any brownfield refactor; S1.102 adoption complete only when satisfied or excepted. Anti-patterns AP-S1.99a–AP-S1.102a added. Count 98→102. (C0 §8 amendment; evidence: metadata-less PRs and an AI co-author found during the v2.0 restructure; brownfield safety; Founder L4 approval 2026-06-21.) | Operating practices are part of the product: an ungoverned workflow and AI-tainted history undermine an AI-governance platform, and unsafe brownfield conversion breaks working systems. |
| v1.3 | 2026-06-22 | **Added Part 19 — Architectural Discipline (S1.103–S1.107):** S1.103 logic lives in its layer (no business logic in UI/transport/data-access); S1.104 data access through repositories (no raw DB/ORM calls outside a repository); S1.105 no hardcoded configuration or magic values; S1.106 DRY — shared code is shared; S1.107 the simplest correct solution ("build smart, not hard"). Anti-patterns AP-S1.103a–AP-S1.107a added. Count 102→107. (C0 §8 amendment per ADR-005 workstream A; layer/context detection reserved for the semantic tier; Founder L4 approval 2026-06-22.) | The existing corpus encoded process and sector specifics but not the universal architectural discipline every system needs; these make separation of concerns, data-access boundaries, configuration hygiene, reuse, and simplicity first-class law. |

| v1.4 | 2026-07-30 | **Amended S1.19 — Conventional Commit Format:** added the `govern` and `decision` types for constitutional amendments and ADRs, with usage guidance and examples; corrected `Enforced By`, which named Commitlint and a CI format check that do not exist, to name the structural probe that actually enforces it. `harden` was considered and **refused** — security work is a `fix` when it closes a vulnerability and `chore`/`refactor` otherwise. Count unchanged at 107. (C0 §8 amendment; evidence: four commits over four months reached for `govern`/`decision`, which no existing type covers — the probe reported 90% conformance; Founder L4 approval 2026-07-30.) | Ratifying a standard and recording an architectural decision are legitimate acts that change no code, so no code-shaped type fits them. A standard that leaves a recurring, lawful act unnamed will be violated by the people acting in good faith. |
| v1.5 | 2026-07-31 | **Added `Grounded In` provenance to Part 19 (S1.103, S1.104, S1.106, S1.107):** each now cites where its requirement is established in the engineering canon — S1.103 and S1.104 in architectural design (layered style, cohesion and coupling, the repository pattern), S1.106 and S1.107 in software evolution (duplicate code, speculative generality). **S1.105 was examined and deliberately left uncited** — no source in the corpus establishes it, and an unverifiable citation is worse than none. Count unchanged at 107; no standard's meaning, scope, priority, or enforcement changed. (C0 §3.1 `Grounded In`, added by the C0 v1.1 amendment; ADR-007 Stage 0; citations verified against the sources with `governova-ingest` per `protocols/practice-to-standard.md`.) | Part 19 was a rediscovery of established practice and said so nowhere, which understated it: a standard defended by citation is defensible to an architecture board or a regulator, while one defended by assertion is house style. |

---

> **LOCKED — v1.5 — 2026-07-31** (amended; originally locked v1.0 2026-05-08)
>
> This document is locked. No standard may be added, removed, or modified
> without following the Amendment Protocol defined in C0 §8.
> Amendments take effect only after commit to `governova`
> with a version bump and amendment log entry.
