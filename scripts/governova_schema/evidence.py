"""C14 as mechanical evidence — the bridge from the analyser to the probe tier.

Nine of C14's fourteen standards are decidable from a schema as written, so they belong
in the evidence model rather than in a declaration. This is what makes them count:
`governova_evidence` runs these alongside its own probes, and constitutional coverage
picks them up with no entry in `governance/project.toml`.

**A repository with no schema is not a repository with a sound schema.** It returns
`unknown` for every standard here — never `satisfied`, never `violated` — the same rule
the requirements tier follows at tier 0 and the same rule that governs every probe.
"""

from __future__ import annotations

from pathlib import Path

from governova_schema.checks import analyse
from governova_schema.model import Confidence, Finding

# Each C14 standard that a mechanical check answers, and the finding code answering it.
#
# The five absent standards are absent on purpose, and each says why in its own text:
# S14.3 (key stability is a claim about the future, which no schema states), S14.7
# (normal form needs functional dependencies, which no schema declares), S14.8 and
# S14.14 (a recorded *rationale* is not a property of a schema file), and S14.13 (a
# design stage leaves no artifact a schema can be checked against).
BOUND: dict[str, str] = {
    "S14.1": "no-primary-key",
    "S14.2": "nullable-primary-key",
    "S14.4": "dangling-foreign-key",
    "S14.5": "foreign-key-to-non-key",
    "S14.6": "repeating-group",
    "S14.9": "unresolved-many-to-many",
    "S14.10": "fan-trap",
    "S14.11": "redundant-relationship",
    "S14.12": "time-variant-without-temporal-key",
}

MECHANICAL_STANDARDS: frozenset[str] = frozenset(BOUND)

ENFORCED_ANTI_PATTERNS: frozenset[str] = frozenset(f"AP-{sid}a" for sid in MECHANICAL_STANDARDS)


def _verdicts(root: Path) -> list[tuple[str, str, str]]:
    """(standard, verdict, evidence) for every mechanically checked C14 standard."""
    from governova_schema import analyse_repository, find_schema_files

    schema_files = find_schema_files(root)
    if not schema_files:
        reason = "no Prisma or SQL schema found — data-model soundness is unassessed"
        return [(sid, "unknown", reason) for sid in sorted(MECHANICAL_STANDARDS)]

    schemas, findings, _ = analyse_repository(root)
    tables = sum(len(s.tables) for s in schemas)
    if not tables:
        reason = f"{len(schema_files)} schema file(s) found but no entity could be read"
        return [(sid, "unknown", reason) for sid in sorted(MECHANICAL_STANDARDS)]

    by_code: dict[str, list[Finding]] = {}
    for finding in findings:
        by_code.setdefault(finding.code, []).append(finding)

    results: list[tuple[str, str, str]] = []
    for sid, code in sorted(BOUND.items()):
        hits = by_code.get(code, [])
        if not hits:
            results.append((sid, "satisfied", f"no {code} finding across {tables} entity/entities"))
            continue
        # A probable finding is a signal, not a verdict. Reporting it as `violated`
        # would let an advisory concern — a deliberate denormalisation, a legitimate
        # fan-trap shape — count against a schema whose designer made the trade on
        # purpose. It is surfaced as unknown, which is uncounted rather than punitive.
        certain = [f for f in hits if f.confidence is Confidence.CERTAIN]
        if certain:
            where = ", ".join(sorted({f.table or "?" for f in certain})[:3])
            results.append((sid, "violated", f"{len(certain)} × {code} ({where})"))
        else:
            results.append(
                (
                    sid,
                    "unknown",
                    f"{len(hits)} × {code} reported as probable — needs the designer's "
                    f"verdict, so this is unassessed rather than failed",
                )
            )
    return results


def probe_verdicts(root: Path) -> list[tuple[str, str, str]]:
    """Public entry point. A failure anywhere degrades to `unknown`, never `satisfied`."""
    try:
        return _verdicts(root)
    except Exception as exc:
        return [
            (sid, "unknown", f"schema probe error: {type(exc).__name__}")
            for sid in sorted(MECHANICAL_STANDARDS)
        ]


__all__ = ["BOUND", "ENFORCED_ANTI_PATTERNS", "MECHANICAL_STANDARDS", "analyse", "probe_verdicts"]
