# Changelog

All notable changes to the `governova` distribution are recorded here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project
follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**A merge never publishes.** A release is cut by pushing a `vX.Y.Z` tag; the tag must match
the version in `scripts/pyproject.toml`, and `.github/workflows/release.yml` re-runs every
gate that guards `main` against the exact commit being shipped before anything reaches PyPI.

Numbers in parentheses are pull requests in
[KSDRILL-SA/governova](https://github.com/KSDRILL-SA/governova).

---

## [Unreleased]

### Added

- **The release gate refuses to publish a version the changelog still calls
  `unreleased`.** The date is the one field that cannot be written truthfully in
  advance — preparation writes `unreleased` because at that moment it is, the tag
  goes out separately, and nobody goes back. It happened on both releases cut
  since this file existed: `0.2.1` was still marked `unreleased` a day after
  shipping, and `0.2.2` was dated only because someone went looking for the same
  mistake an hour after publishing. The check now runs in `verify`, before
  anything is built, and the tests exercise the script extracted from the
  workflow rather than a copy of it.

---

## [0.2.2] — 2026-08-23

**The first release shaped by a repository Governova did not write.** `0.2.1` was installed
from PyPI into a clean virtualenv and pointed at an external Next.js monorepo. The first
command failed for a reason that had nothing to do with the code it was reading, and neither
did the second.

Measured on that repository, same commit, before and after:

| | Findings | Blocking | Verdict |
|---|---|---|---|
| `0.2.1` | 388 | **201** | FAILED |
| `0.2.2` | 187 | **0** | passed |

The 187 that remain are advisories about the reader's own code.

### Fixed

- **The merge gate enforced a sector's law against projects that never adopted it.**
  `governova onboard` states that an undeclared Layer 4 domain's standards are not counted;
  `governova-enforce` then failed the build with **201 blocking findings, 199 of them
  `AP-D-FINTECH.1a`** — from the domain the proposed profile had just declined to declare.
  `applicable_standards` had filtered by declared domain since it was written and the scanner
  never did, so the assessment model and the merge gate answered to different bodies of law.
  The adopter genuinely is fintech, so the findings were true; they were true by luck. Core
  standards still bind every system, Layer 4 binds the sector that adopted it, and withheld
  findings are counted and named rather than dropped in silence. (#325, #332)

- **`--format json` could not be parsed.** The array arrived on stdout wrapped in a summary
  line and a verdict line, so `json.loads` raised at char 4 and every consumer failed on the
  first line. Human output now routes by channel: annotations for `github`, stderr for `json`,
  stdout for `text`. A clean run emits `[]` rather than nothing. (#326, #333)

- **The money rule blocked integer cents — the representation it prescribes.**
  `AP-D-FINTECH.1a` fired on `totalCents`, `collectionAmountCents` and
  `maximumCollectionAmountCents` in a payment submission path: money done exactly as
  `D-FINTECH.1` requires. A developer who read the finding, applied the standard's own remedy
  and re-ran got the same finding back. It also fired on counters — `totalPages`, `totalItems`,
  `totalPaidMonths`. (#327, #334)

- **`S2.18` flagged the two safe branches and missed the one it was written for.** A bare
  `return` in front of `err.message` was signal enough, so two `instanceof`-narrowed returns of
  a project-declared error type were reported while the `unknown` branch — the one that can
  carry a driver message or a stack — was not. `.stack` keeps the loose context; `.message` now
  requires a framework response sender. (#328, #335)

- **The board report could not show a Layer 4 finding at all.** Findings were tallied into
  `index.constitutions` while the index keeps `domains` in a separate list, so a sector finding
  was dropped whether or not the project declared it. The sector standards are the ones with a
  regulatory basis behind them, and the board report is the surface written for the audience
  least able to notice an omission. (#330, #339)

- **stderr could not carry the characters the engine prints.** `governova_console` configured
  stdout only. Once `--format json` routed its human output to stderr, the withheld-domain note
  printed a replacement glyph mid-sentence. (#336)

### Added

- **`governova enforce`** as a subcommand. Enforcement shipped only as its own console script,
  which is right for CI and is not what a person types — every document opened with
  `governova enforce .` and the answer was `No such command 'enforce'`. It delegates, so the
  options live in one place. (#329, #337)
- **`governova --version`**, read from package metadata rather than a constant. (#329, #337)
- **`--domain`** on the enforcer, to adopt a sector without committing a profile first. (#332)
- Live phase reporting during `governova onboard`. (#337)

### Changed

- **`governova onboard` runs in 40 seconds instead of 9m15s**, and produces a byte-identical
  report. The tree was enumerated in full and filtered afterwards by four separate copies of
  the same skip list — `root.rglob("*")` returning 104,536 entries where a pruned walk finds
  877. `walk_files` prunes during the walk and is now the only copy. `site-packages` joins the
  shared list, because an installed dependency tree is not always inside a `.venv`. (#331, #340)
- Two correctness findings fell out of that work: a language probe could answer "no TypeScript"
  about a TypeScript repository once its scan budget was spent inside `node_modules`, and the
  roadmap could offer a dependency's test file as the reader's own characterisation test. (#340)

---

## [0.2.1] — 2026-08-22

**A patch release, and the reason for it is worth stating plainly: `0.2.0` did not work
properly once installed.** Both defects were invisible from a source checkout and appeared the
moment the wheel was installed somewhere else — which is what every adopter does and what
nothing in CI did.

### Fixed

- **`governova enforce .` reported findings from your dependencies.** A directory argument was
  expanded without consulting `SKIP_DIRS`, so the walk reached into `.venv`, `node_modules` and
  `dist`. Measured on a fresh install of `0.2.0` into an empty project containing exactly one
  real violation: **51 blocking findings, 50 of them from inside `site-packages`.** Every one
  was true about the line it cited and none was the reader's code. The exclusions existed and
  were applied only on the branch of that function CI uses, because CI never passes a path.
  (#320, #321)

- **No installed user could ever be issued a Governova Score.** The constitutional coverage
  factor looked for `compiled/constitution.json` relative to the project being scored — a path
  that exists only inside a Governova checkout. `ADR-012` names that factor as the one that
  reaches quorum, so an installed Governova sat permanently at 30% assessed and withheld the
  headline number from everyone not running from source. Six surfaces bypassed the resolver
  that already answered this question; all six now use it, so `GOVERNOVA_CONSTITUTION` reaches
  every command rather than some of them. (#320, #321)

- **Test files named the way the constitution mandates were scanned as source.** `S1.69`
  requires co-located `{source}.test.ts` / `.spec.ts`, and those two conventions were missing
  from the ignore list while Python's and Go's were present — so a repository following
  Governova's own standard was reported against every rule its tests deliberately exercise.
  (#315, #316)

- **The score renderers published a headline below quorum.** `ADR-012` reached the CLI, the
  guardian and the dashboard, and left `to_badge`, `to_markdown`, `to_text` and `to_json`
  printing the arithmetic. The badge was the one that mattered: it goes in a public README and
  showed `0/100 (F)` for a repository nobody had measured. (#304)

- **A core installation reported its own licence boundary as a defect.** `validate_rules`
  returned the 46 rules citing anti-patterns outside the bundled corpus as rule-set drift,
  accusing a correctly built wheel of a bug. `ADR-013` decides the question and splits the two
  claims apart. (#305, #306)

### Added

- `ADR-013` — a rule fires for a defect, not for a licence. Records why rules stay active for
  law the operator has not licensed, on `ADR-010 §5.1` grounds rather than preference.
- A `corpus` marker on the compiled index (schema `1.3.0`, additive). The full and core indexes
  were previously indistinguishable — same schema version, same commit, different law — so
  every coverage figure carried a denominator nobody could attribute.
- 13 rules and 4 probes. Constitutional coverage 17.1 → 19.0.

### Changed

- Complexity gate ratcheted 11 → 10, the conventional limit, with no per-file exemptions.

---

## [0.2.0] — 2026-08-20

The first release since the engine learned to arrive at a repository it has never seen.

`0.1.0` could govern a project that had been governed from its first commit. `0.2.0` can walk
into an existing one, report an honest baseline without touching it, say what to fix first,
and propose the fixes as diffs it refuses to apply on its own. Four constitutions were
ratified alongside it, and the engine's own gates were tightened until they caught the
engine.

**No breaking changes.** Every `0.1.0` command still exists with the same name and behaviour.
The compiled index moves to schema `1.2.0`, which is additive.

| | 0.1.0 | 0.2.0 |
|---|---|---|
| Constitutions | 11 | **15** |
| Standards | 618 | **670** |
| Anti-patterns | 446 | **498** |
| Architecture decisions | 7 | **9** |
| Index schema | 1.1.0 | **1.2.0** |

### Added — brownfield onboarding

The entry path for a repository Governova has never governed. Measured on first contact
against three third-party repositories in three stacks — `pallets/click`, `expressjs/express`
and `spf13/cobra` — with **zero blocking-tier false positives**.

- `governova onboard` — baseline a repository from the outside. Read-only unless `--accept`
  is passed. (193, 194)
- `governova roadmap` — what to fix first, ordered by impact per unit of work. Read-only.
  (199, 200)
- `governova convert` — propose behaviour-preserving fixes as reviewable diffs, refusing the
  ones it cannot make safely. **Applies nothing by default.** (201, 202)

### Added — requirements, data models and traceability

- `governova requirements status | trace | lint` — read, trace and lint the requirements a
  repository exposes, against an interchange format rather than a format of our own. (148)
- `governova trace` — requirement ↔ code ↔ test traceability, in both directions and across
  time. (161)
- `governova schema` — data-model soundness for Prisma schemas and SQL DDL. (157)
- `governova semantic-eval` — measure whether a configured semantic backend is good enough to
  be trusted with governance, instead of assuming it is. (171)

### Added — the constitution

Four constitutions ratified, taking the corpus from 11 to 15:

- **C11 — Requirements Engineering** (150), adopted on Governova itself from tier 0 to
  tier 2 (152)
- **C14 — Data Design** (159)
- **C13 — Software Evolution** (163)
- **C12 — System Modelling** (165)

- **C0 §3.1 — the `Grounded In` provenance block.** A standard now records the body of
  practice it descends from. (141) Twelve existing standards were retro-cited with their
  grounding in the canon. (146)
- Phase 2 closed: project governance is a protocol, not a constitution. (167)

### Added — architecture decisions

- **ADR-007** — lifecycle completeness: govern the whole SDLC, not only the code. (131, 132)
- **ADR-008** — the semantic tier has no default endpoint, and the bar it must clear before
  anything is built on it. (155)

### Changed — the gates now catch the engine

Each of these was written because the repository was found violating a standard it enforces
on everyone else.

- **Test coverage is gated at 80%**, the threshold `S7.25` already set. It was previously
  measured by nobody and gated by nothing. (210)
- **`mypy --strict` is actually enforced**, as this repository had long declared. (207, 208)
- **The CVE gate runs against the commit a release ships**, not only against `main`. (234)
- Every pinned action moved onto the Node 24 runtime. (183)
- `governova validate` existed twice and the two copies had drifted; one of them was silently
  skipping a new check. It is one function now. (223)

### Fixed

- A rule cited `AP-S2.18a` while implementing `AP-S2.18b`, so a true finding was reported
  under a description of a database that was not there. (195, 206)
- Anti-pattern matching stopped at the first half of the sentence. (182)
- The semantic tier was grounded on incidental vocabulary rather than declaration — standards
  were being scored against code they were never shown. (181)
- A transient status discarded an entire measurement instead of being retried (186); so did a
  timeout, which carries no HTTP status and therefore matched nothing (225).
- The semantic tier now reports whether it ran, not only what it found (153), sends what
  breaking a standard looks like rather than only the rule (191), can withhold as well as
  find (178), and drops findings the model itself marks as uncertain (204).
- CLI commands no longer crash while reporting their result. (173)
- The maintenance-type probe had never returned a verdict in its life. Repairing it surfaced
  a real violation that had been invisible rather than absent. (217)
- Commit verdicts now declare which slice of history they were reached in, so two probes
  reading different windows no longer appear to contradict each other. (222)
- Declared law that never reaches the compiled index is now reported. Eleven anti-patterns
  are written down in constitution summary tables that the compiler does not parse, six of
  them Critical. (218)
- The evaluation harness measured itself rather than the backend. (175)

### Security

- **`cryptography` moved to 50.0.0**, clearing `PYSEC-2026-3552`. Transitive via
  `mcp` → `pyjwt[crypto]`; the lockfile pin was the only change. The scheduled supply-chain
  run found it a week after publication with nobody watching. (232)
- **The release gate now runs `pip-audit`.** It previously re-ran eight of the nine gates
  guarding `main`, omitting the one that matters most on ship day, since the advisory
  database moves without this repository moving. (234)

---

## [0.1.0] — 2026-07-30

First public release on PyPI.

The constitution-as-data engine and its local surfaces: the compiler and typed index,
deterministic enforcement across three tiers, the MCP server, the CLI, the VS Code / Cursor
extension, the CI/CD merge gate, the PR Guardian, the web dashboard and the chat notifier —
with the four §18 outputs (Governova Score, Certified, Board-Level Governance Report and
System Bible) generated from the index.

11 constitutions · 618 standards · 446 anti-patterns · index schema 1.1.0.

[Unreleased]: https://github.com/KSDRILL-SA/governova/compare/v0.2.2...HEAD
[0.2.2]: https://github.com/KSDRILL-SA/governova/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/KSDRILL-SA/governova/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/KSDRILL-SA/governova/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/KSDRILL-SA/governova/releases/tag/v0.1.0
