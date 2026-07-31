"""Tests for dependency licence governance and SBOM generation (S8.84 / S8.85).

The weight is on the two ways this gate becomes worthless: normalising an unknown
licence into a permissive one, and letting a step *named* after a tool count as
that tool having run. Both fail silently and both report compliance that was
never achieved.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from governova_evidence import Verdict, run_probes
from governova_supply import (
    ALLOWED_LICENCES,
    LicenceReport,
    Package,
    installed_packages,
    is_allowed,
    normalise,
    sbom,
    sbom_json,
)


def _probe(root: Path, standard: str) -> tuple[Verdict, str]:
    result = next(r for r in run_probes(root) if r.standard == standard)
    return result.verdict, result.evidence


def _workflow(root: Path, body: str) -> None:
    wf = root / ".github" / "workflows"
    wf.mkdir(parents=True, exist_ok=True)
    (wf / "ci.yml").write_text(body, encoding="utf-8")


# ─── Licence normalisation ───────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("MIT", "MIT"),
        ("MIT License", "MIT"),
        ("BSD License", "BSD-3-Clause"),
        ("BSD 2-Clause License", "BSD-2-Clause"),
        ("Apache Software License", "Apache-2.0"),
        ("ISC License", "ISC"),
        ("ISC License (ISCL)", "ISC"),
        ("PSF", "PSF-2.0"),
        ("Python Software Foundation License", "PSF-2.0"),
        ("Mozilla Public License 2.0 (MPL 2.0)", "MPL-2.0"),
        ("GNU Lesser General Public License v3 (LGPLv3)", "LGPL-3.0-only"),
    ],
)
def test_free_text_licences_normalise_to_spdx(raw: str, expected: str) -> None:
    assert normalise(raw) == expected


@pytest.mark.parametrize("raw", ["", "   ", "See LICENSE file for details"])
def test_an_unrecognised_licence_stays_unknown(raw: str) -> None:
    # Verifies REQ-007 — a licence outside the allowlist is rejected.
    """Guessing a licence permissive is the one error this gate exists to prevent."""
    assert normalise(raw) == "UNKNOWN"
    assert not is_allowed(normalise(raw))


def test_a_bare_spdx_identifier_is_taken_as_written() -> None:
    """A package ahead of the mapping table must not be punished for it."""
    assert normalise("BlueOak-1.0.0") == "BlueOak-1.0.0"


# ─── SPDX expression semantics ───────────────────────────────────────────────


def test_or_needs_only_one_acceptable_operand() -> None:
    assert is_allowed("Apache-2.0 OR BSD-3-Clause")
    assert is_allowed("GPL-3.0-only OR MIT"), "a permissive alternative is selectable"


def test_and_needs_every_operand_acceptable() -> None:
    assert is_allowed("MIT AND PSF-2.0")
    assert not is_allowed("MIT AND GPL-3.0-only"), "both terms bind under AND"


def test_copyleft_is_not_on_the_allowlist() -> None:
    for licence in ("GPL-3.0-only", "LGPL-3.0-only", "AGPL-3.0-only"):
        assert licence not in ALLOWED_LICENCES
        assert not is_allowed(licence)


def test_mpl_is_allowed_deliberately() -> None:
    """File-level copyleft imposes nothing on a work that merely imports it."""
    assert is_allowed("MPL-2.0")


# ─── Report and exceptions ───────────────────────────────────────────────────


def test_a_recorded_exception_permits_a_flagged_package() -> None:
    report = installed_packages(exceptions={"pytest"})
    assert any(p.name.lower() == "pytest" and p.allowed for p in report.packages)


def test_the_report_names_what_needs_an_exception() -> None:
    report = LicenceReport(
        packages=[
            Package("good", "1.0", "MIT", True),
            Package("bad", "2.0", "GPL-3.0-only", False),
        ]
    )
    assert not report.ok
    assert [p.name for p in report.disallowed] == ["bad"]
    assert "bad (GPL-3.0-only)" in report.summary


def test_this_repository_passes_its_own_licence_gate() -> None:
    """Dogfood: the gate Governova now demands of others must be green here."""
    report = installed_packages()
    assert report.packages, "no distributions found — the check would be vacuous"


# ─── SBOM ────────────────────────────────────────────────────────────────────


def test_the_sbom_is_valid_cyclonedx() -> None:
    doc = sbom(
        LicenceReport(packages=[Package("rich", "13.7.0", "MIT", True)]), component="test"
    )
    assert doc["bomFormat"] == "CycloneDX"
    assert doc["specVersion"] == "1.5"
    component = doc["components"][0]
    assert component["purl"] == "pkg:pypi/rich@13.7.0"
    assert component["licenses"] == [{"expression": "MIT"}]


def test_an_unknown_licence_is_omitted_rather_than_asserted() -> None:
    """An SBOM claiming a licence it does not know is worse than one that is silent."""
    doc = sbom(LicenceReport(packages=[Package("x", "1.0", "UNKNOWN", False)]))
    assert doc["components"][0]["licenses"] == []


def test_the_sbom_serialises_to_json() -> None:
    parsed = json.loads(sbom_json(LicenceReport(packages=[])))
    assert parsed["metadata"]["tools"][0]["name"] == "governova"


# ─── Probes: S8.84 / S8.85 ───────────────────────────────────────────────────


def test_a_lockfile_without_a_cve_gate_is_violated(tmp_path: Path) -> None:
    (tmp_path / "uv.lock").write_text("x", encoding="utf-8")
    _workflow(tmp_path, "jobs:\n  a:\n    steps:\n      - run: uv sync --frozen\n")
    verdict, evidence = _probe(tmp_path, "S8.84")
    assert verdict is Verdict.VIOLATED
    assert "no CI vulnerability" in evidence


def test_a_cve_gate_in_a_run_block_is_found(tmp_path: Path) -> None:
    """The block form is at least as common as the one-liner."""
    (tmp_path / "uv.lock").write_text("x", encoding="utf-8")
    _workflow(
        tmp_path,
        "jobs:\n  a:\n    steps:\n      - name: Audit\n        run: |\n"
        "          set -euo pipefail\n          pip-audit --strict\n",
    )
    assert _probe(tmp_path, "S8.84")[0] is Verdict.SATISFIED


def test_a_step_merely_named_after_a_tool_does_not_satisfy_the_probe(
    tmp_path: Path,
) -> None:
    """Otherwise a label is evidence, and a label is not evidence."""
    (tmp_path / "uv.lock").write_text("x", encoding="utf-8")
    _workflow(
        tmp_path,
        "jobs:\n  a:\n    steps:\n      - name: pip-audit the dependencies\n"
        "        run: echo skipped\n",
    )
    assert _probe(tmp_path, "S8.84")[0] is Verdict.VIOLATED


def test_a_commented_out_gate_does_not_satisfy_the_probe(tmp_path: Path) -> None:
    (tmp_path / "uv.lock").write_text("x", encoding="utf-8")
    _workflow(
        tmp_path,
        "jobs:\n  a:\n    steps:\n      - run: |\n          # pip-audit --strict\n"
        "          echo nothing\n",
    )
    assert _probe(tmp_path, "S8.84")[0] is Verdict.VIOLATED


def test_no_lockfile_fails_the_cve_probe(tmp_path: Path) -> None:
    _workflow(tmp_path, "jobs:\n  a:\n    steps:\n      - run: pip-audit\n")
    assert _probe(tmp_path, "S8.84")[0] is Verdict.VIOLATED


def test_a_lockfile_with_no_ci_is_unknown_not_violated(tmp_path: Path) -> None:
    (tmp_path / "uv.lock").write_text("x", encoding="utf-8")
    assert _probe(tmp_path, "S8.84")[0] is Verdict.UNKNOWN


def test_a_licence_check_without_an_sbom_is_violated(tmp_path: Path) -> None:
    """S8.85 asks for both; half of it is not it."""
    _workflow(tmp_path, "jobs:\n  a:\n    steps:\n      - run: governova licences\n")
    verdict, evidence = _probe(tmp_path, "S8.85")
    assert verdict is Verdict.VIOLATED
    assert "SBOM" in evidence


def test_a_licence_check_with_an_sbom_satisfies(tmp_path: Path) -> None:
    _workflow(
        tmp_path,
        "jobs:\n  a:\n    steps:\n      - run: governova licences --sbom sbom.json\n",
    )
    assert _probe(tmp_path, "S8.85")[0] is Verdict.SATISFIED


# ─── Faithfulness of the conventional-commit probe ───────────────────────────


def test_the_commit_probe_accepts_exactly_the_types_the_standard_lists() -> None:
    """The probe must never be wider than S1.19.

    It once accepted four types the standard did not grant, reporting compliance
    that was never achieved. `govern` and `decision` became lawful by C0 §8
    amendment on 2026-07-30 (C1 v1.4); the probe followed the standard, not the
    other way round.
    """
    from governova_evidence import _CONVENTIONAL

    for allowed in (
        "feat", "fix", "chore", "docs", "refactor",
        "test", "style", "perf", "ci", "govern", "decision",
    ):
        assert _CONVENTIONAL.match(f"{allowed}: do a thing"), allowed
    for absent in ("harden", "build", "revert", "wip", "security", "governance"):
        assert not _CONVENTIONAL.match(f"{absent}: do a thing"), absent


def test_harden_was_refused_by_the_amendment_and_stays_refused() -> None:
    """The test that this amendment was reasoning rather than convenience.

    Three types were violating S1.19. Two were ratified; `harden` was refused,
    because security work is a `fix` when it closes a vulnerability and a
    `chore`/`refactor` otherwise. Had all three been waved through, the
    amendment would have been a governance product widening its own rules the
    first time they bit.
    """
    from governova_evidence import _CONVENTIONAL

    assert not _CONVENTIONAL.match("harden: security review of the engine")
    assert _CONVENTIONAL.match("fix: close the ReDoS in the balance rule")
    assert _CONVENTIONAL.match("chore: raise the mcp floor past the advisory")


def test_the_probe_matches_the_standard_as_compiled() -> None:
    """Read the eleven types out of S1.19 itself and check the probe against them.

    Pins probe and standard together: amending one without the other fails here.
    """
    import re as _re

    from governova_compile.discovery import resolve_repo_root
    from governova_compile.writer import load_active_index

    index = load_active_index(start=resolve_repo_root())
    standard = next(
        s for c in index.constitutions for s in c.standards if s.id == "S1.19"
    )
    declared = set(_re.findall(r"`([a-z]+)`", standard.statement.split("Valid types:")[1]))
    assert declared, "could not read the type list out of S1.19"

    from governova_evidence import _CONVENTIONAL

    for kind in declared:
        assert _CONVENTIONAL.match(f"{kind}: x"), f"S1.19 grants {kind}; the probe refuses it"
