"""ADR-007's enforcement bar, computed rather than asserted.

Phase 2 adds standards under one binding constraint: **at least 40% of them must be
mechanically enforced at merge** — five times the corpus average. Coverage is a ratio, so
a careless expansion inflates the denominator and *lowers* the score while looking like
progress, and a stage that cannot meet the bar ships fewer standards rather than weaker
checks.

Until now that bar would have been tracked by hand in PR bodies. This repository has been
burned three times by exactly that pattern — `S1.104` declared reliable-tier rules that
did not exist, `S8.84` demanded a CVE gate nobody ran, and the `S1.19` probe drifted from
its own standard until a test tied them together. A bar measured by assertion is a bar
that gets missed politely.
"""

from __future__ import annotations

import pytest
from governova_checks import RULES
from governova_compile.compiler import compile_index
from governova_compile.discovery import resolve_repo_root
from governova_evidence import probed_standards

# The constitutions ADR-007 adds. Listed rather than derived, so that adding a fifth is a
# deliberate act that shows up in this file's diff.
PHASE_2_CONSTITUTIONS: frozenset[str] = frozenset({"C11", "C12", "C13", "C14"})

# Standards Phase 2 added to *existing* constitutions. ADR-007's constraint is on
# "standards added in this phase", not on standards living in new documents — so folding
# project governance into C9 rather than making it a fifth constitution must not exempt it
# from the bar it would otherwise have had to meet.
PHASE_2_ADDITIONS: frozenset[str] = frozenset({"S9.31", "S9.32", "S9.33"})

MINIMUM_MECHANICAL_RATIO = 0.40
"""ADR-007 constraint 2. Not an aspiration."""


@pytest.fixture(scope="module")
def index():
    return compile_index(resolve_repo_root())


def _phase_2_standards(index) -> list:
    return [
        standard
        for constitution in index.constitutions
        for standard in constitution.standards
        if constitution.id in PHASE_2_CONSTITUTIONS or standard.id in PHASE_2_ADDITIONS
    ]


def _mechanically_enforced() -> set[str]:
    """Standards a mechanical check can reach: a reliable-tier rule or the probe tier.

    "Reachable" is the right test, not "currently satisfied here". The bar asks whether
    the law arrived with a check, which is a property of the corpus. Whether *this*
    repository satisfies it is a different question, answered by constitutional coverage.
    """
    return {rule.standard for rule in RULES} | probed_standards()


def test_phase_2_standards_meet_the_mechanical_enforcement_bar(index):
    standards = _phase_2_standards(index)
    if not standards:
        pytest.skip("no Phase 2 constitutions are ratified yet")

    mechanical = {s.id for s in standards if s.id in _mechanically_enforced()}
    ratio = len(mechanical) / len(standards)
    unenforced = sorted({s.id for s in standards} - mechanical)

    assert ratio >= MINIMUM_MECHANICAL_RATIO, (
        f"ADR-007 constraint 2: {len(mechanical)}/{len(standards)} "
        f"({ratio:.0%}) of Phase 2 standards are mechanically enforced, "
        f"below the {MINIMUM_MECHANICAL_RATIO:.0%} bar. "
        f"Ship fewer standards, not weaker checks. Unenforced: {unenforced}"
    )


def test_every_phase_2_standard_declares_an_enforcement_path(index):
    """ADR-007 constraint 1 — no standard without a named enforcement path.

    An empty `Enforced By` is the shape of the defect this constraint exists to
    prevent: law written now, with the check left as an intention.
    """
    standards = _phase_2_standards(index)
    if not standards:
        pytest.skip("no Phase 2 constitutions are ratified yet")
    undeclared = sorted(s.id for s in standards if not s.enforced_by)
    assert undeclared == [], f"Phase 2 standards with no declared enforcement path: {undeclared}"


def test_a_standard_claiming_a_mechanical_path_actually_has_one(index):
    """The `S1.104` failure, made impossible to repeat.

    `S1.104` declared reliable-tier enforcement before any rule existed, and `S8.84`
    demanded a CVE gate this repository did not run. Both were found by auditing
    Governova against its own standards. A Phase 2 standard naming a linter, a probe,
    or a rule must be reachable by one.
    """
    standards = _phase_2_standards(index)
    if not standards:
        pytest.skip("no Phase 2 constitutions are ratified yet")

    reachable = _mechanically_enforced()
    claims_mechanism = ("linter", "probe", "rule", "governova ", "trace")
    liars = sorted(
        s.id
        for s in standards
        if any(token in " ".join(s.enforced_by).lower() for token in claims_mechanism)
        and s.id not in reachable
    )
    assert liars == [], f"standards claiming a mechanical path that does not exist: {liars}"
