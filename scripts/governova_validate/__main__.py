"""`governova-validate` — CLI entrypoint.

Exit codes:
    0  all checks pass (warnings allowed unless --strict)
    2  integrity errors, or warnings under --strict
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from governova_compile.discovery import resolve_repo_root
from governova_compile.schema import CompiledIndex, IntegrityIssue
from governova_compile.writer import load_index
from governova_console import console as shared_console
from rich.table import Table

from governova_validate.run import ERROR_SEVERITIES, run_validation

app = typer.Typer(
    add_completion=False,
    help="Validate the compiled Governova constitutional index.",
)
console = shared_console()


@app.command()
def main(
    repo_root: Annotated[
        Path | None, typer.Option("--repo-root", help="Repo root. Defaults to auto-detection.")
    ] = None,
    index_path: Annotated[
        Path | None, typer.Option("--index", help="Path to constitution.json.")
    ] = None,
    strict: Annotated[bool, typer.Option("--strict", help="Treat warnings as failures.")] = False,
    skip_links: Annotated[
        bool, typer.Option("--skip-links", help="Skip markdown link-integrity checks.")
    ] = False,
) -> None:
    """Run all integrity checks and report the result."""
    try:
        root = repo_root or resolve_repo_root()
    except FileNotFoundError as exc:
        console.print(f"[bold red]error:[/] {exc}")
        raise typer.Exit(code=2) from exc

    index_file = index_path or (root / "compiled" / "constitution.json")
    if not index_file.is_file():
        console.print(
            f"[bold red]error:[/] compiled index not found at {index_file}. "
            f"Run [cyan]governova-compile[/] first."
        )
        raise typer.Exit(code=2)

    index = load_index(index_file)

    run = run_validation(
        root,
        index,
        index_path=str(index_file.relative_to(root)),
        skip_links=skip_links,
    )

    _report(index, run.errors, run.warnings, run.links_checked, strict)

    if run.failed(strict=strict):
        raise typer.Exit(code=2)


def _report(
    index: CompiledIndex,
    errors: list[IntegrityIssue],
    warnings: list[IntegrityIssue],
    links_checked: int,
    strict: bool,
) -> None:
    total_standards = sum(len(c.standards) for c in index.constitutions)

    summary = Table.grid(padding=(0, 2))
    summary.add_row("Standards:", str(total_standards))
    summary.add_row("Constitutions:", str(len(index.constitutions)))
    summary.add_row("Links checked:", str(links_checked))
    summary.add_row("Errors:", f"[red]{len(errors)}[/]" if errors else "[green]0[/]")
    summary.add_row("Warnings:", f"[yellow]{len(warnings)}[/]" if warnings else "[green]0[/]")
    console.print(summary)

    if errors or warnings:
        table = Table(title="Integrity findings", show_lines=False)
        table.add_column("Severity", justify="center")
        table.add_column("Code", style="cyan")
        table.add_column("Location", style="dim")
        table.add_column("Message")
        for issue in (*errors, *warnings):
            colour = "red" if issue.severity in ERROR_SEVERITIES else "yellow"
            loc = issue.source_path or "—"
            if issue.source_line:
                loc += f":{issue.source_line}"
            table.add_row(f"[{colour}]{issue.severity.value}[/]", issue.code, loc, issue.message)
        console.print(table)

    if not errors and not (strict and warnings):
        console.print("[bold green]✓ integrity OK[/]")
    else:
        console.print("[bold red]✗ integrity FAILED[/]")


if __name__ == "__main__":
    app()
