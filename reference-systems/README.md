# Reference Systems — Examples Built *With* Governova

> **These systems are downstream examples that consume Governova — not dependencies of it.**
> Governova does not depend on, require, or build around them. They are the *first systems
> governed by* Governova, kept here as worked references for **anyone building any system**:
> how a stack is chosen, how the constitution is compiled, how the workflow runs, how a
> domain is applied. Delete every folder below and Governova is unchanged and complete.

The dependency arrow points one way:

```
Governova (framework · core · implementation · domains · protocols)
        │  governs
        ▼
Reference systems (examples)  ──  Your system (greenfield or brownfield)
```

They exist to **teach by example** and to **seed the domain library** with battle-tested
standards — not to scope what Governova can govern. Governova governs any system, any stack,
any domain, any organisation (see `constitution/indexes/stack-selection-guide.md`).

## The example systems

| System | Domain | Stack (chosen via the selection guide) | ADR |
|--------|--------|----------------------------------------|-----|
| `fundslink-academy/` | Fintech + Edtech | Angular + FastAPI | ADR-001 |
| `maphophe/` | Govtech + Community | Next.js | ADR-002 |
| `ksdrill-reserve-bank/` | Fintech + Banking | Angular + FastAPI | ADR-003 |
| `syncup/` | Creator + SaaS | Next.js | ADR-004 |

Each demonstrates the **method**, not a menu — the same method applies to a Go service, a
Laravel monolith, a Flutter app, or any other stack (`constitution/implementation/`).

## What each example demonstrates

| Folder | Contents | Teaches |
|--------|----------|---------|
| `context.md` | System context (stack, phase, mode) | How a system declares its governed context |
| `CONSTITUTION-INDEX.md` *(build task)* | Compiled active constitution | How Framework + Core + Implementation + Domains compile for a real system |
| `README.md` *(build task)* | Overview + governance status | How stack/tech/workflow choices are recorded and justified |

> New systems — greenfield (`protocols/github-workflow.md`) or brownfield
> (`protocols/brownfield-adoption.md`) — are **not** added here. This folder holds only the
> canonical examples. Your system lives in your own repository, governed by Governova cloned
> beside it.
