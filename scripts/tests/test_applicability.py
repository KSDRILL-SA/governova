"""Layer 4 law binds the projects that declared the sector, and no others.

The defect these cover was found on the first repository Governova ever read
that it had not written: `governova-enforce .` failed the build with 201 blocking
findings, **199 of them `AP-D-FINTECH.1a`**, against a proposed profile that left
`domains` undeclared — while `governova onboard`, in the same session, printed
"no Layer 4 domain declared — sector standards are not counted".

Two surfaces, two different bodies of law. `governova_project.applicable_standards`
had always filtered; the scanner never did, so every surface reading `scan_paths`
received every domain rule regardless of what the project had adopted.
"""

from __future__ import annotations

from pathlib import Path

from governova_checks import Finding, domain_of, for_declared_domains

MONEY = "export type Invoice = { amount: number }\n"  # AP-D-FINTECH.1a, high → blocks
CORE = "localStorage.setItem('access_token', t);\n"  # AP-S3.14a, high → blocks


def _finding(standard: str) -> Finding:
    return Finding(
        file="a.ts",
        line=1,
        col=1,
        anti_pattern=f"AP-{standard}a",
        standard=standard,
        message="",
        match="",
        confidence="high",
    )


# ── the partition itself ─────────────────────────────────────────────────────


def test_a_core_standard_has_no_domain() -> None:
    assert domain_of("S1.68") is None
    assert domain_of("S13.4") is None


def test_a_domain_standard_names_its_domain() -> None:
    assert domain_of("D-FINTECH.1") == "D-FINTECH"
    assert domain_of("D-GOVTECH.12") == "D-GOVTECH"


def test_core_findings_survive_an_empty_declaration() -> None:
    """Core standards apply to every system; nothing about them is opt-in."""
    result = for_declared_domains([_finding("S1.68")], [])
    assert len(result.findings) == 1
    assert not result.withheld


def test_an_undeclared_domain_is_withheld() -> None:
    result = for_declared_domains([_finding("D-FINTECH.1")], [])
    assert not result.findings
    assert len(result.withheld) == 1
    assert result.withheld_domains == ["D-FINTECH"]


def test_a_declared_domain_is_enforced() -> None:
    result = for_declared_domains([_finding("D-FINTECH.1")], ["D-FINTECH"])
    assert len(result.findings) == 1
    assert not result.withheld


def test_declaring_one_domain_does_not_adopt_another() -> None:
    findings = [_finding("D-FINTECH.1"), _finding("D-EDTECH.2"), _finding("S1.68")]
    result = for_declared_domains(findings, ["D-FINTECH"])
    assert {f.standard for f in result.findings} == {"D-FINTECH.1", "S1.68"}
    assert result.withheld_domains == ["D-EDTECH"]


def test_no_profile_and_an_empty_profile_are_the_same_state() -> None:
    """A project with no profile has adopted no sector, exactly like one whose
    profile leaves the field commented out. That is where every adopter starts."""
    findings = [_finding("D-FINTECH.1")]
    assert for_declared_domains(findings, None).withheld == for_declared_domains(
        findings, []
    ).withheld


def test_the_declaration_is_case_insensitive() -> None:
    result = for_declared_domains([_finding("D-FINTECH.1")], ["d-fintech"])
    assert len(result.findings) == 1


def test_withholding_is_never_silent() -> None:
    """A gate that quietly stops checking something is the same defect in the
    opposite direction, so the note names the domain and the remedy."""
    note = for_declared_domains([_finding("D-FINTECH.1")], []).note
    assert "D-FINTECH" in note
    assert "governance/project.toml" in note
    assert for_declared_domains([_finding("S1.68")], []).note == ""


# ── the surfaces ─────────────────────────────────────────────────────────────


def _write(tmp_path: Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return str(p)


def test_enforce_does_not_block_on_an_undeclared_domain(tmp_path: Path) -> None:
    """The measured defect, reduced to one file: a build failed on law the
    project had never adopted."""
    from governova_enforce.__main__ import app
    from typer.testing import CliRunner

    f = _write(tmp_path, "money.ts", MONEY)
    result = CliRunner().invoke(app, [f, "--no-default-ignore", "--mode", "block"])
    assert result.exit_code == 0
    assert "D-FINTECH" in result.stdout  # withheld, and said so


def test_enforce_still_blocks_on_a_core_standard(tmp_path: Path) -> None:
    """The filter narrows Layer 4 only. Core law is not opt-in and never was."""
    from governova_enforce.__main__ import app
    from typer.testing import CliRunner

    f = _write(tmp_path, "leak.ts", CORE)
    result = CliRunner().invoke(app, [f, "--no-default-ignore", "--mode", "block"])
    assert result.exit_code == 1
    assert "AP-S3.14a" in result.stdout


def test_enforce_blocks_once_the_domain_is_declared(tmp_path: Path) -> None:
    from governova_enforce.__main__ import app
    from typer.testing import CliRunner

    f = _write(tmp_path, "money.ts", MONEY)
    result = CliRunner().invoke(
        app, [f, "--no-default-ignore", "--mode", "block", "--domain", "D-FINTECH"]
    )
    assert result.exit_code == 1
    assert "AP-D-FINTECH.1a" in result.stdout


def test_no_surface_applies_undeclared_layer_4_law() -> None:
    """The mechanism, asserted across every surface rather than the one that broke.

    Six modules consume `scan_paths`, and each would degrade differently: a
    merge gate failing on a foreign sector's law, a violation-rate factor
    penalising a project for breaking it, an onboarding report listing 199
    findings directly beneath a sentence saying they are not counted.

    Two holdouts, for two different reasons:

    * `governova_project` intersects against `applicable_standards`, which has
      filtered by declared domain since it was written, so a domain finding
      cannot reach its result.
    * `governova_bible` documents files and never reads a finding's standard.

    `governova_report` was a third, and is not any more. It tallied findings into
    `index.constitutions` while the index keeps `domains` in a separate list, so
    a domain finding was dropped whether or not the project declared it — the
    mirror of the defect under test here, and fixed alongside it.
    """
    from governova_compile.discovery import resolve_repo_root

    scripts = Path(resolve_repo_root()) / "scripts"
    exempt = {"governova_project", "governova_checks", "governova_bible"}
    offenders: list[str] = []
    for path in scripts.rglob("*.py"):
        if "tests" in path.parts or path.parts[-2] in exempt:
            continue
        text = path.read_text(encoding="utf-8")
        if "scan_paths(" not in text:
            continue
        if "for_declared_domains" not in text:
            offenders.append(path.relative_to(scripts).as_posix())

    assert not offenders, (
        "these surfaces scan without honouring the project's declared domains:\n  "
        + "\n  ".join(offenders)
    )
