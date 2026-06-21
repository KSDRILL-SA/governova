# Phoenix Elixir — Implementation Binding (Layer 3)

**Status:** Planned — community-contributable
**Binds:** C02 — Backend (Elixir)
**Constitution:** `constitution/core/` (C02)

Stack-specific binding of the universal C02 standards to **Phoenix Elixir**. Shows how each
universal `S{C}.{N}` is satisfied in this stack, and what failure looks like here
(`AP-S{C}.{N}{letter}/phoenix-elixir`).

This binding is a **stub**: the universal core and framework already apply to any
Phoenix Elixir system today. A full binding is authored via the contribution process
(`CONTRIBUTING.md`) using `templates/implementation-guide-template.md` and the
proven reference bindings (fastapi, nextjs, angular, nextauth, prisma-postgresql,
beanie-mongodb, chromadb) as the pattern.

See `constitution/indexes/stack-selection-guide.md` for how a stack is chosen,
and `constitution/implementation/README.md` for the binding principle.
