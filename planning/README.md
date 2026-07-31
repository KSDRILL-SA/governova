# planning/

Living documents that govern **how** Governova gets built. Distinct from `governance/` (which records what *has been* done) and `framework/` + `constitution/` (which define *what must be true*).

| File | Purpose |
|------|---------|
| `handoff-2026-07-31.md` | **Current engineer handoff — read this first.** State of the system, standing rules, open work, traps |
| `phase-3-brownfield.md` | **Next phase.** Staged plan for ADR-005 workstream C — onboarding systems Governova has never seen |
| `phase-2-lifecycle-completeness.md` | ADR-007 — **complete.** Retained as the worked example of a staged plan that held |
| `strengthening-roadmap.md` | Standing improvements to the engine and its evidence tiers |
| `governova-build-plan.md` | The master build plan — six phases (A–F) from zero to v1.0, with deliverables, dependencies, and locked decisions |
| `phase-a-spec.md` | Detailed spec for Phase A — constitution as data (parser, validator, schema, types) |
| `handoff-2026-07-30.md` | **Superseded.** Retained because its §3 standing rules and §5 traps are still cited |

> **Phase numbering.** `governova-build-plan.md` uses letters (A–F) for the *engine* build.
> ADR-005 and ADR-007 use numbers (Phase 1–4) for the *platform* workstreams. They are
> different sequences over the same repository, and both are live: the letters describe how
> the engine was built, the numbers describe what the platform ships next.

---

## Workflow

1. Build plan is the source of truth for **what** is being built and **when**
2. Each phase spec is drafted **before** the phase begins
3. L4 approves each spec before any branch is created
4. Specs are amended via PR — not edited silently
5. On phase completion, the build plan gets a "Phase X — Done" appendix with actual effort and lessons learned

---

*All planning documents are L1 (Propose) outputs. L4 approval is required before any L3 (build) work begins on the corresponding phase.*
