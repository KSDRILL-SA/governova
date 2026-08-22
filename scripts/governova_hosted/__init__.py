"""governova_hosted — the hosted read surface. Stage 4 of Workstream D.

Views of what the engine already computed. Not a re-implementation, not a
re-computation, not a second opinion: every endpoint calls the same function the
CLI calls and serialises the result with the same renderer.

`planning/phase-4-cloud.md` states the guarantee this stage exists to keep:

> **The hosted Score and the local Score are the same number by construction** —
> read from the same compiled index by the same code. If they can ever differ,
> that is a defect, not a feature — and it is worth a test that asserts it.

"By construction" is taken literally here. `/score` returns
`to_json(compute_score(root))`, character for character what
`governova govscore --format json` prints, and `test_hosted.py` compares the two
strings rather than two numbers that happen to agree today.

Installed as part of `governova[cloud]`, for the reason `ADR-010` §5.1 gives:
the deterministic engine runs complete and offline forever, so a consumer who
installs `governova` to govern a repository must never acquire a web framework
to do it. That direction is asserted by `test_identity_isolation.py`, which
treats this package the same way it treats `governova_identity`.
"""

from __future__ import annotations

__all__ = ["__doc__"]
