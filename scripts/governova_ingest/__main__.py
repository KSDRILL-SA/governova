"""`governova-ingest` — read a body of practice held outside the repository.

Maintainer tooling for the Phase 2 conversion (ADR-007), alongside
`governova-compile` and `governova-codegen`. It is never part of governing a
consumer's repository, and it never writes into the source tree by default.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from governova_console import console as shared_console
from rich.table import Table

from governova_ingest import Extracted, ExtractionError, extract_corpus

app = typer.Typer(
    add_completion=False,
    help="Extract text from a source corpus for the practice-to-standard conversion.",
)
console = shared_console()


@app.command()
def main(
    source: Annotated[
        Path,
        typer.Argument(help="Directory holding the source documents. Never inside the repository."),
    ],
    out_dir: Annotated[
        Path | None,
        typer.Option("--out", help="Write one .txt per document here. Omitted = summary only."),
    ] = None,
    manifest: Annotated[
        Path | None,
        typer.Option("--manifest", help="Write a JSON digest manifest here."),
    ] = None,
) -> None:
    """Extract every supported document under SOURCE.

    Prints a summary by default and writes nothing. Extracted text is working
    material for an author, not a repository artifact — `--out` is opt-in for
    that reason, and the conventional output location is gitignored.
    """
    try:
        documents = extract_corpus(source)
    except ExtractionError as exc:
        console.print(f"[bold red]error:[/] {exc}")
        raise typer.Exit(code=1) from exc

    if not documents:
        console.print(f"[yellow]No supported documents found in {source}.[/yellow]")
        raise typer.Exit(code=1)

    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        for doc in documents:
            if doc.characters:
                (out_dir / f"{Path(doc.name).stem}.txt").write_text(doc.text, encoding="utf-8")

    if manifest is not None:
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(_manifest_json(documents), encoding="utf-8")

    _print_summary(documents)

    unreadable = [d for d in documents if not d.characters]
    if unreadable:
        console.print(f"[bold red]✗[/] {len(unreadable)} document(s) could not be read.")
        raise typer.Exit(code=1)
    console.print(f"[bold green]✓[/] extracted {len(documents)} document(s).")


def _manifest_json(documents: list[Extracted]) -> str:
    """A digest manifest — deterministic, and it redistributes nothing.

    The digest is over the extracted *text*, not the source bytes, so this file can be
    published and compared while the corpus itself stays outside the repository. It is
    what lets a later reader confirm they are reading what a standard's author read.
    """
    payload = [
        {
            "name": d.name,
            "suffix": d.suffix,
            "characters": d.characters,
            "sha256": d.digest,
        }
        for d in documents
    ]
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _print_summary(documents: list[Extracted]) -> None:
    table = Table(title="Governova — source corpus", show_lines=False)
    table.add_column("Document", style="cyan")
    table.add_column("Characters", justify="right", style="green")
    table.add_column("Digest", style="dim")
    for doc in documents:
        table.add_row(
            doc.name,
            f"{doc.characters:,}" if doc.characters else "[red]unreadable[/]",
            doc.digest[:12] if doc.digest else "—",
        )
    console.print(table)


if __name__ == "__main__":
    app()
