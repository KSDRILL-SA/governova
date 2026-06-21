# planning/

Living documents that govern **how** Governova gets built. Distinct from `governance/` (which records what *has been* done) and `framework/` + `constitution/` (which define *what must be true*).

| File | Purpose |
|------|---------|
| `governova-build-plan.md` | The master build plan — six phases (A–F) from zero to v1.0, with deliverables, dependencies, and locked decisions |
| `phase-a-spec.md` | Detailed spec for Phase A — constitution as data (parser, validator, schema, types) |
| `phase-{B…F}-spec.md` | Drafted before each phase begins, approved by L4 before any code is written |

---

## Workflow

1. Build plan is the source of truth for **what** is being built and **when**
2. Each phase spec is drafted **before** the phase begins
3. L4 approves each spec before any branch is created
4. Specs are amended via PR — not edited silently
5. On phase completion, the build plan gets a "Phase X — Done" appendix with actual effort and lessons learned

---

*All planning documents are L1 (Propose) outputs. L4 approval is required before any L3 (build) work begins on the corresponding phase.*
