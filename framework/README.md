# Framework — Layer 1: Universal Primitives

This folder contains the universal primitives that govern everything in Governova.
These are stack-agnostic and domain-agnostic. They never change regardless of
which technology or industry a project uses.

The framework is what makes Governova universal. Every constitution, every
implementation binding, and every domain extension operates within these primitives.

## Files in this folder

| File | Purpose |
|------|---------|
| `format-specification.md` | The S{C}.{N} standard ID format, AP-S{C}.{N}{letter} anti-pattern format, and required document structure for every constitution |
| `phase-model.md` | The four-phase read and dependency order (Phase 0–3) |
| `severity-model.md` | SEV0–SEV3 classification for violations and incidents |
| `permission-model.md` | The L1–L4 AI permission levels — L4 permanently human-only |
| `conflict-resolution.md` | The constitutional hierarchy and four-step conflict resolution protocol |
| `amendment-protocol.md` | How standards are changed, audited, and versioned |

## Status
Content extracted from C00-constitutional-order.md. The constitution remains the
ratified source; these primitives are the extracted, reusable Layer 1 form.
