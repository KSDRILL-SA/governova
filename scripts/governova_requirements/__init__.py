"""governova_requirements — read a team's requirements, lint them, and trace them.

Governova governs *construction*. It could not answer whether you built the **right
thing** — the most expensive class of defect in software, and the one no later
refactor recovers. This package is that answer, under the constraint ADR-007's
addendum sets: **Governova never owns your requirements.** It defines an interchange
format and reads that, the way it reads CycloneDX rather than owning your dependency
graph.

Three things are deliberately structured for extension, each because a second real
case already exists rather than because one might:

- **`sources.register_reader`** — `referenced` and `manifest` ship; a ReqIF importer
  and a tracker exporter are named in ADR-007 and land without touching the core.
- **`lint.register_rule`** — seven rules ship; a house or regulator-specific rule is
  an addition, not an edit.
- **The manifest `schema_version`** — a published contract other people's exporters
  write against, versioned with the same discipline as the compiled index.

Nothing here blocks a build. The tier is new, and a check that fires wrongly on its
first encounter with a real repository does not get a second one.
"""

from __future__ import annotations

from pathlib import Path

from governova_requirements.closure import (
    ClosureReport,
    close,
    orphan_citations,
    stale_verifications,
    untraced_changes,
)
from governova_requirements.lint import (
    MAX_STATEMENT_CHARS,
    LintRule,
    lint,
    lint_requirement,
    register_rule,
    rules,
)
from governova_requirements.model import (
    KINDS,
    OBLIGATIONS,
    Citation,
    Finding,
    Requirement,
    RequirementSet,
    Tier,
)
from governova_requirements.sources import (
    MANIFEST_SCHEMA_VERSION,
    ManifestError,
    ReaderConfig,
    collect,
    find_manifest,
    load_config,
    parse_manifest,
    read_manifest,
    read_referenced,
    register_reader,
    registered_readers,
)
from governova_requirements.trace import TraceReport, trace

__all__ = [
    "KINDS",
    "MANIFEST_SCHEMA_VERSION",
    "MAX_STATEMENT_CHARS",
    "OBLIGATIONS",
    "Citation",
    "ClosureReport",
    "Finding",
    "LintRule",
    "ManifestError",
    "ReaderConfig",
    "Requirement",
    "RequirementSet",
    "Tier",
    "TraceReport",
    "assess",
    "close",
    "collect",
    "find_manifest",
    "lint",
    "lint_requirement",
    "load_config",
    "orphan_citations",
    "parse_manifest",
    "read_manifest",
    "read_referenced",
    "register_reader",
    "register_rule",
    "registered_readers",
    "rules",
    "stale_verifications",
    "trace",
    "untraced_changes",
]


def assess(root: Path, config: ReaderConfig | None = None) -> tuple[RequirementSet, TraceReport, list[Finding]]:
    """Read, trace, and lint a repository's requirements in one pass.

    Returns the set that was read, the traceability report, and the lint findings.
    Lint findings are empty below tier 2 by construction rather than by a check — at
    tier 1 there is no statement to lint, and inventing one would be the opposite of
    what this design promises.
    """
    requirement_set = collect(root, config)
    return requirement_set, trace(requirement_set), lint(requirement_set.requirements.values())
