"""governova-mcp — Model Context Protocol server for the Governova constitution.

Exposes the compiled constitutional index as live MCP tools so any AI tool
(Claude, Cursor, and others) can query standards, anti-patterns, and bindings —
and run reliable-tier violation checks — at runtime, instead of reading stale
static files. This is the most defensible surface (GOVERNOVA-STRATEGY §3): the
constitution becomes a living, queryable system.

The tool logic lives in pure functions (see `core`) so it is unit-testable without
an MCP client; `__main__` wraps them as FastMCP tools.
"""
