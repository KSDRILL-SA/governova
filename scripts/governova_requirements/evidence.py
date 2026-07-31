"""C11 as mechanical evidence — the bridge from the analyser to the probe tier.

Eleven of C11's twelve standards are decidable from what a repository exposes, so they
belong in the evidence model rather than in a declaration. This module is what makes them
count: `governova_evidence` runs these alongside its own probes, and constitutional
coverage picks them up with no entry in `governance/project.toml`.

**The tier rule governs every verdict here.** A repository that exposes nothing returns
`unknown` — never `satisfied`, and never `violated`. A false `satisfied` silently retires
a standard nobody will examine again, and a false `violated` accuses a team of failing
something it never had the chance to demonstrate. Both are worse than saying so.
"""

from __future__ import annotations

from pathlib import Path

from governova_requirements.lint import lint
from governova_requirements.model import RequirementSet, Tier
from governova_requirements.sources import collect
from governova_requirements.trace import trace

# Every C11 standard that a mechanical check answers, and the finding code that answers
# it. S11.12 is absent on purpose: requirement *history* lives in the tracker a team
# owns, this engine never calls it, and a check that cannot see the previous version
# cannot detect that a version was replaced. The standard says so in its own rationale
# rather than claiming an enforcement path that does not exist.
LINT_BOUND: dict[str, str] = {
    "S11.2": "duplicate-id",
    "S11.5": "modal-absent",
    "S11.6": "grammar",
    "S11.7": "two-obligations",
    "S11.8": "passive-actor",
    "S11.9": "vague-term",
    "S11.10": "unquantified",
    "S11.11": "obligation-mismatch",
}

TRACE_BOUND: dict[str, str] = {
    "S11.3": "requirement-without-implementation",
    "S11.4": "requirement-without-test",
}

# §5 traceability closure — the questions that need history rather than a snapshot.
CLOSURE_BOUND: dict[str, str] = {
    "S11.13": "orphan-citation",
    "S11.14": "stale-verification",
}

# S11.15 is bound separately: `untraced-change` is advisory by construction, so the
# verdict is a *rate* rather than a presence. A refactor, a dependency bump, and a lint
# fix all legitimately serve no requirement, and a check that failed on them would be
# gamed within a week by citing a requirement number in every commit.
UNTRACED_STANDARD = "S11.15"

REACHABILITY_STANDARD = "S11.1"

MECHANICAL_STANDARDS: frozenset[str] = frozenset(
    {REACHABILITY_STANDARD, UNTRACED_STANDARD, *TRACE_BOUND, *LINT_BOUND, *CLOSURE_BOUND}
)
"""The eleven C11 standards with a mechanical enforcement path that exists today."""

# `Grounded In` for the enforcement claim itself: each anti-pattern below is detected by
# the finding code its standard names in `Enforced By`.
ENFORCED_ANTI_PATTERNS: frozenset[str] = frozenset(
    f"AP-{sid}a" for sid in MECHANICAL_STANDARDS
)


def _verdicts(root: Path) -> list[tuple[str, str, str]]:
    """(standard, verdict, evidence) for every mechanically checked C11 standard.

    Verdict strings match `governova_evidence.Verdict` values so the caller can build
    `ProbeResult`s without this module importing that one — the dependency runs one
    way, from the evidence tier into the analyser.
    """
    found = collect(root)
    tier = found.tier

    if tier < Tier.REFERENCED:
        reason = "no requirements are reachable — unassessed, not violated (C11 §opening)"
        return [(sid, "unknown", reason) for sid in sorted(MECHANICAL_STANDARDS)]

    results: list[tuple[str, str, str]] = [
        (
            REACHABILITY_STANDARD,
            "satisfied",
            f"tier {int(tier)} — {len(found.requirements)} requirement(s) reachable "
            f"from {len(found.citations)} citation(s)",
        )
    ]

    report = trace(found)
    trace_codes = {f.code for f in report.findings}
    for sid, code in sorted(TRACE_BOUND.items()):
        if sid == "S11.3" and tier < Tier.EXPORTED:
            # At tier 1 the requirement set *is* the set of citations, so every
            # requirement is implemented by construction. Answering would be circular.
            results.append(
                (sid, "unknown", "tier 1 — no declared requirement set to compare against")
            )
        elif code in trace_codes:
            offending = [f for f in report.findings if f.code == code]
            results.append((sid, "violated", f"{len(offending)} × {code}"))
        else:
            results.append((sid, "satisfied", f"no {code} finding across {report.requirements} requirement(s)"))

    results.extend(_closure_verdicts(root, found))

    lintable = [r for r in found.requirements.values() if r.has_text]
    if not lintable:
        reason = f"tier {int(tier)} — no requirement text is reachable, so grammar is unknown"
        results.extend((sid, "unknown", reason) for sid in sorted(LINT_BOUND))
        return results

    findings = lint(lintable)
    codes = {f.code for f in findings}
    for sid, code in sorted(LINT_BOUND.items()):
        if code in codes:
            count = sum(1 for f in findings if f.code == code)
            results.append((sid, "violated", f"{count} × {code}"))
        else:
            results.append((sid, "satisfied", f"no {code} finding across {len(lintable)} requirement(s)"))
    return results


def _closure_verdicts(root: Path, found: RequirementSet) -> list[tuple[str, str, str]]:
    """Verdicts for §5, which need history rather than the current state."""
    from governova_requirements.closure import close

    report = close(root, found)
    if not report.assessed:
        reason = "no git history available — closure is unassessed, not violated"
        return [
            (sid, "unknown", reason)
            for sid in sorted({UNTRACED_STANDARD, *CLOSURE_BOUND})
        ]

    results: list[tuple[str, str, str]] = []
    by_code = {
        "orphan-citation": report.orphan_citations,
        "stale-verification": report.stale_verifications,
    }
    for sid, code in sorted(CLOSURE_BOUND.items()):
        hits = by_code[code]
        if hits:
            results.append((sid, "violated", f"{len(hits)} × {code}"))
        else:
            results.append((sid, "satisfied", f"no {code} across {report.source_commits} commit(s)"))

    rate = report.citation_rate
    if rate is None:
        results.append((UNTRACED_STANDARD, "unknown", "no source-touching commits to inspect"))
    elif not report.untraced_changes:
        results.append(
            (UNTRACED_STANDARD, "satisfied", f"every source commit cites a requirement ({rate}%)")
        )
    else:
        # Deliberately `unknown`, never `violated`. Whether an untraced change *should*
        # have cited a requirement is a judgement this check cannot make — it makes the
        # portion visible, which is what the standard actually requires.
        results.append(
            (
                UNTRACED_STANDARD,
                "unknown",
                f"{report.cited_commits}/{report.source_commits} source commits cite a "
                f"requirement ({rate}%) — the untraced portion is visible and needs a "
                f"human verdict",
            )
        )
    return results


def probe_verdicts(root: Path) -> list[tuple[str, str, str]]:
    """Public entry point. A failure anywhere degrades to `unknown`, never `satisfied`."""
    try:
        return _verdicts(root)
    except Exception as exc:
        return [
            (sid, "unknown", f"requirements probe error: {type(exc).__name__}")
            for sid in sorted(MECHANICAL_STANDARDS)
        ]
