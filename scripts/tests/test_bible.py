"""Tests for the System Bible (governova_bible)."""

from __future__ import annotations

import json

from governova_bible import build_bible, extract_file, to_json, to_markdown

PY = '''\
"""This module does an important thing.

More detail here.
"""
import os
from collections import OrderedDict


def public_fn():
    pass


def _private_fn():
    pass


class Widget:
    pass
'''

TS = """\
// Loads the thing and exposes typed helpers.
// Second line of the comment.
import { foo } from "./helpers";
const bar = require("lib");

export function doThing() {}
export class Service {}
"""


def test_extract_python(tmp_path):
    p = tmp_path / "mod.py"
    p.write_text(PY, encoding="utf-8")
    e = extract_file(p, tmp_path)
    assert e.language == "Python"
    assert "important thing" in e.purpose
    assert "public_fn" in e.public and "Widget" in e.public
    assert "_private_fn" not in e.public  # privates excluded
    assert "os" in e.dependencies and "collections" in e.dependencies


def test_extract_typescript(tmp_path):
    p = tmp_path / "svc.ts"
    p.write_text(TS, encoding="utf-8")
    e = extract_file(p, tmp_path)
    assert e.language == "TypeScript"
    assert "Loads the thing" in e.purpose
    assert "doThing" in e.public and "Service" in e.public
    assert "./helpers" in e.dependencies and "lib" in e.dependencies


def test_build_bible_on_repo():
    sb = build_bible()
    assert sb.total_files > 10
    assert sb.total_loc > 0
    assert sb.documented_pct > 50  # the engine is well documented
    assert "scripts" in sb.by_area()


def test_renderers(tmp_path):
    p = tmp_path / "mod.py"
    p.write_text(PY, encoding="utf-8")
    sb = build_bible(tmp_path)
    md = to_markdown(sb)
    assert "System Bible" in md and "mod.py" in md
    data = json.loads(to_json(sb))
    assert data["total_files"] == 1 and data["files"][0]["path"] == "mod.py"
