# Protocols — Operational Procedures

How the Governova governance system operates day-to-day. These are the
executable procedures that make the constitutional standards actionable.

## Files

| File | Purpose |
|------|---------|
| `relay-protocol.md` | The 5-engineer relay model — who does what, in what order, with what permissions |
| `relay-clarification.md` | MINOR vs ARCHITECTURAL fast-path — when to pause the relay and when to proceed |
| `relay-abort.md` | What to do when a relay diverges from the design mid-build |
| `github-workflow.md` | **GitHub Operating Standard** — branch→issue→PR→merge order, no-AI-references rule, full issue/PR metadata, mode-based merge authority (solo/team) |
| `brownfield-adoption.md` | **Brownfield Adoption Standard** — onboarding/converting existing systems: gap analysis, non-breaking incremental conversion, edge-case register |
| `external-governance.md` | **External & Ecosystem Governance** — third-party frameworks, dependencies/supply-chain, external APIs, integrations, vendors, temporal governance |
| `git-workflow.md` | Branch model, commit convention, PR process, golden rules (mechanics) |
| `modes/` | Operating modes: personal, team, enterprise |
| `frameworks/` | Reusable AI development frameworks (AI-assisted workflow, review-challenge) |

> `session-lifecycle.md` (the 12-step build session) is specified in
> GOVERNOVA-MASTER.md §12.2 and will be added as a standalone protocol file
> in a follow-up build task.

## Migration
- `workflow/ksdrill-sa-ai-workflow.md` → `protocols/relay-protocol.md`
- `foundation/git-workflow.md` → `protocols/git-workflow.md`
- `workflow/ai-*-framework.md` (+ SKILL dirs) → `protocols/frameworks/`
- `overlays/solo-dev-overlay.md` → `protocols/modes/personal-mode.md`
- `overlays/team-overlay.md` → `protocols/modes/team-mode.md`
