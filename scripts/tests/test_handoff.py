"""Tests for the handoff generator (governova_handoff)."""

from __future__ import annotations

import pytest
from governova_handoff import STAGES, build_handoff, stages, to_markdown


def test_stages_are_dependency_ordered():
    order = stages()
    assert order[0] == "foundation"
    assert order.index("database") < order.index("backend") < order.index("frontend")
    # Every dependency precedes the stage that depends on it.
    for stage, spec in STAGES.items():
        for dep in spec["depends_on"]:
            assert STAGES[dep]["order"] < spec["order"], (stage, dep)


def test_build_handoff_backend_is_grounded():
    h = build_handoff("backend")
    assert h.stage == "backend"
    assert any(a.constitution_id == "C02" for a in h.areas)  # backend constitution
    assert "auth" in h.depends_on and "database" in h.depends_on
    assert h.areas[0].standards > 0 and h.areas[0].key_standards


def test_unknown_stage_raises():
    with pytest.raises(KeyError):
        build_handoff("nonsense")


def test_markdown_brief_contains_guidance():
    md = to_markdown(build_handoff("database"))
    assert "Engineer Handoff — Database" in md
    assert "What you must NOT touch" in md
    assert "Build → Harden → Self-review → External-review → Handoff" in md
    assert "C05" in md  # database constitution cited


def test_foundation_has_no_dependencies():
    h = build_handoff("foundation")
    assert h.depends_on == [] and h.order == 0
