"""The semantic review itself: ground on relevant standards, prompt, parse, validate.

Discipline:
- Advisory only — these findings never block a build.
- Index-grounded — the model is given a specific set of real standards and told to
  cite only those; any citation outside that set is dropped (anti-hallucination).
- Inactive without configuration — returns no findings, so nothing depends on a key.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from governova_compile.discovery import resolve_repo_root
from governova_compile.schema import CompiledIndex, Standard
from governova_compile.writer import load_index

from governova_semantic.client import SemanticUnavailableError, Transport, urllib_transport
from governova_semantic.config import SemanticConfig, from_env

_WORD = re.compile(r"[a-z]{4,}")
_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.S)


@dataclass(frozen=True)
class SemanticFinding:
    standard: str
    message: str
    line: int | None = None
    tier: str = "semantic"
    advisory: bool = True


def _all_standards(index: CompiledIndex) -> list[Standard]:
    return [s for c in index.constitutions for s in c.standards]


def relevant_standards(index: CompiledIndex, code: str, limit: int = 12) -> list[Standard]:
    """Pick the standards most likely relevant to `code` by title-word overlap.

    A cheap, deterministic pre-filter that keeps the prompt grounded and bounded.
    """
    tokens = set(_WORD.findall(code.lower()))
    scored: list[tuple[int, Standard]] = []
    for s in _all_standards(index):
        title_words = set(_WORD.findall(s.title.lower()))
        overlap = len(title_words & tokens)
        if overlap:
            scored.append((overlap, s))
    scored.sort(key=lambda t: (-t[0], t[1].id))
    return [s for _, s in scored[:limit]]


def build_messages(code: str, standards: list[Standard]) -> list[dict[str, str]]:
    catalogue = "\n".join(f"- {s.id}: {s.title} — {s.statement}" for s in standards)
    system = (
        "You are a constitutional code reviewer. You are given a set of governance "
        "standards and a code snippet. Identify only genuine violations of the listed "
        "standards. Respond with strict JSON: "
        '{"findings":[{"standard":"S<c>.<n>","line":<int or null>,"message":"<why>"}]}. '
        "Cite only standards from the provided list. If there are no violations, return "
        '{"findings":[]}. Do not invent standards or wrap the JSON in prose.'
    )
    user = f"Standards:\n{catalogue}\n\nCode:\n{code}"
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def parse_findings(content: str, allowed_ids: set[str]) -> list[SemanticFinding]:
    """Parse the model's JSON and keep only citations of allowed (real) standards."""
    text = content.strip()
    fence = _FENCE.search(text)
    if fence:
        text = fence.group(1).strip()
    try:
        data = json.loads(text)
    except ValueError:
        return []
    raw = data.get("findings", []) if isinstance(data, dict) else []
    out: list[SemanticFinding] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        std = str(item.get("standard", "")).strip().upper()
        if std not in allowed_ids:  # anti-hallucination: only grounded, real standards
            continue
        line = item.get("line")
        line = int(line) if isinstance(line, (int, float)) else None
        message = str(item.get("message", "")).strip()
        if message:
            out.append(SemanticFinding(standard=std, message=message, line=line))
    return out


def review(
    code: str,
    standards: list[Standard] | None = None,
    *,
    index: CompiledIndex | None = None,
    config: SemanticConfig | None = None,
    transport: Transport | None = None,
) -> list[SemanticFinding]:
    """Run an advisory semantic review of `code`. Returns [] when inactive or on error."""
    cfg = config or from_env()
    if not cfg.is_configured:
        return []  # inactive — nothing is configured
    idx = index or load_index(resolve_repo_root() / "compiled" / "constitution.json")
    grounded = standards if standards is not None else relevant_standards(idx, code)
    if not grounded:
        return []
    messages = build_messages(code, grounded)
    send = transport or urllib_transport
    try:
        content = send(cfg, messages)
    except SemanticUnavailableError:
        return []  # degrade gracefully — the reliable tier is unaffected
    allowed = {s.id.upper() for s in grounded}
    return parse_findings(content, allowed)
