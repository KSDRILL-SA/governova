# Vendor Register

> **`S8.86` — every critical external vendor has a register entry (what it does, what data it
> holds, its SLA) and a documented exit/portability plan.** Lock-in nobody has costed is
> discovered when a price changes or a term changes, which is the moment it costs the most.

**Last reviewed:** 2026-08-21 · **Reviewed on every release, and on any ADR that adds a dependency.**

---

## What counts as a vendor here

A **vendor** is an external *service* this project depends on to build, ship or run — something
with an account, a term of service, and the ability to withdraw. A **library** is not a vendor:
it is a pinned artefact governed by `uv.lock`, the CVE gate (`S8.84`) and the licence allowlist
(`S8.85`), and a version that already exists cannot be taken away.

That distinction is why `pydantic`, `typer`, `rich`, `markdown-it-py` and `mcp` are not in this
table. They are dependencies, and they are managed — by a different control.

---

## Register

| Vendor | What it does | What data it holds | SLA | Lock-in |
|---|---|---|---|---|
| **GitHub** (Microsoft) | Source hosting, CI (Actions), issues, pull requests, releases | The full source and corpus, all issue and pull-request history, CI logs, Actions secrets, the audit-chain records that live in-repo | No contractual SLA on the current plan. GitHub publishes 99.9% for Enterprise; this project is not on it | **High.** Not the git data — the workflow surface |
| **PyPI** (Python Software Foundation) | Distribution of the `governova` wheel and sdist | Published artefacts and their attestations. **No user data** — the CLI phones nothing home | None. Community-run, best-effort | **Low** |
| **Astral** (`uv`, `ruff`) | Dependency resolution, lockfile format, the CI setup action, the linter | Nothing. Both tools run locally | None. Open source | **Medium** |
| **LLM endpoint** (operator's choice) | The semantic tier — advisory review only | Whatever source is sent for review, at whichever endpoint the *operator* configures. Governova chooses no provider and ships no key | Whatever the operator's provider offers | **None by design** |

---

## Exit plans

### GitHub — the one that matters

**Git itself is not the exposure.** Every clone is a complete copy of the history; moving the
repository is a `git push` to another remote and costs an afternoon.

The exposure is everything built *around* the repository:

| Asset | How it leaves |
|---|---|
| Source and corpus | Already distributed — every clone is complete |
| Issues, pull requests, comments | `gh api` export, or GitHub's migration API. Held as JSON in-repo if an exit becomes likely |
| CI workflows | **The real work.** Six workflows in Actions syntax. GitLab CI, Forgejo Actions and Woodpecker all express the same steps; the porting cost is days, not hours |
| The `pr-guardian` and `cicd-enforcer` actions | Written as composite actions. Forgejo Actions runs them nearly unchanged; other runners need a rewrite |
| PyPI Trusted Publishing | Bound to GitHub's OIDC issuer. Leaving GitHub means falling back to an API token until the new forge is configured as a trusted publisher |
| Audit chain | Lives in `governance/audit/` **inside the repository**, deliberately. It leaves with the clone |

**Contingency if GitHub becomes unavailable or unacceptable:** the repository and its history are
already portable. Releases can be cut locally and published with a token. CI is the only piece
that stops working, and CI stopping degrades the gates rather than the product — the engine runs
offline, so a consumer's installed copy is unaffected by anything that happens to this forge.

### PyPI

Wheels are self-contained and standards-compliant. `pip` and `uv` both install from any index, a
local directory, or a git URL. If PyPI became unavailable, distribution would move to GitHub
Releases with a documented index URL — the artefact does not change, only where it is fetched
from.

### Astral

`uv.lock` is a documented format and `pyproject.toml` is a standard. Replacing `uv` means
regenerating a lockfile with `pip-tools` or Poetry — mechanical, and a day's work. Replacing
`ruff` means `flake8` plus `isort` plus `black`, which is slower and noisier but well-trodden.
`setup-uv` in CI would be replaced by `setup-python` plus a pip install.

The lock-in is rated medium rather than low because both tools are load-bearing in CI and in
`S1.70`/`S1.74`/`S8.84` evidence, so a swap touches probes as well as pipelines.

### LLM endpoint

**This one was designed to have no lock-in, and the design holds.**

- No vendor SDK. Two open wire protocols (`chat_completions`, `messages`), selected by the operator.
- No default endpoint and no bundled hostname — an unset configuration means the tier is
  *inactive* and says so, rather than silently reaching for a provider.
- `ADR-010` §5.1: the deterministic engine — rules, probes, Score, Board Report, CLI, MCP server,
  CI gate — runs with nothing configured, offline, forever. That is a guarantee, not a default.

Switching providers is an environment variable. Losing every provider costs the advisory tier and
nothing else.

---

## Not vendors of this repository

`ADR-010` and C6 name **Vercel** and **Railway**, and C8 names **Sentry** and **Better Stack**.
Those are platforms of the *reference systems* the constitution governs — FundsLink, Maphophe,
Reserve Bank, SyncUp. Governova itself deploys nothing and runs nothing hosted.

They are listed here as absent on purpose. A register padded with vendors this project does not
use would make the table look thorough and make it useless, and the first person to act on it
would plan an exit from a service nobody was using.

**When Governova Cloud exists (`ADR-010`, `D-09`), it will add real entries here** — a host, a
database, an identity provider and a payment processor, each with the data it holds and the plan
for leaving it. That is the point at which this register starts carrying weight, and it should be
written before the first of them is chosen, not after.

---

## The rule this register follows

**A vendor enters this table when the dependency is taken, not when it becomes uncomfortable.**
An entry leaves only when the dependency is genuinely gone — never because the exit plan was
written and then the entry felt handled.

An exit plan that has never been costed is a wish. Where the cost is unknown, this register says
so rather than estimating downward.
