# Decisions — Architecture Decision Records

Every significant architectural decision made across all systems.
ADRs record: the decision, alternatives considered, the standard that authorised
the chosen approach, and the engineer who made the recommendation.

## File naming
`ADR-{NNN}-{description}.md` — zero-padded three digits.
Restructure / migration records use a descriptive `RESTRUCTURE-{version}.md` name.

## Current records
- ADR-000: Template
- ADR-001: FundsLink Academy stack selection
- ADR-002: Maphophe stack selection
- ADR-003: Reserve Bank stack selection
- ADR-004: SyncUp stack selection
- ADR-005: Governova platform architecture — the 3-plane model and four workstreams
- ADR-006: Engine security posture
- ADR-007: Lifecycle completeness — govern the whole SDLC
- ADR-008: The semantic tier has no default endpoint
- ADR-009: Map/Adapt and Always-On Learning are deferred, and the bar is not amended
- ADR-010: Governova Cloud — the paid boundary, the stack, and the Intelligence Gateway
- ADR-011: The corpus is the product — licence, price ladder, and the gates that unlock each tier
- ADR-012: A score drawn from one factor is not a score, and a count is not a rate
- ADR-013: A rule fires for a defect, not for a licence
- RESTRUCTURE-v2.0: The Governova v2.0 four-layer restructure instruction
  (executed record of the migration that produced this structure)

> This list stopped at ADR-004 while five further records were added, and then at
> ADR-011 while two more were, because it was hand-maintained prose and nothing
> checked it. `test_adr_index_lists_every_record` checks it now: a record added
> without a line here fails the suite. A note admitting that a list goes stale is
> not a substitute for the check that would stop it.

## Migration
All ADRs migrated from original `adrs/` folder.
The v2.0 restructure specification is archived here as `RESTRUCTURE-v2.0.md`.
