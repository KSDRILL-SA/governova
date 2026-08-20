# ADR-011 — The corpus is the product: licence, price ladder, and the gates that unlock each tier

---

| Attribute   | Value |
|-------------|-------|
| **ID**      | ADR-011 |
| **Date**    | 2026-08-21 |
| **Status**  | accepted |
| **Amends**  | ADR-010 §1 (the paid boundary) |
| **Supersedes** | `docs/vision/master.md` §19.1 (tier feature table and price points) |
| **Relates To** | ADR-005 (workstream D), ADR-008, ADR-009, `#246`, `S5.28`, `S8.87` |

---

## Context

`ADR-010` settled that the paid boundary is *"needs a server we run"*, and concluded from that
the deterministic engine stays MIT while the Cloud is sold. **That reasoning was correct about
the engine and wrong about the corpus**, and this ADR corrects it.

The error was treating the compiled constitution as part of the engine. It is not. It is the
asset:

| | Engine | Corpus |
|---|---|---|
| Size | ~6,000 lines of Python | 670 standards · 508 anti-patterns · 15 constitutions · 4 domain packs |
| What it is | A markdown parser, a regex runner, a scorer | Ratified law with provenance, built over months |
| Replaceable in | Weeks, by a competent team | Not replaceable. That is the point |

`ADR-010` reasoned by analogy to how Anthropic sells: SDK free and open, model weights never
distributed. The analogy holds — but **our weights ship as a 1.1 MB JSON file inside an MIT
wheel**, so the licence has to do what their architecture does for free.

### What is already published, stated plainly

`governova` v0.1.0 (2026-07-30) and v0.2.0 (2026-08-20) both bundle
`governova_compile/data/constitution.json` — the complete compiled corpus — under MIT. **MIT
cannot be revoked for what has been distributed.** Both releases have negligible adoption, and
this is the cheapest moment this will ever be to correct.

### And the second thing this ADR has to settle

`master.md` §19.1's price points ($0 / $9 / $19 / $39) were carried forward unexamined by
`ADR-010`. Measured against the market they are wrong in both directions: too low for what an
individual gets, and off by roughly thirty times for what an organisation gets. Meanwhile
`ADR-010` priced tiers — SSO, Certification, the Mapping Engine — for capabilities that **do
not exist and in one case we would currently fail.**

---

## Decision

### 1. The corpus is licensed. The engine stays MIT.

**The engine remains MIT, complete, and offline forever** — every rule, probe, Score, Board
Report, System Bible, the MCP server, the CLI and the CI gate. `ADR-010` §1 stands on that
point and §5's four prohibitions stand entirely.

**The compiled constitution becomes a separately licensed artefact.** From v0.3.0:

- The free wheel bundles a **core subset** — roughly 120 universal standards, enough to govern
  a real project and see the engine work.
- **The full 670, the domain packs, and ongoing amendments require a subscription.**

The gate is **entitlement to download data**, not a check on executing code. No licence server,
no machine-ID binding, no phone-home — `ADR-010` §5.1's prohibition survives untouched, and the
engine must still run perfectly with the Cloud unreachable. It simply runs against whatever
corpus the operator holds.

**v0.1.0 and v0.2.0 are yanked from PyPI** and replaced by v0.2.1 carrying the core subset.
Yanking does not remove the artefact from anyone who already has it; it prevents new resolutions
onto it. That is the whole of what can be done, and it is worth doing now rather than after
adoption grows.

**The decay argument is why this holds.** `S8.87` is our own standard: a constitution ages. A
snapshot frozen at 2026-08-20 is a liability by mid-2027 — the corpus grew 618 → 670 in three
weeks. What is sold is not a file, it is **currency**.

### 2. One price ladder, anchored at R200

Set once, in both currencies independently rather than by conversion, and **it does not move
between stages.**

| Tier | USD /mo | ZAR /mo | Annual | Seats | Credits /mo | Gross margin |
|---|---|---|---|---|---|---|
| **Free** | $0 | R0 | — | 1 | 100 once | — |
| **Starter** *(verified)* | $6 | R99 | $60 · R990 | 1 | 400 | 73% |
| **Pro** *(anchor)* | $12 | **R200** | $120 · R2,000 | 1 | 800 | 73% |
| **Pro+** | $25 | R400 | $250 · R4,000 | 3 | 1,800 | 71% |
| **Team** | $29/seat | R500/seat | $290 · R5,000 | min 5 | 1,200/seat | 83% |

Everything derives from R200 — half for someone still learning, twice for a small team, two and
a half times for a seat inside a company. **One number to defend rather than five.**

Margins are computed against measured cost, not assumed: **3,169 input tokens per file review,
of which 1,967 are a cacheable prefix**, measured by building the prompt `build_messages()`
actually sends. Cache reads bill at ~0.1×, which is why the margins hold at these prices.
Figures above are at *full* credit consumption; typical utilisation of 25–40% puts blended
margin near 90%.

**Starter is paid, not free.** A free tier at 500 credits costs ~$2/month per account — $2,000
a month at a thousand users before any revenue. Starter earns $4.40 against $1.60 of cost from
the first account. It also signals the thing is worth something: a student who pays R99 opens
the tool; one who is handed it does not install it. Verified by `.ac.za`/`.edu` address for
students, and **self-declared for developers between roles** — no proof of unemployment is worth
asking a person to produce. Re-verified annually.

**Campus rate: R199 per student per year** for accredited training providers and universities.
A 300-strong cohort is R59,700 a year, and South African youth unemployment above 60% against
45,000 unfilled technical roles makes this a pipeline into the accounts in §3, not a donation.

### 3. One price, growing value — and it is why R200 is defensible today

**Prices do not rise between stages. What rises is what the money buys.**

Today R200 is the full corpus plus the complete engine. When the Intelligence Gateway ships,
the credit allotments above switch on **at no extra cost, on the same subscription**. Existing
subscribers are not renegotiated; they simply receive more.

This is a better founding offer than a discount, and it is the reason a corpus-only product can
carry R200 now: early customers are not paying less, they are **paying the same for
progressively more**. It also leaves no revenue hole to climb out of later.

### 4. The tiers that are not for sale yet

`ADR-010` priced Certification and Enterprise as though they existed. They do not, and one of
them we would currently fail. **Nothing below is sold until every gate is met** — each gate a
figure our own tooling already reports, none a judgement call.

| Gate | Today |
|---|---|
| Governova scores **≥ 85** on itself | **78** |
| Enforcement coverage **≥ 25%** | **7.5%** |
| Semantic tier clears `ADR-009`, **or** ships labelled advisory | 53% against a 90% bar |
| **SOC 2 Type I** | none |
| One named reference customer in production | none |

Then, and only then:

| Tier | USD | ZAR | Minimum |
|---|---|---|---|
| **Business** | $99/seat/mo | R1,599/seat/mo | 10 seats |
| **Enterprise** | from $30,000/yr | from R480,000/yr | — |
| **Certification** — Standard / Advanced / Enterprise | $2,500 / $7,500 / $25,000 per year | R40,000 / R120,000 / R400,000 | active subscription |

**The gate is also the marketing, and it is the strongest sentence this company can say:**
*"Certification opens when Governova scores 85 on itself."* True, checkable in this repository,
and unavailable to any competitor.

### 5. Rand pricing is a feature, not a discount

At R16.12 to the dollar, converting $12 gives R193 — close to the R200 anchor, so this is not
primarily about affordability. It is about **currency risk**. A South African bank buying
SonarQube pays in dollars and absorbs the exchange exposure itself. A rand-denominated contract
removes a line item every foreign competitor forces onto the buyer, and no foreign vendor owns
that relationship here yet.

Prices are therefore **set per market, not converted** — R200 and $12 are each round numbers in
their own currency, and neither is derived from the other.

---

## Consequences

### What becomes easier

- **The thing we defend is the thing worth defending.** Effort protects a corpus that took
  months, not a parser that takes weeks.
- **The pricing page has one number on it.** R200 anchors every other figure, which makes the
  ladder explicable in a sentence.
- **Nothing is sold that cannot be demonstrated.** Every gate in §4 is a number in this
  repository, so the roadmap and the price list cannot drift apart.
- **Margins are known rather than hoped** — measured against the real prompt, at 71–84% before
  utilisation effects.

### What becomes harder

- **Yanking published releases is a real cost.** Anyone who installed v0.1.0 or v0.2.0 keeps the
  full corpus permanently, and yanking is a visible action that invites the question of why.
  Answer it plainly rather than quietly.
- **The core subset has to be chosen, and it is a judgement.** Too small and the free tier
  governs nothing and nobody experiences value; too large and Starter never converts. ~120 is a
  starting figure, not a derived one.
- **R200 before the Gateway ships is a promise.** The "growing value" story carries it only if
  Stage 2 actually lands. If Cloud slips a year, R200 for a corpus starts to look like a
  commitment we did not keep.
- **Every Stage 3 gate is currently unmet**, which means the highest-margin lines in the
  business — Certification above all — are blocked behind `#246`'s roughly 199 additional
  evidenced standards. That is the single largest commercial risk in this document.

### Constitutional alignment

- **`S8.87`** — the corpus decays without maintenance; currency is what a subscription buys.
- **`S5.28` / `AP-S5.28a`** — credit and monetary arithmetic uses `Decimal`, and balances are
  stored as integer minor units in string form so no float ever touches them.
- **`S10.8` / `AP-S10.8b`** — unchanged: L4 approval, including amendment, stays human-only.
- **`REQ-008`** — unchanged: the semantic tier never changes a build result, metered or not.
- **`ADR-010` §5** — all four prohibitions survive intact. Licensing *data delivery* is not
  gating *code execution*.

---

## Reversibility

**Asymmetric, and the asymmetry is the point.**

Yanking is reversible — a release can be un-yanked. What is not reversible is that the v0.1.0
and v0.2.0 corpora are in the wild under MIT, permanently. The corpus licence therefore protects
everything from v0.3.0 onward and nothing before it, which is precisely why acting now rather
than after adoption matters.

Prices are cheap to revise. **Gates are not** — publishing "Certification opens at 85" and then
selling certification at 78 would destroy the only asset that makes any of this saleable. Treat
§4 as immutable in the direction of loosening.

The core-subset boundary is tunable release to release without breaking anyone, since the engine
reads whatever corpus it is given.
