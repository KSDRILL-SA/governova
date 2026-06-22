"""`governova-enforce` — the CI/CD enforcement surface.

Turns the constitution into a merge gate. Scans a pull request's changed source
files with the reliable-tier detection core and, in block mode, fails the build so
a violation cannot be merged.

Examples:
    governova-enforce src/app.ts                       # scan specific files
    governova-enforce --changed --base origin/main     # scan a PR's changed files
    governova-enforce --changed --mode advisory        # report, never block
    governova-enforce --changed --format github        # GitHub Actions annotations
"""

from __future__ import annotations

import json
import os
import subprocess
from enum import Enum
from pathlib import Path
from typing import Annotated

import typer
from governova_checks import DEFAULT_IGNORES, Finding, is_ignored, scan_paths
from governova_compile.discovery import resolve_repo_root
from rich.console import Console

console = Console()
err_console = Console(stderr=True)

app = typer.Typer(
    add_completion=False,
    help="Governova — constitutional enforcement for CI/CD (the merge gate).",
)

class Mode(str, Enum):
    block = "block"
    advisory = "advisory"


class Fmt(str, Enum):
    github = "github"
    text = "text"
    json = "json"


def _root() -> Path:
    try:
        return resolve_repo_root()
    except FileNotFoundError as exc:
        err_console.print(f"[bold red]error:[/] {exc}")
        raise typer.Exit(code=2) from exc


def _changed_files(base: str, root: Path) -> list[Path]:
    """Files added/copied/modified/renamed vs `base` (three-dot = since merge-base)."""
    try:
        out = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=ACMR", f"{base}...HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        ).stdout
    except (subprocess.SubprocessError, OSError) as exc:
        err_console.print(f"[bold red]error:[/] could not compute changed files vs '{base}': {exc}")
        raise typer.Exit(code=2) from exc
    return [root / line.strip() for line in out.splitlines() if line.strip()]


def _level(finding: Finding, mode: Mode) -> str:
    """error => fails the build; warning => informational. High-confidence rules
    fail only in block mode; medium-confidence rules always warn."""
    if mode is Mode.block and finding.blocking:
        return "error"
    return "warning"


def _emit(findings: list[Finding], fmt: Fmt, mode: Mode, root: Path) -> None:
    if fmt is Fmt.json:
        console.print_json(
            json.dumps(
                [
                    {
                        "file": f.file,
                        "line": f.line,
                        "col": f.col,
                        "anti_pattern": f.anti_pattern,
                        "standard": f.standard,
                        "message": f.message,
                        "match": f.match,
                        "confidence": f.confidence,
                        "blocking": f.blocking and mode is Mode.block,
                    }
                    for f in findings
                ]
            )
        )
        return

    for f in findings:
        loc = f.file or "?"
        level = _level(f, mode)
        if fmt is Fmt.github:
            # GitHub Actions annotation — renders inline on the PR diff.
            msg = f"{f.anti_pattern} ({f.standard}) — {f.message}"
            print(f"::{level} file={loc},line={f.line},col={f.col}::{msg}")
        else:
            colour = "red" if level == "error" else "yellow"
            tag = "block" if level == "error" else "warn"
            console.print(
                f"  [{colour}]{tag}[/] [bold]{f.anti_pattern}[/] [dim]({f.standard})[/] "
                f"{loc}:{f.line}:{f.col} — {f.message}"
            )

    # A human summary also lands in the GitHub job summary, when present.
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        blocking = sum(1 for f in findings if _level(f, mode) == "error")
        lines = [
            f"### Governova enforcement — {blocking} blocking, "
            f"{len(findings) - blocking} advisory",
            "",
        ]
        for f in findings:
            kind = "**BLOCK**" if _level(f, mode) == "error" else "warn"
            lines.append(
                f"- {kind} `{f.file}:{f.line}` **{f.anti_pattern}** ({f.standard}) — {f.message}"
            )
        try:
            Path(summary_path).write_text("\n".join(lines) + "\n", encoding="utf-8")
        except OSError:
            pass


@app.command()
def main(
    paths: Annotated[
        list[Path] | None,
        typer.Argument(help="Files or directories to scan. Omit to scan a PR's changed files."),
    ] = None,
    changed: Annotated[
        bool, typer.Option("--changed", help="Scan files changed vs --base (default when no paths given).")
    ] = False,
    base: Annotated[
        str, typer.Option("--base", help="Git ref to diff against for --changed.")
    ] = "origin/main",
    mode: Annotated[
        Mode, typer.Option("--mode", help="block fails the build on a finding; advisory only reports.")
    ] = Mode.block,
    fmt: Annotated[Fmt, typer.Option("--format", help="Output format.")] = Fmt.text,
    ignore: Annotated[
        list[str] | None, typer.Option("--ignore", help="Extra glob(s) to skip (repeatable).")
    ] = None,
    no_default_ignore: Annotated[
        bool, typer.Option("--no-default-ignore", help="Disable the built-in tests/fixtures ignores.")
    ] = False,
) -> None:
    """Scan changed (or given) source files and gate on constitutional violations."""
    root = _root()
    ignores = (() if no_default_ignore else DEFAULT_IGNORES) + tuple(ignore or ())

    # Resolve the candidate file set.
    if paths:
        candidates: list[Path] = []
        for p in paths:
            if p.is_dir():
                candidates.extend(q for q in p.rglob("*") if q.is_file())
            else:
                candidates.append(p)
    else:
        # No explicit paths -> changed-files mode (the CI default).
        _ = changed  # both no-paths and --changed mean the same thing; kept for clarity
        candidates = _changed_files(base, root)

    # Apply ignores on the repo-relative posix path.
    scannable: list[Path] = []
    for c in candidates:
        try:
            rel = c.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            rel = c.as_posix()
        if not is_ignored(rel, ignores):
            scannable.append(c)

    findings = scan_paths(scannable)
    blocking = [f for f in findings if mode is Mode.block and f.blocking]

    if not findings:
        if fmt is not Fmt.github:
            console.print(
                f"[bold green]✓[/] constitutional enforcement passed "
                f"[dim]({len(scannable)} file(s) scanned)[/]"
            )
        return

    if fmt is not Fmt.github:
        console.print(
            f"[bold]{len(findings)} finding(s)[/] "
            f"[dim]({len(blocking)} blocking, {len(findings) - len(blocking)} advisory)[/]"
        )
    _emit(findings, fmt, mode, root)

    # Block mode fails only on high-confidence (blocking) findings; medium-confidence
    # findings are advisory and never fail the build.
    if blocking:
        if fmt is not Fmt.github:
            console.print(f"[bold red]constitutional enforcement FAILED[/] ({len(blocking)} blocking)")
        raise typer.Exit(code=1)
    if fmt is not Fmt.github:
        console.print("[bold green]✓[/] no blocking violations")


if __name__ == "__main__":
    app()
