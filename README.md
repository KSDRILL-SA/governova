# Governova

> *"AI can build anything. It is us who must tell it exactly what to build,
> how to build it, what not to build, and who approves every decision."*

[![Status](https://img.shields.io/badge/Status-LOCKED-red)](docs/vision/master.md)
[![Version](https://img.shields.io/badge/Version-v2.0-blue)](docs/vision/master.md)
[![Constitutions](https://img.shields.io/badge/Constitutions-11-purple)](constitution/core/)
[![Standards](https://img.shields.io/badge/Standards-613-green)](constitution/indexes/standards-index.md)
[![Phases](https://img.shields.io/badge/Phases-4-teal)](framework/phase-model.md)
[![Locked](https://img.shields.io/badge/Locked-2026--05--22-orange)](docs/vision/master.md)

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
| 2 — Core | `constitution/core/` | 11 constitutions across 4 phases — universal standards as principles |
| 3 — Implementation | `constitution/implementation/` | Stack-specific bindings of core standards |
| 4 — Domains | `constitution/domains/` | Industry-specific extensions |

**613 live standards** across 11 constitutions (594 locked baseline + 6 ratified C0 §8 amendments).

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
└── scripts/                     # Engine: compile · validate · codegen · cli · mcp
```

---

*Built by Maluleke Kurhula Success · KSDRILL SA · 2026*
