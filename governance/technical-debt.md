# Technical Debt Register

> **`S13.2` — one place where known debt is listed with its cost.** Debt nobody has written down
> is not managed, it is merely survived. What follows is what this repository owes, with the
> price of each item and what it blocks.

**Last reviewed:** 2026-08-22 · **Reviewed on every release, and on any ADR that adds scope.**

Cost is stated as effort **and** as what the item prevents, because effort alone never justifies
paying a debt down.

---

## Open

| ID | Debt | Cost | Blocks | Tracked |
|----|------|------|--------|---------|
| **D-05** | **`S13.4` is violated and cannot be repaired.** One `harden:` commit sits in history with no valid maintenance type. Rewriting history to fix a metric is precisely the failure the metric exists to catch | Zero to accept. Unbounded to "fix" dishonestly | One permanently violated probe, correctly reported | — |
| **D-06** | **The relay factor is permanently 85/100.** The audit chain records a refused L4 attempt from the runtime's first live cycle; removing it would break the chain | Zero — accepted permanently | 15 points of the Governova Score, forever. The arithmetic in `#246` already assumes this | — |
| **D-07** | **No TypeScript formatter runs.** `.editorconfig` declares the S1.73 line length, and eleven lines in the IDE extension exceed it. Nothing enforces the number | Small, but it introduces a Node toolchain to govern 485 lines | Nothing today; grows with the extension | `#248` closed with the config; enforcement deferred |
| **D-09** | **The Cloud is written and nothing runs it.** Stages 0–4 exist as code — identity, organisations, the credit ledger, the Gateway and the hosted read API, with tests. None of it is deployed anywhere, and no customer can reach any of it | Deployment, not development: infrastructure, secrets, a database instance, a domain. Weeks, and none of it is code we have not written | Every credit allotment in the price ladder. The code is no longer the blocker; the environment is | `#255`, `#303` |
| **D-27** | **The domain layer is not wired to the schema it declares.** `platform/cloud/prisma/schema.prisma` carries the composite keys and unique constraints that make the invariants enforceable, and nothing connects to it: there are no migrations, no client, and `governova_org` and `governova_ledger` hold state in Python memory. Every invariant the schema would enforce is currently enforced only by the types above it | Medium. Migrations, a client, and rewriting two modules against it — the invariants are already expressed, so this is transcription rather than design | Durability of everything Stages 1–2 own. A restart loses every organisation, membership and ledger entry | `#255` |
| **D-26** | **No CI credential.** `#254` names organisation-scoped API keys as the CI fallback, and the keychain refuses to run headless by design. So a pipeline cannot authenticate at all today. Organisations now exist to scope a key to, so the reason it was deferred is gone | Small — the type it hangs off exists | Any Cloud feature used from CI, which now includes the hosted read API. Still nothing in practice, because nothing is deployed (`D-09`) | `#255` |
| **D-25** | **Identity state is in memory.** Device grants and the revocation list do not survive a restart, so a restart un-revokes every revoked token. Stage 0 ships without a database by design, and the database Stage 1 was meant to bring is still only a schema — see `D-27` | Small once a database exists; it is two tables | Revocation durability. A revoked token is refused until the service restarts, which is the one property `#254` asks for that is currently time-bounded | `#255` |
| **D-28** | **A standard about test code cannot be evidenced by a rule.** The scanner skips test files by design — `#8`'s express measurement is why — so `S7.3` (asserting on private state), `S7.10` (mocking the thing under test), `S7.11` (only the happy path of a protected endpoint) and their neighbours are unreachable by the reliable tier however well a rule is written | Medium, and it is a probe rather than a rule: reading test files deliberately, as evidence, is a different surface from scanning them as source | Nothing today. It removes roughly a dozen standards from the pool `#246` counts as rule-reachable, so the arithmetic there is slightly optimistic | `#246` |
| **D-23** | **Coverage headroom is 1.27 points**, up from 0.4. 191 partial branches remain, the largest groups in `governova_cli/__main__.py` (20, at 34%), `governova_evidence` (15) and `governova_requirements/closure.py` (13) | Unbounded, and it should stay that way — the value is in the behaviour covered, not the percentage | Nothing today. `detect.py` is done; the CLI is mostly typer glue and worth least | `#287` |
| **D-18** | **One merge commit sits in history.** `S1.22` mandates squash merge; `6debca9` predates the discipline. Rewriting history to clear a probe is the same move `D-05` refuses | Zero to accept. Unbounded to "fix" dishonestly | `S1.22` probes as violated, permanently and correctly | — |

---

## Paid down

| ID | Debt | Paid | How |
|----|------|------|-----|
| **D-01** | 218 abbreviated standards carried no anti-pattern, so no rule could ever bind to them | 2026-08-21 | `#262`, `#264` — all 227 abbreviated standards now carry one, and 665 of 670 in the corpus are bindable |
| **D-02** | C08 was the worst of it: 72 of 87 standards bare | 2026-08-21 | `#258`, `#259` — C08 closed in full, then C04, C05, C01, C02 and C06's prescriptive standards |
| **D-04** | Two orphan anti-patterns, fossils of an earlier numbering declared only in the index | 2026-08-21 | The stale rows were retired in `#216`; `AP-S2.55a` and `AP-S10.14a` now exist as real anti-patterns on `S2.55` and `S10.14`, written from those standards' own words |
| **D-22** | The complexity gate sat at 11, three above the conventional default of 10, with `_project_name`, `_statement_changed_at` and `parse_manifest` holding it there | 2026-08-22 | `max-complexity = 10`. Each of the three was split along a boundary it already had — a manifest format's parser separated from the search order around it, reading git history separated from comparing what it returned, envelope validation separated from record validation. No per-file ignore was added: a ratchet that exempts what it cannot reach is not a ratchet. The walk down from 15 took nine refactors in total |
| **D-24** | The engine assumed it held the whole corpus. On the core wheel, 46 of 64 rules cite anti-patterns the bundled corpus does not contain, and `validate_rules` reported all 46 as rule-set drift — accusing a correctly built wheel of a defect | 2026-08-22 | `ADR-013` decides that a rule fires whether or not the operator holds the law it cites: dormancy would be a licence check inside an engine `ADR-010 §5.1` guarantees runs complete and offline. Its three consequences are implemented — rule messages stand alone without the standard, `unresolved_bindings` reports the boundary as a fact while `validate_rules` keeps `REQ-006` and declines to answer where the answer is unknowable, and the index now carries a `corpus` marker so no coverage figure is read against an unattributable denominator |
| **D-16** | No pull request or issue templates | 2026-08-21 | A pull request template carrying all eight `S1.46` fields, plus three issue forms. `S1.46` probes satisfied; `S1.29` was already satisfied and the probe was corrected to see it |
| **D-17** | No vendor register, and so no exit plan for any dependency | 2026-08-21 | `governance/vendors.md` — four vendors with what they hold, their SLA and a costed exit. `S8.86` probes satisfied |
| **D-15** | Configuration was read where it was used, and every fallback was silent | 2026-08-21 | `governova_settings` — one validated read, surfaced by `governova config`. It reports a value that is not a number, a value outside the accepted set, and a variable name nothing reads, which had no other symptom |
| **D-19** | Branch coverage was not tracked, so 194 partial branches sat behind an 82% line figure | 2026-08-21 | `branch = true`, with `fail_under` unchanged at 80. Twenty of the partial branches were probe verdicts that had never been produced in a test; those are covered now |
| **D-20** | No coverage report reached a pull request | 2026-08-21 | `validate.yml` publishes `coverage.xml` on every run, including failed ones — the run worth reading most is the one that failed |
| **D-21** | No complexity gate; ruff selected `C4` (comprehensions) and not `C901` (mccabe) | 2026-08-21 | `C90` enabled at the current ceiling. The ratchet down is `D-22` |
| **D-03** | The violation-rate factor saturated, and a headline score rested on one factor | 2026-08-21 | `ADR-012` — no score is issued below a quorum of 50% of the model, and density is reported beside the count. The saturation itself is **not** removed: amending the penalty curve means picking a number for a pleasing shape, and that is deferred with the reason recorded |
| **D-08** | The corpus was bundled whole in every wheel, so `ADR-011`'s licence had no mechanism | 2026-08-21 | `governance/core-subset.toml` declares the boundary as data; `governova compile` writes `constitution.core.json` beside the full index and commits it; the wheel and sdist carry only the core; the release gate asserts the shipped corpus against the manifest. Measured: the built wheel carries 118 standards and no domain pack |
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
