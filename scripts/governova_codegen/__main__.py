"""`governova-codegen` — generate TypeScript and Python types from the schema.

Exit codes:
    0  success
    3  codegen error (TS toolchain failure, schema not found)
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Annotated

import typer
from governova_compile.discovery import resolve_repo_root
from governova_compile.schema import export_json_schema
from rich.console import Console

from governova_codegen.python_types import generate_python_types

app = typer.Typer(
    add_completion=False,
    help="Generate TypeScript and Python types from the Governova schema.",
)
console = Console()


@app.command()
def main(
    repo_root: Annotated[
        Path | None, typer.Option("--repo-root", help="Repo root. Defaults to auto-detection.")
    ] = None,
    skip_ts: Annotated[
        bool, typer.Option("--skip-ts", help="Skip TypeScript generation (Python only).")
    ] = False,
) -> None:
    """Emit platform/shared/types-py and platform/shared/types-ts."""
    try:
        root = repo_root or resolve_repo_root()
    except FileNotFoundError as exc:
        console.print(f"[bold red]error:[/] {exc}")
        raise typer.Exit(code=3) from exc

    # Ensure the schema file is fresh on disk for the TS generator to consume.
    schema_path = root / "compiled" / "constitution.schema.json"
    schema_path.parent.mkdir(parents=True, exist_ok=True)
    schema_path.write_text(
        json.dumps(export_json_schema(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    # ── Python types ──────────────────────────────────────────────────────
    schema_source = root / "scripts" / "governova_compile" / "schema.py"
    models_path = generate_python_types(schema_source, root / "platform" / "shared" / "types-py")
    console.print(f"[green]✓[/] Python types → {models_path.relative_to(root)}")

    # ── TypeScript types ──────────────────────────────────────────────────
    if skip_ts:
        console.print("[yellow]∙[/] Skipped TypeScript generation (--skip-ts).")
        return

    ts_root = root / "platform" / "shared" / "types-ts"
    if not (ts_root / "node_modules").is_dir():
        console.print("[cyan]∙[/] Installing TypeScript codegen dependencies…")
        rc = _run(["npm", "install", "--no-audit", "--no-fund"], cwd=ts_root)
        if rc != 0:
            console.print("[bold red]error:[/] npm install failed.")
            raise typer.Exit(code=3)

    rc = _run(["npm", "run", "generate"], cwd=ts_root)
    if rc != 0:
        console.print("[bold red]error:[/] TypeScript generation failed.")
        raise typer.Exit(code=3)

    rc = _run(["npm", "run", "typecheck"], cwd=ts_root)
    if rc != 0:
        console.print("[bold red]error:[/] Generated TypeScript failed tsc --strict.")
        raise typer.Exit(code=3)

    console.print(f"[green]✓[/] TypeScript types → {(ts_root / 'src/index.ts').relative_to(root)}")
    console.print("[bold green]✓ codegen complete[/]")


def _run(cmd: list[str], cwd: Path) -> int:
    try:
        return subprocess.run(cmd, cwd=cwd, check=False).returncode
    except OSError as exc:
        console.print(f"[bold red]error:[/] {' '.join(cmd)} — {exc}")
        return 1


if __name__ == "__main__":
    app()
