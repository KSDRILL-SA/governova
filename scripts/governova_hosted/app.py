"""The hosted read API.

FastAPI, per `S8.2`, and shaped by the same route rules the identity service
follows: `/api/v1/` on everything (`S6.22`) and `/health` outside it (`S6.23`).

**Every endpoint is a view.** The bodies below are three lines each, and that is
the design rather than an accident of scope. The moment one of them computes
something — filters a factor, rounds a number, decides a threshold — the hosted
answer and the local answer become two implementations of one question, and they
will eventually disagree. So each endpoint delegates to the engine function the
CLI calls and serialises the result with the engine's own renderer.

**Read-only, structurally.** Only `@router.get` appears here, and a test asserts
no route is registered under any other method. Stage 4 reports; it does not
mutate. Billing writes go through the Gateway (Stage 3) and organisation writes
through Stage 1, both of which own invariants this surface has no way to honour.

**What Stage 4 does not do.** No database — the snapshot history is in memory and
says so, the same admission Stage 0 makes about its grant store. No pagination,
no per-organisation routing: this serves one repository, named at construction.
"""

from __future__ import annotations

import dataclasses
import datetime as dt
import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, FastAPI, Header, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from governova_identity.app import AUDIENCE
from governova_identity.tokens import SigningKey

API_PREFIX = "/api/v1"


@dataclasses.dataclass(frozen=True)
class Snapshot:
    """What the score *was*, on a date. Never an answer to what it *is*.

    The tempting shape for a hosted score is a stored one: compute it nightly,
    serve the stored value, answer instantly. It would also be a **cache that can
    disagree with the thing it caches**, which is the failure `ADR-012` guards on
    the headline and `#255` guards on the ledger balance.

    So a stored score exists here, and it is only ever reachable through
    `/score/history`, in this shape, with `taken_on` on every row. A consumer
    cannot mistake one of these for the current score even by accident — and
    `test_the_live_score_is_never_read_from_history` asserts the live path never
    touches them.
    """

    taken_on: dt.date
    score: int
    grade: str
    has_quorum: bool
    assessed_weight: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "taken_on": self.taken_on.isoformat(),
            "score": self.score,
            "grade": self.grade,
            "has_quorum": self.has_quorum,
            "assessed_weight": self.assessed_weight,
        }


class HostedService:
    """The repository being served, the key that verifies callers, and history.

    Held on an instance rather than at module scope so each test gets a clean
    one — the same reason `DeviceGrantStore` is built this way.

    `verifier` is required and has no default. An optional one would mean this
    service could start with authentication off, and a governance report names a
    company's unfixed violations: it is the last thing that should become
    world-readable because a deployment forgot a variable.
    """

    def __init__(
        self,
        root: Path,
        verifier: SigningKey,
        *,
        history: list[Snapshot] | None = None,
    ) -> None:
        self.root = root
        self.verifier = verifier
        self.history: list[Snapshot] = list(history or [])

    # ── The engine, called exactly as the CLI calls it ───────────────────────

    def score_json(self) -> str:
        """Byte-identical to `governova govscore --format json`."""
        from governova_score import compute_score, to_json

        return to_json(compute_score(self.root))

    def report_json(self) -> str:
        """Byte-identical to `governova report --format json`."""
        from governova_report import build_report, to_json

        return to_json(build_report(self.root))

    def report_markdown(self) -> str:
        """Byte-identical to `governova report --format markdown`."""
        from governova_report import build_report, to_markdown

        return to_markdown(build_report(self.root))

    def coverage(self) -> dict[str, Any]:
        from governova_checks import enforcement_coverage
        from governova_compile.writer import load_active_index

        return enforcement_coverage(load_active_index(start=self.root))

    def audit(self) -> dict[str, Any]:
        from governova_audit import verify

        result = verify(self.root)
        return {
            "valid": result.valid,
            "records": result.records,
            "issues": result.issues,
            "summary": result.summary,
        }

    def dashboard_html(self) -> str:
        """`build_html`, not a re-composition of its parts.

        The dashboard is Score + coverage + R/A/G areas assembled in a particular
        way. Assembling them again here would be a second dashboard that looks
        like the first one until either is changed.
        """
        from governova_dashboard import build_html

        return build_html(self.root)


def _authenticate(service: HostedService, authorization: str) -> None:
    """Verify the bearer token with the issuer's own verifier.

    Not a second, weaker check. `SigningKey.verify` pins RS256 explicitly, which
    is what stops the algorithm-confusion attack, and re-deriving that here would
    mean two places to get it right. It also returns a reason rather than raising,
    and `TokenError.sentence` already holds the words a person needs — so the 401
    below can say a session expired instead of saying `invalid_token`.
    """
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
            detail={
                "error": "unauthorised",
                "message": "this endpoint reports on a repository's governance and "
                "needs a session — run `governova login`.",
            },
        )

    verified = service.verifier.verify(token.strip(), audience=AUDIENCE)
    if verified.error is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
            detail={"error": verified.error.value, "message": verified.error.sentence},
        )


def create_app(service: HostedService) -> FastAPI:
    """The hosted read surface."""
    app = FastAPI(
        title="Governova Hosted",
        version="0.1.0",
        description="Views of what the engine already computed. Stage 4 of Workstream D.",
    )
    app.state.service = service

    @app.get("/health", tags=["health"])
    def health() -> dict[str, Any]:
        """`S6.23`. Unauthenticated on purpose: a load balancer carries no token.

        It reports that the process is up and which repository it serves. It
        reports nothing about that repository's governance, which is the part
        that needs a session.
        """
        return {
            "status": "healthy",
            "repository": str(service.root),
            "timestamp": dt.datetime.now(dt.UTC).isoformat(),
        }

    app.include_router(_router(service), prefix=API_PREFIX)
    return app


def _router(service: HostedService) -> APIRouter:
    router = APIRouter(tags=["hosted"])

    @router.get("/score")
    def score(authorization: str = Header(default="")) -> JSONResponse:
        """The Governova Score, computed now, in the CLI's exact serialisation."""
        _authenticate(service, authorization)
        return JSONResponse(json.loads(service.score_json()))

    @router.get("/score/history")
    def score_history(authorization: str = Header(default="")) -> JSONResponse:
        """What the score *was*. See `Snapshot` for why this is a separate path."""
        _authenticate(service, authorization)
        return JSONResponse({"snapshots": [s.as_dict() for s in service.history]})

    @router.get("/report")
    def report(authorization: str = Header(default="")) -> JSONResponse:
        """The Board-Level Governance Report, as JSON."""
        _authenticate(service, authorization)
        return JSONResponse(json.loads(service.report_json()))

    @router.get("/report/markdown", response_class=PlainTextResponse)
    def report_markdown(authorization: str = Header(default="")) -> str:
        """The same report as markdown, for a board pack."""
        _authenticate(service, authorization)
        return service.report_markdown()

    @router.get("/coverage")
    def coverage(authorization: str = Header(default="")) -> JSONResponse:
        """How much of the constitution is mechanically enforceable."""
        _authenticate(service, authorization)
        return JSONResponse(service.coverage())

    @router.get("/audit")
    def audit(authorization: str = Header(default="")) -> JSONResponse:
        """The chain's integrity, from the same verifier `governova audit` uses."""
        _authenticate(service, authorization)
        return JSONResponse(service.audit())

    @router.get("/dashboard", response_class=HTMLResponse)
    def dashboard(authorization: str = Header(default="")) -> str:
        """The same standalone HTML `governova dashboard` writes."""
        _authenticate(service, authorization)
        return service.dashboard_html()

    return router
