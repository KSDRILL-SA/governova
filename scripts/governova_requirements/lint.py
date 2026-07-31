"""The requirements linter — the canon's grammar, as deterministic checks.

The canon specifies a *grammar*, not a philosophy:

    <Req ID> The <system> <shall|must|should|may> <function>.

Unique IDs, one idea per requirement, quantified thresholds, and an explicit
banned-word list. Every rule here is decidable by someone other than its author, which
is the filter `protocols/practice-to-standard.md` §3 applies. Judgement — is this
requirement *feasible*, was the right elicitation technique used — is deliberately
absent, because a check that cannot be adjudicated becomes a lever for whoever argues
hardest.

Two disciplines shape every rule:

**A rule that cannot see the text returns nothing, never a violation.** At tier 1 the
statement lives in a tracker Governova never calls. Absent text is `unknown`.

**Every quantifier is bounded**, and statements are length-capped before matching. An
unbounded quantifier once cost 8.7 seconds on a single line in this repository.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable
from dataclasses import dataclass

from governova_requirements.model import Finding, Requirement

MAX_STATEMENT_CHARS = 2000
"""Longer than any single requirement, and short enough to bound every scan."""


@dataclass(frozen=True)
class LintRule:
    """One deterministic check over a single requirement's text.

    A registry entry rather than a hard-coded branch, so an organisation can add its
    own house rule — a mandated ID scheme, a banned term specific to its regulator —
    without editing this module.
    """

    code: str
    title: str
    check: Callable[[Requirement], str | None]
    """Returns the finding message, or None when the requirement passes."""


_RULES: list[LintRule] = []


def register_rule(rule: LintRule) -> None:
    """Add a lint rule. The extension point for house and regulator-specific checks."""
    _RULES.append(rule)


def rules() -> tuple[LintRule, ...]:
    return tuple(_RULES)


def _statement(requirement: Requirement) -> str | None:
    """The text to lint, capped — or None when there is nothing to see."""
    if not requirement.has_text:
        return None
    assert requirement.statement is not None
    return requirement.statement.strip()[:MAX_STATEMENT_CHARS]


# ─── The rules ───────────────────────────────────────────────────────────────

_MODAL = re.compile(r"\b(shall|must|should|may)\b", re.I)
# `<subject> <modal> <function>` — something before the modal, something after it.
_GRAMMAR = re.compile(r"^.{1,300}?\b(?:shall|must|should|may)\b\s+\S.{0,1500}$", re.I | re.S)

# The canon's banned list: adjectives that read as requirements but bind nobody,
# because no two people would agree on whether they were met.
_VAGUE_TERMS: tuple[str, ...] = (
    "fast", "quick", "easy", "simple", "user-friendly", "intuitive", "efficient",
    "robust", "seamless", "appropriate", "adequate", "flexible", "reliable",
    "state-of-the-art", "as needed", "if possible", "etc",
)
_VAGUE = re.compile(rf"\b({'|'.join(re.escape(t) for t in _VAGUE_TERMS)})\b", re.I)

# A conjunction joining two *obligations* — not every "and". "email and password" is
# one idea; "shall authenticate and shall log" is two.
_TWO_OBLIGATIONS = re.compile(
    r"\b(?:shall|must|should|may)\b.{1,400}?\b(?:and|as well as|also|additionally)\b"
    r".{0,80}?\b(?:shall|must|should|may)\b",
    re.I | re.S,
)

# A requirement about a measurable property. If it names one, it needs a number.
_MEASURABLE = re.compile(
    r"\b(performance|latency|response time|throughput|availability|uptime|"
    r"scalab\w{0,6}|concurrent|capacity|downtime|recovery time)\b",
    re.I,
)
_HAS_NUMBER = re.compile(r"\d")

# "shall be validated" with nobody named to do the validating.
_PASSIVE = re.compile(
    r"\b(?:shall|must|should|may)\s+be\s+\w{2,20}(?:ed|en)\b(?!\s+by\s+\S)",
    re.I,
)

# Quoted text is data, not obligation. A requirement whose *message string* contains
# the word "fast" is not a vague requirement, and firing on it is the false positive
# that would end this rule's credibility on its first real repository.
_QUOTED = re.compile(r"\"[^\"]{0,500}\"|'[^']{0,500}'|`[^`]{0,500}`")


def _without_quotes(text: str) -> str:
    return _QUOTED.sub(" ", text)


def _check_modal_present(requirement: Requirement) -> str | None:
    text = _statement(requirement)
    if text is None:
        return None
    if _MODAL.search(text):
        return None
    return "no obligation verb — a requirement states shall, must, should, or may"


def _check_grammar(requirement: Requirement) -> str | None:
    text = _statement(requirement)
    if text is None or not _MODAL.search(text):
        return None  # `modal-absent` owns that finding; do not report it twice
    if _GRAMMAR.match(text):
        return None
    return "does not read as <subject> <obligation verb> <function>"


def _check_vague_terms(requirement: Requirement) -> str | None:
    text = _statement(requirement)
    if text is None:
        return None
    match = _VAGUE.search(_without_quotes(text))
    if match is None:
        return None
    return f"unverifiable term {match.group(1)!r} — state the measurable property instead"


def _check_one_idea(requirement: Requirement) -> str | None:
    text = _statement(requirement)
    if text is None:
        return None
    if _TWO_OBLIGATIONS.search(_without_quotes(text)) is None:
        return None
    return "joins two obligations — split into one requirement per obligation"


def _check_quantified(requirement: Requirement) -> str | None:
    text = _statement(requirement)
    if text is None:
        return None
    stripped = _without_quotes(text)
    match = _MEASURABLE.search(stripped)
    if match is None or _HAS_NUMBER.search(stripped):
        return None
    return f"names {match.group(1)!r} without a threshold — an unmeasurable target"


def _check_passive_actor(requirement: Requirement) -> str | None:
    text = _statement(requirement)
    if text is None:
        return None
    match = _PASSIVE.search(_without_quotes(text))
    if match is None:
        return None
    return "passive obligation with no named actor — say which component is responsible"


def _check_obligation_declared(requirement: Requirement) -> str | None:
    """The manifest's `obligation` field must agree with the statement's verb.

    Two sources for the same fact will disagree eventually, and a tracker export that
    labels a `should` as mandatory is a defect in the export the team cannot otherwise
    see.
    """
    text = _statement(requirement)
    if text is None or requirement.obligation is None:
        return None
    match = _MODAL.search(text)
    if match is None or match.group(1).lower() == requirement.obligation.lower():
        return None
    return (
        f"declared obligation {requirement.obligation!r} disagrees with "
        f"{match.group(1).lower()!r} in the statement"
    )


for _rule in (
    LintRule("modal-absent", "Requirement states an obligation", _check_modal_present),
    LintRule("grammar", "Requirement follows the canonical grammar", _check_grammar),
    LintRule("vague-term", "Requirement avoids unverifiable terms", _check_vague_terms),
    LintRule("two-obligations", "Requirement expresses one idea", _check_one_idea),
    LintRule("unquantified", "Measurable requirement carries a threshold", _check_quantified),
    LintRule("passive-actor", "Obligation names its actor", _check_passive_actor),
    LintRule("obligation-mismatch", "Declared obligation matches the statement", _check_obligation_declared),
):
    register_rule(_rule)


# ─── Running the linter ──────────────────────────────────────────────────────


def lint_requirement(requirement: Requirement) -> list[Finding]:
    """Every rule's verdict on one requirement. Untextual requirements yield nothing."""
    findings: list[Finding] = []
    for rule in _RULES:
        message = rule.check(requirement)
        if message is not None:
            findings.append(
                Finding(code=rule.code, message=message, requirement_id=requirement.id)
            )
    return findings


def lint(requirements: Iterable[Requirement]) -> list[Finding]:
    """Lint a whole requirement set, including the checks that span requirements.

    Ordered by requirement id so two runs over the same input produce the same
    report — a linter whose output reorders cannot be diffed between builds.
    """
    ordered = sorted(requirements, key=lambda r: r.id)
    findings: list[Finding] = []
    for requirement in ordered:
        findings.extend(lint_requirement(requirement))
    findings.extend(_check_unique_ids(ordered))
    return findings


def _check_unique_ids(requirements: list[Requirement]) -> list[Finding]:
    """Duplicate identifiers, which no single-requirement rule can see.

    An ID naming two requirements makes every trace built on it ambiguous, and the
    ambiguity is silent — both look linked.
    """
    seen: dict[str, int] = {}
    for requirement in requirements:
        seen[requirement.id] = seen.get(requirement.id, 0) + 1
    return [
        Finding(
            code="duplicate-id",
            message=f"{count} requirements share the id {rid!r} — identifiers are unique",
            requirement_id=rid,
        )
        for rid, count in sorted(seen.items())
        if count > 1
    ]
