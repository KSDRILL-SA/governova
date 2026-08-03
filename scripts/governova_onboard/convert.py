"""governova_onboard.convert — proposed changes, never applied changes.

Scan, Learn & Rewrite. This is the stage that can break a working system, so
almost all of it is refusal machinery and only a little of it is transformation.

## The two guarantees, mechanised rather than restated

**`S1.101` — characterisation tests pin behaviour before a refactor.** A code
conversion whose files carry no conventionally-named test is *refused*, with the
reason, and no flag overrides it. Rewriting untested legacy code is the single
fastest way to break a working system and end an adoption, and a `--force` that
skips the check would make the guarantee decorative.

**`S6.45` / `S8.83` — incremental, non-breaking, individually reversible.** One
conversion is one file and one change. Each carries the exact text it replaced,
so reverting is not a re-derivation — it is writing back a string this object is
holding. Applying re-reads the file first and refuses if it no longer matches
what was proposed, because a diff reviewed against content that has since moved
is not the diff being applied.

## Why the converter set is small, and the test it has to pass

**A converter must fix the thing, not the check.** That single rule rejected most
of the obvious candidates:

* *Create `governance/decisions/` with a template ADR* — makes the `S1.85` probe
  pass while documenting no decision. Gaming the metric.
* *Add the missing headings to a thin README* — makes `S1.84` pass while
  documenting nothing. Same failure.
* *Strip `console.log`* — removes output somebody may rely on. Not
  behaviour-preserving.
* *Money `float` → `Decimal`* — changes arithmetic semantics. Exactly the class
  the plan says not to start with.
* *Add the missing index the schema analyser flagged* — the plan names this, but
  the analyser reports normalisation and integrity defects (`no-primary-key`,
  `fan-trap`, `dangling-foreign-key`) and **has no missing-index finding**. There
  is nothing to convert from. Recorded rather than invented.

What survives is deliberately narrow, and `register_converter` is the extension
point so a house-specific conversion is an addition rather than an edit — the
same line `AP-S1.107a` draws for readers and rules.
"""

from __future__ import annotations

import difflib
import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from governova_evidence import Verdict

from governova_onboard.baseline import Baseline
from governova_onboard.roadmap import Kind, Protection, find_characterisation_tests


@dataclass(frozen=True)
class Conversion:
    """One proposed change to one file. Never applied on construction."""

    converter: str
    standard: str
    path: str
    """Repository-relative, so the diff reads the same wherever it was produced."""
    before: str
    after: str
    rationale: str
    kind: Kind
    protection: Protection
    protected_by: tuple[str, ...] = ()

    @property
    def diff(self) -> str:
        """A unified diff — the reviewable artefact `S6.45` asks for."""
        return "".join(
            difflib.unified_diff(
                self.before.splitlines(keepends=True),
                self.after.splitlines(keepends=True),
                fromfile=f"a/{self.path}",
                tofile=f"b/{self.path}",
                n=3,
            )
        )

    @property
    def refusal(self) -> str:
        """Why this must not be applied, or an empty string when it may be.

        Structural changes touch configuration and alter no runtime behaviour,
        so there is no behaviour to pin first — demanding a characterisation
        test before adding a line to `.gitignore` would be `S1.101` applied
        where it has no subject.
        """
        if self.kind is Kind.CODE and self.protection is Protection.UNKNOWN:
            return (
                f"S1.101 — no characterisation test found for {self.path}. "
                f"Behaviour must be pinned before it is refactored. Write one, or "
                f"apply this by hand having read it."
            )
        if self.before == self.after:
            return "the conversion produced no change"
        return ""

    @property
    def applicable(self) -> bool:
        return not self.refusal


class ConversionRefusedError(RuntimeError):
    """Raised when applying a conversion the safety rules forbid.

    There is no override. A guarantee with a bypass flag is a suggestion, and
    `S1.101` is not a suggestion.
    """


class ConversionStaleError(RuntimeError):
    """Raised when the file on disk no longer matches what was proposed.

    A diff reviewed against content that has since changed is not the diff being
    applied, and applying it anyway would silently discard whatever moved.
    """


def apply(root: Path, conversion: Conversion) -> Path:
    """Write one conversion. Refuses unsafe and refuses stale.

    Returns the path written. The caller keeps the `Conversion`, which holds the
    exact text replaced — that is the revert path (`S8.83`), and it needs no
    re-derivation.
    """
    if conversion.refusal:
        raise ConversionRefusedError(conversion.refusal)
    target = root / conversion.path
    current = target.read_text(encoding="utf-8") if target.exists() else ""
    if current != conversion.before:
        raise ConversionStaleError(
            f"{conversion.path} has changed since this was proposed — re-run to "
            f"regenerate the diff rather than applying one reviewed against different content."
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(conversion.after, encoding="utf-8")
    return target


def revert(root: Path, conversion: Conversion) -> Path:
    """Put back exactly what was there (`S8.83`). The inverse of `apply`."""
    target = root / conversion.path
    current = target.read_text(encoding="utf-8") if target.exists() else ""
    if current != conversion.after:
        raise ConversionStaleError(
            f"{conversion.path} is not in the state this conversion produced — "
            f"reverting would discard a later change."
        )
    target.write_text(conversion.before, encoding="utf-8")
    return target


# ── Converters ───────────────────────────────────────────────────────────────

Converter = Callable[[Path, Baseline], list[Conversion]]
_REGISTRY: dict[str, Converter] = {}


def register_converter(name: str, converter: Converter) -> None:
    """Add a conversion without editing this module (`AP-S1.107a`)."""
    _REGISTRY[name] = converter


def registered_converters() -> tuple[str, ...]:
    return tuple(sorted(_REGISTRY))


def _gitignore_env(root: Path, baseline: Baseline) -> list[Conversion]:
    """`S8.25` — ensure `.env` is gitignored.

    Additive, alters no runtime behaviour, and it makes the standard's property
    genuinely true rather than merely making the probe pass: after this, `.env`
    really is ignored. That is the whole test a converter has to meet.
    """
    violated = {p.standard for p in baseline.probes if p.verdict is Verdict.VIOLATED}
    if "S8.25" not in violated:
        return []

    path = root / ".gitignore"
    before = path.read_text(encoding="utf-8") if path.is_file() else ""
    # Matches the probe's own test exactly, so the converter cannot claim to fix
    # something the probe would still report — or fire on something it would not.
    if re.search(r"^\s*\.env\b", before, re.M):
        return []

    # Normalise trailing blank lines rather than appending to whatever is there:
    # a file ending in one newline and a file ending in three both need the same
    # result, and a diff carrying stray blank lines invites the reviewer to
    # wonder what else the tool did to their file.
    body = before.rstrip("\n")
    prefix = f"{body}\n\n" if body else ""
    after = f"{prefix}# Local environment values — never committed (S8.25).\n.env\n"
    return [
        Conversion(
            converter="gitignore-env",
            standard="S8.25",
            path=".gitignore",
            before=before,
            after=after,
            rationale="`.env` is not gitignored, so a local secrets file can be committed.",
            kind=Kind.STRUCTURAL,
            protection=Protection.PROTECTED,
        )
    ]


# `NAME = "https://..."` where NAME already reads as a URL setting. The rule this
# serves (`AP-S1.105a`) matches the same shape; anchoring on the assignment means
# the conversion cannot touch a literal the rule would not have flagged.
_PY_URL_ASSIGNMENT = re.compile(
    r"^(?P<indent>[ \t]{0,32})(?P<name>[A-Za-z_][A-Za-z0-9_]{0,64})"
    # `[ \t]` rather than `\s` on both sides: `\s` matches newlines, so `\s*$`
    # ran past the end of the line and swallowed the blank line after it. The
    # conversion then deleted whitespace it had no business touching, which makes
    # the diff larger than the change and gives a reviewer something extra to
    # explain. Every quantifier stays bounded.
    r"(?P<gap>[ \t]{0,8}=[ \t]{0,8})"
    r"(?P<quote>['\"])(?P<value>https?://[^'\"\n]{1,300})(?P=quote)[ \t]*$",
    re.M,
)

_URLISH = re.compile(r"base_?url|api_?url|endpoint|webhook_?url|host_?name|service_?url", re.I)


def _env_sourced_urls(root: Path, baseline: Baseline) -> list[Conversion]:
    """`S1.105` — read an inlined environment URL from configuration instead.

    `NAME = "https://…"` becomes `NAME = os.environ.get("NAME", "https://…")`.

    **Behaviour-preserving by construction**: the literal survives as the
    default, so an unset variable produces exactly the previous value. The
    obvious alternative — `os.environ["NAME"]` — raises on a machine that has
    not set it, which is a working system broken by a governance tool.

    **It refuses a file that does not already import `os`.** Inserting an import
    means deciding where it goes, whether the name is shadowed, and whether the
    module is a package `__init__` with re-export ordering that matters. Every
    one of those is a guess, and the conversion is worth nothing if it is not
    provably safe.
    """
    conversions: list[Conversion] = []
    targets = sorted(
        {f for g in baseline.groups if g.anti_pattern == "AP-S1.105a" for f in g.files}
    )
    for relative in targets:
        if not relative.endswith(".py"):
            continue
        path = root / relative
        try:
            before = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if not re.search(r"^\s{0,32}import\s+os\b", before, re.M):
            continue

        def substitute(match: re.Match[str]) -> str:
            name = match.group("name")
            if not _URLISH.search(name):
                return match.group(0)
            quote, value = match.group("quote"), match.group("value")
            return (
                f"{match.group('indent')}{name}{match.group('gap')}"
                f"os.environ.get({quote}{name}{quote}, {quote}{value}{quote})"
            )

        after = _PY_URL_ASSIGNMENT.sub(substitute, before)
        if after == before:
            continue

        tests = find_characterisation_tests(root, (relative,))
        conversions.append(
            Conversion(
                converter="env-sourced-urls",
                standard="S1.105",
                path=relative,
                before=before,
                after=after,
                rationale=(
                    "An environment-specific URL is inlined as a literal. Reading it "
                    "from the environment with the current value as the default keeps "
                    "behaviour identical while making it configurable."
                ),
                kind=Kind.CODE,
                protection=Protection.PROTECTED if tests else Protection.UNKNOWN,
                protected_by=tests,
            )
        )
    return conversions


register_converter("gitignore-env", _gitignore_env)
register_converter("env-sourced-urls", _env_sourced_urls)


def propose_conversions(
    root: Path, baseline: Baseline, *, only: str | None = None
) -> list[Conversion]:
    """Every conversion the registered converters offer. Writes nothing.

    Named `propose_conversions` rather than `propose` because
    `governova_onboard.propose` is a module in this package: importing it binds
    that name on the package and would silently shadow a function of the same
    name re-exported from `__init__`. That exact collision has already cost this
    package one debugging session.
    """
    names = [only] if only else list(registered_converters())
    conversions: list[Conversion] = []
    for name in names:
        converter = _REGISTRY.get(name)
        if converter is None:
            raise KeyError(f"no converter named {name!r} — registered: {registered_converters()}")
        conversions.extend(converter(root, baseline))
    return conversions


__all__ = [
    "Conversion",
    "ConversionRefusedError",
    "ConversionStaleError",
    "Converter",
    "apply",
    "propose_conversions",
    "register_converter",
    "registered_converters",
    "revert",
]
