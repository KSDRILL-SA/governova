# START HERE — paste this into a new session

This file is the briefing for the next engineer picking up Governova. Copy it whole into
Claude Code (or read it top to bottom yourself) before touching anything.

It is written to be self-contained. A fresh session knows nothing about this repository.

---

You are taking over **Governova** — a constitutional governance platform, live on PyPI as
`governova` (**`0.2.3` published 2026-08-23** — `main` and PyPI in step; see the handoff §1).
**Confirm the published version against PyPI rather than this file**; it said `0.1.0` for two
releases, and a stale claim here is how a session starts by believing something untrue.

You are a senior engineer with **L3 (build)** authority. **L4 — ratifying law, amending the
constitution, tagging a release, approving anything sensitive — is human-only, always.**

REPO: `C:\Users\Public\GITHUB\governova`   BRANCH: `main`, clean, tree clean

---

## READ THESE FIRST, IN THIS ORDER

1. **`planning/handoff-2026-08-23.md` IN FULL.** §3 is the finding that reframes the
   project: the merge gate failed an adopter's build on law they had never adopted.
   **§7 is your work order, and Step 1 needs a human.**
   `planning/handoff-2026-08-22.md` is the session before it and is still worth reading —
   its §1 is why the published wheel did not work once installed. Earlier handoffs
   (`2026-07-30` … `2026-08-03`) are history, not instructions.
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
    uv run pytest scripts/tests -q          # 1348, ~7 min. `--timeout` is NOT installed.
    uv run ruff check scripts/              # NEVER `ruff format` — not enforced in CI
    cd scripts && uv run mypy               # MUST run from scripts/. Strict, 99 files.

PowerShell is primary. **Git Bash stdout is cp1252** and mangles `—`, `·`, `✓`, `✗` in
captured output — the files are UTF-8, the terminal is not. `Select-Object -First N` on a
piped native command gives exit 255; that is a broken-pipe artifact, not a failure.

The full test suite takes ~7 minutes. Run it in the background and do other work — do
not poll it; you are notified when it finishes. Its output is block-buffered when
redirected, so a tail of the log shows nothing new for minutes at a time. That is the
pipe, not a hang.

---

## STATE, AS MEASURED ON `24d99ae` (= `v0.2.3`)

    Tests                    1347 passed · 1 skipped
    validate                 standards=670 errors=0 warnings=287 · integrity OK
    Enforcement coverage     77 rules (23 blocking · 54 advisory) · 41 probes · 9.3%
    Constitutional coverage  19.0%  (113 of 596 applicable standards evidenced)
    Governova Score          80/100  [B]
    mypy                     strict, 99 files, clean
    Corpus                   15 constitutions · 670 standards · 789 anti-patterns
                             4 Layer 4 domains · 19 domain standards · 14 ADRs
    Distribution             PyPI 0.2.3 published 2026-08-23 — main is released
    Governed externally      4 repositories, gate on every PR

**Regenerate all of these before trusting them.** This file has been wrong before, and was
again: it read `72 rules`, which is the count of *implementation bindings* in
`governova stats`. The rule count is `governova coverage`, and it was 77.
`uv run pytest scripts/tests -q`, `governova govscore`, `governova stats`, `governova coverage`.

**The score is held down by exactly one thing.** Four of its five factors score 100 or 85.
Constitutional coverage scores **19/100**. Certified (≥85) needs that factor at 44, which is
262 evidenced standards against today's 113 — roughly 150 more rules. That is real work and it
is **not launch-blocking**; see the 08-22 handoff §6 for why it is also the shape of a trap.

**`1 violated` is correct and was earned.** A probe that had never returned a verdict in its
life was repaired, and it surfaced a real violation that had been invisible rather than
absent. Do not "fix" that number by breaking the probe again.

---

## YOUR WORK, IN ORDER

Full detail is `planning/handoff-2026-08-23.md` §7. In brief:

    1. v2-deferral ADR  record what v1 excludes, and why               L3 proposes
    2. Stage 1          migrations + client; the ledger is in RAM        L3
    3. Xkimi profile    declare D-FINTECH; 182 findings, mostly true     L3

**Nothing is release-blocked.** `0.2.3` shipped on 2026-08-23 and `main` and PyPI are in step,
so the next session starts from a released baseline rather than a backlog.

**The engine no longer has to be pointed at anything by hand.** `governova-enforce --changed`
runs on every pull request in four external repositories across three GitHub owners. That is
where the next finding will come from, and it now arrives without anybody remembering to look.

**The approved v1 scope is narrower than "everything".** Persistence, billing, the Angular
console and the marketing site. The Intelligence Gateway, the four stub surfaces and
Certification are v2 — deferred deliberately, and step 1 is writing that down.

**The critical path runs through decisions, not code.** You can be entirely blocked while the
repository is entirely green — that is the expected state, not a problem with your setup.

**What is deliberately not on this list:** writing more rules. Certified needs ~150 more and
they are not launch-blocking. See the 08-22 handoff §6 before spending a session on them.

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
