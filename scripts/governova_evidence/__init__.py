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

import contextlib
import re
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class Verdict(StrEnum):
    """Implements REQ-002 — a check that cannot determine an answer says so."""

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


# A workflow step's command. Matching only the `run:` line misses the block form,
# which is at least as common:
#
#     - run: ruff check .          - name: Lint
#                                    run: |
#                                      set -euo pipefail
#                                      ruff check .
#
# In the block form the command sits on a continuation line, so a probe anchored
# to `run:` reports a compliant repository as violating — a false negative that
# accuses the innocent, which is the worse direction for a governance tool to err.
# `_workflow_commands` therefore returns command-bearing text with comments and
# human-readable labels removed, and probes search that.
# Lines that are prose rather than commands. A step named "Run pip-audit" must not
# satisfy a probe looking for pip-audit.
_LABEL_LINE = re.compile(r"^\s*(?:-\s*)?(?:name|description|id|if|uses|with|env):", re.I)


def _workflow_text(root: Path) -> str | None:
    """Every CI workflow concatenated, or None when there is no CI to inspect."""
    workflows = sorted((root / ".github" / "workflows").glob("*.y*ml"))
    if not workflows:
        return None
    parts = [t for p in workflows if (t := _read(p)) is not None]
    return "\n".join(parts) if parts else None


def _workflow_commands(root: Path) -> str | None:
    """Workflow text reduced to the lines that can actually execute something.

    Comments and label keys (`name:`, `uses:`, `if:` …) are dropped, so a step
    *named* after a tool cannot satisfy a probe looking for that tool, while a
    command inside a `run: |` block still can.
    """
    text = _workflow_text(root)
    if text is None:
        return None
    return "\n".join(
        line
        for line in text.splitlines()
        if line.strip() and not line.strip().startswith("#") and not _LABEL_LINE.match(line)
    )


def _find_command(root: Path, tools: str) -> re.Match[str] | None:
    """Find an invocation of any tool in the `tools` alternation."""
    commands = _workflow_commands(root)
    if commands is None:
        return None
    return re.search(rf"^.*\b(?:{tools})\b.*$", commands, re.I | re.M)


# ── Probes ───────────────────────────────────────────────────────────────────

_LOCKFILES = ("uv.lock", "poetry.lock", "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "Cargo.lock", "go.sum", "Gemfile.lock", "composer.lock")

# Frozen-install invocations across ecosystems, per S1.98.
_FROZEN_TOOLS = (
    r"uv\s+sync|npm\s+ci|pnpm\s+install[^\n]*--frozen-lockfile|"
    r"yarn\s+install[^\n]*--immutable|poetry\s+install|bundle\s+install[^\n]*--deployment|"
    r"cargo\s+build[^\n]*--locked|go\s+mod\s+download"
)

# Exactly the eleven types S1.19 lists — no more.
#
# The probe once accepted `build`, `revert`, `govern`, and `decision`, none of
# which the standard granted. A probe grading against a rubric wider than the
# standard it cites reports compliance that was never achieved — the same defect
# as an audit check scoring any file as evidence. It was narrowed to the nine
# types the standard then listed, which reported this repository at 90%.
#
# `govern` and `decision` are now lawful: added to S1.19 by C0 §8 amendment on
# 2026-07-30 (C1 v1.4). `harden` was considered in that amendment and **refused**
# — security work is a `fix` when it closes a vulnerability and `chore`/
# `refactor` otherwise — so it stays out of this list, and the `harden:` commit
# in this repository's history remains a violation of record.
#
# The rule this list exists under: change the standard first, then the probe.
# Never the reverse.
_CONVENTIONAL = re.compile(
    r"^(?:feat|fix|chore|docs|refactor|test|style|perf|ci|govern|decision)"
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
    if _workflow_text(root) is None:
        return _unknown(sid, "no CI workflows found")
    m = _find_command(root, r"ruff\s+check|eslint|flake8|golangci-lint|clippy")
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
    m = _find_command(root, _FROZEN_TOOLS)
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
    m = _find_command(root, r"pytest|jest|vitest|go\s+test|cargo\s+test|mvn\s+test|npm\s+test")
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


def _probe_cve_gate(root: Path) -> ProbeResult:
    """S8.84 — a committed lockfile behind a CI vulnerability (SCA) gate."""
    sid = "S8.84"
    locks = [name for name in _LOCKFILES if (root / name).is_file()]
    if not locks:
        return _bad(sid, "no committed lockfile found")
    text = _workflow_text(root)
    if text is None:
        return _unknown(sid, f"{locks[0]} committed, but no CI workflows to inspect")
    m = _find_command(
        root,
        r"pip-audit|safety\s+check|npm\s+audit|pnpm\s+audit|yarn\s+audit|cargo\s+audit|"
        r"govulncheck|osv-scanner|trivy|snyk\s+test|grype",
    )
    if not m:
        return _bad(sid, f"{locks[0]} committed, but no CI vulnerability (SCA) gate found")
    return _ok(sid, f"{locks[0]} committed; CI audits via '{m.group(0).strip()[:60]}'")


def _probe_licence_gate(root: Path) -> ProbeResult:
    """S8.85 — dependency licences checked against an allowlist; SBOM generated."""
    sid = "S8.85"
    text = _workflow_text(root)
    if text is None:
        return _unknown(sid, "no CI workflows found")
    m = _find_command(
        root,
        r"governova\s+licences|licensecheck|pip-licenses|license-checker|reuse\s+lint|cargo\s+deny",
    )
    if not m:
        return _bad(sid, "no CI licence-allowlist check found")
    sbom_present = re.search(r"\bsbom\b|cyclonedx|spdx", text, re.I) is not None
    if not sbom_present:
        return _bad(sid, "licence check present, but no SBOM is generated")
    return _ok(sid, f"CI checks licences and emits an SBOM: '{m.group(0).strip()[:60]}'")


_DEBT_REGISTER_CANDIDATES = (
    "TECHNICAL_DEBT.md",
    "DEBT.md",
    "docs/technical-debt.md",
    "governance/technical-debt.md",
    "docs/debt.md",
)

# Commit types mapped to the canon's four maintenance classes. Derived from the type
# `S1.19` already requires rather than from a second field a human must fill in — a
# second field is a second thing that drifts.
_MAINTENANCE_CLASS: dict[str, str] = {
    "fix": "corrective",
    "ci": "adaptive",
    "chore": "adaptive",
    "build": "adaptive",
    "feat": "perfective",
    "perf": "perfective",
    "style": "perfective",
    "docs": "perfective",
    "refactor": "preventive",
    "test": "preventive",
    "govern": "adaptive",
    "decision": "adaptive",
}


def _probe_debt_register(root: Path) -> ProbeResult:
    """S13.2 — one place where known debt is listed with its cost."""
    sid = "S13.2"
    for candidate in _DEBT_REGISTER_CANDIDATES:
        path = root / candidate
        if path.is_file() and (text := _read(path)) and len(text.strip()) > 40:
            return _ok(sid, f"debt register at {candidate} ({len(text.splitlines())} lines)")
    # A register may legitimately live in the team's tracker rather than the
    # repository, and this engine never calls a tracker. Absent is therefore
    # unknown, not violated — the same rule every probe here follows.
    return _unknown(
        sid,
        "no debt register found in the repository; it may live in the tracker, "
        "which this engine does not read",
    )


def _probe_maintenance_classification(root: Path) -> ProbeResult:
    """S13.4 — every change is classifiable as corrective, adaptive, perfective, or preventive."""
    sid = "S13.4"
    try:
        result = subprocess.run(
            ["git", "log", "-n", "100", "--no-merges", "--format=%s"],
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

    profile: dict[str, int] = {}
    unclassified = 0
    for subject in subjects:
        match = _CONVENTIONAL.match(subject)
        klass = _MAINTENANCE_CLASS.get(match.group(1).lower()) if match else None
        if klass is None:
            unclassified += 1
        else:
            profile[klass] = profile.get(klass, 0) + 1

    mix = " · ".join(f"{k} {v}" for k, v in sorted(profile.items())) or "none"
    if unclassified:
        return _bad(
            sid,
            f"{unclassified}/{len(subjects)} recent commits carry no classifiable type; "
            f"profile so far: {mix}",
        )
    return _ok(sid, f"{len(subjects)} recent commits classified — {mix}")


# ─── C9 Part 9 — Project Governance ──────────────────────────────────────────

_RISK_REGISTER_CANDIDATES = (
    "RISKS.md",
    "RISK_REGISTER.md",
    "docs/risks.md",
    "governance/risks.md",
    "governance/risk-register.md",
)
_ESTIMATE_RECORD_CANDIDATES = (
    "governance/estimates.md",
    "governance/estimates.csv",
    "docs/estimates.md",
    "ESTIMATES.md",
)
# A markdown table row: `| description | owner | mitigation |`. Bounded, as every
# quantifier here is.
_TABLE_ROW = re.compile(r"^\s{0,4}\|(.{1,600})\|\s{0,4}$", re.M)
_HEADER_SEP = re.compile(r"^\s{0,4}\|[\s:|-]{3,200}\|\s{0,4}$")
# Placeholders that look like an owner and name nobody. A team is not a person.
_NOT_A_PERSON = re.compile(
    r"^\s{0,4}(?:-{1,3}|—|n/?a|tbd|tba|unassigned|none|\?+|"
    r"[\w ]{0,30}\b(?:team|squad|guild|group|everyone|all)\b[\w ]{0,20})\s{0,4}$",
    re.I,
)


def _first_existing(root: Path, candidates: tuple[str, ...]) -> tuple[str, str] | None:
    for name in candidates:
        path = root / name
        if path.is_file() and (text := _read(path)):
            return name, text
    return None


def _table_rows(text: str) -> list[list[str]]:
    """Body rows of the first markdown table, header and separator dropped."""
    rows: list[list[str]] = []
    seen_separator = False
    for line in text.splitlines():
        if _HEADER_SEP.match(line):
            seen_separator = True
            rows.clear()  # everything before the separator was the header
            continue
        match = _TABLE_ROW.match(line)
        if match and seen_separator:
            rows.append([cell.strip() for cell in match.group(1).split("|")])
    return rows


def _probe_risk_ownership(root: Path) -> ProbeResult:
    """S9.31 — each recorded risk names one accountable person.

    Ownership by a group is ownership by nobody: every member reasonably assumes
    another is watching. So a cell naming a team is treated as unowned, not as owned.
    """
    sid = "S9.31"
    found = _first_existing(root, _RISK_REGISTER_CANDIDATES)
    if found is None:
        # A register may live in the tracker this engine never calls. Unknown, not
        # violated — the same rule every probe here follows.
        return _unknown(sid, "no risk register found in the repository")
    name, text = found

    rows = _table_rows(text)
    if not rows:
        return _unknown(sid, f"{name} present but holds no readable table of risks")

    header_match = _TABLE_ROW.search(text)
    header = [c.strip().lower() for c in header_match.group(1).split("|")] if header_match else []
    try:
        owner_column = next(i for i, c in enumerate(header) if "owner" in c)
    except StopIteration:
        return _unknown(sid, f"{name} has no owner column, so ownership cannot be read")

    unowned = [
        row
        for row in rows
        if owner_column >= len(row) or not row[owner_column] or _NOT_A_PERSON.match(row[owner_column])
    ]
    if unowned:
        return _bad(sid, f"{len(unowned)}/{len(rows)} risk(s) in {name} name no accountable person")
    return _ok(sid, f"all {len(rows)} risk(s) in {name} name an accountable person")


def _probe_estimate_calibration(root: Path) -> ProbeResult:
    """S9.32 — estimates are recorded against their actuals so drift is measurable.

    Mechanisable exactly when the data is exposed, which is the same shape the
    requirements tiers use: absent data is unknown, never a violation.
    """
    sid = "S9.32"
    found = _first_existing(root, _ESTIMATE_RECORD_CANDIDATES)
    if found is None:
        return _unknown(sid, "no estimate record found in the repository")
    name, text = found

    rows = _table_rows(text)
    header_match = _TABLE_ROW.search(text)
    header = [c.strip().lower() for c in header_match.group(1).split("|")] if header_match else []
    has_estimate = any("estimate" in c for c in header)
    has_actual = any("actual" in c for c in header)
    if not rows or not (has_estimate and has_actual):
        return _unknown(
            sid, f"{name} present but carries no estimate/actual pair, so drift is not computable"
        )

    actual_column = next(i for i, c in enumerate(header) if "actual" in c)
    missing = [
        row
        for row in rows
        if actual_column >= len(row) or not row[actual_column] or _NOT_A_PERSON.match(row[actual_column])
    ]
    if missing:
        return _bad(
            sid,
            f"{len(missing)}/{len(rows)} estimate(s) in {name} have no actual recorded — "
            f"the estimate is never falsified",
        )
    return _ok(sid, f"all {len(rows)} estimate(s) in {name} carry an actual; drift is computable")


# ─── C12 — System Modelling ──────────────────────────────────────────────────

# Text formats whose changes are legible in a diff. An exported image may accompany
# a model; it is never the model (S12.3).
_DIFFABLE_MODEL_SUFFIXES = frozenset({".puml", ".plantuml", ".mmd", ".mermaid", ".d2", ".dot", ".dbml"})
# Opaque formats: a change to one is invisible in review, so the model stops changing.
_OPAQUE_MODEL_SUFFIXES = frozenset({".drawio", ".vsdx", ".xmi", ".eap", ".graffle", ".sketch"})
# Where models conventionally live. Used to keep the scan bounded and to avoid
# reading a stray `.dot` in a build directory as an architectural model.
_MODEL_DIRS = ("docs", "doc", "design", "architecture", "models", "diagrams", "adr")
_CONTEXT_WORDS = re.compile(r"\b(?:context|boundary|system[- ]landscape|c4|container)\b", re.I)
_MERMAID_FENCE = re.compile(r"^```\s*mermaid\b", re.M)
# Published contracts a model may describe (S12.7).
_CONTRACT_NAMES = re.compile(
    r"(?:openapi|swagger)\.(?:ya?ml|json)$|\.(?:proto|graphql|gql)$|schema\.prisma$", re.I
)


def _model_files(root: Path) -> list[Path]:
    """Model artifacts under version control, in a stable order."""
    found: list[Path] = []
    for directory in _MODEL_DIRS:
        base = root / directory
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            suffix = path.suffix.lower()
            # A fenced diagram inside a document counts. Most teams model that way
            # rather than in a modelling tool, and a probe that missed them would
            # report `unknown` for repositories that are in fact modelling.
            is_model = suffix in _DIFFABLE_MODEL_SUFFIXES or suffix in _OPAQUE_MODEL_SUFFIXES
            if is_model or (
                suffix in {".md", ".markdown"}
                and (text := _read(path))
                and _MERMAID_FENCE.search(text)
            ):
                found.append(path)
    return sorted(found, key=lambda p: p.as_posix())


def _probe_models_versioned(root: Path) -> ProbeResult:
    """S12.2 — models live in the repository, versioned with the code."""
    sid = "S12.2"
    models = _model_files(root)
    if not models:
        # A team may model in a tool this engine cannot see. Absent is unknown, never
        # violated — the same rule every probe here follows.
        return _unknown(
            sid,
            "no model artifacts found in the repository; models may be held elsewhere, "
            "which this engine cannot read",
        )
    names = ", ".join(p.relative_to(root).as_posix() for p in models[:3])
    return _ok(sid, f"{len(models)} model artifact(s) under version control: {names}")


def _probe_models_are_diffable(root: Path) -> ProbeResult:
    """S12.3 — a model is expressed in a form whose changes are legible in a diff."""
    sid = "S12.3"
    models = _model_files(root)
    if not models:
        return _unknown(sid, "no model artifacts to inspect")
    opaque = [p for p in models if p.suffix.lower() in _OPAQUE_MODEL_SUFFIXES]
    if opaque:
        names = ", ".join(p.relative_to(root).as_posix() for p in opaque[:3])
        return _bad(sid, f"{len(opaque)} model(s) in an opaque format — changes cannot be reviewed: {names}")
    return _ok(sid, f"all {len(models)} model artifact(s) are diffable text")


def _probe_context_model(root: Path) -> ProbeResult:
    """S12.1 — a system boundary is modelled before its first external interface."""
    sid = "S12.1"
    models = _model_files(root)
    if not models:
        return _unknown(sid, "no model artifacts found; a boundary model may be held elsewhere")
    named = [p for p in models if _CONTEXT_WORDS.search(p.stem)]
    if named:
        return _ok(sid, f"boundary model present: {named[0].relative_to(root).as_posix()}")
    # Models exist but none names a boundary. That is a real signal, not a violation:
    # a boundary may be modelled inside a document whose filename says nothing.
    return _unknown(
        sid,
        f"{len(models)} model(s) present but none is named as a context or boundary model",
    )


def _probe_models_track_contracts(root: Path) -> ProbeResult:
    """S12.7 — models change with the contracts they describe.

    Compares the last commit touching any model against the last commit touching any
    published contract. Model drift is a correctness problem with a delay: nothing
    fails when a model goes stale, so it is discovered only when somebody acts on it.
    """
    sid = "S12.7"
    models = _model_files(root)
    if not models:
        return _unknown(sid, "no model artifacts to compare against")

    contracts = [
        p
        for p in root.rglob("*")
        if p.is_file()
        and _CONTRACT_NAMES.search(p.name)
        and not any(part in {".git", "node_modules", ".venv"} for part in p.parts)
    ]
    if not contracts:
        return _unknown(sid, "no published contract found to compare models against")

    model_time = max((_last_commit_time(root, p) or 0) for p in models)
    contract_time = max((_last_commit_time(root, p) or 0) for p in contracts)
    if not model_time or not contract_time:
        return _unknown(sid, "git history unavailable for models or contracts")
    if model_time < contract_time:
        return _bad(
            sid,
            "a published contract changed more recently than any model describing it — "
            "the models may no longer hold",
        )
    return _ok(sid, "models are no older than the contracts they describe")


def _last_commit_time(root: Path, path: Path) -> int | None:
    try:
        relative = path.relative_to(root).as_posix()
    except ValueError:
        return None
    try:
        result = subprocess.run(
            ["git", "log", "-n", "1", "--format=%ct", "--", relative],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
            timeout=15,
        )
    except (subprocess.SubprocessError, OSError):
        return None
    return int(result.stdout.strip()) if result.stdout.strip().isdigit() else None


PROBES: tuple[Probe, ...] = (
    Probe("S1.19", "Commits follow the conventional format", _probe_conventional_commits),
    Probe("S1.70", "Lint enforced in CI", _probe_lint_in_ci),
    Probe("S1.71", "Pre-commit hooks enforce lint and format", _probe_pre_commit_hooks),
    Probe("S1.84", "README maintained at the repository root", _probe_readme),
    Probe("S1.85", "ADRs document significant decisions", _probe_adrs),
    Probe("S1.98", "Reproducible installs — lockfile + frozen CI", _probe_frozen_install),
    Probe("S7.6", "Tests run on every PR", _probe_tests_in_ci),
    Probe("S8.25", "Environment configuration hygiene", _probe_env_hygiene),
    Probe("S8.84", "Lockfile behind a CI vulnerability gate", _probe_cve_gate),
    Probe("S8.85", "Licence allowlist + SBOM", _probe_licence_gate),
    Probe("S9.31", "Every recorded risk names an accountable person", _probe_risk_ownership),
    Probe("S9.32", "Estimates are recorded against their actuals", _probe_estimate_calibration),
    Probe("S12.1", "A system boundary is modelled", _probe_context_model),
    Probe("S12.2", "Models are versioned with the code", _probe_models_versioned),
    Probe("S12.3", "Models are expressed in a form that diffs", _probe_models_are_diffable),
    Probe("S12.7", "Models change with the contracts they describe", _probe_models_track_contracts),
    Probe("S13.2", "A debt register exists and is reachable", _probe_debt_register),
    Probe("S13.4", "Every change declares its maintenance type", _probe_maintenance_classification),
)


def _requirements_results(root: Path) -> list[ProbeResult]:
    """C11's mechanically checked standards, from the requirements analyser.

    A fourth kind of evidence joins the three this module was built for. The probes
    above answer questions about the repository's *shape*; these answer questions
    about what it was asked to do, which needs an analyser rather than a file scan.
    The dependency runs one way — this module knows about the analyser, never the
    reverse — and the verdict discipline is identical: a repository exposing no
    requirements is UNKNOWN, never SATISFIED and never VIOLATED.
    """
    results: list[ProbeResult] = []
    for module in ("governova_requirements.evidence", "governova_schema.evidence"):
        try:
            probe_verdicts = __import__(module, fromlist=["probe_verdicts"]).probe_verdicts
        except ImportError:  # pragma: no cover - the analysers ship in the same wheel
            continue
        results.extend(
            ProbeResult(standard, Verdict(verdict), evidence)
            for standard, verdict, evidence in probe_verdicts(root)
        )
    return results


def run_probes(root: Path) -> list[ProbeResult]:
    """Run every probe against `root`. A probe that raises is UNKNOWN, never satisfied."""
    results: list[ProbeResult] = []
    for probe in PROBES:
        try:
            results.append(probe.run(root))
        # A broken probe must never claim success — any failure becomes UNKNOWN.
        except Exception as exc:
            results.append(_unknown(probe.standard, f"probe error: {type(exc).__name__}"))
    # The analyser already degrades every failure to UNKNOWN internally; this is the
    # belt to that braces, so an import-time fault cannot take the probe tier with it.
    with contextlib.suppress(Exception):
        results.extend(_requirements_results(root))
    return results


def satisfied_standards(root: Path) -> set[str]:
    """Standard ids the probes verified as satisfied — mechanical evidence."""
    return {r.standard for r in run_probes(root) if r.satisfied}


def probed_standards() -> set[str]:
    """Standards this tier can reach — the file-shape probes plus the analysers."""
    reachable = {p.standard for p in PROBES}
    for module in ("governova_requirements.evidence", "governova_schema.evidence"):
        try:
            reachable |= set(__import__(module, fromlist=["MECHANICAL_STANDARDS"]).MECHANICAL_STANDARDS)
        except ImportError:  # pragma: no cover - the analysers ship in the same wheel
            continue
    return reachable
