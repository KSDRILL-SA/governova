"""`ADR-013` — a rule fires for a defect, not for a licence.

`ADR-011` splits the corpus: the wheel carries 167 anti-patterns under MIT and the
domain packs are licensed. The rules did not split and could not — they are code,
they ship in the same wheel, and every one of them works. So on a core
installation 46 of 64 rules cite law the operator does not hold.

`ADR-013` decides what that means. These are its three consequences, asserted:

- **(a)** a finding is readable without the corpus,
- **(b)** citing unheld law is a fact, not a defect,
- **(c)** every coverage figure names the corpus it was computed against.

The decision underneath them is that the rules **fire anyway**, and the reason is
not preference: `ADR-010 §5.1` guarantees the deterministic engine runs complete
and offline forever, and a rule that goes dormant because the operator's corpus
lacks the standard is a licence check evaluated locally.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from governova_checks import (
    enforcement_coverage,
    scan_text,
    unresolved_bindings,
    validate_rules,
)
from governova_checks.rules import RULES
from governova_compile.discovery import resolve_repo_root
from governova_compile.writer import load_index

ROOT = Path(resolve_repo_root())


@pytest.fixture(scope="module")
def full():
    return load_index(ROOT / "compiled" / "constitution.json")


@pytest.fixture(scope="module")
def core():
    path = ROOT / "compiled" / "constitution.core.json"
    if not path.exists():  # pragma: no cover - the core index is committed
        pytest.skip("no core index in this tree")
    return load_index(path)


# ─── The decision: a rule fires whether or not the law is held ───────────────


def test_a_rule_fires_against_a_corpus_that_does_not_contain_its_anti_pattern(core) -> None:
    """The central decision, checked with a rule that is unresolved on core.

    `AP-S5.28a` — money in a float — is outside the core subset. A payments bug
    is a payments bug whether or not the operator licensed C05, and a scanner
    that detected it and declined to say so is the failure this project exists
    to name.
    """
    assert "AP-S5.28a" in unresolved_bindings(core)

    findings = scan_text("class Order:\n    total_amount: float = 0.0\n")
    assert any(f.anti_pattern == "AP-S5.28a" for f in findings), findings


def test_detection_does_not_consult_the_corpus_at_all(core) -> None:
    """The mechanism behind it: `rules.py` is pure stdlib and reads no index.

    This is what makes the guarantee structural rather than remembered. There is
    no index parameter to thread an entitlement through, so there is nowhere for
    a licence check to be added without a visible change of signature.
    """
    import inspect

    import governova_checks.rules as rules

    source = inspect.getsource(rules)
    for forbidden in ("CompiledIndex", "load_index", "load_active_index", "core_subset"):
        assert forbidden not in source, (
            f"rules.py reads the corpus via {forbidden}; detection must not depend on "
            "which law the operator holds — ADR-010 §5.1"
        )


# ─── (a) A finding is readable without the corpus ────────────────────────────


def test_every_rule_explains_itself_without_the_standard_behind_it() -> None:
    """`ADR-013` §(a). "Buy the domain pack to find out what is wrong" is not a message.

    On a core installation 46 of these citations do not resolve, so the message
    is the whole of what the reader gets. It has to name the defect and it has to
    name the standard, so the citation is a pointer rather than the only content.
    """
    for rule in RULES:
        message = rule.message.strip()
        assert len(message) >= 40, f"{rule.anti_pattern}: message too thin to stand alone"
        assert rule.standard in message, (
            f"{rule.anti_pattern}: the message does not name {rule.standard}, so a "
            "reader without the corpus cannot tell which law it is about"
        )


# ─── (b) Citing unheld law is a fact, not a defect ───────────────────────────


def test_the_full_corpus_grounds_every_rule(full) -> None:
    """`REQ-006`, unchanged. Against the full corpus, drift is drift."""
    assert validate_rules(full) == []
    assert unresolved_bindings(full) == []


def test_the_core_corpus_does_not_ground_every_rule_and_that_is_not_drift(core) -> None:
    """`ADR-013` §(b). The measurement is the same; the conclusion is opposite.

    `validate_rules` used to return these 46 and call them drift — accusing a
    correctly built wheel of a defect. An installation holding a subset cannot
    tell a missing standard from an unlicensed one, so it does not guess.
    """
    unresolved = unresolved_bindings(core)
    assert len(unresolved) > 0, "this test is meaningless if the subset grounds everything"
    assert validate_rules(core) == [], (
        "a core installation reported the licence boundary as rule-set drift"
    )


def test_validate_rules_answers_only_where_the_answer_is_knowable(core, full) -> None:
    """The discipline every probe follows, applied here.

    A check that cannot determine an answer returns nothing rather than the
    convenient one. Here the convenient answer was a false accusation.
    """
    assert full.corpus == "full"
    assert core.corpus == "core"
    assert validate_rules(core) == []


# ─── (c) Every coverage figure names its corpus ──────────────────────────────


def test_the_coverage_payload_says_which_corpus_it_describes(full, core) -> None:
    """`ADR-013` §(c). Both figures are correct and they are not comparable."""
    on_full = enforcement_coverage(full)
    on_core = enforcement_coverage(core)

    assert on_full["corpus"] == "full"
    assert on_core["corpus"] == "core"

    # The reason the label is not optional: the smaller corpus scores higher.
    assert on_core["coverage_pct"] > on_full["coverage_pct"]
    assert on_core["total_anti_patterns"] < on_full["total_anti_patterns"]


def test_the_coverage_payload_reports_unresolved_bindings_as_a_number(core) -> None:
    """Reported, because hiding it would be the other dishonesty available here."""
    assert enforcement_coverage(core)["unresolved_bindings"] == len(unresolved_bindings(core))


def test_the_two_committed_indexes_are_distinguishable(full, core) -> None:
    """The defect that made §(c) necessary: they were not.

    Same schema version, same source commit, different law, and nothing in either
    document said which was which. Every metric read off one of them carried a
    denominator nobody could attribute.
    """
    assert full.schema_version == core.schema_version
    assert full.source_commit_sha == core.source_commit_sha
    assert full.corpus != core.corpus


def test_the_corpus_marker_is_covered_by_the_checksum(core) -> None:
    """Otherwise an index could claim to be core, be tampered with, and verify."""
    from governova_compile.writer import compute_checksum

    assert compute_checksum(core) == core.checksum

    forged = core.model_copy(deep=True)
    forged.corpus = "full"
    assert compute_checksum(forged) != core.checksum


# ─── The record of the decision has to be findable ───────────────────────────


def test_adr_index_lists_every_record() -> None:
    """`governance/decisions/README.md` carried a note saying it goes stale.

    It had stopped at ADR-004 while five records were added, then at ADR-011
    while two more were — and the note explaining that was left in place instead
    of a check. A decision nobody can find from the index is a decision that gets
    made again, differently.
    """
    decisions = ROOT / "governance" / "decisions"
    index = (decisions / "README.md").read_text(encoding="utf-8")

    missing = [
        path.name
        for path in sorted(decisions.glob("ADR-*.md"))
        if path.stem.split("-")[0] + "-" + path.stem.split("-")[1] not in index
    ]
    assert not missing, f"ADR record(s) absent from the decisions index: {missing}"
