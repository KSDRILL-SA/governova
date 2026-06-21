# Implementation — Layer 3: Stack-Specific Bindings

This folder contains the implementation guides that bind universal core standards
to specific technologies. Each binding shows how a universal principle is satisfied
in a concrete stack, and what failure looks like there.

## The principle of binding

A core standard states what must be true (universal).
An implementation binding states how it is satisfied in a specific technology.

Example:
- Core (universal): S2.04 — Every endpoint validates all input against a typed schema.
- Implementation (fastapi): S2.04/fastapi — Satisfied by a Pydantic model bound to
  every route. Raw dict access is AP-S2.04a/fastapi.

## The KSDRILL SA reference bindings

| Folder | Binds | For |
|--------|-------|-----|
| `nextjs/` | C04 Frontend | Content-driven, SEO-critical systems (Maphophe, SyncUp) |
| `angular/` | C04 Frontend | Enterprise dashboards, financial systems (FundsLink, Reserve Bank) |
| `fastapi/` | C02 Backend | All backend services |
| `nextauth/` | C03 Auth | Authentication across both stacks |
| `prisma-postgresql/` | C05 Database | Relational, transactional data |
| `beanie-mongodb/` | C05 Database | Document, flexible-schema data |
| `chromadb/` | C05 Database | Vector data, AI/RAG pipelines |

## Migration status
Implementation guides migrated from the original repo:
- C02-backend-implementation.md → `fastapi/C02-backend-fastapi.md`
- C03-auth-implementation.md → `nextauth/C03-auth-nextauth.md`
- C04-frontend-implementation.md → `nextjs/C04-frontend-nextjs.md`
- C05-database-implementation.md → `prisma-postgresql/C05-database-prisma.md`

Note: The full split of the C04 guide (`nextjs` + `angular`) and the C05 guide
(`prisma-postgresql` + `beanie-mongodb` + `chromadb`) by stack is a Phase 1 build
task. For now the full guide sits in the primary stack folder; the split is noted here.
