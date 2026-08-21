"""governova_identity — the identity service. Stage 0 of Workstream D.

The only issuer. `ADR-010` fixes the boundary this sits on: the deterministic
engine stays MIT, complete and **offline forever**, and nothing in this package
is imported by it. That is not a convention — it is asserted by a test that
imports every engine surface with this package's dependencies made unimportable.

Installed as an extra (`governova[cloud]`), so a consumer who only governs a
repository never pulls FastAPI, uvicorn or a JWT library into their environment.
"""

from __future__ import annotations

__all__ = ["__doc__"]
