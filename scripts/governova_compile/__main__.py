"""`governova-compile` — CLI entrypoint."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from governova_console import console as shared_console
from rich.table import Table

from governova_compile.compiler import compile_index
from governova_compile.discovery import resolve_repo_root
from governova_compile.schema import CompiledIndex
from governova_compile.writer import compute_checksum, write_index

app = typer.Typer(
    add_completion=False,
    help="Compile the Governova constitutional database into a typed JSON index.",
)
console = shared_console()


@app.command()
def main(
    repo_root: Annotated[
        Path | None,
        typer.Option("--repo-root", help="Repo root. Defaults to auto-detection."),
    ] = None,
    out_dir: Annotated[
        Path | None,
        typer.Option("--out", help="Output directory. Defaults to <repo>/compiled."),
    ] = None,
    quiet: Annotated[
        bool, typer.Option("--quiet", "-q", help="Suppress the summary table.")
    ] = False,
    check: Annotated[
        bool,
        typer.Option(
            "--check",
            help="Do not write. Exit non-zero if the committed index is stale (CI drift check).",
        ),
    ] = False,
) -> None:
    """Parse every constitution and write the compiled index."""
    try:
        root = repo_root or resolve_repo_root()
    except FileNotFoundError as exc:
        console.print(f"[bold red]error:[/] {exc}")
        raise typer.Exit(code=1) from exc

    out = out_dir or (root / "compiled")

    try:
        index = compile_index(root)
    except Exception as exc:
        console.print(f"[bold red]compile failed:[/] {exc}")
        raise typer.Exit(code=1) from exc

    if check:
        fresh = compute_checksum(index)
        checksum_file = out / "checksum.txt"
        stored = (
            checksum_file.read_text(encoding="utf-8").strip() if checksum_file.is_file() else ""
        )
        if fresh != stored:
            console.print(
                f"[bold red]✗ stale:[/] committed index does not match a fresh compile.\n"
                f"  stored: {stored or '(none)'}\n  fresh:  {fresh}\n"
                f"  Run [cyan]governova-compile[/] and commit the result."
            )
            raise typer.Exit(code=1)
        console.print("[bold green]✓[/] committed index is up to date.")
        return

    artifacts = write_index(index, out)

    if not quiet:
        _print_summary(index, artifacts, root)

    console.print(
        f"[bold green]✓[/] Compiled "
        f"{index.integrity.standards_extracted} standards across "
        f"{len(index.constitutions)} constitutions → {artifacts['index'].relative_to(root)}"
    )


def _print_summary(index: CompiledIndex, artifacts: dict[str, Path], root: Path) -> None:
    table = Table(title="Governova — Compiled Constitutional Index", show_lines=False)
    table.add_column("Constitution", style="cyan")
    table.add_column("Phase", justify="center")
    table.add_column("Standards", justify="right", style="green")
    table.add_column("Anti-Patterns", justify="right", style="yellow")

    for c in index.constitutions:
        aps = sum(len(s.anti_patterns) for s in c.standards)
        phase = c.phase.value if c.phase else "—"
        table.add_row(f"{c.id} {c.name}", phase, str(len(c.standards)), str(aps))

    console.print(table)

    meta = Table.grid(padding=(0, 2))
    practices = sum(len(i.practices) for i in index.implementations)
    bindings = sum(len(i.bindings) for i in index.implementations)
    meta.add_row("Framework primitives:", str(len(index.framework)))
    meta.add_row("Implementation guides:", str(len(index.implementations)))
    meta.add_row("Practices:", str(practices))
    meta.add_row("Stack bindings:", str(bindings))
    meta.add_row("Runbooks:", str(len(index.runbooks)))
    meta.add_row("ADRs:", str(len(index.adrs)))
    meta.add_row("Domain extensions:", str(len(index.domains)))
    meta.add_row("Schema version:", index.schema_version)
    meta.add_row("Source commit:", index.source_commit_sha or "unknown")
    console.print(meta)


if __name__ == "__main__":
    app()
