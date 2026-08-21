<!--
S1.46 — every field below is required. A pull request with missing fields is
returned before review begins (S1.35).

Delete no headings. If a field does not apply, write why it does not apply —
"n/a" with no reason is a missing field.
-->

## Linked issue

<!-- S1.46 — `Closes #N` so the issue closes on merge. If this closes nothing,
say what it advances and why no issue exists. -->

Closes #

## What changed

<!-- Every component, service, model, route, standard or rule this touches.
A bullet list, not a paragraph — a reviewer reads this to decide where to look. -->

-

## Why it changed

<!-- Link the approved proposal or issue. The reasoning, not the restatement:
"why this, rather than the alternative" is what a later reader needs. -->

## How to test

<!-- Step by step from a clean state. A reviewer must be able to follow this
without asking a question. -->

1.

## Screenshots

<!-- S1.46 — **mandatory** for every change that affects a UI, before and after.
For a change with no UI surface, write "no UI surface". -->

no UI surface

## Verification

<!-- The commands that were actually run, with their results. Paste the output
rather than describing it. -->

| Check | Result |
|---|---|
| `pytest scripts/tests --cov` | |
| `mypy` (strict, as CI invokes it) | |
| `ruff check scripts/` | |
| `governova validate` | |
| `governova guard --base main` | |

## Constitutional compliance

<!-- S1.46 — cite every standard that governs this change, and say how it is
met. A citation with no claim attached is not a citation.

If this change amends the constitution, name the standard amended and the
authority for it (C0 §8). -->

- **`S1.2`** —

## Self-review (S1.45)

<!-- All four quadrants, completed before this pull request was opened. -->

- [ ] **Architecture** — correct layer, service boundary respected, no business logic in the presentation layer
- [ ] **Code quality** — no `any`, no dead code, no debug artifacts, no magic literals
- [ ] **Testing** — the change is covered, and the near-miss case is covered too
- [ ] **Constitutional** — every standard this touches has been read, not recalled

- [ ] I have completed the self-review checklist (S1.45).
