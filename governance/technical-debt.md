# Technical Debt Register

> **`S13.2` — one place where known debt is listed with its cost.** Debt nobody has written down
> is not managed, it is merely survived. What follows is what this repository owes, with the
> price of each item and what it blocks.

**Last reviewed:** 2026-08-21 · **Reviewed on every release, and on any ADR that adds scope.**

Cost is stated as effort **and** as what the item prevents, because effort alone never justifies
paying a debt down.

---

## Open

| ID | Debt | Cost | Blocks | Tracked |
|----|------|------|--------|---------|
| **D-03** | **The violation-rate factor saturates.** 53 findings score identically whether the repository has 30 files or 30,000, so on first contact a mature library baselines at 0/100 | Small to fix, but it is a `C0 §8` model change and therefore L4 | An honest first-contact score for real adopters | `#196` |
| **D-05** | **`S13.4` is violated and cannot be repaired.** One `harden:` commit sits in history with no valid maintenance type. Rewriting history to fix a metric is precisely the failure the metric exists to catch | Zero to accept. Unbounded to "fix" dishonestly | One permanently violated probe, correctly reported | — |
| **D-06** | **The relay factor is permanently 85/100.** The audit chain records a refused L4 attempt from the runtime's first live cycle; removing it would break the chain | Zero — accepted permanently | 15 points of the Governova Score, forever. The arithmetic in `#246` already assumes this | — |
| **D-07** | **No TypeScript formatter runs.** `.editorconfig` declares the S1.73 line length, and eleven lines in the IDE extension exceed it. Nothing enforces the number | Small, but it introduces a Node toolchain to govern 485 lines | Nothing today; grows with the extension | `#248` closed with the config; enforcement deferred |
| **D-08** | **The corpus is bundled whole in every wheel.** `ADR-011` licenses it, which requires splitting a core subset out of the build — the packaging assumes one artefact today | Medium. Touches `hatch_build.py`, the release gate's bundled-constitution assertion, and the compile step | The entire `ADR-011` corpus licence | — |
| **D-09** | **No Cloud exists.** Workstream D is design-complete (`ADR-010`, `phase-4-cloud.md`) and has no code. Credits are priced and promised in `ADR-011` | Months | Every credit allotment in the price ladder | `#254`, `#255` |
| **D-15** | **Configuration is read where it is used, not validated at startup.** `GOVERNOVA_*` variables are read inline — `writer.py:122` reads the constitution-path override at the point of use, and `.env.example` declares eleven variables nothing validates on boot | Small — one settings object the CLI reads once | Nothing today. It is the failure `S1.68` and `S2.67` describe, found by binding a rule for them and then scoping that rule to the region its standard governs | — |
| **D-18** | **One merge commit sits in history.** `S1.22` mandates squash merge; `6debca9` predates the discipline. Rewriting history to clear a probe is the same move `D-05` refuses | Zero to accept. Unbounded to "fix" dishonestly | `S1.22` probes as violated, permanently and correctly | — |

---

## Paid down

| ID | Debt | Paid | How |
|----|------|------|-----|
| **D-01** | 218 abbreviated standards carried no anti-pattern, so no rule could ever bind to them | 2026-08-21 | `#262`, `#264` — all 227 abbreviated standards now carry one, and 665 of 670 in the corpus are bindable |
| **D-02** | C08 was the worst of it: 72 of 87 standards bare | 2026-08-21 | `#258`, `#259` — C08 closed in full, then C04, C05, C01, C02 and C06's prescriptive standards |
| **D-04** | Two orphan anti-patterns, fossils of an earlier numbering declared only in the index | 2026-08-21 | The stale rows were retired in `#216`; `AP-S2.55a` and `AP-S10.14a` now exist as real anti-patterns on `S2.55` and `S10.14`, written from those standards' own words |
| **D-16** | No pull request or issue templates | 2026-08-21 | A pull request template carrying all eight `S1.46` fields, plus three issue forms. `S1.46` probes satisfied; `S1.29` was already satisfied and the probe was corrected to see it |
| **D-17** | No vendor register, and so no exit plan for any dependency | 2026-08-21 | `governance/vendors.md` — four vendors with what they hold, their SLA and a costed exit. `S8.86` probes satisfied |
| **D-10** | The abbreviated form discarded anti-patterns unconditionally — 227 standards could not carry one however carefully it was written | 2026-08-20 | `#241` taught the compiler to read a block on an abbreviated standard, index byte-identical on landing |
| **D-11** | A blocking rule cited `S2.34` (idempotency) while implementing money-as-float | 2026-08-20 | `#243`, once `AP-S5.28a` existed to bind to. Law before check |
| **D-12** | The per-rule cost ceiling measured the scheduler, not the rule — 3 failures in 8 under load, with noise reaching 255x against a 355x signal | 2026-08-20 | `#247` — min-of-repeats sampling, ceiling unchanged, and the negative case the gate never had |
| **D-13** | The release gate re-ran eight of the nine gates guarding `main`, omitting the CVE check | 2026-08-20 | `#234` |
| **D-14** | `mcp` was capped below 2.0, so 2.x security patches could not be taken | 2026-08-20 | `#251` — migration plus the wiring tests that would have caught the original break |

---

## The rule this register follows

**Debt is recorded when it is incurred, not when it becomes painful.** An item leaves this table
only when the underlying condition is gone — never because it was reclassified, and never because
the number it affects was redefined.

`D-05` and `D-06` are permanent and stay listed. A register that only holds solvable problems
teaches the reader that everything here is solvable.
