"""Traceability closure — the questions that need history, not just the current state.

`trace.py` answers what is reachable *now*: a requirement with no test, a requirement
nothing implements. Those are properties of one snapshot. Three more questions are only
answerable across time and across both directions of the link, and they are the ones the
industry has discussed for forty years without mechanising:

- **A citation that resolves to nothing.** A test asserts `REQ-1234` and the requirement
  set no longer contains it. The test still passes, still looks linked, and verifies a
  commitment nobody holds any more.
- **A verification that went stale.** A requirement's *statement* changed after the test
  citing it was last touched. The test passes against text that no longer says what it
  said, which is worse than an absent test because it reports confidence.
- **A change that traces to nothing.** Source moved and no requirement was cited. Scope
  creep, which is invisible precisely because nothing about it fails.

None of these is decidable without the pieces the earlier stages put in place —
requirement identifiers, a declared set, and citations from tests. That is why this is
Stage 5 and not Stage 1.

**Everything here needs git history and degrades to nothing without it.** A shallow
clone, an export, or a directory that is not a repository are all ordinary, and none of
them is evidence of a governance failure.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

from governova_requirements.model import Finding, RequirementSet, Tier
from governova_requirements.sources import ReaderConfig, find_manifest, parse_manifest

# History is bounded. A repository with ten thousand commits is not ten thousand times
# more interesting than one with two hundred, and an unbounded walk is a denial of
# service against whoever runs this in CI.
_MAX_MANIFEST_REVISIONS = 200
_MAX_SOURCE_COMMITS = 200
# One finding per uncited commit would drown the report on a repository that does not
# cite requirements at all. The count is what matters; the examples are illustration.
_MAX_REPORTED_EXAMPLES = 10

_SOURCE_SUFFIXES = frozenset(
    {".py", ".ts", ".tsx", ".js", ".jsx", ".java", ".go", ".rb", ".cs", ".kt", ".rs", ".php"}
)


@dataclass(frozen=True)
class ClosureReport:
    """The bidirectional view. `assessed` is False when history is unavailable."""

    assessed: bool
    orphan_citations: list[Finding]
    stale_verifications: list[Finding]
    untraced_changes: list[Finding]
    source_commits: int = 0
    cited_commits: int = 0
    notes: list[str] | None = None

    @property
    def findings(self) -> list[Finding]:
        return [*self.orphan_citations, *self.stale_verifications, *self.untraced_changes]

    @property
    def citation_rate(self) -> float | None:
        """Share of source-touching commits that cite a requirement. None if unassessed."""
        if not self.assessed or not self.source_commits:
            return None
        return round(100 * self.cited_commits / self.source_commits, 1)


def _git(root: Path, *args: str) -> str | None:
    """Run git with literal arguments only. Returns None when history is unavailable."""
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
    except (subprocess.SubprocessError, OSError):
        return None
    return result.stdout


# ─── A citation that resolves to nothing ─────────────────────────────────────


def orphan_citations(requirement_set: RequirementSet) -> list[Finding]:
    """Citations naming a requirement the declared set does not contain.

    Only meaningful at tier 2 or above. **At tier 1 the requirement set *is* the set of
    citations**, so every citation resolves by construction and asking the question
    would answer itself — reporting a hollow zero would be worse than staying silent,
    because it would look like the check had run.
    """
    if requirement_set.tier < Tier.EXPORTED:
        return []
    declared = {
        rid for rid, r in requirement_set.requirements.items() if r.origin != "referenced"
    }
    if not declared:
        return []

    seen: set[tuple[str, str]] = set()
    findings: list[Finding] = []
    for citation in requirement_set.citations:
        if citation.requirement_id in declared:
            continue
        key = (citation.requirement_id, citation.location)
        if key in seen:
            continue
        seen.add(key)
        findings.append(
            Finding(
                code="orphan-citation",
                message=(
                    f"{citation.location} cites {citation.requirement_id}, which the "
                    f"declared requirement set does not contain — the link is broken, "
                    f"and whatever it verifies is a commitment nobody holds"
                ),
                requirement_id=citation.requirement_id,
                location=citation.location,
            )
        )
    return sorted(findings, key=lambda f: (f.requirement_id or "", f.location or ""))


# ─── A verification that went stale ──────────────────────────────────────────


def _statement_changed_at(root: Path, manifest_relative: str) -> dict[str, int]:
    """When each requirement's *statement* last changed, as a commit timestamp.

    Walks the manifest's own history and compares statements between revisions, rather
    than using the file's modification time. That distinction is the whole point: a
    manifest edited to add REQ-009 must not mark every other requirement's tests stale.
    """
    log = _git(root, "log", "-n", str(_MAX_MANIFEST_REVISIONS), "--format=%H %ct", "--", manifest_relative)
    if not log:
        return {}

    revisions: list[tuple[str, int]] = []
    for line in log.splitlines():
        sha, _, when = line.partition(" ")
        if sha and when.strip().isdigit():
            revisions.append((sha, int(when.strip())))
    if not revisions:
        return {}

    changed_at: dict[str, int] = {}
    # `git log` is newest-first, which is the order this walk wants: the first revision
    # in which a statement differs from the one before it is the most recent change to
    # that statement. Comparing consecutive pairs is what keeps the answer per
    # requirement rather than per file — adding REQ-009 must not age REQ-001's test.
    newer_statements: dict[str, str] | None = None
    newer_when: int | None = None
    for revision_sha, revision_when in revisions:
        current = _statements(_git(root, "show", f"{revision_sha}:{manifest_relative}"))
        if newer_statements is not None and newer_when is not None:
            for rid, statement in newer_statements.items():
                if rid not in changed_at and current.get(rid) != statement:
                    changed_at[rid] = newer_when
        newer_statements, newer_when = current, revision_when

    # Whatever survived to the oldest revision inspected was introduced no later than
    # that commit, which is the earliest moment this walk can attribute a change to.
    if newer_statements is not None and newer_when is not None:
        for rid in newer_statements:
            changed_at.setdefault(rid, newer_when)
    return changed_at


def _statements(blob: str | None) -> dict[str, str]:
    if not blob:
        return {}
    try:
        return {r.id: r.statement or "" for r in parse_manifest(blob)}
    except Exception:
        # A revision predating the format, or a malformed one. Treated as "unknown
        # shape" rather than "no requirements", so it cannot manufacture a change.
        return {}


def _last_touched(root: Path, relative: str) -> int | None:
    log = _git(root, "log", "-n", "1", "--format=%ct", "--", relative)
    if not log or not log.strip().isdigit():
        return None
    return int(log.strip())


def stale_verifications(root: Path, requirement_set: RequirementSet) -> list[Finding]:
    """Requirements whose statement changed after the test verifying them last did.

    Worse than a missing test, because it reports confidence. The suite is green, the
    citation resolves, and the assertion is against text that no longer says what it
    said when the assertion was written.
    """
    if requirement_set.tier < Tier.EXPORTED:
        return []
    manifest = find_manifest(root, ReaderConfig())
    if manifest is None:
        return []
    try:
        relative = manifest.relative_to(root).as_posix()
    except ValueError:
        return []

    changed_at = _statement_changed_at(root, relative)
    if not changed_at:
        return []

    findings: list[Finding] = []
    for rid, statement_time in sorted(changed_at.items()):
        tests = requirement_set.cited_by(rid, "test")
        if not tests:
            continue  # `requirement-without-test` owns that; one defect, one finding
        for citation in tests:
            touched = _last_touched(root, citation.location)
            if touched is None or touched >= statement_time:
                continue
            findings.append(
                Finding(
                    code="stale-verification",
                    message=(
                        f"{rid} changed after {citation.location} last did — the test "
                        f"passes against a statement that has since been rewritten"
                    ),
                    requirement_id=rid,
                    location=citation.location,
                )
            )
    return findings


# ─── A change that traces to nothing ─────────────────────────────────────────


def untraced_changes(root: Path, config: ReaderConfig | None = None) -> tuple[list[Finding], int, int]:
    """Commits that moved source and cited no requirement. Returns (findings, total, cited).

    Scope creep is invisible because nothing about it fails: the code is written, the
    tests pass, and no artifact records that it served no stated purpose. This is the
    only mechanical view of it, and it is deliberately **advisory** — a refactor, a
    dependency bump, and a lint fix all legitimately serve no requirement, so the count
    is a prompt for judgement rather than a verdict.
    """
    cfg = config or ReaderConfig()
    log = _git(
        root,
        "log",
        "-n",
        str(_MAX_SOURCE_COMMITS),
        "--no-merges",
        "--name-only",
        "--format=%x1e%H%x1f%B%x1f",
    )
    if not log:
        return [], 0, 0

    pattern = cfg.id_pattern
    findings: list[Finding] = []
    total = 0
    cited = 0

    for record in log.split("\x1e"):
        if record.count("\x1f") < 2:
            continue
        sha, _, rest = record.partition("\x1f")
        body, _, files = rest.partition("\x1f")
        sha = sha.strip()
        touched_source = any(
            Path(line.strip()).suffix.lower() in _SOURCE_SUFFIXES
            for line in files.splitlines()
            if line.strip()
        )
        if not sha or not touched_source:
            continue
        total += 1
        if pattern.search(body):
            cited += 1
            continue
        if len(findings) < _MAX_REPORTED_EXAMPLES:
            subject = body.strip().splitlines()[0][:70] if body.strip() else "(no subject)"
            findings.append(
                Finding(
                    code="untraced-change",
                    message=(
                        f"commit {sha[:12]} moved source and cites no requirement — "
                        f"{subject!r}"
                    ),
                    location=f"commit:{sha[:12]}",
                )
            )
    return findings, total, cited


# ─── The closure report ──────────────────────────────────────────────────────


def close(root: Path, requirement_set: RequirementSet, config: ReaderConfig | None = None) -> ClosureReport:
    """Run every closure check. Unavailable history yields an unassessed report."""
    notes: list[str] = []
    if _git(root, "rev-parse", "--git-dir") is None:
        return ClosureReport(
            assessed=False,
            orphan_citations=[],
            stale_verifications=[],
            untraced_changes=[],
            notes=["no git history available — closure is unknown, not violated"],
        )

    untraced, total, cited = untraced_changes(root, config)
    if requirement_set.tier < Tier.EXPORTED:
        notes.append(
            "tier 1 — every citation resolves by construction, so orphan citations and "
            "stale verification are unassessable without a declared requirement set"
        )
    return ClosureReport(
        assessed=True,
        orphan_citations=orphan_citations(requirement_set),
        stale_verifications=stale_verifications(root, requirement_set),
        untraced_changes=untraced,
        source_commits=total,
        cited_commits=cited,
        notes=notes,
    )


def to_json(report: ClosureReport) -> str:
    """Deterministic machine contract for the closure report."""
    payload = {
        "assessed": report.assessed,
        "source_commits": report.source_commits,
        "cited_commits": report.cited_commits,
        "citation_rate": report.citation_rate,
        "findings": [
            {
                "code": f.code,
                "requirement_id": f.requirement_id,
                "location": f.location,
                "message": f.message,
            }
            for f in report.findings
        ],
        "notes": report.notes or [],
    }
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
