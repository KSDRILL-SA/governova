# Relay State Machine

**Status:** Shipped (v0.1) — `scripts/governova_relay`

Tracks relay position, handoffs, and permission levels, and enforces
`protocols/relay-protocol.md` §4 with `framework/permission-model.md`. Implements
the `relay-state-machine` component of `platform/engine/SPEC.md`.

## States

```
idle ──open_task──► idle ──assign──► assigned ──submit──► awaiting_approval
                      ▲                                          │
                      └──────────────── approve (L4) ────────────┘
                                    │
                                 close_task ──► closed
```

State lives in `governance/relay/state.json` — the current position only. History
lives in the audit trail, which is the tamper-evident record.

## The three invariants

The protocol calls these non-negotiable. This module makes them mechanical.

**1. One engineer at a time.** A second `assign` while another engineer holds the
task is refused (SEV1). No parallel work.

**2. L4 approval between every handoff.** The next engineer cannot be assigned
from `awaiting_approval`. The gate cannot be skipped.

**3. L4 is human-only, permanently.** A non-human actor calling `approve` is
refused at the API boundary — before any state is read or written — and the
attempt is recorded as SEV1. There is no parameter, flag, or configuration that
permits it, because a control that only reports the breach it could have prevented
is not a control.

`open_task` and `close_task` are also L4 acts and are equally human-only.
`system` is not a loophole around `human`.

## Usage

```bash
governova relay open   --task "…" --by "Founder"
governova relay assign --engineer engineer-02 --level L3
governova relay submit --engineer engineer-02
governova relay approve --by "Founder"          # human only
governova relay close  --by "Founder"
governova relay status
```

A refused transition prints `REFUSED [SEV{n}] (S{id})` and exits non-zero, so CI
and scripts fail on a governance breach rather than continuing past it.

## Compliance scoring

`compliance()` feeds the Governova Score's relay factor:

- Every submission must reach an L4 approval; an unapproved submission is a
  skipped gate and lowers the score proportionally.
- Each refused L4 attempt costs 15 points. It was correctly blocked, so it is not
  a breach — but it is evidence that a tool tried to self-approve, and the score
  must not read as clean.
- A repository that has never run the relay is **unassessed**, not compliant.
  Absence of evidence is never scored as evidence.

## Dogfood note

This repository's own relay compliance is **85/100**, not 100. During the runtime's
first live cycle an AI engineer attempted an L4 approval; it was refused and
recorded. That record cannot be removed without breaking the audit chain — the
trail prevents its own author from laundering his history, which is the property
the whole design exists to provide.
