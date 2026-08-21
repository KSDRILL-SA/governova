"""Tests for the identity service — Stage 0 of Workstream D.

This is the stage `#254` calls the one where a mistake is most expensive to undo,
so the tests below are weighted toward the properties that are hard to fix after
tokens have been issued: what the public endpoint discloses, what a revoked token
can still do, and what a client learns from an error it should not.
"""

from __future__ import annotations

import datetime as dt

import pytest

fastapi_testclient = pytest.importorskip(
    "fastapi.testclient",
    reason="the identity service is an extra: `pip install governova[cloud]`",
)
TestClient = fastapi_testclient.TestClient

from governova_identity.app import (  # noqa: E402
    API_PREFIX,
    AUDIENCE,
    DEVICE_CODE_GRANT,
    IdentityService,
    create_app,
)
from governova_identity.device_grant import (  # noqa: E402
    DeviceGrantStore,
    PollOutcome,
    normalise_user_code,
)
from governova_identity.tokens import (  # noqa: E402
    ENV_PRIVATE_KEY,
    ENV_PRIVATE_KEY_FILE,
    MissingSigningKeyError,
    SigningKey,
    TokenError,
    load_signing_key,
)

# One key for the whole module. Generating RSA is slow, and every test that needs
# a *different* key makes one explicitly.
_KEY = SigningKey.generate()


@pytest.fixture
def service() -> IdentityService:
    """A fresh service per test.

    Not a module-level singleton: the first test to revoke a token would
    otherwise change the outcome of every test after it.
    """
    return IdentityService(_KEY)


@pytest.fixture
def client(service: IdentityService) -> TestClient:
    return TestClient(create_app(service))


def _login(client: TestClient, subject: str = "person@example.invalid") -> dict:
    """Drive a whole device grant and return the token payload."""
    started = client.post(f"{API_PREFIX}/oauth/device/code").json()
    approved = client.post(
        f"{API_PREFIX}/oauth/device/approve",
        json={"user_code": started["user_code"], "subject": subject},
    )
    assert approved.status_code == 200
    token = client.post(
        f"{API_PREFIX}/oauth/token",
        json={"grant_type": DEVICE_CODE_GRANT, "device_code": started["device_code"]},
    )
    assert token.status_code == 200, token.text
    return token.json()


# ─── The signing key ─────────────────────────────────────────────────────────


def test_the_service_refuses_to_start_without_a_signing_key() -> None:
    """No key means no service. It never generates one to carry on.

    A generated key works perfectly in development and issues tokens that stop
    verifying the next restart — and in a fleet, every instance mints tokens the
    others reject. The symptom is intermittent logouts that look like a client
    bug, which is the worst kind of failure to hand somebody.
    """
    with pytest.raises(MissingSigningKeyError) as caught:
        load_signing_key({})
    assert ENV_PRIVATE_KEY in str(caught.value)


def test_a_key_file_that_does_not_exist_is_refused_rather_than_ignored(tmp_path) -> None:
    with pytest.raises(MissingSigningKeyError):
        load_signing_key({ENV_PRIVATE_KEY_FILE: str(tmp_path / "absent.pem")})


def test_a_key_is_loaded_from_a_file(tmp_path) -> None:
    pem = tmp_path / "signing.pem"
    pem.write_bytes(_pem_of(SigningKey.generate()))
    assert load_signing_key({ENV_PRIVATE_KEY_FILE: str(pem)}).key_id


def test_an_undersized_key_is_refused() -> None:
    """1024-bit RSA is still loadable and still not acceptable for a token."""
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    weak = rsa.generate_private_key(public_exponent=65537, key_size=1024)
    pem = weak.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    with pytest.raises(ValueError, match="2048"):
        SigningKey(pem)


def _pem_of(key: SigningKey) -> bytes:
    return key._private_pem


# ─── What the public endpoint discloses ──────────────────────────────────────


def test_the_jwks_endpoint_publishes_only_public_material(client: TestClient) -> None:
    """The failure this guards against publishes the signing key to the internet.

    It would look exactly like a working service — every token would verify, and
    so would every token anyone else chose to mint.
    """
    body = client.get("/.well-known/jwks.json")
    assert body.status_code == 200
    text = body.text

    for forbidden in ("PRIVATE KEY", "-----BEGIN", '"d"', '"p"', '"q"', '"dp"', '"dq"', '"qi"'):
        assert forbidden not in text, f"the JWKS document leaked {forbidden}"

    key = body.json()["keys"][0]
    assert key["kty"] == "RSA"
    assert key["alg"] == "RS256"
    assert set(key) == {"kty", "use", "alg", "kid", "n", "e"}


def test_the_key_id_is_stable_across_instances() -> None:
    """A restart must not invalidate a cached JWKS, so `kid` is derived from the key."""
    pem = _pem_of(_KEY)
    assert SigningKey(pem).key_id == SigningKey(pem).key_id


def test_rs256_is_what_is_advertised_and_what_is_used(client: TestClient) -> None:
    metadata = client.get("/.well-known/oauth-authorization-server").json()
    assert metadata["id_token_signing_alg_values_supported"] == ["RS256"]
    assert DEVICE_CODE_GRANT in metadata["grant_types_supported"]


# ─── The device grant ────────────────────────────────────────────────────────


def test_a_user_code_avoids_the_characters_people_mistype() -> None:
    """`0`/`O` and `1`/`I`/`L` are indistinguishable read off one screen.

    A mistyped code is indistinguishable from a wrong one, so the user is told
    their code is invalid and has no way to learn why.
    """
    store = DeviceGrantStore()
    now = dt.datetime.now(dt.UTC)
    codes = [store.start(now).user_code for _ in range(60)]
    for code in codes:
        assert not set(code) & set("O0I1L"), code


def test_a_user_code_is_read_back_the_way_a_person_types_it() -> None:
    """Case and hyphens are cosmetic. Rejecting them costs the login and teaches nothing."""
    assert normalise_user_code("bcdf-gh23") == normalise_user_code("BCDFGH23")


def test_the_device_code_carries_more_entropy_than_the_user_code() -> None:
    """The user code is short because a human types it; the device code is not."""
    store = DeviceGrantStore()
    grant = store.start(dt.datetime.now(dt.UTC))
    assert len(grant.device_code) > 4 * len(grant.user_code)


def test_polling_before_the_interval_is_told_to_slow_down() -> None:
    """Without this the user code's small keyspace is searched at any rate a client likes."""
    store = DeviceGrantStore()
    now = dt.datetime.now(dt.UTC)
    grant = store.start(now)

    assert store.poll(grant.device_code, now)[0] is PollOutcome.AUTHORIZATION_PENDING
    assert store.poll(grant.device_code, now)[0] is PollOutcome.SLOW_DOWN


def test_hammering_the_endpoint_does_not_hold_the_poll_window_open() -> None:
    """A refused poll must not reset the clock, or the limit is self-defeating."""
    store = DeviceGrantStore()
    now = dt.datetime.now(dt.UTC)
    grant = store.start(now)
    store.poll(grant.device_code, now)

    for _ in range(20):
        assert store.poll(grant.device_code, now)[0] is PollOutcome.SLOW_DOWN

    later = now + dt.timedelta(seconds=grant.interval)
    assert store.poll(grant.device_code, later)[0] is PollOutcome.AUTHORIZATION_PENDING


def test_an_expired_grant_is_refused() -> None:
    store = DeviceGrantStore()
    now = dt.datetime.now(dt.UTC)
    grant = store.start(now)
    assert store.poll(grant.device_code, now + dt.timedelta(hours=1))[0] is (
        PollOutcome.EXPIRED_TOKEN
    )


def test_an_unknown_device_code_is_refused_without_revealing_anything() -> None:
    """Answered before the rate-limit branch, so the response is not an oracle."""
    store = DeviceGrantStore()
    outcome, grant = store.poll("not-a-real-code", dt.datetime.now(dt.UTC))
    assert outcome is PollOutcome.INVALID_GRANT
    assert grant is None


def test_a_device_code_can_be_exchanged_exactly_once(client: TestClient) -> None:
    """A code captured from a log or a shell history must not be replayable."""
    started = client.post(f"{API_PREFIX}/oauth/device/code").json()
    client.post(
        f"{API_PREFIX}/oauth/device/approve",
        json={"user_code": started["user_code"], "subject": "a@example.invalid"},
    )
    body = {"grant_type": DEVICE_CODE_GRANT, "device_code": started["device_code"]}

    assert client.post(f"{API_PREFIX}/oauth/token", json=body).status_code == 200
    replay = client.post(f"{API_PREFIX}/oauth/token", json=body)
    assert replay.status_code == 400
    assert replay.json()["error"]["code"] == "invalid_grant"


def test_a_denied_login_says_so(client: TestClient) -> None:
    started = client.post(f"{API_PREFIX}/oauth/device/code").json()
    client.post(
        f"{API_PREFIX}/oauth/device/approve",
        json={"user_code": started["user_code"], "subject": "a@example.invalid", "approve": False},
    )
    refused = client.post(
        f"{API_PREFIX}/oauth/token",
        json={"grant_type": DEVICE_CODE_GRANT, "device_code": started["device_code"]},
    )
    assert refused.json()["error"]["code"] == "access_denied"


def test_approving_a_code_that_is_not_waiting_gives_one_answer(client: TestClient) -> None:
    """"No such code", "already used" and "expired" must not be distinguishable.

    Telling them apart turns this endpoint into an oracle for probing the small
    user-code keyspace.
    """
    refused = client.post(
        f"{API_PREFIX}/oauth/device/approve",
        json={"user_code": "ZZZZ-9999", "subject": "a@example.invalid"},
    )
    assert refused.status_code == 400
    assert refused.json()["detail"]["error"] == "invalid_user_code"


# ─── Tokens ──────────────────────────────────────────────────────────────────


def test_a_full_login_issues_a_verifiable_pair(client: TestClient) -> None:
    tokens = _login(client)
    assert tokens["token_type"] == "Bearer"
    assert tokens["expires_in"] == 900

    verified = _KEY.verify(tokens["access_token"], audience=AUDIENCE)
    assert verified.ok
    assert verified.claims is not None
    assert verified.claims.subject == "person@example.invalid"
    assert verified.claims.kind == "access"


def test_whoami_answers_for_a_valid_token(client: TestClient) -> None:
    tokens = _login(client, "someone@example.invalid")
    me = client.get(
        f"{API_PREFIX}/me", headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    assert me.status_code == 200
    assert me.json()["subject"] == "someone@example.invalid"


def _forge(header: dict, payload: dict, secret: bytes) -> str:
    """Build a JWT by hand, HMAC-signed with `secret`.

    Constructed manually because PyJWT *refuses to encode* HMAC with an
    asymmetric key — it blocks the attack on the way in. That protection is
    welcome and it is not the property under test: what matters is that our
    `verify` refuses the token even when an attacker builds it without PyJWT,
    which they obviously would.
    """
    import base64
    import hashlib
    import hmac
    import json

    def part(obj: dict) -> bytes:
        raw = json.dumps(obj, separators=(",", ":")).encode()
        return base64.urlsafe_b64encode(raw).rstrip(b"=")

    signing_input = part(header) + b"." + part(payload)
    signature = hmac.new(secret, signing_input, hashlib.sha256).digest()
    return (
        signing_input + b"." + base64.urlsafe_b64encode(signature).rstrip(b"=")
    ).decode("ascii")


def test_a_token_hmac_signed_with_the_published_key_is_refused() -> None:
    """Algorithm confusion — the attack that turns a public key into a signing key.

    The JWKS document is published, so anyone can fetch it. If verification
    honoured the header's `alg`, an attacker could HMAC-sign a token using the
    *public* key as the shared secret and it would verify. `algorithms` is
    pinned to RS256 for exactly this.
    """
    forged = _forge(
        {"alg": "HS256", "typ": "JWT"},
        {
            "iss": "https://identity.governova.dev",
            "sub": "attacker",
            "aud": AUDIENCE,
            "exp": int((dt.datetime.now(dt.UTC) + dt.timedelta(hours=1)).timestamp()),
        },
        _KEY.public_pem,
    )
    assert not _KEY.verify(forged, audience=AUDIENCE).ok


def test_an_unsigned_token_is_refused() -> None:
    """`alg: none` — the other half of the same family."""
    unsigned = _forge(
        {"alg": "none", "typ": "JWT"},
        {"iss": "https://identity.governova.dev", "sub": "attacker", "aud": AUDIENCE},
        b"",
    )
    assert not _KEY.verify(unsigned, audience=AUDIENCE).ok


def test_a_token_from_another_issuer_is_refused() -> None:
    other = SigningKey.generate()
    token, _ = other.issue("someone", audience=AUDIENCE)
    assert not _KEY.verify(token, audience=AUDIENCE).ok


def test_an_expired_token_is_refused_with_a_sentence() -> None:
    token, _ = _KEY.issue(
        "someone",
        audience=AUDIENCE,
        ttl=dt.timedelta(seconds=-1),
        now=dt.datetime.now(dt.UTC) - dt.timedelta(minutes=1),
    )
    result = _KEY.verify(token, audience=AUDIENCE)
    assert result.error is TokenError.EXPIRED
    assert "log in" in result.error.sentence or "login" in result.error.sentence


def test_a_token_for_a_different_audience_is_refused() -> None:
    token, _ = _KEY.issue("someone", audience="some-other-service")
    assert _KEY.verify(token, audience=AUDIENCE).error is TokenError.WRONG_AUDIENCE


# ─── Revocation — `#254` acceptance criterion 2 ──────────────────────────────


def test_a_revoked_token_stops_working_and_says_why(client: TestClient) -> None:
    """The criterion: revocation works, and the failure is a sentence."""
    tokens = _login(client)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    assert client.get(f"{API_PREFIX}/me", headers=headers).status_code == 200

    assert client.post(f"{API_PREFIX}/oauth/revoke", headers=headers).status_code == 200

    after = client.get(f"{API_PREFIX}/me", headers=headers)
    assert after.status_code == 401
    detail = after.json()["detail"]
    assert detail["error"] == "revoked"
    assert detail["message"].strip().endswith("again")
    assert "Traceback" not in after.text


def test_revoking_an_invalid_token_reports_success(client: TestClient) -> None:
    """RFC 7009 §2.2 — idempotent, and it must not confirm a guess."""
    refused = client.post(
        f"{API_PREFIX}/oauth/revoke", headers={"Authorization": "Bearer nonsense"}
    )
    assert refused.status_code == 200


def test_a_refresh_token_rotates_and_the_old_one_dies(client: TestClient) -> None:
    """A stolen refresh token is usable once, and using it locks out the thief or the owner.

    Either way somebody notices, which is the point — a refresh token that can be
    replayed forever is a permanent, silent compromise.
    """
    tokens = _login(client)
    first = tokens["refresh_token"]

    refreshed = client.post(
        f"{API_PREFIX}/oauth/token", json={"grant_type": "refresh_token", "refresh_token": first}
    )
    assert refreshed.status_code == 200
    assert refreshed.json()["refresh_token"] != first

    replay = client.post(
        f"{API_PREFIX}/oauth/token", json={"grant_type": "refresh_token", "refresh_token": first}
    )
    assert replay.status_code == 400
    assert replay.json()["error"]["code"] == "invalid_grant"


def test_an_access_token_cannot_be_used_as_a_refresh_token(client: TestClient) -> None:
    """Otherwise a session extends indefinitely without the refresh token ever being held."""
    tokens = _login(client)
    refused = client.post(
        f"{API_PREFIX}/oauth/token",
        json={"grant_type": "refresh_token", "refresh_token": tokens["access_token"]},
    )
    assert refused.status_code == 400
    assert "access token" in refused.json()["error"]["message"]


# ─── Shapes the rest of the corpus requires ──────────────────────────────────


def test_health_reports_what_this_service_depends_on(client: TestClient) -> None:
    """`S6.23`/`S2.48`. Stage 0 depends on a signing key and nothing else."""
    body = client.get("/health")
    assert body.status_code == 200
    assert body.json()["status"] == "healthy"
    assert body.json()["signing_key"] == "loaded"


def test_every_application_route_carries_the_version_prefix(service: IdentityService) -> None:
    """`S6.22`. The two exceptions are fixed by specification, not by preference.

    `/.well-known/*` is placed at the root by RFC 8615 and a conforming client
    looks nowhere else; `/health` is placed by `S6.23` itself.
    """
    # Read from the OpenAPI document rather than `app.routes`: FastAPI wraps an
    # included router in a single object with no `.path`, so walking `app.routes`
    # inspects nothing and passes for the wrong reason. The OpenAPI paths are
    # also what a client actually sees, which is what the standard is about.
    app = create_app(service)
    paths = set(app.openapi()["paths"])
    application = {p for p in paths if not p.startswith(("/.well-known", "/health"))}

    assert application, "this test is meaningless if it inspects nothing"
    assert all(p.startswith(API_PREFIX) for p in application), sorted(application)
    assert f"{API_PREFIX}/oauth/token" in application


def test_an_oauth_error_carries_both_envelopes(client: TestClient) -> None:
    """`S2.19`/`S2.22` shape, plus the RFC 6749 §5.2 field an OAuth client reads."""
    refused = client.post(f"{API_PREFIX}/oauth/token", json={"grant_type": "password"})
    body = refused.json()
    assert body["success"] is False
    assert body["error"]["code"] == "unsupported_grant_type"
    assert body["error_description"]


def test_an_unsupported_grant_type_is_refused(client: TestClient) -> None:
    refused = client.post(f"{API_PREFIX}/oauth/token", json={"grant_type": "client_credentials"})
    assert refused.status_code == 400


def test_a_token_request_missing_its_code_is_refused(client: TestClient) -> None:
    refused = client.post(f"{API_PREFIX}/oauth/token", json={"grant_type": DEVICE_CODE_GRANT})
    assert refused.json()["error"]["code"] == "invalid_request"


def test_whoami_without_a_token_is_refused_in_words(client: TestClient) -> None:
    refused = client.get(f"{API_PREFIX}/me")
    assert refused.status_code == 401
    assert "Traceback" not in refused.text


def test_expired_grants_are_purged_rather_than_accumulating() -> None:
    store = DeviceGrantStore()
    now = dt.datetime.now(dt.UTC)
    for _ in range(5):
        store.start(now)
    assert len(store) == 5
    assert store.purge_expired(now + dt.timedelta(hours=1)) == 5
    assert len(store) == 0
