# ADR-009 — Map/Adapt and Always-On Learning Are Deferred, and the Bar Is Not Amended

---

| Attribute   | Value |
|-------------|-------|
| **ID**      | ADR-009 |
| **Date**    | 2026-08-20 |
| **Status**  | accepted |
| **Supersedes** | — |
| **Relates To** | ADR-005 (workstream C), ADR-008 (the trust bar), `#138`, `S1.101`, `S8.87`, `REQ-008` |

---

## Context

`ADR-005` workstream C defines four brownfield modes. Two are deterministic and shipped in
v0.2.0 — Scan & Learn (`onboard`, `roadmap`) and Scan, Learn & Rewrite (`convert`). The other
two, **Map/Adapt (Stage 3)** and **Always-On Learning (Stage 4)**, depend on the semantic tier.

`ADR-008` established that the tier reaches nothing by default and set the bar it must clear
before anything is built on it: **90% worst-run precision, with recall held.** The reasoning is
that an invented finding discredits every other finding the tier makes.

The tier has now been measured at five runs per condition, across three conditions, using the
`governova semantic-eval` harness built for exactly this purpose:

| Condition | Worst-run precision | Recall | Spread | Verdict |
|---|---|---|---|---|
| Baseline (5 runs) | 45% | 90% | 45–60% | — |
| **H1** — excerpt framing | 50% | **80%** | 50–56% | **rejected — cost recall** |
| **H2** — confidence filter | **53%** | **90%** | 53–75% | kept |
| H2 confirmation (5 more) | **53%** | **90%** | 53–69% | floor reproduces |

**53% against a bar of 90%.** The floor reproduced exactly across an independent second set of
five runs, so this is a measurement rather than a bad day.

Three further facts bear on the decision and were established at cost:

- **Everything measured before `#181` was invalid.** The grounding filter selected standards by
  word overlap between their titles and identifiers in the code, so backends were scored on
  standards they were never shown. Those figures were removed rather than annotated.
- **Three runs cannot separate an 8-point change from noise** on this backend — the baseline's
  own three runs ranged 45%–56%. Five runs per condition, one change at a time.
- **The endpoint looks healthy to a naive probe while failing real work.** `say ready` returned
  `200` in 2–5s throughout a period when 5 of 17 real fixtures returned `HTTPError`.

`planning/phase-3-brownfield.md` already records the standing position: *"If a later backend
lands just short, that is when amending the bar becomes a live question — deliberately, not
quietly."*

---

## Decision

**Stages 3 and 4 are deferred. `ADR-008`'s 90% bar is not amended, and no context-varying bar
is introduced.**

### Why the bar is not amended

The case for amending it is real and was considered: the 90% bar is calibrated for a
**blocking gate running unattended in someone else's CI**, and Stage 3 is a different context —
a human is present, reviewing a proposal, on first contact with their own repository. `convert`
already established that shape: propose diffs, refuse the unsafe ones, never auto-apply.

It is rejected on one ground. **53% is not "just short" of 90%, and an amendment written to
accommodate a number 37 points away is not a recalibration — it is the bar following the
measurement.** A governance product that moves its own threshold to admit the capability it
wants is doing the thing it exists to refuse. The standing rule is that a threshold must sit
between two reachable scores; this one does, and the tier is below it.

The context-varying bar remains the right idea for a backend that lands close. It is recorded
here so it is not re-derived, and it is not adopted now.

### Why deferral, not indefinite parking

**Deferring with no criteria is the `S8.87` decay that produced `#142`.** So this deferral
carries explicit re-entry criteria. Stages 3–4 reopen when **any one** of these holds:

1. **A backend measures ≥85% worst-run precision with recall held at ≥90%**, over five runs per
   condition, through `governova semantic-eval`. At that point the tier is *just short*, and
   the context-varying bar in the section above becomes the live question this ADR declines to
   settle today.
2. **A Governova-tuned local model (`#138`) lands and clears (1).** `ADR-008` already makes the
   local path the strategic direction; this makes Stage 3 one of its acceptance criteria.
3. **Workstream D closes and workstream C is deliberately re-scoped** against what the Cloud
   makes possible — including a metered hosted tier that may reach precision a free local
   backend cannot.

Absent all three, Stages 3–4 stay closed and nobody re-opens the analysis from scratch.

### What proceeds instead

**Workstream D — Governova Cloud.** `ADR-005` sequences it last and largest and notes it is
where the revenue sits, which is the argument for *finishing* C rather than perfecting it. C is
finished at Stages 0–2: a repository Governova has never seen can be baselined, prioritised and
safely converted, deterministically, with zero blocking-tier false positives measured across
three third-party repositories in three stacks.

---

## Consequences

### What becomes easier

- **The critical path stops running through an unmeasurable dependency.** Stage 3 has been
  "blocked on a decision, not on code" across three handoffs; it is now settled, and the next
  engineer starts at workstream D rather than re-deriving the semantic evidence a fourth time.
- **The trust claim stays intact.** Governova continues to hold its own tier to the bar it
  publishes, at the cost of a feature it wanted. That is the more valuable asset.
- **`#138` gains a concrete acceptance criterion** instead of being an open-ended aspiration.

### What becomes harder

- **Map/Adapt does not ship, and it is the mode enterprise adopters ask for first.** An
  organisation with its own existing standards cannot have them mapped onto the Governova index
  automatically. The manual route remains: `protocols/practice-to-standard.md` documents the
  worked method, and it is a human process.
- **Always-On Learning does not ship**, so the constitution does not improve itself from
  observed practice. Amendments stay entirely human-proposed under `C0 §8` — which is the
  correct default, but slower.
- **`ADR-005`'s workstream C is delivered at two modes of four**, and that should be stated
  plainly in any roadmap that claims C is complete. It is complete *as scoped by this ADR*, not
  as originally specified.

### Constitutional alignment

- **`REQ-008`** — an advisory tier never changes a build result. Preserved: nothing new is built
  on a tier that cannot be trusted.
- **`S8.87`** — the external surface decays on its own. The re-entry criteria are what stop this
  deferral from becoming the undated parking that produced `#142`.
- **`S1.101`** — untested legacy code is not rewritten. Unaffected, and it would have bounded
  Stage 3 regardless.
- **`C0 §8`** — amendments are human-proposed and human-ratified. Stage 4 would have had an
  engine proposing them; deferring it keeps the amendment path entirely human for now.

---

## Reversibility

**Cheap, and deliberately so.** Nothing is deleted. `governova semantic-eval`, the fixtures, the
grounding filter and the confidence filter all remain shipped and working, so re-entry is a
measurement run rather than a rebuild — the harness is the thing that took the time, and it
survives this decision intact.

Re-opening requires no code change to reverse: run the harness against a candidate backend at
five runs per condition, and if criterion (1) holds, amend this ADR rather than working around
it.

**Whatever is measured next: recall must not fall · five runs per condition · one change at a
time · and read `ADR-008` and `planning/phase-3-brownfield.md` §5 first.** The endpoint looks
healthy to a naive probe while failing real work, and that has cost two sessions already.
