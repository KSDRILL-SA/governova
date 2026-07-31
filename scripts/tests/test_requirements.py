"""Tests for the requirements tier.

Every lint rule gets a positive *and* a negative case. The negative is the deliverable:
a legitimate requirement that merely contains the word "fast" inside a quoted string
must not fire, and a rule that cannot tell those apart would be withdrawn on its first
encounter with a real repository.

The governing property, asserted repeatedly below: **a repository that exposes no
requirements is `unknown`, never in violation.**
"""

from __future__ import annotations

import json

import pytest
from governova_requirements import (
    MANIFEST_SCHEMA_VERSION,
    ManifestError,
    ReaderConfig,
    Requirement,
    RequirementSet,
    Tier,
    collect,
    lint,
    lint_requirement,
    parse_manifest,
    read_referenced,
    registered_readers,
    trace,
)
from governova_requirements.model import Citation


def _req(statement: str, rid: str = "REQ-001", **kwargs: object) -> Requirement:
    return Requirement(id=rid, statement=statement, **kwargs)  # type: ignore[arg-type]


def _codes(requirement: Requirement) -> set[str]:
    return {f.code for f in lint_requirement(requirement)}


def _manifest(*requirements: dict[str, object], version: str = MANIFEST_SCHEMA_VERSION) -> str:
    return json.dumps({"schema_version": version, "requirements": list(requirements)})


# ─── Lint rules: positive and negative for each ──────────────────────────────


def test_modal_absent_fires_and_a_real_requirement_does_not():
    assert "modal-absent" in _codes(_req("The system authenticates users."))
    assert "modal-absent" not in _codes(_req("The system shall authenticate users."))


def test_grammar_rule_does_not_double_report_a_missing_modal():
    # `modal-absent` owns that finding. Two findings for one defect is noise, and
    # noise is how a linter's output stops being read.
    assert _codes(_req("Users log in somehow.")) & {"grammar", "modal-absent"} == {"modal-absent"}


def test_vague_term_fires_on_an_unverifiable_adjective():
    assert "vague-term" in _codes(_req("The system shall be fast when loading results."))


def test_vague_term_ignores_the_word_inside_a_quoted_string():
    # The negative case that matters. A requirement about a *message* containing the
    # word "fast" is not a vague requirement.
    ok = _req('The system shall display the message "Fast delivery available" on checkout.')
    assert "vague-term" not in _codes(ok)


def test_two_obligations_fires_on_a_joined_requirement():
    joined = _req("The system shall authenticate the user and shall log the attempt.")
    assert "two-obligations" in _codes(joined)


def test_two_obligations_ignores_an_ordinary_conjunction():
    # "email and password" is one idea. A rule that split it would make every real
    # requirement a finding.
    single = _req("The system shall authenticate users with an email and a password.")
    assert "two-obligations" not in _codes(single)


def test_unquantified_fires_on_a_measurable_property_with_no_number():
    assert "unquantified" in _codes(_req("The system shall provide high availability."))


def test_unquantified_accepts_a_stated_threshold():
    quantified = _req("The system shall sustain 99.95% availability measured monthly.")
    assert "unquantified" not in _codes(quantified)


def test_unquantified_ignores_a_requirement_about_nothing_measurable():
    assert "unquantified" not in _codes(_req("The system shall record the user's locale."))


def test_passive_actor_fires_when_nobody_is_named():
    assert "passive-actor" in _codes(_req("Credentials shall be validated."))


def test_passive_actor_accepts_a_named_actor():
    named = _req("Credentials shall be validated by the authentication service.")
    assert "passive-actor" not in _codes(named)


def test_obligation_mismatch_fires_when_the_declared_field_disagrees():
    mismatched = _req("The system should retry failed deliveries.", obligation="must")
    assert "obligation-mismatch" in _codes(mismatched)


def test_obligation_mismatch_silent_when_they_agree_or_none_is_declared():
    assert "obligation-mismatch" not in _codes(
        _req("The system should retry failed deliveries.", obligation="should")
    )
    assert "obligation-mismatch" not in _codes(_req("The system should retry deliveries."))


def test_a_well_formed_requirement_produces_no_findings_at_all():
    """The single most important negative case in this module.

    If a correctly written requirement produces findings, every finding this linter
    makes becomes noise and the feature is worse than absent.
    """
    clean = _req(
        "The payment service shall reject a transaction whose amount exceeds 10000 ZAR.",
        obligation="shall",
        kind="functional",
    )
    assert lint_requirement(clean) == []


def test_requirement_with_no_text_is_never_linted():
    # Tier 1: the statement lives in a tracker Governova never calls. Absent text is
    # unknown, and a linter that invented findings from an id would be fabricating.
    assert lint_requirement(Requirement(id="REQ-500", origin="referenced")) == []


def test_duplicate_ids_are_reported_across_the_set():
    findings = lint([_req("The system shall do X."), _req("The system shall do Y.")])
    assert any(f.code == "duplicate-id" for f in findings)


def test_unique_ids_produce_no_duplicate_finding():
    findings = lint(
        [_req("The system shall do X.", "REQ-001"), _req("The system shall do Y.", "REQ-002")]
    )
    assert not any(f.code == "duplicate-id" for f in findings)


def test_lint_output_is_deterministic():
    requirements = [_req("The system shall be fast.", "REQ-9"), _req("Users log in.", "REQ-2")]
    assert [f.code for f in lint(requirements)] == [f.code for f in lint(requirements)]


# ─── The manifest contract ───────────────────────────────────────────────────


def test_manifest_parses_a_well_formed_document():
    requirements = parse_manifest(
        _manifest(
            {
                "id": "REQ-001",
                "statement": "The system shall authenticate users.",
                "kind": "functional",
                "obligation": "shall",
            }
        )
    )
    assert [r.id for r in requirements] == ["REQ-001"]
    assert requirements[0].kind == "functional"


@pytest.mark.parametrize(
    ("payload", "match"),
    [
        ("not json at all", "not valid JSON"),
        (json.dumps([]), "must be an object"),
        (json.dumps({"requirements": []}), "missing `schema_version`"),
        (_manifest(version="9.0"), "not compatible"),
        (json.dumps({"schema_version": "1.0", "requirements": {}}), "must be a list"),
        (_manifest({"statement": "no id here"}), "has no `id`"),
        (_manifest({"id": "REQ-1", "kind": "invented"}), "is not one of"),
        (_manifest({"id": "REQ-1", "obligation": "ought"}), "is not one of"),
    ],
)
def test_manifest_rejects_malformed_documents(payload, match):
    # Strict on purpose: a manifest is a published contract other people's exporters
    # write against, and silently skipping a record they believed was accepted would
    # make the contract untestable from their side.
    with pytest.raises(ManifestError, match=match):
        parse_manifest(payload)


# ─── Tier detection and the rule that makes this adoptable ───────────────────


def test_repository_with_no_requirements_is_tier_zero(tmp_path):
    (tmp_path / "app.py").write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
    found = read_referenced(tmp_path, ReaderConfig())
    assert found.tier is Tier.INVISIBLE
    assert found.requirements == {}


def test_tier_zero_traces_to_unknown_and_produces_no_findings(tmp_path):
    """The rule the whole design rests on: never punish a team for what we cannot see."""
    report = trace(read_referenced(tmp_path, ReaderConfig()))
    assert report.tier is Tier.INVISIBLE
    assert not report.assessed
    assert report.findings == []
    assert report.coverage_pct is None


def test_citations_in_source_reach_tier_one(tmp_path):
    (tmp_path / "billing.py").write_text(
        "# Implements REQ-1234 — invoice totals\ndef total():\n    return 0\n", encoding="utf-8"
    )
    found = read_referenced(tmp_path, ReaderConfig())
    assert found.tier is Tier.REFERENCED
    assert set(found.requirements) == {"REQ-1234"}
    assert found.cited_by("REQ-1234", "source")


def test_a_requirement_cited_only_in_source_has_no_test(tmp_path):
    (tmp_path / "billing.py").write_text("# REQ-1234\nx = 1\n", encoding="utf-8")
    report = trace(read_referenced(tmp_path, ReaderConfig()))
    assert report.assessed
    assert [f.code for f in report.findings] == ["requirement-without-test"]
    assert report.untested == 1


def test_a_requirement_cited_from_a_test_is_traced(tmp_path):
    (tmp_path / "billing.py").write_text("# REQ-1234\nx = 1\n", encoding="utf-8")
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_billing.py").write_text(
        "def test_total_REQ_1234():\n    # REQ-1234\n    assert True\n", encoding="utf-8"
    )
    report = trace(read_referenced(tmp_path, ReaderConfig()))
    assert report.tested == 1
    assert report.findings == []
    assert report.coverage_pct == 100.0


def test_default_prefix_does_not_invent_requirements_from_ordinary_text(tmp_path):
    # A general `[A-Z]+-\d+` pattern would read UTF-8, SHA-256, and ISO-8601 as
    # requirements. Manufacturing findings out of prose is how a governance tool
    # loses the argument on its first run.
    (tmp_path / "codec.py").write_text(
        'ENC = "UTF-8"\nHASH = "SHA-256"\nDATE = "ISO-8601"\nHTTP_2 = True\n', encoding="utf-8"
    )
    assert read_referenced(tmp_path, ReaderConfig()).tier is Tier.INVISIBLE


def test_a_configured_prefix_is_honoured(tmp_path):
    (tmp_path / "app.py").write_text("# PROJ-77 implemented here\n", encoding="utf-8")
    found = read_referenced(tmp_path, ReaderConfig(id_prefixes=("PROJ",)))
    assert set(found.requirements) == {"PROJ-77"}


def test_an_unsafe_configured_prefix_is_discarded(tmp_path):
    from governova_requirements.sources import _clean_prefixes

    # Configuration is input. A prefix reaching `re.compile` unchecked is a repository
    # handing this tool a pathological pattern.
    assert _clean_prefixes(["(a+)+", "REQ", "", "ok-ish", 12]) == ("REQ",)


def test_excluded_paths_do_not_manufacture_requirements(tmp_path):
    # A fixture file whose subject *is* requirement ids is not a citation. Tier 1
    # cannot tell the two apart by inspection, so the team that knows declares it.
    fixtures = tmp_path / "tests"
    fixtures.mkdir()
    (fixtures / "test_linter_fixtures.py").write_text("SAMPLE = 'REQ-1234'\n", encoding="utf-8")
    assert read_referenced(tmp_path, ReaderConfig()).tier is Tier.REFERENCED
    excluded = ReaderConfig(exclude=("tests/test_linter_fixtures.py",))
    assert read_referenced(tmp_path, excluded).tier is Tier.INVISIBLE


def test_exclusion_does_not_hide_real_citations_elsewhere(tmp_path):
    # The negative half: excluding a fixture must not blind the reader to the rest of
    # the repository, or the option becomes a way to suppress findings.
    fixtures = tmp_path / "tests"
    fixtures.mkdir()
    (fixtures / "test_linter_fixtures.py").write_text("SAMPLE = 'REQ-1234'\n", encoding="utf-8")
    (tmp_path / "billing.py").write_text("# REQ-777\n", encoding="utf-8")
    found = read_referenced(tmp_path, ReaderConfig(exclude=("tests/test_linter_fixtures.py",)))
    assert set(found.requirements) == {"REQ-777"}


def test_generated_and_vendored_trees_are_skipped(tmp_path):
    vendored = tmp_path / "node_modules" / "pkg"
    vendored.mkdir(parents=True)
    (vendored / "index.js").write_text("// REQ-9999\n", encoding="utf-8")
    assert read_referenced(tmp_path, ReaderConfig()).tier is Tier.INVISIBLE


def test_commit_trailers_are_citations_but_prose_is_not():
    from governova_requirements.sources import _TRAILER

    # Found by running this tool on its own repository: a commit *quoting* the
    # ADR's example sentence was read as citing a requirement. A trailer is a
    # deliberate declaration; a mention in prose is people discussing requirements.
    assert _TRAILER.match("Requirement: REQ-1234")
    assert _TRAILER.match("Refs: REQ-1234, REQ-1235")
    assert not _TRAILER.match("cite REQ-1234 in a test name or a commit trailer")
    assert not _TRAILER.match("  Requirement: REQ-1234")


def test_collect_runs_every_registered_reader(tmp_path):
    assert set(registered_readers()) >= {"referenced", "manifest"}
    (tmp_path / "app.py").write_text("# REQ-1\n", encoding="utf-8")
    (tmp_path / "requirements.governova.json").write_text(
        _manifest({"id": "REQ-1", "statement": "The system shall do X."}), encoding="utf-8"
    )
    found = collect(tmp_path)
    # The manifest carries text and the citation does not, so the richer reading wins
    # while the citation is still recorded.
    assert found.tier is Tier.EXPORTED
    assert found.requirements["REQ-1"].has_text
    assert found.cited_by("REQ-1", "source")


def test_a_broken_manifest_is_reported_not_swallowed(tmp_path):
    (tmp_path / "requirements.governova.json").write_text("{ broken", encoding="utf-8")
    found = collect(tmp_path)
    assert found.tier is Tier.INVISIBLE
    assert any("requirements.governova.json" in note for note in found.notes)


def test_declared_requirement_with_no_implementation_is_reported(tmp_path):
    (tmp_path / "requirements.governova.json").write_text(
        _manifest({"id": "REQ-42", "statement": "The system shall export a report."}),
        encoding="utf-8",
    )
    report = trace(collect(tmp_path))
    assert any(f.code == "requirement-without-implementation" for f in report.findings)


def test_untraced_check_is_silent_at_tier_one():
    # At tier 1 the requirement set *is* the set of citations, so every requirement is
    # cited by construction. Asking the question there would answer itself.
    found = RequirementSet(
        tier=Tier.REFERENCED,
        requirements={"REQ-1": Requirement(id="REQ-1")},
        citations=[Citation("REQ-1", "app.py", "test", 1)],
    )
    assert not any(
        f.code == "requirement-without-implementation" for f in trace(found).findings
    )
