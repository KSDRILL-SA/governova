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
from dataclasses import dataclass, field
from enum import StrEnum

from governova_compile.schema import CompiledIndex, Standard
from governova_compile.writer import load_active_index

from governova_semantic.client import SemanticUnavailableError, Transport, default_transport
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


class Outcome(StrEnum):
    """What actually happened, as distinct from what was found.

    This tier degrades silently by design — an advisory check that fails a build over
    a typo'd secret is a worse product, and REQ-008 fixes that. But *silent* and
    *invisible* are different things, and conflating them cost two releases: an
    unreachable endpoint, a rejected token, and a clean review all produced zero
    findings, so a green build was not evidence the tier had run at all.

    The outcome is reported; the build result still never changes.
    """

    INACTIVE = "inactive"
    """No endpoint, key, or model configured. The tier is off, deliberately."""

    NOT_GROUNDED = "not-grounded"
    """No standard was relevant to this code, so nothing was asked."""

    REVIEWED = "reviewed"
    """The endpoint answered. Findings are the real answer, including none."""

    UNAVAILABLE = "unavailable"
    """The endpoint did not answer. **Zero findings here means nothing.**"""


@dataclass(frozen=True)
class ReviewResult:
    """A review's findings *and* whether the review happened."""

    outcome: Outcome
    findings: list[SemanticFinding] = field(default_factory=list)
    detail: str = ""
    """Human-readable diagnosis. Never contains a URL, a key, or any part of either."""

    status: int | None = None
    """HTTP status when the endpoint answered with one. Safe to log; carries no secret."""

    @property
    def ran(self) -> bool:
        """True only when the endpoint actually answered.

        The property every caller should branch on before treating an empty finding
        list as a clean review.
        """
        return self.outcome is Outcome.REVIEWED


def _all_standards(index: CompiledIndex) -> list[Standard]:
    return [s for c in index.constitutions for s in c.standards]


ALWAYS_GROUNDED: tuple[str, ...] = ("S1.106", "S1.107")
"""Standards with **no lexical signature**, submitted on every review.

Word overlap cannot select these, and no amount of scoring will change that: duplication
and speculative generality are *structural* properties of code, not vocabulary in it.
`S1.106` ("Don't Repeat Yourself") and `S1.107` ("The Simplest Correct Solution") are
aphorisms whose words never appear in the code they govern.

That made them the most expensive possible gap, because both are **deliberately left to
the semantic tier precisely because they have no deterministic signature** — so a
lexical pre-filter guaranteed the tier could never reach the two standards it exists for.
Found by the evaluation harness on its first run against a perfect backend, which scored
0.5 recall with nothing wrong with the backend.

Kept as a short explicit list rather than inferred. Any inference would be a guess about
which standards lack a signature, and the list is small because the property is rare.
"""


def relevant_standards(index: CompiledIndex, code: str, limit: int = 12) -> list[Standard]:
    """Pick the standards most likely relevant to `code`, and submit only those.

    A cheap, deterministic pre-filter that keeps the prompt grounded and bounded. It is
    also a **ceiling on the tier's recall** — a standard this never selects cannot be
    found, however good the model is — which is why `ALWAYS_GROUNDED` exists.
    """
    tokens = set(_WORD.findall(code.lower()))
    scored: list[tuple[int, Standard]] = []
    for s in _all_standards(index):
        title_words = set(_WORD.findall(s.title.lower()))
        overlap = len(title_words & tokens)
        if overlap:
            scored.append((overlap, s))
    scored.sort(key=lambda t: (-t[0], t[1].id))
    selected = [s for _, s in scored[:limit]]

    chosen = {s.id for s in selected}
    unconditional = [
        s for s in _all_standards(index) if s.id in ALWAYS_GROUNDED and s.id not in chosen
    ]
    return [*selected, *unconditional]


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


def review_result(
    code: str,
    standards: list[Standard] | None = None,
    *,
    index: CompiledIndex | None = None,
    config: SemanticConfig | None = None,
    transport: Transport | None = None,
) -> ReviewResult:
    """Run an advisory semantic review of `code`, reporting what happened.

    Never raises and never changes a build result (REQ-008) — but it always says
    which of the four outcomes occurred, so an empty finding list can be read
    correctly instead of being mistaken for a clean review.
    """
    cfg = config or from_env()
    if not cfg.is_configured:
        return ReviewResult(
            outcome=Outcome.INACTIVE,
            detail="no endpoint, model, or key configured — set GOVERNOVA_LLM_*",
        )
    idx = index or load_active_index()
    grounded = standards if standards is not None else relevant_standards(idx, code)
    if not grounded:
        return ReviewResult(
            outcome=Outcome.NOT_GROUNDED,
            detail="no standard matched this code, so none was submitted for review",
        )
    messages = build_messages(code, grounded)
    send = transport or default_transport
    try:
        content = send(cfg, messages)
    except SemanticUnavailableError as exc:
        # The tier degrades rather than failing. What changed is that it now says so.
        return ReviewResult(
            outcome=Outcome.UNAVAILABLE,
            detail=str(exc),
            status=getattr(exc, "status", None),
        )
    allowed = {s.id.upper() for s in grounded}
    findings = parse_findings(content, allowed)
    return ReviewResult(
        outcome=Outcome.REVIEWED,
        findings=findings,
        detail=f"reviewed against {len(grounded)} grounded standard(s)",
    )


def review(
    code: str,
    standards: list[Standard] | None = None,
    *,
    index: CompiledIndex | None = None,
    config: SemanticConfig | None = None,
    transport: Transport | None = None,
) -> list[SemanticFinding]:
    """Findings only. Prefer `review_result` — an empty list here is ambiguous.

    Kept because callers that genuinely only want findings should not have to unpack
    an outcome they will ignore. Anything reporting to a human should use
    `review_result` and branch on `.ran`.
    """
    return review_result(
        code, standards, index=index, config=config, transport=transport
    ).findings
