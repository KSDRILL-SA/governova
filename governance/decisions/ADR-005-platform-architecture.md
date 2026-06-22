# ADR-005 — Governova Platform Architecture (3-plane model)

---

| Attribute   | Value |
|-------------|-------|
| **ID**      | ADR-005 |
| **Date**    | 2026-06-22 |
| **Status**  | accepted |
| **Supersedes** | — |
| **Relates To** | S10.1, S1.2 |

---

## Context

Governova began as a constitution-as-data engine with local CLI / IDE / MCP / CI surfaces —
everything runs in-repo, free, offline. The next stage of the product introduces capabilities
that a purely local tool cannot serve:

- **Onboarding** — handing the product to individuals, teams, businesses, companies, or whole
  organisations who may already have governance, and who must be able to (1) map Governova onto
  it, (2) scan-and-learn from it non-destructively, or (3) scan-learn-and-rewrite it.
- **Always-on improvement** — Governova should keep learning a user's lifecycle and proposing
  governance improvements continuously, not only while they work.
- **Accounts, subscriptions, and metered intelligence** — account creation, login, settings,
  billing, and an AI brain with effort tiers and usage cycles.

These require a hosted service, identity, billing, and a metered LLM gateway — a different
deployment model from the local engine. This ADR records how the whole vision fits together so
we build against one durable blueprint.

---

## Decision

Adopt a **3-plane architecture** and sequence delivery so the governance substance is made
world-class before the SaaS control plane is built.

### The three planes

1. **Open Engine (local, free, offline).** The current product: constitution-as-data, the
   compiler, deterministic enforcement, the Score / Board Report / System Bible, and all
   surfaces. No account required. This is the wedge and the trust-builder; it stays free and
   offline forever.
2. **Governova Cloud (hosted SaaS).** Identity, organisations/teams, subscriptions and billing,
   the **Intelligence Gateway** (metered AI with effort tiers and usage cycles), the
   **Always-On Learning** workers, and the brownfield onboarding service.
3. **Clients.** The CLI, IDE extension, and MCP server authenticate to the Cloud via account
   login; deterministic features keep working offline and free, while AI features call the
   metered gateway.

### The four workstreams

- **A — Constitution corpus (universal).** Refactor sector-specific standards so the *core* is
  universal and applies to any platform/sector, with sector specifics living in
  `constitution/domains/{fintech,healthtech,…}`. Add the broad software-engineering best
  practices not yet encoded, several of which become deterministic rules: repository pattern (no
  direct DB access outside repositories), no business logic in the UI layer, no hardcoded
  values, DRY / shared libraries, no needless duplication. Governing beyond software (business /
  financial process governance) is a later major expansion of the constitution's model.
- **B — Build lifecycle & methodology.** A phase-ordered, dependency-first build: Phase 00
  (stack + project structure + environment) → database → auth → backend → frontend → the rest;
  core components first because everything depends on them. Each phase runs the loop
  **Build → Harden → Self-review (builder) → External-review (a different engineer) → Handoff.**
  The external reviewer exists specifically to catch the builder's blind spots. Governova
  generates per-engineer handoffs (what/why/where/what-not-to-touch) from its full knowledge of
  the rules; engineers may edit them and Governova refines. Two principles are constitutionalised:
  *"make it exist first, then make it beautiful later"* (lay the foundation, then harden on top)
  and *"build smart, not hard"* (enforce the single simplest, lightest, best-recommended solution).
- **C — Brownfield onboarding.** Three user-chosen modes: **Map/Adapt**, **Scan & Learn**
  (read-only), **Scan, Learn & Rewrite** (diff + review before applying). The **Always-On
  Learning** engine periodically re-analyses the repo and decisions to propose amendments;
  it requires explicit consent and a defined data-handling/privacy posture.
- **D — Governova Cloud.** Account login via **OAuth 2.0 Device Authorization Grant**
  (`governova login` → browser approval → token in the OS keychain; API keys remain only as a
  CI/automation fallback). Subscriptions and org/team management. The **Intelligence Gateway**
  meters AI usage by **effort tier (Low / Medium / High / Max** = model size × reasoning depth ×
  review passes**)** against a **credit budget** that accrues hourly with a cooldown window when
  capped, and degrades gracefully (downshift/queue near the cap, never hard-cut mid-task).

### Sequencing (locked)

- **Phase 1 — A + B.** Make the governance itself world-class. Extends what exists; ships clean
  with no new infrastructure.
- **Phase 2 — C.** Brownfield onboarding, using the existing provider-agnostic semantic tier for
  the AI parts.
- **Phase 3 — D.** The Cloud control plane (the largest new system).

---

## Consequences

### What becomes easier

- One blueprint reconciles every requested capability; each workstream is independently shippable
  through the branch → issue → PR → merge workflow.
- Deterministic governance stays free and offline (the wedge); the AI brain is the metered,
  subscription-gated value — a clean separation and a clean business model.
- Phase 1 (corpus + lifecycle) delivers immediate, infrastructure-free value and de-risks the
  later SaaS build.

### What becomes harder

- Plane 2 is a genuine SaaS build (backend, database, identity, billing, a metered LLM gateway) —
  months of work and real operational surface.
- Always-On Learning ingests user activity; consent, data handling, retention, and security
  become first-class design concerns, not afterthoughts.
- "Beyond software" governance requires generalising the constitution from code standards to
  process standards — a major model change reserved for later.

### Constitutional alignment

- Reinforces S10.1 (AI collaboration is governed, not ad-hoc) and S1.2 (logic and structure are
  deliberate, reviewable decisions). The build-lifecycle workstream (B) extends the existing
  `protocols/frameworks/ai-assisted-software-development-workflow` and
  `ai-review-challenge-framework`. The brownfield workstream (C) extends the Brownfield Adoption
  Standard and the External & Ecosystem Governance protocol.
- The no-AI-references rule continues to apply to all GitHub metadata; the product itself using
  LLMs is product functionality and remains provider-agnostic (as the semantic tier already is).

### Open questions (resolved in later, dedicated ADRs)

- The exact token-credit economics per subscription tier (deep research before Plane 2/D).
- The privacy/consent and data-retention model for Always-On Learning.
- The model for governing non-software (business/financial) processes.
