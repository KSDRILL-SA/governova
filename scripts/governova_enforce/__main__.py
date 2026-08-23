"""`governova-enforce` — the CI/CD enforcement surface.

Turns the constitution into a merge gate. Scans a pull request's changed source
files with the reliable-tier detection core and, in block mode, fails the build so
a violation cannot be merged.

Core standards bind every system. **Layer 4 domain standards bind the sector that
adopted them**, declared in `governance/project.toml` or with `--domain`; findings
from an undeclared domain are withheld and counted, never applied in silence.

Examples:
    governova-enforce src/app.ts                       # scan specific files
    governova-enforce --changed --base origin/main     # scan a PR's changed files
    governova-enforce --changed --mode advisory        # report, never block
    governova-enforce --changed --format github        # GitHub Actions annotations
    governova-enforce . --domain D-FINTECH             # adopt a sector without a profile
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
    for_declared_domains,
    is_ignored,
    scan_paths,
    walk_files,
)
from governova_checks.gather import is_generated
from governova_compile.discovery import resolve_target_root
from governova_compile.writer import load_active_index
from governova_console import configure_stdout
from governova_console import err_console as _err_console
from governova_project import load_profile
from governova_semantic import Outcome, ReviewResult
from governova_semantic import from_env as semantic_from_env
from governova_semantic import review_result as semantic_review_result
from rich.console import Console

configure_stdout()
console = Console()
err_console = _err_console()

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


def _declared_domains(root: Path, override: list[str] | None) -> list[str]:
    """The Layer 4 domains this project has adopted.

    `--domain` wins over the profile so a pipeline can adopt a sector without
    committing a profile first — the flag is the fast path, `governance/project.toml`
    is the durable one. An absent profile and a profile declaring no domain are the
    same state, and it is the state every new adopter starts in.
    """
    if override:
        return [d.upper() for d in override]
    profile = load_profile(root)
    return list(profile.domains) if profile else []


def _notice(message: str, fmt: Fmt, *, styled: str | None = None) -> None:
    """Say something that is not a finding, in whichever channel the format has.

    `github` gets an annotation so it surfaces in the checks UI rather than only
    in a log nobody opens until something has already gone wrong. `json` gets
    **stderr**, because its stdout is a machine contract: the array and nothing
    else, so `--format json | jq` works.

    Every human line in this module goes through here. They previously did not,
    and were guarded by `fmt is not Fmt.github` instead — a condition that reads
    correctly and is wrong, because it asks which format has its own protocol
    rather than which format is being parsed. The summary and the verdict landed
    on either side of the array, and `json.loads` failed at char 4.

    Routing rather than deleting is deliberate. A human watching a `--format json`
    run still wants the counts; a redirect still wants a clean payload. stderr
    gives both, and dropping the lines would have been the smaller diff and the
    worse product.
    """
    if not message:
        return
    if fmt is Fmt.github:
        # An annotation carries no markup, so the plain wording is what ships.
        print(f"::notice::{message}")
        return
    if fmt is Fmt.json:
        # Plain, like the annotation: this is a machine run being narrated, and
        # rich's fallback renders an unstyled glyph as its escape sequence.
        err_console.print(message, highlight=False)
        return
    console.print(styled or f"[dim]{message}[/]")


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

        result = semantic_review_result(code, index=index)
        # UNPARSEABLE is a 200 with no readable verdict. Reported like an outage
        # because it has the same consequence — nothing was reviewed — and the
        # same invisibility. Either way, stop at the first failure: every
        # remaining file fails identically, and hammering a dead endpoint once
        # per file is neither informative nor polite to whoever operates it.
        if result.outcome in (Outcome.UNPARSEABLE, Outcome.UNAVAILABLE):
            unavailable = result
            break
        if result.ran:
            reviewed += 1
        count += _emit_semantic_findings(result, _relative(p, root), fmt)

    _report_semantic_outcome(fmt, reviewed=reviewed, findings=count, unavailable=unavailable)
    return count


def _relative(path: Path, root: Path) -> str:
    """A repo-relative posix path, or the path as given when it lies outside."""
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _emit_semantic_findings(result: ReviewResult, rel: str, fmt: Fmt) -> int:
    """Print one file's advisory findings. Returns how many there were."""
    for f in result.findings:
        if fmt is Fmt.github:
            print(
                f"::warning file={rel},line={f.line or 1}::"
                f"{f.standard} (semantic) — {f.message}"
            )
        else:
            loc = f"{rel}:{f.line}" if f.line else rel
            console.print(f"  [magenta]semantic[/] [bold]{f.standard}[/] {loc} — {f.message}")
    return len(result.findings)


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


def _candidate_files(paths: list[Path] | None, base: str, root: Path) -> list[Path]:
    """Every file the invocation asks about, before ignores are applied.

    Given paths, directories are walked. Given none, this is a pull request and
    the candidates are the files it changed — the CI default.

    **A directory walk honours `SKIP_DIRS`.** It did not, and the effect was the
    worst first impression this tool can make. `governova enforce .` is the first
    command a new adopter types, and a bare `rglob("*")` reached into `.venv`,
    `node_modules` and `dist`: measured against a freshly installed wheel in an
    empty project, it reported **51 blocking findings, every one of them from
    somebody else's dependency**, including files inside `site-packages`.

    The exclusions already existed and were only consulted on the other branch of
    this function — `iter_source_files`, used when no paths are given, has always
    filtered. So the CI path was correct and the human path was not, which is why
    nothing caught it: CI never passes an argument.

    A file named explicitly is still honoured wherever it lives. Naming a file is
    a decision; naming a directory is not a decision about everything vendored
    inside it.
    """
    if not paths:
        return _changed_files(base, root)

    candidates: list[Path] = []
    for p in paths:
        if p.is_dir():
            candidates.extend(_walk_directory(p))
        else:
            candidates.append(p)
    return candidates


def _walk_directory(directory: Path) -> list[Path]:
    """Files under `directory`, skipping the directories nothing authored.

    Pruned during the walk rather than filtered afterwards, so a large
    `node_modules` is never enumerated in the first place. That pruning now lives
    in `walk_files`, which is where four other copies of it converged — this
    function is the one that had it right, and keeping a private version would
    have made it the fifth.
    """
    return [p for p in walk_files(directory) if not is_generated(p.name)]


def _not_ignored(candidates: list[Path], root: Path, ignores: tuple[str, ...]) -> list[Path]:
    """The candidates that survive the ignore globs, matched repo-relative.

    A path outside the repository has no relative form; it is matched as given
    rather than dropped, because a caller who names a file explicitly means it.
    """
    kept: list[Path] = []
    for c in candidates:
        try:
            rel = c.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            rel = c.as_posix()
        if not is_ignored(rel, ignores):
            kept.append(c)
    return kept


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
    domain: Annotated[
        list[str] | None,
        typer.Option(
            "--domain",
            help=(
                "Layer 4 domain(s) this project is governed by, e.g. D-FINTECH. "
                "Overrides governance/project.toml. Undeclared domains are not enforced."
            ),
        ),
    ] = None,
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

    # Both no-paths and --changed mean the same thing; the flag is kept for clarity.
    _ = changed
    candidates = _candidate_files(paths, base, root)
    scannable = _not_ignored(candidates, root, ignores)

    # Layer 4 law binds a project that has adopted the sector, and no other.
    # Filtered here, before anything is counted, emitted or exited on, so the
    # gate and the assessment model answer to the same body of law.
    applicable = for_declared_domains(scan_paths(scannable), _declared_domains(root, domain))
    findings = applicable.findings
    blocking = [f for f in findings if mode is Mode.block and f.blocking]
    # Never a silent subtraction. A gate that quietly stops checking something is
    # the same defect in the opposite direction.
    _notice(applicable.note, fmt)

    if not findings:
        # The machine contract holds on the clean path too: an empty result set
        # is still a result set, and a consumer that parsed a run with findings
        # then crashed on the run that fixed them would have the defect back.
        #
        # Scoped to `json` rather than emitting unconditionally, because `_emit`
        # also overwrites GITHUB_STEP_SUMMARY — and a clean run has never written
        # there, so widening that would let it clobber another step's summary.
        if fmt is Fmt.json:
            _emit(findings, fmt, mode, root)
        _notice(
            f"constitutional enforcement passed ({len(scannable)} file(s) scanned)",
            fmt,
            styled=(
                f"[bold green]✓[/] constitutional enforcement passed "
                f"[dim]({len(scannable)} file(s) scanned)[/]"
            ),
        )
        if semantic:
            _run_semantic(scannable, fmt, root)
        return

    _notice(
        f"{len(findings)} finding(s) "
        f"({len(blocking)} blocking, {len(findings) - len(blocking)} advisory)",
        fmt,
        styled=(
            f"[bold]{len(findings)} finding(s)[/] "
            f"[dim]({len(blocking)} blocking, {len(findings) - len(blocking)} advisory)[/]"
        ),
    )
    _emit(findings, fmt, mode, root)

    if semantic:
        _run_semantic(scannable, fmt, root)

    # Block mode fails only on high-confidence (blocking) findings; medium-confidence
    # findings are advisory and never fail the build.
    if blocking:
        _notice(
            f"constitutional enforcement FAILED ({len(blocking)} blocking)",
            fmt,
            styled=f"[bold red]constitutional enforcement FAILED[/] ({len(blocking)} blocking)",
        )
        raise typer.Exit(code=1)
    _notice("no blocking violations", fmt, styled="[bold green]✓[/] no blocking violations")


if __name__ == "__main__":
    app()
