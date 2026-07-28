"""Outbound-URL validation, shared by every surface that makes an HTTP request.

Both network surfaces — the semantic tier and the chat notifier — take a URL from
operator configuration and hand it to `urllib.request.urlopen`. urlopen honours
every scheme it knows, so an unvalidated value is a general-purpose file reader
(`file:///etc/passwd`) and, in the notifier's case, a way to make Governova issue
requests from inside a CI network to somewhere the operator never intended.

Neither is a remote-attacker capability today: both values arrive from
environment variables the operator sets. But a config value typo'd, templated
from a variable, or inherited from a shared org-level secret is exactly how these
become real, and refusing a scheme costs one comparison. The check lives here
rather than in each caller so a third network surface cannot forget it.
"""

from __future__ import annotations

from urllib.parse import urlsplit

ALLOWED_SCHEMES = frozenset({"http", "https"})


def require_http_url(url: str, *, what: str = "URL") -> str:
    """Return `url` if it is a plain http/https URL, else raise ValueError.

    The error names the scheme but never the URL: these values routinely carry
    inline credentials or a secret path segment, and error text lands in CI logs.
    """
    try:
        parts = urlsplit(url)
    except ValueError as exc:
        raise ValueError(f"{what} is not a parsable URL") from exc

    if parts.scheme.lower() not in ALLOWED_SCHEMES:
        raise ValueError(
            f"{what} must use http or https — refusing scheme "
            f"{parts.scheme.lower() or '(none)'!r}"
        )
    if not parts.netloc:
        raise ValueError(f"{what} has no host")
    return url
