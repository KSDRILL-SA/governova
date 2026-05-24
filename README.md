# Governova

> *"AI can build anything. It is us who must tell it exactly what to build,
> how to build it, what not to build, and who approves every decision."*

[![Status](https://img.shields.io/badge/Status-LOCKED-red)](GOVERNOVA-MASTER.md)
[![Version](https://img.shields.io/badge/Version-v2.0-blue)](GOVERNOVA-MASTER.md)
[![Constitutions](https://img.shields.io/badge/Constitutions-11-purple)](constitution/core/)
[![Phases](https://img.shields.io/badge/Phases-4-teal)](framework/phase-model.md)
[![Locked](https://img.shields.io/badge/Locked-2026--05--22-orange)](GOVERNOVA-MASTER.md)

---

**Governova** is the world's first AI development governance platform.
The constitutional layer between AI capability and enterprise trust.

[→ Read the full vision: GOVERNOVA-MASTER.md](GOVERNOVA-MASTER.md)

---

## What it is

Governova tells AI tools exactly what to build, how to build it, what not to build,
and who approves every decision — for any system, any domain, any stack, any scale.
It records every AI action in an immutable audit trail and generates complete
documentation for every file ever built.

## Four-layer architecture

| Layer | Folder | Description |
|-------|--------|-------------|
| 1 — Framework | `framework/` | Universal primitives: format, phases, severity, permissions, hierarchy |
| 2 — Core | `constitution/core/` | 11 constitutions across 4 phases — universal standards as principles |
| 3 — Implementation | `constitution/implementation/` | Stack-specific bindings of core standards |
| 4 — Domains | `constitution/domains/` | Industry-specific extensions |

## Quick start

```bash
# Clone alongside your project
git clone https://github.com/MALULEKE-KS/governova.git

# First — read the master document
cat GOVERNOVA-MASTER.md

# Start a new governed project
cat QUICKSTART.md
```

## Repository structure

```
governova/
├── GOVERNOVA-MASTER.md          # Source of truth — read this first
├── QUICKSTART.md                # 10-step new project setup
├── framework/                   # Layer 1: universal primitives
├── constitution/                # Layers 2–4: the standards database
│   ├── C00-constitutional-order.md
│   ├── core/                    # By phase (Phase 0–3)
│   ├── implementation/          # Stack bindings
│   ├── domains/                 # Domain extensions
│   └── indexes/                 # Fast lookup
├── protocols/                   # How the system operates
├── governance/                  # Operational records
│   ├── runbooks/                # RB-01 – RB-08
│   ├── decisions/               # ADRs
│   └── changelog/               # Amendment audit trail
├── platform/                    # The product (engine + surfaces)
├── reference-systems/           # 4 flagship implementations
├── templates/                   # Instantiation templates
└── scripts/                     # validate-integrity · compile-constitution
```

---

*Built by Maluleke Kurhula Success · KSDRILL SA · 2026*
