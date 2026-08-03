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
from governova_compile.discovery import resolve_repo_root, resolve_target_root
from governova_compile.schema import CompiledIndex, IntegrityIssue
from governova_compile.writer import (
    load_active_index,
    load_index,
    resolve_index_path,
    write_index,
)
from governova_console import console as shared_console
from governova_validate.checks import ALL_CHECKS
from governova_validate.run import ERROR_SEVERITIES, run_validation
from rich.table import Table
from rich.text import Text

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Governova — constitutional governance for AI-assisted development.",
)


console = shared_console()

# Mirrors `governova_onboard.baseline.DEFAULT_TOP`. Duplicated rather than
# imported because typer evaluates option defaults at decoration time, and
# importing the onboarding package there would pull the whole analysis stack into
# every `governova --help`. A test asserts the two stay equal, so the duplication
# cannot drift silently.
DEFAULT_ONBOARD_TOP = 12


def _root(repo_root: Path | None) -> Path:
    """The repository under governance.

    Prefers the Governova source tree when the command is run inside one — so
    maintainer commands keep working — and otherwise resolves the consumer's
    repository. Falling back rather than failing is what lets every read-only
    surface run against somebody else's code.
    """
    if repo_root is not None:
        return repo_root
    try:
        return resolve_repo_root()
    except FileNotFoundError:
        return resolve_target_root()


def _onboard_index_path(root: Path) -> Path:
    """Which constitution should judge a repository somewhere else on disk.

    Every other command runs *inside* the tree it governs, so walking upward from
    the target always finds an index or falls through to the bundled copy.
    `onboard` is the first command whose whole purpose is to point at a directory
    elsewhere, and it is the one that exposed the gap: run from a Governova
    source checkout — where nothing is installed and so nothing is bundled —
    against a stranger's repository, the upward walk from the *target* finds
    nothing and the command dies before it scans a single file.

    So the target is asked first, because a repository carrying its own amended
    corpus must be judged by that corpus rather than by ours. Only when the
    target has none does this fall back to the invocation's own context, which
    is what `resolve_index_path` already does for every other command.
    """
    try:
        return resolve_index_path(start=root)
    except FileNotFoundError:
        return resolve_index_path()


def _load(root: Path) -> CompiledIndex:
    """The constitution to govern with — working-tree copy first, else bundled."""
    try:
        return load_active_index(start=root)
    except FileNotFoundError as exc:
        console.print(f"[bold red]error:[/] {exc}")
        raise typer.Exit(code=2) from exc


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
    if match.grounded_in:
        console.print("\n[bold]Grounded in[/]")
        for citation in match.grounded_in:
            console.print(f"  [dim]{citation}[/]")


@app.command()
def validate(
    strict: Annotated[bool, typer.Option("--strict", help="Treat warnings as failures.")] = False,
    skip_links: Annotated[bool, typer.Option("--skip-links")] = False,
    repo_root: Annotated[Path | None, typer.Option("--repo-root")] = None,
) -> None:
    """Run all integrity checks against the compiled index."""
    root = _root(repo_root)
    index = _load(root)
    run = run_validation(root, index, skip_links=skip_links)
    errors, warnings = run.errors, run.warnings
    console.print(
        f"standards={len(_all_standards(index))} errors={len(errors)} warnings={len(warnings)}"
    )
    for i in (*errors, *warnings):
        loc = i.source_path or "-"
        if i.source_line:
            loc += f":{i.source_line}"
        console.print(f"  [{i.severity.value}] {i.code} {loc} — {i.message}")
    if run.failed(strict=strict):
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

    # Index-only, deliberately: this scores the constitution itself, so link and
    # source-tree findings are out of scope and must not move the number.
    issues: list[IntegrityIssue] = []
    for c in ALL_CHECKS:
        issues.extend(c(index))
    errors = [i for i in issues if i.severity in ERROR_SEVERITIES]

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
    (GOVERNOVA_LLM_MODEL / GOVERNOVA_LLM_BASE_URL / GOVERNOVA_LLM_API_KEY, and
    optionally GOVERNOVA_LLM_PROTOCOL). Findings are advisory and never block.
    Provider-agnostic; the reliable rules are unaffected.
    """
    from governova_semantic import Outcome, from_env, review_result

    if not from_env().is_configured:
        console.print(
            "[yellow]semantic tier inactive[/] — no endpoint configured (ADR-008: there "
            "is no default, and none is bundled).\n"
            "[dim]Set GOVERNOVA_LLM_BASE_URL / GOVERNOVA_LLM_MODEL / "
            "GOVERNOVA_LLM_API_KEY to any endpoint speaking chat_completions or "
            "messages.\nThe zero-cost route is a local OpenAI-compatible server — no "
            "account, no bill, nothing leaves the machine:\n"
            "  GOVERNOVA_LLM_BASE_URL=http://localhost:11434/v1\n"
            "The deterministic rules, the probes, and the gate are unaffected.[/]"
        )
        return
    index = _load(_root(repo_root))
    total = 0
    reviewed = 0
    for p in paths:
        if not p.is_file():
            continue
        result = review_result(p.read_text(encoding="utf-8", errors="replace"), index=index)
        if result.outcome is Outcome.UNPARSEABLE:
            console.print(
                f"[bold red]semantic tier RETURNED NO VERDICT[/] — {result.detail}.\n"
                f"[dim]The endpoint answered, so this is not an outage. Zero findings "
                f"here means nothing was read.[/]"
            )
            raise typer.Exit(code=1)
        if result.outcome is Outcome.UNAVAILABLE:
            # Never report "no findings" for a review that did not happen. That
            # ambiguity is what let an endpoint retire unnoticed for two releases.
            console.print(
                f"[bold red]semantic tier DID NOT RUN[/] — {result.detail}.\n"
                f"[dim]Advisory only, so nothing is failing; but zero findings here "
                f"means nothing was checked. Verify the endpoint, the token's "
                f"permissions, and the model id, in that order.[/]"
            )
            raise typer.Exit(code=1)
        if result.ran:
            reviewed += 1
        for f in result.findings:
            loc = f"{p}:{f.line}" if f.line else str(p)
            console.print(f"  [magenta]semantic[/] [bold]{f.standard}[/] {loc} — {f.message}")
            total += 1
    if not reviewed:
        console.print("[yellow]no file matched a standard[/] — nothing was submitted for review.")
        return
    console.print(
        f"[dim]{total} advisory semantic finding(s) across {reviewed} reviewed file(s)[/]"
        if total
        else f"[green]reviewed {reviewed} file(s) — no semantic findings[/]"
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


@app.command()
def licences(
    sbom_out: Annotated[
        Path | None, typer.Option("--sbom", help="Also write a CycloneDX SBOM here.")
    ] = None,
    allow: Annotated[
        list[str] | None,
        typer.Option("--allow", help="Package with a recorded L4 exception (repeatable)."),
    ] = None,
) -> None:
    """Check dependency licences against the allowlist (S8.85). Exits non-zero on a gap."""
    from governova_supply import installed_packages, sbom_json

    report = installed_packages(exceptions=set(allow or ()))
    if sbom_out is not None:
        sbom_out.write_text(sbom_json(report), encoding="utf-8")
        console.print(f"[dim]SBOM written to {sbom_out}[/]")

    if report.ok:
        console.print(f"[green]✓ {report.summary}[/]")
        return

    console.print(f"[red]✗ {report.summary}[/]")
    t = Table("Package", "Version", "Licence", box=None, pad_edge=False)
    for p in report.disallowed:
        t.add_row(p.name, p.version, p.licence)
    console.print(t)
    console.print(
        "\n[dim]S8.85: an unknown or copyleft licence requires a recorded L4 exception. "
        "Re-run with --allow <package> once the exception is on record.[/]"
    )
    raise typer.Exit(code=1)


requirements_app = typer.Typer(
    no_args_is_help=True,
    help="Read, trace, and lint the requirements this repository exposes.",
)
app.add_typer(requirements_app, name="requirements")


@requirements_app.command("status")
def requirements_status(
    repo_root: Annotated[Path | None, typer.Option("--repo-root")] = None,
) -> None:
    """Report which requirements tier this repository is at, and why."""
    from governova_requirements import Tier, collect

    root = repo_root or resolve_target_root()
    found = collect(root)
    label = {
        Tier.INVISIBLE: "[yellow]0 — invisible[/]",
        Tier.REFERENCED: "[green]1 — referenced[/]",
        Tier.EXPORTED: "[green]2 — exported[/]",
        Tier.NATIVE: "[green]3 — native[/]",
    }[found.tier]
    t = Table.grid(padding=(0, 2))
    t.add_row("Tier:", label)
    t.add_row("Requirements:", str(len(found.requirements)))
    t.add_row("Citations:", str(len(found.citations)))
    console.print(t)
    for note in found.notes:
        console.print(f"[dim]· {note}[/]")
    if found.tier is Tier.INVISIBLE:
        # Tier 0 is unknown, never a violation. Exiting non-zero here would punish a
        # team for a requirement Governova simply cannot see (ADR-007 addendum).
        console.print(
            "\n[dim]Unassessed, not failing. Cite requirement ids "
            "(REQ-1234) in tests or commit trailers to reach tier 1 at no cost.[/]"
        )


@requirements_app.command("trace")
def requirements_trace(
    repo_root: Annotated[Path | None, typer.Option("--repo-root")] = None,
    strict: Annotated[
        bool, typer.Option("--strict", help="Exit non-zero when findings exist.")
    ] = False,
) -> None:
    """Show requirement ↔ code ↔ test linkage."""
    from governova_requirements import collect, trace

    root = repo_root or resolve_target_root()
    report = trace(collect(root))

    if not report.assessed:
        console.print("[yellow]unknown[/] — no requirements reachable in this repository.")
        for note in report.notes:
            console.print(f"[dim]· {note}[/]")
        return

    coverage = report.coverage_pct
    console.print(
        f"tier={int(report.tier)} requirements={report.requirements} "
        f"tested={report.tested} untested={report.untested} "
        f"coverage={coverage if coverage is not None else '—'}%"
    )
    for finding in report.findings:
        console.print(f"  [yellow]{finding.code}[/] {finding.message}")
    if report.findings and strict:
        raise typer.Exit(code=1)


@requirements_app.command("lint")
def requirements_lint(
    repo_root: Annotated[Path | None, typer.Option("--repo-root")] = None,
    strict: Annotated[
        bool, typer.Option("--strict", help="Exit non-zero when findings exist.")
    ] = False,
) -> None:
    """Lint requirement text against the canonical grammar (tiers 2–3)."""
    from governova_requirements import Tier, collect, lint

    root = repo_root or resolve_target_root()
    found = collect(root)
    if found.tier < Tier.EXPORTED:
        console.print(
            "[yellow]unknown[/] — no requirement text is reachable, so nothing can be linted."
        )
        for note in found.notes:
            console.print(f"[dim]· {note}[/]")
        return

    findings = lint(found.requirements.values())
    console.print(f"requirements={len(found.requirements)} findings={len(findings)}")
    for finding in findings:
        console.print(f"  [yellow]{finding.code}[/] {finding.requirement_id} — {finding.message}")
    if findings and strict:
        raise typer.Exit(code=1)


@app.command(name="semantic-eval")
def semantic_eval(
    repo_root: Annotated[Path | None, typer.Option("--repo-root")] = None,
    runs: Annotated[
        int,
        typer.Option(
            "--runs",
            min=1,
            max=20,
            help="Measure the set this many times. Use 3+ before deciding — one run is a sample.",
        ),
    ] = 1,
    strict: Annotated[
        bool, typer.Option("--strict", help="Exit non-zero when the backend misses the bar.")
    ] = False,
) -> None:
    """Measure whether the configured semantic backend is good enough to be trusted.

    Runs the evaluation fixtures and scores precision and recall. Precision is weighted
    far above recall: a missed violation disappoints, an invented one discredits every
    other finding the tier makes.
    """
    from governova_semantic import MIN_PRECISION, MIN_RECALL, evaluate

    report = evaluate(index=_load(_root(repo_root)), runs=runs)

    if not report.assessed:
        console.print("[yellow]unassessed[/] — the backend could not be measured.")
        for note in report.notes:
            console.print(f"[dim]· {note}[/]")
        return

    console.print(f"model={report.model} measured={report.measured_at} runs={max(runs, 1)}")
    console.print(report.summary())
    if report.spread is not None:
        worst = report.worst_run
        console.print(
            f"[dim]precision across runs: {report.spread} — the verdict uses the worst "
            f"({worst.precision:.0%}/{worst.recall:.0%}), because the same code reviewed "
            f"twice must not give two answers[/]"
            if worst and worst.precision is not None and worst.recall is not None
            else f"[dim]precision across runs: {report.spread}[/]"
        )
    console.print(
        f"[dim]true positives {report.true_positives} · "
        f"false positives {report.false_positives} · "
        f"false negatives {report.false_negatives}[/]"
    )

    table = Table("Fixture", "Expected", "Found", "Verdict", box=None, pad_edge=False)
    for outcome in report.outcomes:
        if outcome.false_positives:
            verdict = f"[red]invented {', '.join(sorted(outcome.false_positives))}[/]"
        elif outcome.false_negatives:
            missed = ", ".join(sorted(outcome.false_negatives))
            # A standard the pre-filter never submitted is not the model's miss.
            verdict = (
                f"[yellow]not grounded: {missed}[/]"
                if outcome.ungrounded
                else f"[yellow]missed {missed}[/]"
            )
        else:
            verdict = "[green]correct[/]"
        table.add_row(
            outcome.fixture_id,
            ", ".join(sorted(outcome.expected)) or "—",
            ", ".join(sorted(outcome.found)) or "—",
            verdict,
        )
    console.print(table)

    for note in report.notes:
        console.print(f"[dim]· {note}[/]")

    if report.passed:
        console.print(f"[bold green]✓ clears the bar[/] (≥{MIN_PRECISION:.0%} precision, ≥{MIN_RECALL:.0%} recall)")
        return
    console.print(
        f"[bold red]✗ below the bar[/] — this backend should not be relied on for "
        f"governance findings (≥{MIN_PRECISION:.0%} precision, ≥{MIN_RECALL:.0%} recall)"
    )
    if strict:
        raise typer.Exit(code=1)


@app.command()
def trace(
    repo_root: Annotated[Path | None, typer.Option("--repo-root")] = None,
    as_json: Annotated[bool, typer.Option("--json", help="Machine-readable output.")] = False,
    strict: Annotated[
        bool, typer.Option("--strict", help="Exit non-zero when a link is broken.")
    ] = False,
) -> None:
    """Requirement ↔ code ↔ test traceability, in both directions."""
    from governova_requirements import close, collect, load_config
    from governova_requirements.closure import to_json
    from governova_requirements.trace import trace as trace_links

    root = repo_root or resolve_target_root()
    config = load_config(root)
    found = collect(root, config)
    links = trace_links(found)
    closure = close(root, found, config)

    if as_json:
        print(to_json(closure), end="")
        return

    if not links.assessed:
        console.print("[yellow]unknown[/] — no requirements reachable in this repository.")
        for note in links.notes:
            console.print(f"[dim]· {note}[/]")
        return

    coverage = links.coverage_pct
    console.print(
        f"tier={int(links.tier)} requirements={links.requirements} "
        f"verified={links.tested} unverified={links.untested} "
        f"coverage={coverage if coverage is not None else '—'}%"
    )
    rate = closure.citation_rate
    if closure.assessed:
        console.print(
            f"[dim]source commits inspected={closure.source_commits} "
            f"citing a requirement={closure.cited_commits}"
            f"{f' ({rate}%)' if rate is not None else ''}[/]"
        )

    # Forward direction: requirement → code → test.
    for finding in links.findings:
        console.print(f"  [yellow]{finding.code}[/] {finding.message}")
    # Reverse direction, and the direction across time.
    for finding in (*closure.orphan_citations, *closure.stale_verifications):
        console.print(f"  [red]{finding.code}[/] {finding.message}")
    for finding in closure.untraced_changes:
        console.print(f"  [dim]{finding.code}[/] {finding.message}")

    for note in (*links.notes, *(closure.notes or [])):
        console.print(f"[dim]· {note}[/]")

    # Only a broken link fails. An untraced change is a prompt for judgement — a
    # refactor, a dependency bump, and a lint fix all legitimately serve no requirement.
    broken = [*closure.orphan_citations, *closure.stale_verifications, *links.findings]
    if broken and strict:
        raise typer.Exit(code=1)


@app.command()
def schema(
    paths: Annotated[
        list[Path] | None,
        typer.Argument(help="Schema files. Omitted = discover them under the repository."),
    ] = None,
    repo_root: Annotated[Path | None, typer.Option("--repo-root")] = None,
    strict: Annotated[
        bool, typer.Option("--strict", help="Exit non-zero when certain findings exist.")
    ] = False,
) -> None:
    """Analyse data-model soundness (C14) — Prisma and SQL DDL."""
    from governova_schema import Confidence, analyse_path, analyse_repository

    root = repo_root or resolve_target_root()
    if paths:
        schemas, findings, unknowns = [], [], []
        for p in paths:
            s, f, u = analyse_path(p, root=root)
            schemas.append(s)
            findings.extend(f)
            unknowns.extend(u)
    else:
        schemas, findings, unknowns = analyse_repository(root)

    if not schemas:
        # No schema is not a sound schema. Same rule as requirements tier 0.
        console.print("[yellow]unknown[/] — no Prisma or SQL schema found in this repository.")
        return

    tables = sum(len(s.tables) for s in schemas)
    certain = [f for f in findings if f.confidence is Confidence.CERTAIN]
    probable = [f for f in findings if f.confidence is Confidence.PROBABLE]
    console.print(
        f"schemas={len(schemas)} tables={tables} "
        f"certain={len(certain)} probable={len(probable)}"
    )
    for finding in (*certain, *probable):
        mark = "[red]certain[/]" if finding.confidence is Confidence.CERTAIN else "[yellow]probable[/]"
        where = f"{finding.source_path}:{finding.table}" if finding.table else finding.source_path
        console.print(f"  {mark} [bold]{finding.code}[/] {where} — {finding.message}")

    for note in (n for s in schemas for n in s.notes):
        console.print(f"[dim]· {note}[/]")

    if unknowns:
        # Printed, not omitted. A silent gap looks like a clean result.
        questions = sorted({u.question for u in unknowns})
        console.print(
            f"\n[dim]unanswered: {', '.join(questions)} — a schema does not declare "
            f"functional dependencies, and guessing them would discredit the rest.[/]"
        )
    if certain and strict:
        raise typer.Exit(code=1)


@app.command()
def onboard(
    path: Annotated[
        Path | None,
        typer.Argument(help="The repository to onboard. Omitted = the one you are standing in."),
    ] = None,
    accept_profile: Annotated[
        bool,
        typer.Option(
            "--accept",
            help="Write the proposed profile to governance/project.toml. Never overwrites.",
        ),
    ] = False,
    show_probes: Annotated[
        bool, typer.Option("--probes", help="Also list every structural probe and its verdict.")
    ] = False,
    top: Annotated[
        int, typer.Option("--top", help="How many finding groups to show.")
    ] = DEFAULT_ONBOARD_TOP,
    as_json: Annotated[
        bool, typer.Option("--json", help="Emit the whole baseline as JSON instead.")
    ] = False,
) -> None:
    """Baseline a repository Governova has never seen. Read-only unless --accept.

    Scan & Learn: what this repository is, what it scores today, where the gaps
    sit, and what to look at first. Nothing is written and nothing is applied.
    """
    from governova_onboard import ProfileExistsError, assess, render_profile
    from governova_onboard import accept as write_profile
    from governova_onboard.render import (
        findings_table,
        heatmap_table,
        probe_table,
        profile_table,
        score_table,
        structural_table,
        to_json,
    )

    root = (path or resolve_target_root()).resolve()
    if not root.is_dir():
        console.print(f"[bold red]error:[/] {root} is not a directory.")
        raise typer.Exit(code=2)

    try:
        index_path = _onboard_index_path(root)
    except FileNotFoundError as exc:
        console.print(f"[bold red]error:[/] {exc}")
        raise typer.Exit(code=2) from exc
    index = load_index(index_path)
    baseline = assess(root, index)

    if as_json:
        console.print_json(to_json(baseline, top=None))
        return

    console.print(f"\n[bold]Onboarding[/] {root}")
    # Which corpus judged this repository is part of the result. Two runs that
    # disagree because they loaded different constitutions would otherwise look
    # like the repository changed.
    console.print(
        f"[dim]judged against {index_path} — "
        f"{len(index.constitutions)} constitution(s)[/]\n"
    )
    console.print("[bold]What this repository is[/]")
    console.print(profile_table(baseline))

    assessed = len(baseline.score.assessed_factors)
    console.print(
        f"\n[bold]Baseline score:[/] {baseline.score.score}/100  [{baseline.score.grade}]"
    )
    # The headline is the only line some readers take away, so what it rests on
    # belongs beside it. On first contact most factors need governance records the
    # repository does not have yet, and a score drawn from one factor out of five
    # is a different claim from one drawn from all of them.
    console.print(
        f"[dim]drawn from {assessed} of 5 factors ({baseline.score.assessed_weight}% of "
        f"factor weight) — the rest need governance instrumentation this repository "
        f"does not have yet[/]"
    )
    console.print(score_table(baseline))

    console.print("\n[bold]Gap heatmap[/] — against the proposed profile")
    console.print(heatmap_table(baseline))
    console.print(
        f"[dim]{baseline.unknown} of {baseline.applicable} applicable standard(s) are "
        f"undetermined. On first contact that is the expected shape: undetermined means "
        f"nobody has looked yet, and it is never counted as satisfied.[/]"
    )

    if baseline.groups:
        shown = min(top, len(baseline.groups))
        console.print(
            f"\n[bold]Top findings[/] — {shown} of {len(baseline.groups)} group(s), "
            f"blocking first"
        )
        console.print(findings_table(baseline, top=top))

    # Probe violations count toward the heatmap's `violated` column, so they are
    # printed whenever there are any. Omitting them left the report showing a
    # violated standard it could not account for.
    if baseline.violated_probes:
        console.print("\n[bold]Structural findings[/] — repository facts, not lines")
        console.print(structural_table(baseline))

    if baseline.clean:
        console.print(
            "\n[green]No deterministic findings.[/] [dim]That is not a clean bill of "
            "health — see the undetermined column above.[/]"
        )

    if show_probes:
        console.print("\n[bold]Structural probes[/]")
        console.print(probe_table(baseline))

    if baseline.provisional:
        console.print("\n[yellow]These numbers are provisional:[/]")
        for reason in baseline.provisional:
            console.print(f"  [yellow]•[/] {reason}")

    proposal = render_profile(
        baseline.detection,
        domains=tuple(d.id for d in index.domains),
        source=root.as_posix(),
    )
    if not accept_profile:
        console.print(
            "\n[bold]Proposed profile[/] [dim](nothing written — review, then re-run "
            "with --accept)[/]"
        )
        # Printed as text, never as markup. Rich reads `[project]` as a style tag
        # and deletes it, which would offer the reviewer TOML that cannot parse.
        console.print(Text(proposal, style="dim"))
        return

    try:
        written = write_profile(root, proposal)
    except ProfileExistsError as exc:
        console.print(f"\n[bold red]error:[/] {exc}")
        raise typer.Exit(code=1) from exc
    except OSError as exc:
        console.print(f"\n[bold red]error:[/] could not write the profile: {exc}")
        raise typer.Exit(code=2) from exc
    console.print(f"\n[green]✓[/] profile written to {written.relative_to(root).as_posix()}")
    console.print(
        "[dim]Review it — the domain and phase lines are commented out because no scan "
        "can settle them, and both change which standards apply.[/]"
    )


@app.command()
def convert(
    path: Annotated[
        Path | None,
        typer.Argument(help="The repository to convert. Omitted = the one you are standing in."),
    ] = None,
    apply_changes: Annotated[
        bool,
        typer.Option("--apply", help="Write the safe conversions. Without this, nothing changes."),
    ] = False,
    converter: Annotated[
        str | None, typer.Option("--converter", help="Run only this converter.")
    ] = None,
) -> None:
    """Propose behaviour-preserving fixes as reviewable diffs. Applies nothing by default.

    Scan, Learn & Rewrite. A conversion against code with no characterisation
    test is refused (S1.101) and there is no flag that overrides it.
    """
    from governova_onboard import assess, propose_conversions
    from governova_onboard.convert import ConversionRefusedError, ConversionStaleError
    from governova_onboard.convert import apply as apply_conversion

    root = (path or resolve_target_root()).resolve()
    if not root.is_dir():
        console.print(f"[bold red]error:[/] {root} is not a directory.")
        raise typer.Exit(code=2)

    try:
        index = load_index(_onboard_index_path(root))
    except FileNotFoundError as exc:
        console.print(f"[bold red]error:[/] {exc}")
        raise typer.Exit(code=2) from exc

    try:
        conversions = propose_conversions(root, assess(root, index), only=converter)
    except KeyError as exc:
        console.print(f"[bold red]error:[/] {exc}")
        raise typer.Exit(code=2) from exc

    if not conversions:
        console.print(
            "\n[green]Nothing to convert.[/] [dim]The converter set is deliberately narrow — "
            "only changes that preserve behaviour and fix the standard rather than the "
            "check. Run `governova roadmap` for what still needs a human.[/]"
        )
        return

    safe = [c for c in conversions if c.applicable]
    refused = [c for c in conversions if not c.applicable]

    console.print(f"\n[bold]Proposed conversions[/] {root}\n")
    for conversion in conversions:
        mark = "[green]ready[/]" if conversion.applicable else "[yellow]refused[/]"
        console.print(f"{mark} [bold]{conversion.path}[/] — {conversion.standard}")
        console.print(f"[dim]{conversion.rationale}[/]")
        # Printed as text: a diff is full of markup-like brackets, and rich would
        # eat them.
        console.print(Text(conversion.diff, style="dim"))
        if conversion.refusal:
            console.print(f"[yellow]refused:[/] {conversion.refusal}\n")

    if not apply_changes:
        console.print(
            f"[dim]{len(safe)} ready · {len(refused)} refused. Nothing was written — "
            f"re-run with --apply.[/]"
        )
        return

    applied = 0
    for conversion in safe:
        try:
            apply_conversion(root, conversion)
        except (ConversionRefusedError, ConversionStaleError) as exc:
            console.print(f"[yellow]skipped[/] {conversion.path}: {exc}")
            continue
        applied += 1
        console.print(f"[green]✓[/] {conversion.path}")

    console.print(
        f"\n[dim]{applied} change(s) written, each to one file and each individually "
        f"revertible (S8.83). {len(refused)} refused and left alone.[/]"
    )


@app.command()
def roadmap(
    path: Annotated[
        Path | None,
        typer.Argument(help="The repository to plan for. Omitted = the one you are standing in."),
    ] = None,
    top: Annotated[
        int | None, typer.Option("--top", help="Show only the first N items.")
    ] = None,
    as_json: Annotated[
        bool, typer.Option("--json", help="Emit the whole plan as JSON instead.")
    ] = False,
) -> None:
    """What to fix first, ordered by impact per unit of work. Read-only.

    A baseline says what is wrong; this says what to do about it, in what order.
    Each item is one PR — individually green, individually revertible (S8.83).
    """
    from governova_onboard import assess, build_roadmap, roadmap_to_json
    from governova_onboard.render import roadmap_table

    root = (path or resolve_target_root()).resolve()
    if not root.is_dir():
        console.print(f"[bold red]error:[/] {root} is not a directory.")
        raise typer.Exit(code=2)

    try:
        index_path = _onboard_index_path(root)
    except FileNotFoundError as exc:
        console.print(f"[bold red]error:[/] {exc}")
        raise typer.Exit(code=2) from exc

    index = load_index(index_path)
    plan = build_roadmap(assess(root, index), index)

    if as_json:
        console.print_json(roadmap_to_json(plan))
        return

    console.print(f"\n[bold]Remediation roadmap[/] {root}\n")
    if not plan:
        # An empty plan is a real result. Manufacturing work to look busy on a
        # clean repository is the first lie a tool can tell about it.
        console.print(
            "[green]No deterministic findings — nothing to plan.[/]\n"
            "[dim]That is not a clean bill of health: run `governova onboard` to see how "
            "much is undetermined rather than clean.[/]"
        )
        return

    console.print(roadmap_table(plan, top=top))
    console.print(
        f"\n[dim]{len(plan)} item(s) · {len(plan.blocking_items)} blocking. "
        f"Ordered blocking-first, then by leverage (blast ÷ effort). The components are "
        f"measured; the weights are a stated convention — dispute the order by reading "
        f"the columns, not by trusting the rank.[/]"
    )

    needing = plan.needing_tests
    if needing:
        console.print(
            f"\n[yellow]{len(needing)} item(s) need a characterisation test first (S1.101):[/]"
        )
        for item in needing[: top or len(needing)]:
            console.print(
                f"  [yellow]•[/] {item.standard} — no conventionally-named test found for "
                f"{', '.join(item.files[:2])}"
            )
        console.print(
            "[dim]'No test found' is not 'no test exists' — a filename search cannot prove "
            "absence. It means nobody has shown the behaviour is pinned, which is exactly "
            "what S1.101 asks for before a brownfield refactor.[/]"
        )


if __name__ == "__main__":
    app()
