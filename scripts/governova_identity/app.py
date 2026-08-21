"""The identity service — the only issuer.

FastAPI, per `S8.2` and `ADR-010` §2. Everything it does is one of four things:
start a device grant, let a human approve one, exchange an approved grant for
tokens, and let a verifier fetch the public key.

**Route placement.** `S6.22` requires an `/api/v1/` prefix on all routes and
`S6.23` places the health endpoint at `/health` for FastAPI. Two paths sit
outside the prefix and both are fixed by specification rather than by choice:
`/.well-known/jwks.json` is defined by RFC 8615 to live at the root, and a client
that follows RFC 8414 discovery will look there and nowhere else. Moving it under
the prefix would make the service unusable by a conforming client while looking
tidier. That is recorded here rather than left for a reader to wonder about.

**What Stage 0 does not do.** No database (Stage 1), no organisations, no seats,
no billing, no Gateway. The store is in memory and says so.
"""

from __future__ import annotations

import datetime as dt
import os
from typing import Any

from fastapi import APIRouter, FastAPI, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from governova_identity.device_grant import DeviceGrantStore, PollOutcome
from governova_identity.tokens import (
    ACCESS_TOKEN_TTL,
    REFRESH_TOKEN_TTL,
    SigningKey,
    TokenError,
    load_signing_key,
)

API_PREFIX = "/api/v1"
AUDIENCE = "governova-cli"
DEVICE_CODE_GRANT = "urn:ietf:params:oauth:grant-type:device_code"


class DeviceCodeResponse(BaseModel):
    """RFC 8628 §3.2."""

    device_code: str
    user_code: str
    verification_uri: str
    verification_uri_complete: str
    expires_in: int
    interval: int


class TokenRequest(BaseModel):
    grant_type: str
    device_code: str | None = None
    refresh_token: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int


class ApprovalRequest(BaseModel):
    user_code: str
    subject: str = Field(description="Who is approving. Stage 1 replaces this with a session.")
    approve: bool = True


class Identity(BaseModel):
    subject: str
    scopes: list[str]
    expires_at: dt.datetime


class IdentityService:
    """The service's state, kept off module scope so tests get a fresh one.

    A module-level singleton would make every test share one store and one
    revocation list, and the first test to revoke a token would change the
    outcome of the rest.
    """

    def __init__(self, key: SigningKey, *, base_url: str = "http://localhost:8000") -> None:
        self.key = key
        self.grants = DeviceGrantStore()
        self.base_url = base_url.rstrip("/")
        # Revoked token ids. In memory for Stage 0, like everything else here.
        # Stage 1 moves it to PostgreSQL, at which point it survives a restart —
        # today a restart un-revokes, which is recorded rather than hidden.
        self.revoked: set[str] = set()

    def now(self) -> dt.datetime:
        return dt.datetime.now(dt.UTC)


def create_app(
    service: IdentityService | None = None,
    *,
    env: dict[str, str] | None = None,
) -> FastAPI:
    """Build the app. Raises at startup when no signing key is configured.

    Failing here is deliberate: a service that starts without a key and issues
    unverifiable tokens is worse than one that does not start, because the first
    person to notice is a user who cannot log in and has nothing to point at.
    """
    if service is None:
        service = IdentityService(load_signing_key(dict(env if env is not None else os.environ)))

    app = FastAPI(
        title="Governova Identity",
        version="0.1.0",
        description="Device grant and RS256 token issuance. Stage 0 of Workstream D.",
    )
    app.state.service = service

    _mount_wellknown(app, service)
    _mount_health(app, service)
    app.include_router(_api_router(service), prefix=API_PREFIX)
    return app


def _mount_wellknown(app: FastAPI, service: IdentityService) -> None:
    @app.get("/.well-known/jwks.json", tags=["discovery"])
    def jwks() -> dict[str, Any]:
        """The public half of the signing key. Never anything else."""
        return service.key.jwks()

    @app.get("/.well-known/oauth-authorization-server", tags=["discovery"])
    def metadata() -> dict[str, Any]:
        """RFC 8414 — so a client can find the endpoints without them being hardcoded."""
        return {
            "issuer": service.base_url,
            "device_authorization_endpoint": f"{service.base_url}{API_PREFIX}/oauth/device/code",
            "token_endpoint": f"{service.base_url}{API_PREFIX}/oauth/token",
            "revocation_endpoint": f"{service.base_url}{API_PREFIX}/oauth/revoke",
            "jwks_uri": f"{service.base_url}/.well-known/jwks.json",
            "grant_types_supported": [DEVICE_CODE_GRANT, "refresh_token"],
            "id_token_signing_alg_values_supported": ["RS256"],
        }


def _mount_health(app: FastAPI, service: IdentityService) -> None:
    @app.get("/health", tags=["health"])
    def health() -> dict[str, Any]:
        """`S6.23`/`S2.48` — 200 with the state of what this service depends on.

        Stage 0 depends on a signing key and nothing else. When Stage 1 adds a
        database this reports its connectivity too, and returns 503 without it —
        a health endpoint that answers 200 while the database is unreachable is
        `AP-S6.23a`, which this repository ships a standard against.
        """
        return {
            "status": "healthy",
            "signing_key": "loaded",
            "key_id": service.key.key_id,
            "pending_grants": len(service.grants),
            "timestamp": service.now().isoformat(),
        }


def _api_router(service: IdentityService) -> APIRouter:  # noqa: C901
    router = APIRouter(tags=["oauth"])

    @router.post("/oauth/device/code", response_model=DeviceCodeResponse)
    def device_code(request: Request) -> DeviceCodeResponse:
        """Start a login. RFC 8628 §3.1–3.2."""
        now = service.now()
        service.grants.purge_expired(now)
        grant = service.grants.start(now)
        verification = f"{service.base_url}/activate"
        return DeviceCodeResponse(
            device_code=grant.device_code,
            user_code=grant.user_code,
            verification_uri=verification,
            verification_uri_complete=f"{verification}?user_code={grant.user_code}",
            expires_in=int((grant.expires_at - now).total_seconds()),
            interval=grant.interval,
        )

    @router.post("/oauth/device/approve")
    def approve(body: ApprovalRequest) -> dict[str, str]:
        """The browser half. Stage 1 replaces `subject` with a real session."""
        now = service.now()
        if body.approve:
            ok = service.grants.approve(body.user_code, body.subject, now)
        else:
            ok = service.grants.deny(body.user_code, now)
        if not ok:
            # One message for "no such code", "already used" and "expired". They
            # are different internally and telling them apart out loud turns this
            # endpoint into an oracle for probing user codes.
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "invalid_user_code",
                    "message": "That code is not waiting for approval. It may have expired — "
                    "logins are valid for ten minutes. Run `governova login` again.",
                },
            )
        return {"status": "approved" if body.approve else "denied"}

    @router.post("/oauth/token")
    def token(body: TokenRequest) -> JSONResponse:
        """Exchange an approved device code, or refresh. RFC 8628 §3.4–3.5."""
        if body.grant_type == DEVICE_CODE_GRANT:
            return _exchange_device_code(service, body)
        if body.grant_type == "refresh_token":
            return _refresh(service, body)
        return _oauth_error(
            "unsupported_grant_type",
            f"this service supports {DEVICE_CODE_GRANT} and refresh_token",
            status.HTTP_400_BAD_REQUEST,
        )

    @router.post("/oauth/revoke")
    def revoke(authorization: str = Header(default="")) -> dict[str, str]:
        """Revoke the presented token. `#254`: revocation must actually stop it."""
        verified = _verify_header(service, authorization)
        if verified.claims is None:
            # RFC 7009 §2.2 — revocation is idempotent and does not report
            # whether the token was valid. Saying "that token was already
            # invalid" would confirm a guess.
            return {"status": "revoked"}
        service.revoked.add(verified.claims.token_id)
        return {"status": "revoked"}

    @router.get("/me", response_model=Identity)
    def me(authorization: str = Header(default="")) -> Identity:
        """`governova whoami`. The one endpoint that answers "who am I"."""
        verified = _verify_header(service, authorization)
        if verified.claims is None:
            reason = verified.error or TokenError.MALFORMED
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": reason.value, "message": reason.sentence},
            )
        return Identity(
            subject=verified.claims.subject,
            scopes=list(verified.claims.scopes),
            expires_at=verified.claims.expires_at,
        )

    return router


def _exchange_device_code(service: IdentityService, body: TokenRequest) -> JSONResponse:
    if not body.device_code:
        return _oauth_error(
            "invalid_request", "device_code is required", status.HTTP_400_BAD_REQUEST
        )

    outcome, grant = service.grants.poll(body.device_code, service.now())
    if outcome is not PollOutcome.APPROVED or grant is None or grant.subject is None:
        # RFC 8628 §3.5 — `authorization_pending` and `slow_down` are 400s and
        # are the *expected* answers while a human is still deciding, so they are
        # not logged as failures anywhere.
        return _oauth_error(outcome.value, _POLL_MESSAGES[outcome], status.HTTP_400_BAD_REQUEST)

    return _issue_pair(service, grant.subject)


def _refresh(service: IdentityService, body: TokenRequest) -> JSONResponse:
    if not body.refresh_token:
        return _oauth_error(
            "invalid_request", "refresh_token is required", status.HTTP_400_BAD_REQUEST
        )
    verified = service.key.verify(
        body.refresh_token, audience=AUDIENCE, revoked=service.revoked
    )
    if verified.claims is None:
        reason = verified.error or TokenError.MALFORMED
        return _oauth_error("invalid_grant", reason.sentence, status.HTTP_400_BAD_REQUEST)
    if verified.claims.kind != "refresh":
        # An access token presented as a refresh token would otherwise extend a
        # session indefinitely without the refresh token ever being held.
        return _oauth_error(
            "invalid_grant",
            "that is an access token, not a refresh token",
            status.HTTP_400_BAD_REQUEST,
        )

    # Rotation: the presented refresh token is revoked as the new pair is issued,
    # so a stolen refresh token is usable exactly once and its use invalidates
    # the copy the real owner holds — which is what makes the theft visible.
    service.revoked.add(verified.claims.token_id)
    return _issue_pair(service, verified.claims.subject)


def _issue_pair(service: IdentityService, subject: str) -> JSONResponse:
    now = service.now()
    access, _ = service.key.issue(
        subject, kind="access", audience=AUDIENCE, scopes=("cli",), now=now
    )
    refresh, _ = service.key.issue(subject, kind="refresh", audience=AUDIENCE, now=now)
    return JSONResponse(
        TokenResponse(
            access_token=access,
            refresh_token=refresh,
            expires_in=int(ACCESS_TOKEN_TTL.total_seconds()),
        ).model_dump()
    )


def _verify_header(service: IdentityService, authorization: str) -> Any:
    scheme, _, raw = authorization.partition(" ")
    if scheme.lower() != "bearer" or not raw:
        from governova_identity.tokens import VerifiedToken

        return VerifiedToken(None, TokenError.MALFORMED)
    return service.key.verify(raw.strip(), audience=AUDIENCE, revoked=service.revoked)


def _oauth_error(code: str, message: str, http_status: int) -> JSONResponse:
    """The shape `S2.19`/`S2.22` require, carrying the RFC 6749 §5.2 field too."""
    return JSONResponse(
        status_code=http_status,
        content={
            "success": False,
            "error": {"code": code, "message": message},
            # RFC 6749 names this field `error`; clients written to the RFC read
            # it at the top level, so it is present in both places rather than
            # forcing every OAuth client to learn our envelope.
            "error_description": message,
        },
    )


_POLL_MESSAGES = {
    PollOutcome.AUTHORIZATION_PENDING: "waiting for you to approve this login in the browser",
    PollOutcome.SLOW_DOWN: "polling too quickly — increase the interval and try again",
    PollOutcome.ACCESS_DENIED: "that login was denied in the browser",
    PollOutcome.EXPIRED_TOKEN: "this login expired — run `governova login` again",
    PollOutcome.INVALID_GRANT: "this login code is not valid",
    PollOutcome.APPROVED: "approved",
}

REFRESH_WINDOW_SECONDS = int(REFRESH_TOKEN_TTL.total_seconds())
