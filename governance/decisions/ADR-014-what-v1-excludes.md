# ADR-014 — What v1 excludes, and the gate that reopens each one

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-23 |
| **Authority** | L4 — `C0 §8`. Scopes the delivery of `ADR-005` Phase 3 |
| **Supersedes** | Nothing. Scopes `ADR-010` and `ADR-011` rather than amending them |
| **Relates To** | `ADR-005 §Sequencing`, `ADR-008`, `ADR-010 §1`, `ADR-011 §4` |

---

## Context

`ADR-005` locks the sequencing as Phase 1 (corpus and lifecycle) → Phase 2 (brownfield) →
Phase 3 (Cloud). Phases 1 and 2 are complete and published: `governova 0.2.3` is on PyPI, it
governs four external repositories across three GitHub owners, and a merge gate runs on every
pull request in each of them.

Phase 3 is one ADR (`ADR-010`) and one plan (`planning/phase-4-cloud.md`) covering six stages.
Building all six is roughly a quarter of focused work, and **none of it makes the engine better
at governing a repository.** The engine already does that, offline and free, and `ADR-010 §1`
guarantees it always will.

Three forces make the scope question urgent rather than academic.

**The Cloud was already deferred once, and the deferral held because it had a reason.** The
credit ledger is a Python list in RAM. Deploying it meant a customer buys credits, the process
restarts, and the balance is gone — an incident, not an incomplete feature. That deferral was
recorded, and it is why nothing was shipped that could not be operated.

**One stage carries unresolved research and the rest do not.** Stages 1, 2 and 4 are ordinary
product engineering. Stage 3, the Intelligence Gateway, wraps a semantic tier measuring **53%
against `ADR-008`'s 90% bar**. Sequencing them together makes the whole release wait on the one
piece nobody can schedule.

**Two of the excluded items are already forbidden to sell.** `ADR-011 §4` lists five gates for
Certification and Enterprise — Governova scoring ≥ 85 on itself, enforcement coverage ≥ 25%, the
semantic bar, SOC 2 Type I, one named reference customer — and states that **nothing below is
sold until every gate is met.** Deferring them costs no revenue that exists.

The risk this ADR exists to prevent is the one every unscoped roadmap carries: *"everything"*
becomes the requirement, the quarter absorbs it, and the thing that already works ships to
nobody while the thing that does not is built.

---

## Decision

**v1 is the free engine plus a Cloud that does accounts, organisations and the hosted report.**
Concretely: Stage 0 (identity, done), Stage 1 (persistence), Stage 2 (subscriptions and the
credit ledger), Stage 4 (hosted surfaces and the Angular console), and the marketing site.

**Everything below is excluded from v1, and each exclusion names the condition that reopens it.**
A deferral without a re-entry condition is a backlog; a deferral with one is a decision.

| Excluded from v1 | Why now | Reopens when |
|---|---|---|
| **Intelligence Gateway** — Stage 3 | The only item with unresolved research. The semantic tier measures 53% against a 90% bar, and hosting an untrusted tier does not make it trusted. | `ADR-008`'s bar is met, **or** it ships labelled advisory and never blocking — which `ADR-008` already permits. |
| **PR Guardian bot** | The CI gate already posts the Guardian verdict to every pull request. | A user asks for a surface the gate does not already give them. |
| **Slack / Teams bot** | `governova notify` already posts to a Slack-compatible webhook. | Same. |
| **Standalone web dashboard** | `governova dashboard` already emits self-contained HTML, and the Angular console supersedes it. | Never, most likely. Its job is being done twice. |
| **JetBrains plugin** | The VS Code extension has not yet been used by anyone outside this project. | The first extension earns a second. |
| **Certification tiers** | `ADR-011 §4` already forbids selling them. Two of its five gates are unmet by a wide margin. | All five gates in `ADR-011 §4` are met. Each is a figure our own tooling reports. |
| **Intelligence Network** — Stage 5 | Consent-gated, and inherits `ADR-009`'s deferral of Always-On Learning. | `ADR-009` is revisited on its own terms. |

**Constitutional coverage is explicitly not a v1 gate.** Reaching Certification's 44% means 262
evidenced standards against today's 113 — roughly 150 more rules. That is real work and it is
the shape of the trap: a metric Governova defines about itself, which could absorb a year while
nothing ships. It continues as background work at whatever rate the rule batches allow.

---

## Consequences

### What becomes easier

- **v1 has a date.** Four stages of ordinary engineering, with no item whose completion nobody
  can predict.
- **The one research risk is isolated.** Stage 3 can run late, or ship advisory, without holding
  a release.
- **Every tier v1 sells has met its gates.** The Pro ladder anchored at R200 is the full corpus
  plus the complete engine, which is true today and checkable in this repository.
- **The strongest marketing sentence stays true.** *"Certification opens when Governova scores
  85 on itself"* is only sayable while Certification is genuinely closed.

### What becomes harder

- **The product sold at v1 is narrower than the product described in `master.md`.** That gap
  must be visible on the marketing site rather than discovered at signup — a roadmap page, not
  a feature table with asterisks.
- **Four surface directories stay stubs**, and a reader browsing the repository will find them.
  Each keeps a README stating what supersedes it, so an empty directory is never mistaken for
  abandoned work.
- **Deferring the Gateway defers the differentiator.** The deterministic tier is what competitors
  can copy; the semantic tier is what they cannot. Shipping without it means competing on the
  copyable half for one release.

### Constitutional alignment

- `S6.6` — an ADR against the rubric for a decision of this shape. This one scopes delivery
  rather than choosing a stack, so the stack matrix does not apply; the gates table replaces it.
- `ADR-010 §1` — the free boundary is untouched. Nothing moves behind the paid line, and nothing
  excluded here was ever free.
- `ADR-011 §4` — this ADR does not weaken a single gate. It records that we are not selling what
  we cannot demonstrate, which that ADR already required.
- `C0 §8` — ratification is L4. This document is **Proposed** until a human accepts it.

---

## Alternatives Considered

| Option | Why rejected |
|---|---|
| **Build all six stages, ship once** | Roughly a quarter, gated on the one stage with unresolved research. The engine that already governs four repositories would sit unshipped behind a Gateway nobody can schedule. |
| **Ship the engine alone, no Cloud** | The engine is already shipped and free. This is not a v1 of a company — it is the status quo with a version number, and it forecloses revenue that Stages 1, 2 and 4 genuinely unlock. |
| **Ship the Gateway advisory in v1** | Defensible, and `ADR-008` permits it. Rejected for v1 only because metering an advisory tier against a credit budget asks customers to pay for something we have said is not trusted. It becomes the obvious v2 opening. |
| **Defer without writing it down** | What was already happening. A deferral that lives in a conversation is a backlog, and the four stub directories are what a backlog looks like six months later. |
| **Cut Stage 2 (billing) as well** | Then the Cloud has accounts and no way to charge for them, and Stage 4's console renders orgs that cannot hold a subscription. Billing is what makes the rest sellable rather than a demo. |

---

## Approved Deviations

None. This ADR narrows what is built; it does not deviate from any standard.

---

> **Status: PROPOSED — 2026-08-23**
> *Ratification is L4 and belongs to the owner: Maluleke Kurhula Success.*
