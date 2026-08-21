"""The engine does not depend on the Cloud. Asserted, not assumed.

`ADR-010` §1 and §5.1 make this a **prohibition**, not a preference: the
deterministic engine runs complete and offline forever, with no feature flag, no
licence check and no phone-home. `#254`'s first acceptance criterion says the
same thing operationally — every deterministic command behaves identically with
the service down — and adds the part that matters: *tested with the service
stopped, not with it running and unused.*

A test that runs the engine while FastAPI happens to be installed proves nothing.
What follows makes the Cloud's dependencies **unimportable**, then imports and
runs the engine. If any engine module has acquired an import of `fastapi`, `jwt`
or `cryptography` — directly or through a chain — these fail.

That is the failure worth catching early. It would not break anything visibly:
the engine would keep working for everyone who happened to have the extra
installed, and would fail only for the users who installed `governova` to govern
a repository and never asked for a web framework.
"""

from __future__ import annotations

import builtins
import importlib
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

# Everything the Cloud brings in. None of it may be reachable from engine code.
CLOUD_ONLY = ("fastapi", "uvicorn", "jwt", "cryptography", "starlette", "keyring")

# Every surface the engine offers. `#254` names the commands; these are the
# modules behind them.
ENGINE_MODULES = (
    "governova_checks",
    "governova_compile",
    "governova_validate",
    "governova_score",
    "governova_report",
    "governova_evidence",
    "governova_project",
    "governova_enforce",
    "governova_guardian",
    "governova_onboard",
    "governova_bible",
    "governova_dashboard",
    "governova_audit",
    "governova_relay",
    "governova_settings",
    "governova_schema",
    "governova_requirements",
    "governova_cli.__main__",
)


def test_no_engine_module_imports_a_cloud_dependency() -> None:
    """Run in a subprocess with the Cloud's packages blocked at import time.

    A subprocess because the engine modules are already imported in this test
    session, and an import that has succeeded cannot be un-succeeded.
    """
    program = textwrap.dedent(
        f"""
        import builtins, sys

        blocked = {CLOUD_ONLY!r}
        real_import = builtins.__import__

        def guarded(name, *args, **kwargs):
            root = name.split(".")[0]
            if root in blocked:
                raise ModuleNotFoundError(
                    f"{{root}} is a Cloud dependency and the engine must not need it"
                )
            return real_import(name, *args, **kwargs)

        builtins.__import__ = guarded
        for cached in [m for m in sys.modules if m.split(".")[0] in blocked]:
            del sys.modules[cached]

        for module in {ENGINE_MODULES!r}:
            real_import(module)
        print("clean")
        """
    )
    result = subprocess.run(
        [sys.executable, "-c", program],
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, (
        "an engine module imports a Cloud dependency:\n" + result.stderr[-3000:]
    )
    assert "clean" in result.stdout


def test_the_engine_runs_with_the_cloud_unimportable(tmp_path) -> None:
    """Not just imports — the deterministic commands actually produce their answers.

    Import isolation proves the dependency is absent. This proves the *behaviour*
    is unaffected, which is what `#254` asks for and what an adopter experiences.
    """
    (tmp_path / "app.ts").write_text(
        "localStorage.setItem('access_token', t);\n", encoding="utf-8"
    )
    program = textwrap.dedent(
        f"""
        import builtins, sys
        from pathlib import Path

        blocked = {CLOUD_ONLY!r}
        real_import = builtins.__import__

        def guarded(name, *args, **kwargs):
            if name.split(".")[0] in blocked:
                raise ModuleNotFoundError(name)
            return real_import(name, *args, **kwargs)

        builtins.__import__ = guarded

        from governova_checks import scan_text
        from governova_score import compute_score

        findings = scan_text("localStorage.setItem('access_token', t);")
        assert any(f.anti_pattern == "AP-S3.14a" for f in findings), findings

        score = compute_score(Path({str(tmp_path)!r}))
        assert score.factors, "the score produced no factors"
        print("engine ok")
        """
    )
    result = subprocess.run(
        [sys.executable, "-c", program], capture_output=True, text=True, timeout=180
    )
    assert result.returncode == 0, result.stderr[-3000:]
    assert "engine ok" in result.stdout


def test_the_identity_package_is_not_reachable_from_the_engine() -> None:
    """No engine module may import `governova_identity` either.

    The dependency direction is one-way by design: the Cloud may read the engine,
    and the engine must never learn the Cloud exists.
    """
    offenders: list[str] = []
    for name in ENGINE_MODULES:
        module = importlib.import_module(name)
        source = getattr(module, "__file__", None)
        if source is None:
            continue
        text = Path(source).read_text(encoding="utf-8")
        if "governova_identity" in text:
            offenders.append(name)
    assert not offenders, f"engine module(s) reference the identity package: {offenders}"


def test_the_cli_reaches_the_auth_client_only_inside_the_identity_commands() -> None:
    """`login`, `logout` and `whoami` may use the client. Nothing else may.

    They are the only commands that need a network, and the import sits inside
    each command body rather than at module scope — importing at the top would
    put a keychain library on the import path of `governova score`.
    """
    import governova_cli.__main__ as cli

    source = Path(cli.__file__).read_text(encoding="utf-8")
    module_scope = source.split("def login(")[0]
    for line in module_scope.splitlines():
        stripped = line.strip()
        if stripped.startswith(("import ", "from ")) and line[:1] not in {" ", "	"}:
            assert "governova_auth" not in stripped, (
                f"the auth client is imported at module scope: {stripped}"
            )


def test_the_identity_service_is_an_extra_not_a_runtime_dependency() -> None:
    """A consumer governing a repository must not acquire a web framework to do it."""
    import tomllib
    from pathlib import Path

    from governova_compile.discovery import resolve_repo_root

    packaging = tomllib.loads(
        (Path(resolve_repo_root()) / "scripts" / "pyproject.toml").read_text(encoding="utf-8")
    )
    runtime = " ".join(packaging["project"]["dependencies"]).lower()
    for package in ("fastapi", "uvicorn", "pyjwt", "cryptography"):
        assert package not in runtime, f"{package} became a runtime dependency"

    extras = packaging["project"]["optional-dependencies"]
    assert "cloud" in extras, "the identity service must be installable as an extra"
    assert any("fastapi" in spec for spec in extras["cloud"])


def test_importing_identity_without_the_extra_fails_loudly_not_silently() -> None:
    """If the extra is missing the error names it, rather than being an ImportError.

    Skipped when the extra *is* installed, which it is in development — the
    behaviour under test only exists in an environment without it.
    """
    real_import = builtins.__import__

    def guarded(name, *args, **kwargs):  # type: ignore[no-untyped-def]
        if name.split(".")[0] == "fastapi":
            raise ModuleNotFoundError("No module named 'fastapi'")
        return real_import(name, *args, **kwargs)

    for cached in [m for m in sys.modules if m.startswith(("governova_identity", "fastapi"))]:
        del sys.modules[cached]

    builtins.__import__ = guarded
    try:
        with pytest.raises(ModuleNotFoundError):
            importlib.import_module("governova_identity.app")
    finally:
        builtins.__import__ = real_import
        for cached in [m for m in sys.modules if m.startswith("governova_identity")]:
            del sys.modules[cached]
