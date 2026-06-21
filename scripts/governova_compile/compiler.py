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
from governova_compile.parsers import parse_constitution
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
    return path.read_text(encoding="utf-8")


def compile_index(repo_root: Path | None = None) -> CompiledIndex:
    """Compile the full constitutional database into a CompiledIndex."""
    root = repo_root or resolve_repo_root()

    framework = [
        FrameworkPrimitive(id=e.id, title=e.title, summary=e.summary, path=e.relative_path)
        for e in FRAMEWORK_REGISTRY
        if (root / e.relative_path).is_file()
    ]

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

    domains: list[Constitution] = []
    for dpath in find_domain_constitutions(root):
        # Domain constitutions use the D-{DOMAIN} format; we parse standards
        # generically. Phase/rank are unknown for domains, left None.
        domains.append(
            parse_constitution(
                _read(dpath),
                constitution_id="C99",  # placeholder; domains are not numbered C0-10
                number=99,
                name=dpath.stem,
                phase=None,
                path=str(dpath.relative_to(root)),
                hierarchy_rank=None,
                binds_implementation=False,
            )
        )

    runbooks: list[Runbook] = []
    for rpath in find_runbooks(root):
        rb = parse_runbook(rpath, root)
        if rb is not None:
            runbooks.append(rb)

    adrs: list[ADR] = []
    for apath in find_adrs(root):
        adr = parse_adr(apath, root)
        if adr is not None:
            adrs.append(adr)

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
