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
    check: Annotated[
        bool,
        typer.Option(
            "--check",
            help="Fail if the committed generated types are stale. Writes nothing.",
        ),
    ] = False,
) -> None:
    """Emit platform/shared/types-py and platform/shared/types-ts."""
    try:
        root = repo_root or resolve_repo_root()
    except FileNotFoundError as exc:
        console.print(f"[bold red]error:[/] {exc}")
        raise typer.Exit(code=3) from exc

    if check:
        _check_drift(root)
        return

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
    # The TypeScript target has no scaffolding committed, so npm would run in a
    # directory that does not exist and fail with something unrelated to the real
    # cause. Say what is actually wrong instead of failing obscurely.
    if not (ts_root / "package.json").is_file():
        console.print(
            "[yellow]∙[/] TypeScript target is not scaffolded "
            f"([dim]{ts_root.relative_to(root).as_posix()}/package.json[/] absent) — "
            "skipping. Python types were generated."
        )
        return
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


def _check_drift(root: Path) -> None:
    """Compare committed generated types against what the schema would produce now.

    Mirrors `governova compile --check`: generated output is committed so consumers
    can read it without running the generator, which only works if CI proves the
    committed copy still matches its source.
    """
    from governova_codegen.python_types import _BANNER, _strip_leading_docstring, generated_files

    types_py_root = root / "platform" / "shared" / "types-py"
    expected = dict(generated_files(types_py_root))
    schema_source = root / "scripts" / "governova_compile" / "schema.py"
    expected[types_py_root / "governova_types" / "models.py"] = (
        _BANNER + "\n" + _strip_leading_docstring(schema_source.read_text(encoding="utf-8"))
    )

    stale: list[str] = []
    for path, content in sorted(expected.items()):
        rel = path.relative_to(root).as_posix()
        if not path.is_file():
            stale.append(f"{rel} — missing")
        # Compare on normalised line endings: the repo stores LF, a Windows
        # checkout materialises CRLF, and that difference is not drift.
        elif path.read_text(encoding="utf-8").replace("\r\n", "\n") != content.replace(
            "\r\n", "\n"
        ):
            stale.append(f"{rel} — differs from the schema")

    if stale:
        console.print("[bold red]generated types are stale:[/]")
        for item in stale:
            console.print(f"  [red]•[/] {item}")
        console.print("\n[dim]Run [cyan]governova-codegen --skip-ts[/] and commit the result.[/]")
        raise typer.Exit(code=3)
    console.print("[bold green]✓ generated types are up to date[/]")


def _run(cmd: list[str], cwd: Path) -> int:
    try:
        return subprocess.run(cmd, cwd=cwd, check=False).returncode
    except OSError as exc:
        console.print(f"[bold red]error:[/] {' '.join(cmd)} — {exc}")
        return 1


if __name__ == "__main__":
    app()
