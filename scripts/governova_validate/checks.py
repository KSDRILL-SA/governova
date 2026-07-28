"""Integrity checks over a compiled index.

Each check returns a list of IntegrityIssue. Errors fail the run unconditionally;
warnings fail only under --strict.
"""

from __future__ import annotations

from governova_compile.schema import CompiledIndex, IntegrityIssue, Severity


def _all_standard_ids(index: CompiledIndex) -> set[str]:
    ids: set[str] = set()
    for constitution in (*index.constitutions, *index.domains):
        for std in constitution.standards:
            ids.add(std.id)
    return ids


def check_references(index: CompiledIndex) -> list[IntegrityIssue]:
    """Every `depends_on` and `cross_references` target must resolve to a real standard."""
    known = _all_standard_ids(index)
    issues: list[IntegrityIssue] = []
    for constitution in (*index.constitutions, *index.domains):
        for std in constitution.standards:
            for ref in (*std.depends_on, *std.cross_references):
                if ref.standard_id not in known:
                    issues.append(
                        IntegrityIssue(
                            severity=Severity.SEV2,
                            code="orphan-reference",
                            message=(
                                f"{std.id} references {ref.standard_id}, "
                                f"which is not a defined standard."
                            ),
                            source_path=std.source_path,
                            source_line=std.source_line,
                        )
                    )
    return issues


def check_anti_patterns(index: CompiledIndex) -> list[IntegrityIssue]:
    """Each anti-pattern ID must derive from its parent standard's ID."""
    issues: list[IntegrityIssue] = []
    for constitution in (*index.constitutions, *index.domains):
        for std in constitution.standards:
            for ap in std.anti_patterns:
                # AP-S8.9a → implied standard S8.9
                implied = ap.id[len("AP-") :].rstrip("abcdefghijklmnopqrstuvwxyz")
                if implied != std.id:
                    issues.append(
                        IntegrityIssue(
                            severity=Severity.SEV3,
                            code="anti-pattern-mismatch",
                            message=(
                                f"Anti-pattern {ap.id} is listed under {std.id} "
                                f"but its ID implies standard {implied}."
                            ),
                            source_path=std.source_path,
                            source_line=std.source_line,
                        )
                    )
    return issues


def check_practices(index: CompiledIndex) -> list[IntegrityIssue]:
    """Practices should reference standards that exist."""
    known = _all_standard_ids(index)
    issues: list[IntegrityIssue] = []
    for impl in index.implementations:
        for practice in impl.practices:
            for sid in practice.satisfies_standards:
                if sid not in known:
                    issues.append(
                        IntegrityIssue(
                            severity=Severity.SEV3,
                            code="practice-orphan-standard",
                            message=(
                                f"Practice {practice.id} ({impl.stack}) cites {sid}, "
                                f"which is not a defined standard."
                            ),
                            source_path=practice.source_path,
                            source_line=practice.source_line,
                        )
                    )
    return issues


def check_hierarchy(index: CompiledIndex) -> list[IntegrityIssue]:
    """Every core constitution must appear exactly once in the hierarchy, and the
    hierarchy must not reference unknown constitutions."""
    issues: list[IntegrityIssue] = []
    core_ids = {c.id for c in index.constitutions}
    hierarchy = index.hierarchy

    for cid in core_ids:
        if cid not in hierarchy:
            issues.append(
                IntegrityIssue(
                    severity=Severity.SEV1,
                    code="hierarchy-missing",
                    message=f"Constitution {cid} is not present in the conflict hierarchy.",
                )
            )
    for cid in hierarchy:
        if cid not in core_ids:
            issues.append(
                IntegrityIssue(
                    severity=Severity.SEV1,
                    code="hierarchy-unknown",
                    message=f"Hierarchy references unknown constitution {cid}.",
                )
            )
    return issues


def check_phases(index: CompiledIndex) -> list[IntegrityIssue]:
    """The phase map must agree with each constitution's declared phase."""
    issues: list[IntegrityIssue] = []
    for constitution in index.constitutions:
        if constitution.phase is None:
            continue
        members = index.phases.get(constitution.phase, [])
        if constitution.id not in members:
            issues.append(
                IntegrityIssue(
                    severity=Severity.SEV1,
                    code="phase-mismatch",
                    message=(
                        f"{constitution.id} declares phase {constitution.phase.value} "
                        f"but is absent from the phase map for that phase."
                    ),
                    source_path=constitution.path,
                )
            )
    return issues


def check_standard_completeness(index: CompiledIndex) -> list[IntegrityIssue]:
    """Full (non-abbreviated) standards should carry a rationale and at least one
    anti-pattern, per C0 §3.2 SR-2 and SR-3. Abbreviated standards are exempt."""
    issues: list[IntegrityIssue] = []
    for constitution in index.constitutions:
        for std in constitution.standards:
            if std.abbreviated:
                continue
            if not std.statement:
                issues.append(
                    IntegrityIssue(
                        severity=Severity.SEV2,
                        code="missing-statement",
                        message=f"{std.id} has no statement text.",
                        source_path=std.source_path,
                        source_line=std.source_line,
                    )
                )
            if not std.rationale:
                issues.append(
                    IntegrityIssue(
                        severity=Severity.SEV3,
                        code="missing-rationale",
                        message=f"{std.id} has no rationale (C0 §3.2 SR-2).",
                        source_path=std.source_path,
                        source_line=std.source_line,
                    )
                )
            if not std.anti_patterns:
                issues.append(
                    IntegrityIssue(
                        severity=Severity.SEV3,
                        code="missing-anti-pattern",
                        message=f"{std.id} has no anti-pattern (C0 §3.2 SR-3).",
                        source_path=std.source_path,
                        source_line=std.source_line,
                    )
                )
    return issues


def check_domain_extensions(index: CompiledIndex) -> list[IntegrityIssue]:
    """Layer 4 discipline: a domain standard must extend the core, not float free.

    A domain extension exists to add what an industry requires *on top of* the
    universal core (master.md §9). A domain standard that declares no core
    standard it extends has no anchor — it cannot be conflict-checked against the
    core, and it is indistinguishable from a standard that belongs in Layer 2.
    Each one must also carry its own namespace, rationale, and anti-pattern.
    """
    core_ids = {std.id for c in index.constitutions for std in c.standards}
    issues: list[IntegrityIssue] = []

    for domain in index.domains:
        for std in domain.standards:
            if not std.id.startswith(f"{domain.id}."):
                issues.append(
                    IntegrityIssue(
                        severity=Severity.SEV1,
                        code="domain-namespace-mismatch",
                        message=f"{std.id} is declared in {domain.id} but uses another namespace.",
                        source_path=std.source_path,
                        source_line=std.source_line,
                    )
                )
            extended = [r.standard_id for r in std.depends_on if r.standard_id in core_ids]
            if not extended:
                issues.append(
                    IntegrityIssue(
                        severity=Severity.SEV2,
                        code="domain-extends-nothing",
                        message=(
                            f"{std.id} declares no core standard it extends "
                            f"(master.md §9 — a domain adds to the universal core)."
                        ),
                        source_path=std.source_path,
                        source_line=std.source_line,
                    )
                )
            if not std.rationale:
                issues.append(
                    IntegrityIssue(
                        severity=Severity.SEV3,
                        code="missing-rationale",
                        message=f"{std.id} has no rationale (C0 §3.2 SR-2).",
                        source_path=std.source_path,
                        source_line=std.source_line,
                    )
                )
            if not std.anti_patterns:
                issues.append(
                    IntegrityIssue(
                        severity=Severity.SEV3,
                        code="missing-anti-pattern",
                        message=f"{std.id} has no anti-pattern (C0 §3.2 SR-3).",
                        source_path=std.source_path,
                        source_line=std.source_line,
                    )
                )
    return issues


ALL_CHECKS = (
    check_references,
    check_anti_patterns,
    check_practices,
    check_hierarchy,
    check_phases,
    check_standard_completeness,
    check_domain_extensions,
)
