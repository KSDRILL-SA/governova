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
    assert h["standards"] == 667
