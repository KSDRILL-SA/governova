"""`governova-mcp` — FastMCP server exposing the constitution as live tools.

Run over stdio (the standard MCP transport):
    governova-mcp
or:
    python -m governova_mcp

Configure an AI client (Claude Desktop / Cursor / etc.) to launch this command;
the constitution then answers live queries instead of the tool reading stale files.
"""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from governova_mcp import core

mcp = FastMCP("governova")


@mcp.tool()
def list_constitutions() -> list[dict[str, Any]]:
    """List every constitution with its phase and standard count."""
    return core.list_constitutions()


@mcp.tool()
def get_standard(standard_id: str) -> dict[str, Any]:
    """Get one standard in full by id (e.g. 'S3.14'): statement, rationale, anti-patterns."""
    result = core.get_standard(standard_id)
    return result or {"error": f"{standard_id} not found"}


@mcp.tool()
def search_standards(query: str, limit: int = 20) -> list[dict[str, Any]]:
    """Search standards by id, title, or statement text (case-insensitive)."""
    return core.search_standards(query, limit)


@mcp.tool()
def get_anti_pattern(anti_pattern_id: str) -> dict[str, Any]:
    """Get an anti-pattern by id (e.g. 'AP-S3.14a') and the standard it violates."""
    result = core.get_anti_pattern(anti_pattern_id)
    return result or {"error": f"{anti_pattern_id} not found"}


@mcp.tool()
def get_binding(stack: str, standard_id: str) -> dict[str, Any]:
    """Get how a standard is satisfied in a stack, e.g. get_binding('spring-boot','S2.1')."""
    result = core.get_binding(stack, standard_id)
    return result or {"error": f"no {stack} binding for {standard_id}"}


@mcp.tool()
def check_text(code: str) -> list[dict[str, Any]]:
    """Run reliable-tier (deterministic, advisory) constitutional checks on a code snippet.

    Returns findings linked to their anti-pattern and standard. Advisory only — this is
    a 'review this' signal, never a hard block (GOVERNOVA-STRATEGY §11.2).
    """
    return core.check_text(code)


@mcp.tool()
def constitution_health() -> dict[str, Any]:
    """Constitution Health Score (0-100) for the constitutional database itself."""
    return core.constitution_health()


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
