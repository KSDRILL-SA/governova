"""governova_onboard — arriving at a repository Governova has never seen.

Governova can govern a repository it has always governed. Until this package it
could not **onboard** one it had never seen, and every real adopter arrives with
a system that already exists. The engine had the analysis; it had no way to
arrive.

That is the whole gap, and it is why this package is mostly assembly. The rules,
the structural probes, the requirements analyser, the schema analyser, the score
and the applicability model were all built already. What was missing was an entry
point that runs them against somebody else's code and reports the result in a
form a stranger can trust on first reading.

Three properties are load-bearing, in the order they matter:

1. **It is read-only.** `assess` writes nothing. `propose.accept` is the only
   function in this package that touches the filesystem, it writes exactly one
   file, and it refuses to overwrite an existing one.
2. **Detection degrades, it never guesses.** A dimension that could not be
   determined is reported as undetermined, and the two dimensions no scan can
   settle — Layer 4 domain and lifecycle phase — are never inferred at all.
3. **The profile is a proposal.** `governance/project.toml` decides which
   standards apply, so it is rendered for review and written only on an explicit
   instruction. An adopter believes the numbers before they question the profile
   that produced them, which is exactly why the profile cannot be silent.

Read `protocols/brownfield-adoption.md` for the human protocol this mechanises,
and `planning/phase-3-brownfield.md` for the staged plan it opens.
"""

from __future__ import annotations

from governova_onboard.baseline import (
    DEFAULT_TOP,
    Baseline,
    ConstitutionGap,
    FindingGroup,
    assess,
    proposed_profile,
)
from governova_onboard.detect import (
    DIMENSIONS,
    UNDERIVABLE,
    Detection,
    Signal,
    detect,
)
from governova_onboard.propose import ProfileExistsError, accept, render_profile
from governova_onboard.render import roadmap_to_json, to_json
from governova_onboard.roadmap import Item, Kind, Protection, Roadmap
from governova_onboard.roadmap import build as build_roadmap

# `render_profile` is deliberately not named `render`: `governova_onboard.render`
# is a module in this package, and importing it binds that name on the package,
# silently shadowing any function of the same name re-exported here. The first
# call site hit exactly that and failed with "'module' object is not callable".
__all__ = [
    "DEFAULT_TOP",
    "DIMENSIONS",
    "UNDERIVABLE",
    "Baseline",
    "ConstitutionGap",
    "Detection",
    "FindingGroup",
    "Item",
    "Kind",
    "ProfileExistsError",
    "Protection",
    "Roadmap",
    "Signal",
    "accept",
    "assess",
    "build_roadmap",
    "detect",
    "proposed_profile",
    "render_profile",
    "roadmap_to_json",
    "to_json",
]
