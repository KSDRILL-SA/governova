# Governova — Strengthening Roadmap

Forward-looking recommendations to make the platform more powerful, captured during a
full system gap-audit. Ordered by leverage. Each item is independently shippable through
the standard branch → issue → PR → merge workflow.

## Where the platform stands

- **Engine** (Python, `scripts/`): compile · validate · codegen · cli · mcp · checks ·
  enforce · score · report · bible · semantic · dashboard · guardian · notify.
- **Detection**: four tiers — reliable (deterministic, blocking), structural probes
  (repository facts), advisory (medium-confidence, warns), semantic (LLM, advisory,
  env-gated, inactive without a key).
- **Surfaces**: MCP, CLI, IDE extension, CI/CD enforcer, PR Guardian, web dashboard,
  chat notifier shipped (7/8); JetBrains plugin planned.
- **§18 outputs**: Governova Score, Governova Certified eligibility, Board-Level
  Governance Report, System Bible — all generated automatically.
- **Quality gates** (CI): ruff, mypy, drift check, structural integrity, 96 unit tests,
  reference cross-check, constitutional enforcement, PR guardian.
- **Self-score**: 78/100 (C) across **all five factors at full weight**. It read
  100 while three factors were unassessed; instrumenting them lowered it, which is
  the point. Core enforcement coverage 7.4% (33/446) plus 4/38 Layer 4 domain
  anti-patterns; constitutional coverage 7.7% (42/544 evidenced).
- **Detection**: now four tiers — reliable (regex, blocking), **structural probes**
  (repository facts: lockfile, frozen CI install, gitignored `.env`, conventional
  commits — deterministic, and unreachable by any line-scan), advisory, and
  semantic. A probe that cannot determine an answer returns `unknown`, never
  `satisfied`.
- **Runtime**: `governova_audit` (hash-chained trail), `governova_relay` (§4 state
  machine, L4 human-only at the API boundary), `governova_project` (applicability).
- **Layer 4**: 4 ratified domains (`D-FINTECH`, `D-GOVTECH`, `D-EDTECH`, `D-SAAS`),
  19 domain standards, 38 domain anti-patterns — counted separately from the core.

## Recommendations (highest leverage first)

### 1. Activate the semantic tier in a secret-enabled pipeline
The semantic tier is built and integrated (`--semantic` on the enforcer; `--semantic`
on the bible) but no workflow runs it. Add an **advisory semantic job** that activates
only when an `GOVERNOVA_LLM_*` secret is present (a no-op otherwise, so forks stay green).
This turns the architectural/process standards — the 93% the regex tier cannot reach —
into live PR feedback. **Highest leverage: it unlocks the bulk of the constitution.**

### 2. ~~Build the runtime components (relay + audit trail)~~ — **DONE**
`governova_audit` (hash-chained, tamper-evident) and `governova_relay` (the §4 state
machine, L4 refused at the API boundary) shipped, and `governova_project` closed the
constitutional-coverage factor. **All five score factors are now assessed — 100% of
the weight**, up from 45%.

The remaining work here is **raising** the score honestly, not instrumenting it:
constitutional coverage sits at 6.6% because only 36 of 544 applicable standards are
evidenced. Evidencing a standard means citing a file that resolves, so this is real
work — and it is the highest-value backlog the project has, because every standard
evidenced is one an adopting organisation can see demonstrated rather than claimed.

Score-history persistence (for the Board Report trend line) is still open — see §7.

### 3. Expand stack bindings (5/37 → broader)
Only 5 of 37 implementation-stack folders are wired into the compiler registry
(`fastapi`, `spring-boot`, `nextauth`, `nextjs`, `prisma-postgresql`). Wiring the
remaining popular stacks (react, django, express, go-gin, flutter, …) is low-risk,
high-coverage content work that directly widens real-world applicability.

### 4. Grow rule coverage + lean on the semantic tier
The reliable tier is at 7.4% (33 of 446 core anti-patterns, plus 4 of 38 domain).
**Path-scoped rules** raised the ceiling this estimate assumed: a rule can now be
bound to an architectural region, so "no data access outside a repository" and
"no business logic in the presentation layer" are deterministically detectable —
the same line is a violation in a component and correct in a repository. That
unlocked `S1.103`/`S1.104`, which were previously reserved for the semantic tier.

Coverage will still plateau, because most remaining standards are genuinely
process-level. Two Part 19 standards are deliberately left to the semantic tier:
`S1.106` (DRY) and `S1.107` (simplest correct solution) have no deterministic
signature, and a lossy regex for them would trade the gate's trustworthiness for
a coverage number. Keep adding clean, low-false-positive rules where real
signatures exist — including path-scoped ones — and route the rest to #1.

### 5. Distribution
- Publish the **enforcer composite action** to the GitHub Marketplace.
- Publish **`governova-types`** (already generated by codegen) to PyPI for external consumers.
- Publish the **dashboard** to GitHub Pages for a live public governance URL.

### 6. JetBrains plugin (8th surface)
The last surface. It mirrors the VS Code extension (read the compiled index, surface
diagnostics/hover) but requires a JVM/Gradle toolchain to build and verify, so it is
specified rather than shipped here. See `platform/surfaces/jetbrains-plugin/README.md`.

### 7. Deeper assurance
- Run a **security review** of the engine's subprocess (git), HTTP (semantic/notify),
  and file-I/O surfaces.
- Tighten **mypy** incrementally toward strict mode.
- Add **score-history** persistence (artifact- or tag-based to avoid bot commits) to
  power the Board Report trend.

---

*Maintained as a living plan. Every item is constitutional-workflow-shippable.*
