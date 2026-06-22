"""`governova` — the unified command-line surface.

Examples:
    governova stats
    governova standards --constitution C03
    governova standard S3.14
    governova validate --strict
    governova compile --check
    governova score
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from governova_compile.compiler import compile_index
from governova_compile.discovery import resolve_repo_root
from governova_compile.schema import CompiledIndex, IntegrityIssue, Severity
from governova_compile.writer import load_index, verify_checksum, write_index
from governova_validate.checks import ALL_CHECKS
from governova_validate.links import check_links
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Governova — constitutional governance for AI-assisted development.",
)
console = Console()

_ERROR_SEVERITIES = {Severity.SEV0, Severity.SEV1, Severity.SEV2}


def _root(repo_root: Path | None) -> Path:
    try:
        return repo_root or resolve_repo_root()
    except FileNotFoundError as exc:
        console.print(f"[bold red]error:[/] {exc}")
        raise typer.Exit(code=2) from exc


def _load(root: Path) -> CompiledIndex:
    index_file = root / "compiled" / "constitution.json"
    if not index_file.is_file():
        console.print(
            "[bold red]error:[/] compiled index not found. Run [cyan]governova compile[/] first."
        )
        raise typer.Exit(code=2)
    return load_index(index_file)


def _all_standards(index: CompiledIndex) -> list:
    return [s for c in index.constitutions for s in c.standards]


@app.command()
def stats(
    repo_root: Annotated[Path | None, typer.Option("--repo-root")] = None,
) -> None:
    """Show a summary of the constitutional database."""
    index = _load(_root(repo_root))
    standards = _all_standards(index)
    aps = sum(len(s.anti_patterns) for s in standards)
    bindings = sum(len(i.bindings) + len(i.practices) for i in index.implementations)
    t = Table.grid(padding=(0, 2))
    t.add_row("Constitutions:", str(len(index.constitutions)))
    t.add_row("Standards:", str(len(standards)))
    t.add_row("Anti-patterns:", str(aps))
    t.add_row("Implementation bindings:", str(bindings))
    t.add_row("Runbooks:", str(len(index.runbooks)))
    t.add_row("ADRs:", str(len(index.adrs)))
    t.add_row("Source commit:", index.source_commit_sha or "—")
    console.print(t)


@app.command()
def standards(
    constitution: Annotated[
        str | None, typer.Option("--constitution", "-c", help="Filter by constitution id, e.g. C03.")
    ] = None,
    repo_root: Annotated[Path | None, typer.Option("--repo-root")] = None,
) -> None:
    """List standards (optionally filtered to one constitution)."""
    index = _load(_root(repo_root))
    table = Table(show_lines=False)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Title")
    count = 0
    for c in index.constitutions:
        if constitution and c.id.upper() != constitution.upper():
            continue
        for s in c.standards:
            table.add_row(s.id, s.title)
            count += 1
    console.print(table)
    console.print(f"[dim]{count} standards[/]")


@app.command()
def standard(
    standard_id: Annotated[str, typer.Argument(help="Standard id, e.g. S3.14.")],
    repo_root: Annotated[Path | None, typer.Option("--repo-root")] = None,
) -> None:
    """Show one standard in full."""
    index = _load(_root(repo_root))
    target = standard_id.upper()
    match = next((s for s in _all_standards(index) if s.id.upper() == target), None)
    if match is None:
        console.print(f"[bold red]error:[/] {standard_id} not found.")
        raise typer.Exit(code=1)
    console.print(f"[bold cyan]{match.id}[/] — [bold]{match.title}[/]")
    meta = " · ".join(
        x for x in [str(match.priority.value if match.priority else ""), match.phase_label, match.applies_to] if x
    )
    if meta:
        console.print(f"[dim]{meta}[/]")
    console.print(f"\n[bold]Standard[/]\n{match.statement}")
    if match.rationale:
        console.print(f"\n[bold]Rationale[/]\n{match.rationale}")
    if match.anti_patterns:
        console.print("\n[bold]Anti-patterns[/]")
        for ap in match.anti_patterns:
            console.print(f"  [yellow]{ap.id}[/] — {ap.description}")


@app.command()
def validate(
    strict: Annotated[bool, typer.Option("--strict", help="Treat warnings as failures.")] = False,
    skip_links: Annotated[bool, typer.Option("--skip-links")] = False,
    repo_root: Annotated[Path | None, typer.Option("--repo-root")] = None,
) -> None:
    """Run all integrity checks against the compiled index."""
    root = _root(repo_root)
    index = _load(root)
    issues: list[IntegrityIssue] = []
    if not verify_checksum(index):
        issues.append(
            IntegrityIssue(
                severity=Severity.SEV1,
                code="checksum-mismatch",
                message="Stored checksum does not match the index — re-run governova compile.",
                source_path="compiled/constitution.json",
            )
        )
    for check in ALL_CHECKS:
        issues.extend(check(index))
    if not skip_links:
        link_issues, _ = check_links(root)
        issues.extend(link_issues)
    errors = [i for i in issues if i.severity in _ERROR_SEVERITIES]
    warnings = [i for i in issues if i.severity == Severity.SEV3]
    console.print(
        f"standards={len(_all_standards(index))} errors={len(errors)} warnings={len(warnings)}"
    )
    for i in (*errors, *warnings):
        loc = i.source_path or "-"
        if i.source_line:
            loc += f":{i.source_line}"
        console.print(f"  [{i.severity.value}] {i.code} {loc} — {i.message}")
    if errors or (strict and warnings):
        console.print("[bold red]integrity FAILED[/]")
        raise typer.Exit(code=2)
    console.print("[bold green]integrity OK[/]")


@app.command()
def compile(  # noqa: A001 — the CLI verb is intentionally "compile"
    check: Annotated[bool, typer.Option("--check", help="Fail if the committed index is stale.")] = False,
    repo_root: Annotated[Path | None, typer.Option("--repo-root")] = None,
) -> None:
    """Compile the constitutions into the index (or --check for drift)."""
    from governova_compile.writer import compute_checksum

    root = _root(repo_root)
    index = compile_index(root)
    out_dir = root / "compiled"
    if check:
        committed = out_dir / "constitution.json"
        if committed.is_file() and compute_checksum(index) == load_index(committed).checksum:
            console.print("[green]committed index is up to date.[/]")
            return
        console.print("[bold red]committed index is stale — run `governova compile`.[/]")
        raise typer.Exit(code=2)
    write_index(index, out_dir)
    console.print(
        f"[green]compiled {len(_all_standards(index))} standards -> compiled/constitution.json[/]"
    )


@app.command()
def score(
    repo_root: Annotated[Path | None, typer.Option("--repo-root")] = None,
) -> None:
    """Compute the Constitution Health Score (0-100) for this constitutional database.

    This scores the *constitution itself* (completeness + integrity), distinct from a
    project's Governova Score (which weights runtime violations and relay compliance).
    """
    root = _root(repo_root)
    index = _load(root)
    standards = _all_standards(index)
    n = len(standards)
    if n == 0:
        console.print("[red]no standards.[/]")
        raise typer.Exit(code=2)

    with_ap = sum(1 for s in standards if s.anti_patterns)
    with_rationale = sum(1 for s in standards if (s.rationale or "").strip())

    issues: list[IntegrityIssue] = []
    for c in ALL_CHECKS:
        issues.extend(c(index))
    errors = [i for i in issues if i.severity in _ERROR_SEVERITIES]

    ap_cov = with_ap / n
    rat_cov = with_rationale / n
    integrity = 1.0 if not errors else max(0.0, 1.0 - len(errors) / n)

    # Weighted: integrity 40, anti-pattern coverage 35, rationale coverage 25.
    total = round(100 * (0.40 * integrity + 0.35 * ap_cov + 0.25 * rat_cov))

    t = Table.grid(padding=(0, 2))
    t.add_row("Standards:", str(n))
    t.add_row("Integrity (no errors):", f"{integrity * 100:.0f}%")
    t.add_row("Anti-pattern coverage:", f"{ap_cov * 100:.0f}%")
    t.add_row("Rationale coverage:", f"{rat_cov * 100:.0f}%")
    console.print(t)
    colour = "green" if total >= 85 else "yellow" if total >= 70 else "red"
    console.print(f"\n[bold {colour}]Constitution Health Score: {total}/100[/]")


@app.command()
def coverage(
    repo_root: Annotated[Path | None, typer.Option("--repo-root")] = None,
) -> None:
    """Enforcement coverage: how much of the constitution is mechanically enforceable.

    Distinct from the Constitution Health Score (which measures the database's own
    completeness). This measures how many anti-patterns the CI/CD enforcer can detect.
    """
    from governova_checks import enforcement_coverage

    index = _load(_root(repo_root))
    cov = enforcement_coverage(index)
    t = Table.grid(padding=(0, 2))
    t.add_row("Rules:", str(cov["rules"]))
    t.add_row("  blocking (high):", str(cov["blocking_rules"]))
    t.add_row("  advisory (medium):", str(cov["advisory_rules"]))
    t.add_row(
        "Enforceable anti-patterns:",
        f"{cov['enforceable_anti_patterns']} / {cov['total_anti_patterns']}",
    )
    console.print(t)
    pct = cov["coverage_pct"]
    colour = "green" if pct >= 50 else "yellow" if pct >= 15 else "cyan"
    console.print(f"\n[bold {colour}]Enforcement Coverage: {pct}%[/]")
    if cov["covered"]:
        console.print(f"[dim]covered: {', '.join(cov['covered'])}[/]")


@app.command()
def govscore(
    output: Annotated[
        str, typer.Option("--format", help="text | markdown | json | badge")
    ] = "text",
    repo_root: Annotated[Path | None, typer.Option("--repo-root")] = None,
) -> None:
    """Compute the project Governova Score (0-100) — the headline governance metric.

    The weighted model from master.md §18.1, scored over the factors assessable from
    the repo (renormalised), with a transparent per-factor breakdown. In markdown
    mode, also appended to the GitHub job summary when running in CI.
    """
    import os

    from governova_score import compute_score, to_badge, to_json, to_markdown, to_text

    gs = compute_score(_root(repo_root))
    fmt = output.lower()
    if fmt == "json":
        console.print_json(to_json(gs))
        return
    if fmt == "badge":
        console.print(to_badge(gs))
        return
    if fmt == "markdown":
        md = to_markdown(gs)
        console.print(md)
        summary = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary:
            try:
                with open(summary, "a", encoding="utf-8") as fh:
                    fh.write(md + "\n")
            except OSError:
                pass
        return

    colour = "green" if gs.score >= 85 else "yellow" if gs.score >= 70 else "red"
    t = Table.grid(padding=(0, 2))
    for f in gs.factors:
        val = f"{f.score:.0f}/100" if f.assessed else "[dim]not assessed[/]"
        t.add_row(f"{f.title} ({f.weight}%):", f"{val}  [dim]{f.detail}[/]")
    console.print(t)
    console.print(f"\n[bold {colour}]Governova Score: {gs.score}/100  [{gs.grade}][/]")
    if gs.certified_eligible:
        console.print("[bold green]✓ Governova Certified eligible (≥85)[/]")


@app.command()
def report(
    output: Annotated[str, typer.Option("--format", help="markdown | json")] = "markdown",
    out_file: Annotated[
        Path | None, typer.Option("--out", help="Write the report to a file as well.")
    ] = None,
    repo_root: Annotated[Path | None, typer.Option("--repo-root")] = None,
) -> None:
    """Generate the Board-Level Governance Report (master.md §18.3).

    A one-page, plain-English governance report for non-technical stakeholders:
    overall score, certification status, red/amber/green per constitutional area,
    and governance events. In markdown mode, also appended to the GitHub job summary.
    """
    import os

    from governova_report import build_report, to_json, to_markdown

    br = build_report(_root(repo_root))
    rendered = to_json(br) if output.lower() == "json" else to_markdown(br)
    if output.lower() == "json":
        console.print_json(rendered)
    else:
        console.print(rendered)
        summary = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary:
            try:
                with open(summary, "a", encoding="utf-8") as fh:
                    fh.write(rendered + "\n")
            except OSError:
                pass
    if out_file:
        out_file.write_text(rendered + "\n", encoding="utf-8")
        console.print(f"[dim]written to {out_file}[/]")


@app.command()
def bible(
    output: Annotated[str, typer.Option("--format", help="markdown | json")] = "markdown",
    out_file: Annotated[
        Path | None, typer.Option("--out", help="Write the System Bible to a file.")
    ] = None,
    repo_root: Annotated[Path | None, typer.Option("--repo-root")] = None,
) -> None:
    """Generate the System Bible (master.md §18.4) — per-file documentation of the codebase.

    Documents every source file: its purpose, public surface, and dependencies —
    turning the codebase from a black box into something a maintainer can navigate.
    """
    from governova_bible import build_bible, to_json, to_markdown

    sb = build_bible(_root(repo_root))
    rendered = to_json(sb) if output.lower() == "json" else to_markdown(sb)
    if output.lower() == "json":
        console.print_json(rendered)
    elif out_file:
        console.print(
            f"[green]System Bible: {sb.total_files} files, {sb.total_loc} LOC, "
            f"{sb.documented_pct}% documented[/]"
        )
    else:
        console.print(rendered)
    if out_file:
        out_file.write_text(rendered + "\n", encoding="utf-8")
        console.print(f"[dim]written to {out_file}[/]")


if __name__ == "__main__":
    app()
