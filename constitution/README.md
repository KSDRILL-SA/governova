# Constitution — The Standards Database

This folder contains the complete Governova constitutional standards database,
organised in four layers:

| Layer | Folder | Description |
|-------|--------|-------------|
| Layer 2 | `core/` | Universal constitutions organised by phase — principles that apply to any system |
| Layer 3 | `implementation/` | Stack-specific bindings — how universal principles are satisfied in specific technologies |
| Layer 4 | `domains/` | Domain-specific extensions — what specific industries additionally require |
| Index | `indexes/` | Fast lookup: standards, anti-patterns, quick reference, stack matrix |

## C00 — Constitutional Order
`C00-constitutional-order.md` sits at this folder root — above the phases —
because it governs the phases themselves.

## How a project compiles its constitution
A project declares its stack and domain. Governova compiles:
Framework + Core (all phases) + Implementation (declared stack) + Domains (declared domain)
= the project's CONSTITUTION-INDEX

See GOVERNOVA-MASTER.md §5 for the full compilation model.
