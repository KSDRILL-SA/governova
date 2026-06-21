# Auth0 — Implementation Binding (Layer 3)

**Status:** Planned — community-contributable
**Binds:** C03 — Auth (IdP)
**Constitution:** `constitution/core/` (C03)

Stack-specific binding of the universal C03 standards to **Auth0**. Shows how each
universal `S{C}.{N}` is satisfied in this stack, and what failure looks like here
(`AP-S{C}.{N}{letter}/auth0`).

This binding is a **stub**: the universal core and framework already apply to any
Auth0 system today. A full binding is authored via the contribution process
(`CONTRIBUTING.md`) using `templates/implementation-guide-template.md` and the
proven reference bindings (fastapi, nextjs, angular, nextauth, prisma-postgresql,
beanie-mongodb, chromadb) as the pattern.

See `constitution/indexes/stack-selection-guide.md` for how a stack is chosen,
and `constitution/implementation/README.md` for the binding principle.
