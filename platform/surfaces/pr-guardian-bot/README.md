# Governova — PR Guardian

**Status:** Alpha — working (v0.1)
**Surface:** consolidated PR governance verdict

Every pull request gets a single **Governova Guardian** panel — a plain-English verdict
combining the three things a reviewer needs at a glance:

- **Governova Score** (overall repo posture)
- **This PR** — enforcement result on the changed files: blocking vs advisory findings
- **Enforcement coverage** — how much of the constitution is mechanically enforced

The verdict renders in the PR's **job summary** (no bot comments, no non-human actor in
the conversation). The blocking gate stays with the Constitutional Enforcement workflow;
the Guardian is advisory — it *reports*, it does not block.

## Use it

```bash
governova guard --base origin/main     # prints the verdict + writes the job summary
```

`.github/workflows/pr-guardian.yml` runs it on every PR.

## Implementation

`governova_guardian` (`scripts/governova_guardian/`): composes `compute_score`,
the reliable-tier scan over the PR's changed files, and `enforcement_coverage` — all
deterministic, no external services.
