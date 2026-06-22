# Governova — CLI (second surface)

**Status:** Alpha — working (v0.1)
**Surface:** `governova` command · the glue surface (GOVERNOVA-PRODUCT §6.2)

The unified developer CLI. It **wraps the engine** (`governova_compile` / `governova_validate`)
into one command and reads the compiled index — the single source of truth — never markdown.

## Implementation

The CLI lives in the engine's uv workspace as the `governova_cli` package
(`scripts/governova_cli/`), exposed as the `governova` console script in
`scripts/pyproject.toml`. This keeps it a thin, zero-duplication wrapper over the engine.

```bash
# in the workspace (uv sync --all-packages), then:
governova stats
governova standards --constitution C03
governova standard S3.14
governova validate --strict
governova compile --check
governova score
```

| Command | Purpose |
|---------|---------|
| `stats` | Summary: constitutions, standards, anti-patterns, bindings, runbooks, ADRs |
| `standards [-c C0N]` | List standards, optionally filtered to one constitution |
| `standard <id>` | Show one standard: statement, rationale, anti-patterns |
| `validate [--strict]` | Run the engine's integrity checks; exit-coded for CI |
| `compile [--check]` | Compile the index, or drift-check the committed one |
| `score` | **Constitution Health Score (0–100)** — integrity + anti-pattern + rationale coverage |

## Note

`score` reports the **Constitution Health Score** — the health of the constitutional
database itself (completeness + integrity). It is distinct from a *project's* Governova
Score (GOVERNOVA-MASTER §18.1), which weights runtime violations, relay compliance, and
audit-trail completeness and is computed by the platform engine over a governed project.
