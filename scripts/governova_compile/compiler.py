"""Orchestrates the full compile: discover → parse → assemble CompiledIndex."""

from __future__ import annotations

import subprocess
from datetime import UTC, datetime
from pathlib import Path

from governova_compile.discovery import (
    CONSTITUTION_REGISTRY,
    FRAMEWORK_REGISTRY,
    HIERARCHY_ORDER,
    IMPLEMENTATION_REGISTRY,
    find_adrs,
    find_domain_constitutions,
    find_runbooks,
    resolve_repo_root,
)
from governova_compile.metadata import parse_adr, parse_implementation, parse_runbook
from governova_compile.parsers import parse_constitution, parse_domain_constitution
from governova_compile.schema import (
    ADR,
    CompiledIndex,
    Constitution,
    FrameworkPrimitive,
    Implementation,
    IntegrityReport,
    Phase,
    Runbook,
)


def _git_sha(repo_root: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        return result.stdout.strip() or None
    except (subprocess.SubprocessError, OSError):
        return None


def _read(path: Path) -> str:
    # Normalise line endings so the compiled index is byte-identical regardless
    # of the checkout platform (Windows CRLF vs Linux LF). Without this, a
    # CRLF working tree bakes \r into the parsed content and the content
    # checksum diverges from a CI compile on LF. See writer._index_body_for_checksum.
    return path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")


# Each gather below reads one registry or directory and returns one list. They
# were the body of `compile_index`, which made that function a sequence of six
# unrelated loops with nothing to name the boundaries between them (`S13.6`).


def _gather_framework(root: Path) -> list[FrameworkPrimitive]:
    return [
        FrameworkPrimitive(id=e.id, title=e.title, summary=e.summary, path=e.relative_path)
        for e in FRAMEWORK_REGISTRY
        if (root / e.relative_path).is_file()
    ]


def _gather_constitutions(root: Path) -> list[Constitution]:
    constitutions: list[Constitution] = []
    for entry in CONSTITUTION_REGISTRY:
        path = root / entry.relative_path
        if not path.is_file():
            continue
        constitutions.append(
            parse_constitution(
                _read(path),
                constitution_id=entry.id,
                number=entry.number,
                name=entry.name,
                phase=entry.phase,
                path=entry.relative_path,
                hierarchy_rank=entry.hierarchy_rank,
                binds_implementation=entry.binds_implementation,
            )
        )
    return constitutions


def _gather_implementations(root: Path) -> list[Implementation]:
    implementations: list[Implementation] = []
    for impl in IMPLEMENTATION_REGISTRY:
        path = root / impl.relative_path
        if not path.is_file():
            continue
        implementations.append(
            parse_implementation(
                path,
                stack=impl.stack,
                binds_constitution=impl.binds_constitution,
                name=impl.name,
                repo_root=root,
            )
        )
    return implementations


def _gather_domains(root: Path) -> list[Constitution]:
    return [
        parse_domain_constitution(
            _read(dpath),
            entry_id=domain_entry.id,
            name=domain_entry.name,
            slug=domain_entry.slug,
            regulatory_basis=list(domain_entry.regulatory_basis),
            reference_systems=list(domain_entry.reference_systems),
            path=dpath.relative_to(root).as_posix(),
        )
        for domain_entry, dpath in find_domain_constitutions(root)
    ]


def _gather_runbooks(root: Path) -> list[Runbook]:
    """Unparseable runbooks are skipped, not fatal — one bad file must not stop a compile."""
    return [rb for rpath in find_runbooks(root) if (rb := parse_runbook(rpath, root)) is not None]


def _gather_adrs(root: Path) -> list[ADR]:
    return [adr for apath in find_adrs(root) if (adr := parse_adr(apath, root)) is not None]


def compile_index(repo_root: Path | None = None) -> CompiledIndex:
    """Compile the full constitutional database into a CompiledIndex."""
    root = repo_root or resolve_repo_root()

    framework = _gather_framework(root)
    constitutions = _gather_constitutions(root)
    implementations = _gather_implementations(root)
    domains = _gather_domains(root)
    runbooks = _gather_runbooks(root)
    adrs = _gather_adrs(root)

    phases: dict[Phase, list[str]] = {}
    for c in constitutions:
        if c.phase is not None:
            phases.setdefault(c.phase, []).append(c.id)

    integrity = IntegrityReport(
        standards_extracted=sum(len(c.standards) for c in constitutions),
        anti_patterns_extracted=sum(
            len(s.anti_patterns) for c in constitutions for s in c.standards
        ),
        bindings_extracted=sum(len(i.practices) + len(i.bindings) for i in implementations),
        domain_standards_extracted=sum(len(d.standards) for d in domains),
        domain_anti_patterns_extracted=sum(
            len(s.anti_patterns) for d in domains for s in d.standards
        ),
    )

    index = CompiledIndex(
        compiled_at=datetime.now(UTC),
        source_commit_sha=_git_sha(root),
        checksum="",  # filled by writer
        framework=framework,
        constitutions=constitutions,
        implementations=implementations,
        domains=domains,
        runbooks=runbooks,
        adrs=adrs,
        hierarchy=[c for c in HIERARCHY_ORDER if any(con.id == c for con in constitutions)],
        phases=phases,
        integrity=integrity,
    )
    return index
