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
from typing import Any

from governova_compile.schema import CompiledIndex, Standard
from governova_compile.writer import load_active_index

from governova_semantic.client import (
    SemanticUnavailableError,
    Transport,
    default_transport,
)
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

    UNPARSEABLE = "unparseable"
    """The endpoint answered, and the answer carried no readable verdict.

    Distinct from `REVIEWED` with no findings, which is a clean review, and distinct
    from `UNAVAILABLE`, which is a dead endpoint. Collapsing this into either is how a
    tier reports confidence it never earned.

    The case that made it concrete: a reasoning model spends its token budget on an
    internal `reasoning` field and returns `content: ""`. Nothing errors, the HTTP status
    is 200, and a build goes green on a review that produced no answer. Raising
    `GOVERNOVA_LLM_MAX_TOKENS` is usually the fix — which is only discoverable if the
    outcome says so.
    """


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


def declares_semantic_tier(standard: Standard) -> bool:
    """Whether a standard names the semantic tier as one of its enforcement paths.

    Read from `enforced_by`, which the standard's author writes. This is a *declaration*,
    not a measurement, and it deliberately feeds no score — coverage is computed from
    `RULES`, so adding a standard to this tier cannot inflate any published number.
    """
    return any("semantic" in path.lower() for path in standard.enforced_by)


def semantic_pool(index: CompiledIndex) -> list[Standard]:
    """The standards this tier exists to check, in index order.

    **The pool is declared, not inferred.** The previous implementation ranked all 670
    standards by word overlap between their titles and the identifiers in the code, and
    submitted the top twelve. On a loan-assessment handler every one of those twelve
    matched on a single incidental token — `async` selected "Async Standup Replaces
    Synchronous Daily Meetings", `post` selected "Post-Merge Cleanup Is Mandatory", `debt`
    selected "The System Maintains a Debt Register" — while `S1.103` and `S1.105`, which
    the code actually violated, scored zero and were never submitted at all.

    That is not a filter that needs better weighting. Code identifiers and standard titles
    are different vocabularies, and the standards this tier is *for* are the ones whose
    words provably never appear in the code they govern: whether a unit has one concern,
    whether an abstraction is speculative, whether two blocks are the same logic. No
    lexical score can select those, which is why the old implementation carried a
    hardcoded `ALWAYS_GROUNDED` list for the two it most obviously missed — a patch on a
    mechanism that was wrong rather than incomplete.

    So the pool is whatever declares `semantic tier` in `enforced_by`. That makes the
    tier's scope explicit and auditable, puts it under the same review as any other change
    to the corpus, and makes reachability a property that can be asserted in CI instead of
    an emergent accident of vocabulary.
    """
    return [s for s in _all_standards(index) if declares_semantic_tier(s)]


def _signature(standard: Standard) -> set[str]:
    """Every word that could plausibly tie a standard to code that breaks it.

    Anti-pattern descriptions matter most here — they are written in terms of what the
    defect looks like ("implemented inside a UI component, route handler, or data-access
    call"), where the title is written in terms of the principle.
    """
    parts = [standard.title, standard.statement, *(a.description for a in standard.anti_patterns)]
    return set(_WORD.findall(" ".join(parts).lower()))


def relevant_standards(index: CompiledIndex, code: str, limit: int = 12) -> list[Standard]:
    """The standards submitted for review of `code`.

    The whole pool when it fits in the budget, which is the normal case and the one worth
    optimising for: a small declared pool means every standard the tier is responsible for
    is checked on every review, and recall has no pre-filter ceiling at all.

    Ranking only decides what to drop once the pool outgrows `limit`. It scores against the
    full signature rather than the title, and breaks ties by id so the selection is
    deterministic — but a pool large enough to need it has outgrown one prompt, and
    splitting the review is the better answer than silently discarding standards.
    """
    pool = semantic_pool(index)
    if len(pool) <= limit:
        return pool
    tokens = set(_WORD.findall(code.lower()))
    ranked = sorted(pool, key=lambda s: (-len(_signature(s) & tokens), s.id))
    return ranked[:limit]


def _catalogue_entry(standard: Standard) -> str:
    """One standard as the model sees it: the rule, then what breaking it looks like.

    **A statement alone is a prohibition without a stopping condition.** `S1.105` reads
    "values that carry meaning are named and sourced from configuration — never inlined as
    literals", and a model given only that will find something matching in almost any code,
    including code that already complies. Measured: `S1.105` and `S2.53` produced 12 of the
    false positives in a run scoring 33% precision, and both were reported against the
    fixtures written as their *negative* case — code doing exactly what the standard asks.

    The corpus already carries the missing half. An anti-pattern describes the concrete
    defect and, crucially, its contrast: `AP-S1.105a` is a literal inlined *"instead of
    named configuration"*, which exempts the named-constant case the statement appears to
    forbid. `AP-S2.53a` is a guard *"checking JWT role but not specific resource
    ownership"*, not any handler touching a user's data.

    Statements are written for humans applying judgement, and they are correct as written —
    this is a prompt-construction change, not a corpus change. (Distinct from the earlier
    experiment that fed anti-pattern text to the *grounding pre-filter*, which measured no
    improvement and was reverted; that filter no longer exists.)
    """
    entry = f"- {standard.id}: {standard.title} — {standard.statement}"
    for anti in standard.anti_patterns:
        entry += f"\n    Report only when: {anti.description}"
    return entry


def build_messages(code: str, standards: list[Standard]) -> list[dict[str, str]]:
    """Build the review prompt.

    The instruction to **withhold** is as important as the instruction to find, and was
    missing from the first version. Measured on `gpt-oss:120b`, the original prompt scored
    50–75% precision: the model found the real violations and could not resist adding
    marginal ones, because nothing asked it not to. A tier whose findings cannot be taken
    at face value is worse than no tier, so the prompt now states the asymmetry the bar
    encodes — a missed violation is cheaper than an invented one.
    """
    catalogue = "\n".join(_catalogue_entry(s) for s in standards)
    system = (
        "You are a constitutional code reviewer. You are given a set of governance "
        "standards and a code snippet. Identify only genuine violations of the listed "
        "standards. Respond with strict JSON: "
        '{"findings":[{"standard":"S<c>.<n>","line":<int or null>,"message":"<why>",'
        '"confidence":"high|medium|low"}]}. '
        "Cite only standards from the provided list. If there are no violations, return "
        '{"findings":[]}. Do not invent standards or wrap the JSON in prose.'
        "\n\n"
        "Report only violations you would defend in a code review. When a standard only "
        "arguably applies, or the code is a reasonable choice somebody made on purpose, "
        "report nothing for it. A missed violation costs little; a wrong one destroys "
        "trust in every other finding you make. Returning an empty list is a correct and "
        "expected answer for well-written code."
        "\n\n"
        "Set confidence honestly, because it is used rather than displayed. Use 'high' "
        "only when the code plainly does the thing the standard's 'Report only when' "
        "clause describes and you would defend the finding to the author. Use 'medium' "
        "when the standard arguably applies but a reasonable reviewer could disagree. Use "
        "'low' when it is a stretch. Anything below 'high' is discarded, so a finding you "
        "are unsure about costs you nothing to mark honestly."
    )
    user = f"Standards:\n{catalogue}\n\nCode:\n{code}"
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def payload(content: str) -> dict[str, Any] | None:
    """The JSON object the model was asked for, or None if the reply carried none.

    Separated from `parse_findings` because the two failures it distinguishes are
    otherwise identical and mean opposite things: **`{"findings": []}` is a clean
    review; an empty or unparseable reply is no review at all.** Collapsing both to an
    empty finding list is how a tier reports confidence it never earned.

    The case that made this concrete: a reasoning model spends its token budget on a
    `reasoning` field and returns `content: ""`. Nothing errors, nothing is logged, and
    the build goes green on a review that produced no answer.
    """
    text = content.strip()
    fence = _FENCE.search(text)
    if fence:
        text = fence.group(1).strip()
    try:
        data = json.loads(text)
    except ValueError:
        return None
    return data if isinstance(data, dict) else None


DISCARDED_CONFIDENCE = frozenset({"medium", "low"})
"""Confidence levels dropped before a finding is reported.

The same idea as the ungrounded-citation filter, applied to certainty rather than
to identity: the model is asked how sure it is, and anything it does not call
`high` is discarded. A marginal finding costs more than a missed one, because it
is the one that teaches a reader to discount the rest.

**An absent or unrecognised confidence is kept, not dropped.** A backend that
ignores the field would otherwise report nothing at all while looking like a
clean review — the precise failure `Outcome.UNPARSEABLE` exists to prevent, and
silently emptying the tier is worse than not filtering it. Keeping is also the
direction that cannot cost recall.
"""


def parse_findings(content: str, allowed_ids: set[str]) -> list[SemanticFinding]:
    """Parse the model's JSON, keeping only grounded, high-confidence findings."""
    data = payload(content)
    if data is None:
        return []
    raw = data.get("findings", [])
    out: list[SemanticFinding] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        std = str(item.get("standard", "")).strip().upper()
        if std not in allowed_ids:  # anti-hallucination: only grounded, real standards
            continue
        if str(item.get("confidence", "")).strip().lower() in DISCARDED_CONFIDENCE:
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
    if payload(content) is None:
        # A 200 carrying no readable verdict. Reporting this as a clean review would be
        # the same defect as reporting an unreachable endpoint as one.
        return ReviewResult(
            outcome=Outcome.UNPARSEABLE,
            detail=(
                "the endpoint answered but returned no readable JSON verdict "
                f"({len(content.strip())} char(s) of content) — a reasoning model may "
                f"need a larger GOVERNOVA_LLM_MAX_TOKENS"
            ),
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
    return review_result(code, standards, index=index, config=config, transport=transport).findings
