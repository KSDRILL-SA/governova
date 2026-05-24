# C9 — Product & Feature Constitution

---

| Attribute          | Value                                                              |
|--------------------|--------------------------------------------------------------------|
| **Document**       | C9 — Product & Feature Constitution                                |
| **Organisation**   | KSDRILL SA                                                         |
| **Version**        | v1.0                                                               |
| **Status**         | LOCKED                                                             |
| **Locked**         | 2026-05-08                                                         |
| **Next Review**    | 2026-08-08                                                         |
| **Applies To**     | All Systems · Both Stacks                                          |
| **Paired With**    | — (The Crown Jewel — Phase 3, no implementation guide)             |

---

> *"Build what solves the problem. Nothing more. Nothing less."*

---

## Opening Statement

This is the Crown Jewel. Every other constitution governs how systems are built. This constitution governs what gets built and why. Every feature decision, every v1 scope call, every roadmap item must pass through this constitution. The other ten constitutions tell engineers how to work. This one tells them what work is worth doing.

Product and technical constitutions are deliberately separated in phase order (C9 is Phase 3, after all technical constitutions are locked). Product decisions must be made against a stable technical foundation — knowing what is architecturally possible, what the database supports, what the authentication system handles, and what the testing infrastructure validates. A product decision that ignores technical constraints is not a product decision — it is a fantasy.

This constitution does not govern how features are implemented — that is C2 through C8. It does not govern how AI participates in building — that is C10. What this constitution governs is the product itself: the systems being built, why they exist, what problems they solve, how features are qualified for inclusion, and how the roadmap is governed.

The KSDRILL SA mission is stated explicitly: build what should already exist, with the precision, care, and permanence it deserves. Every feature decision is a test of whether the proposed work moves toward that mission or away from it.

---

## Table of Contents

| Part | Title | Standards |
|------|-------|-----------|
| Part 1 | Product Vision & Philosophy | S9.1–S9.6 |
| Part 2 | Feature Governance | S9.7–S9.13 |
| Part 3 | MVP Definitions | S9.14–S9.20 |
| Part 4 | User Feedback Integration | S9.21–S9.25 |
| Part 5 | Roadmap Governance | S9.26–S9.30 |
| Anti-Patterns Index | — | AP-S9.* |
| Cross-Constitution Dependency Map | — | — |
| Amendment Log | — | — |

---

## Part 1 — Product Vision & Philosophy (`S9.1`–`S9.6`)

---

### S9.1 — Every Platform Solves a Real Problem Felt by Real People

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S9.1 |
| **Priority**    | Critical |
| **Applies To**  | All Systems |
| **Phase**       | Phase 3 — Product & Intelligence |
| **Depends On**  | — |
| **Enforced By** | Feature proposal review (S9.7) |

**Standard:**
Every KSDRILL SA platform must solve a problem that real people experience in their daily lives — not a technology problem, an engineering problem, or a problem invented to justify a technology choice. The problem must be documented before the solution is designed. If the problem cannot be described in one plain-English sentence understood by the person experiencing it, the problem statement is not complete.

**Rationale:**
Products built around technology choices rather than human problems are abandoned when the technology evolves. Products built around human problems endure as long as the problem exists. KSDRILL SA builds for endurance.

**Anti-Patterns:**
- `AP-S9.1a` — "We should build a blockchain-based scholarship system" — a technology choice, not a problem statement. The problem is student funding exclusion; the technology follows.

**Cross-References:** `S1.27` (feature lifecycle — problem statement is Step 1)

---

### S9.2 — The Primary User Workflow Is Sacred

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S9.2 |
| **Priority**    | Critical |
| **Applies To**  | All Systems |
| **Phase**       | Phase 3 — Product & Intelligence |
| **Depends On**  | `S9.1` (problem definition) |
| **Enforced By** | Feature proposal review, sprint planning |

**Standard:**
Every platform has one primary user workflow — the sequence of steps a user must complete to receive the core value. This workflow is the product. Everything else is a feature. The primary workflow works flawlessly before any secondary feature is built. A platform with a beautiful admin panel and a broken primary workflow is a worse product than one with a plain interface and a working primary workflow.

| System | Primary Workflow |
|--------|----------------|
| FundsLink Academy | Student creates profile → submits application → receives AI-matched funding options |
| Maphophe Community System | Resident creates account → submits service request → ward admin reviews → resident sees status |
| KSDRILL Reserve Bank | User creates account → sets savings goal → makes first deposit → sees balance and interest |
| SyncUp Creator Platform | Creator discovers another creator → sends structured pitch → receives negotiated response |

**Anti-Patterns:**
- `AP-S9.2a` — Building analytics dashboards before the primary workflow is complete and tested — dashboards have no data if the primary workflow doesn't work.

**Cross-References:** `S9.9` (Groups 1+2 in v1 only), `S9.14` (MVP done criteria)

---

### S9.3 — Sequential Build — One System Fully Before the Next Begins

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S9.3 |
| **Priority**    | Critical |
| **Applies To**  | All Systems |
| **Phase**       | Phase 3 — Product & Intelligence |
| **Depends On**  | `S9.1`, `S9.2` |
| **Enforced By** | Sprint planning · Owner decision |

**Standard:**
KSDRILL SA builds one flagship system at a time. The build order is locked: FundsLink Academy (Q2 2026) → Maphophe Community System (Q3 2026) → KSDRILL Reserve Bank (Q4 2026) → SyncUp Creator Platform (Q1 2027). No parallel platform development. FundsLink MVP must ship before Maphophe development begins. Each system builds engineering confidence and user feedback loops before the next begins.

**Rationale:**
Parallel platform development splits focus, produces lower-quality work on all platforms, and delays the user feedback that informs subsequent platform decisions. Sequential development produces one working system at a time.

**Anti-Patterns:**
- `AP-S9.3a` — Starting Maphophe development while FundsLink primary workflow is incomplete — the incomplete system generates no user feedback, and the second system starts without the learnings from the first.

**Cross-References:** `S9.16` (build order locked in system register)

---

### S9.4 — Design-First — Full Architecture Locked Before the First Line of Code

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S9.4 |
| **Priority**    | Critical |
| **Applies To**  | All Systems |
| **Phase**       | Phase 3 — Product & Intelligence |
| **Depends On**  | `S1.1` (C1 — design first), `S6.6` (ADR before development) |
| **Enforced By** | Pre-build checklist (C0 §11) |

**Standard:**
No platform begins coding until the full system design is locked: stack ADR, database schema, module definitions, interface designs (wireframes or mockups), OpenAPI contract for all v1 endpoints, and constitutional registration in system context file. "We'll figure it out as we build" produces systems that cannot be maintained.

**Anti-Patterns:**
- `AP-S9.4a` — Starting the FundsLink Angular app before the FastAPI endpoint contracts are written — the Angular components are built against assumptions that the API then violates.

**Cross-References:** `S1.1` (C1 design-first), `S6.6` (ADR), `S2.7` (OpenAPI first)

---

### S9.5 — African Context Is a Design Constraint

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S9.5 |
| **Priority**    | High |
| **Applies To**  | All Systems |
| **Phase**       | Phase 3 — Product & Intelligence |
| **Depends On**  | `S9.1` (real problem, real people) |
| **Enforced By** | Design review |

**Standard:**
KSDRILL SA builds for South African users first. Design constraints are not optional: Maphophe is optimised for low-bandwidth rural connections (PWA offline-ready, minimum data usage). FundsLink is designed for students without reliable internet (fast load times, form-saving, resume-on-reconnect). Reserve Bank addresses the South African savings behaviour gap with enforcement mechanics. These constraints are primary design requirements — not accessibility add-ons retrofitted before launch.

**Anti-Patterns:**
- `AP-S9.5a` — Designing FundsLink with a 3MB initial bundle "to be optimised later" — students on mobile data cannot afford to load 3MB per visit; this is a launch blocker, not a later concern.

**Cross-References:** `S4.2` (mobile-first 320px), `S4.69` (Lighthouse performance ≥ 80)

---

### S9.6 — GrowthCore Solutions Is a Separate Entity

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S9.6 |
| **Priority**    | High |
| **Applies To**  | All Systems |
| **Phase**       | Phase 3 — Product & Intelligence |
| **Depends On**  | — |
| **Enforced By** | Owner decision |

**Standard:**
KSDRILL SA and GrowthCore Solutions are separate companies with separate missions. KSDRILL SA builds platforms solving real-world challenges. GrowthCore Solutions delivers client web development, marketing, and analytics services. No KSDRILL SA system is built as a GrowthCore client project. Sprint work never overlaps between the two entities. Constitutional frameworks are KSDRILL SA internal governance — not licensed to GrowthCore client projects without explicit written authorisation.

**Anti-Patterns:**
- `AP-S9.6a` — Using KSDRILL SA sprint capacity to build a GrowthCore client deliverable — conflates sprint capacity across entities; KSDRILL SA governance does not apply to GrowthCore work.

**Cross-References:** `S1.6` (sprint planning — one entity per sprint)

---

## Part 2 — Feature Governance (`S9.7`–`S9.13`)

---

### S9.7 — 5 Gate Questions — Every Feature Must Pass All Five

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S9.7 |
| **Priority**    | Critical |
| **Applies To**  | All Systems |
| **Phase**       | Phase 3 — Product & Intelligence |
| **Depends On**  | `S9.2` (primary workflow), `S1.27` (feature lifecycle) |
| **Enforced By** | Feature proposal review |

**Standard:**
Every feature proposed for any platform — regardless of how small or "obvious" — must pass all five gate questions before being added to a sprint. Failing any gate defers the feature to v2. No exceptions for "quick wins" or "obviously needed" features.

| Gate | Question | Failure → |
|------|----------|-----------|
| Q1 | Does a real user need this to complete the primary workflow? | Defer to v2 |
| Q2 | Does removing this feature break the primary workflow or core value? | Defer to v2 |
| Q3 | Can this be designed, built, and tested within 2–4 weeks? | Reduce scope or defer |
| Q4 | Does the OpenAPI contract exist? Is the DB schema defined? | No code until yes |
| Q5 | Has a real user (not the builder) confirmed they need this? | User research required |

**Anti-Patterns:**
- `AP-S9.7a` — "This is obviously needed, we don't need to answer the gate questions" — every feature that ever caused scope creep was "obviously needed" by its proposer.

**Cross-References:** `S1.27` (feature lifecycle proposal), `S9.8` (feature group classification)

---

### S9.8 — Feature Groups — Classification by Impact on Primary Workflow

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S9.8 |
| **Priority**    | Critical |
| **Applies To**  | All Systems |
| **Phase**       | Phase 3 — Product & Intelligence |
| **Depends On**  | `S9.7` (gate questions) |
| **Enforced By** | Sprint planning |

**Standard:**
Every feature that passes the 5 gates is classified into a feature group:

| Group | Definition | v1 Inclusion |
|-------|-----------|--------------|
| G1 — Core | Essential to primary workflow — user cannot complete core value without it | Always in v1 |
| G2 — Supporting | Directly supports G1 — needed for a complete primary workflow experience | In v1 where capacity allows |
| G3 — Secondary | Valuable but not needed for primary workflow | v2+ only |
| G4 — Nice-to-Have | Improves experience but does not affect primary workflow outcome | v2+ only |

**Anti-Patterns:**
- `AP-S9.8a` — Classifying an admin analytics dashboard as G1 — admin dashboards are G3; the primary workflow does not depend on analytics.

**Cross-References:** `S9.9` (Groups 1+2 in v1), `S4.71` (group build order in frontend)

---

### S9.9 — v1 Contains Maximum 6 Features — Hard Limit

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S9.9 |
| **Priority**    | Critical |
| **Applies To**  | All Systems |
| **Phase**       | Phase 3 — Product & Intelligence |
| **Depends On**  | `S9.7` (gate questions), `S9.8` (feature groups) |
| **Enforced By** | Sprint planning · Owner decision |

**Standard:**
Every platform ships v1 with a maximum of 6 features (authentication counts as one feature). If more than 6 features pass all 5 gate questions, the lowest-impact features are cut to v2. v1 ships only G1 and G2 features. G3 and G4 are v2+.

| System | v1 Feature Set |
|--------|---------------|
| FundsLink Academy | Auth + Profile + Application + AI Matching + Status = 5 |
| Maphophe Community | Auth + Announcements + Service Requests + Status = 4 |
| KSDRILL Reserve Bank | Auth + Account + Deposits + Goals + Interest View = 5 |
| SyncUp Creator Platform | Auth + Profiles + Pitch + Negotiation Engine = 4 |

**Rationale:**
A v1 with 4 flawless features outperforms a v1 with 8 half-finished features. The 6-feature limit forces ruthless prioritisation that produces a focused, high-quality first release.

**Anti-Patterns:**
- `AP-S9.9a` — "We'll add bulk export, email notifications, and an admin dashboard to v1 since they're all ready" — scope creep that delays the primary workflow shipping; these are G3/G4 features.

**Cross-References:** `S9.7` (gate questions), `S9.8` (feature groups)

---

### S9.10 — Feature Flags for All Features Beyond Initial v1 Set

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S9.10 |
| **Priority**    | Critical |
| **Applies To**  | All Systems |
| **Phase**       | Phase 3 — Product & Intelligence |
| **Depends On**  | `S5.10` (FeatureFlag table) |
| **Enforced By** | Code Review |

**Standard:**
Every new feature beyond the initial v1 set ships behind a feature flag stored in the `FeatureFlag` PostgreSQL table with `enabled: false` as the default. The feature is deployed but disabled — it goes live only when the flag is enabled. Feature flags are never hardcoded. This decouples deployment from release and enables instant kill switches.

**Anti-Patterns:**
- `AP-S9.10a` — `if (process.env.FEATURE_SCHOLARSHIP_EXPORT === 'true')` — environment variable feature flags require a deployment to change; database feature flags can be toggled instantly.

**Cross-References:** `S5.10` (FeatureFlag model in Prisma)

---

### S9.11–S9.13 — Additional Feature Governance Standards

> **S9.11** — Stack impact assessed before any feature approval: Does it require a new database table? New endpoint (pushes toward the v1 endpoint limit)? New background job? New external service? Features that exceed v1 stack complexity limits are deferred.

> **S9.12** — A feature that requires switching frameworks is automatically deferred. FundsLink cannot add React components. Maphophe cannot add FastAPI. The framework assignment is locked by C6 and C1.

> **S9.13** — Feature proposals are written in plain language describing the user problem and expected behaviour — not technical specifications. Technical design is a separate document that follows a locked feature proposal.

---

## Part 3 — MVP Definitions (`S9.14`–`S9.20`)

---

### S9.14 — MVP Done Criteria — System-Specific Definition

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S9.14 |
| **Priority**    | Critical |
| **Applies To**  | All Systems |
| **Phase**       | Phase 3 — Product & Intelligence |
| **Depends On**  | `S9.2` (primary workflow), `S9.9` (v1 feature set) |
| **Enforced By** | Sprint completion criteria |

**Standard:**
MVP "done" is defined by the completion of the primary user workflow end-to-end in the production environment — not staging. MVP is not done when: features are built but not tested, the primary workflow is complete but other v1 features are broken, or the system works on the developer's machine but not in production.

| System | MVP Done When |
|--------|--------------|
| FundsLink Academy | A student can apply and receive at least one matched funding opportunity end-to-end in production |
| Maphophe Community | A resident can submit a service request and see its progress in production |
| KSDRILL Reserve Bank | A user can create an account, make a deposit, and see their balance and interest calculation in production |
| SyncUp Creator Platform | A creator can send a pitch and receive a response through the structured negotiation flow in production |

**Anti-Patterns:**
- `AP-S9.14a` — "MVP is done when it works in staging" — staging is the validation environment; production is the done environment.

**Cross-References:** `S9.2` (primary workflow), `S8.12` (production deploy gate)

---

### S9.15–S9.20 — Additional MVP Standards

> **S9.15** — MVP includes: all C3 auth requirements, all v1 database schemas migrated, all v1 API endpoints under OpenAPI contract, CI/CD pipeline green, test coverage gates passing, visual regression at 320/375/390px passing.

> **S9.16** — Build order is locked per S9.3. No system begins until the previous system's MVP is in production and has been in production for at least 2 weeks with no SEV0/SEV1 incidents.

> **S9.17** — MVP launch includes a public status page (Better Stack) and a support email address. Users experiencing issues have a way to report them.

> **S9.18** — Performance budget is part of MVP criteria: Lighthouse mobile score ≥ 80 in production. FundsLink and Maphophe target ≥ 85 given the low-bandwidth constraint (S9.5).

> **S9.19** — Accessibility is part of MVP criteria: axe-core CI gate passing (no critical/serious violations). This is enforced by C7 S7.20 but confirmed here as a product criterion, not just a technical criterion.

> **S9.20** — MVP does not include v2 features in a disabled/hidden state. Features that are not ready are not deployed — not deployed and hidden. Ship only what is done.

---

## Part 4 — User Feedback Integration (`S9.21`–`S9.25`)

> **S9.21** — User feedback is collected from real users — not from the builder's assumptions about what users want. User research is conducted before v2 scope is locked.

> **S9.22** — User feedback is documented as GitHub Issues in the system repository with the `user-feedback` label — not as informal notes or in messaging apps.

> **S9.23** — User feedback informs the next sprint's feature gate evaluation — a feature that multiple users have independently requested scores higher on Q5 (has a real user confirmed they need this?).

> **S9.24** — Quantitative metrics (active users, primary workflow completion rate, time-to-complete, error rate) are tracked from day 1 of v1 production via Vercel Analytics and Sentry. Decisions are made against data, not intuition.

> **S9.25** — A feature requested by users that fails Q1–Q4 gate questions is still deferred — user desire does not override the constitutional gate framework. Document the request in the v2 backlog.

---

## Part 5 — Roadmap Governance (`S9.26`–`S9.30`)

> **S9.26** — The roadmap is the sequence of constitutionally approved features — not a wishlist. Items on the roadmap have passed the 5 gate questions, have a feature group classification, and have a written feature proposal.

> **S9.27** — v2 scope is not locked until v1 has been in production for at least 2 weeks with quantitative usage data. v2 features are informed by real usage, not pre-launch assumptions.

> **S9.28** — Roadmap items are prioritised by: (1) primary workflow impact, (2) user feedback volume, (3) technical dependency order. Not by engineering interest, tool novelty, or feature complexity.

> **S9.29** — A roadmap item that has been on the backlog for two consecutive sprints without being started is reviewed: either it enters the current sprint as a priority, or it is moved to a formal "deferred" list with written reasoning.

> **S9.30** — The roadmap is reviewed at every quarterly constitutional review (C0 §12) — features that no longer pass the 5 gate questions given new information are removed from the roadmap.

---

## Anti-Patterns Index

| ID | Description | Violated Standard | Severity |
|----|-------------|-------------------|----------|
| `AP-S9.1a` | Technology choice presented as problem statement | S9.1 | High |
| `AP-S9.2a` | Admin dashboard before primary workflow complete | S9.2 | Critical |
| `AP-S9.3a` | Second system started before first MVP ships | S9.3 | Critical |
| `AP-S9.4a` | Angular app started before API contracts written | S9.4 | High |
| `AP-S9.5a` | 3MB initial bundle "to be optimised later" | S9.5 | High |
| `AP-S9.6a` | KSDRILL SA sprint capacity used for GrowthCore work | S9.6 | High |
| `AP-S9.7a` | Gate questions skipped for "obviously needed" feature | S9.7 | Critical |
| `AP-S9.8a` | Admin analytics dashboard classified as G1 | S9.8 | High |
| `AP-S9.9a` | G3/G4 features added to v1 because "they're ready" | S9.9 | Critical |
| `AP-S9.10a` | Feature flag in environment variable instead of database | S9.10 | High |
| `AP-S9.14a` | MVP declared done in staging | S9.14 | High |
| `AP-S9.20a` | v2 features deployed but hidden in v1 | S9.20 | Standard |

---

## Cross-Constitution Dependency Map

**This constitution depends on:**
| Dependency | Reason |
|------------|--------|
| `C0 — Constitutional Order` | Amendment protocol, review calendar |
| `C1 — Engineering Standards` | Feature lifecycle (S1.27) is the implementation of feature governance |
| `C2–C8 — All Technical Constitutions` | Feature decisions must be technically feasible against all standards |

**The following constitutions depend on this one:**
| Dependent | Reason |
|-----------|--------|
| *None* — C9 is a terminal node in the dependency graph. |

---

## Amendment Log

| Version | Date | Change | Reason |
|---------|------|--------|--------|
| v1.0 | 2026-05-08 | Initial lock — rebuilt from Product & Feature Constitution v3.0. Feature group table formalised (S9.8). v1 feature sets per system documented with counts (S9.9). MVP done criteria aligned with production environment requirement (S9.14). Performance and accessibility added as explicit MVP criteria (S9.18, S9.19). | Full system rebuild — HTML to Markdown, version reset. |

---

> **LOCKED — v1.0 — 2026-05-08**
>
> This document is locked. No standard may be added, removed, or modified
> without following the Amendment Protocol defined in C0 §8.
> Amendments take effect only after commit to `system-design-template`
> with a version bump and amendment log entry.
>
> This is Constitution 9 of 10 — the Crown Jewel. It governs what gets built.
> Every technical decision made under C2–C8 must serve a product decision made here.
