# Governova — Product Documentation

---

| Attribute | Value |
|-----------|-------|
| **Document** | Product, Traceability & Go-To-Market Specification |
| **Organisation** | KSDRILL SA |
| **Product** | Governova — AI Development Governance Platform |
| **Version** | v2.0 |
| **Status** | LIVING — reviewed quarterly |
| **Date** | 2026-05-22 |
| **Supersedes** | v1.0 (sharpened with strategy insights: wedge sequencing, honest detection tiers, configurable relay, concrete traceability) |
| **Author** | Maluleke Kurhula Success, Founder |
| **Companion to** | `GOVERNOVA-MASTER.md` (architecture) · `GOVERNOVA-STRATEGY.md` (thesis + risks) · `CLAUDE-CODE-INSTRUCTIONS.md` (build) |

---

> *"AI can build anything. It is us who must tell it exactly what to build, how to build it,
> what not to build — and prove, afterward, exactly what it did, why, where, and who let it."*

---

## How to read this document

This describes the complete product: what it is, what every part does, how it solves the AI
governance problem, and how it expands from one tool into a platform used everywhere. It is
deliberately honest about what is buildable today versus what is the destination — because a
product document that confuses ambition with reality is the kind that gets a team building
the wrong thing. Where something is aspirational, it says so. The full risk analysis lives in
`GOVERNOVA-STRATEGY.md`; this document stays focused on the product itself.

---

## Table of Contents

| # | Section |
|---|---------|
| 1 | The Problem This Product Exists To Solve |
| 2 | What Governova Is, In Practice |
| 3 | The Traceability Model — Who, What, Where, How |
| 4 | What Is Actually Buildable — The Honest Capability Tiers |
| 5 | The Wedge — The One Product That Starts Everything |
| 6 | The Full Product Portfolio — Nine Surfaces |
| 7 | How The Surfaces Reinforce Each Other |
| 8 | The Governed Build — A Complete Walkthrough |
| 9 | Who Buys It, And The Exact Job It Does For Them |
| 10 | The Business Model |
| 11 | Going Wide — The Four-Axis Expansion |
| 12 | What Makes It Better, Not Just Different |
| 13 | The Product Roadmap, Sequenced By Evidence |
| 14 | The Lock |

---

## §1 — The Problem This Product Exists To Solve

### 1.1 The break

For the entire history of software, the person who wrote a piece of code could also explain
it, review it, and be accountable for it — because they made it, at human speed, slowly
enough to understand it. AI broke that. Code is now produced faster than any human can read,
which means the author and the accountable party are no longer the same entity. AI writes.
A human approves an outcome they did not produce and frequently cannot fully explain.

### 1.2 The precise failure — goal-state divergence

When a developer tells an AI *"build a login that errors on a wrong password and looks
clean,"* the AI optimises for *a* working solution — code that compiles, tests that pass, a
UI that looks fine. It does not optimise for the organisation's unstated requirements: the
token-storage policy, the rate-limiting standard, the audit-logging obligation, the past
incidents that shaped current practice. Nobody told the AI those things, so it could not have
honoured them.

The AI reached a valid goal state. Not *your* goal state. Every AI-era security gap and
unexplainable system lives in the gap between those two. **The entire product is built to
collapse that gap** — to make the specification so precise that the AI's goal state and the
organisation's desired state become the same thing.

### 1.3 The four costs organisations pay right now

| Cost | What it looks like in practice |
|------|--------------------------------|
| Unexplainable systems | Code shipped yesterday nobody can explain next quarter |
| Unprovable governance | "We use AI responsibly" with zero evidence a CISO can audit |
| Blocked velocity | AI banned in the exact systems where it would help most, because it can't be governed |
| Untraceable failure | A production incident with no record of what decided the thing that broke, or who allowed it |

Governova is designed to eliminate all four from a single governance engine.

---

## §2 — What Governova Is, In Practice

Governova sits *between* the AI tool and the codebase, for the entire life of a build. It
does three things continuously:

**Before code is written** — it hands the AI a precise specification: which standards apply,
what is permitted, what is forbidden, and at what permission level the AI may act. The AI is
*commanded*, not merely *prompted*.

**While code is written** — it watches every action against that specification, flags
violations as they happen, and enforces that certain categories of decision can never be
made without a human checkpoint.

**After code is written** — it produces a complete, structured, human-readable record of
what was built, why, how it works, what breaks it, and how to fix it — for every file,
automatically, as a byproduct of the build itself.

The outcome for an organisation: AI runs at full speed, every action is governed, every
decision is attributable, and every system comes with its own explanation built in. The
organisation never has to choose between AI velocity and governance — Governova is what makes
having both at once possible.

---

## §3 — The Traceability Model: Who, What, Where, How

This is the heart of what the product promises: every organisation must be able to
reconstruct, for any piece of their system, exactly what happened, where, by whom, and how to
fix it.

### 3.1 The questions every audit entry permanently answers

For every action taken by any AI tool anywhere in a governed system, the audit trail records,
immutably:

| Question | Recorded |
|----------|----------|
| **Who** | Which engineer (AI tool or named human) acted, at what permission level (L1–L4) |
| **What** | The exact action — file created, standard applied, decision made, code written |
| **Where** | The exact file, function, and line range affected |
| **How** | Which standard authorised the decision, and the reasoning |
| **When** | Timestamp, session ID, position in the build sequence |
| **Approved by** | Which human approved the L4 checkpoint this action depended on |

This record is append-only — never edited, never deleted — and is generated as a *byproduct
of normal work*, not a separate compliance chore. No engineer has to remember to document
anything; every action already passes through the governance engine, so the engine records it.

### 3.2 What this is — and what it is not

This is a **decision record**, not an event log. Application logs tell you what happened at
runtime. Observability tools tell you what the system is doing now. Neither captures *why a
decision was made when the code was written, or under whose authority.* That decision-and-
authority layer is the thing that does not exist in any tool on the market today, and it is
precisely the thing a CISO needs to sign off on AI use in a serious system.

### 3.3 Locating and fixing a problem — the actual experience

When something breaks in a governed system:

1. The failing component is identified (by an engineer or an alert).
2. The engineer opens that file. The System Bible overlay shows instantly: why this file
   exists, how it works, the documented ways it is known to fail, and the fix guide for each.
3. If the failure isn't a known pattern, they query the audit trail for that file: who built
   it, what AI engineer, under what standard, what the handoff report said at the time.
4. They can trace it back to the original design rationale — the Why Layer — written at the
   moment the architecture was decided, however long ago.

Nobody reverse-engineers a black box. The explanation was generated at build time and has
been waiting there ever since. **That is the product's core promise made concrete.**

---

## §4 — What Is Actually Buildable: The Honest Capability Tiers

A product that promises magic detection and then ships noise destroys trust. So here, plainly,
is what Governova can actually detect — and how each tier is handled — because being honest
about this is what makes the product *trustworthy*, which is the entire point of a governance
tool.

| Tier | Example | How it works | Status | Enforcement |
|------|---------|--------------|--------|-------------|
| Pattern | Token in `localStorage` | Static analysis / AST | Reliable today | **Hard block** allowed |
| Structural | Endpoint missing input validation | AST + framework-aware rules | Reliable with per-stack work | **Hard block** allowed |
| Semantic | "Violates our session-handling principle" | LLM evaluation against the standard | Probabilistic | **Advisory only** — never blocks |
| Intent | "Contradicts the system's architectural direction" | LLM + full system context | Aspirational | **Advisory only** — flagged for human |

### 4.1 The governing rule

**Deterministic detections may block. Probabilistic detections may only advise.** A semantic
check that flags "review this" is helpful; a semantic check that *blocks correct code* because
the model was unsure is the fastest way to get the whole tool disabled. This discipline —
never letting an uncertain check stop a developer — keeps trust intact and is non-negotiable
in the product design.

### 4.2 Why this is still powerful with only the reliable tiers

A large fraction of genuinely damaging anti-patterns *are* pattern-matchable or structural —
the token in the wrong place, the missing validation, the unparameterised query, the secret
in the code. The reliable tiers alone deliver real, defensible value on day one. The semantic
and intent tiers are upside that improves over time as detection is proven — not the
foundation the product stands on.

---

## §5 — The Wedge: The One Product That Starts Everything

The full platform is nine surfaces across many domains and org sizes. But a platform is the
*destination*, never the *start*. Every platform that won began as one sharp tool for one
user with one painful problem.

### 5.1 The single wedge

**One user:** a developer building with AI in VS Code or Cursor, who has felt the specific
discomfort of AI generating code they don't fully trust or understand.

**One product:** the IDE extension, free.

**One job done so well they'd hate to lose it:** it makes AI-generated code *legible and
trustworthy in the moment of writing it* — the reliable-tier violations flagged inline before
commit, and the "why/how/what-breaks-it" attached to every piece on hover. Not a linter. A
trust layer that travels with the code.

### 5.2 Why this wedge and not another surface

It has the shortest path to value (install, feel it in one session), the lowest adoption
friction (free, no team approval needed), and — critically — it *generates the audit-trail
data that every other surface and the entire enterprise pitch depend on.* The wedge is not
merely the easiest entry. It is the surface that produces the asset the rest of the company is
built on.

### 5.3 The expansion is pulled, not pushed

```
Individual trusts the tool        →  IDE extension (free)
  Team wants it enforced          →  CI/CD enforcer + PR bot (paid)
    Manager wants visibility      →  dashboard + score (paid)
      Org needs to prove it       →  audit trail + board report (enterprise)
        Industry needs a standard →  certification (category ownership)
```

Each step is pulled by the previous step's success. You never sell the dashboard to a company
whose developers don't already love the extension. This sequencing is the difference between a
product that compounds and one that sprawls.

---

## §6 — The Full Product Portfolio: Nine Surfaces

This is the answer to "wide, not single-focus." Governova is **one governance engine exposed
through nine products**, each solving the governance problem at a different point in the
lifecycle, for a different persona. A single-surface product is copied in months; nine
surfaces drawing from one engine and one audit trail is something a competitor needs years to
replicate — because each surface deepens the value of every other.

| # | Surface | Lifecycle stage | Persona | Buildable when |
|---|---------|-----------------|---------|----------------|
| 1 | IDE Extension (VS Code/Cursor) | Writing | Individual developer | **Now — the wedge** |
| 2 | CLI Tool | Automating | Developer / DevOps | Now — alongside the wedge |
| 3 | CI/CD Enforcer | Merging | Team / DevOps | After wedge validated |
| 4 | PR Guardian Bot | Reviewing | Tech lead | After wedge validated |
| 5 | Web Dashboard | Managing | Manager / CTO | After team adoption |
| 6 | Slack / Teams Bot | Staying informed | Whole team | After dashboard |
| 7 | MCP Server | AI orchestration | The AI tools themselves | After core engine is solid |
| 8 | JetBrains Plugin | Writing | Enterprise backend dev | Enterprise phase |
| 9 | REST + GraphQL API | Integrating | Platform teams | Enterprise phase |

Each is specified below — problem, persona, what it does, and what it contributes to the whole.

### 6.1 IDE Extension (VS Code + Cursor) — the wedge
**Problem:** Developers writing with AI have no inline visibility into which standards apply,
no warning before they commit a violation, no record of why AI-generated code looks as it
does. **What it does:** Surfaces active standards in the sidebar; flags reliable-tier
violations inline before save; shows relay position in the status bar; generates
`.cursorrules` from the active CONSTITUTION-INDEX so Cursor's own AI inherits the governance;
shows the System Bible Why/How/Failure/Fix on hover for any function. **Contribution:** This
is where the audit data originates. Every other surface is downstream of it.

### 6.2 CLI Tool
**Problem:** Not every workflow lives in an IDE; scripts and pipelines need governance without
a GUI. **What it does:** `init`, `validate`, `validate --pre-commit`, `generate cursorrules`,
`generate bible`, `report`, `score`, `relay status`, `relay abort`, `amend`.
**Contribution:** The glue surface — makes Governova embeddable in any workflow a team already
has.

### 6.3 CI/CD Enforcer
**Problem:** A developer can ignore an IDE warning. They cannot ignore a blocked merge.
Optional governance is not governance. **What it does:** Runs validation as a required check
on every PR; reliable-tier SEV0/SEV1 violations block the merge; SEV2 needs a fix or a
documented exception; new files are checked for System Bible completeness. **Contribution:**
The moment governance stops being a suggestion and becomes infrastructure — and the team's
*chosen* enforcement point, which is why blocking here is acceptable when blocking an
individual never is.

### 6.4 PR Guardian Bot
**Problem:** Human review rarely catches "this violates our standard in a way only obvious if
you know the standard exists." **What it does:** Reads every PR, cross-references the diff
against the active CONSTITUTION-INDEX, leaves inline comments citing the exact standard,
anti-pattern, severity, and correct pattern. Semantic findings are framed as advisory.
**Contribution:** Makes Governova feel like "a senior engineer reviewing everything" — the
single strongest word-of-mouth driver inside a team.

### 6.5 Web Dashboard
**Problem:** No individual tool gives a manager or CISO a single view of governance health
across all projects. **What it does:** Governova Score per project and trend; violation
heatmaps; relay status; the full filterable audit trail; System Bible completeness; team
analytics. **Contribution:** The surface shown in a leadership meeting — converts "developers
like this" into "the org has decided this is mandatory."

### 6.6 Slack / Teams Bot
**Problem:** Governance events in a dashboard nobody watches don't get acted on. Teams live in
chat. **What it does:** SEV0/SEV1 alerts tagged to the responsible party; relay handoff
approval notifications; daily governance digest; temporal alerts when a framework change may
have invalidated a standard. **Contribution:** Keeps governance alive and present, and is the
surface most likely to get a non-engineering stakeholder to notice the product.

### 6.7 MCP Server
**Problem:** Every other surface is for humans. Static `.md` files require an AI tool to
remember to read them and trust they're current. **What it does:** Exposes the constitutional
database as live, queryable MCP tools — `get_standard`, `get_active_constitution`,
`check_violation`, `get_anti_pattern`, `get_relay_state`, `log_ai_action`, `get_runbook`,
`flag_temporal_review`. Central amendments reflect on the next call, no stale local copies.
**Contribution:** The most technically significant and most defensible surface — it makes the
constitutional database a living system, and it is the hardest part to copy.

### 6.8 JetBrains Plugin
**Problem:** VS Code does not reach the enterprise Java/Kotlin/backend market where IntelliJ
and WebStorm dominate — exactly the buyers most anxious about ungoverned AI. **What it does:**
Full feature parity via the JetBrains Platform SDK. **Contribution:** Unlocks the
highest-value enterprise segment unreachable through VS Code alone.

### 6.9 REST + GraphQL API
**Problem:** Larger organisations want governance data inside their existing internal tools,
not in a separate destination. **What it does:** Full access to index management, violation
records, audit trail, relay state, Score, System Bible, amendments — JWT-authenticated,
rate-limited per tier. **Contribution:** Makes Governova infrastructure that disappears into a
customer's stack rather than a destination they must visit.

---

## §7 — How The Surfaces Reinforce Each Other

No surface is an island. One build event flows through all of them:

A developer writes code in the **IDE Extension**. The AI tool queries the **MCP Server** for
active standards before generating. As code is written, the violation detector flags a
reliable-tier issue inline, immediately. The developer fixes it. They open a PR; the **CI/CD
Enforcer** blocks it because a SEV1 slipped through; the **PR Guardian Bot** explains exactly
why, citing the standard. Fixed, the PR passes and merges. The entire sequence — every standard
checked, every violation caught, every approval given — lands in the **audit trail**. That data
feeds the **Web Dashboard**, updates the **Governova Score**, and fires a **Slack/Teams**
notification if it was a SEV0/SEV1 event. At month's end the board report summarises it in
plain English. The customer's internal tool pulls the same data via the **API**.

One event. Nine touchpoints. One continuous, provable record. That is "wide" in practice — not
nine unrelated products, but one governance fact surfaced everywhere it is needed.

---

## §8 — The Governed Build: A Complete Walkthrough

To make it concrete, here is a real auth feature built under Governova, end to end:

**Design (Claude, L1→L2).** Claude reads the active CONSTITUTION-INDEX. It proposes the auth
architecture and, for each decision, writes the Why Layer: *"Access token in memory, refresh in
HttpOnly cookie — per S3.14, because localStorage exposes tokens to XSS (AP-S3.14a)."* The
Founder approves the design (L4).

**Build (Claude Code, L2→L3).** Claude Code implements only the approved design. As it writes,
the violation detector confirms each file against reliable-tier standards. It generates the How
Layer for every function. A MINOR question arises (nullable field?) — it decides, documents it
in the commit, flags it at handoff. An ARCHITECTURAL question would have paused the relay
instead.

**Review (PR Guardian Bot + CI/CD).** The PR opens. The bot reviews against the index. CI/CD
runs validation. Everything passes because governance happened during the build, not after.

**Record (audit trail + System Bible).** The complete record seals: who built each file, under
what standard, what was approved by whom, the Failure Map and Fix Guide for every file. Six
months later, when someone needs to change this auth flow, the entire reasoning is waiting for
them.

That is the product working as designed — not catching problems at the end, but governing the
decisions that prevent them, and leaving a provable trail.

---

## §9 — Who Buys It, And The Exact Job It Does

| Buyer | Their problem | The job Governova does | Entry surface |
|-------|----------------|------------------------|----------------|
| Solo developer | Building fast with AI, doesn't know what they don't know | Teaches governance through use, free | IDE Extension |
| Team lead | Reviewing AI PRs they can't fully trust | Standards-aware automatic review | PR Bot + CI/CD |
| CTO | No visibility into whether AI use is safe org-wide | One score, full drill-down | Dashboard |
| CISO / Compliance | Can't approve AI in regulated systems without proof | The audit artifact they need | Audit trail + reports |
| Board / Investors | Need AI-risk assurance before scaling/funding | External, verifiable signal | Score + Certification |
| Dev agency | Wants to monetise governance for clients | White-label resale at a margin | All surfaces, rebranded |
| Regulator (future) | Needs an auditable reference standard | The standard they point to | Certification |

---

## §10 — The Business Model

### 10.1 Tiers

| Tier | Price | Target |
|------|-------|--------|
| Free | $0 | Individual developers — the wedge and data source |
| Pro | $9/mo · $89/yr | Serious individual developers |
| Pro+ | $19/mo · $189/yr | Small teams |
| Max | $39/mo · $389/yr | Larger teams, agencies, white-label |
| Enterprise | Custom | Mapping Engine, SLA, dedicated onboarding |
| Certification | Annual | Independent of subscription — the long game |

### 10.2 The honest revenue picture

Individual-tier conversion runs 2–5%, not 10% — plan for 3%. The individual tiers are a
*customer-acquisition and data-generation engine that happens to make some money.* **The
business is built on enterprise contracts and certification** — one enterprise contract can
equal thousands of Pro subscriptions. The wedge exists to *reach* enterprises and *generate the
audit data*, not to monetise individuals. Stating this plainly is what keeps the model
credible.

### 10.3 The cost reality

The expensive part is not hosting — it is LLM inference if semantic detection and PR review use
model calls. That cost scales with usage and must be priced in, or margins invert at scale.
Mitigation: reliable-tier deterministic checks run cheaply on every keystroke; expensive
model-based checks run only at commit/PR boundaries, only on changed code, cached aggressively,
and priced into the tiers that use them. This number is modelled before pricing locks.

### 10.4 Beyond subscriptions
- **Certification** — annual fee, the reason to stay governed indefinitely.
- **Enterprise contracts** — Mapping Engine, onboarding, bespoke domain constitutions, SLA.
- **White-label** — agencies pay Max rate, resell at margin, become an unpaid sales force.
- **Domain contribution revenue share** — community-contributed domains earn their authors a
  share of revenue generated through their use.

---

## §11 — Going Wide: The Four-Axis Expansion

Breadth comes from extending in four independent directions that compound each other.

**Across surfaces (horizontal).** Nine surfaces, one engine, every lifecycle touchpoint covered
— first keystroke to board report (§6).

**Across stacks (technical depth).** The implementation layer extends indefinitely. KSDRILL
ships Next.js, Angular, FastAPI, Prisma/PostgreSQL, Beanie/MongoDB, ChromaDB as the proven
reference set. Spring Boot, Django, Rails, Go, Rust, and any future stack are added as new
bindings *without touching the universal core* — so the addressable market is not limited to
KSDRILL's own technology choices.

**Across domains (industry depth).** The domain layer plans fintech, govtech, edtech, SaaS,
healthtech, e-commerce, IoT, AI/ML. Each domain is a wedge into a different vertical with its
own buyers, compliance needs, and willingness to pay for governance proof. A hospital, a bank,
and a logistics platform all become addressable from the same core.

**Across organisation size (go-to-market depth).** A solo developer on Free, a startup on
Pro+, a 200-person org on Max with enterprise mode, and a regulated bank requiring a full
Mapping Engine implementation are all served by the same product at different depths. Nobody
outgrows Governova — they grow into deeper tiers of it.

**The combined effect.** Surfaces × stacks × domains × org sizes — the addressable space is not
"developers who use Cursor." It is every organisation, of any size, in any industry, on any
technology, using AI to build anything that matters enough to need proof of how it was built.
That is the real scope of "wide."

### 11.1 One correction the strategy work forced
The relay model (the five named AI tools — Claude, Claude Code, ChatGPT, DeepSeek, Kimi) is the
*KSDRILL reference configuration*, not universal doctrine. The durable principle is the
permission levels, the human-approval boundary, and the structured handoff. The *specific tool
assignment* is configuration: any organisation defines its own relay, its own tools, its own
permission mapping. This keeps the product from dating the moment the tool landscape shifts —
which it will.

---

## §12 — What Makes It Better, Not Just Different

Four structural choices that put Governova ahead of anything a competitor builds by default:

**Govern the process, not the output.** Every existing tool inspects code after it exists — an
autopsy. Governova governs the decision that produces the code, before and during creation — a
living checkup. Preventing the wrong decision costs nothing; fixing the wrong artifact costs
everything.

**Documentation as a byproduct, not a task.** Everyone else treats docs as work someone has to
do and therefore doesn't. Governova generates the explanation as a side-effect of governing the
build — it gets explainability for free because of *where in the lifecycle it sits.*

**Translate to the customer's language, don't impose yours.** "Adopt our rules" gets blocked by
procurement. The Mapping Engine ingests *their* standards and hands back *their* policies made
stronger. One asks an enterprise to change; the other gives them a gift.

**The network compounds; competitors start at zero.** Every governed project makes the database
smarter for the next. A competitor launching later starts at zero regardless of funding. This
is the only part of the moat that strengthens daily and cannot be bought.

---

## §13 — The Product Roadmap, Sequenced By Evidence

Sequencing matters more than ambition. The order:

**Now — Prove the wedge.** Finish one reference system end to end under governance. Build the
thinnest IDE extension (reliable-tier detection + System Bible hover only). Put it in ten real
developers' hands and watch whether they keep it on. This single experiment decides everything.

**Then — Team surfaces (if the wedge holds).** CI/CD Enforcer, PR Guardian Bot, CLI. Pulled by
teams whose developers already love the extension.

**Then — Visibility.** Web Dashboard, Governova Score, Slack/Teams bot. Pulled by managers who
see team adoption.

**Then — The living engine.** MCP Server. Makes the database dynamic for AI tools at runtime.

**Then — Enterprise.** JetBrains Plugin, REST/GraphQL API, Mapping Engine, board reports,
enterprise mode. Pulled by organisations needing proof.

**Then — The standard.** Certification programme, Intelligence Network at scale. The category
ownership play.

Each phase is *pulled* by validated demand from the previous one. Nothing past "prove the
wedge" is built until the wedge returns a signal. The discipline to *not* build all nine
surfaces at once is what determines whether this works.

---

## §14 — The Lock

**The problem.** AI broke the assumption that the author of code can account for it.
Enterprises correctly refuse to trust AI they cannot govern.

**The product.** Governova commands AI with precise standards, enforces an unbypassable
human-approval boundary, records every decision immutably, and explains every file — as a
byproduct of building, not a separate task.

**The proof.** For any system, any time, an organisation can answer who did what, where, how,
and under whose authority — the traceability this generation of AI development has lacked.

**The honesty.** The reliable detection tiers ship first and are enough; semantic detection
advises, never blocks, until proven. The business runs on enterprise and certification, not
individual subscriptions. The relay is configurable, not fixed. Nothing past the wedge is built
until the wedge is proven.

**The breadth.** Nine surfaces, unlimited stacks, unlimited domains, every org size — one
engine beneath all of it, compounding with every project it governs.

**The destination.** Not a tool a few developers use. The standard every serious organisation
building with AI is expected to hold — the way SOC2 and ISO 27001 are expected today.

**The one sentence.** *Win one developer's trust with one tool that makes AI-built code
provable — then let every organisation on earth pull you into the rest.*

---

*This is a living product document, paired with `GOVERNOVA-MASTER.md` (architecture),
`GOVERNOVA-STRATEGY.md` (thesis and risks), and `CLAUDE-CODE-INSTRUCTIONS.md` (build). Product
decisions must reconcile with what is written here.*

*v2.0 — 2026-05-22 — Maluleke Kurhula Success, Founder, KSDRILL SA*
