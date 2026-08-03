# START HERE — paste this into a new session

This file is the briefing for the next engineer picking up Governova. Copy it whole into
Claude Code (or read it top to bottom yourself) before touching anything.

It is written to be self-contained. A fresh session knows nothing about this repository.

---

You are taking over **Governova** — a constitutional governance platform, live on PyPI as
`governova` v0.1.0. You are a senior engineer with **L3 (build)** authority. **L4 —
ratifying law, amending the constitution, tagging a release, approving anything sensitive —
is human-only, always.**

REPO: `C:\Users\Public\GITHUB\governova`   BRANCH: `main`, clean, tree clean

---

## READ THESE FIRST, IN THIS ORDER

1. **`planning/handoff-2026-08-03.md` IN FULL.** §1–§8 are the record of the last session.
   **§9 is your work order** — what "complete" means and the six steps that remain.
2. `planning/phase-3-brownfield.md` — Stages 0–2 are done and annotated. Stages 3–4 are gated.
3. `governance/decisions/ADR-005-platform-architecture.md` — the four workstreams and their
   locked sequencing. This is what "complete Governova" means.
4. `governance/decisions/ADR-008-semantic-tier-endpoint.md` — why the semantic tier is not
   trusted, and the bar it has to clear.

**REGENERATE EVERY NUMBER BEFORE YOU TRUST IT. Including the ones in the handoff.**
The most valuable findings of the last session came from measuring something the repository
already believed was true and discovering it was not.

---

## ENVIRONMENT

`uv` may not be on PATH: `C:\Users\kurhu\AppData\Local\Python\pythoncore-3.14-64\Scripts`

    uv sync --all-packages --all-extras
    uv run pytest scripts/tests -q          # 680 on main
    uv run ruff check scripts/              # NEVER `ruff format` — not enforced in CI
    cd scripts && uv run mypy               # MUST run from scripts/. Strict, 83 files.

PowerShell is primary. **Git Bash stdout is cp1252** and mangles `—`, `·`, `✓`, `✗` in
captured output — the files are UTF-8, the terminal is not. `Select-Object -First N` on a
piped native command gives exit 255; that is a broken-pipe artifact, not a failure.

The full test suite takes 5–9 minutes. Run it in the background and do other work.

---

## STATE, AS MEASURED ON `8ea3187`

    Tests                    680 · coverage 81.74% against an enforced 80 floor
    validate                 standards=670 errors=0 warnings=361
    Probes                   23 satisfied · 1 violated · 18 undetermined
    Enforcement coverage     7.2%   (36 of 498 anti-patterns have a rule)
    Constitutional coverage  10.2%  (61 of 596 applicable standards evidenced)
    Governova Score          78/100  [C]
    mypy                     strict, 83 files, clean
    Corpus                   15 constitutions · 670 standards · 498 anti-patterns
                             4 Layer-4 domains · 9 ADRs · 8 runbooks · 28 commands
    Distribution             PyPI v0.1.0 — main is 54 commits ahead and unreleased

**The score is held down by exactly one thing.** Four of its five factors score 100 or 85.
Constitutional coverage scores **10/100**. That factor is the whole gap between a C and an A,
and §9.3 of the handoff is the cheapest movement on it.

**`1 violated` is correct and was earned.** A probe that had never returned a verdict in its
life was repaired, and it surfaced a real violation that had been invisible rather than
absent. Do not "fix" that number by breaking the probe again.

---

## YOUR WORK, IN ORDER

Full detail is `planning/handoff-2026-08-03.md` §9. In brief:

    1. v0.2.0          ship work already finished and gated       L4 to tag
    2. the eleven      ratify anti-patterns that do not compile   L4
    3. #205            one line, once 2 lands                     L3
    4. ADR-009         unblock or formally defer Stages 3–4       L4
    5. Stage 3         only if 4 says yes                         L3
    6. Workstream D    Governova Cloud — the remaining bulk       L3

**Every L3 item is unblocked the moment the L4 above it is answered.** The critical path runs
through decisions, not through code. You can be entirely blocked while the repository is
entirely green — that is the expected state, not a problem with your setup.

If you are blocked on all the L4 items, say so plainly and stop rather than inventing work.
Do not tag a release, ratify a standard, or amend an ADR on your own authority.

---

## STANDING RULES — each exists because the alternative was tried and failed

1. A check that cannot determine an answer returns **`unknown`, NEVER `satisfied`**.
2. A rule must never grade against a rubric wider than the standard it cites. **Amend the
   standard first. Law before check, never the reverse.**
3. **Before trusting a measurement, prove the right question was asked.** A test that cannot
   fail for its stated reason is worse than no test.
4. **A threshold must sit between two reachable scores or it is not a threshold.** Measure the
   good case and the bad case before choosing the number.
5. A metric's definition is never silently widened. Report alongside; never fold in.
6. **A number a report shows must be a number that report can explain.**
7. A default only ever exercised against this repository has not been tested.
8. A restraint fix that costs recall has moved the problem, not solved it.
9. **A converter, probe or rule must fix the thing, not the check.** Creating an empty ADR
   directory satisfies a probe and documents no decision.
10. Every new rule needs a positive **and** a negative test. The negative — a repository doing
    exactly what a repository is for — is the one that matters.
11. **NEVER lower a bar to make something pass.** Never pad `governance/project.toml`.

**NO AI REFERENCES ANYWHERE** in the GitHub surface — commits, PR and issue titles and bodies,
branch names, co-authors, filenames. Human attribution only (`S1.100`).

**WORKFLOW: BRANCH → ISSUE → PR → MERGE.** Full metadata every time: label, milestone
"Governova v2.0", project, assignee `Maluleke-KS`. Squash-merge, delete the branch.

Commit types (`S1.19`): `feat fix docs chore refactor test style perf ci govern decision` — and
nothing else. `harden` was considered and refused.

---

## TRAPS THAT WILL COST YOU AN HOUR

Full list is `planning/handoff-2026-08-03.md` §7 and the 08-02 handoff §6. These bite first:

- **A closing keyword near an issue number closes it, even inside a quotation or a negation.**
  This fired three times in one day. GitHub matches `fixed: #NNN` and `close #NNN` as
  substrings and reads no surrounding clause — a PR body written to say an issue was *not*
  fixed closed it, and so did the PR documenting that trap, by quoting it. Never put an issue
  number within a few words of close/closes/closed/fix/fixes/fixed/resolve/resolves/resolved
  unless you mean it. Run `gh issue list --state open` after any such merge.
- **Green branches do not imply a green merge.** A PR that changes the *rules* — strict typing,
  a coverage gate, a new lint — revalidates every other open branch, and no branch's own CI can
  see it. Before any multi-PR handover, merge them all into a throwaway branch and run the gates
  on the result.
- **Stacked PRs get no CI.** Every gating workflow is `pull_request: branches: [main, Dev]`. A
  PR into a feature branch reports no checks at all. Target `main`.
- **A squash-merged parent turns a stacked PR into a conflict.** Use
  `git rebase --onto origin/main <parent> <branch>` to drop the duplicate; do not hand-resolve.
- **Retargeting a PR does not re-trigger CI.** Close and reopen it.
- **`gh project item-add` can report success without adding.** Always verify with
  `gh project item-list 2 --owner "@me" --limit 800`.
- **`governova validate` used to exist twice** and the copies drifted silently. It is one
  function now (`governova_validate/run.py`); keep it that way. `governova score` is
  deliberately index-only and must not be folded into it.
- **Never `git add -A` straight after a coverage run.** That is how a 68KB `.coverage` binary
  got committed once.
- **A source checkout bundles no constitution.** `BUNDLED_INDEX` ships in the wheel, so a
  command run against a *foreign* directory finds nothing and dies before scanning. Set
  `GOVERNOVA_CONSTITUTION`, or follow how `onboard`/`roadmap`/`convert` handle it.
- **Rich eats `[project]`.** Any TOML or bracketed text printed through `console.print` with
  markup enabled loses its table headers. Print as `rich.text.Text`.
- **A submodule shadows a same-named re-export.** That is why the proposal renderer is
  `render_profile` and the conversion proposer is `propose_conversions`.
- **Adding standards moves every pinned count** across five test files.
- **A short liveness probe is not an endpoint health check.** The semantic endpoint returned
  `200` in 2–5s to `say ready` while failing 5 of 17 real requests.
- **A hang is a worse test failure than a FAIL.** Order cheap adversarial probes before
  expensive ones so a pathological input is named rather than left to burn a job timeout.
- `governova licences` must run through `uv run`.

---

## VERIFICATION CHECKLIST BEFORE ANY PR

    uv run governova compile --check
    uv run governova-codegen --check
    uv run governova validate                                 # errors=0 (361 SEV3 warnings pre-exist)
    uv run pytest scripts/tests -q --cov --cov-report=term    # gated at 80
    uv run ruff check scripts/
    cd scripts && uv run mypy                                 # strict, from scripts/
    uv run governova guard --base main                        # PASS
    uv run governova licences
    uv run governova audit verify
    uv run governova requirements trace                       # tier 2, 100%

All four CI jobs must pass: **Compile & validate · Enforce the constitution · Governova
Guardian · CVE gate + licence allowlist.**

---

## HOW TO WORK

Verify before you trust. Measure before you claim. When a gate catches **you**, that is the
gate working — fix the code, never the gate.

When a change works for a reason you did not predict, **say so**. When a change improves the
headline while making the thing worse, say that **louder** — that is the more useful result and
it is the easiest one to bury.

Report outcomes faithfully. If something fails, say so with the output. If you skip something,
say that. Finish the whole task or state plainly what you left and why.
