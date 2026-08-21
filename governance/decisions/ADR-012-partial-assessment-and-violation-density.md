# ADR-012 — A score drawn from one factor is not a score, and a count is not a rate

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-08-21 |
| **Authority** | L4 — `C0 §8`. Amends the §18.1 scoring model |
| **Supersedes** | Nothing. Amends `ADR-002` §18.1 as implemented |
| **Tracked** | `#196`, `D-03` |

---

## Context

`governova onboard` run against four mature third-party libraries, on the current engine:

| Repository | Files | Blocking | Advisory | Violation factor | Headline |
|---|---|---|---|---|---|
| `pallets/click` | 32 | 0 | 52 | 0/100 | **0/100 (F)** |
| `psf/requests` | 24 | 0 | 63 | 0/100 | **0/100 (F)** |
| `expressjs/express` | 58 | 1 | 46 | 0/100 | **0/100 (F)** |
| `spf13/cobra` | 19 | 0 | 7 | 79/100 | 79/100 (C) |

Every finding is a correct application of the standard it cites. No false positives are
involved, and the three duplicate rules that were inflating these counts were removed in `#281`
before this measurement was taken.

`D-03` recorded the cause as **saturation** — that `100 - 3 × advisory` reaches zero at 34
findings and cannot distinguish 34 from 340. That is true, and it is not the cause of the
headline.

**Density does not rescue these repositories.** `click` carries 1.63 findings per file and
`requests` 2.63. A per-file model returns them a very low score too, because they genuinely do
carry more than one finding per file. The saturation is real and it is not what produces `F`.

What produces `F` is the second defect, which `D-03` did not record.

### The actual cause

On first contact with a repository that has no Governova instrumentation:

- **relay compliance** and **audit trail** need a live runtime — unassessed
- **constitutional coverage** is unassessed *by design* until a human accepts a profile
- **amendment discipline** needs governance records the repository has never had reason to keep

So four of five factors return `None`, `finalize` renormalises over the assessed weight, and
**30% of the model becomes 100% of the answer**.

`pallets/click` is then told it scores 0 out of 100, grade F, by a product it has run once. That
number is not a weighted average of five factors. It is one factor wearing the name of five.

> *"The first run against somebody else's repository is the only first impression this product
> gets."* — `planning/phase-3-brownfield.md`

---

## Decision

Two amendments to §18.1. Neither changes any factor's weight or any factor's arithmetic.

### 1. A headline score requires a quorum of the model

**No Governova Score is issued when the assessed factors carry less than half the model's
weight.** The assessment is reported as **partial**: every assessed factor is shown with its
score, and no headline number and no grade are produced.

The threshold is **50 of 100** — a majority of the model. This is not a tuned number:

- It is the point at which more of the model is present than absent, which is the least that can
  be claimed by something calling itself a weighted average of five factors.
- It falls naturally where the product's own design already places the boundary. Violation rate
  alone is 30. Adding constitutional coverage brings it to 50 — and coverage becomes assessable
  exactly when a human accepts the proposed profile, which is the moment the tool stops guessing
  what applies to the repository.

So the score appears when the user has told the tool what it is looking at. Before that, the
honest output is a measurement, not a grade.

`certified_eligible` requires quorum. A repository cannot be Certified on a partial assessment.

### 2. Violation density is reported beside the count, and does not replace it

`violation_rate` keeps its definition, its weight and its arithmetic. **A separate density
figure — findings per scanned file — is reported alongside it.**

This is the pattern already used for `mechanical_coverage_pct` beside `coverage_pct`, and it
exists for the same reason: a metric's definition is never silently widened. Every historical
reading of `violation_rate` continues to mean what it meant.

Density is reported because the count alone cannot answer the question a reader actually has
once the factor reads zero — *how bad, and how spread out?* 52 findings across 32 files and 52
across 3,200 are the same number and different situations, and the factor is entitled to say so
without pretending to have measured something else.

---

## Consequences

**Easier**

- A mature repository's first contact is a measurement it can act on rather than an `F` it can
  dismiss.
- Density gives the count somewhere to go once it saturates, without redefining the count.
- The score's own claim becomes true: it is issued only when it is a weighted average of a
  majority of the model.

**Harder**

- Every surface that renders a score must handle "no headline". That is four renderers, and a
  partial state is more work to present well than a number.
- Adopters who want a number immediately will not get one. This is the intended cost — a number
  they should not trust is worse than a wait.
- Two figures where there was one. Density will be misread as the score by somebody.

**Not changed**

- No factor's weight. No factor's arithmetic. No historical reading of `violation_rate`.
- The saturation `D-03` describes is **still present** and still recorded. Density makes it
  legible; it does not remove it. Amending the penalty curve would be picking a number to
  produce a pleasing shape, and that decision has not been made here.

---

## Alternatives considered

**Normalise `violation_rate` by file count.** Rejected on the measurement: `click` and
`requests` carry more than one finding per file, so a density-based factor still returns them a
near-zero score. It would also silently reinterpret every previous reading of the factor, and it
flatters large repositories — 500 findings in 5,000 files would read as healthy.

**Soften the penalty curve — logarithmic or asymptotic.** Rejected as unprincipled *for now*.
Picking a curve is picking a number, and no defensible basis for a particular curve has been
established. This is deferred rather than refused; a curve derived from measured distributions
across many repositories would be a different and better proposal.

**Leave it.** Rejected. The factor is honest about count, but the *headline* is not honest about
what it rests on, and that is a separate claim from the factor's.

**Report a lower-confidence score rather than none.** Rejected. A number with a caveat beside it
is read as a number. The caveat is not what gets quoted.

---

## Standards

- **`S1.16`** — no bar was lowered. Both amendments make the model report *less* about a
  repository until it has grounds to report more.
- **`C0 §8`** — the law is amended before the check that implements it.
