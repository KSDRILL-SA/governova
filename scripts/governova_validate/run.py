"""The validation run, in one place.

There were two of these. `governova validate` had its own copy of the sequence and
`governova-validate` had another: checksum, the `ALL_CHECKS` loop, the source-tree
checks, links, the error/warning split. They shared the check *functions* but not
the wiring that calls them, so adding a check to one did nothing to the other and
nothing said so — no test, no type error, no lint.

That is the worst shape a gap can take. #218 added `check_declared_anti_patterns`,
wired it into one entry point, and the other went on printing `warnings=350` — which
is indistinguishable from a check that ran and found nothing. It cost a debugging
round, and only because the expected number was known in advance.

Both entry points now call `run_validation` and differ only in how they render it.
A new check is wired once, by construction.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from governova_compile.schema import CompiledIndex, IntegrityIssue, Severity
from governova_compile.writer import verify_checksum

from governova_validate.checks import ALL_CHECKS
from governova_validate.declared import check_declared_anti_patterns
from governova_validate.links import check_links

# SEV0–SEV2 fail the run outright; SEV3 fails only under --strict.
ERROR_SEVERITIES = frozenset({Severity.SEV0, Severity.SEV1, Severity.SEV2})


@dataclass(frozen=True)
class ValidationRun:
    """Everything both entry points need, so neither has to recompute it."""

    issues: tuple[IntegrityIssue, ...]
    links_checked: int

    @property
    def errors(self) -> list[IntegrityIssue]:
        return [i for i in self.issues if i.severity in ERROR_SEVERITIES]

    @property
    def warnings(self) -> list[IntegrityIssue]:
        return [i for i in self.issues if i.severity == Severity.SEV3]

    def failed(self, *, strict: bool) -> bool:
        return bool(self.errors) or (strict and bool(self.warnings))


def run_validation(
    root: Path,
    index: CompiledIndex,
    *,
    index_path: str = "compiled/constitution.json",
    skip_links: bool = False,
) -> ValidationRun:
    """Run every integrity check over `index` and the source tree beneath `root`."""
    issues: list[IntegrityIssue] = []

    if not verify_checksum(index):
        issues.append(
            IntegrityIssue(
                severity=Severity.SEV1,
                code="checksum-mismatch",
                message=(
                    "Stored checksum does not match the index body. "
                    "The index may have been edited by hand — re-run `governova compile`."
                ),
                source_path=index_path,
            )
        )

    for check in ALL_CHECKS:
        issues.extend(check(index))

    # Needs the source tree, not only the index — it exists to catch the case where
    # the two disagree, which an index-only check cannot see by construction.
    issues.extend(check_declared_anti_patterns(root, index))

    links_checked = 0
    if not skip_links:
        link_issues, links_checked = check_links(root)
        issues.extend(link_issues)

    return ValidationRun(issues=tuple(issues), links_checked=links_checked)
