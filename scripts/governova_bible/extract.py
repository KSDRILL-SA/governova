"""Per-file extraction: purpose, public surface, and dependencies.

Python is parsed with the AST for accuracy; other languages use conservative
heuristics (leading comment block + simple export/import patterns).
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

from governova_bible.model import FileEntry

LANGUAGES: dict[str, str] = {
    ".py": "Python", ".ts": "TypeScript", ".tsx": "TypeScript", ".js": "JavaScript",
    ".jsx": "JavaScript", ".mjs": "JavaScript", ".cjs": "JavaScript", ".vue": "Vue",
    ".svelte": "Svelte", ".java": "Java", ".kt": "Kotlin", ".go": "Go", ".rb": "Ruby",
    ".php": "PHP", ".rs": "Rust", ".cs": "C#", ".swift": "Swift", ".dart": "Dart",
    ".css": "CSS", ".scss": "SCSS",
}


def detect_language(path: Path) -> str:
    return LANGUAGES.get(path.suffix.lower(), path.suffix.lstrip(".").upper() or "text")


def _first_paragraph(text: str) -> str:
    para: list[str] = []
    for line in text.strip().splitlines():
        if not line.strip():
            if para:
                break
            continue
        para.append(line.strip())
    return " ".join(para).strip()


def _extract_python(text: str) -> tuple[str, list[str], list[str]]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return "", [], []
    purpose = _first_paragraph(ast.get_docstring(tree) or "")
    public: list[str] = []
    deps: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if not node.name.startswith("_"):
                public.append(node.name)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                deps.add(a.name.split(".", 1)[0])
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            deps.add(node.module.split(".", 1)[0])
    return purpose, public, sorted(deps)


_LEADING_COMMENT = re.compile(r"^\s*(//|#|\*|/\*\*?|\*/)")
_EXPORT = re.compile(
    r"\bexport\s+(?:default\s+)?(?:async\s+)?(?:function|class|const|interface|type|enum)\s+([A-Za-z_$][\w$]*)"
)
_DECL = re.compile(r"\b(?:public\s+)?(?:function|class)\s+([A-Za-z_$][\w$]*)")
_IMPORT_FROM = re.compile(r"""\bfrom\s+['"]([^'"]+)['"]""")
_REQUIRE = re.compile(r"""\brequire\(\s*['"]([^'"]+)['"]\s*\)""")


def _extract_generic(text: str) -> tuple[str, list[str], list[str]]:
    lines = text.splitlines()
    # Leading comment block as purpose.
    comment: list[str] = []
    for line in lines:
        if not line.strip():
            if comment:
                break
            continue
        if _LEADING_COMMENT.match(line):
            cleaned = re.sub(r"^\s*(/\*\*?|\*/|//|#|\*)\s?", "", line).strip()
            if cleaned:
                comment.append(cleaned)
        else:
            break
    purpose = _first_paragraph("\n".join(comment))

    public: list[str] = []
    for pat in (_EXPORT, _DECL):
        for m in pat.finditer(text):
            if m.group(1) not in public:
                public.append(m.group(1))
    deps = sorted({m.group(1) for m in _IMPORT_FROM.finditer(text)} | {
        m.group(1) for m in _REQUIRE.finditer(text)
    })
    return purpose, public, deps


def extract_file(path: Path, root: Path) -> FileEntry:
    text = path.read_text(encoding="utf-8", errors="replace")
    loc = sum(1 for line in text.splitlines() if line.strip())
    lang = detect_language(path)
    if lang == "Python":
        purpose, public, deps = _extract_python(text)
    else:
        purpose, public, deps = _extract_generic(text)
    rel = path.resolve().relative_to(root.resolve()).as_posix()
    return FileEntry(
        path=rel,
        language=lang,
        loc=loc,
        purpose=purpose,
        public=public[:30],
        dependencies=deps[:30],
    )
