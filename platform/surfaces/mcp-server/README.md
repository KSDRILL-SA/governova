# Governova — MCP Server (live governance for AI tools)

**Status:** Alpha — working (v0.1)
**Surface:** Model Context Protocol (stdio) · the most defensible surface (GOVERNOVA-STRATEGY §3, MASTER §17.9)

Exposes the compiled constitutional index as **live MCP tools**, so any MCP-capable AI
tool (Claude Desktop, Cursor, and others) queries the constitution **at runtime** instead
of reading stale static files. This is what makes the constitutional database a living,
queryable system — the part hardest for a competitor to copy.

## Implementation

Lives in the engine's uv workspace as `governova_mcp` (`scripts/governova_mcp/`), exposed
as the `governova-mcp` console script (stdio transport). Built on the MCP Python SDK
(FastMCP). Tool logic is pure and unit-tested in `governova_mcp.core`.

## Tools

| Tool | Purpose |
|------|---------|
| `list_constitutions` | Every constitution with phase + standard count |
| `get_standard(id)` | One standard in full: statement, rationale, anti-patterns |
| `search_standards(query, limit)` | Search by id / title / statement |
| `get_anti_pattern(id)` | An anti-pattern and the standard it violates |
| `get_binding(stack, standard)` | How a standard is satisfied in a stack (e.g. `spring-boot`, `S2.1`) |
| `check_text(code)` | **Reliable-tier, advisory** violation checks on a snippet (never a hard block) |
| `constitution_health()` | Constitution Health Score (0–100) |

## Configure an AI client

```jsonc
// e.g. Claude Desktop / Cursor MCP config
{
  "mcpServers": {
    "governova": { "command": "governova-mcp" }
  }
}
```

(Run `uv sync --all-packages` in `scripts/` so `governova-mcp` is on PATH.)

## Discipline

`check_text` is **deterministic and advisory only** (GOVERNOVA-STRATEGY §11.2) — a
"review this" signal, never a blocking gate. Semantic/intent detection is reserved for the
CI/PR surfaces. The server reads the committed index; run `governova compile` after
constitution changes.
