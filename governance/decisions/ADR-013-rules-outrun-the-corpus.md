# ADR-013 — A rule fires for a defect, not for a licence

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-08-22 |
| **Authority** | L4 — `C0 §8`. Interprets `ADR-010 §5.1` and `ADR-011`'s corpus boundary |
| **Supersedes** | Nothing. Decides the question `ADR-011` left open |
| **Tracked** | `D-24` |

---

## Context

`ADR-011` split the corpus: a **core** subset ships in the wheel under MIT, and the domain packs
are licensed. `#8`'s implementation made that real — the built wheel carries 167 anti-patterns,
the full corpus carries 789.

The rules did not split, and could not: they are code, they ship in the same MIT wheel, and
every one of them works. Measured on the current build:

| | Full corpus | Core wheel |
|---|---|---|
| Rules | 64 | 64 |
| Rules citing an anti-pattern in the corpus | 64 | **18** |
| Anti-patterns in the corpus | 789 | 167 |
| `coverage_pct` | 7.6% | **10.8%** |

So on a core installation, **46 of 64 rules cite law the operator does not hold**. They still
scan, still match, and still produce findings — the regex does not consult the corpus.

Three things follow from that, and none of them had been decided.

### 1. Nothing says whether those rules *should* fire

This is the question `D-24` recorded and the reason this ADR exists. It reads like a packaging
detail and it is a product decision: it determines what the free tier does.

### 2. `validate_rules` reports 46 defects that are not defects

`validate_rules` implements `REQ-006` — *the rule set cannot drift from the corpus it enforces*
— by returning every anti-pattern id a rule cites that the index does not define. Against the
full index it returns nothing. Against the core index it returns 46.

Those 46 are not drift. They are the licence boundary, correctly placed, being reported by a
function that has no way to tell the two apart.

### 3. The coverage number goes **up** on the smaller corpus

10.8% on core against 7.6% on full, because the denominator shrank faster than the numerator.
Both figures are correct — 18 of 167, and 60 of 789 — and a reader who sees them side by side
without being told which corpus each was computed against will conclude that coverage improved
when the corpus was cut. Nothing in the payload says which corpus it describes.

---

## Decision

### A rule fires whether or not the operator holds the law it cites

The alternative — a rule that goes dormant when its anti-pattern is outside the installed
corpus — is rejected, and it is rejected on a stronger ground than preference.

**`ADR-010 §5.1` prohibits it.** That section guarantees the deterministic engine runs
*complete and offline forever*: no licence server, no machine-ID binding, no phone-home. A rule
that withholds a finding because the operator's corpus does not include the relevant standard
is a licence check evaluated locally. It is the cleanest imaginable implementation of exactly
the thing `§5.1` forbids, and the fact that it needs no network does not make it something
else. The prohibition is on the engine gating itself by entitlement, not on the mechanism used
to do the gating.

Two further reasons, either of which would be sufficient on its own:

**The finding is the value; the citation is the provenance.** Money held in a `float` is a
defect in a payments codebase whether or not the operator has licensed C05. The standard
explains *why it is a defect* and gives it authority. It does not make it one.

**Dormancy would make the free tier worse than no tool at all.** A scanner that silently
declines to report a defect it detected is the precise failure this project exists to name.
The verdict discipline everywhere else in the engine is that a check which cannot determine an
answer returns `unknown` and never `satisfied`; a dormant rule returns `satisfied` for a file
it found a problem in. We do not get to hold that line for probes and abandon it for revenue.

### The three consequences must be handled, or the decision is dishonest

**(a) The citation must not dangle.** A finding that cites `AP-S5.28a` on an installation with
no `S5.28` is a finding the reader cannot look up, and "buy the domain pack to find out what is
wrong with your code" is not a defensible thing for a scanner to say. Every rule therefore
carries its own one-line statement of what it detects and why, shipped in the code beside the
pattern. The corpus **deepens** a citation — full statement, rationale, related standards — it
does not gate it.

**(b) `validate_rules` keeps its meaning and stops conflating two conditions.** `REQ-006` is an
authoring-time invariant: a rule citing an anti-pattern that exists **nowhere** is a bug, and
that check is evaluated against the full corpus, where the answer is and must remain zero. A
rule citing law outside *this installation's* corpus is a **fact about the installation**, and
is reported separately, by a function whose name says so, with no severity attached.

**(c) Every coverage payload states which corpus it was computed against.** The numbers are
already right; what is missing is the label that makes them comparable. A coverage figure
without its denominator's provenance is a number that invites exactly the wrong conclusion.

---

## Consequences

**The free tier is a complete scanner.** All 64 rules, all findings, every one with a reason.
What the licence buys is the law: the full statement, the rationale, the domain packs, the
standards that carry no mechanical rule at all, and the ability to govern against them.

**`coverage_pct` on a core installation is not comparable to `coverage_pct` on the full
corpus,** and both are now labelled so nobody has to know that.

**A rule may be written for an anti-pattern outside the core subset,** and that is normal
rather than a defect to be worked around. It is how a domain pack gets mechanical enforcement.

**This does not decide what a Cloud-connected installation does.** The hosted surfaces read the
corpus the operator holds. Nothing here creates a path for the engine to acquire law at
runtime, and `§5.1` would have to be amended before one could exist.

---

## What this does not do

It does not make the 46 rules *useful* to a core operator in the way the 18 grounded ones are.
A finding with a one-line reason is weaker than a finding backed by a ratified standard with a
rationale and a review history. That gap is the product's honest sales argument, and stating it
plainly is better than closing it by making the free tier quietly defective.
