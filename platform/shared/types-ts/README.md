# @governova/types (TypeScript)

Generated TypeScript types for the Governova compiled constitutional index.

**Do not edit `src/index.ts` by hand.** It is generated from
`compiled/constitution.schema.json` by `governova-codegen`, whose source of truth
is `scripts/governova_compile/schema.py`.

## Regenerate

```bash
# From the repo root (orchestrated):
uv run governova-codegen

# Or directly:
cd platform/shared/types-ts
npm install
npm run generate
npm run typecheck
```

The Python equivalent lives at `platform/shared/types-py/`.
