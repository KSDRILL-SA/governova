"""governova_evidence — deterministic repository-level probes.

The third evidence tier. The reliable tier scans *lines inside source files*; the
semantic tier reasons about code advisorily. Neither can answer questions about
the **repository itself** — is a lockfile committed, does CI install frozen, is
`.env` gitignored, do commits follow the conventional format. Those standards are
fully deterministic and were previously reachable only by a human declaration,
which is the weakest evidence the model accepts.

A probe binds one standard, inspects the repository, and returns concrete
evidence: the file, the line, the matched value. Not a boolean — an auditor
asking "how do you know" must get an answer that points at something.

**The rule that keeps this honest: a probe returns `UNKNOWN`, never `SATISFIED`,
when it cannot determine the answer.** A probe that guesses inflates coverage in
exactly the way the profile model was built to prevent, and a false "satisfied"
is worse than a false "unknown" because it silently retires a standard nobody
will examine again.
"""

from __future__ import annotations

import re
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class Verdict(StrEnum):
    SATISFIED = "satisfied"
    VIOLATED = "violated"
    UNKNOWN = "unknown"  # cannot determine — never counted as satisfied


@dataclass(frozen=True)
class ProbeResult:
    standard: str
    verdict: Verdict
    evidence: str

    @property
    def satisfied(self) -> bool:
        return self.verdict is Verdict.SATISFIED


@dataclass(frozen=True)
class Probe:
    standard: str
    title: str
    run: Callable[[Path], ProbeResult]


def _ok(standard: str, evidence: str) -> ProbeResult:
    return ProbeResult(standard, Verdict.SATISFIED, evidence)


def _bad(standard: str, evidence: str) -> ProbeResult:
    return ProbeResult(standard, Verdict.VIOLATED, evidence)


def _unknown(standard: str, evidence: str) -> ProbeResult:
    return ProbeResult(standard, Verdict.UNKNOWN, evidence)


def _read(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


# A workflow step's command. Both YAML forms are valid and both are common:
#   - name: Lint          |    - run: ruff check .
#     run: ruff check .   |
_RUN_STEP = r"^\s*(?:-\s*)?run:.*"


def _workflow_text(root: Path) -> str | None:
    """Every CI workflow concatenated, or None when there is no CI to inspect."""
    workflows = sorted((root / ".github" / "workflows").glob("*.y*ml"))
    if not workflows:
        return None
    parts = [t for p in workflows if (t := _read(p)) is not None]
    return "\n".join(parts) if parts else None


# ── Probes ───────────────────────────────────────────────────────────────────

_LOCKFILES = ("uv.lock", "poetry.lock", "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "Cargo.lock", "go.sum", "Gemfile.lock", "composer.lock")

# Frozen-install invocations across ecosystems, per S1.98.
_FROZEN_INSTALL = re.compile(
    r"uv\s+sync[^\n]*--frozen|uv\s+sync\b|npm\s+ci\b|pnpm\s+install[^\n]*--frozen-lockfile|"
    r"yarn\s+install[^\n]*--immutable|poetry\s+install\b|bundle\s+install[^\n]*--deployment|"
    r"cargo\s+build[^\n]*--locked|go\s+mod\s+download\b",
    re.I,
)

_CONVENTIONAL = re.compile(
    r"^(?:feat|fix|chore|docs|refactor|test|style|perf|ci|build|revert|govern|decision)"
    r"(?:\([^)]+\))?!?:\s+\S"
)


def _probe_conventional_commits(root: Path) -> ProbeResult:
    """S1.19 — commit subjects follow `{type}({scope}): {description}`."""
    sid = "S1.19"
    try:
        result = subprocess.run(
            ["git", "log", "-n", "50", "--no-merges", "--format=%s"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
            timeout=15,
        )
    except (subprocess.SubprocessError, OSError):
        return _unknown(sid, "git history unavailable")

    subjects = [s for s in result.stdout.splitlines() if s.strip()]
    if not subjects:
        return _unknown(sid, "no commits to inspect")

    bad = [s for s in subjects if not _CONVENTIONAL.match(s)]
    conforming = len(subjects) - len(bad)
    pct = round(100 * conforming / len(subjects))
    if not bad:
        return _ok(sid, f"{conforming}/{len(subjects)} recent commits conventional (100%)")
    return _bad(sid, f"{pct}% conventional; first non-conforming: '{bad[0][:60]}'")


def _probe_lint_in_ci(root: Path) -> ProbeResult:
    """S1.70 — lint is configured and enforced in CI."""
    sid = "S1.70"
    text = _workflow_text(root)
    if text is None:
        return _unknown(sid, "no CI workflows found")
    m = re.search(
        rf"{_RUN_STEP}\b(?:ruff\s+check|eslint|flake8|golangci-lint|clippy)\b.*$", text, re.I | re.M
    )
    if m:
        return _ok(sid, f"CI runs lint: '{m.group(0).strip()[:70]}'")
    return _bad(sid, "no lint step found in any CI workflow")


def _probe_pre_commit_hooks(root: Path) -> ProbeResult:
    """S1.71 — hooks enforce lint/format before a commit is created."""
    sid = "S1.71"
    config = root / ".pre-commit-config.yaml"
    if config.is_file():
        return _ok(sid, ".pre-commit-config.yaml present")
    husky = root / ".husky"
    if husky.is_dir() and any(husky.iterdir()):
        return _ok(sid, ".husky/ hooks present")
    return _bad(sid, "no pre-commit or husky hook configuration found")


def _probe_readme(root: Path) -> ProbeResult:
    """S1.84 — README documents purpose, setup, and env var names."""
    sid = "S1.84"
    text = _read(root / "README.md")
    if text is None:
        return _bad(sid, "no README.md at the repository root")
    low = text.lower()
    required = {
        "purpose/overview": any(k in low for k in ("## what", "purpose", "> *", "overview")),
        "setup": any(k in low for k in ("install", "setup", "getting started", "quickstart")),
    }
    missing = [k for k, present in required.items() if not present]
    if missing:
        return _bad(sid, f"README.md missing: {', '.join(missing)}")
    return _ok(sid, f"README.md documents {', '.join(required)} ({len(text.splitlines())} lines)")


def _probe_adrs(root: Path) -> ProbeResult:
    """S1.85 — significant decisions are recorded as ADRs."""
    sid = "S1.85"
    decisions = root / "governance" / "decisions"
    if not decisions.is_dir():
        return _bad(sid, "no governance/decisions/ directory")
    # The template is scaffolding, not a decision.
    adrs = [p for p in decisions.glob("ADR-*.md") if "template" not in p.name.lower()]
    if not adrs:
        return _bad(sid, "governance/decisions/ contains no ADRs beyond the template")
    return _ok(sid, f"{len(adrs)} ADR(s) recorded, latest {sorted(p.name for p in adrs)[-1]}")


def _probe_frozen_install(root: Path) -> ProbeResult:
    """S1.98 — a committed lockfile AND a frozen CI install."""
    sid = "S1.98"
    locks = [name for name in _LOCKFILES if (root / name).is_file()]
    if not locks:
        return _bad(sid, "no committed lockfile found")
    text = _workflow_text(root)
    if text is None:
        return _unknown(sid, f"lockfile {locks[0]} committed, but no CI workflows to inspect")
    m = _FROZEN_INSTALL.search(text)
    if not m:
        return _bad(sid, f"lockfile {locks[0]} committed, but CI has no frozen install step")
    return _ok(sid, f"{locks[0]} committed; CI installs frozen via '{m.group(0).strip()}'")


def _probe_tests_in_ci(root: Path) -> ProbeResult:
    """S7.6 — the test suite runs on every PR."""
    sid = "S7.6"
    text = _workflow_text(root)
    if text is None:
        return _unknown(sid, "no CI workflows found")
    # The standard is specifically "on every PR", so a repo whose CI never runs on
    # a pull request cannot be judged against it — that is a different question.
    if "pull_request" not in text:
        return _unknown(sid, "CI workflows present but none trigger on pull_request")
    m = re.search(
        rf"{_RUN_STEP}\b(?:pytest|jest|vitest|go\s+test|cargo\s+test|mvn\s+test|npm\s+test)\b.*$",
        text,
        re.I | re.M,
    )
    if m:
        return _ok(sid, f"CI runs tests on PRs: '{m.group(0).strip()[:70]}'")
    return _bad(sid, "no test step found in any CI workflow")


def _probe_env_hygiene(root: Path) -> ProbeResult:
    """S8.25 — `.env.example` committed; `.env` gitignored."""
    sid = "S8.25"
    gitignore = _read(root / ".gitignore")
    if gitignore is None:
        return _bad(sid, "no .gitignore at the repository root")
    ignored = bool(re.search(r"^\s*\.env\b", gitignore, re.M))
    example = (root / ".env.example").is_file()
    if ignored and example:
        return _ok(sid, ".env.example committed and .env gitignored")
    if ignored and not example:
        # No .env.example may simply mean the project needs no env vars. Saying
        # "violated" would be a guess about a project we cannot see into.
        return _unknown(sid, ".env gitignored; no .env.example (project may need no env vars)")
    return _bad(sid, ".env is not gitignored")


PROBES: tuple[Probe, ...] = (
    Probe("S1.19", "Commits follow the conventional format", _probe_conventional_commits),
    Probe("S1.70", "Lint enforced in CI", _probe_lint_in_ci),
    Probe("S1.71", "Pre-commit hooks enforce lint and format", _probe_pre_commit_hooks),
    Probe("S1.84", "README maintained at the repository root", _probe_readme),
    Probe("S1.85", "ADRs document significant decisions", _probe_adrs),
    Probe("S1.98", "Reproducible installs — lockfile + frozen CI", _probe_frozen_install),
    Probe("S7.6", "Tests run on every PR", _probe_tests_in_ci),
    Probe("S8.25", "Environment configuration hygiene", _probe_env_hygiene),
)


def run_probes(root: Path) -> list[ProbeResult]:
    """Run every probe against `root`. A probe that raises is UNKNOWN, never satisfied."""
    results: list[ProbeResult] = []
    for probe in PROBES:
        try:
            results.append(probe.run(root))
        # A broken probe must never claim success — any failure becomes UNKNOWN.
        except Exception as exc:
            results.append(_unknown(probe.standard, f"probe error: {type(exc).__name__}"))
    return results


def satisfied_standards(root: Path) -> set[str]:
    """Standard ids the probes verified as satisfied — mechanical evidence."""
    return {r.standard for r in run_probes(root) if r.satisfied}


def probed_standards() -> set[str]:
    return {p.standard for p in PROBES}
