# Governova â€” Build Plan

| Attribute | Value |
|-----------|-------|
| **Document** | Build Plan â€” zero to v1.0 |
| **Status** | DRAFT â€” pending Phase A start |
| **Target scope** | Phases Aâ€“F (free tier + paid backend) |
| **Locked decisions** | See Â§6 |
| **Authors** | Maluleke Kurhula Success |
| **Created** | 2026-05-24 |

---

> *The Master Document (`GOVERNOVA-MASTER.md`) defines what Governova **is**.
> This document defines how it gets **built** â€” phase by phase, file by file,
> with explicit definitions of done.*

---

## Â§1 â€” Why this document exists

`GOVERNOVA-MASTER.md` is the locked vision. It says what Governova must become: a four-layer constitutional architecture with one governance engine, seven product surfaces, four outputs, and an intelligence layer.

What it does **not** do is sequence the build. This document fills that gap. It breaks the destination state into six executable phases (Aâ€“F), each with its own spec file under `planning/phase-{X}-spec.md`. Phase G+ (enterprise features â€” Mapping Engine, JetBrains, Intelligence Network, Certification, Temporal Governance) is explicitly out of scope for v1.0 and will be planned after v1.0 ships.

The build target: **a Governova v1.0 that can govern the build of the four reference systems** (FundsLink Academy, Maphophe, KSDRILL Reserve Bank, SyncUp) and serve as commercial-grade evidence of the platform's value.

---

## Â§2 â€” Current state vs destination state

### What exists today

The repository is fully restructured into the four-layer architecture per `GOVERNOVA-MASTER.md Â§22`. Every constitution (C00â€“C10), framework primitive, protocol, runbook, ADR, template, and reference-system context is in place.

### What does NOT exist

The **product** â€” every executable surface of Governova â€” is unbuilt. There is no working CLI, no MCP server, no engine, no extension, no dashboard, no CI/CD enforcer. The constitutional database itself is markdown only; nothing can query it programmatically.

### The gap to close

| Concern | Today | v1.0 target |
|---------|-------|-------------|
| Constitution storage | Markdown files only | Machine-readable JSON index, regenerated on every commit |
| Query interface | None | CLI + MCP server (stdio) + REST API |
| Validation | Manual | CLI + GitHub Action, blocks PRs on SEV0/SEV1 |
| AI integration | Static file reads | MCP server with live constitutional queries |
| IDE integration | None | VS Code + Cursor extension with violation highlights |
| Score / dashboard | None | Web dashboard on Vercel + engine on Railway |
| Commercial product | None | Free / Pro / Pro+ / Max tiers with license server + Lemon Squeezy payments |
| System Bible | None | Deferred to post-v1.0 (Phase G) |
| Mapping Engine | None | Deferred to post-v1.0 (Phase H) |

---

## Â§3 â€” The six v1.0 phases

```
Phase A â€” Constitution as data        Foundation for every surface
        â”‚
        â”œâ”€â”€â–º Phase B â€” CLI (TypeScript)
        â”œâ”€â”€â–º Phase C â€” MCP server (TypeScript, stdio)
        â”œâ”€â”€â–º Phase D â€” GitHub Action (wraps CLI from B)
        â””â”€â”€â–º Phase E â€” VS Code + Cursor extension (TypeScript)
                â”‚
                â–¼
        Phase F â€” Governance engine (FastAPI) + Dashboard (Next.js) + Payments
```

Phases B, C, E run in parallel after A. Phase D depends on B. Phase F depends on a stabilised compiled-index schema from A and reuses score logic from B.

### Phase A â€” Constitution as data

Turn the markdown constitutions into a machine-readable, integrity-validated, typed JSON index. Without this, nothing else can compile.

**Deliverables:** parser, validator v2, schema, compiled index, TS + Py type packages, ADR-005, CI workflow.
**Detail:** `planning/phase-a-spec.md`.
**Estimate:** 5â€“10 work-sessions.

### Phase B â€” CLI (`governova`)

TypeScript-distributed CLI. Reads compiled index. Provides init, validate, score, relay status, generate-cursorrules.

**Deliverables:** `platform/surfaces/cli/` package, published to npm as `governova` (or `@governova/cli`).
**Detail:** `planning/phase-b-spec.md` (to be drafted before B starts).
**Estimate:** 10â€“15 work-sessions.

### Phase C â€” MCP server

TypeScript MCP server running over stdio. Wires Claude Code, Cursor, and any MCP-compatible AI tool into live constitutional queries.

**Tools exposed:** `get_standard`, `get_active_constitution`, `check_violation`, `get_anti_pattern`, `get_relay_state`, `log_ai_action`, `get_runbook`, `flag_temporal_review`.

**Deliverables:** `platform/surfaces/mcp-server/` package.
**Detail:** `planning/phase-c-spec.md` (drafted before C starts).
**Estimate:** 8â€“12 work-sessions.

### Phase D â€” GitHub Action (CI/CD enforcer)

Reusable composite action. Runs CLI validate on every PR. Posts check run. SEV0/SEV1 block merge; SEV2 requires exception; SEV3 logs.

**Deliverables:** `platform/surfaces/github-action/` with `action.yml`, dist bundle, marketplace listing.
**Detail:** `planning/phase-d-spec.md`.
**Estimate:** 5â€“8 work-sessions.

### Phase E â€” VS Code + Cursor extension

TypeScript extension. Sidebar standards browser by active layer. Inline violation highlights (calls CLI). Relay step tracker. Hover overlay for standards.

**Deliverables:** `platform/surfaces/vscode-extension/` package, published to VS Marketplace and Open VSX.
**Detail:** `planning/phase-e-spec.md`.
**Estimate:** 15â€“20 work-sessions.

### Phase F â€” Engine + Dashboard + Payments

The commercial product layer.

- **Engine** (`platform/engine/`): FastAPI on Railway. Constitutional store, violation log, audit trail, score computation, license server.
- **Dashboard** (`platform/surfaces/dashboard/`): Next.js on Vercel. Project health, violation heatmap, audit trail browser, score trend, billing portal.
- **Payments**: Lemon Squeezy for Pro / Pro+ / Max tiers per `GOVERNOVA-MASTER.md Â§19.1`.
- **License**: short-lived JWT (24h auto-refresh), machine ID binding, concurrent session detection.

**Deliverables:** working engine + dashboard + payment integration + license JWTs.
**Detail:** `planning/phase-f-spec.md`.
**Estimate:** 30â€“50 work-sessions (the largest phase by far).

---

## Â§4 â€” Monorepo layout

```
governova/                  (the Governova repo)
â”œâ”€â”€ (existing) GOVERNOVA-MASTER.md, framework/, constitution/, protocols/, ...
â”‚
â”œâ”€â”€ planning/                            â† this folder
â”‚   â”œâ”€â”€ governova-build-plan.md          (this file)
â”‚   â”œâ”€â”€ phase-a-spec.md                  (next phase to execute)
â”‚   â”œâ”€â”€ phase-b-spec.md                  (drafted before Phase B starts)
â”‚   â””â”€â”€ ... per-phase specs added as we go
â”‚
â”œâ”€â”€ compiled/                            (Phase A output)
â”‚   â”œâ”€â”€ constitution.json                (the index â€” committed)
â”‚   â”œâ”€â”€ constitution.schema.json         (versioned schema)
â”‚   â””â”€â”€ checksum.txt
â”‚
â”œâ”€â”€ platform/
â”‚   â”œâ”€â”€ engine/                          (Phase F â€” FastAPI)
â”‚   â”‚   â”œâ”€â”€ app/  Â· alembic/  Â· tests/  Â· pyproject.toml
â”‚   â”œâ”€â”€ surfaces/
â”‚   â”‚   â”œâ”€â”€ cli/                         (Phase B â€” TypeScript)
â”‚   â”‚   â”œâ”€â”€ mcp-server/                  (Phase C â€” TypeScript)
â”‚   â”‚   â”œâ”€â”€ github-action/               (Phase D)
â”‚   â”‚   â”œâ”€â”€ vscode-extension/            (Phase E â€” TypeScript)
â”‚   â”‚   â””â”€â”€ dashboard/                   (Phase F â€” Next.js)
â”‚   â””â”€â”€ shared/                          (Phase A output â€” generated types)
â”‚       â”œâ”€â”€ types-ts/                    (published as @governova/types)
â”‚       â””â”€â”€ types-py/                    (published as governova-types)
â”‚
â””â”€â”€ scripts/
    â”œâ”€â”€ compile-constitution.py          (Phase A â€” parser)
    â”œâ”€â”€ validate-integrity.py            (Phase A v2 â€” replaces stub)
    â””â”€â”€ generate-schemas.py              (Phase A â€” emits TS + Py types)
```

### Monorepo tooling

| Side | Tool | Purpose |
|------|------|---------|
| TypeScript | pnpm workspaces + Turborepo | Single `pnpm install` bootstraps CLI + MCP + extension + dashboard. Cached builds. |
| Python | uv workspaces | Single `uv sync` bootstraps scripts + engine. Fast resolver. |
| Shared schema | Python is source of truth | Parser emits JSON Schema â†’ both TS and Py types regenerated from it |
| Pre-commit | `pre-commit` framework | Runs compile + validate + format on every commit |

---

## Â§5 â€” Shared-types boundary

The CLI / MCP / extension / dashboard (TypeScript) and the engine / scripts (Python) must agree on the shape of every constitutional record. The boundary is enforced by:

1. **Source of truth:** Pydantic v2 models in `scripts/schema.py`.
2. **Schema export:** `scripts/compile-constitution.py` writes `compiled/constitution.schema.json`.
3. **Type generation:** `scripts/generate-schemas.py` emits both `platform/shared/types-ts/index.d.ts` and `platform/shared/types-py/__init__.py`.
4. **Consumers:** every surface imports from one of the generated packages â€” never reads markdown directly.

Any breaking change to the schema bumps `schema_version` in the compiled index and forces every consumer to update.

---

## Â§6 â€” Locked decisions

| # | Decision | Rationale |
|---|----------|-----------|
| D1 | v1.0 scope = Phases Aâ€“F | Includes free tier (CLI, MCP, GH Action, extension) AND paid backend (engine, dashboard, payments). Phase G+ (System Bible, Mapping Engine, Intelligence Network, JetBrains, Certification) is post-v1.0. |
| D2 | TypeScript CLI + FastAPI engine | TS gives best ecosystem fit for CLI / MCP / IDE / CI. FastAPI matches existing ADR-001/003 backend stack. |
| D3 | Monorepo (single repo for everything) | Code + constitutions stay in sync. One PR can update both. Matches `GOVERNOVA-MASTER.md Â§22` structure. |
| D4 | Python = schema source of truth | One Pydantic definition â†’ JSON Schema â†’ TS + Py types. Single point of truth. |
| D5 | Validator includes markdown link integrity | Catches broken paths in MANIFEST and cross-references. Cheap to add. |
| D6 | No content edits to C00â€“C10 without explicit per-file approval | Strict L3 boundary preserved. If parser cannot handle a constitution's format, stop and ask. |
| D7 | `compiled/constitution.json` is committed | Consumers pin a version without re-running the parser. |
| D8 | Phase G+ planned later | Mapping Engine, Intelligence Network, JetBrains, Certification, Temporal Governance, Board Report â€” all explicitly post-v1.0. |

---

## Â§7 â€” Definition of v1.0 done

Governova v1.0 is **shipped** when all of the following are true:

- [ ] Phase A complete: compiled index exists, validator green, types published
- [ ] Phase B complete: `governova` CLI on npm, all commands working against compiled index
- [ ] Phase C complete: MCP server installable, Claude Code + Cursor wired to it
- [ ] Phase D complete: GitHub Action published to marketplace, in use on `governova` itself
- [ ] Phase E complete: VS Code extension on Marketplace, Cursor compatibility verified
- [ ] Phase F complete: engine deployed to Railway, dashboard on Vercel, Lemon Squeezy payments live, license JWTs working
- [ ] FundsLink Academy is being built under Governova v1.0 governance â€” every commit validated, every relay session logged
- [ ] At least one paying Pro user (can be the founder)
- [ ] `governova.dev` website live with documentation
- [ ] Open-source core constitutions published

**v1.0 is NOT done until Governova is actively governing FundsLink.** That is the dogfood proof.

---

## Â§8 â€” What comes after v1.0 (preview only)

Recorded here so the v1.0 build stays focused. **No work on these until v1.0 ships.**

- **Phase G â€” System Bible generator** (`GOVERNOVA-MASTER.md Â§13`)
- **Phase H â€” PR Guardian Bot** (`Â§17.4`)
- **Phase I â€” Mapping Engine** (`Â§14`)
- **Phase J â€” JetBrains plugin** (`Â§17.2`)
- **Phase K â€” Slack/Teams bot** (`Â§17.7`)
- **Phase L â€” Intelligence Network** (`Â§15.1`)
- **Phase M â€” Temporal Governance** (`Â§15.2`)
- **Phase N â€” Pre-build Risk Assessment** (`Â§15.3`)
- **Phase O â€” Governova Certified programme** (`Â§18.2`)
- **Phase P â€” Board-level report generator** (`Â§18.3`)

These are real phases. They are real revenue. They are also each their own multi-month build. v1.0 first.

---

## Â§9 â€” Build governance

This build itself operates under Governova's own constitutions:

- **L4 â€” Approve**: Maluleke Kurhula Success (always, no exceptions)
- **L3 â€” Build**: Claude Code (this AI engineer)
- **Branching**: every phase gets its own branch off `Dev`; PR targets `Dev`; L4 merges manually
- **Commits**: authored as Maluleke Kurhula Success; no AI attribution in code, commits, PR titles, or PR bodies
- **Each phase**: spec drafted and approved BEFORE coding starts
- **Each amendment to this plan**: recorded in `governance/changelog/amendments-log.md`

---

*This is a living document. Each phase completion will append a "Phase X â€” Done" section with actual effort, deviations, and lessons learned.*

*Version 1.0 (draft) â€” 2026-05-24 â€” KSDRILL SA*
