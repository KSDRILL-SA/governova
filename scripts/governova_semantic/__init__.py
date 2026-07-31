"""governova_semantic — the advisory semantic tier above the reliable rules.

Provider-agnostic (env-configured), advisory-only, and index-grounded. Inactive
unless an endpoint, key, and model are configured — so nothing depends on it being
available. It augments the deterministic rules; it never blocks and never changes them.
"""

from __future__ import annotations

from governova_semantic.client import SemanticUnavailableError
from governova_semantic.config import SemanticConfig, from_env
from governova_semantic.describe import describe_code
from governova_semantic.review import (
    Outcome,
    ReviewResult,
    SemanticFinding,
    build_messages,
    parse_findings,
    relevant_standards,
    review,
    review_result,
)

__all__ = [
    "Outcome",
    "ReviewResult",
    "SemanticConfig",
    "SemanticFinding",
    "SemanticUnavailableError",
    "build_messages",
    "describe_code",
    "from_env",
    "parse_findings",
    "relevant_standards",
    "review",
    "review_result",
]
