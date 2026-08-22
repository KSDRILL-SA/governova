"""Governance of the rule set against the constitution.

Kept separate from `rules.py` (which is pure stdlib) because these functions read
the compiled index. They answer two questions:

- Is every rule *legitimate* — does it bind a real anti-pattern? (`validate_rules`)
- Which bindings does *this* installation's corpus not resolve? (`unresolved_bindings`)
- How much of the constitution is mechanically enforceable? (`enforcement_coverage`)

The first two look like one question and are two, which is what `ADR-013` decides:
a rule citing an anti-pattern that exists nowhere is a bug; a rule citing law this
installation does not hold is the licence boundary, and reporting it as a bug is a
false accusation against a correctly-built wheel.
"""

from __future__ import annotations

from typing import Any

from governova_compile.schema import CompiledIndex
from governova_compile.writer import load_active_index

from governova_checks.rules import RULES, covered_anti_patterns


def _load_index(index: CompiledIndex | None) -> CompiledIndex:
    if index is not None:
        return index
    return load_active_index()


def index_anti_patterns(index: CompiledIndex | None = None) -> set[str]:
    """Anti-pattern ids defined by the **core** constitutions (C00–C10).

    This is the denominator of the headline coverage metric, and it deliberately
    excludes Layer 4 so that adding a domain cannot move a number that is meant
    to track progress against the core.
    """
    idx = _load_index(index)
    return {ap.id for c in idx.constitutions for s in c.standards for ap in s.anti_patterns}


def domain_anti_patterns(index: CompiledIndex | None = None) -> set[str]:
    """Anti-pattern ids defined by Layer 4 domain extensions."""
    idx = _load_index(index)
    return {ap.id for d in idx.domains for s in d.standards for ap in s.anti_patterns}


def unresolved_bindings(index: CompiledIndex | None = None) -> list[str]:
    """Anti-pattern ids referenced by rules that this index does not define.

    A fact about the index, with no verdict attached. On the full corpus this is
    empty and any entry is drift; on the core subset it is 46 entries and every
    one of them is the licence boundary working correctly. The two cases are the
    same measurement and opposite conclusions, which is why the conclusion is
    drawn by `validate_rules` below rather than here.
    """
    defined = index_anti_patterns(index) | domain_anti_patterns(index)
    return sorted(r.anti_pattern for r in RULES if r.anti_pattern not in defined)


def validate_rules(index: CompiledIndex | None = None) -> list[str]:
    """Rule-set drift: anti-pattern ids that exist in **no** corpus at all.

    Implements `REQ-006` — the rule set cannot drift from the corpus it enforces.
    An empty list means the rule set is grounded. Core and domain anti-patterns
    are both legitimate bindings; a rule may enforce either.

    **This is an authoring-time invariant and it is answerable only against the
    full corpus.** `ADR-013` §(b): on a core installation 46 of 64 rules cite law
    the operator does not hold, by design, and this function used to report all
    46 as drift — accusing the licence boundary of being a bug. An installation
    holding a subset cannot tell a missing standard from an unlicensed one, so it
    does not guess. It returns nothing and `unresolved_bindings` reports the fact.

    That is the same discipline every probe follows: a check that cannot
    determine an answer says so rather than returning the convenient one. Here
    the convenient answer was a false accusation, which is worse than silence.
    """
    if _load_index(index).corpus != "full":
        return []
    return unresolved_bindings(index)


def analyser_anti_patterns() -> set[str]:
    """Anti-patterns bound by an **analyser** rather than by a reliable-tier rule.

    `coverage_pct` has always meant "anti-patterns a regex rule reaches", and it keeps
    that meaning here so the number stays comparable with every figure ever reported
    against it. But that definition stopped being the whole truth when detection grew
    past line-scanning: C11's grammar and traceability findings are as mechanical as
    any rule, and are invisible to a metric that only counts `RULES`.

    So this is reported **alongside** rather than folded in — the same treatment Layer 4
    gets, and for the same reason. Silently widening a metric makes every historical
    reading of it a lie.
    """
    bound: set[str] = set()
    for module in ("governova_requirements.evidence", "governova_schema.evidence"):
        try:
            bound |= set(__import__(module, fromlist=["ENFORCED_ANTI_PATTERNS"]).ENFORCED_ANTI_PATTERNS)
        except ImportError:  # pragma: no cover - the analysers ship in the same wheel
            continue
    return bound


def enforcement_coverage(index: CompiledIndex | None = None) -> dict[str, Any]:
    """How much of the constitution's anti-pattern surface is enforceable.

    The top-level keys describe **core** coverage by the reliable tier and keep the
    meaning they have always had, so the metric stays comparable across time. Layer 4
    coverage is reported alongside under `domain_*`, and analyser-bound coverage under
    `analyser_*` / `mechanical_*`, rather than being folded into the headline.
    """
    core = index_anti_patterns(index)
    domain = domain_anti_patterns(index)
    detected = covered_anti_patterns()

    covered = detected & core
    covered_domain = detected & domain
    total = len(core)
    pct = round(100 * len(covered) / total, 1) if total else 0.0
    domain_pct = round(100 * len(covered_domain) / len(domain), 1) if domain else 0.0

    by_analyser = analyser_anti_patterns() & core
    mechanical = covered | by_analyser
    mechanical_pct = round(100 * len(mechanical) / total, 1) if total else 0.0

    high = sum(1 for r in RULES if r.confidence == "high")
    medium = sum(1 for r in RULES if r.confidence == "medium")
    return {
        # `ADR-013` §(c) — every figure below is a fraction of a corpus, and the
        # core subset returns a *higher* `coverage_pct` than the full one (10.8
        # against 7.6) because its denominator shrank faster than its numerator.
        # Both are correct. Read side by side without this label, they say
        # coverage improved when the corpus was cut.
        "corpus": _load_index(index).corpus,
        "unresolved_bindings": len(unresolved_bindings(index)),
        "rules": len(RULES),
        "blocking_rules": high,
        "advisory_rules": medium,
        "path_scoped_rules": sum(1 for r in RULES if r.path_scoped),
        "enforceable_anti_patterns": len(covered),
        "total_anti_patterns": total,
        "coverage_pct": pct,
        "covered": sorted(covered),
        "domain_enforceable_anti_patterns": len(covered_domain),
        "domain_total_anti_patterns": len(domain),
        "domain_coverage_pct": domain_pct,
        "domain_covered": sorted(covered_domain),
        "analyser_enforceable_anti_patterns": len(by_analyser),
        "analyser_covered": sorted(by_analyser),
        "mechanical_enforceable_anti_patterns": len(mechanical),
        "mechanical_coverage_pct": mechanical_pct,
    }
