"""RS256 token issuance and verification — the only issuer.

`S3.5` and `S3.13` require RS256 rather than HS256, and the reason is the whole
architecture: with an asymmetric key the **public** half is published, so every
surface that needs to verify a token can do so without holding anything that
could mint one. A shared HMAC secret makes every verifier a potential issuer,
and there is no way to walk that back once it is distributed.

Two rules shape everything below.

**There is no default key.** The service refuses to start without one rather
than generating an ephemeral pair and carrying on. A generated default works
perfectly in development and silently issues tokens nobody can verify after a
restart — the "default that lies" failure `ADR-008` was written about, which
converts an absent capability into a believed one. The development path exists,
but it is explicit and it says what it is.

**Revocation is checked on every verification.** `#254` requires a revoked token
to stop working within one refresh window and to fail in a sentence rather than a
stack trace, so `verify` returns a typed reason rather than raising.
"""

from __future__ import annotations

import base64
import dataclasses
import datetime as dt
import secrets
import uuid
from enum import StrEnum
from pathlib import Path
from typing import Any

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

ALGORITHM = "RS256"
ISSUER = "https://identity.governova.dev"

# Short, because revocation of an access token cannot be instant without a lookup
# on every request, and a lookup on every request is the thing a stateless token
# exists to avoid. Fifteen minutes is the window `#254`'s second acceptance
# criterion is measured against.
ACCESS_TOKEN_TTL = dt.timedelta(minutes=15)
REFRESH_TOKEN_TTL = dt.timedelta(days=30)


class TokenError(StrEnum):
    """Why a token was not accepted. A reason, never an exception at the edge."""

    EXPIRED = "expired"
    REVOKED = "revoked"
    MALFORMED = "malformed"
    WRONG_ISSUER = "wrong_issuer"
    WRONG_AUDIENCE = "wrong_audience"

    @property
    def sentence(self) -> str:
        """What a person is told. `#254` asks for a sentence, not a stack trace."""
        return {
            TokenError.EXPIRED: "your session has expired — run `governova login` again",
            TokenError.REVOKED: "this session was revoked — run `governova login` again",
            TokenError.MALFORMED: "this credential is not a readable token",
            TokenError.WRONG_ISSUER: "this token was issued by a different service",
            TokenError.WRONG_AUDIENCE: "this token was not issued for this service",
        }[self]


@dataclasses.dataclass(frozen=True)
class Claims:
    """A verified token's contents."""

    subject: str
    token_id: str
    kind: str
    issued_at: dt.datetime
    expires_at: dt.datetime
    scopes: tuple[str, ...] = ()


@dataclasses.dataclass(frozen=True)
class VerifiedToken:
    """The outcome of verification: claims, or a reason there are none."""

    claims: Claims | None
    error: TokenError | None = None

    @property
    def ok(self) -> bool:
        return self.claims is not None


class SigningKey:
    """One RSA key pair, and the JWKS document derived from its public half."""

    def __init__(self, private_pem: bytes, *, key_id: str | None = None) -> None:
        loaded = serialization.load_pem_private_key(private_pem, password=None)
        if not isinstance(loaded, rsa.RSAPrivateKey):
            raise ValueError(
                "the identity signing key must be RSA — RS256 is required by S3.5, "
                "and an EC or Ed25519 key cannot produce an RS256 signature"
            )
        if loaded.key_size < 2048:
            raise ValueError(
                f"the identity signing key is {loaded.key_size} bits; RSA below 2048 "
                "is not acceptable for a token anyone relies on"
            )
        self._private = loaded
        self._private_pem = private_pem
        self.key_id = key_id or _thumbprint(loaded.public_key())

    @classmethod
    def generate(cls, *, key_id: str | None = None) -> SigningKey:
        """A fresh pair. For tests and the explicit development path only.

        Never reached by an accident of configuration: nothing calls this to fill
        in a missing key. See `load_signing_key`.
        """
        private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        pem = private.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        return cls(pem, key_id=key_id)

    @property
    def public_pem(self) -> bytes:
        return self._private.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

    def jwks(self) -> dict[str, Any]:
        """The public half, in the shape a verifier fetches.

        Only ever the public numbers. A test asserts no private component and no
        PEM header appears anywhere in this document — the failure it guards
        against would publish the signing key to the internet, and it would look
        exactly like a working service.
        """
        numbers = self._private.public_key().public_numbers()
        return {
            "keys": [
                {
                    "kty": "RSA",
                    "use": "sig",
                    "alg": ALGORITHM,
                    "kid": self.key_id,
                    "n": _b64u(numbers.n),
                    "e": _b64u(numbers.e),
                }
            ]
        }

    def issue(
        self,
        subject: str,
        *,
        kind: str = "access",
        audience: str,
        scopes: tuple[str, ...] = (),
        ttl: dt.timedelta | None = None,
        now: dt.datetime | None = None,
    ) -> tuple[str, Claims]:
        """Sign a token and return it beside the claims it carries."""
        moment = now or dt.datetime.now(dt.UTC)
        lifetime = ttl or (ACCESS_TOKEN_TTL if kind == "access" else REFRESH_TOKEN_TTL)
        expires = moment + lifetime
        token_id = str(uuid.uuid4())
        payload: dict[str, Any] = {
            "iss": ISSUER,
            "sub": subject,
            "aud": audience,
            "iat": int(moment.timestamp()),
            "exp": int(expires.timestamp()),
            "jti": token_id,
            "typ": kind,
            "scope": " ".join(scopes),
        }
        encoded = jwt.encode(
            payload, self._private_pem, algorithm=ALGORITHM, headers={"kid": self.key_id}
        )
        return encoded, Claims(
            subject=subject,
            token_id=token_id,
            kind=kind,
            issued_at=moment,
            expires_at=expires,
            scopes=scopes,
        )

    def verify(
        self,
        token: str,
        *,
        audience: str,
        revoked: set[str] | None = None,
    ) -> VerifiedToken:
        """Check a token. Returns a reason rather than raising.

        `algorithms` is pinned to RS256 explicitly. Accepting whatever the header
        declares is the algorithm-confusion vulnerability: a token whose header
        says `none`, or one signed with HMAC using the *public* key as the
        secret, would otherwise verify.
        """
        try:
            payload = jwt.decode(
                token,
                self.public_pem,
                algorithms=[ALGORITHM],
                audience=audience,
                issuer=ISSUER,
            )
        except jwt.ExpiredSignatureError:
            return VerifiedToken(None, TokenError.EXPIRED)
        except jwt.InvalidAudienceError:
            return VerifiedToken(None, TokenError.WRONG_AUDIENCE)
        except jwt.InvalidIssuerError:
            return VerifiedToken(None, TokenError.WRONG_ISSUER)
        except jwt.InvalidTokenError:
            return VerifiedToken(None, TokenError.MALFORMED)

        token_id = str(payload.get("jti", ""))
        if revoked and token_id in revoked:
            return VerifiedToken(None, TokenError.REVOKED)

        scope = str(payload.get("scope", "")).split()
        return VerifiedToken(
            Claims(
                subject=str(payload["sub"]),
                token_id=token_id,
                kind=str(payload.get("typ", "access")),
                issued_at=dt.datetime.fromtimestamp(payload["iat"], dt.UTC),
                expires_at=dt.datetime.fromtimestamp(payload["exp"], dt.UTC),
                scopes=tuple(scope),
            )
        )


def _b64u(value: int) -> str:
    raw = value.to_bytes((value.bit_length() + 7) // 8, "big")
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _thumbprint(public_key: rsa.RSAPublicKey) -> str:
    """A stable id for a key, derived from the key itself.

    Derived rather than random so that restarting the service with the same key
    keeps the same `kid`, and a cached JWKS stays valid.
    """
    numbers = public_key.public_numbers()
    material = f"{numbers.n}:{numbers.e}".encode()
    import hashlib

    return hashlib.sha256(material).hexdigest()[:16]


ENV_PRIVATE_KEY = "GOVERNOVA_IDENTITY_PRIVATE_KEY"
ENV_PRIVATE_KEY_FILE = "GOVERNOVA_IDENTITY_PRIVATE_KEY_FILE"


class MissingSigningKeyError(RuntimeError):
    """Raised at startup when no key is configured. Never fallen back from."""


def load_signing_key(env: dict[str, str]) -> SigningKey:
    """The configured key, or a refusal to start.

    **No key means no service.** Generating one here would work, and would issue
    tokens that stop verifying the next time the process restarts — a fleet of
    instances would each mint tokens the others reject, and the symptom is
    intermittent logouts that look like a client bug.
    """
    inline = env.get(ENV_PRIVATE_KEY, "").strip()
    if inline:
        return SigningKey(inline.encode("utf-8"))

    path = env.get(ENV_PRIVATE_KEY_FILE, "").strip()
    if path:
        pem = Path(path).expanduser()
        if not pem.is_file():
            raise MissingSigningKeyError(
                f"{ENV_PRIVATE_KEY_FILE} points at {pem}, which is not a readable file"
            )
        return SigningKey(pem.read_bytes())

    raise MissingSigningKeyError(
        f"No signing key. Set {ENV_PRIVATE_KEY} to a PEM, or "
        f"{ENV_PRIVATE_KEY_FILE} to a path. The service will not generate one: a "
        "generated key issues tokens that stop verifying on restart, and every "
        "instance in a fleet would reject the others' tokens."
    )


def new_opaque_secret(length: int = 32) -> str:
    """A high-entropy, URL-safe secret for a device code or an API key."""
    return secrets.token_urlsafe(length)
