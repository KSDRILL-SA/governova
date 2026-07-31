# ADR-008 — The Semantic Tier Has No Default Endpoint

---

| Attribute   | Value |
|-------------|-------|
| **ID**      | ADR-008 |
| **Date**    | 2026-07-31 |
| **Status**  | accepted |
| **Supersedes** | The bundled-default decision shipped in #137 (partially — the protocol and configuration model stand) |
| **Amends**  | ADR-005 (the "free and offline" characterisation of the Open Engine) |
| **Relates To** | ADR-006, `#142`, `#138`, `S8.87`, `REQ-008` |

---

## Context

**GitHub Models was fully retired on 30 July 2026.** The inference API, model catalog,
playground, and BYOK endpoints are gone. The endpoint returns `HTTP 410` with
`github_models_retirement_brownout`, and it will not come back.

That endpoint was the entire basis of the semantic tier's default configuration, chosen in
#137 for one property nothing else had: it was reachable from a stock GitHub Actions token,
so the tier ran **with no account, no key, and no cost**. `pr-guardian.yml` still points at
it, and has since it was written.

Two facts make this a decision rather than a repair.

**The property that made the default possible no longer exists anywhere.** Every remaining
inference endpoint — Microsoft Foundry, OpenAI, Anthropic, Groq, Together, OpenRouter, or
a Copilot subscription — requires an account and a credential, and most require payment.
There is no longer a category of "free inference reachable from CI with a built-in token".
The default was not merely broken; the thing it was an instance of has been discontinued.

**A default endpoint is a vendor choice made on the adopter's behalf.** Baking in a
specific provider would commit every consumer of this engine to that provider's terms,
availability, pricing, and data handling, in a tool whose entire proposition is that it is
auditable. It would also repeat the failure that produced `#142`: a shipped default whose
liveness this project does not control and cannot monitor, decaying with no change to the
repository — precisely what `S8.87` exists to name.

The alternative that is *not* obvious: an OpenAI-compatible server running locally
(Ollama, llama.cpp, LM Studio, vLLM) speaks the `chat_completions` protocol this engine
already implements. It needs no account, costs nothing, and never leaves the machine.

---

## Decision

**The semantic tier ships with no default endpoint. It is inactive unless configured, and
it says so.**

Three parts.

### 1. The dead default is removed, not replaced

`pr-guardian.yml` no longer supplies a fallback base URL, model, or token. With no
secrets configured, the tier reports `inactive` and the build is unaffected.

Removing rather than substituting is the point. A default that lies is worse than no
default, because it converts an absent capability into a *believed* one — which is exactly
how the tier reached nothing for two releases while every build stayed green.

### 2. A local OpenAI-compatible endpoint is the documented zero-cost route

It requires no account, incurs no cost, sends nothing off the machine, and needs no new
code — it is the protocol the engine already speaks:

```bash
GOVERNOVA_LLM_BASE_URL=http://localhost:11434/v1
GOVERNOVA_LLM_MODEL=<a model served locally>
GOVERNOVA_LLM_API_KEY=<any non-empty string; local servers ignore it>
```

This is **not** made the default. A localhost default would attempt a connection on every
CI run, fail on every one of them, and emit a "did not run" notice on builds where nothing
was ever going to be listening — trading a silent lie for a loud one.

### 3. Hosted providers stay first-class and unopinionated

The existing environment contract is unchanged: any endpoint speaking `chat_completions`
or `messages` works, selected by `GOVERNOVA_LLM_PROTOCOL`. Governova names no vendor,
bundles no hostname, and holds no credential.

---

## Consequences

### What gets worse, stated plainly

**Out-of-the-box semantic coverage is gone**, and with it the claim that the tier reaches
the ~93% of standards regex cannot. A new adopter now gets the reliable tier, the
structural probes, and the requirements analyser — all deterministic, all free — and gets
the semantic tier only if they configure one.

That is a real reduction in what this project offers by default, and it should be recorded
as one rather than softened. It is also the honest position: the capability was
discontinued by its provider, and pretending otherwise would mean shipping a default that
cannot work.

**ADR-005's "free and offline forever" characterisation is narrowed.** The deterministic
engine remains free and offline. The semantic tier is free and offline *only* when pointed
at a local model, and otherwise carries whatever cost its provider charges. The project is
in pilot and this is an accepted change of shape, not a broken promise.

### What gets better

- **No vendor is chosen on an adopter's behalf**, and no hostname this project does not
  control sits in a shipped default.
- **The failure mode that produced `#142` cannot recur from a bundled default**, because
  there is no longer one to decay. Combined with the outcome reporting merged in `#153`,
  a configured endpoint that dies is now visible on the first build after it dies.
- **The local path is a better long-run answer than the one being lost.** It is offline,
  free, private, and unmetered, and it is the on-ramp to `#138` — a Governova-tuned local
  model, which this decision makes the strategic direction rather than an idea.

### Constitutional alignment

Reinforces `S8.87` (the external surface decays on its own — so depend on less of it),
`REQ-008` (an advisory tier never changes a build result), and the standing rule that a
check which cannot determine an answer reports `unknown` rather than assuming. An inactive
tier that says it is inactive is that rule applied to a capability instead of a check.

---

## Reversibility

Deliberately cheap to undo. If a credential-free, CI-reachable endpoint appears again, the
default is three lines of workflow configuration and no engine change — the protocol
layer, the configuration contract, and the outcome reporting are all unchanged by this
decision.

---

## Alternatives rejected

| Option | Rejected because |
|---|---|
| **Substitute another hosted provider as the default** | Every candidate needs an account and a credential, so it would not restore the property being lost — it would only impose a vendor and a bill on adopters, and re-create the decay risk `S8.87` names |
| **Default to `localhost`** | Fails on every CI run where nothing is listening, replacing a silent wrong answer with a loud one |
| **Bundle a small model in the distribution** | A model in a PyPI wheel is a licensing and size problem, and `#138` is the considered form of this idea |
| **Remove the semantic tier entirely** | The tier works; only its free hosting was discontinued. Deleting a working capability because one provider retired is an overcorrection, and the tier is the only route to standards with no deterministic signature |

---

## Open questions deferred

- Whether `#138` (a Governova-tuned local model) becomes a shipped artifact or a
  documented recipe.
- Whether to detect a reachable local endpoint automatically at developer-machine scope,
  where a failed connection is cheap and private — explicitly not in CI.
