# Governova Scripts

The build tooling for the constitutional database. Three executables, all installed via the uv workspace.

| Command | Module | Purpose |
|---------|--------|---------|
| `governova-compile` | `governova_compile` | Parse every markdown constitution into `compiled/constitution.json` |
| `governova-validate` | `governova_validate` | Validate the compiled index — references, anti-patterns, hierarchy, links |
| `governova-codegen` | `governova_codegen` | Emit TypeScript types and Python re-export package from the schema |

## Quick start

```bash
# Bootstrap the workspace (from repo root)
uv sync

# Compile the constitutional database
uv run governova-compile

# Validate the compiled index
uv run governova-validate

# Validate strictly (fail on any warning)
uv run governova-validate --strict

# Regenerate TypeScript + Python types
uv run governova-codegen
```

## Outputs

| Path | Description |
|------|-------------|
| `compiled/constitution.json` | The compiled index (committed) |
| `compiled/constitution.schema.json` | JSON Schema describing the index (committed) |
| `compiled/checksum.txt` | SHA-256 of the index for tamper detection (committed) |
| `platform/shared/types-ts/src/index.ts` | TypeScript type definitions (generated) |
| `platform/shared/types-py/governova_types/models.py` | Python Pydantic re-exports (generated) |

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Compilation error (file not found, parse failure) |
| 2 | Validation error (strict mode triggered, integrity failure) |
| 3 | Codegen error (TS compilation, schema mismatch) |

## Tests

```bash
uv run pytest scripts/tests/
```

## Development

```bash
uv run ruff format .
uv run ruff check . --fix
uv run mypy scripts/
```

---

*All scripts are Layer 1 tooling — they read constitutions, never write them.*
