# Governova Engine — Architecture Specification

| Attribute | Value |
|-----------|-------|
| **Document** | Engine Architecture Specification |
| **Status** | Spec phase — pre-build |
| **Version** | v1.0 |

---

## Overview

The governance engine is the central runtime of the Governova platform.
Every product surface connects to it. Every AI tool in the relay queries it.

## Seven components

| Component | Folder | Purpose |
|-----------|--------|---------|
| Constitutional Store | `constitutional-store/` | Live versioned database of active standards per session |
| Violation Detector | `violation-detector/` | Real-time AP violation scanning |
| Relay State Machine | `relay-state-machine/` | Relay position, handoffs, permissions, abort conditions |
| Audit Trail | `audit-trail/` | Immutable append-only record of every AI action |
| System Knowledge Engine | `system-knowledge-engine/` | Generates Why/How/Failure/Fix per file |
| Mapping Engine | `mapping-engine/` | Enterprise standard translation |
| Intelligence | `intelligence/` | Network effect, temporal governance, pre-build risk |

## Technology stack (planned)

- Runtime: FastAPI (Python)
- Database: PostgreSQL (constitutional store, audit trail)
- Cache: Redis (active session index, relay state)
- Queue: BullMQ (violation scanning, Bible generation jobs)
- Hosting: Railway

## Build order

1. Constitutional Store + Violation Detector (core — everything else depends on these)
2. Relay State Machine + Audit Trail (governance layer)
3. System Knowledge Engine (documentation layer)
4. Mapping Engine (enterprise layer)
5. Intelligence (network layer — requires user base)

## API contract (draft)

```
GET  /standard/{id}                 → StandardRecord
GET  /constitution/{project_id}     → CompiledIndex
POST /violation/check               → ViolationReport
GET  /anti-pattern/{id}             → AntiPatternRecord
GET  /relay/{session_id}/state      → RelayState
POST /audit/log                     → AuditEntry
GET  /runbook/{incident_type}       → RunbookContent
POST /temporal/flag/{standard_id}   → TemporalFlag
```
