"""Compute the Governova Score for a repository.

Each §18.1 factor has an assessor that returns a Factor with a sub-score, or with
score=None when the data needed to assess it is not present (e.g. no runtime relay
or audit instrumentation). `model.finalize` then renormalises over assessed factors.
"""

from __future__ import annotations

from pathlib import Path

from governova_checks import for_declared_domains, iter_source_files, scan_paths
from governova_compile.discovery import resolve_repo_root
from governova_project import load_profile

from governova_score.model import TITLES, WEIGHTS, Factor, GovernovaScore, finalize

# Violation-rate penalties (points off per finding). Blocking (high-confidence)
# findings cost far more than advisory (medium-confidence) ones.
_BLOCKING_PENALTY = 10
_ADVISORY_PENALTY = 3


def _factor(key: str, score: float | None, detail: str) -> Factor:
    return Factor(key=key, title=TITLES[key], weight=WEIGHTS[key], score=score, detail=detail)


def _violation_rate(root: Path) -> Factor:
    """Always assessable: scan the repo's source and penalise findings.

    The factor is a **count**, and it saturates: at three points per advisory
    finding it reaches zero at 34, and cannot then distinguish 34 from 340. That
    is a real limitation and it is not corrected here — amending the penalty
    curve means picking a number to produce a pleasing shape, and no defensible
    basis for a particular curve has been established (ADR-012).

    What is added is **density beside the count**, never instead of it. Once the
    factor reads zero the reader's next question is *how bad, and how spread
    out?* — and 52 findings across 32 files is a different situation from 52
    across 3,200 while being the same number. Reported the same way
    `mechanical_coverage_pct` sits beside `coverage_pct`, and for the same
    reason: a metric's definition is never silently widened, so every historical
    reading of `violation_rate` still means what it meant.
    """
    files = list(iter_source_files(root))
    # Layer 4 findings count only for a project that declared the sector. The
    # coverage factor has always excluded undeclared domains from its
    # denominator; counting their violations here would penalise a project for
    # breaking law the same model says does not bind it.
    profile = load_profile(root)
    applicable = for_declared_domains(
        scan_paths(files), profile.domains if profile else None
    )
    findings = applicable.findings
    blocking = sum(1 for f in findings if f.blocking)
    advisory = len(findings) - blocking
    score = max(0.0, 100.0 - _BLOCKING_PENALTY * blocking - _ADVISORY_PENALTY * advisory)

    if not findings:
        clean = f"clean across {len(files)} source file(s)"
        if applicable.withheld:
            clean += (
                f"; {len(applicable.withheld)} withheld "
                f"({', '.join(applicable.withheld_domains)} not declared)"
            )
        return _factor("violation_rate", score, clean)

    density = len(findings) / len(files) if files else 0.0
    detail = (
        f"{blocking} blocking, {advisory} advisory across {len(files)} source file(s) "
        f"— {density:.2f} per file"
    )
    if applicable.withheld:
        detail += (
            f"; {len(applicable.withheld)} withheld "
            f"({', '.join(applicable.withheld_domains)} not declared)"
        )
    return _factor("violation_rate", score, detail)


def _amendment_discipline(root: Path) -> Factor:
    """Assessable when the repo keeps governance records (changelog + ADRs)."""
    changelog = root / "governance" / "changelog"
    decisions = root / "governance" / "decisions"
    if not changelog.is_dir() and not decisions.is_dir():
        return _factor("amendment_discipline", None, "no governance records found")

    points = 0.0
    bits: list[str] = []
    amendments_log = changelog / "amendments-log.md"
    if amendments_log.is_file() and amendments_log.stat().st_size > 0:
        points += 50
        bits.append("amendments log ✓")
    else:
        bits.append("amendments log ✗")
    adrs = list(decisions.glob("ADR-*.md")) if decisions.is_dir() else []
    if adrs:
        points += 50
        bits.append(f"{len(adrs)} ADR(s)")
    else:
        bits.append("no ADRs")
    return _factor("amendment_discipline", points, ", ".join(bits))


def _audit_trail(root: Path) -> Factor:
    """Measure the trail's integrity, not its existence.

    The previous implementation scored 100 for any file in `governance/audit/`,
    which meant `touch governance/audit/x` earned full marks on the one factor
    whose purpose is proving records were not fabricated. What matters is whether
    the chain verifies: a broken chain is worse than no trail, because it is a
    trail that has been altered, so it scores zero rather than partial credit.
    """
    from governova_audit import audit_path, completeness, verify

    if not audit_path(root).is_file():
        return _factor("audit_trail", None, "no audit trail (requires runtime instrumentation)")

    chain = verify(root)
    if chain.records == 0:
        return _factor("audit_trail", None, "audit trail present but empty")
    if not chain.valid:
        return _factor("audit_trail", 0.0, f"TAMPERED — {chain.issues[0]}")

    pct = completeness(root)
    return _factor(
        "audit_trail",
        pct,
        f"chain intact, {chain.records} record(s), {pct}% fully attributed",
    )


def _relay_compliance(root: Path) -> Factor:
    """Measured from recorded relay history (see `governova_relay.compliance`)."""
    from governova_relay import compliance

    score, detail = compliance(root)
    return _factor("relay_compliance", score, detail)


def _constitutional_coverage(root: Path) -> Factor:
    """Share of the standards that apply to this project which are satisfied.

    Applicability is derived from the project profile (`governova_project`); it is
    never hand-listed. A project that has declared no profile is unassessed — an
    undeclared project is never assumed compliant.
    """
    from governova_compile.writer import load_active_index
    from governova_project import coverage_factor

    # `load_active_index`, not `root / "compiled" / ...`. The hard-coded path
    # exists only in a Governova source tree, so an installed adopter always got
    # "no compiled index" here — and this is the factor `ADR-012` names as the
    # one that reaches quorum. The effect was that **no installed user could
    # ever be issued a Governova Score**, which is the product's headline number.
    #
    # The resolver already handles all four cases: an explicit path, the
    # `GOVERNOVA_CONSTITUTION` override, a working-tree index found by walking
    # up, and the copy bundled in the wheel.
    try:
        index = load_active_index(start=root)
    except FileNotFoundError:
        return _factor("constitutional_coverage", None, "no constitution index found")
    score, detail = coverage_factor(root, index)
    return _factor("constitutional_coverage", score, detail)


def compute_score(root: Path | None = None) -> GovernovaScore:
    """Compute the Governova Score for the repo rooted at `root`."""
    r = root or resolve_repo_root()
    factors = [
        _violation_rate(r),
        _relay_compliance(r),
        _constitutional_coverage(r),
        _amendment_discipline(r),
        _audit_trail(r),
    ]
    return finalize(factors)
