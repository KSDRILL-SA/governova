---
name: Bug report
about: Something behaves differently from what a standard says it should
title: ""
labels: bug
assignees: ""
---

## What happened

<!-- The observed behaviour. Paste output rather than describing it. -->

## What should have happened

<!-- Cite the standard, ADR or documented behaviour this contradicts, if you
know it. "It surprised me" is a legitimate report; say so plainly rather than
inventing a rule. -->

## Reproduction

<!-- Step by step from a clean state. If it does not reproduce reliably, say how
often it happened and out of how many attempts — an intermittent fault reported
as intermittent is far more useful than one reported as certain. -->

1.

## Environment

| | |
|---|---|
| `governova --version` | |
| Python | |
| Operating system | |
| Installed from | <!-- PyPI / source checkout / wheel --> |

## Severity

<!-- S8.47 — four levels. Suggest one; the maintainer classifies (S10.30). -->

- [ ] **SEV0** — data loss, a security breach, or a financial correctness fault
- [ ] **SEV1** — a core workflow is unusable and has no workaround
- [ ] **SEV2** — degraded, with a workaround
- [ ] **SEV3** — cosmetic, or an inconvenience

## Does a gate report this?

<!-- Governova's own gates are the first place a defect in Governova should
surface. If `validate`, `guard` or the enforcer stayed green through this, that
silence is part of the bug and worth saying so. -->
