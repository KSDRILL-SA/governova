---
name: Feature proposal
about: The mandatory first step of the feature lifecycle (S1.27, S1.29)
title: ""
labels: enhancement
assignees: ""
---

<!--
S1.29 — all seven fields are required. A proposal with missing fields is
returned without review.

The full form, with the gate questions and the worked examples, is
`templates/feature-proposal-template.md`. This issue is the short form; use the
full template for anything touching authentication, schema, or the API contract
(S10.20 — such a feature is never "small").
-->

## Feature name

<!-- One line. Matches this issue's title. -->

## Problem statement

<!-- The user problem, in the words of the person having it. **No solution
language** — if this paragraph names a technology, it is the wrong paragraph. -->

## Proposed solution

<!-- Plain English. No code. What the system would do differently, not how. -->

## Architecture map

<!-- Which systems, services, layers and components are involved. -->

## Data models

<!-- Which models are read or created. Note any schema change explicitly —
a schema change is always L4 (S10.12). -->

## Edge cases

<!-- Error states, loading states, empty states, boundary conditions. The empty
state is the one most often missed and the one every user sees first. -->

## Acceptance criteria

<!-- Measurable conditions that confirm this is complete. "Works correctly" is
not a criterion; "returns 429 with `RATE_LIMIT_EXCEEDED` after ten attempts" is. -->

- [ ]

## Gate questions (S9.7)

<!-- A feature that fails any of these is deferred, however much it is wanted —
user desire does not override the gate (S9.25). -->

- [ ] Does this serve the primary workflow?
- [ ] Is it needed for v1, or is it a v2 want?
- [ ] Can it be built inside the locked stack, with no new framework?
- [ ] Does it fit the v1 complexity limits (tables, endpoints, jobs, services)?
- [ ] Has a real user confirmed they need this?
