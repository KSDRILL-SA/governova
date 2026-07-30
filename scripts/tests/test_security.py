"""Security regression tests for the engine's attack surface.

Governova now installs into other people's CI and runs, as a blocking gate, over
their source. That changes the threat model: a hang is their pipeline stalled, an
argument injection is a write inside their runner, and an error string is
something many people can read. Each test here pins one finding from the review
so it cannot come back quietly.
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

import pytest
from governova_checks.gather import _validate_rev, changed_files
from governova_checks.net import require_http_url
from governova_checks.rules import MAX_LINE_LENGTH, RULES, scan_text

# Generous enough to absorb a slow CI runner, tight enough that quadratic
# backtracking cannot hide underneath it.
_BUDGET_SECONDS = 0.25


# ─── Catastrophic backtracking (ReDoS) ───────────────────────────────────────

ADVERSARIAL = {
    "long-nonmatch": "x" * 20_000,
    "balance-bomb": "balance" + "=" * 4_000,
    "dotted-words": ("a." * 3_000) + "balance = ",
    "underscored": ("ab_" * 2_000) + "balance",
    "money-prefix": "price " + "a" * 4_000,
    "url-prefix": 'baseUrl = "https://' + "a" * 5_000,
    "tenant-prefix": "req.query." + "a" * 5_000,
    "open-parens": "session.query(" + "(" * 3_000,
    "sql-fragment": "`SELECT " + "a " * 3_000,
    "wide-gap": "assertAlmostEqual" + " " * 5_000 + "(",
}


@pytest.mark.parametrize("rule", RULES, ids=lambda r: r.anti_pattern)
def test_no_rule_backtracks_catastrophically(rule) -> None:  # type: ignore[no-untyped-def]
    """Every rule must stay fast on hostile input.

    `AP-D-FINTECH.3a` once took 8.7 seconds on a single 20k-character line —
    an ordinary minified bundle. As a blocking gate in a consumer's CI that is
    a denial of service, so the budget is enforced per rule rather than trusted
    to review.
    """
    for name, payload in ADVERSARIAL.items():
        start = time.perf_counter()
        rule.pattern.search(payload)
        elapsed = time.perf_counter() - start
        assert elapsed < _BUDGET_SECONDS, (
            f"{rule.anti_pattern} took {elapsed:.3f}s on '{name}' — "
            f"likely catastrophic backtracking"
        )


def test_a_hostile_file_scans_quickly_end_to_end() -> None:
    hostile = "\n".join(list(ADVERSARIAL.values()) * 20)
    start = time.perf_counter()
    scan_text(hostile, file="src/a.ts")
    assert time.perf_counter() - start < 2.0


def test_absurdly_long_lines_are_skipped_not_scanned() -> None:
    """Defence in depth: cost scales with line length, so length is capped."""
    line = "x" * (MAX_LINE_LENGTH + 1)
    assert scan_text(f'const t = req.query.tenantId; // {line}', file="src/a.ts") == []


def test_a_normal_long_line_is_still_scanned() -> None:
    """The cap must sit far above anything a human writes."""
    padding = "x" * (MAX_LINE_LENGTH - 100)
    code = f"const tenantId = req.query.tenantId; // {padding}"
    assert any(f.anti_pattern == "AP-D-SAAS.1b" for f in scan_text(code, file="src/a.ts"))


# ─── Git argument injection ──────────────────────────────────────────────────


@pytest.mark.parametrize(
    "hostile",
    [
        "--output=/tmp/pwned",
        "--upload-pack=touch /tmp/pwned",
        "-o/tmp/pwned",
        "--exec=sh",
        "",
        "--",
    ],
)
def test_a_revision_git_could_read_as_an_option_is_refused(hostile: str) -> None:
    """`git diff --output=<path>` writes a file — proven to work before the fix.

    There is no shell here, so this was never shell injection; it was git's own
    option parsing being handed caller-controlled text.
    """
    with pytest.raises(ValueError, match="refusing to use"):
        _validate_rev(hostile)


@pytest.mark.parametrize(
    "legitimate",
    ["main", "origin/main", "HEAD~3", "v1.2.3", "a1b2c3d", "feature/thing", "HEAD^"],
)
def test_ordinary_revisions_are_accepted(legitimate: str) -> None:
    assert _validate_rev(legitimate) == legitimate


def test_changed_files_refuses_a_hostile_revision(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    target = tmp_path / "PWNED"
    with pytest.raises(ValueError):
        changed_files(f"--output={target}", tmp_path)
    assert not target.exists(), "git must never have been invoked at all"


def test_an_over_long_revision_is_refused() -> None:
    with pytest.raises(ValueError):
        _validate_rev("a" * 300)


# ─── Outbound URL validation ─────────────────────────────────────────────────


@pytest.mark.parametrize(
    "hostile",
    [
        "file:///etc/passwd",
        "file://C:/Windows/win.ini",
        "ftp://example.com/x",
        "gopher://example.com",
        "data:text/plain,hello",
        "/no/scheme",
        "https://",
    ],
)
def test_non_http_urls_are_refused(hostile: str) -> None:
    """urlopen honours every scheme it knows — including local file reads."""
    with pytest.raises(ValueError):
        require_http_url(hostile, what="test URL")


@pytest.mark.parametrize(
    "ok", ["http://localhost:8080/v1", "https://hooks.example.com/services/T/B/x"]
)
def test_http_and_https_are_allowed(ok: str) -> None:
    assert require_http_url(ok) == ok


def test_the_url_is_never_echoed_in_the_error() -> None:
    """These values routinely carry inline credentials, and errors reach CI logs."""
    secret = "file:///etc/passwd?token=SUPERSECRET"
    with pytest.raises(ValueError) as exc:
        require_http_url(secret, what="webhook")
    assert "SUPERSECRET" not in str(exc.value)
    assert "/etc/passwd" not in str(exc.value)


def test_the_notifier_refuses_a_non_http_webhook() -> None:
    from governova_notify import urllib_transport

    with pytest.raises(ValueError):
        urllib_transport("file:///etc/passwd", {"text": "x"}, 1.0)


def test_the_semantic_client_refuses_a_non_http_endpoint() -> None:
    """Every protocol, not only the default — a second transport must not be a gap."""
    from governova_semantic.client import default_transport
    from governova_semantic.config import PROTOCOLS, SemanticConfig

    for protocol in PROTOCOLS:
        cfg = SemanticConfig(model="m", base_url="file:///etc", api_key="k", protocol=protocol)
        with pytest.raises(ValueError):
            default_transport(cfg, [{"role": "user", "content": "x"}])


def test_evidence_outside_the_repository_is_not_evidence(tmp_path: Path) -> None:
    """A claim only means something if a reader of the repo can check it.

    Existence alone would accept an absolute path to anything on the machine —
    `/etc/hostname` exists and evidences nothing.
    """
    from governova_project import _evidence_resolves

    real = tmp_path / "docs" / "real.md"
    real.parent.mkdir()
    real.write_text("x", encoding="utf-8")
    assert _evidence_resolves(tmp_path, "docs/real.md")

    outside = tmp_path.parent / "outside.md"
    outside.write_text("x", encoding="utf-8")
    assert not _evidence_resolves(tmp_path, str(outside)), "absolute path accepted"
    assert not _evidence_resolves(tmp_path, "../outside.md"), "traversal accepted"


def test_a_transport_failure_does_not_leak_the_endpoint() -> None:
    """urllib echoes the request URL; an endpoint may embed credentials."""
    from governova_semantic.client import SemanticUnavailableError, default_transport
    from governova_semantic.config import PROTOCOLS, SemanticConfig

    for protocol in PROTOCOLS:
        cfg = SemanticConfig(
            model="m",
            base_url="http://user:SUPERSECRET@127.0.0.1:1/v1",
            api_key="k",
            timeout=0.2,
            protocol=protocol,
        )
        with pytest.raises(SemanticUnavailableError) as exc:
            default_transport(cfg, [{"role": "user", "content": "x"}])
        assert "SUPERSECRET" not in str(exc.value)
