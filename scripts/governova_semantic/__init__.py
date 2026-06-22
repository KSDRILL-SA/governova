"""governova_semantic — the advisory semantic tier above the reliable rules.

Provider-agnostic (env-configured), advisory-only, and index-grounded. Inactive
unless an endpoint, key, and model are configured — so nothing depends on it being
available. It augments the deterministic rules; it never blocks and never changes them.
"""

from __future__ import annotations

from governova_semantic.config import SemanticConfig, from_env
from governova_semantic.review import (
    SemanticFinding,
    build_messages,
    parse_findings,
    relevant_standards,
    review,
)

__all__ = [
    "SemanticConfig",
    "SemanticFinding",
    "build_messages",
    "from_env",
    "parse_findings",
    "relevant_standards",
    "review",
]
