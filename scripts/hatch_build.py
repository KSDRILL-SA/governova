"""Build hook that bundles the compiled constitution into the wheel.

An installed `governova` must carry its own constitution, or it cannot govern a
repository that does not contain one. The file lives at `compiled/constitution.json`
in the repository root — one copy, no committed duplicate to drift.

**Why a hook rather than a static `force-include`.** A `force-include` of
`../compiled/constitution.json` works when building from the repository and fails
when building from an sdist, because the sdist root *is* the project directory and
nothing exists above it. `uv build` builds the wheel from the sdist by default, so
the static form produced a working wheel locally and a broken one in any release
pipeline — and an sdist that cannot build a wheel is also broken for anyone
installing with `--no-binary`.

The hook resolves the file at build time from wherever it actually is:

- `../compiled/constitution.json` — building in the repository
- `./compiled/constitution.json`  — building from an unpacked sdist, where the
  sdist target places it (see `[tool.hatch.build.targets.sdist.force-include]`)

Failing loudly is deliberate. A wheel without the constitution installs cleanly
and then fails on first use, which is a defect the person installing it discovers
rather than the person shipping it.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    from hatchling.builders.hooks.plugin.interface import BuildHookInterface
except ModuleNotFoundError:  # pragma: no cover - only absent outside a build
    # hatchling is a build-time dependency, present only while a distribution is
    # being built. The resolver below needs nothing from it, and the test suite
    # exercises the resolver — so the module must import in an ordinary
    # environment rather than failing and taking those tests with it. The hook
    # class is instantiated by hatchling alone, so this base is never used.
    BuildHookInterface = object

BUNDLED_AT = "governova_compile/data/constitution.json"
_CANDIDATES = ("../compiled/constitution.json", "compiled/constitution.json")


def locate_constitution(root: Path) -> Path:
    """Find the compiled constitution relative to a build root.

    Separate from the hook so it is testable without hatchling's plugin
    machinery — the hook itself is then a two-line adapter.
    """
    for relative in _CANDIDATES:
        candidate = (root / relative).resolve()
        if candidate.is_file():
            return candidate

    searched = ", ".join(str(root / c) for c in _CANDIDATES)
    raise FileNotFoundError(
        "Cannot build the governova wheel: the compiled constitution was not "
        f"found. Looked in: {searched}. Run `governova compile` first."
    )


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        if self.target_name != "wheel":
            return
        found = locate_constitution(Path(self.root))
        build_data.setdefault("force_include", {})[str(found)] = BUNDLED_AT
