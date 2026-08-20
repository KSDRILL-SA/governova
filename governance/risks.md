# Risk Register

> **`S9.31` — every recorded risk names one accountable person.** Ownership by a group is
> ownership by nobody: each member reasonably assumes another is watching. A team name in the
> owner column is treated as unowned, and correctly so.
>
> This project is currently one person, so every owner below is the same name. That is a fact
> worth seeing written down rather than distributed across a page to look larger — it is itself
> risk **R-06**.

**Last reviewed:** 2026-08-21 · **Review cadence:** monthly, or on any ADR that changes scope.

Severity follows the constitutional scale: **SEV0** existential · **SEV1** blocks a release or a
sale · **SEV2** degrades the product · **SEV3** accepted for now.

---

## Open risks

| ID | Risk | Sev | Owner | Mitigation | Trigger to escalate |
|----|------|-----|-------|------------|---------------------|
| **R-01** | Governova scores **78** against its own Certified bar of 85, so Certification — the highest-margin line in `ADR-011` — cannot be sold. Closing the gap needs roughly **199 more evidenced standards** (`#246`) | SEV1 | Maluleke Kurhula Success | Ceiling-first programme in `#246`: give abbreviated standards anti-patterns, then bind rules and probes to them | Score still below 82 by 2026-12-31 |
| **R-02** | The **semantic tier measures 53% precision against a 90% bar**, so Map/Adapt is deferred (`ADR-009`). `master.md` §14 says enterprises enhance their own governance rather than adopt a foreign one — without Map/Adapt the enterprise pitch is "adopt all 670 of ours" | SEV1 | Maluleke Kurhula Success | `ADR-009` re-entry criteria; `#138` tuned local model as the likeliest route | A named enterprise prospect declines specifically for this reason |
| **R-03** | **No SOC 2 and no security questionnaire answered.** Every regulated mid-market buyer named in the pricing model gates procurement on this, independent of price or product quality | SEV1 | Maluleke Kurhula Success | Scope SOC 2 Type I readiness before approaching any bank; it is a Stage 3 gate in `ADR-011` §4 | First enterprise conversation reaches procurement |
| **R-04** | **v0.1.0 and v0.2.0 shipped the full corpus under MIT** and cannot be un-published. Every day of adoption raises the cost of the `ADR-011` corpus licence | SEV2 | Maluleke Kurhula Success | Yank both, ship v0.2.1 carrying the core subset only. Adoption is negligible today and will not stay so | Either release exceeds 500 downloads |
| **R-05** | **No distribution.** The product and the pricing are further along than any route to a customer. For a solo founder this is usually the binding constraint, not the code | SEV1 | Maluleke Kurhula Success | Name one reference customer as a Stage 3 gate; treat it as engineering-equivalent work rather than something that happens later | No inbound interest by 2026-11-30 |
| **R-06** | **Single-person dependency.** One person holds the corpus, the engine, the roadmap and the customer relationships. A bank asking "will you exist in three years" has no good answer today | SEV1 | Maluleke Kurhula Success | Keep the constitution, ADRs and handoffs at a standard a stranger can pick up cold — already the practice, and `START-HERE.md` is the artefact | Any enterprise contract reaches signature |
| **R-07** | **`R200` is priced for a product that does not exist yet.** `ADR-011`'s "one price, growing value" carries it only if Workstream D actually lands; if Cloud slips a year it reads as a promise not kept | SEV2 | Maluleke Kurhula Success | Say the growing-value bargain plainly on the pricing page rather than implying it | Phase 4 Stage 0 not merged by 2026-11-30 |
| **R-08** | **Enforcement coverage is 7.5%** — 38 of 508 anti-patterns have a rule. A buyer reading that number gets a fair impression of mechanical reach, and it is thin | SEV2 | Maluleke Kurhula Success | Do not headline the figure; move it via `#246` rather than by narrowing the denominator | Coverage still below 12% at the next release |
| **R-09** | **The free core corpus is unsized.** ~120 standards is a guess: too small and nobody experiences value, too large and Starter never converts | SEV3 | Maluleke Kurhula Success | Choose the subset deliberately before v0.2.1, against what a real project needs to be governed at all | v0.2.1 preparation begins |

---

## Closed

| ID | Risk | Closed | How |
|----|------|--------|-----|
| **R-00** | A `cryptography` advisory left the supply-chain gate red on `main` for eleven days, and a `v*` tag during that window would have published a wheel carrying it | 2026-08-20 | Lockfile bumped (#232); the release gate now runs the CVE check it previously omitted (#234) |

---

## How this register is used

A risk is opened when it would change a decision if it came true, and closed only when the
condition that made it a risk is gone — not when it stops being uncomfortable to read.

**The escalation trigger is the load-bearing column.** A risk with no trigger is a worry;
a risk with a trigger is a decision waiting for a date.
