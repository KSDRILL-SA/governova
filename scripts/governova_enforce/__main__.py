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

import contextlib
import json
import os
import subprocess
from enum import StrEnum
from pathlib import Path
from typing import Annotated

import typer
from governova_checks import (
    DEFAULT_IGNORES,
    Finding,
    changed_files,
    is_ignored,
    scan_paths,
)
from governova_compile.discovery import resolve_target_root
from governova_compile.writer import load_active_index
from governova_console import configure_stdout
from governova_semantic import Outcome, ReviewResult
from governova_semantic import from_env as semantic_from_env
from governova_semantic import review_result as semantic_review_result
from rich.console import Console

configure_stdout()
console = Console()
err_console = Console(stderr=True)

app = typer.Typer(
    add_completion=False,
    help="Governova — constitutional enforcement for CI/CD (the merge gate).",
)

class Mode(StrEnum):
    block = "block"
    advisory = "advisory"


class Fmt(StrEnum):
    github = "github"
    text = "text"
    json = "json"


def _root() -> Path:
    """The repository under governance — never the Governova source tree.

    The enforcer runs inside somebody else's CI, so it must resolve the repo it
    is scanning, not the corpus it scans with. Those are separate: the
    constitution arrives via `load_active_index`.
    """
    return resolve_target_root()


def _changed_files(base: str, root: Path) -> list[Path]:
    """Files changed vs `base`; exits cleanly if git cannot compute the diff."""
    try:
        return changed_files(base, root)
    except (subprocess.SubprocessError, OSError) as exc:
        err_console.print(f"[bold red]error:[/] could not compute changed files vs '{base}': {exc}")
        raise typer.Exit(code=2) from exc


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
        with contextlib.suppress(OSError):
            Path(summary_path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def _run_semantic(scannable: list[Path], fmt: Fmt, root: Path) -> int:
    """Advisory semantic pass. A no-op (returns 0) when no endpoint is configured.

    Findings are emitted as warnings and never affect the exit code — the reliable
    tier alone gates the build.
    """
    cfg = semantic_from_env()
    if not cfg.is_configured:
        # Inactive is a valid, stated outcome — not a silence. There is no default
        # endpoint (ADR-008), so this is the expected result until one is configured,
        # and saying so keeps it distinguishable from an endpoint that died.
        message = (
            "semantic tier inactive — no endpoint configured (ADR-008: no default is "
            "bundled). Set GOVERNOVA_LLM_* to enable the advisory pass; a local "
            "OpenAI-compatible server is the zero-cost route."
        )
        if fmt is Fmt.github:
            print(f"::notice::{message}")
        elif fmt is not Fmt.json:
            console.print(f"[dim]{message}[/]")
        return 0
    if fmt is Fmt.json:
        return 0  # json output is the reliable-tier machine contract
    index = load_active_index(start=root)
    count = 0
    reviewed = 0
    unavailable: ReviewResult | None = None

    for p in scannable:
        try:
            code = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        try:
            rel = p.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            rel = p.as_posix()

        result = semantic_review_result(code, index=index)
        if result.outcome is Outcome.UNPARSEABLE:
            # A 200 with no readable verdict. Reported like an outage because it has the
            # same consequence — nothing was reviewed — and the same invisibility.
            unavailable = result
            break
        if result.outcome is Outcome.UNAVAILABLE:
            # Stop at the first failure. Every remaining file would fail the same way,
            # and hammering a dead endpoint once per file is neither informative nor
            # polite to whoever operates it.
            unavailable = result
            break
        if result.ran:
            reviewed += 1

        for f in result.findings:
            if fmt is Fmt.github:
                print(
                    f"::warning file={rel},line={f.line or 1}::"
                    f"{f.standard} (semantic) — {f.message}"
                )
            else:
                loc = f"{rel}:{f.line}" if f.line else rel
                console.print(
                    f"  [magenta]semantic[/] [bold]{f.standard}[/] {loc} — {f.message}"
                )
            count += 1

    _report_semantic_outcome(fmt, reviewed=reviewed, findings=count, unavailable=unavailable)
    return count


def _report_semantic_outcome(
    fmt: Fmt, *, reviewed: int, findings: int, unavailable: ReviewResult | None
) -> None:
    """Say what happened, always — including when nothing did.

    This is the whole fix for the defect that made the tier's inertness invisible.
    Previously the `github` format emitted warnings and nothing else, so a run against
    an unreachable endpoint and a run that found nothing produced byte-identical
    output: an env block followed by silence. A green build was not evidence the tier
    had run, and for two releases it had not.

    The build result is still never affected. An advisory tier that fails a build over
    a typo'd secret is a worse product (REQ-008) — but saying so out loud costs nothing.
    """
    if unavailable is not None:
        message = (
            f"semantic tier DID NOT RUN — {unavailable.detail}. "
            f"Advisory only, so this build is unaffected; the ~93% of standards this "
            f"tier reaches were not checked."
        )
        if fmt is Fmt.github:
            # A notice annotation, so it is visible in the checks UI and not only in
            # a log nobody opens until something has already gone wrong.
            print(f"::notice::{message}")
        else:
            console.print(f"[yellow]{message}[/]")
        return

    summary = (
        f"semantic tier: reviewed {reviewed} file(s), {findings} advisory finding(s)"
        if reviewed
        else "semantic tier: no file matched a standard, so nothing was reviewed"
    )
    if fmt is Fmt.github:
        print(f"::notice::{summary}")
    else:
        console.print(f"[dim]{summary}[/]")


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
    semantic: Annotated[
        bool,
        typer.Option(
            "--semantic",
            help="Also run the advisory semantic tier (requires an LLM endpoint; never blocks).",
        ),
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
        if semantic:
            _run_semantic(scannable, fmt, root)
        return

    if fmt is not Fmt.github:
        console.print(
            f"[bold]{len(findings)} finding(s)[/] "
            f"[dim]({len(blocking)} blocking, {len(findings) - len(blocking)} advisory)[/]"
        )
    _emit(findings, fmt, mode, root)

    if semantic:
        _run_semantic(scannable, fmt, root)

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
