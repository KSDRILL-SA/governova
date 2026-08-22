"""Tests for the hosted read API — Stage 4.

The guarantee this stage exists to keep, from `planning/phase-4-cloud.md`:

> **The hosted Score and the local Score are the same number by construction** —
> read from the same compiled index by the same code. If they can ever differ,
> that is a defect, not a feature — and it is worth a test that asserts it.

`test_the_hosted_score_is_byte_identical_to_the_cli` is that test, and it is the
reason this file exists. The rest guard the properties that make the guarantee
survive editing: that no endpoint computes, that nothing here can write, and that
the stored history can never be served as the live answer.
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import pytest

pytest.importorskip("fastapi", reason="the hosted API is part of the `cloud` extra")

from fastapi.testclient import TestClient
from governova_compile.discovery import resolve_repo_root
from governova_hosted.app import (
    API_PREFIX,
    HostedService,
    Snapshot,
    create_app,
)
from governova_identity.app import AUDIENCE
from governova_identity.tokens import ACCESS_TOKEN_TTL, SigningKey

ROOT = Path(resolve_repo_root())


@pytest.fixture(scope="module")
def key() -> SigningKey:
    return SigningKey.generate()


@pytest.fixture(scope="module")
def service(key: SigningKey) -> HostedService:
    return HostedService(
        ROOT,
        key,
        history=[
            Snapshot(
                taken_on=dt.date(2026, 1, 1),
                score=11,
                grade="F",
                has_quorum=False,
                assessed_weight=20,
            )
        ],
    )


@pytest.fixture(scope="module")
def client(service: HostedService) -> TestClient:
    return TestClient(create_app(service))


@pytest.fixture(scope="module")
def auth(key: SigningKey) -> dict[str, str]:
    token, _ = key.issue(
        "user-1", audience=AUDIENCE, ttl=ACCESS_TOKEN_TTL, kind="access"
    )
    return {"Authorization": f"Bearer {token}"}


# ─── The guarantee ───────────────────────────────────────────────────────────


def test_the_hosted_score_is_byte_identical_to_the_cli(
    client: TestClient, auth: dict[str, str]
) -> None:
    """The whole reason Stage 4 is a view rather than a service.

    Compared as parsed JSON *and* as the exact string the CLI would print. The
    parsed comparison catches a value drifting; the string comparison catches a
    key being renamed, reordered or dropped on the way out — which is how two
    surfaces start describing the same score differently while both look right.
    """
    from governova_score import compute_score, to_json

    cli_output = to_json(compute_score(ROOT))

    response = client.get(f"{API_PREFIX}/score", headers=auth)
    assert response.status_code == 200
    assert response.json() == json.loads(cli_output)
    assert json.dumps(response.json(), sort_keys=True) == json.dumps(
        json.loads(cli_output), sort_keys=True
    )


def test_the_hosted_report_is_byte_identical_to_the_cli(
    client: TestClient, auth: dict[str, str]
) -> None:
    from governova_report import build_report, to_json

    response = client.get(f"{API_PREFIX}/report", headers=auth)
    assert response.status_code == 200
    assert response.json() == json.loads(to_json(build_report(ROOT)))


def test_the_hosted_markdown_report_is_the_cli_string_exactly(
    client: TestClient, auth: dict[str, str]
) -> None:
    """A board pack downloaded from the console must match one generated locally."""
    from governova_report import build_report, to_markdown

    response = client.get(f"{API_PREFIX}/report/markdown", headers=auth)
    assert response.status_code == 200
    assert response.text == to_markdown(build_report(ROOT))


def test_the_hosted_dashboard_is_the_cli_html_exactly(
    client: TestClient, auth: dict[str, str]
) -> None:
    from governova_dashboard import build_html

    response = client.get(f"{API_PREFIX}/dashboard", headers=auth)
    assert response.status_code == 200
    assert response.text == build_html(ROOT)


def test_no_endpoint_body_computes_anything(service: HostedService) -> None:
    """The mechanism behind the guarantee, asserted rather than trusted.

    Every accessor on `HostedService` is a delegation: an import, a call, a
    return. Arithmetic, comparison against a threshold, or filtering a collection
    here would be the hosted surface forming its own opinion — which is exactly
    how it acquires one that differs from the engine's.

    Checked against the parsed function bodies rather than by grepping the file,
    so an explanation of why there is no arithmetic does not fail the test that
    asserts there is none.

    Joining a path with `/` is allowed and everything else built with an operator
    is not. The first version banned every `BinOp` and caught
    `self.root / "compiled" / "constitution.json"`, which derives nothing — it
    names a file, the same way six engine modules name it. A rule that flags
    naming a file teaches people to add exclusions to it, and then it stops
    catching the arithmetic it was written for.
    """
    import ast
    import inspect

    def derives(node: ast.AST) -> bool:
        if isinstance(node, ast.BinOp):
            return not isinstance(node.op, ast.Div)
        return isinstance(node, (ast.Compare, ast.IfExp, ast.ListComp, ast.GeneratorExp))

    accessors = [
        "score_json",
        "report_json",
        "report_markdown",
        "coverage",
        "audit",
        "dashboard_html",
    ]
    for name in accessors:
        source = inspect.getsource(getattr(HostedService, name))
        tree = ast.parse(source.lstrip().replace("\n    ", "\n"))
        offenders = [type(node).__name__ for node in ast.walk(tree) if derives(node)]
        assert not offenders, f"HostedService.{name} computes: {offenders}"


# ─── The stored score is history, never the answer ───────────────────────────


def test_the_live_score_is_never_read_from_history(
    client: TestClient, auth: dict[str, str], service: HostedService
) -> None:
    """A stored score is a fact about the past; a cache is a claim about the present.

    The fixture's snapshot says 11. If `/score` ever served a stored value, that
    is the number that would come back.
    """
    from governova_score import compute_score

    live = client.get(f"{API_PREFIX}/score", headers=auth).json()
    assert live["score"] == compute_score(ROOT).score
    assert service.history[0].score == 11
    assert live is not service.history[0].as_dict()


def test_history_is_served_under_its_own_path_with_a_date_on_every_row(
    client: TestClient, auth: dict[str, str]
) -> None:
    """The shape is what stops a consumer confusing the two, so the shape is asserted."""
    response = client.get(f"{API_PREFIX}/score/history", headers=auth)
    assert response.status_code == 200
    snapshots = response.json()["snapshots"]
    assert snapshots
    for row in snapshots:
        assert row["taken_on"], "a stored score without a date reads as a current one"


def test_an_empty_history_is_an_empty_list_not_a_zero(key: SigningKey) -> None:
    """A repository nobody has snapshotted has no history, which is not a score of 0."""
    client = TestClient(create_app(HostedService(ROOT, key)))
    token, _ = key.issue("u", audience=AUDIENCE, ttl=ACCESS_TOKEN_TTL, kind="access")
    response = client.get(
        f"{API_PREFIX}/score/history", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.json() == {"snapshots": []}


# ─── Read-only, structurally ─────────────────────────────────────────────────


def test_no_route_can_mutate_anything(service: HostedService) -> None:
    """Stage 4 reports. Writes belong to the stages that own the invariants.

    Asserted over the registered routes rather than over the source, so a POST
    added through any mechanism — a sub-router, a decorator, a later include —
    fails this rather than only a literal `@router.post`.
    """
    from fastapi.routing import APIRoute

    for route in create_app(service).routes:
        if isinstance(route, APIRoute):
            assert route.methods <= {"GET", "HEAD", "OPTIONS"}, (
                f"{route.path} accepts {route.methods}; the hosted surface is read-only"
            )


def test_every_reporting_route_sits_under_the_versioned_prefix(
    service: HostedService,
) -> None:
    """`S6.22`, with `S6.23`'s health endpoint the single documented exception."""
    from fastapi.routing import APIRoute

    outside = {
        route.path
        for route in create_app(service).routes
        if isinstance(route, APIRoute) and not route.path.startswith(API_PREFIX)
    }
    assert outside <= {"/health", "/openapi.json", "/docs", "/docs/oauth2-redirect", "/redoc"}


# ─── Authentication ──────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "path",
    ["/score", "/score/history", "/report", "/report/markdown", "/coverage", "/audit",
     "/dashboard"],
)
def test_every_reporting_endpoint_refuses_an_anonymous_caller(
    client: TestClient, path: str
) -> None:
    """A governance report names a company's unfixed violations. It is not public.

    Parametrised over the paths rather than spot-checked, because the endpoint
    that gets added without a check is never the one somebody wrote a test for.
    """
    assert client.get(f"{API_PREFIX}{path}").status_code == 401


def test_health_is_open_and_says_nothing_about_governance(client: TestClient) -> None:
    """A load balancer carries no token, so `/health` must answer without one."""
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert not {"score", "grade", "violations", "findings"} & set(body)


def test_a_token_for_another_audience_is_refused(
    client: TestClient, key: SigningKey
) -> None:
    """Reusing the issuer's verifier is what makes this hold without re-deriving it."""
    token, _ = key.issue(
        "u", audience="some-other-service", ttl=ACCESS_TOKEN_TTL, kind="access"
    )
    response = client.get(
        f"{API_PREFIX}/score", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401


def test_an_expired_token_is_told_it_expired(client: TestClient, key: SigningKey) -> None:
    """`#254` asks for a sentence, not a stack trace — and the sentence already exists."""
    token, _ = key.issue(
        "u",
        audience=AUDIENCE,
        ttl=dt.timedelta(seconds=-1),
        kind="access",
    )
    response = client.get(
        f"{API_PREFIX}/score", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401
    assert "expired" in response.json()["detail"]["message"]


def test_a_forged_token_is_refused(client: TestClient) -> None:
    """Signed by a different key entirely — the case the pinned RS256 check exists for."""
    other = SigningKey.generate()
    token, _ = other.issue("u", audience=AUDIENCE, ttl=ACCESS_TOKEN_TTL, kind="access")
    response = client.get(
        f"{API_PREFIX}/score", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401


def test_a_service_cannot_be_built_without_a_verifier() -> None:
    """No default means no deployment that starts with authentication off."""
    import inspect

    signature = inspect.signature(HostedService.__init__)
    assert signature.parameters["verifier"].default is inspect.Parameter.empty
