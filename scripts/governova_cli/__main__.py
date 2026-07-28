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
from typing import Annotated, Any

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


def _all_standards(index: CompiledIndex) -> list[Any]:
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
    domain_standards = [s for d in index.domains for s in d.standards]
    t.add_row("Domains (Layer 4):", str(len(index.domains)))
    t.add_row("Domain standards:", str(len(domain_standards)))
    t.add_row("Runbooks:", str(len(index.runbooks)))
    t.add_row("ADRs:", str(len(index.adrs)))
    t.add_row("Source commit:", index.source_commit_sha or "—")
    console.print(t)


@app.command()
def domains(
    repo_root: Annotated[Path | None, typer.Option("--repo-root")] = None,
) -> None:
    """List the Layer 4 domain extensions and the standards each adds to the core."""
    index = _load(_root(repo_root))
    if not index.domains:
        console.print("[yellow]No domain extensions compiled.[/yellow]")
        return
    t = Table("Domain", "Name", "Standards", "Regulatory basis", box=None, pad_edge=False)
    for domain in index.domains:
        t.add_row(
            domain.id,
            domain.name,
            str(len(domain.standards)),
            " · ".join(domain.regulatory_basis) or "—",
        )
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
def compile(
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
    t.add_row("  path-scoped:", str(cov["path_scoped_rules"]))
    t.add_row(
        "Core anti-patterns:",
        f"{cov['enforceable_anti_patterns']} / {cov['total_anti_patterns']}",
    )
    t.add_row(
        "Domain anti-patterns:",
        f"{cov['domain_enforceable_anti_patterns']} / {cov['domain_total_anti_patterns']}",
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

    from governova_score import compute_score, to_badge, to_json, to_markdown

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
def notify(
    base: Annotated[str, typer.Option("--base", help="Git ref to diff against.")] = "origin/main",
    repo_root: Annotated[Path | None, typer.Option("--repo-root")] = None,
) -> None:
    """Post the Governova Guardian verdict to a chat webhook (Slack/Teams-compatible).

    Inactive unless GOVERNOVA_WEBHOOK_URL is set; then posts the consolidated verdict.
    """
    from governova_notify import from_env
    from governova_notify import notify as do_notify

    if not from_env().is_configured:
        console.print(
            "[yellow]notifier inactive[/] — set GOVERNOVA_WEBHOOK_URL to enable chat notifications."
        )
        return
    ok = do_notify(base, _root(repo_root))
    console.print("[green]verdict posted[/]" if ok else "[red]failed to post verdict[/]")


@app.command()
def handoff(
    stage: Annotated[str, typer.Argument(help="Build stage: foundation|database|auth|backend|frontend|quality|product")],
    out_file: Annotated[Path | None, typer.Option("--out", help="Write the handoff to a file.")] = None,
    repo_root: Annotated[Path | None, typer.Option("--repo-root")] = None,
) -> None:
    """Generate an engineer handoff brief for a build stage (protocols/build-lifecycle.md).

    Grounded in the compiled index: what to build, why (governing standards), what it
    depends on, and what not to touch. Editable; the engineer's single source of guidance.
    """
    from governova_handoff import build_handoff, to_markdown
    from governova_handoff import stages as _stages

    try:
        h = build_handoff(stage, _root(repo_root))
    except KeyError:
        console.print(f"[bold red]error:[/] unknown stage '{stage}'. Known: {', '.join(_stages())}")
        raise typer.Exit(code=1) from None
    md = to_markdown(h)
    console.print(md)
    if out_file:
        out_file.write_text(md + "\n", encoding="utf-8")
        console.print(f"[dim]written to {out_file}[/]")


@app.command()
def guard(
    base: Annotated[str, typer.Option("--base", help="Git ref to diff against.")] = "origin/main",
    repo_root: Annotated[Path | None, typer.Option("--repo-root")] = None,
) -> None:
    """PR Guardian — a consolidated governance verdict for the changes vs --base.

    Combines the Governova Score, this PR's enforcement result, and coverage into one
    panel (also appended to the GitHub job summary). Advisory: reporting only, never blocks.
    """
    import os

    from governova_guardian import build_verdict, to_markdown

    verdict = build_verdict(base, _root(repo_root))
    md = to_markdown(verdict)
    console.print(md)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        try:
            with open(summary, "a", encoding="utf-8") as fh:
                fh.write(md + "\n")
        except OSError:
            pass


@app.command()
def dashboard(
    out_file: Annotated[
        Path | None, typer.Option("--out", help="Write the dashboard HTML to a file.")
    ] = None,
    repo_root: Annotated[Path | None, typer.Option("--repo-root")] = None,
) -> None:
    """Generate a self-contained governance dashboard (HTML).

    One standalone page — Governova Score, enforcement coverage, and red/amber/green
    per constitutional area. No server, no external assets.
    """
    from governova_dashboard import build_html

    out = out_file or (_root(repo_root) / "dashboard.html")
    out.write_text(build_html(_root(repo_root)), encoding="utf-8")
    console.print(f"[green]dashboard written to {out}[/]")


@app.command(name="semantic-review")
def semantic_review(
    paths: Annotated[list[Path], typer.Argument(help="Source files to review.")],
    repo_root: Annotated[Path | None, typer.Option("--repo-root")] = None,
) -> None:
    """Advisory semantic review (LLM tier) of the given files.

    Inactive unless an endpoint is configured via the environment
    (GOVERNOVA_LLM_MODEL / GOVERNOVA_LLM_BASE_URL / GOVERNOVA_LLM_API_KEY). Findings
    are advisory and never block. Provider-agnostic; the reliable rules are unaffected.
    """
    from governova_semantic import from_env, review

    if not from_env().is_configured:
        console.print(
            "[yellow]semantic tier inactive[/] — set GOVERNOVA_LLM_MODEL / "
            "GOVERNOVA_LLM_BASE_URL / GOVERNOVA_LLM_API_KEY to enable it. "
            "The reliable rules and the gate are unaffected."
        )
        return
    index = _load(_root(repo_root))
    total = 0
    for p in paths:
        if not p.is_file():
            continue
        findings = review(p.read_text(encoding="utf-8", errors="replace"), index=index)
        for f in findings:
            loc = f"{p}:{f.line}" if f.line else str(p)
            console.print(f"  [magenta]semantic[/] [bold]{f.standard}[/] {loc} — {f.message}")
            total += 1
    console.print(
        f"[dim]{total} advisory semantic finding(s)[/]"
        if total
        else "[green]no semantic findings[/]"
    )


@app.command()
def bible(
    output: Annotated[str, typer.Option("--format", help="markdown | json")] = "markdown",
    out_file: Annotated[
        Path | None, typer.Option("--out", help="Write the System Bible to a file.")
    ] = None,
    semantic: Annotated[
        bool,
        typer.Option(
            "--semantic",
            help="Enrich each file with a behavioural summary (requires an LLM endpoint).",
        ),
    ] = False,
    repo_root: Annotated[Path | None, typer.Option("--repo-root")] = None,
) -> None:
    """Generate the System Bible (master.md §18.4) — per-file documentation of the codebase.

    Documents every source file: its purpose, public surface, and dependencies —
    turning the codebase from a black box into something a maintainer can navigate.
    With --semantic and an LLM endpoint configured, each file also gets a summary.
    """
    from governova_bible import build_bible, to_json, to_markdown

    sb = build_bible(_root(repo_root), semantic=semantic)
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


audit_app = typer.Typer(no_args_is_help=True, help="The tamper-evident audit trail.")
relay_app = typer.Typer(no_args_is_help=True, help="The relay state machine.")
app.add_typer(audit_app, name="audit")
app.add_typer(relay_app, name="relay")


@audit_app.command("verify")
def audit_verify(
    repo_root: Annotated[Path | None, typer.Option("--repo-root")] = None,
) -> None:
    """Walk the audit chain and report any tampering. Exits non-zero if broken."""
    from governova_audit import verify

    result = verify(_root(repo_root))
    if result.valid:
        console.print(f"[green]✓ {result.summary}[/]")
        return
    console.print(f"[red]✗ {result.summary}[/]")
    for issue in result.issues:
        console.print(f"  [red]•[/] {issue}")
    raise typer.Exit(code=1)


@audit_app.command("log")
def audit_log(
    limit: Annotated[int, typer.Option("--limit", "-n", help="Most recent N records.")] = 20,
    repo_root: Annotated[Path | None, typer.Option("--repo-root")] = None,
) -> None:
    """Show the most recent audit records."""
    from governova_audit import read_records

    records = read_records(_root(repo_root))
    if not records:
        console.print("[yellow]No audit records.[/]")
        return
    t = Table("Seq", "When", "Actor", "Lvl", "Action", "Outcome", box=None, pad_edge=False)
    for r in records[-limit:]:
        style = "red" if r.outcome == "REFUSED" else ""
        t.add_row(
            str(r.seq),
            r.timestamp,
            f"{r.actor} ({r.actor_kind})",
            r.permission_level,
            r.action,
            f"[{style}]{r.outcome}[/{style}]" if style else r.outcome,
        )
    console.print(t)


@audit_app.command("record")
def audit_record(
    actor: Annotated[str, typer.Option("--actor", help="Who performed the action.")],
    action: Annotated[str, typer.Option("--action", help="What was done.")],
    subject: Annotated[str, typer.Option("--subject", help="What it was done to.")],
    kind: Annotated[str, typer.Option("--kind", help="human | ai | system")] = "human",
    level: Annotated[str, typer.Option("--level", help="L1 | L2 | L3 | L4")] = "L3",
    outcome: Annotated[str, typer.Option("--outcome")] = "recorded",
    detail: Annotated[str, typer.Option("--detail")] = "",
    repo_root: Annotated[Path | None, typer.Option("--repo-root")] = None,
) -> None:
    """Append one record to the audit trail."""
    from governova_audit import append

    rec = append(
        _root(repo_root),
        actor=actor,
        actor_kind=kind,
        permission_level=level,
        action=action,
        subject=subject,
        outcome=outcome,
        detail=detail,
    )
    console.print(f"[green]recorded seq {rec.seq}[/] · hash {rec.record_hash[:16]}…")


@relay_app.command("status")
def relay_status(
    repo_root: Annotated[Path | None, typer.Option("--repo-root")] = None,
) -> None:
    """Show the current relay position and compliance."""
    from governova_relay import compliance, load

    root = _root(repo_root)
    relay = load(root)
    score, detail = compliance(root)
    t = Table.grid(padding=(0, 2))
    t.add_row("State:", relay.state)
    t.add_row("Task:", relay.task or "—")
    t.add_row("Engineer:", relay.engineer or "—")
    t.add_row("Permission:", relay.permission_level or "—")
    t.add_row("Handoffs:", str(relay.handoffs))
    t.add_row("Approvals:", str(relay.approvals))
    t.add_row("Compliance:", f"{score}/100" if score is not None else "not assessed")
    t.add_row("", detail)
    console.print(t)
    for v in relay.violations:
        console.print(f"[red]  • {v}[/]")


def _relay_action(fn: Any, **kwargs: Any) -> None:
    """Run a relay transition, rendering a refusal as the governance event it is."""
    from governova_relay import RelayViolationError

    try:
        fn(**kwargs)
    except RelayViolationError as exc:
        console.print(f"[red]REFUSED [{exc.severity}] ({exc.standard})[/] {exc}")
        raise typer.Exit(code=1) from exc


@relay_app.command("open")
def relay_open(
    task: Annotated[str, typer.Option("--task", help="What the task is.")],
    by: Annotated[str, typer.Option("--by", help="Who opened it (L4, human).")],
    kind: Annotated[str, typer.Option("--kind", help="human | ai | system")] = "human",
    repo_root: Annotated[Path | None, typer.Option("--repo-root")] = None,
) -> None:
    """Open a task. L4 only — human only."""
    from governova_relay import open_task

    _relay_action(open_task, root=_root(repo_root), task=task, opened_by=by, actor_kind=kind)
    console.print(f"[green]task opened:[/] {task}")


@relay_app.command("assign")
def relay_assign(
    engineer: Annotated[str, typer.Option("--engineer")],
    level: Annotated[str, typer.Option("--level", help="L1 | L2 | L3")] = "L3",
    kind: Annotated[str, typer.Option("--kind", help="human | ai | system")] = "ai",
    repo_root: Annotated[Path | None, typer.Option("--repo-root")] = None,
) -> None:
    """Hand the task to an engineer. Refused if another already holds it."""
    from governova_relay import assign

    _relay_action(
        assign,
        root=_root(repo_root),
        engineer=engineer,
        permission_level=level,
        actor_kind=kind,
    )
    console.print(f"[green]assigned to[/] {engineer} at {level}")


@relay_app.command("submit")
def relay_submit(
    engineer: Annotated[str, typer.Option("--engineer")],
    detail: Annotated[str, typer.Option("--detail")] = "",
    repo_root: Annotated[Path | None, typer.Option("--repo-root")] = None,
) -> None:
    """Submit the held work for L4 review."""
    from governova_relay import submit

    _relay_action(submit, root=_root(repo_root), engineer=engineer, detail=detail)
    console.print("[green]submitted — awaiting L4 approval[/]")


@relay_app.command("approve")
def relay_approve(
    by: Annotated[str, typer.Option("--by", help="Who approves (L4, human).")],
    kind: Annotated[str, typer.Option("--kind", help="human | ai | system")] = "human",
    detail: Annotated[str, typer.Option("--detail")] = "",
    repo_root: Annotated[Path | None, typer.Option("--repo-root")] = None,
) -> None:
    """Approve the submitted handoff. Human only, permanently."""
    from governova_relay import approve

    _relay_action(approve, root=_root(repo_root), approver=by, actor_kind=kind, detail=detail)
    console.print("[green]approved[/]")


@relay_app.command("close")
def relay_close(
    by: Annotated[str, typer.Option("--by", help="Who closes it (L4, human).")],
    kind: Annotated[str, typer.Option("--kind", help="human | ai | system")] = "human",
    repo_root: Annotated[Path | None, typer.Option("--repo-root")] = None,
) -> None:
    """Close the task. L4 only — human only."""
    from governova_relay import close_task

    _relay_action(close_task, root=_root(repo_root), closed_by=by, actor_kind=kind)
    console.print("[green]task closed[/]")


@app.command()
def project(
    repo_root: Annotated[Path | None, typer.Option("--repo-root")] = None,
) -> None:
    """Show which standards apply to this project and how many are satisfied."""
    from governova_project import (
        compute_coverage,
        enforced_clean_standards,
        load_profile,
        profile_path,
    )

    root = _root(repo_root)
    profile = load_profile(root)
    if profile is None:
        console.print(
            f"[yellow]No project profile at {profile_path(root).relative_to(root)}.[/]\n"
            f"[dim]Applicability is undeclared, so constitutional coverage is "
            f"unassessed — not assumed compliant.[/]"
        )
        raise typer.Exit(code=1)

    index = _load(root)
    result = compute_coverage(root, index, profile, enforced=enforced_clean_standards(root))
    t = Table.grid(padding=(0, 2))
    t.add_row("Project:", profile.name or "—")
    t.add_row("Stacks:", " · ".join(profile.stacks) or "—")
    t.add_row("Domains:", " · ".join(profile.domains) or "—")
    t.add_row("Phase reached:", str(profile.phase) if profile.phase is not None else "—")
    t.add_row("", "")
    t.add_row("Applicable standards:", str(result.applicable))
    t.add_row("  mechanically verified:", str(result.mechanical))
    t.add_row("  declared with evidence:", str(result.declared))
    t.add_row("  approved exceptions:", str(result.excepted))
    t.add_row("  unaddressed:", str(result.unaddressed))
    t.add_row("Coverage:", f"{result.pct}%")
    console.print(t)

    if result.broken_claims:
        console.print("\n[red]Unresolved claims — not counted as satisfied:[/]")
        for c in result.broken_claims:
            console.print(f"  [red]•[/] {c.standard} ({c.kind}): '{c.evidence}' does not resolve")
        raise typer.Exit(code=1)


@app.command()
def evidence(
    repo_root: Annotated[Path | None, typer.Option("--repo-root")] = None,
) -> None:
    """Run the structural probes — repository facts no line-scan can reach."""
    from governova_evidence import PROBES, Verdict, run_probes

    results = run_probes(_root(repo_root))
    titles = {p.standard: p.title for p in PROBES}
    marks = {Verdict.SATISFIED: "[green]✓[/]", Verdict.VIOLATED: "[red]✗[/]", Verdict.UNKNOWN: "[yellow]?[/]"}

    t = Table("", "Standard", "Check", "Evidence", box=None, pad_edge=False)
    for r in results:
        t.add_row(marks[r.verdict], r.standard, titles.get(r.standard, ""), r.evidence)
    console.print(t)

    satisfied = sum(1 for r in results if r.verdict is Verdict.SATISFIED)
    violated = sum(1 for r in results if r.verdict is Verdict.VIOLATED)
    unknown = len(results) - satisfied - violated
    console.print(
        f"\n[dim]{satisfied} satisfied · {violated} violated · {unknown} undetermined "
        f"(undetermined never counts as satisfied)[/]"
    )
    if violated:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
