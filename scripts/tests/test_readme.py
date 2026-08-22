"""The front door states numbers the engine can confirm.

The README is the first thing anyone sees, and every number on it was
hand-maintained. That is the same defect Governova exists to name: a metric
nobody regenerates drifts from the thing it describes, and the drift is invisible
because nothing checks.

It had drifted. The badge advertised **78 (C)** and the prose "61 of 596
evidenced" while the engine computed **80 (B)** and 113 — so the shop window
understated the product by two points and by half the evidence, for anyone who
read it between the last hand-edit and this test.

A governance tool whose own headline number is stale has published exactly the
failure it sells the cure for.
"""

from __future__ import annotations

import re
from pathlib import Path

from governova_compile.discovery import resolve_repo_root
from governova_score import compute_score

ROOT = Path(resolve_repo_root())
README = (ROOT / "README.md").read_text(encoding="utf-8")


def test_readme_states_the_score_the_engine_computes() -> None:
    """The badge and the prose both, because they drifted independently."""
    score = compute_score(ROOT)
    assert score.headline is not None, (
        "the repository is below quorum, so the README must not claim a score at all"
    )

    badge = re.search(r"Governova_Score-(\d{1,3})%2F100_\((\w)\)", README)
    assert badge, "the Governova Score badge is missing or no longer machine-readable"

    stated, grade = int(badge.group(1)), badge.group(2)
    assert stated == score.headline, (
        f"the README badge says {stated}/100; the engine computes {score.headline}/100. "
        "Regenerate it: `governova govscore --format badge`."
    )
    assert grade == score.grade, f"the badge grade says {grade}; the engine says {score.grade}"


def test_the_readme_does_not_quote_an_unreproducible_count() -> None:
    """The README may state the score. It may not state the evidenced count.

    The count moves with the environment and the headline does not. Measured on
    one commit, three ways:

        full checkout, Windows        113 of 596
        shallow clone, same branch    114 of 596   (`S1.22` has no merge commit
                                                    to find in a one-commit
                                                    history, so it flips clean)
        CI, Linux, shallow            112 of 596   (unexplained; see `D-29`)

    The headline is 80 (B) in all three, because a two-standard swing moves the
    coverage factor by 0.2 and the weighted total by 0.04.

    So the badge is quotable and the count is not. Writing the count on the front
    page means the front page is wrong for somebody, and a governance product
    cannot publish a number that depends on how the reader cloned it.

    The fix for `D-29` is to make the count reproducible, not to quote it more
    carefully — and when that lands, this test is where the decision to publish
    it again gets recorded.
    """
    assert "of 596" not in README, (
        "the README quotes an evidenced/applicable count, which is not reproducible "
        "across environments — see D-29"
    )


def test_the_readme_tells_a_newcomer_to_install_rather_than_clone() -> None:
    """It told them to clone, for as long as the package has been on PyPI.

    Cloning is right for reading the corpus or governing Governova itself. It is
    the wrong first instruction for somebody who wants to govern *their own*
    project, and it was the only one offered.
    """
    quick_start = README.split("## Quick start", 1)
    assert len(quick_start) == 2, "the README has no Quick start section"
    body = quick_start[1].split("\n## ", 1)[0]

    assert "pip install governova" in body, "the quick start does not tell anyone to install it"
    assert body.index("pip install governova") < body.index("git clone"), (
        "the quick start offers `git clone` before `pip install` — the first instruction "
        "a newcomer reads should be the one that governs their own project"
    )


def test_the_readme_does_not_promise_a_cloud_that_runs_nowhere() -> None:
    """`D-09`: the Cloud is written and deployed nowhere.

    Advertising a hosted service, credits or a dashboard that nobody can reach
    is the one kind of inaccuracy a governance product cannot afford on its own
    front page. When a Cloud stage is actually deployed, this test is the place
    that records the decision to say so.
    """
    forbidden = (
        "sign up",
        "start free trial",
        "app.governova",
        "cloud.governova",
        "dashboard.governova",
    )
    lowered = README.lower()
    claimed = [phrase for phrase in forbidden if phrase in lowered]
    assert not claimed, f"the README promises a hosted service that does not run: {claimed}"
