# Phase 4 — Governova Cloud

| Attribute | Value |
|-----------|-------|
| **Decision** | `governance/decisions/ADR-010-governova-cloud.md` · `ADR-005` workstream D |
| **Status** | Planned — Stage 0 ready to implement |
| **Sequenced** | After Phase 3 (closed as scoped by `ADR-009`). The last workstream. |
| **Stack** | Angular + FastAPI — scored 10–0 against the assignment matrix in `ADR-010` §2 |

> Read `ADR-010` first. It carries the decisions; this document carries the work.
> Every stage below is independently shippable through branch → issue → PR → merge.

---

## What this phase is

Everything shipped so far runs on a laptop. **Phase 4 is the first Governova that needs a server
we operate**, and it is the only part anyone pays for.

`ADR-010` fixes the boundary: the deterministic engine stays MIT, complete and offline forever,
and the Cloud sells what a local tool cannot do — metered AI, cross-project learning, hosted
history, organisations, certification. **The free engine is not a lead magnet; it is the proof
the paid product is honest.**

---

## The bar this phase is held to

Phase 3's bar was trust on first contact. Phase 4's is **trust with someone's code and someone's
money**, which is a different and higher thing.

| Metric | Required |
|---|---|
| Engine without the Cloud | **Fully functional, always.** No feature flag, no licence check, no phone-home |
| Code leaving the machine | **Never without explicit opt-in**, and the request states what it sends |
| Credit arithmetic | **`Decimal` throughout.** A float in money code is `AP-S5.28a`, which we block in other people's CI |
| Mid-task behaviour at the cap | **Degrade or queue. Never terminate.** A truncated verdict looks like a result |
| Hosted Score vs local Score | **Identical, by construction** — same compiled index, same code path |
| Semantic quality | `ADR-009`'s bar, unchanged. Hosting does not earn trust |
| Auth secrets at rest | OS keychain for the CLI; HttpOnly cookie for refresh; **memory only** for access (`S3.14`) |

**The first invoice is the only first impression the paid product gets**, and a metering bug is
not a rounding error — it is a charge someone did not agree to.

---

## What already exists

Most of the intelligence exists; what is missing is the plane it runs on.

| Capability | Where |
|---|---|
| The semantic tier, provider-agnostic | `governova_semantic` |
| Trust measurement for any backend | `governova semantic-eval` (`ADR-009` re-entry criteria) |
| Score, coverage, board report, Bible | `governova_score`, `governova_report`, `governova_bible` |
| Applicability from `governance/project.toml` | `governova_project` |
| Tamper-evident audit chain | `governova_audit` |
| The relay state machine | `governova_relay` |
| Compiled constitution as one typed artefact | `compiled/constitution.json` |

**What does not exist: identity, persistence, billing, and a metered path to a model.** That is
Stages 0–3.

---

## Stage 0 — Identity · **start here**

**Ships:** `governova login`, and a service that can say who someone is.

Nothing else in this phase can start without it, and it is the stage where a mistake is most
expensive to undo.

### 0.1 · The device grant

OAuth 2.0 Device Authorization Grant (RFC 8628): `governova login` prints a short code and a
URL, the browser approves, the CLI polls, and the token lands in the **OS keychain** — Keychain,
Credential Manager, or Secret Service. Never a dotfile, never an environment variable in a
shell history.

`governova logout` and `governova whoami` ship in the same stage. A login you cannot inspect or
revoke from the same tool is not finished.

### 0.2 · The token model

FastAPI is the only issuer. **RS256, not HS256** (`S3.5`) — the public key is published so
surfaces verify without holding a signing secret. Refresh token in an HttpOnly cookie for the
dashboard; access token in Angular memory (`S3.14`, enforced by `AP-S3.14a`, which this
repository already ships as a blocking rule).

**API keys are the CI fallback only** — organisation-scoped, revocable, listed in the dashboard
with a last-used timestamp so an unused key is visible rather than forgotten.

### 0.3 · What Stage 0 must prove before Stage 1 starts

- A CLI with no network reaches every deterministic command unchanged. **Test it with the
  service down**, not with it up and unused.
- A revoked token stops working within one refresh window, and the CLI says so in words rather
  than a stack trace.
- No token is ever written to disk in plaintext by any path, including error handling.

---

## Stage 1 — Persistence and organisations

**Ships:** PostgreSQL via Prisma (`S5.9`), organisations, teams, seats, roles.

The data model is the thing that is expensive to change later, so it is designed against C05 and
C14 before it is written — `governova schema` already analyses Prisma and SQL DDL, and **this
phase is its first real customer.** Run it on our own schema.

Roles map to `S16`'s operating modes rather than inventing a parallel vocabulary: Personal, Team,
Enterprise. **Seats are the unit that is billed**; projects are not counted, because counting
projects is the crippled-tier thinking `ADR-010` retired.

Soft deletes and `deleted_at IS NULL` (`S5.22`), `NOT NULL` on required fields (`S5.29`), unique
constraints at the database rather than in application code (`S5.30`). We ship rules for all of
these.

---

## Stage 2 — Subscriptions and the credit ledger

**Ships:** billing, tiers, and the ledger the Gateway meters against.

`ADR-010` §4 fixes the model: **credits accrue hourly** against a tier budget rather than
resetting monthly, so bursty work is not punished.

**This is financial code and inherits C05 entirely.** `Decimal` for every monetary and credit
value — never `float`, which is `AP-S5.28a` and blocks builds. Idempotency keys on every write
(`S2.34`), because a retried webhook that double-charges is the defect this phase most deserves
to be judged on. Every balance change is an append-only ledger entry; a balance is a projection,
never a mutable column.

`governova audit` already implements a tamper-evident chain. **Use it, do not build a second
one.**

---

## Stage 3 — The Intelligence Gateway

**Ships:** the metered path to the semantic tier — the first paid capability that touches user
code.

Effort tiers Low / Medium / High / Max, being *model size × reasoning depth × review passes*.
Degrade and queue at the cap; **never terminate mid-task.**

**`ADR-009`'s bar applies unchanged.** A hosted backend is measured through
`governova semantic-eval` at five runs per condition, and 53% precision does not become
acceptable because it is now billable. If the hosted tier cannot clear the bar, it ships as
advisory-only and says so — `REQ-008` means it never changes a build result regardless.

`ADR-008`'s bring-your-own endpoint stays free and first-class. The Gateway competes on
convenience, not on being the only door.

---

## Stage 4 — Hosted surfaces

**Ships:** the Angular dashboard — score history and trend, violation heatmap, relay monitor,
audit trail, coverage, board report download.

Everything here is a *view* of data the engine already produces. **The hosted Score and the
local Score are the same number by construction**, read from the same compiled index by the same
code. If they can ever differ, that is a defect, not a feature — and it is worth a test that
asserts it.

---

## Stage 5 — Intelligence Network · **consent-gated**

**Ships:** §15.1 — anonymised, aggregated cross-project learning.

**Off by default and opt-in, always.** What is collected, what is retained, and for how long is
stated before the first upload, not in a settings page nobody opens. This is the stage that most
resembles the Always-On Learning work `ADR-009` deferred, and it inherits that deferral's
reasoning: an engine that proposes is correct, one that ratifies is a constitutional violation
by construction (`S10.8`, `AP-S10.8b`).

---

## Sequencing, and what blocks what

    0  Identity            nothing starts without it
    1  Persistence         needs 0
    2  Subscriptions       needs 1
    3  Gateway             needs 2 for metering, and ADR-009's bar for trust
    4  Dashboard           needs 1; better with 2 and 3
    5  Network             needs 4, and a written privacy posture

Stages 0–2 are ordinary product engineering with no unresolved research. **Stage 3 is the only
one carrying a live risk**, and it is `ADR-009`'s: the semantic tier is not yet good enough to be
trusted, and hosting it does not change that. If the bar is still unmet when Stage 3 arrives, it
ships advisory-only rather than waiting — the metering, the queueing and the degradation are
useful and measurable independent of how good the model is.

---

## Traps carried forward

- **A second implementation of anything the engine already does is the defect.** `validate`
  existed twice and the copies drifted silently; a hosted Score computed by hosted code would be
  the same failure with money attached.
- **A capability that runs on a laptop is free.** If a Cloud feature would work offline, it does
  not belong behind the boundary — see `ADR-010` §1.
- **A short liveness probe is not a health check.** The semantic endpoint returned `200` in 2–5s
  while failing 5 of 17 real requests. The Gateway needs real-work health, not `say ready`.
- **`float` in credit arithmetic is a blocking violation of our own constitution**, and the
  first place anyone will look if they think they were overcharged.
