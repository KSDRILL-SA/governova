"""governova_onboard.detect — what a repository is, read from what it contains.

`governance/project.toml` decides which standards apply, so every number in a
baseline report is downstream of it. Getting the profile wrong does not produce a
slightly wrong report — it produces a confident report about the wrong
constitution, and the adopter will believe the numbers long before they think to
question the profile.

So detection obeys the rule the probes and the requirements analyser already
obey: **it reports what it found, names the file it found it in, and where it
found nothing it says so.** There is no inference step. A repository with no
manifest is not "probably Python"; its stack is *undetected*, and the proposal
says so in the place a human has to fill in.

Two dimensions cannot be derived by any amount of scanning, and are never
guessed:

* **Domain** (Layer 4) states which business a system is in. A payments ledger
  and a lesson planner can be structurally identical.
* **Phase** states how far the build lifecycle has been taken. Code on disk
  cannot distinguish "phase 3 reached" from "phase 1, written by someone
  thorough".

Both are reported as requiring a human rather than quietly omitted, because a
field left out of a proposal is a field nobody fills in.

One asymmetry is deliberate. **Stacks come from manifests; languages come from
file counts.** A manifest is a declaration — the repository saying what it is —
and it is the only evidence strong enough to narrow the applicable set. Extension
counts are an observation, reported for the reader's benefit and never fed into
applicability, because "there are four `.rb` files" is not the same claim as
"this is a Ruby project".
"""

from __future__ import annotations

import json
import os
import re
import tomllib
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path

from governova_checks import SKIP_DIRS

# Dimensions that are *probed*. Every one appears in the report even when nothing
# was found, because "we looked for CI and there is none" is the finding.
DIMENSIONS: tuple[str, ...] = ("stack", "language", "tests", "ci", "schema", "requirements")

# Dimensions no scan can settle. Reported as needing a human, never inferred.
UNDERIVABLE: tuple[str, ...] = ("domain", "phase")

# Bounds. A walk over an unknown repository is untrusted input like any other:
# a monorepo with a checked-in node_modules, or a symlink cycle, must not turn a
# read-only baseline into an unbounded traversal.
MAX_FILES = 40_000
MAX_MANIFEST_BYTES = 2_000_000

# Extension → language. Observational only (see the module docstring).
LANGUAGES: Mapping[str, str] = {
    ".py": "python", ".ts": "typescript", ".tsx": "typescript", ".js": "javascript",
    ".jsx": "javascript", ".mjs": "javascript", ".cjs": "javascript", ".go": "go",
    ".rs": "rust", ".java": "java", ".kt": "kotlin", ".rb": "ruby", ".php": "php",
    ".cs": "c#", ".swift": "swift", ".scala": "scala", ".c": "c", ".h": "c",
    ".cpp": "c++", ".cc": "c++", ".hpp": "c++", ".m": "objective-c", ".ex": "elixir",
    ".exs": "elixir", ".dart": "dart", ".vue": "vue", ".svelte": "svelte",
    ".sql": "sql", ".sh": "shell", ".ps1": "powershell",
}

# Directories whose contents describe somebody else's code. Language counts taken
# inside them describe a dependency tree, not the repository.
_EXTRA_SKIP: frozenset[str] = frozenset({"vendor", "third_party", "thirdparty", ".tox", "target"})

_ALL_SKIP: frozenset[str] = SKIP_DIRS | _EXTRA_SKIP

# CI configuration, by the file that proves it.
_CI_FILES: tuple[tuple[str, str], ...] = (
    (".gitlab-ci.yml", "GitLab CI"),
    ("Jenkinsfile", "Jenkins"),
    (".circleci/config.yml", "CircleCI"),
    ("azure-pipelines.yml", "Azure Pipelines"),
    (".travis.yml", "Travis CI"),
    ("bitbucket-pipelines.yml", "Bitbucket Pipelines"),
    (".drone.yml", "Drone"),
)

# Filenames that only exist to hold tests.
_TEST_FILE = re.compile(
    r"(?:^|/)(?:test_[^/]+\.py|[^/]+_test\.(?:py|go|rb|ts|js)"
    r"|[^/]+\.(?:test|spec)\.(?:ts|tsx|js|jsx|mjs)|[^/]+Test\.java|[^/]+Tests\.cs)$"
)
_TEST_DIRS: frozenset[str] = frozenset({"tests", "test", "__tests__", "spec", "specs", "testing"})


@dataclass(frozen=True)
class Signal:
    """One observed fact about the repository, and the file that proves it.

    `evidence` is a repository-relative path. An auditor asking "how do you know"
    gets a path they can open, which is the same bar the structural probes hold.
    """

    dimension: str
    value: str
    evidence: str


@dataclass(frozen=True)
class Detection:
    """Everything the scan could establish, plus what it cost."""

    signals: tuple[Signal, ...] = ()
    name: str = ""
    files_scanned: int = 0
    truncated: bool = False
    """True when the walk hit `MAX_FILES`. The report says so rather than
    presenting a partial count as a total."""

    def of(self, dimension: str) -> tuple[Signal, ...]:
        return tuple(s for s in self.signals if s.dimension == dimension)

    def values(self, dimension: str) -> tuple[str, ...]:
        """Distinct values for a dimension, first-seen order preserved."""
        seen: dict[str, None] = {}
        for signal in self.of(dimension):
            seen.setdefault(signal.value, None)
        return tuple(seen)

    @property
    def stacks(self) -> tuple[str, ...]:
        return self.values("stack")

    @property
    def undetected(self) -> tuple[str, ...]:
        """Dimensions that were probed and yielded nothing."""
        return tuple(d for d in DIMENSIONS if not self.of(d))

    @property
    def empty(self) -> bool:
        """Whether the scan established nothing at all about this repository."""
        return not self.signals


# ── Dependency readers ───────────────────────────────────────────────────────
# Each turns a manifest's text into the set of dependency names it declares.
# Every one is total: an unparseable manifest yields no names rather than raising,
# because a repository with a broken `package.json` is still a repository to
# report on, and the base stack signal survives the parse failure.

_REQUIREMENT_NAME = re.compile(r"\A\s*([A-Za-z0-9][A-Za-z0-9._-]*)")


def _requirement_name(spec: str) -> str:
    """The bare name from a PEP 508 specifier — `fastapi[all]>=0.1` → `fastapi`."""
    match = _REQUIREMENT_NAME.match(spec)
    return match.group(1).lower() if match else ""


def _node_dependencies(text: str) -> set[str]:
    try:
        data = json.loads(text)
    except ValueError:
        return set()
    if not isinstance(data, dict):
        return set()
    names: set[str] = set()
    for key in ("dependencies", "devDependencies", "peerDependencies"):
        block = data.get(key)
        if isinstance(block, dict):
            names.update(str(k).lower() for k in block)
    return names


def _pyproject_dependencies(text: str) -> set[str]:
    try:
        data = tomllib.loads(text)
    except (tomllib.TOMLDecodeError, ValueError):
        return set()
    names: set[str] = set()
    project = data.get("project")
    if isinstance(project, dict):
        declared = project.get("dependencies")
        if isinstance(declared, list):
            names.update(_requirement_name(str(d)) for d in declared)
        optional = project.get("optional-dependencies")
        if isinstance(optional, dict):
            for group in optional.values():
                if isinstance(group, list):
                    names.update(_requirement_name(str(d)) for d in group)
    tool = data.get("tool")
    if isinstance(tool, dict):
        poetry = tool.get("poetry")
        if isinstance(poetry, dict):
            declared_poetry = poetry.get("dependencies")
            if isinstance(declared_poetry, dict):
                names.update(str(k).lower() for k in declared_poetry)
    return {n for n in names if n}


def _requirements_txt_dependencies(text: str) -> set[str]:
    names: set[str] = set()
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith(("#", "-")):
            continue
        name = _requirement_name(line)
        if name:
            names.add(name)
    return names


_MAVEN_ARTIFACT = re.compile(r"<artifactId>\s*([^<\s]+)\s*</artifactId>", re.I)
_GRADLE_COORDINATE = re.compile(r"""['"][A-Za-z0-9._-]+:([A-Za-z0-9._-]+)""")


def _maven_dependencies(text: str) -> set[str]:
    return {m.lower() for m in _MAVEN_ARTIFACT.findall(text)}


def _gradle_dependencies(text: str) -> set[str]:
    return {m.lower() for m in _GRADLE_COORDINATE.findall(text)}


def _composer_dependencies(text: str) -> set[str]:
    try:
        data = json.loads(text)
    except ValueError:
        return set()
    if not isinstance(data, dict):
        return set()
    names: set[str] = set()
    for key in ("require", "require-dev"):
        block = data.get(key)
        if isinstance(block, dict):
            names.update(str(k).lower() for k in block)
    return names


_GEM_NAME = re.compile(r"""^\s*gem\s+['"]([A-Za-z0-9._-]+)['"]""", re.M)


def _gemfile_dependencies(text: str) -> set[str]:
    return {m.lower() for m in _GEM_NAME.findall(text)}


def _no_dependencies(text: str) -> set[str]:
    """For manifests whose contents this engine does not parse.

    The manifest's *existence* is still evidence of the base stack; declaring
    that we read its dependencies when we did not would be the kind of overclaim
    the probes exist to avoid.
    """
    return set()


@dataclass(frozen=True)
class _Manifest:
    """A manifest filename, the stack its presence proves, and its frameworks.

    Framework matching is **exact on the dependency name**. Substring matching
    was rejected: `next` is a substring of `next-auth` and `nextra`, so a
    substring rule would report a Next.js project on the strength of a session
    library. A framework absent from the table degrades to the base stack, which
    is a smaller claim rather than a wrong one.
    """

    filename: str
    base: str
    read: Callable[[str], set[str]]
    frameworks: Mapping[str, str]


MANIFESTS: tuple[_Manifest, ...] = (
    _Manifest("package.json", "node", _node_dependencies, {
        "next": "nextjs",
        "@angular/core": "angular",
        "react": "react",
        "vue": "vue",
        "svelte": "svelte",
        "@sveltejs/kit": "sveltekit",
        "@nestjs/core": "nestjs",
        "express": "express",
        "fastify": "fastify",
    }),
    _Manifest("pyproject.toml", "python", _pyproject_dependencies, {
        "fastapi": "fastapi", "django": "django", "flask": "flask", "litestar": "litestar",
    }),
    _Manifest("requirements.txt", "python", _requirements_txt_dependencies, {
        "fastapi": "fastapi", "django": "django", "flask": "flask", "litestar": "litestar",
    }),
    _Manifest("setup.py", "python", _no_dependencies, {}),
    _Manifest("go.mod", "go", _no_dependencies, {}),
    _Manifest("Cargo.toml", "rust", _no_dependencies, {}),
    _Manifest("pom.xml", "java", _maven_dependencies, {
        "spring-boot-starter": "spring", "spring-boot-starter-web": "spring",
    }),
    _Manifest("build.gradle", "java", _gradle_dependencies, {
        "spring-boot-starter": "spring", "spring-boot-starter-web": "spring",
    }),
    _Manifest("build.gradle.kts", "java", _gradle_dependencies, {
        "spring-boot-starter": "spring", "spring-boot-starter-web": "spring",
    }),
    _Manifest("composer.json", "php", _composer_dependencies, {
        "laravel/framework": "laravel", "symfony/framework-bundle": "symfony",
    }),
    _Manifest("Gemfile", "ruby", _gemfile_dependencies, {"rails": "rails"}),
)

_BY_FILENAME: Mapping[str, _Manifest] = {m.filename: m for m in MANIFESTS}


def _read(path: Path) -> str | None:
    """Manifest text, or None when it cannot be read or is implausibly large."""
    try:
        if path.stat().st_size > MAX_MANIFEST_BYTES:
            return None
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


@dataclass
class _Walk:
    """What one bounded traversal collected."""

    manifests: list[Path]
    language_counts: dict[str, int]
    test_paths: list[str]
    ci_paths: list[str]
    files: int
    truncated: bool


def _walk(root: Path) -> _Walk:
    """One traversal, honouring `SKIP_DIRS` and bounded by `MAX_FILES`.

    A single pass collects everything: repeating the walk per dimension would
    multiply the cost on exactly the large repositories where the cost matters.
    `followlinks` stays off so a symlink loop cannot make this unbounded.
    """
    manifests: list[Path] = []
    language_counts: dict[str, int] = {}
    test_paths: list[str] = []
    ci_paths: list[str] = []
    seen = 0
    truncated = False

    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = sorted(d for d in dirnames if d not in _ALL_SKIP)
        here = Path(dirpath)
        parts = {p.lower() for p in here.relative_to(root).parts}
        in_test_dir = bool(parts & _TEST_DIRS)

        for filename in sorted(filenames):
            seen += 1
            if seen > MAX_FILES:
                truncated = True
                break
            path = here / filename
            relative = path.relative_to(root).as_posix()

            if filename in _BY_FILENAME or filename.endswith((".csproj", ".sln")):
                manifests.append(path)

            suffix = path.suffix.lower()
            language = LANGUAGES.get(suffix)
            if language is not None:
                language_counts[language] = language_counts.get(language, 0) + 1

            # A source file inside a test directory, or a file whose own name
            # says it is a test. The directory alone is not enough: a README in
            # `tests/` is not evidence that this repository has tests.
            looks_like_a_test = (in_test_dir and language is not None) or bool(
                _TEST_FILE.search(relative)
            )
            if len(test_paths) < 4 and looks_like_a_test:
                test_paths.append(relative)
            if relative.startswith(".github/workflows/") and suffix in {".yml", ".yaml"}:
                ci_paths.append(relative)

        if truncated:
            break

    return _Walk(manifests, language_counts, test_paths, ci_paths, seen, truncated)


def _stack_signals(root: Path, manifests: list[Path]) -> list[Signal]:
    """Base stacks and frameworks, each citing the manifest that declares it."""
    signals: list[Signal] = []
    emitted: set[tuple[str, str]] = set()

    for path in sorted(manifests, key=lambda p: (len(p.parts), p.as_posix())):
        relative = path.relative_to(root).as_posix()
        if path.suffix.lower() in {".csproj", ".sln"}:
            key = ("stack", "dotnet")
            if key not in emitted:
                emitted.add(key)
                signals.append(Signal("stack", "dotnet", relative))
            continue

        manifest = _BY_FILENAME[path.name]
        key = ("stack", manifest.base)
        if key not in emitted:
            emitted.add(key)
            signals.append(Signal("stack", manifest.base, relative))

        text = _read(path)
        if text is None:
            continue
        declared = manifest.read(text)
        for dependency, token in manifest.frameworks.items():
            if dependency in declared and ("stack", token) not in emitted:
                emitted.add(("stack", token))
                signals.append(Signal("stack", token, f"{relative} → {dependency}"))
    return signals


def _project_name(root: Path, manifests: list[Path]) -> str:
    """The repository's own name for itself, else its directory name.

    The directory name is a fact about the checkout rather than a guess about the
    project, so it is a safe fallback — and the proposal is reviewed by a human
    who can correct it in one edit.
    """
    for path in sorted(manifests, key=lambda p: (len(p.parts), p.as_posix())):
        text = _read(path)
        if text is None:
            continue
        if path.name == "package.json" or path.name == "composer.json":
            try:
                data = json.loads(text)
            except ValueError:
                continue
            if isinstance(data, dict):
                name = data.get("name")
                if isinstance(name, str) and name.strip():
                    return name.strip()
        elif path.name == "pyproject.toml":
            try:
                data_toml = tomllib.loads(text)
            except (tomllib.TOMLDecodeError, ValueError):
                continue
            project = data_toml.get("project")
            if isinstance(project, dict):
                name = project.get("name")
                if isinstance(name, str) and name.strip():
                    return name.strip()
    return root.name


def detect(root: Path) -> Detection:
    """Everything derivable about `root`, each fact citing its evidence."""
    walk = _walk(root)
    signals: list[Signal] = list(_stack_signals(root, walk.manifests))

    for language, count in sorted(walk.language_counts.items(), key=lambda kv: (-kv[1], kv[0])):
        signals.append(Signal("language", language, f"{count} file(s)"))

    if walk.test_paths:
        signals.append(Signal("tests", "present", walk.test_paths[0]))

    for relative in walk.ci_paths[:3]:
        signals.append(Signal("ci", "GitHub Actions", relative))
    for candidate, label in _CI_FILES:
        if (root / candidate).is_file():
            signals.append(Signal("ci", label, candidate))

    signals.extend(_schema_signals(root))
    signals.extend(_requirements_signals(root))

    return Detection(
        signals=tuple(signals),
        name=_project_name(root, walk.manifests),
        files_scanned=walk.files,
        truncated=walk.truncated,
    )


def _schema_signals(root: Path) -> list[Signal]:
    """Schema files, via the analyser that already knows how to find them."""
    from governova_schema import find_schema_files

    found = find_schema_files(root)
    if not found:
        return []
    first = found[0]
    try:
        relative = first.relative_to(root).as_posix()
    except ValueError:  # pragma: no cover — find_schema_files searches under root
        relative = first.as_posix()
    label = f"{len(found)} file(s)" if len(found) > 1 else "1 file"
    return [Signal("schema", label, relative)]


def _requirements_signals(root: Path) -> list[Signal]:
    """The requirements tier, via the analyser that defines it.

    Tier 0 means *invisible* — no requirements were found — so it produces no
    signal and the dimension is reported as undetected, which is the honest
    reading rather than "tier 0" dressed up as a result.
    """
    from governova_requirements import Tier, collect

    found = collect(root)
    if found.tier is Tier.INVISIBLE:
        return []
    evidence = found.notes[0] if found.notes else f"{len(found.requirements)} requirement(s)"
    return [Signal("requirements", f"tier {int(found.tier)}", evidence)]


__all__ = [
    "DIMENSIONS",
    "LANGUAGES",
    "MANIFESTS",
    "MAX_FILES",
    "MAX_MANIFEST_BYTES",
    "UNDERIVABLE",
    "Detection",
    "Signal",
    "detect",
]
