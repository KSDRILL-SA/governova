# Phase 3 — Brownfield Onboarding

| Attribute | Value |
|-----------|-------|
| **Decision** | `governance/decisions/ADR-005-platform-architecture.md` — workstream C |
| **Status** | Planned — ready to implement |
| **Sequenced** | After Phase 2 (ADR-007, complete), before Phase 4 (workstream D — Cloud) |
| **Paired protocols** | `protocols/brownfield-adoption.md` · `protocols/practice-to-standard.md` |

> Read ADR-005 workstream C first. It carries the decision; this document carries the work.
> Every stage below is independently shippable through branch → issue → PR → merge.

---

## What this phase is

Governova can govern a repository it has always governed. **It cannot yet onboard one it
has never seen** — and every real customer arrives with a system that already exists.

That is the entire gap. The engine has the analysis; it has no way to *arrive*.

ADR-005 defines four modes:

| Mode | What it does | Tier |
|---|---|---|
| **Scan & Learn** | Read-only. Baseline score, gap heatmap, the honest starting line | deterministic |
| **Scan, Learn & Rewrite** | Proposes a diff; nothing is applied without review | deterministic |
| **Map / Adapt** | Maps an organisation's *own* standards onto the Governova index, in their language | **semantic** |
| **Always-On Learning** | Periodically re-analyses the repo and proposes amendments | **semantic** |

---

## The bar this phase is held to

Phase 2's bar was about the *corpus*. Phase 3's is about **trust on first contact**, because
that is what this phase actually risks.

| Metric | Required |
|---|---|
| False positives in a baseline report | **Zero blocking-tier false positives** on a real third-party repository |
| Standards added | **≤ 6**, and ≥ 50% mechanically enforced — this phase is engine work, not corpus work |
| Constitutional coverage | Must **not fall**. It is 9.9%; adding standards without evidence lowers it |
| Governova Score | ≥ 78 — no regression |
| Applying a change | **Never without an explicit, reviewable diff** |

**The first run against somebody else's repository is the only first impression this
product gets.** A baseline that reports forty violations, of which six are wrong, is a
baseline nobody reads twice. Prefer reporting less and being right.

---

## What already exists

**Most of this phase is assembly, not invention.** Know what is already built before
writing anything:

| Capability | Where |
|---|---|
| Gap analysis — reliable tier | `governova_checks` (40 rules, 12 blocking) |
| Gap analysis — repository facts | `governova_evidence` (18 probes) |
| Requirements analysis | `governova_requirements` (tiers 0–3, linter, trace, closure) |
| Schema soundness | `governova_schema` (Prisma + SQL DDL) |
| Baseline score + coverage | `governova_score`, `governova_project` |
| Applicability derivation | `governova_project` (from `governance/project.toml`) |
| The Mapping Engine's worked method | `protocols/practice-to-standard.md` |
| Source-corpus extraction | `governova_ingest` |
| The human protocol (6 phases) | `protocols/brownfield-adoption.md` |
| The law | `S1.101` characterisation tests · `S1.102` adoption completeness · `S6.45` incremental non-breaking · `S8.83` per-step reversibility · all of C13 |

**What does not exist: an entry point.** There is no `governova onboard`. That is Stage 0.

---

## Stage 0 — Arrival

**Ships:** `governova onboard` — the read-only baseline. **Nothing else can start until
this is merged.**

This is Scan & Learn, and it is the mode most adopters will only ever use.

### 0.1 · The baseline report

One command against a repository Governova has never seen, producing:

1. **Detected profile** — stacks, languages, whether it has tests, CI, a schema,
   requirements. Written as a proposed `governance/project.toml`, never applied silently.
2. **Baseline score** — the honest starting line, with all five factors.
3. **Gap heatmap** — per constitution: applicable, evidenced, violated, unknown.
4. **Top findings, risk-ranked** — blocking first, and never more than can be read.

### 0.2 · The rule that governs the whole phase

**Detection must degrade, never guess.** A repository with no tests is not a repository
that fails `S7.6`; it is one where the question is `unknown`. Every tier already follows
this and Stage 0 must not be the place it breaks — the temptation is strongest here,
because a baseline full of `unknown` looks less impressive than one full of violations.

It is also the honest one, and it is what makes the second run credible.

### 0.3 · Profile detection is a proposal

`governance/project.toml` decides applicability, so getting it wrong distorts every number
downstream. Stage 0 **proposes** it with its reasoning and requires a human to accept it.
Never write it silently.

**Exit criteria:** `governova onboard` runs against three third-party repositories of
different stacks · **zero blocking-tier false positives** · profile written only on
explicit acceptance · a repository with nothing detectable produces a *useful* report
saying so, not an empty one.

---

## Stage 1 — Remediation planning

**Ships:** the risk-ranked roadmap — `protocols/brownfield-adoption.md` Phase 2 made
mechanical.

A baseline says what is wrong. A roadmap says **what to do first**, and that ordering is
the product. Ranking is by *blast radius × effort*, both derivable:

- **Blast radius** — the standard's priority, whether it is blocking, and how many files
  the finding touches.
- **Effort** — how many findings share a single fix (one repository boundary fixes forty
  `AP-S1.104a`), and whether a characterisation test exists to protect the change.

Output is issue-shaped: each item is one PR, individually green, individually revertible
(`S8.83`).

**Exit criteria:** the roadmap orders by measured blast radius, not by standard number ·
every item names its standard and its evidence · a repository with no findings produces an
empty roadmap rather than busywork.

---

## Stage 2 — Safe conversion

**Ships:** Scan, Learn & Rewrite — proposed diffs, never applied without review.

The two guarantees are already law and must be mechanised here, not restated:

- **`S1.101`** — characterisation tests pin behaviour *before* any refactor. A conversion
  proposed against untested code must say so and refuse to auto-apply.
- **`S6.45` / `S8.83`** — incremental, non-breaking, individually reversible.

**Start with the conversions that are mechanically safe**: import reordering, config
extraction to named constants, adding missing indexes flagged by the schema analyser. **Do
not start with the repository pattern**, however tempting — it is the highest-value fix and
the one most likely to change behaviour.

**Exit criteria:** every proposed change is a reviewable diff · nothing applies without
explicit confirmation · a proposal against untested code is refused with the reason ·
each applied change is individually revertible.

---

## Stage 3 — Map / Adapt · **semantic-gated**

**Ships:** mapping an organisation's own standards onto the Governova index.

This is `master.md §14`'s Mapping Engine, and **the worked example it must reproduce
already exists** — `protocols/practice-to-standard.md`, written in Phase 2 Stage 0
precisely so this could be built from evidence rather than imagination. Read it before
designing anything.

> **This stage depends on the semantic tier, which is inert by default (ADR-008).** See §5
> below. Do not start it until that decision is made and the evaluation harness exists.

---

## Stage 4 — Always-On Learning · **semantic-gated, and consent-gated**

**Ships:** periodic re-analysis proposing constitutional amendments.

ADR-005 is explicit that this **requires explicit consent and a defined data-handling and
privacy posture**. That is not a footnote:

- Nothing leaves the machine without opt-in.
- What is analysed, what is retained, and for how long is stated before the first run.
- A proposed amendment is a *proposal*. `C0 §8` governs amendments and **L4 is human-only,
  always** — an engine that proposes is correct; one that ratifies is a constitutional
  violation by construction.

> Semantic-gated, as Stage 3. Additionally gated on the privacy posture being written.

---

## §5 — The semantic-tier dependency, and what to do about it

ADR-005 says workstream C uses *"the existing provider-agnostic semantic tier for the AI
parts."* **ADR-008 established that tier reaches nothing by default** — GitHub Models was
retired, and every remaining provider needs an account and a credential.

So Stages 3 and 4 have no engine unless something changes. Three options, and a
recommendation.

| Option | Assessment |
|---|---|
| **Ship a local model now** (`#138`) | **Measured and rejected** — see below |
| **Defer indefinitely** | Deferring with no criteria is the `S8.87` decay that produced `#142` |
| **Build the evaluation harness first** | **Done** — `governova semantic-eval`, #171/#175 |

### Measured — and re-measured after the grounding defect

**Everything measured before 2026-08-01 was invalid.** `#180` found that the tier's
grounding filter selected standards by word overlap between their *titles* and the
*identifiers in the code*: on a loan-assessment handler all twelve it chose matched a single
incidental token, and the standards the code actually violated were never submitted.
Backends were being scored on standards they were never shown. The figures that stood here
have been removed rather than annotated — a stale number in a plan gets quoted.

**Latest measurement** — `gpt-oss:120b-cloud`, 17 fixtures, 10 required findings, 3 runs,
worst run governs. Figures are **after** `#191`:

| | before `#191` | after `#191` |
|---|---|---|
| worst-run precision | 33% | **47%** |
| worst-run recall | 90% | **90% — held** |
| false positives per run | 11 / 11 / 18 | 9 / 10 / 7 |

**Still FAIL. 47% is not close to 90%.**

`#191` sent each standard's anti-pattern description as an explicit *report only when*
clause, on the theory that statements like "never inlined as literals in code" are
prohibitions with no stopping condition. It bought **14 points of worst-run precision at
zero recall cost**, which is why it was kept — but **the predicted mechanism was wrong.**
The two fixtures written as the *negative case* for `S1.105` and `S2.53` are still flagged
by the standard they satisfy, and `clean-ownership-checked-before-read` picked up `S1.103`
on top. The noise partly *moved* rather than reduced.

So the remaining false positives are no longer concentrated in two standards — they are
spread one or two each across five. **That is a different problem from the one `#190` was
opened for, and the "give those two a stopping condition" framing is closed.**

The evidence now points at something the prompt cannot reach: **the model judges a snippet
with no surrounding codebase.** `clean-ownership-checked-before-read` calls
`documents.get_for_owner(document_id, owner_id=user.id)` — ownership *is* enforced, but only
if you trust the method name. Next hypotheses, in cost order:

1. **Say in the prompt that the snippet is an excerpt**, and that a called function may be
   assumed to do what its name says. Cheap, and aimed straight at the two survivors.
2. **Ask for a confidence and drop low-confidence findings** — the same idea as the existing
   ungrounded-citation filter, applied to certainty.
3. **Only then** a tuned local model (`#138`).

**So the tier is restraint-limited, not reach-limited**, and the deficit is concentrated:
`S1.105` causes 8 of 11 false positives and `S2.53` causes 4, while `S1.3`, `S1.107` and
`S2.18` are essentially quiet. Two of those are damning rather than debatable — the fixtures
written as the *negative case* for `S1.105` and `S2.53` were both flagged by the very
standard they satisfy. Both statements read as unconditional prohibitions (*no* magic
values, *any* user-scoped operation), so the model has no stopping condition.

The other local result that survives: **`qwen2.5-coder:1.5b` invents findings freely**, firing
on every clean fixture including a `slugify` function, at ~100s per file. **`qwen2.5-coder:7b`
is unmeasurable on the dev machine** — one fixture hit the 900s timeout, the set extrapolates
to ~2 hours — which is a hardware verdict on an Intel N150, not a model verdict. Nothing is
known about it either way.

### Why not the local model yet

**Its quality can now be measured, and nothing has passed.** The harness exists, and the
argument it was built to settle still stands: shipping an unmeasured model into a governance
tool is exactly the *false satisfied* the whole corpus forbids. A semantic tier that invents
a finding against `S1.104` is worse than one switched off, because a wrong finding teaches
people to discount the right ones — and at 33% precision that is what would happen.

**It is also a different discipline** — eval sets, serving, distribution size, licensing —
opened while Phase 3 is the thing with adopters waiting. And **ADR-005 already put AI on
the metered side** of the business model (Phase 4's Intelligence Gateway); a bundled local
model needs a decision about how it relates to that.

### The recommendation

The harness is built and has done its job: `#138` is now a decision backed by numbers
rather than intuition, and **any** backend — local or hosted — is gated behind a
measurable bar, so the next endpoint retirement is survivable.

Experiments remaining, in cost order — the first is now much narrower than it looked:

1. **Give `S1.105` and `S2.53` a stopping condition in the submitted catalogue.** They cause
   most of the deficit, and both read as unconditional prohibitions. This is a
   prompt-construction change, not a corpus change — the standards are correctly written for
   human readers. **One run of 1.9 minutes to find out.**
2. **Submit fewer standards per review** — eight structural standards on one snippet invites
   eight opinions. Scope by `applies_to` and language, or review in smaller grounded batches.
3. **Only then** a tuned local model, which is what `#138` is actually about — and note that
   this repository has **no evidence either way** about a competent local coder model, since
   the 7b could not be run here.

**The bar stands.** It was unreachable by construction before `#181` — at four required
findings the only reachable precisions were 100%, 80%, 67%, 57% and 50%, so 90% silently
meant *zero false positives in every run*. At ten required findings one mistake passes and
two fail, and a test holds that property. If a later backend lands *just* short, that is when
amending the bar becomes a live question — deliberately, not quietly. 33% is nowhere near it.

Until then: BYO endpoint works today, and the local OpenAI-compatible recipe is documented
in ADR-008 — offline, free, no account.

**The local model remains the right destination.** Offline, free, private and unmetered
beats a metered vendor for the free wedge. It should arrive when the harness can prove it,
and probably after Phase 4 clarifies where the revenue sits.

---

## Sequencing and dependencies

```
Stage 0  Arrival — `governova onboard`     ── blocks everything
   │
   ├── Stage 1  Remediation planning
   │      └── Stage 2  Safe conversion   (needs Stage 1's ranking)
   │
   └── ⟨evaluation harness⟩  ── blocks Stages 3 and 4
          ├── Stage 3  Map / Adapt
          └── Stage 4  Always-On Learning  (also needs the privacy posture)
```

**Stage 0 blocks all of them. Stages 3 and 4 are blocked on a decision, not on code.**

---

## Traps specific to this phase

1. **Do not let the baseline guess.** The temptation is strongest in Stage 0, because a
   report full of `unknown` looks less impressive than one full of violations. The second
   run is where credibility is won, and a wrong finding in the first run means there is no
   second run.
2. **Do not write `governance/project.toml` silently.** It decides applicability, so a
   wrong profile distorts every number downstream — and the adopter will believe the
   numbers before they believe the profile.
3. **Do not auto-apply anything.** `S1.101` requires characterisation tests before a
   refactor. A tool that rewrites untested legacy code is the single fastest way to break a
   working system and end an adoption.
4. **Do not start conversion with the repository pattern.** Highest value, highest chance
   of changing behaviour. Earn trust on the safe conversions first.
5. **Do not add standards to make this phase feel constitutional.** Phase 3 is engine work.
   Six standards is a ceiling, not a target — and coverage is a ratio, so unevidenced
   additions lower the score while looking like progress.
6. **Do not let the learning engine ratify.** It proposes; `C0 §8` disposes, and **L4 is
   human-only, always.** An engine that amends its own constitution is the failure the
   relay was built to refuse.
7. **Do not build the Mapping Engine from imagination.** The worked method is written down
   (`protocols/practice-to-standard.md`) specifically so it does not have to be.

---

## What this phase is claiming

**That a system Governova has never seen can be onboarded without breaking it.**

Every governance product can grade a greenfield repository its own tooling created. The
hard problem — the one that decides whether this is a product or a demo — is arriving at
a decade-old system, telling the truth about it, and improving it in steps that are each
individually safe, reviewable, and reversible.

Phase 2 made the corpus able to *discuss* requirements and schemas. Phase 3 is what makes
that reach anybody else's code.
