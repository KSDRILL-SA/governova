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


def test_readme_states_the_evidence_count_the_engine_computes() -> None:
    """The sentence that explains the score has to survive the score moving.

    This is the half that rotted hardest — a badge at least looks like a number
    somebody might check, while a count buried in prose reads as background.
    """
    coverage = next(
        factor for factor in compute_score(ROOT).factors
        if factor.key == "constitutional_coverage"
    )
    # The sentence wraps, and it wraps inside a blockquote, so the separator
    # between the two halves can be `\n> `. Matching only spaces made this test
    # fail on prose it was supposed to be reading.
    evidenced = re.search(
        r"(\d+) of (\d+)[\s>]*applicable standards are \*evidenced\*", README
    )
    assert evidenced, "the README no longer states an evidenced/applicable count"

    stated_evidenced, stated_applicable = int(evidenced.group(1)), int(evidenced.group(2))
    detail = coverage.detail
    actual = re.search(r"(\d+)/(\d+) applicable standard", detail)
    assert actual, f"the coverage factor's detail changed shape: {detail!r}"

    assert (stated_evidenced, stated_applicable) == (int(actual.group(1)), int(actual.group(2))), (
        f"the README says {stated_evidenced} of {stated_applicable} evidenced; the engine "
        f"reports {actual.group(1)} of {actual.group(2)}. Run `governova govscore`."
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
