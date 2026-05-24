# ADR-005 — Constitution as Data

---

| Attribute   | Value |
|-------------|-------|
| **ID**      | ADR-005 |
| **Date**    | 2026-05-24 |
| **Status**  | accepted |
| **Supersedes** | — |
| **Relates To** | C0 §3 (Standard Format Specification), C0 §5.1 (Constitution Register), `framework/format-specification.md` |

---

## Context

The constitutional database existed only as markdown. Every Governova surface — the
CLI, the MCP server, the CI/CD enforcer, the IDE extension, the engine, the dashboard —
needs to query standards, anti-patterns, the hierarchy, and the phase map
programmatically. Re-parsing markdown in five languages across six surfaces would
guarantee drift: each surface would interpret the format slightly differently, and a
change to one constitution would silently break consumers.

Phase A of the build plan (`planning/phase-a-spec.md`) requires a single,
machine-readable, integrity-validated, typed representation of the constitution that
every surface imports — compiled once, consumed everywhere.

Two further constraints shaped the decision:

1. The build is split-stack: a TypeScript CLI/MCP/extension and a Python (FastAPI)
   engine (ADR-001/003 lineage). Both must agree on the exact shape of every record.
2. Locked decision D6 forbids editing constitution content to suit the tooling. The
   parser must adapt to the constitutions as written, not the reverse.

---

## Decision

**Python is the single source of truth for the compiled-index schema.** A Pydantic v2
model (`scripts/governova_compile/schema.py`) defines every record. From it flow three
artifacts, all generated and committed:

1. `compiled/constitution.json` — the compiled index (594 standards, anti-patterns,
   practices, runbooks, ADRs, hierarchy, phase map).
2. `compiled/constitution.schema.json` — JSON Schema (draft 2020-12) exported from the
   Pydantic model.
3. Generated types: `platform/shared/types-ts/` (TypeScript, via
   `json-schema-to-typescript`) and `platform/shared/types-py/` (Python, vendored from
   the schema). Every surface imports from one of these — none re-parses markdown.

The compiled artifact is **committed** (D7) so consumers pin a version without running
the parser. Integrity is enforced by `governova-validate` and a GitHub Action on every
PR to `Dev`/`main`.

This option was chosen over generating types from a hand-written JSON Schema (which
would drift from the models) and over a TypeScript source of truth (which would not
serve the Python engine natively).

---

## Consequences

### What becomes easier

- Every surface reads one typed artifact; no surface re-implements markdown parsing.
- A change to the constitution recompiles to a new fingerprint; CI catches stale indexes.
- The reference graph (depends-on, cross-references, anti-patterns) is queryable.
- Independent validation: the parser arrives at exactly 594 standards, matching the
  count C0 §5.1 declares — a self-checking signal that nothing was dropped.

### What becomes harder

- The parser must handle every standard-authoring format the constitutions use (full
  `### S{C}.{N}` blocks, blockquote shorthand `> **S{C}.{N}** — …`, range/group
  headings, and prose/table/checklist content). New formats require parser work, not
  constitution edits.
- The committed artifacts add review surface; the checksum is a content fingerprint
  (it excludes volatile build metadata) so re-compiles do not churn the diff.

### Constitutional alignment

- Aligns with C0 §3 (the format specification the parser targets) and C0 §5.1 (the
  register the standard count is validated against).
- No constitution content was edited (D6). Where the constitutions are incomplete
  against C0 §3.2 (SR-2 rationale required, SR-3 anti-pattern required), the validator
  surfaces SEV3 warnings rather than altering the source.

---

## Alternatives Considered

| Option | Why Rejected |
|--------|-------------|
| Hand-written JSON Schema as source of truth | Would drift from the Python models the engine uses; two things to keep in sync. |
| TypeScript source of truth (CLI-first) | The FastAPI engine would need a second, hand-maintained Python model. |
| No committed artifact (compile on demand) | Every consumer would need the Python toolchain installed; no stable pinned version. |
| Re-parse markdown per surface | Guaranteed drift across six surfaces and two languages. |

---

## Schema versioning

`SCHEMA_VERSION` is semantic. Adding an optional field is a minor bump; removing,
renaming, or changing the type of a field is a major bump and forces every consumer to
update. The version is embedded in every compiled index.

---

> **Status: ACCEPTED — 2026-05-24**  
> *Owner approval: Maluleke Kurhula Success*
