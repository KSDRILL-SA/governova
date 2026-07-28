# Audit Trail

**Status:** Shipped (v0.1) — `scripts/governova_audit`

The immutable, append-only record of every governed action. Implements the
`audit-trail` component of `platform/engine/SPEC.md`.

## Why a hash chain

An audit trail exists to be trusted by someone who does not trust the system that
wrote it — an auditor, a regulator, a customer in a dispute. A plain log proves
nothing, because the party whose conduct is in question is the party that controls
the file.

Each record carries the SHA-256 hash of its predecessor. Editing a record,
deleting one, or reordering two breaks every link after the change, and the break
is detectable by walking the chain — no external service, no database, no trust
required. That is the difference between *"we log our actions"* and *"our actions
can be shown not to have been altered."*

## Storage

`governance/audit/audit-log.jsonl` — one JSON object per line, appended, never
rewritten, flushed to disk before the call returns. A record still sitting in a
buffer when the process dies is a record that did not happen.

## What a record carries

`seq · timestamp · actor · actor_kind · permission_level · action · subject ·
outcome · standards · detail · prev_hash · record_hash`

`record_hash` covers every other field including `prev_hash`. The encoding is
canonical (sorted keys, fixed separators) so a record hashes identically on any
platform.

## Detected tampering

| Attack | How it surfaces |
|--------|-----------------|
| A record edited after the fact | its own hash no longer matches its content |
| A record deleted | broken link **and** a sequence gap |
| Records reordered | link mismatch |
| The head truncated | first record's predecessor is not the genesis hash |
| A forgery with a recomputed hash | the record is self-consistent, but every following link still committed to the original hash |

The last row is what chaining buys over per-record checksums, and it is why an
attacker who fully understands the format still cannot rewrite history silently.

## Usage

```bash
governova audit verify          # walk the chain; exits non-zero if broken
governova audit log -n 20       # most recent records
governova audit record --actor … --action … --subject …
```

## Consumed by

- **Governova Score** — the audit-trail factor scores chain integrity and
  attribution completeness. A **broken chain scores 0, never partial credit**: an
  altered trail is worse than no trail.
- **`governova_relay`** — every relay transition writes here, so relay history and
  audit history cannot disagree.
