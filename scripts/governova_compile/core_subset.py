"""The core subset of the corpus — what a free wheel is entitled to carry.

`ADR-011` §1 licenses the corpus and leaves the engine MIT. From v0.3.0 the
published wheel bundles a **core subset**; the full corpus, the domain packs and
ongoing amendments require a subscription.

The boundary lives in `governance/core-subset.toml` as data, not here as code.
This module reads it and produces a second index — nothing in it decides what is
free. That separation is the point: the commercial boundary is `ADR-011`'s to
set and L4's to ratify, and it must be reviewable in a diff rather than inferred
from a build script.

**The gate is entitlement to *data*, never a check on executing code.** `ADR-010`
§5.1 prohibits a licence server, machine-ID binding and phoning home, and this
mechanism touches none of them: it decides which file is placed in a wheel at
build time. The engine runs identically against whichever corpus it is handed,
and runs offline forever against either.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from governova_compile.schema import CompiledIndex

MANIFEST_RELATIVE = "governance/core-subset.toml"


@dataclass(frozen=True)
class CoreManifest:
    """The declared boundary between the free wheel and the licensed corpus."""

    constitutions: tuple[str, ...]
    domains: tuple[str, ...] = ()
    include_framework: bool = True
    include_runbooks: bool = False
    include_adrs: bool = False
    basis: str = ""
    ratified: bool = False

    # Constitutions named in the manifest that the corpus does not contain. A
    # typo here would silently shrink what the free tier receives, and silence
    # is the failure mode that matters: the wheel would build, install and
    # govern with fewer standards than anyone intended.
    missing: tuple[str, ...] = field(default=())


def load_manifest(root: Path) -> CoreManifest:
    """Read the core-subset manifest from a repository root."""
    path = root / MANIFEST_RELATIVE
    if not path.is_file():
        raise FileNotFoundError(
            f"No core-subset manifest at {path}. ADR-011 requires the free wheel's "
            "boundary to be declared as data; the build will not guess it."
        )
    raw = tomllib.loads(path.read_text(encoding="utf-8"))
    core = raw.get("core", {})
    criterion = raw.get("criterion", {})
    return CoreManifest(
        constitutions=tuple(core.get("constitutions", ())),
        domains=tuple(core.get("domains", ())),
        include_framework=bool(core.get("include_framework", True)),
        include_runbooks=bool(core.get("include_runbooks", False)),
        include_adrs=bool(core.get("include_adrs", False)),
        basis=str(criterion.get("basis", "")),
        ratified=bool(criterion.get("ratified", False)),
    )


def core_index(index: CompiledIndex, manifest: CoreManifest) -> CompiledIndex:
    """The subset of `index` the manifest declares free.

    Whole constitutions only. A subset assembled standard by standard breaks
    cross-references, and a free tier whose standards cite standards it does not
    carry teaches an adopter that the product is broken rather than that it is
    partial.
    """
    wanted = {c.upper() for c in manifest.constitutions}
    wanted_domains = {d.upper() for d in manifest.domains}

    subset = index.model_copy(deep=True)
    subset.constitutions = [c for c in index.constitutions if c.id.upper() in wanted]
    subset.domains = [d for d in index.domains if d.id.upper() in wanted_domains]
    if not manifest.include_framework:
        subset.framework = []
    if not manifest.include_runbooks:
        subset.runbooks = []
    if not manifest.include_adrs:
        subset.adrs = []

    # An implementation guide is stack-specific advice *for one constitution*.
    # A guide for a constitution the subset does not carry is advice about law
    # the reader does not have, so it goes with its constitution rather than
    # being carried as an orphan.
    subset.implementations = [
        impl for impl in index.implementations if impl.binds_constitution.upper() in wanted
    ]
    return subset


def unknown_constitutions(index: CompiledIndex, manifest: CoreManifest) -> tuple[str, ...]:
    """Manifest entries the corpus does not contain.

    A typo silently shrinks the free tier, and the wheel still builds, installs
    and governs — with fewer standards than anyone chose. The compile step turns
    this into a loud failure.
    """
    known = {c.id.upper() for c in index.constitutions}
    known_domains = {d.id.upper() for d in index.domains}
    missing = [c for c in manifest.constitutions if c.upper() not in known]
    missing += [d for d in manifest.domains if d.upper() not in known_domains]
    return tuple(missing)
