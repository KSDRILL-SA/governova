# Governova — IDE Extension (the wedge)

**Status:** Alpha — ground broken (v0.1.0)
**Surface:** VS Code + Cursor · the product wedge (GOVERNOVA-STRATEGY §4)

The free developer surface that makes AI-generated code legible and trustworthy in the
moment of writing it. It consumes the **compiled constitutional index**
(`compiled/constitution.json`, produced by `governova-compile`) — it never re-parses
markdown — and surfaces governance directly in the editor.

## What v0.1 does

| Feature | Description |
|---------|-------------|
| **Standards explorer** | Activity-bar sidebar: every constitution → its standards, loaded from the compiled index |
| **Hover docs** | Hover any `S{C}.{N}` reference in any file → the standard's title, statement, and anti-patterns |
| **Reliable-tier diagnostics** | Deterministic, **advisory-only** violation surfacing (token in localStorage → `AP-S3.14a`, wildcard CORS → `AP-S2.17a`, money as float → `AP-S2.34a`, leaked error detail → `AP-S2.18a`). Never blocks — per STRATEGY §11.2 |
| **`.cursorrules` generator** | `Governova: Generate .cursorrules` writes a governance file so Cursor's own AI inherits the standards |
| **Find Standard** | `Governova: Find Standard…` — quick-pick search across all standards |

## Architecture

```
governova-compile  →  compiled/constitution.json  →  IDE extension (this)
   (engine)              (index of record)             (consumes, never re-parses)
```

The extension finds the index in the workspace, `.ksdrill/`, or `_governance/` (or via
the `governova.indexPath` setting).

## Develop

```bash
cd platform/surfaces/ide-extension
npm install
npm run typecheck   # tsc --noEmit
npm run compile     # tsc -> out/
# Press F5 in VS Code to launch an Extension Development Host
```

## Honest scope

Per the strategy, the wedge ships the **reliable detection tiers only** and is **advisory,
never blocking**. Semantic/intent detection is reserved for the CI/PR surfaces. This is
v0.1 — ground broken, not the finished product.
