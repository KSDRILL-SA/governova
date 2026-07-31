"""governova_supply — dependency licence governance and SBOM generation.

Implements the parts of `S8.85` that are deterministic: every dependency's licence
is checked against an allowlist, and an SBOM is generated for releases. The CVE
half of `S8.84` is deliberately **not** implemented here — see below.

**Why this is not a CVE scanner.** Matching packages against advisory databases is
a solved problem with maintained tooling (`pip-audit`, backed by OSV and the PyPI
advisory database). Reimplementing it would mean shipping a vulnerability database
that goes stale between releases, and a stale CVE gate is worse than none because
it reports "clean" for advisories it has never heard of. `S1.107` — the simplest
correct solution — says use the existing tool for the network-backed half, and add
value where there is none: the licence check below is stdlib-only, needs no
network, and works offline in any consumer's CI.

Licences are read from installed distribution metadata rather than from a
lockfile, because the lockfile records what was resolved and the metadata records
what is actually importable. It is the second that ships.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from importlib.metadata import Distribution, distributions
from typing import Any

# SPDX identifiers whose terms impose no source-disclosure obligation on a
# distributed work. A dependency outside this set is not "bad" — it requires a
# recorded L4 exception, which is what S8.85 asks for.
ALLOWED_LICENCES: frozenset[str] = frozenset(
    {
        "MIT",
        "MIT-0",
        "BSD-2-Clause",
        "BSD-3-Clause",
        "0BSD",
        "Apache-2.0",
        "ISC",
        "PSF-2.0",
        "Python-2.0",
        "Unlicense",
        "CC0-1.0",
        "Zlib",
        "MPL-2.0",  # file-level copyleft; imposes nothing on a work that merely imports it
    }
)

# Free-text licence fields are not SPDX. This maps the forms actually seen in
# published metadata onto their identifiers; anything unmapped stays UNKNOWN and
# is reported rather than guessed, because guessing a licence permissive is the
# one error this check exists to prevent.
_NORMALISE: dict[str, str] = {
    "mit": "MIT",
    "mit license": "MIT",
    "the mit license": "MIT",
    "mit license (mit)": "MIT",
    "bsd": "BSD-3-Clause",
    "bsd license": "BSD-3-Clause",
    "bsd 2-clause license": "BSD-2-Clause",
    "bsd 3-clause license": "BSD-3-Clause",
    "bsd-2-clause": "BSD-2-Clause",
    "bsd-3-clause": "BSD-3-Clause",
    "apache 2.0": "Apache-2.0",
    "apache-2.0": "Apache-2.0",
    "apache software license": "Apache-2.0",
    "apache license 2.0": "Apache-2.0",
    "apache license, version 2.0": "Apache-2.0",
    "isc": "ISC",
    "isc license": "ISC",
    "isc license (iscl)": "ISC",
    "python software foundation license": "PSF-2.0",
    "psf": "PSF-2.0",
    "psf-2.0": "PSF-2.0",
    "the unlicense (unlicense)": "Unlicense",
    "unlicense": "Unlicense",
    "mozilla public license 2.0 (mpl 2.0)": "MPL-2.0",
    "mpl-2.0": "MPL-2.0",
    "gnu lesser general public license v3 (lgplv3)": "LGPL-3.0-only",
    "lgpl-3.0-only": "LGPL-3.0-only",
    "gnu general public license v3 (gplv3)": "GPL-3.0-only",
    "zlib": "Zlib",
    "cc0-1.0": "CC0-1.0",
}

_SPDX_SPLIT = re.compile(r"\s+(AND|OR)\s+", re.I)


@dataclass(frozen=True)
class Package:
    name: str
    version: str
    licence: str  # normalised SPDX expression, or "UNKNOWN"
    allowed: bool


@dataclass(frozen=True)
class LicenceReport:
    packages: list[Package] = field(default_factory=list)

    @property
    def disallowed(self) -> list[Package]:
        return [p for p in self.packages if not p.allowed]

    @property
    def ok(self) -> bool:
        return not self.disallowed

    @property
    def summary(self) -> str:
        if self.ok:
            return f"{len(self.packages)} dependency licence(s) all on the allowlist"
        names = ", ".join(f"{p.name} ({p.licence})" for p in self.disallowed[:5])
        return f"{len(self.disallowed)} of {len(self.packages)} require an exception: {names}"


def normalise(raw: str) -> str:
    """Map a free-text licence field onto an SPDX identifier, or UNKNOWN."""
    text = (raw or "").strip().rstrip(".")
    if not text:
        return "UNKNOWN"
    # Already an SPDX expression with operators — normalise each operand.
    if _SPDX_SPLIT.search(text):
        parts = _SPDX_SPLIT.split(text)
        return " ".join(
            p.upper() if p.lower() in ("and", "or") else normalise(p) for p in parts
        )
    lowered = text.lower()
    if lowered in _NORMALISE:
        return _NORMALISE[lowered]
    # A bare identifier that already looks like SPDX (no spaces) is taken as-is,
    # so a correctly-declaring package is not punished for being ahead of the map.
    if " " not in text and any(c.isalpha() for c in text):
        return text
    return "UNKNOWN"


def is_allowed(expression: str) -> bool:
    """SPDX semantics: OR needs one acceptable operand, AND needs all of them."""
    if not _SPDX_SPLIT.search(expression):
        return expression in ALLOWED_LICENCES
    parts = _SPDX_SPLIT.split(expression)
    operands = parts[::2]
    operators = {op.upper() for op in parts[1::2]}
    if "AND" in operators:
        return all(is_allowed(o) for o in operands)
    return any(is_allowed(o) for o in operands)


def _declared_licence(dist: Distribution) -> str:
    """Read a licence from distribution metadata, preferring the modern field."""
    meta = dist.metadata
    for key in ("License-Expression", "License"):
        value = meta.get(key)
        # Some packages paste their entire licence text into `License`.
        if value and len(value) <= 60:
            return str(value)
    for classifier in meta.get_all("Classifier") or []:
        if classifier.startswith("License ::"):
            return classifier.split(" :: ")[-1]
    return ""


def installed_packages(exceptions: set[str] | None = None) -> LicenceReport:  # REQ-007
    """Licence-classify every installed distribution.

    `exceptions` names packages with a recorded L4 exception; they are reported
    as allowed so the gate stays green while the exception remains on record.
    """
    excepted = {e.lower() for e in (exceptions or set())}
    packages: list[Package] = []
    seen: set[str] = set()
    for dist in distributions():
        name = dist.metadata.get("Name")
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        licence = normalise(_declared_licence(dist))
        packages.append(
            Package(
                name=str(name),
                version=dist.version or "0",
                licence=licence,
                allowed=is_allowed(licence) or name.lower() in excepted,
            )
        )
    packages.sort(key=lambda p: p.name.lower())
    return LicenceReport(packages=packages)


def sbom(report: LicenceReport | None = None, *, component: str = "governova") -> dict[str, Any]:
    """A CycloneDX 1.5 SBOM of the installed dependency set.

    Emitted directly rather than via a generator dependency: the format is a
    documented schema, this is the minimum conformant subset, and an SBOM tool
    that itself pulls in a dependency tree is a poor trade for a supply-chain
    artifact.
    """
    rep = report or installed_packages()
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "version": 1,
        "metadata": {
            "timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
            "component": {"type": "application", "name": component},
            "tools": [{"vendor": "KSDRILL SA", "name": "governova"}],
        },
        "components": [
            {
                "type": "library",
                "name": p.name,
                "version": p.version,
                "purl": f"pkg:pypi/{p.name.lower()}@{p.version}",
                "licenses": (
                    [{"expression": p.licence}] if p.licence != "UNKNOWN" else []
                ),
            }
            for p in rep.packages
        ],
    }


def sbom_json(report: LicenceReport | None = None, *, component: str = "governova") -> str:
    return json.dumps(sbom(report, component=component), indent=2, sort_keys=True)
