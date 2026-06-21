# Governova

> *"AI can build anything. It is us who must tell it exactly what to build,
> how to build it, what not to build, and who approves every decision."*

[![Status](https://img.shields.io/badge/Status-LOCKED-red)](GOVERNOVA-MASTER.md)
[![Version](https://img.shields.io/badge/Version-v2.0-blue)](GOVERNOVA-MASTER.md)
[![Constitutions](https://img.shields.io/badge/Constitutions-11-purple)](constitution/core/)
[![Standards](https://img.shields.io/badge/Standards-613-green)](constitution/indexes/standards-index.md)
[![Phases](https://img.shields.io/badge/Phases-4-teal)](framework/phase-model.md)
[![Locked](https://img.shields.io/badge/Locked-2026--05--22-orange)](GOVERNOVA-MASTER.md)

---

**Governova** is the world's first AI development governance platform.
The constitutional layer between AI capability and enterprise trust.

[â†’ Read the full vision: GOVERNOVA-MASTER.md](GOVERNOVA-MASTER.md) Â·
[Product](GOVERNOVA-PRODUCT.md) Â·
[Strategy](GOVERNOVA-STRATEGY.md)

---

## What it is

Governova tells AI tools exactly what to build, how to build it, what not to build,
and who approves every decision â€” for any system, any domain, any stack, any scale.
It records every AI action in an immutable audit trail and generates complete
documentation for every file ever built.

## Four-layer architecture

| Layer | Folder | Description |
|-------|--------|-------------|
| 1 â€” Framework | `framework/` | Universal primitives: format, phases, severity, permissions, hierarchy, amendments |
| 2 â€” Core | `constitution/core/` | 11 constitutions across 4 phases â€” universal standards as principles |
| 3 â€” Implementation | `constitution/implementation/` | Stack-specific bindings of core standards |
| 4 â€” Domains | `constitution/domains/` | Industry-specific extensions |

**613 live standards** across 11 constitutions (594 locked baseline + 6 ratified C0 Â§8 amendments).

## Quick start

```bash
# Clone alongside your project
git clone https://github.com/KSDRILL-SA/governova.git

# First â€” read the master document
cat GOVERNOVA-MASTER.md

# Start a new governed project
cat QUICKSTART.md

# Validate constitutional integrity at any time
python scripts/validate-integrity.py
```

## Repository structure

```
governova/
â”œâ”€â”€ GOVERNOVA-MASTER.md          # Source of truth â€” read this first
â”œâ”€â”€ GOVERNOVA-PRODUCT.md         # Product + go-to-market
â”œâ”€â”€ GOVERNOVA-STRATEGY.md        # Thesis + adversarial risk analysis
â”œâ”€â”€ QUICKSTART.md                # 10-step new project setup
â”œâ”€â”€ CONTRIBUTING.md              # Domain/stack contribution process
â”œâ”€â”€ AI-INSTRUCTIONS.md           # Read first, every AI session
â”œâ”€â”€ MANIFEST.md                  # Complete navigation map
â”œâ”€â”€ framework/                   # Layer 1: universal primitives
â”œâ”€â”€ constitution/                # Layers 2â€“4: the standards database
â”‚   â”œâ”€â”€ C00-constitutional-order.md
â”‚   â”œâ”€â”€ core/                    # By phase (Phase 0â€“3)
â”‚   â”œâ”€â”€ implementation/          # Stack bindings
â”‚   â”œâ”€â”€ domains/                 # Domain extensions
â”‚   â””â”€â”€ indexes/                 # Fast lookup
â”œâ”€â”€ protocols/                   # How the system operates
â”‚   â”œâ”€â”€ modes/                   # personal Â· team Â· enterprise
â”‚   â””â”€â”€ frameworks/              # AI development + review frameworks
â”œâ”€â”€ governance/                  # Operational records
â”‚   â”œâ”€â”€ runbooks/                # RB-01 â€“ RB-08
â”‚   â”œâ”€â”€ decisions/               # ADRs + restructure records
â”‚   â””â”€â”€ changelog/               # Amendment audit trail
â”œâ”€â”€ platform/                    # The product (engine + 8 surfaces)
â”œâ”€â”€ reference-systems/           # 4 flagship implementations
â”œâ”€â”€ templates/                   # Instantiation templates
â””â”€â”€ scripts/                     # validate-integrity.py
```

---

*Built by Maluleke Kurhula Success Â· KSDRILL SA Â· 2026*
