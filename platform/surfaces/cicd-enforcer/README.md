# Governova — CI/CD Enforcer (the merge gate)

**Status:** Alpha — working (v0.1)
**Surface:** GitHub Action · the enforcement wedge (GOVERNOVA-STRATEGY §3, §11)

The surface that makes governance **undeniable**. Where the MCP, CLI, and IDE
surfaces *report* violations, the enforcer *blocks* them: it scans a pull request's
changed files and fails the build when code introduces a constitutional violation —
so a violation cannot be merged.

## How it works

```
PR opened ──▶ [governova-enforce] ──▶ scans changed source files
                       │
                       ├── clean      → check passes, merge allowed
                       └── violation  → inline annotation + ❌ status, merge blocked
```

It reuses the engine's **reliable-tier** detection core (`governova_checks`) — the
exact same deterministic rules the MCP server exposes advisorily. One rule set,
shown as advice at the IDE/MCP surfaces and **enforced** here. No duplicated logic.

## Use it (GitHub Actions)

```yaml
# .github/workflows/enforce.yml
on:
  pull_request:
jobs:
  enforce:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }        # history is needed for the diff
      - uses: KSDRILL-SA/governova/platform/surfaces/cicd-enforcer@main
        with:
          mode: block                   # or: advisory
          base: ${{ github.event.pull_request.base.sha }}
```

## The CLI behind it

```bash
governova-enforce path/to/file.ts          # scan specific files
governova-enforce --changed --base origin/main   # scan a PR's changed files
governova-enforce --changed --mode advisory      # report, never block
governova-enforce --changed --format github      # GitHub Actions annotations
```

| Option | Purpose |
|--------|---------|
| `--changed` | Scan files changed vs `--base` (the default when no paths are given) |
| `--base <ref>` | Git ref to diff against (the PR base) |
| `--mode block\|advisory` | `block` fails the build on a finding; `advisory` only reports |
| `--format github\|text\|json` | `github` emits inline PR annotations |
| `--ignore <glob>` | Extra path globs to skip (repeatable) |

Test code, fixtures, vendored dependencies, and the rule set itself are ignored by
default — they legitimately contain violation patterns as examples.

## Discipline

Reliable tier only: every finding is **deterministic and explainable** — it names
the exact anti-pattern (`AP-S{C}.{N}{x}`) and the standard it violates. Blocking is
appropriate precisely because the checks are deterministic; the semantic/LLM tier is
a separate, later layer of this same surface and never silently changes these
results. The MCP surface stays advisory (GOVERNOVA-STRATEGY §11.2); enforcement lives
here.
