# Phase A — Constitution as Data — Specification

| Attribute | Value |
|-----------|-------|
| **Phase** | A — Constitution as Data |
| **Status** | DRAFT — approved scope, pending start |
| **Depends on** | PR #5 merged into Dev (done) |
| **Blocks** | Phases B, C, D, E, F |
| **Branch** | `refactor/phase-a-constitution-as-data` (off `Dev`) |
| **Estimate** | 5–10 work-sessions |
| **L4 approver** | Maluleke Kurhula Success |
| **Created** | 2026-05-24 |

---

## A.1 — Goal

Turn the markdown constitutional database into a **machine-readable, integrity-validated, typed JSON index** that every other Governova surface imports from a single source. Without Phase A, no other phase can compile.

---

## A.2 — Deliverables

| # | File | Purpose |
|---|------|---------|
| 1 | `scripts/compile-constitution.py` | Walks `framework/`, `constitution/core/`, `constitution/implementation/`, `constitution/domains/`. Extracts every `S{C}.{N}` standard, every `AP-S{C}.{N}{letter}` anti-pattern, every framework primitive, every runbook reference. Emits `compiled/constitution.json`. |
| 2 | `scripts/validate-integrity.py` v2 | Rewrites the current stub. Loads `compiled/constitution.json`. Verifies: (a) every `S{C}.{N}` reference in any file resolves to a defined standard; (b) every `AP-S{C}.{N}{letter}` references a real standard; (c) every constitution declares its phase; (d) every implementation binding cites a real core standard; (e) hierarchy order is consistent; (f) **markdown link integrity — every `[text](path)` link resolves to a real file**. Exits non-zero on any failure. |
| 3 | `scripts/generate-schemas.py` | Reads `compiled/constitution.schema.json`. Emits `platform/shared/types-ts/index.d.ts` and `platform/shared/types-py/__init__.py` (Pydantic v2 models). Run as part of the compile step. |
| 4 | `scripts/schema.py` | The Pydantic v2 source of truth — every other type derives from these models. |
| 5 | `compiled/constitution.schema.json` | JSON Schema (draft 2020-12) describing the shape of the compiled index. Versioned. Breaking changes bump the schema version. |
| 6 | `compiled/constitution.json` | The artifact itself. Generated AND committed (consumers pin a version without re-running the parser). Has `compiled_at`, `schema_version`, `checksum`, and `source_commit_sha` header. |
| 7 | `compiled/checksum.txt` | SHA256 of `constitution.json` content for tamper detection. |
| 8 | `platform/shared/types-ts/` | Generated TS types + minimal `package.json`. Publishable later as `@governova/types`. |
| 9 | `platform/shared/types-py/` | Generated Pydantic models + minimal `pyproject.toml`. Publishable later as `governova-types` on PyPI. |
| 10 | `pyproject.toml` (root) | uv workspace root, declares `scripts/` and `platform/shared/types-py/` as members. |
| 11 | `.github/workflows/validate.yml` | GitHub Action: on every PR to `Dev` or `main`, runs compile + validate. Fails the check on any integrity error. |
| 12 | `.pre-commit-config.yaml` | Hooks: compile-constitution, validate-integrity, format. |
| 13 | `scripts/README.md` | How to run each script, what they produce, how to interpret failures. |
| 14 | `governance/decisions/ADR-005-constitution-as-data.md` | Records the decision: Python is the source of truth for the schema; markdown constitutions are the authoritative source for content. Records why JSON Schema 2020-12, why Pydantic v2, why we commit the compiled artifact. |
| 15 | `governance/changelog/amendments-log.md` | New entry recording Phase A as the first build phase under the build plan. |

---

## A.3 — Tech stack (Phase A only)

| Concern | Choice | Why |
|---------|--------|-----|
| Language | Python 3.12 | Matches Phase F engine choice; best markdown parsing libraries |
| Markdown parser | `markdown-it-py` | AST-based, robust enough to walk headings + tables + code blocks |
| Schema models | Pydantic v2 | Native JSON Schema export, fast, well-typed |
| Schema dialect | JSON Schema draft 2020-12 | Latest standard, supported by `json-schema-to-typescript` |
| TS type gen | `json-schema-to-typescript` | Deterministic, industry standard |
| Py type "gen" | Pydantic models themselves (no codegen) | The schema IS the Python types |
| Package manager | `uv` | Fast resolver, lockfile, workspace support |
| Pre-commit | `pre-commit` framework | Standard hook runner |
| CI | GitHub Actions | Already wired to repo |

---

## A.4 — Compiled index shape

```json
{
  "schema_version": "1.0.0",
  "compiled_at": "2026-05-24T20:30:00Z",
  "source_commit_sha": "19dc3f8",
  "checksum": "sha256:abc123...",

  "framework": {
    "primitives": [
      {
        "id": "format-specification",
        "title": "Format Specification",
        "path": "framework/format-specification.md",
        "summary": "S{C}.{N} standard ID format, AP anti-pattern format, document structure"
      }
    ]
  },

  "constitutions": [
    {
      "id": "C00",
      "name": "Constitutional Order",
      "phase": null,
      "path": "constitution/C00-constitutional-order.md",
      "hierarchy_rank": 1,
      "binds_implementation": false,
      "standards": []
    },
    {
      "id": "C02",
      "name": "Backend Constitution",
      "phase": 1,
      "path": "constitution/core/phase-1-core-architecture/C02-backend-constitution.md",
      "hierarchy_rank": 3,
      "binds_implementation": true,
      "standards": [
        {
          "id": "S2.7",
          "title": "OpenAPI-first contract",
          "severity": "SEV1",
          "applies_to": "all backend services",
          "rule": "Every API endpoint must be defined in OpenAPI before the handler is implemented.",
          "rationale": "...",
          "anti_patterns": [
            { "id": "AP-S2.7a", "description": "Handler written before schema." }
          ]
        }
      ]
    }
  ],

  "implementations": [
    {
      "stack": "fastapi",
      "binds_constitution": "C02",
      "path": "constitution/implementation/fastapi/C02-backend-fastapi.md",
      "bindings": [
        {
          "binds_standard": "S2.7",
          "id": "S2.7/fastapi",
          "binding": "Use FastAPI's automatic OpenAPI generation via Pydantic models.",
          "anti_pattern": "AP-S2.7a/fastapi"
        }
      ]
    }
  ],

  "domains": [],

  "runbooks": [
    {
      "id": "RB-01",
      "name": "SEV0 Response",
      "path": "governance/runbooks/RB-01-sev0-response.md",
      "trigger": "Production down or data at risk"
    }
  ],

  "adrs": [
    {
      "id": "ADR-001",
      "name": "FundsLink Stack",
      "path": "governance/decisions/ADR-001-fundslink-stack.md",
      "status": "ACCEPTED"
    }
  ],

  "hierarchy": ["C00", "C03", "C02", "C05", "C04", "C06", "C01", "C07", "C08", "C09", "C10"],

  "phases": {
    "0": ["C01"],
    "1": ["C02", "C03", "C04", "C05", "C06"],
    "2": ["C07", "C08"],
    "3": ["C09", "C10"]
  },

  "integrity": {
    "standard_references_resolved": 0,
    "anti_pattern_references_resolved": 0,
    "link_references_resolved": 0,
    "warnings": [],
    "errors": []
  }
}
```

---

## A.5 — Parser strategy

Standards in current constitutions appear in three observed formats:

1. **Heading-based:** `### S1.1 — Standard title` followed by an attribute table
2. **Table-based:** Markdown tables with `**Standard**`, `**Rule**`, `**Rationale**` columns
3. **Code-block listings:** `S{C}.{N}` enumerated inside code blocks (rare)

### Parser approach

- Walk the markdown AST, not regex on raw text
- For each heading matching `S{C}.{N} — {title}`: extract the following block until the next heading of same or higher level
- For tables with a recognised standard schema: extract rows
- Reject ambiguous structures → log warning → fail validation if `--strict`

### Normalisation rule (LOCKED)

**Per locked decision D6**: if a constitution's format cannot be handled by the parser, **STOP and ask** before any edit. No silent normalisation. Each format quirk gets either:

- A parser enhancement (preferred — zero content edits)
- An explicit per-file approval request to the L4 approver with a diff preview

This adds parser engineering cost but preserves the L3 boundary absolutely.

---

## A.6 — Build sequence

| # | Sub-step | Output | Gate |
|---|----------|--------|------|
| A.1 | Create branch `refactor/phase-a-constitution-as-data` off `Dev` | Branch | After PR #5 merged ✓ |
| A.2 | Set up `uv` workspace at repo root | `pyproject.toml`, `uv.lock` | — |
| A.3 | Write Pydantic v2 schema models (`scripts/schema.py`) | Models + JSON Schema export | — |
| A.4 | Write parser core (`scripts/compile-constitution.py`) | First successful parse of C00, C01 | Eyeball output |
| A.5 | Add parsers for C02–C10 incrementally | Full compiled index for core | Each constitution validated |
| A.6 | Add implementation/binding parsers | All 4 stack bindings parsed | — |
| A.7 | Add anti-pattern + runbook + ADR + index parsers | Complete compiled index | — |
| A.8 | Write `validate-integrity.py` v2 (incl. link integrity) | Validator | Must pass on `compiled/constitution.json` |
| A.9 | Wire `generate-schemas.py` | TS + Py types in `platform/shared/` | TS compiles under `tsc --strict` |
| A.10 | Add pre-commit hooks + GitHub Action | Auto-run on push and PR | CI green |
| A.11 | Write `ADR-005-constitution-as-data.md` | ADR | — |
| A.12 | Append amendments-log entry | Log entry | — |
| A.13 | Open PR → `Dev` | PR with all deliverables | L4 approval |

---

## A.7 — Definition of Done

- [ ] `uv run python scripts/compile-constitution.py` produces `compiled/constitution.json` with **every** `S{C}.{N}` in the repo represented
- [ ] `uv run python scripts/validate-integrity.py` exits 0 on the compiled output
- [ ] `uv run python scripts/validate-integrity.py --strict` exits non-zero if any orphaned `S{C}.{N}` reference exists
- [ ] Validator catches markdown link integrity failures (broken `[text](path)` links)
- [ ] `platform/shared/types-ts/index.d.ts` compiles under `tsc --noEmit --strict`
- [ ] `platform/shared/types-py/` imports cleanly in Python 3.12
- [ ] GitHub Action runs on PRs to `Dev`, blocks merge on integrity failure
- [ ] Pre-commit hooks run locally on every commit
- [ ] ADR-005 explains the decision
- [ ] Amendments log entry recorded
- [ ] Zero content edits to C00–C10 without explicit per-file L4 approval
- [ ] All commits authored as Maluleke Kurhula Success — zero AI attribution anywhere

---

## A.8 — Risks & open questions

| # | Risk / Question | Resolution |
|---|-----------------|------------|
| R1 | Some constitutions may use formats the parser can't handle | Per D6: stop, flag, ask. Never edit silently. |
| R2 | `compiled/constitution.json` will be ~50–200KB committed | Acceptable. Add to PR review checklist. |
| R3 | Schema versioning: what counts as breaking? | Defined in ADR-005: any removed field or renamed key. Additions are non-breaking. Bump `schema_version.minor` for additions, `.major` for breaking. |
| Q1 | Link integrity scope: only relative paths, or also anchors (`#section`)? | Default: relative paths only. Anchor checking added in a later iteration if needed. |
| Q2 | What happens if `constitution/domains/` is empty? | Parser returns `"domains": []`, validator warns (not errors). |
| Q3 | Should the parser also extract framework primitive content (severity model tables, permission model, etc.)? | Yes — extracted as `framework.primitives[*].content_summary` for surfaces that need them. |
| Q4 | Token still valid for pushing? | Confirmed at session start. Re-confirm before push at A.13. |

---

## A.9 — Out of scope for Phase A

Explicitly NOT in Phase A — these belong to later phases:

- ❌ CLI commands (Phase B)
- ❌ MCP server tools (Phase C)
- ❌ Real violation detection in code (Phase D + B)
- ❌ Score computation (Phase B uses A's output)
- ❌ Engine API endpoints (Phase F)
- ❌ Dashboard UI (Phase F)
- ❌ System Bible generation (Phase G — post-v1.0)
- ❌ Editing constitution content (forbidden absolutely)

---

*Phase A is the foundation. Every subsequent phase depends on the compiled index it produces being correct, stable, and typed. There is no shortcut around it.*

*Version 1.0 (draft) — 2026-05-24 — KSDRILL SA*
