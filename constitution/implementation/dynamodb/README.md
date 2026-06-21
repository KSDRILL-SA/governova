# Dynamodb — Implementation Binding (Layer 3)

**Status:** Planned — community-contributable
**Binds:** C05 — Database (NoSQL)
**Constitution:** `constitution/core/` (C05)

Stack-specific binding of the universal C05 standards to **Dynamodb**. Shows how each
universal `S{C}.{N}` is satisfied in this stack, and what failure looks like here
(`AP-S{C}.{N}{letter}/dynamodb`).

This binding is a **stub**: the universal core and framework already apply to any
Dynamodb system today. A full binding is authored via the contribution process
(`CONTRIBUTING.md`) using `templates/implementation-guide-template.md` and the
proven reference bindings (fastapi, nextjs, angular, nextauth, prisma-postgresql,
beanie-mongodb, chromadb) as the pattern.

See `constitution/indexes/stack-selection-guide.md` for how a stack is chosen,
and `constitution/implementation/README.md` for the binding principle.
