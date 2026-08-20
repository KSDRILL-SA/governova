# Governova

> *"AI can build anything. It is us who must tell it exactly what to build,
> how to build it, what not to build, and who approves every decision."*

[![Governova Score](https://img.shields.io/badge/Governova_Score-78%2F100_(C)-yellow)](docs/vision/master.md)
[![Status](https://img.shields.io/badge/Status-LOCKED-red)](docs/vision/master.md)
[![Version](https://img.shields.io/badge/Version-v2.0-blue)](docs/vision/master.md)
[![Constitutions](https://img.shields.io/badge/Constitutions-15-purple)](constitution/core/)
[![Standards](https://img.shields.io/badge/Standards-670-green)](constitution/indexes/standards-index.md)
[![Phases](https://img.shields.io/badge/Phases-4-teal)](framework/phase-model.md)
[![Locked](https://img.shields.io/badge/Locked-2026--05--22-orange)](docs/vision/master.md)

> **On that score.** Governova scores itself with the same engine it ships, over
> all five factors at full weight — and currently scores **78 (C)**, below its own
> Certified bar of 85. It was 100 while three of the five factors were unassessed;
> instrumenting them lowered it. The gap is constitutional coverage: 61 of 596
> applicable standards are *evidenced*, and undemonstrated compliance is
> deliberately uncounted. A governance product that grades itself generously is
> the one number nobody should trust.

---

> **Continuing work on Governova itself?** Read [`START-HERE.md`](START-HERE.md) first —
> current state, the remaining work order, the standing rules, and the traps that cost
> the last engineer an hour each.

---

**Governova** is the world's first AI development governance platform —
the constitutional layer between AI capability and enterprise trust.

[**→ Vision**](docs/vision/master.md) ·
[Product](docs/vision/product.md) ·
[Strategy](docs/vision/strategy.md) ·
[Quickstart](docs/guides/quickstart.md) ·
[Docs index](docs/README.md)

---

## What it is

Governova tells AI tools exactly what to build, how to build it, what not to build,
and who approves every decision — for any system, any domain, any stack, any scale.
It records every AI action in an immutable audit trail and generates complete
documentation for every file ever built.

## Four-layer architecture

| Layer | Folder | Description |
|-------|--------|-------------|
| 1 — Framework | `framework/` | Universal primitives: format, phases, severity, permissions, hierarchy, amendments |
| 2 — Core | `constitution/core/` | 15 constitutions across 4 phases — universal standards as principles |
| 3 — Implementation | `constitution/implementation/` | Stack-specific bindings of core standards |
| 4 — Domains | `constitution/domains/` | Industry-specific extensions |

**670 live standards** and 498 anti-patterns across 15 constitutions (the 594 locked baseline,
plus ratified C0 §8 amendments and the four constitutions ratified since — C11 Requirements
Engineering, C12 System Modelling, C13 Software Evolution, C14 Data Design).

> Every count on this page is `compiled/constitution.json`, which the engine regenerates and
> `governova compile --check` gates on. Regenerate before editing: `governova stats`,
> `governova validate`, `governova govscore`.

## Quick start

```bash
# Clone alongside your project
git clone https://github.com/KSDRILL-SA/governova.git

# First — read the master document
cat docs/vision/master.md

# Start a new governed project
cat docs/guides/quickstart.md

# Validate constitutional integrity at any time
python scripts/validate-integrity.py
```

New here? Start with the [documentation index](docs/README.md).

## Repository structure

```
governova/
├── README.md                    # You are here
├── CONTRIBUTING.md              # Domain/stack contribution process
├── CODE_OF_CONDUCT.md           # Community standards
├── SECURITY.md                  # Vulnerability disclosure policy
├── docs/                        # All documentation
│   ├── vision/                  # master · product · strategy
│   ├── guides/                  # quickstart · ai-instructions
│   └── reference/               # manifest (navigation map)
├── framework/                   # Layer 1: universal primitives
├── constitution/                # Layers 2–4: the standards database
│   ├── C00-constitutional-order.md
│   ├── core/                    # By phase (Phase 0–3)
│   ├── implementation/          # Stack bindings
│   ├── domains/                 # Domain extensions
│   └── indexes/                 # Fast lookup
├── protocols/                   # How the system operates
│   ├── modes/                   # personal · team · enterprise
│   └── frameworks/              # AI development + review frameworks
├── governance/                  # Operational records
│   ├── runbooks/                # RB-01 – RB-08
│   ├── decisions/               # ADRs + restructure records
│   └── changelog/               # Amendment audit trail
├── platform/                    # The product (engine + surfaces)
├── reference-systems/           # Flagship implementations
├── templates/                   # Instantiation templates
├── compiled/                    # Compiled constitutional index (engine output)
└── scripts/                     # The engine (Python): compile · validate · codegen · cli
                                 #   · mcp · checks · enforce · score · report · bible
                                 #   · semantic · dashboard · guardian · notify
```

---

## The platform

The constitution is compiled into a typed index (`compiled/constitution.json`) that
every surface reads — one source of truth, no surface re-parses markdown.

### Detection — three tiers

| Tier | What | Discipline |
|------|------|------------|
| **Reliable** | Deterministic rules, each bound to a real anti-pattern | Blocks in CI when high-confidence |
| **Advisory** | Medium-confidence reliable rules | Warns, never blocks |
| **Semantic** | LLM review grounded in the constitution | Advisory only; provider-agnostic; inactive without a key |

### Surfaces

| Surface | Status | What it does |
|---------|--------|--------------|
| MCP server | ✅ | Live constitutional governance for AI tools |
| CLI (`governova`) | ✅ | The unified command surface |
| IDE extension | ✅ | VS Code / Cursor diagnostics + hover |
| CI/CD enforcer | ✅ | The merge gate — blocks violating PRs |
| PR Guardian | ✅ | Consolidated per-PR governance verdict |
| Web dashboard | ✅ | Self-contained HTML governance dashboard |
| Chat notifier | ✅ | Slack/Teams verdicts via webhook |
| JetBrains plugin | ◻︎ | Planned |

### The four §18 outputs

**Governova Score** (0–100) · **Governova Certified** (≥85) · **Board-Level Governance
Report** · **System Bible** — all generated automatically from the engine.

### Command surface

```bash
governova stats | standards | standard <id>      # explore the constitution
governova validate | compile [--check]            # integrity + drift
governova score | coverage | govscore             # health · enforcement coverage · project score
governova report | bible | dashboard              # §18 outputs
governova guard --base <ref>                      # PR governance verdict
governova-enforce --changed --base <ref>          # the CI merge gate
governova semantic-review <paths>                 # advisory LLM tier (env-gated)
governova notify --base <ref>                     # chat webhook (env-gated)
```

---

*Built by Maluleke Kurhula Success · KSDRILL SA · 2026*
