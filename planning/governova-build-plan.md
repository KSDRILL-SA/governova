# Governova — Build Plan

| Attribute | Value |
|-----------|-------|
| **Document** | Build Plan — zero to v1.0 |
| **Status** | DRAFT — pending Phase A start |
| **Target scope** | Phases A–F (free tier + paid backend) |
| **Locked decisions** | See §6 |
| **Authors** | Maluleke Kurhula Success |
| **Created** | 2026-05-24 |

---

> *The Master Document (`GOVERNOVA-MASTER.md`) defines what Governova **is**.
> This document defines how it gets **built** — phase by phase, file by file,
> with explicit definitions of done.*

---

## §1 — Why this document exists

`GOVERNOVA-MASTER.md` is the locked vision. It says what Governova must become: a four-layer constitutional architecture with one governance engine, seven product surfaces, four outputs, and an intelligence layer.

What it does **not** do is sequence the build. This document fills that gap. It breaks the destination state into six executable phases (A–F), each with its own spec file under `planning/phase-{X}-spec.md`. Phase G+ (enterprise features — Mapping Engine, JetBrains, Intelligence Network, Certification, Temporal Governance) is explicitly out of scope for v1.0 and will be planned after v1.0 ships.

The build target: **a Governova v1.0 that can govern the build of the four reference systems** (FundsLink Academy, Maphophe, KSDRILL Reserve Bank, SyncUp) and serve as commercial-grade evidence of the platform's value.

---

## §2 — Current state vs destination state

### What exists today

The repository is fully restructured into the four-layer architecture per `GOVERNOVA-MASTER.md §22`. Every constitution (C00–C10), framework primitive, protocol, runbook, ADR, template, and reference-system context is in place.

### What does NOT exist

The **product** — every executable surface of Governova — is unbuilt. There is no working CLI, no MCP server, no engine, no extension, no dashboard, no CI/CD enforcer. The constitutional database itself is markdown only; nothing can query it programmatically.

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

## §3 — The six v1.0 phases

```
Phase A — Constitution as data        Foundation for every surface
        │
        ├──► Phase B — CLI (TypeScript)
        ├──► Phase C — MCP server (TypeScript, stdio)
        ├──► Phase D — GitHub Action (wraps CLI from B)
        └──► Phase E — VS Code + Cursor extension (TypeScript)
                │
                â–¼
        Phase F — Governance engine (FastAPI) + Dashboard (Next.js) + Payments
```

Phases B, C, E run in parallel after A. Phase D depends on B. Phase F depends on a stabilised compiled-index schema from A and reuses score logic from B.

### Phase A — Constitution as data

Turn the markdown constitutions into a machine-readable, integrity-validated, typed JSON index. Without this, nothing else can compile.

**Deliverables:** parser, validator v2, schema, compiled index, TS + Py type packages, ADR-005, CI workflow.
**Detail:** `planning/phase-a-spec.md`.
**Estimate:** 5–10 work-sessions.

### Phase B — CLI (`governova`)

TypeScript-distributed CLI. Reads compiled index. Provides init, validate, score, relay status, generate-cursorrules.

**Deliverables:** `platform/surfaces/cli/` package, published to npm as `governova` (or `@governova/cli`).
**Detail:** `planning/phase-b-spec.md` (to be drafted before B starts).
**Estimate:** 10–15 work-sessions.

### Phase C — MCP server

TypeScript MCP server running over stdio. Wires Claude Code, Cursor, and any MCP-compatible AI tool into live constitutional queries.

**Tools exposed:** `get_standard`, `get_active_constitution`, `check_violation`, `get_anti_pattern`, `get_relay_state`, `log_ai_action`, `get_runbook`, `flag_temporal_review`.

**Deliverables:** `platform/surfaces/mcp-server/` package.
**Detail:** `planning/phase-c-spec.md` (drafted before C starts).
**Estimate:** 8–12 work-sessions.

### Phase D — GitHub Action (CI/CD enforcer)

Reusable composite action. Runs CLI validate on every PR. Posts check run. SEV0/SEV1 block merge; SEV2 requires exception; SEV3 logs.

**Deliverables:** `platform/surfaces/github-action/` with `action.yml`, dist bundle, marketplace listing.
**Detail:** `planning/phase-d-spec.md`.
**Estimate:** 5–8 work-sessions.

### Phase E — VS Code + Cursor extension

TypeScript extension. Sidebar standards browser by active layer. Inline violation highlights (calls CLI). Relay step tracker. Hover overlay for standards.

**Deliverables:** `platform/surfaces/vscode-extension/` package, published to VS Marketplace and Open VSX.
**Detail:** `planning/phase-e-spec.md`.
**Estimate:** 15–20 work-sessions.

### Phase F — Engine + Dashboard + Payments

The commercial product layer.

- **Engine** (`platform/engine/`): FastAPI on Railway. Constitutional store, violation log, audit trail, score computation, license server.
- **Dashboard** (`platform/surfaces/dashboard/`): Next.js on Vercel. Project health, violation heatmap, audit trail browser, score trend, billing portal.
- **Payments**: Lemon Squeezy for Pro / Pro+ / Max tiers per `GOVERNOVA-MASTER.md §19.1`.
- **License**: short-lived JWT (24h auto-refresh), machine ID binding, concurrent session detection.

**Deliverables:** working engine + dashboard + payment integration + license JWTs.
**Detail:** `planning/phase-f-spec.md`.
**Estimate:** 30–50 work-sessions (the largest phase by far).

---

## §4 — Monorepo layout

```
governova/                  (the Governova repo)
├── (existing) GOVERNOVA-MASTER.md, framework/, constitution/, protocols/, ...
│
├── planning/                            ← this folder
│   ├── governova-build-plan.md          (this file)
│   ├── phase-a-spec.md                  (next phase to execute)
│   ├── phase-b-spec.md                  (drafted before Phase B starts)
│   └── ... per-phase specs added as we go
│
├── compiled/                            (Phase A output)
│   ├── constitution.json                (the index — committed)
│   ├── constitution.schema.json         (versioned schema)
│   └── checksum.txt
│
├── platform/
│   ├── engine/                          (Phase F — FastAPI)
│   │   ├── app/  · alembic/  · tests/  · pyproject.toml
│   ├── surfaces/
│   │   ├── cli/                         (Phase B — TypeScript)
│   │   ├── mcp-server/                  (Phase C — TypeScript)
│   │   ├── github-action/               (Phase D)
│   │   ├── vscode-extension/            (Phase E — TypeScript)
│   │   └── dashboard/                   (Phase F — Next.js)
│   └── shared/                          (Phase A output — generated types)
│       ├── types-ts/                    (published as @governova/types)
│       └── types-py/                    (published as governova-types)
│
└── scripts/
    ├── compile-constitution.py          (Phase A — parser)
    ├── validate-integrity.py            (Phase A v2 — replaces stub)
    └── generate-schemas.py              (Phase A — emits TS + Py types)
```

### Monorepo tooling

| Side | Tool | Purpose |
|------|------|---------|
| TypeScript | pnpm workspaces + Turborepo | Single `pnpm install` bootstraps CLI + MCP + extension + dashboard. Cached builds. |
| Python | uv workspaces | Single `uv sync` bootstraps scripts + engine. Fast resolver. |
| Shared schema | Python is source of truth | Parser emits JSON Schema → both TS and Py types regenerated from it |
| Pre-commit | `pre-commit` framework | Runs compile + validate + format on every commit |

---

## §5 — Shared-types boundary

The CLI / MCP / extension / dashboard (TypeScript) and the engine / scripts (Python) must agree on the shape of every constitutional record. The boundary is enforced by:

1. **Source of truth:** Pydantic v2 models in `scripts/schema.py`.
2. **Schema export:** `scripts/compile-constitution.py` writes `compiled/constitution.schema.json`.
3. **Type generation:** `scripts/generate-schemas.py` emits both `platform/shared/types-ts/index.d.ts` and `platform/shared/types-py/__init__.py`.
4. **Consumers:** every surface imports from one of the generated packages — never reads markdown directly.

Any breaking change to the schema bumps `schema_version` in the compiled index and forces every consumer to update.

---

## §6 — Locked decisions

| # | Decision | Rationale |
|---|----------|-----------|
| D1 | v1.0 scope = Phases A–F | Includes free tier (CLI, MCP, GH Action, extension) AND paid backend (engine, dashboard, payments). Phase G+ (System Bible, Mapping Engine, Intelligence Network, JetBrains, Certification) is post-v1.0. |
| D2 | TypeScript CLI + FastAPI engine | TS gives best ecosystem fit for CLI / MCP / IDE / CI. FastAPI matches existing ADR-001/003 backend stack. |
| D3 | Monorepo (single repo for everything) | Code + constitutions stay in sync. One PR can update both. Matches `GOVERNOVA-MASTER.md §22` structure. |
| D4 | Python = schema source of truth | One Pydantic definition → JSON Schema → TS + Py types. Single point of truth. |
| D5 | Validator includes markdown link integrity | Catches broken paths in MANIFEST and cross-references. Cheap to add. |
| D6 | No content edits to C00–C10 without explicit per-file approval | Strict L3 boundary preserved. If parser cannot handle a constitution's format, stop and ask. |
| D7 | `compiled/constitution.json` is committed | Consumers pin a version without re-running the parser. |
| D8 | Phase G+ planned later | Mapping Engine, Intelligence Network, JetBrains, Certification, Temporal Governance, Board Report — all explicitly post-v1.0. |

---

## §7 — Definition of v1.0 done

Governova v1.0 is **shipped** when all of the following are true:

- [ ] Phase A complete: compiled index exists, validator green, types published
- [ ] Phase B complete: `governova` CLI on npm, all commands working against compiled index
- [ ] Phase C complete: MCP server installable, Claude Code + Cursor wired to it
- [ ] Phase D complete: GitHub Action published to marketplace, in use on `governova` itself
- [ ] Phase E complete: VS Code extension on Marketplace, Cursor compatibility verified
- [ ] Phase F complete: engine deployed to Railway, dashboard on Vercel, Lemon Squeezy payments live, license JWTs working
- [ ] FundsLink Academy is being built under Governova v1.0 governance — every commit validated, every relay session logged
- [ ] At least one paying Pro user (can be the founder)
- [ ] `governova.dev` website live with documentation
- [ ] Open-source core constitutions published

**v1.0 is NOT done until Governova is actively governing FundsLink.** That is the dogfood proof.

---

## §8 — What comes after v1.0 (preview only)

Recorded here so the v1.0 build stays focused. **No work on these until v1.0 ships.**

- **Phase G — System Bible generator** (`GOVERNOVA-MASTER.md §13`)
- **Phase H — PR Guardian Bot** (`§17.4`)
- **Phase I — Mapping Engine** (`§14`)
- **Phase J — JetBrains plugin** (`§17.2`)
- **Phase K — Slack/Teams bot** (`§17.7`)
- **Phase L — Intelligence Network** (`§15.1`)
- **Phase M — Temporal Governance** (`§15.2`)
- **Phase N — Pre-build Risk Assessment** (`§15.3`)
- **Phase O — Governova Certified programme** (`§18.2`)
- **Phase P — Board-level report generator** (`§18.3`)

These are real phases. They are real revenue. They are also each their own multi-month build. v1.0 first.

---

## §9 — Build governance

This build itself operates under Governova's own constitutions:

- **L4 — Approve**: Maluleke Kurhula Success (always, no exceptions)
- **L3 — Build**: Claude Code (this AI engineer)
- **Branching**: every phase gets its own branch off `Dev`; PR targets `Dev`; L4 merges manually
- **Commits**: authored as Maluleke Kurhula Success; no AI attribution in code, commits, PR titles, or PR bodies
- **Each phase**: spec drafted and approved BEFORE coding starts
- **Each amendment to this plan**: recorded in `governance/changelog/amendments-log.md`

---

*This is a living document. Each phase completion will append a "Phase X — Done" section with actual effort, deviations, and lessons learned.*

*Version 1.0 (draft) — 2026-05-24 — KSDRILL SA*
