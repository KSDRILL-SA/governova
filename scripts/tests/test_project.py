"""Tests for per-project applicability and constitutional coverage.

The weight is on the ways this metric could be **inflated**, because that is the
only way it becomes worthless: shrinking the denominator by over-claiming
inapplicability, or padding the numerator with declarations nobody checked. Both
are easy to write accidentally and impossible to detect from the number alone.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from governova_compile.schema import (
    CompiledIndex,
    Constitution,
    DocumentHeader,
    Phase,
    Priority,
    Standard,
)
from governova_project import (
    Profile,
    applicable_standards,
    applies,
    compute_coverage,
    coverage_factor,
    load_profile,
    verify_claims,
)
from governova_score.compute import compute_score


def _std(sid: str, applies_to: str = "Both Stacks", phase: Phase | None = None) -> Standard:
    return Standard(
        id=sid,
        title="T",
        constitution_id="C01",
        priority=Priority.STANDARD,
        applies_to=applies_to,
        phase=phase,
        statement="s",
        rationale="r",
        source_path="p",
        source_line=1,
    )


def _index(*standards: Standard, domains: list[Constitution] | None = None) -> CompiledIndex:
    return CompiledIndex(
        compiled_at=datetime(2026, 7, 28, tzinfo=UTC),
        checksum="x",
        constitutions=[
            Constitution(
                id="C01",
                number=1,
                name="Engineering",
                header=DocumentHeader(document="C1"),
                path="p",
                standards=list(standards),
            )
        ],
        domains=domains or [],
    )


def _write(root: Path, toml: str) -> None:
    (root / "governance").mkdir(parents=True, exist_ok=True)
    (root / "governance" / "project.toml").write_text(toml, encoding="utf-8")


# ─── Applicability: the denominator ──────────────────────────────────────────


def test_universal_standards_apply_to_every_project() -> None:
    profile = Profile(stacks=["python"])
    for scope in ("Both Stacks", "All Systems", "All Stacks · all systems", ""):
        assert applies(_std("S1.1", scope), profile), scope


def test_a_stack_exclusive_standard_does_not_apply_to_another_stack() -> None:
    profile = Profile(stacks=["python", "fastapi"])
    assert not applies(_std("S4.1", "Angular Only"), profile)
    assert not applies(_std("S4.2", "Next.js Stack"), profile)


def test_a_stack_exclusive_standard_applies_to_a_project_using_that_stack() -> None:
    assert applies(_std("S4.1", "Angular Only"), Profile(stacks=["angular"]))
    assert applies(_std("S4.2", "Next.js Stack"), Profile(stacks=["nextjs"]))


def test_an_unrecognised_scope_defaults_to_applicable() -> None:
    """The load-bearing default.

    A narrower denominator is an easier score, so anything the matcher does not
    confidently recognise as stack-exclusive must count as applicable.
    """
    profile = Profile(stacks=["python"])
    for scope in (
        "All Stacks · every external integration (OAuth/SSO, webhooks, partner APIs)",
        "Something nobody anticipated",
        "All Stacks · existing-system adoption",
    ):
        assert applies(_std("S8.1", scope), profile), scope


def test_a_future_phase_is_not_yet_applicable() -> None:
    profile = Profile(stacks=["python"], phase=1)
    assert applies(_std("S1.1", phase=Phase.FOUNDATION), profile)
    assert applies(_std("S2.1", phase=Phase.CORE_ARCHITECTURE), profile)
    assert not applies(_std("S7.1", phase=Phase.QUALITY_RELIABILITY), profile)


def test_no_declared_phase_means_every_phase_applies() -> None:
    profile = Profile(stacks=["python"], phase=None)
    assert applies(_std("S9.1", phase=Phase.PRODUCT_INTELLIGENCE), profile)


def test_only_declared_domains_contribute_standards() -> None:
    domain = Constitution(
        id="D-SAAS",
        number=99,
        name="SaaS",
        header=DocumentHeader(document="d"),
        path="p",
        slug="saas",
        standards=[_std("D-SAAS.1")],
    )
    index = _index(_std("S1.1"), domains=[domain])
    assert len(applicable_standards(index, Profile(domains=["D-SAAS"]))) == 2
    assert len(applicable_standards(index, Profile(domains=[]))) == 1


# ─── Evidence: the numerator ─────────────────────────────────────────────────


def test_a_declaration_without_resolvable_evidence_counts_for_nothing(
    tmp_path: Path,
) -> None:
    """The inflation path this factor exists to close.

    Without this, a project satisfies the entire constitution by typing.
    """
    profile = Profile(
        stacks=["python"],
        satisfied=[{"standard": "S1.1", "evidence": "docs/does-not-exist.md"}],
    )
    result = compute_coverage(tmp_path, _index(_std("S1.1")), profile)
    assert result.satisfied == 0
    assert result.pct == 0.0
    assert len(result.broken_claims) == 1


def test_a_declaration_with_resolvable_evidence_counts(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "real.md").write_text("x", encoding="utf-8")
    profile = Profile(
        stacks=["python"], satisfied=[{"standard": "S1.1", "evidence": "docs/real.md"}]
    )
    result = compute_coverage(tmp_path, _index(_std("S1.1")), profile)
    assert result.satisfied == 1 and result.pct == 100.0


def test_an_exception_citing_a_nonexistent_adr_counts_for_nothing(tmp_path: Path) -> None:
    profile = Profile(stacks=["python"], exceptions=[{"standard": "S1.1", "adr": "ADR-999"}])
    result = compute_coverage(tmp_path, _index(_std("S1.1")), profile)
    assert result.excepted == 0
    assert result.broken_claims and result.broken_claims[0].kind == "exception"


def test_an_exception_citing_a_real_adr_counts(tmp_path: Path) -> None:
    decisions = tmp_path / "governance" / "decisions"
    decisions.mkdir(parents=True)
    (decisions / "ADR-005-platform-architecture.md").write_text("x", encoding="utf-8")
    profile = Profile(stacks=["python"], exceptions=[{"standard": "S1.1", "adr": "ADR-005"}])
    result = compute_coverage(tmp_path, _index(_std("S1.1")), profile)
    assert result.excepted == 1 and result.pct == 100.0


def test_a_claim_about_an_inapplicable_standard_does_not_inflate_coverage(
    tmp_path: Path,
) -> None:
    """Claiming standards outside your own scope must not raise the numerator."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "real.md").write_text("x", encoding="utf-8")
    profile = Profile(
        stacks=["python"],
        satisfied=[
            {"standard": "S1.1", "evidence": "docs/real.md"},
            {"standard": "S4.1", "evidence": "docs/real.md"},  # Angular-only
        ],
    )
    index = _index(_std("S1.1"), _std("S4.1", "Angular Only"))
    result = compute_coverage(tmp_path, index, profile)
    assert result.applicable == 1
    assert result.pct == 100.0, "the out-of-scope claim must neither count nor exceed 100"


def test_mechanical_and_declared_evidence_are_not_double_counted(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "real.md").write_text("x", encoding="utf-8")
    profile = Profile(
        stacks=["python"], satisfied=[{"standard": "S1.1", "evidence": "docs/real.md"}]
    )
    index = _index(_std("S1.1"), _std("S1.2"))
    result = compute_coverage(tmp_path, index, profile, enforced={"S1.1"})
    assert result.mechanical == 1
    assert result.declared == 0, "already mechanically verified — must not count twice"
    assert result.satisfied == 1


def test_mechanical_evidence_needs_no_declaration(tmp_path: Path) -> None:
    result = compute_coverage(
        tmp_path, _index(_std("S1.1")), Profile(stacks=["python"]), enforced={"S1.1"}
    )
    assert result.satisfied == 1 and result.pct == 100.0


def test_verify_claims_reports_both_kinds(tmp_path: Path) -> None:
    profile = Profile(
        satisfied=[{"standard": "S1.1", "evidence": "nope.md"}],
        exceptions=[{"standard": "S1.2", "adr": "ADR-000"}],
    )
    claims = verify_claims(tmp_path, profile)
    assert {c.kind for c in claims} == {"satisfied", "exception"}
    assert not any(c.resolved for c in claims)


# ─── Profile loading ─────────────────────────────────────────────────────────


def test_a_missing_profile_leaves_the_factor_unassessed(tmp_path: Path) -> None:
    """Undeclared is never assumed compliant."""
    assert load_profile(tmp_path) is None
    score, detail = coverage_factor(tmp_path, _index(_std("S1.1")))
    assert score is None and "no project profile" in detail


def test_a_malformed_profile_is_unassessed_not_perfect(tmp_path: Path) -> None:
    _write(tmp_path, "this is not [valid toml")
    assert load_profile(tmp_path) is None


def test_profile_fields_are_normalised(tmp_path: Path) -> None:
    _write(
        tmp_path,
        '[project]\nname = "X"\nstacks = ["Python", "FastAPI"]\ndomains = ["d-saas"]\nphase = 2\n',
    )
    profile = load_profile(tmp_path)
    assert profile is not None
    assert profile.stacks == ["python", "fastapi"]
    assert profile.domains == ["D-SAAS"]
    assert profile.phase == 2


# ─── Score integration ───────────────────────────────────────────────────────


def test_the_coverage_factor_is_unassessed_without_a_profile(tmp_path: Path) -> None:
    factor = next(
        f for f in compute_score(tmp_path).factors if f.key == "constitutional_coverage"
    )
    assert factor.score is None


def test_this_repository_assesses_every_factor() -> None:
    """The point of the runtime work: no factor left dark."""
    from governova_compile.discovery import resolve_repo_root

    factors = compute_score(resolve_repo_root()).factors
    unassessed = [f.key for f in factors if f.score is None]
    assert not unassessed, f"still dark: {unassessed}"
    assert sum(f.weight for f in factors) == 100
