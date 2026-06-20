# Engine — The Governance Runtime

The central runtime of the Governova platform.
Every product surface connects to it. Every AI tool in the relay queries it.

## Components

| Folder | Component | Purpose |
|--------|-----------|---------|
| `constitutional-store/` | Constitutional Store | Live versioned database of active standards per session |
| `violation-detector/` | Violation Detector | Real-time scanner for AP violations in code diffs and PR content |
| `relay-state-machine/` | Relay State Machine | Tracks relay position, handoffs, permission levels, abort conditions |
| `audit-trail/` | Audit Trail | Immutable append-only record of every AI action |
| `system-knowledge-engine/` | System Knowledge Engine | Generates Why/How/Failure/Fix layers for every file built |
| `mapping-engine/` | Mapping Engine | Translates enterprise standards into a Governova CONSTITUTION-INDEX |
| `intelligence/` | Intelligence Layer | Network effect, temporal governance, pre-build risk assessment |

See `SPEC.md` for the full engine architecture specification.
