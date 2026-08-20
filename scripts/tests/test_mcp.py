"""Tests for the MCP server's query/check logic (pure core, no MCP client needed)."""

from __future__ import annotations

from governova_mcp import core


def test_list_constitutions():
    cons = core.list_constitutions()
    assert len(cons) == 15
    assert all("standards" in c for c in cons)


def test_get_standard():
    s = core.get_standard("S3.14")
    assert s is not None
    assert s["id"] == "S3.14"
    assert s["statement"]


def test_get_standard_missing():
    assert core.get_standard("S99.99") is None


def test_search_standards():
    hits = core.search_standards("token")
    assert any(h["id"] == "S3.14" for h in hits)


def test_get_binding_spring_boot():
    b = core.get_binding("spring-boot", "S2.1")
    assert b is not None
    assert b["stack"] == "spring-boot"
    assert b["binds_standard"] == "S2.1"


def test_check_text_flags_localstorage_token():
    findings = core.check_text("localStorage.setItem('access_token', t);")
    assert any(f["anti_pattern"] == "AP-S3.14a" for f in findings)
    assert all(f["advisory"] for f in findings)


def test_check_text_clean_code_has_no_findings():
    assert core.check_text("const sum = a + b;") == []


def test_constitution_health():
    h = core.constitution_health()
    assert 0 <= h["score"] <= 100
    assert h["standards"] == 670


# ─── The server wiring itself ────────────────────────────────────────────────
#
# Everything above tests `core`, which is deliberately free of MCP. That split
# makes the tools unit-testable — and it also meant **the surface that actually
# talks to the MCP library had no test at all.** When `mcp` 2.0 removed
# `mcp.server.fastmcp`, nothing in this suite could notice: an unbounded floor
# resolved to 2.0.0, the import died at startup, and every test still passed.
#
# These exercise the wiring. They are cheap, and they are the ones that fail on
# the next breaking release instead of a user discovering it.


def test_the_server_exposes_every_core_tool():
    """The registry, not the module. A decorator that silently stopped registering
    would leave the functions importable and the server empty."""
    import asyncio

    from governova_mcp.__main__ import mcp

    tools = asyncio.run(mcp.list_tools())
    assert {t.name for t in tools} == {
        "list_constitutions",
        "get_standard",
        "search_standards",
        "get_anti_pattern",
        "get_binding",
        "check_text",
        "constitution_health",
    }
    assert mcp.name == "governova"


def test_every_exposed_tool_describes_itself():
    """An MCP client shows the description to a model choosing between tools, so an
    undescribed tool is a tool that does not get called."""
    import asyncio

    from governova_mcp.__main__ import mcp

    for tool in asyncio.run(mcp.list_tools()):
        assert tool.description, f"{tool.name} has no description"


def test_a_tool_answers_through_the_server():
    """End to end through the MCP call path rather than the Python function, because
    the failure this guards against is in the wiring, not the logic."""
    import asyncio

    from governova_mcp.__main__ import mcp

    result = asyncio.run(mcp.call_tool("get_standard", {"standard_id": "S3.14"}))
    assert result, "the server returned nothing for a standard that exists"
