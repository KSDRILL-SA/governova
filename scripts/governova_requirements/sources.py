"""Where requirements come from — a registry of readers, not a fixed list.

**This is the extension point of the requirements tier**, and it is a registry rather
than a hard-coded chain because there are already three concrete readers in view and a
fourth named in ADR-007: `referenced` and `manifest` ship here, a team's own tracker
exporter writes a manifest, and ReqIF import is explicitly deferred rather than refused.
An extension point with real cases behind it is design; one with none is
`AP-S1.107a`, and the difference is whether the second case exists yet.

A reader answers one question — *what can be determined about this repository's
requirements from the thing I know how to read* — and returns a `RequirementSet` whose
tier says how much that was. A reader that finds nothing returns `Tier.INVISIBLE`, which
is `unknown` and never a violation.
"""

from __future__ import annotations

import json
import re
import subprocess
import tomllib
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path

from governova_requirements.model import (
    KINDS,
    OBLIGATIONS,
    Citation,
    Requirement,
    RequirementSet,
    Tier,
)

MANIFEST_SCHEMA_VERSION = "1.0"
"""The interchange contract's version.

Versioned like the compiled index and with the same discipline: this is a published
contract that other people's exporters write against, so it changes by decision rather
than by accident.
"""

CONFIG_RELATIVE_PATH = "governance/project.toml"

DEFAULT_ID_PREFIXES: tuple[str, ...] = ("REQ",)
"""Deliberately narrow.

A general `[A-Z]+-\\d+` pattern matches `UTF-8`, `SHA-256`, `ISO-8601`, and `HTTP-2`,
which would manufacture requirements out of ordinary prose and put a governance tool's
credibility behind them. Teams whose tracker uses another prefix declare it; the cost of
that one line is far lower than the cost of a tool that invents findings.
"""

DEFAULT_COMMIT_LIMIT = 200

# Bounded, as every quantifier in this repository is. An ID longer than nine digits is
# not an ID, and the bound is what keeps a pathological line from costing seconds.
_PREFIX_TOKEN = re.compile(r"^[A-Z][A-Z0-9_]{0,15}$")

# A git trailer: `Key: value` at the start of a line. Deliberate and machine-readable,
# which is what separates a declaration from a mention in prose.
_TRAILER = re.compile(r"^[A-Za-z][A-Za-z0-9-]{0,30}:[ \t]{0,4}(.{0,400})$")

_TEST_PATH = re.compile(r"(^|/)(tests?|spec|__tests__|e2e)(/|$)|(^|/)[^/]*(test|spec)[^/]*\.[a-z]{1,5}$")
_SOURCE_SUFFIXES = frozenset(
    {".py", ".ts", ".tsx", ".js", ".jsx", ".java", ".go", ".rb", ".cs", ".kt", ".rs", ".php"}
)
_SKIP_DIRS = frozenset(
    {".git", ".venv", "venv", "node_modules", "__pycache__", "dist", "build", ".mypy_cache",
     ".pytest_cache", ".ruff_cache", "site-packages", ".tox"}
)
# A file large enough to be generated rather than written. Scanning it costs time and
# yields citations nobody authored.
_MAX_FILE_BYTES = 1_000_000


class ManifestError(ValueError):
    """A manifest exists but cannot be read as the contract it claims to implement."""


@dataclass(frozen=True)
class ReaderConfig:
    """How to read this repository's requirements. Declared, never guessed."""

    id_prefixes: tuple[str, ...] = DEFAULT_ID_PREFIXES
    manifest_path: str | None = None
    commit_limit: int = DEFAULT_COMMIT_LIMIT
    exclude: tuple[str, ...] = ()
    """Repo-relative path fragments whose citations are fixtures, not requirements.

    A requirement identifier appearing in a file is normally a citation. It is not
    when the file's subject *is* requirement identifiers — a test for requirements
    tooling, a documentation example, a fixture directory. Tier 1 cannot tell those
    apart by inspection, because `REQ-1234` looks identical either way, so the team
    that knows says so here. This repository is the first case: its own linter tests
    are full of example ids that are not requirements of Governova.

    Suppressing a *finding* would be padding. Excluding a file that was never
    evidence is the opposite — it stops the tool asserting something untrue.
    """

    @property
    def id_pattern(self) -> re.Pattern[str]:
        """`\\b(REQ-1234)\\b` for the declared prefixes, with a bounded numeric part."""
        alternatives = "|".join(re.escape(p) for p in self.id_prefixes)
        return re.compile(rf"\b((?:{alternatives})-\d{{1,9}})\b")


def load_config(root: Path) -> ReaderConfig:
    """Read `[requirements]` from the project profile. Absent config is not an error.

    A repository that has declared nothing is exactly the tier-1 case this design
    exists to serve, so the defaults have to be usable on their own.
    """
    path = root / CONFIG_RELATIVE_PATH
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, OSError):
        return ReaderConfig()

    section = data.get("requirements")
    if not isinstance(section, dict):
        return ReaderConfig()

    prefixes = _clean_prefixes(section.get("id_prefixes"))
    manifest = section.get("manifest")
    limit = section.get("commit_limit")
    raw_exclude = section.get("exclude")
    exclude = (
        tuple(e.strip().replace("\\", "/") for e in raw_exclude if isinstance(e, str) and e.strip())
        if isinstance(raw_exclude, list)
        else ()
    )
    return ReaderConfig(
        id_prefixes=prefixes or DEFAULT_ID_PREFIXES,
        manifest_path=manifest if isinstance(manifest, str) and manifest.strip() else None,
        commit_limit=limit if isinstance(limit, int) and 0 < limit <= 5000 else DEFAULT_COMMIT_LIMIT,
        exclude=exclude,
    )


def _clean_prefixes(raw: object) -> tuple[str, ...]:
    """Keep only prefixes that are safe to interpolate into a pattern.

    Configuration is input. A prefix reaching `re.compile` unchecked is a repository
    able to hand this tool a pathological pattern, which is the same class of defect
    as an unvalidated subprocess argument.
    """
    if not isinstance(raw, list):
        return ()
    return tuple(
        p.strip().upper()
        for p in raw
        if isinstance(p, str) and _PREFIX_TOKEN.match(p.strip().upper())
    )


# ─── Reader registry ─────────────────────────────────────────────────────────

Reader = Callable[[Path, ReaderConfig], RequirementSet]

_READERS: dict[str, Reader] = {}


def register_reader(name: str, reader: Reader) -> None:
    """Add a requirement source. The extension point ADR-007 asks for.

    A ReqIF importer, a tracker exporter that runs in-process, or an
    organisation's bespoke format registers here and every downstream surface —
    lint, trace, the score — reads it without changing.
    """
    _READERS[name] = reader


def registered_readers() -> tuple[str, ...]:
    return tuple(sorted(_READERS))


# ─── Reader: referenced (tier 1) ─────────────────────────────────────────────


def _iter_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in _SOURCE_SUFFIXES:
            continue
        if any(part in _SKIP_DIRS for part in path.parts):
            continue
        try:
            if path.stat().st_size > _MAX_FILE_BYTES:
                continue
        except OSError:
            continue
        yield path


def _citation_kind(relative: str) -> str:
    return "test" if _TEST_PATH.search(relative.lower()) else "source"


def read_referenced(root: Path, config: ReaderConfig) -> RequirementSet:
    """Tier 1 — requirement IDs cited from code, tests, and commit messages.

    Costs an adopting team nothing: they keep their tracker and write `REQ-1234` in a
    test name or a commit trailer. From that alone the two findings teams most need
    become available — a requirement with no test, and a change with no requirement.
    """
    pattern = config.id_pattern
    citations: list[Citation] = []

    for path in _iter_files(root):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        relative = path.relative_to(root).as_posix()
        if any(fragment in relative for fragment in config.exclude):
            continue
        kind = _citation_kind(relative)
        for lineno, line in enumerate(text.splitlines(), start=1):
            for match in pattern.finditer(line):
                citations.append(
                    Citation(requirement_id=match.group(1), location=relative, kind=kind, line=lineno)
                )

    citations.extend(_commit_citations(root, config))

    requirements = {
        c.requirement_id: Requirement(id=c.requirement_id, origin="referenced") for c in citations
    }
    if not requirements:
        return RequirementSet(
            tier=Tier.INVISIBLE,
            notes=[
                "no requirement identifiers found in code, tests, or commits "
                f"(looking for {'/'.join(config.id_prefixes)}-NNN)"
            ],
        )
    return RequirementSet(
        tier=Tier.REFERENCED,
        requirements=requirements,
        citations=citations,
        notes=[f"{len(requirements)} requirement id(s) cited in {len(citations)} place(s)"],
    )


def _commit_citations(root: Path, config: ReaderConfig) -> list[Citation]:
    """Requirement IDs declared in commit **trailers** — not anywhere in the body.

    ADR-007 says a team cites `REQ-1234` in "a test name or a commit trailer", and
    the distinction turned out to matter: scanning whole commit bodies read this
    repository's own history as citing a requirement, because a commit message
    *quoting the ADR's example sentence* is prose about the format rather than a
    declaration of a requirement. A trailer is deliberate and machine-readable; a
    mention in prose is neither, and treating them alike manufactures requirements
    out of people discussing requirements.

    Returns nothing rather than raising when history is unavailable — a shallow
    clone, an export, or a directory that is not a repository are all ordinary, and
    none of them is evidence of a governance failure.
    """
    try:
        result = subprocess.run(
            # Every argument is a literal or an int bounded by `load_config`. Nothing
            # from the repository under inspection reaches this list as text.
            ["git", "log", "-n", str(int(config.commit_limit)), "--no-merges", "--format=%H%x1f%B%x1e"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
            timeout=20,
        )
    except (subprocess.SubprocessError, OSError):
        return []

    pattern = config.id_pattern
    citations: list[Citation] = []
    for record in result.stdout.split("\x1e"):
        if "\x1f" not in record:
            continue
        sha, _, body = record.partition("\x1f")
        sha = sha.strip()
        if not sha:
            continue
        trailer_values = "\n".join(
            m.group(1) for line in body.splitlines() if (m := _TRAILER.match(line))
        )
        for rid in dict.fromkeys(m.group(1) for m in pattern.finditer(trailer_values)):
            citations.append(Citation(requirement_id=rid, location=f"commit:{sha[:12]}", kind="commit"))
    return citations


# ─── Reader: manifest (tiers 2 and 3) ────────────────────────────────────────

_MANIFEST_CANDIDATES: tuple[str, ...] = (
    "requirements.governova.json",
    "governance/requirements.json",
    ".governova/requirements.json",
)


def find_manifest(root: Path, config: ReaderConfig) -> Path | None:
    """Locate the manifest — declared path first, then conventional locations."""
    if config.manifest_path:
        declared = root / config.manifest_path
        return declared if declared.is_file() else None
    for candidate in _MANIFEST_CANDIDATES:
        path = root / candidate
        if path.is_file():
            return path
    return None


def _manifest_records(text: str) -> list[object]:
    """Validate the envelope and return the record list. Raises `ManifestError`.

    The envelope and the records fail for unrelated reasons — a wrong schema
    version against a record missing an id — and reading them in one function
    meant every new envelope rule deepened the loop below it.
    """
    try:
        data = json.loads(text)
    except ValueError as exc:
        raise ManifestError(f"manifest is not valid JSON ({type(exc).__name__})") from exc
    if not isinstance(data, dict):
        raise ManifestError("manifest must be an object")

    version = data.get("schema_version")
    if not isinstance(version, str) or not version.strip():
        raise ManifestError("manifest is missing `schema_version`")
    if version.split(".", 1)[0] != MANIFEST_SCHEMA_VERSION.split(".", 1)[0]:
        raise ManifestError(
            f"manifest schema_version {version!r} is not compatible with "
            f"{MANIFEST_SCHEMA_VERSION!r} supported here"
        )

    raw = data.get("requirements")
    if not isinstance(raw, list):
        raise ManifestError("manifest `requirements` must be a list")
    return raw


def _requirement_from_record(item: object, position: int, origin: str) -> Requirement:
    """One record. Raises `ManifestError` naming the record that is wrong.

    `position` is in every message that cannot quote an id, because "requirement
    #7 is not an object" is findable and "manifest is malformed" is not.
    """
    if not isinstance(item, dict):
        raise ManifestError(f"requirement #{position} is not an object")

    rid = item.get("id")
    if not isinstance(rid, str) or not rid.strip():
        raise ManifestError(f"requirement #{position} has no `id`")

    kind = item.get("kind")
    if kind is not None and kind not in KINDS:
        raise ManifestError(f"{rid}: kind {kind!r} is not one of {sorted(KINDS)}")

    obligation = item.get("obligation")
    if obligation is not None and obligation not in OBLIGATIONS:
        raise ManifestError(
            f"{rid}: obligation {obligation!r} is not one of {sorted(OBLIGATIONS)}"
        )

    return Requirement(
        id=rid.strip(),
        statement=_text_or_none(item.get("statement")),
        kind=kind,
        obligation=obligation,
        source=_text_or_none(item.get("source")),
        acceptance=_text_or_none(item.get("acceptance")),
        origin=origin,
    )


def parse_manifest(text: str, *, origin: str = "manifest") -> list[Requirement]:
    """Parse the interchange manifest. Raises `ManifestError` on anything malformed.

    Strict on purpose. A manifest is a published contract that other people's
    exporters write against, and silently skipping a record the writer believed was
    accepted would make the contract untestable from their side.
    """
    return [
        _requirement_from_record(item, position, origin)
        for position, item in enumerate(_manifest_records(text))
    ]


def _text_or_none(value: object) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def read_manifest(root: Path, config: ReaderConfig) -> RequirementSet:
    """Tiers 2 and 3 — a manifest, however it was produced.

    Native authoring and a tracker export are the same input here by design: the
    manifest is the contract, and who wrote it is the team's business. A manifest
    that exists but cannot be parsed is reported rather than swallowed — a broken
    export is a fact the team needs, and treating it as absence would hide it.
    """
    path = find_manifest(root, config)
    if path is None:
        return RequirementSet(tier=Tier.INVISIBLE, notes=["no requirements manifest found"])
    relative = path.relative_to(root).as_posix() if path.is_relative_to(root) else path.name
    try:
        requirements = parse_manifest(path.read_text(encoding="utf-8"))
    except OSError:
        return RequirementSet(tier=Tier.INVISIBLE, notes=[f"{relative} could not be read"])
    except ManifestError as exc:
        return RequirementSet(tier=Tier.INVISIBLE, notes=[f"{relative}: {exc}"])

    return RequirementSet(
        tier=Tier.EXPORTED,
        requirements={r.id: r for r in requirements},
        notes=[f"{len(requirements)} requirement(s) read from {relative}"],
    )


register_reader("referenced", read_referenced)
register_reader("manifest", read_manifest)


def collect(root: Path, config: ReaderConfig | None = None) -> RequirementSet:
    """Run every registered reader and merge the results.

    A reader that raises is skipped with a note rather than failing the run: one
    broken source must not make the others unreadable, and the note keeps the failure
    visible instead of turning it into a silent tier-0.
    """
    cfg = config or load_config(root)
    combined = RequirementSet()
    for name in registered_readers():
        try:
            combined = combined.merge(_READERS[name](root, cfg))
        except Exception as exc:
            combined.notes.append(f"reader {name!r} failed ({type(exc).__name__})")
    return combined
