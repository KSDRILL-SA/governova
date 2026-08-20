# ADR-010 — Governova Cloud: the paid boundary, the stack, and the Intelligence Gateway

---

| Attribute   | Value |
|-------------|-------|
| **ID**      | ADR-010 |
| **Date**    | 2026-08-20 |
| **Status**  | accepted |
| **Supersedes** | `docs/vision/master.md` §19.1 (tier feature table) and §19.2 (licence-server protection model) |
| **Amends**  | ADR-005 (workstream D — resolves its first open question, the token-credit economics) |
| **Relates To** | ADR-006, ADR-008, ADR-009, `S6.1`–`S6.7`, `S3.1`, `S3.5`, `S3.13`, `S3.14`, `S5.9`, `S5.28`, `S8.1`, `S8.2` |

---

## Context

`ADR-005` locked four workstreams and sequenced **D — Governova Cloud** last and largest. A, B
and C are now closed: C shipped Stages 0–2 in v0.2.0, and `ADR-009` deferred Stages 3–4 with
explicit re-entry criteria. D is the remaining bulk of the product and **no code exists**.

`ADR-005` left three open questions "resolved in later, dedicated ADRs". This resolves the
first — token-credit economics — and settles the architecture. The Always-On Learning privacy
posture is moot while `ADR-009` holds it deferred, and non-software process governance stays
out of scope.

### The product is described twice, and shipping settled it

`master.md` §19 and `ADR-005` describe different products, and **v0.2.0 has already decided
between them in fact**:

| `master.md` §19 says | What is true on PyPI today |
|---|---|
| Free tier: 1 project, **3 critical anti-pattern alerts** | all 42 rules, unlimited projects |
| MCP server is a **Max**-tier ($39/mo) feature | ships in the wheel |
| Premium features call a **licence server** for feature flags | no such code exists |
| Protected by **machine-ID binding, concurrent session detection** | no such code exists |
| A self-hosted fork "gets none of the Score" | `governova govscore` runs offline |

The package is **MIT**, published, and complete on the deterministic side. **MIT cannot be
revoked for what is already distributed.** §19.1 and §19.2 are not aspirations awaiting
implementation; they describe a product that can no longer be built from here, and leaving them
in force would mean designing a Cloud around a gate that cannot exist.

---

## Decision

### 1. The paid boundary is "needs a server", not "is valuable"

**The local deterministic engine stays MIT, complete, and offline forever.** Every rule, probe,
score, report, Bible, the MCP server, the CLI and the CI gate are free, now and in every future
release. This is `ADR-005`'s plane 1 held to literally, and it is the wedge.

**Governova Cloud sells what a local tool cannot do**, and nothing else:

| Free forever — MIT, offline | Governova Cloud — paid |
|---|---|
| all deterministic rules and probes | **Intelligence Gateway** — metered AI with effort tiers |
| Score · Board Report · System Bible | **Intelligence Network** — cross-project learning (§15.1) |
| CLI · MCP server · CI/CD gate · PR Guardian | hosted dashboard, history and trend |
| `onboard` · `roadmap` · `convert` | organisations, teams, seats, SSO |
| the whole compiled constitution | Certification programme (§18.2) |
| | Temporal governance feeds (§15.2) |

The test for any future capability: **does it require a server we run?** If it runs correctly on
a laptop with no account, it is free. A capability is never moved behind the boundary because it
turned out to be popular.

**This is not generosity, it is the only coherent position.** A governance product's asset is
being trusted, and a free tier crippled to 3 alerts teaches an adopter that the numbers are a
sales instrument. The engine being complete and verifiable is what makes the Score worth paying
to have hosted.

§19.1's price points (Free / Pro $9 / Pro+ $19 / Max $39) and §16's mode mapping survive
unchanged. **What each tier buys is redefined** as Cloud entitlements — seats, credit budget,
retention, org features — never as local features withheld.

### 2. Stack: Angular + FastAPI, scored against the matrix rather than chosen

`S6.6` requires an ADR against the rubric for a new system type.
`constitution/indexes/stack-assignment-matrix.md` scoring:

| Criterion | → Next.js | → Angular + FastAPI | Governova Cloud |
|---|---|---|---|
| SEO requirement (public, discoverable pages) | +3 | 0 | **0** — the control plane is authenticated; the marketing site is a separate system |
| SSR/SSG required for performance/indexing | +3 | 0 | **0** — authenticated dashboards, nothing to index |
| Enterprise multi-role dashboard, complex forms | 0 | +3 | **+3** — orgs, teams, seats, roles, billing, exception recording |
| Precision financial calculations required | 0 | +3 | **+3** — credit metering and subscription billing |
| Python AI (LangChain, embeddings) required | 0 | +3 | **+3** — the Gateway wraps `governova_semantic` |
| React ecosystem preference / existing team | +1 | 0 | **0** |
| Dedicated Python data team exists | 0 | +1 | **+1** — the engine is Python and this team maintains it |
| **Total** | **0** | | **10** |

**Angular + FastAPI, 10 to 0.** Not close, and not a preference.

The decisive fact is structural rather than scored: **the engine is Python.** The Gateway must
call `governova_semantic` and the hosted surfaces must read the same
`compiled/constitution.json` the CLI reads. A Next.js backend would shell out to Python or
reimplement the engine — and a second implementation of the compiler is the exact failure that
`governova validate` existing twice already taught this repository.

Inherited from the matrix, not re-decided: PostgreSQL via Prisma (`S5.9`), FastAPI on Railway
(`S8.2`), Angular on Vercel (`S8.1`, `S8.3`), Vitest (`S7.2`), RS256 JWT issued by FastAPI
(`S3.1`, `S3.5`, `S3.13`), refresh token in an HttpOnly cookie and access token in Angular
memory (`S3.6`, `S3.14`).

### 3. Authentication: device grant for the CLI, RS256 for everything

`ADR-005` specifies **OAuth 2.0 Device Authorization Grant** (RFC 8628) for `governova login`,
and it composes with the matrix rather than competing: the device grant is how a CLI *obtains* a
token; FastAPI still issues RS256 JWTs and remains the only issuer.

- `governova login` → device code → browser approval → token stored in the **OS keychain**
  (Keychain / Credential Manager / Secret Service), never in a dotfile.
- **API keys exist only as a CI fallback**, scoped to one organisation, revocable, and never the
  documented path for a human.
- **Machine-ID binding and concurrent-session detection are dropped with §19.2.** They are DRM
  for a local binary that is MIT and cannot be bound, and they would punish the ordinary case —
  one engineer, laptop and CI — to deter a copy that `pip download` already permits.

`S3.14` (access token in memory, never `localStorage`) is enforced by `AP-S3.14a`, a rule this
repository ships. **The Cloud is scanned by the gate it sells.**

### 4. The Intelligence Gateway meters effort, and degrades rather than cuts

The Gateway is the metered path to the semantic tier. It is the only paid capability that
touches user code, so its contract is stated before it is built:

- **Effort tiers** — Low / Medium / High / Max, being *model size × reasoning depth × review
  passes*. A tier is a declared intent, and the mapping from tier to model is ours to change as
  models change; the price of a tier is not.
- **Credits accrue hourly** against a tier budget rather than resetting monthly, so a subscriber
  who works in bursts is not punished for the shape of their week.
- **Degrade, never hard-cut.** Approaching the cap, the Gateway downshifts effort tier and then
  queues. **It never terminates a review mid-task**, because a governance verdict truncated
  halfway is worse than one not attempted — it looks like a result.
- **Metering is `Decimal`, never `float`.** `S5.28` and `AP-S5.28a`, which this repository
  enforces as a blocking rule in other people's CI. Credit arithmetic is money arithmetic.
- **`REQ-008` holds: the semantic tier never changes a build result.** Metered or not, it is
  advisory. A gateway outage degrades a build to the deterministic tier and says so — it never
  fails one.
- **`ADR-008`'s bring-your-own-endpoint path stays first-class and free.** The Gateway is a
  convenience over a capability adopters can always run themselves, which is what keeps its
  pricing honest.
- **`ADR-009`'s bar is not relaxed by hosting.** A hosted backend measured through
  `governova semantic-eval` faces the same 90% precision bar. Charging for a tier does not
  entitle it to be trusted.

### 5. What the Cloud must never do

Stated as prohibitions because each is a thing a subscription business drifts toward:

1. **Never gate a deterministic capability.** No feature flag, no licence check, no phone-home
   in the engine. The engine must remain fully functional with the Cloud unreachable.
2. **Never send code without explicit opt-in.** The Gateway transmits what a review requires and
   states what that is. The Intelligence Network is opt-in, aggregated and anonymised (§15.1),
   and off by default.
3. **Never let an engine ratify.** `S10.8` and `AP-S10.8b` — L4 is human-only. A hosted
   amendment proposer is still a proposer.
4. **Never let the hosted Score and the local Score disagree.** Both read the same compiled
   index by the same code. A hosted number that flatters is the one number nobody should trust.

---

## Consequences

### What becomes easier

- **The commercial model stops contradicting the artefact.** Anyone can verify the free claim by
  installing the package, which is the strongest possible marketing for a trust product.
- **The stack question is closed by the project's own rubric**, with the scoring recorded as
  `S6.6` requires — not re-litigated per service.
- **Python end to end.** One engine, one compiled index, no second implementation of the
  compiler and no cross-language boundary between the gate and the hosted surfaces.
- **Pricing pressure is honest.** BYO endpoint stays free, so the Gateway competes on
  convenience and measured quality rather than on being the only way in.

### What becomes harder

- **The free tier is genuinely generous, so the Cloud must be genuinely good.** There is no
  crippled-tier lever to pull if conversion is weak; the paid surface has to be worth buying on
  its own terms.
- **This is a real SaaS build** — identity, billing, a metered LLM gateway, an operational
  surface with uptime expectations — and it is months, as `ADR-005` warned.
- **Metering is financial code.** It inherits C05's monetary standards, `Decimal` throughout,
  and the reconciliation duty that comes with charging people.
- **`master.md` §19 must be rewritten**, not merely annotated. A superseded section left in a
  vision document is read as current by the next person.

### Constitutional alignment

- `S6.1`–`S6.7` — stack assigned by the matrix, with the scoring documented in an ADR.
- `S3.1`, `S3.5`, `S3.13`, `S3.14` — RS256 issued by the backend; access token in memory.
- `S5.9`, `S5.28` — PostgreSQL via Prisma; monetary values as `Decimal`.
- `S8.1`, `S8.2` — Vercel for the frontend, Railway for the backend.
- `S10.8` / `AP-S10.8b` — L4 approval, including amendments, stays human-only.
- `REQ-008` — an advisory tier never changes a build result.
- `ADR-006` — the engine security posture applies unchanged to code the Gateway executes.

---

## Reversibility

**The paid boundary is the one irreversible part, and deliberately so.** Once the engine is MIT
and published there is no path back to gating it, and this ADR chooses to stop pretending
otherwise rather than preserve an option that does not exist.

Everything else is cheap to revisit. The stack decision is reversible before the first service
ships and expensive after — which is why it is made here, against a rubric, before any code.
Effort-tier-to-model mappings are configuration. Credit economics are pricing and change with a
changelog entry. The Gateway itself is optional by construction: `ADR-008`'s BYO endpoint means
every adopter has a working path if the Cloud is switched off entirely.
