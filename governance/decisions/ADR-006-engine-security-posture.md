# ADR-006 — Engine Security Posture

---

| Attribute   | Value |
|-------------|-------|
| **ID**      | ADR-006 |
| **Date**    | 2026-07-28 |
| **Status**  | accepted |
| **Supersedes** | — |
| **Relates To** | S8.84, S2.81, S1.98, S10.8 |

---

## Context

Until #112 the engine could only run inside its own repository, so its attack
surface was bounded by a single trusted repo and a single trusted operator. Making
it installable changed the threat model rather than extending it:

- It runs **inside other people's CI**, as a **blocking gate**, over **their**
  source — including source contributed by whoever opens a pull request.
- A hang is their pipeline stalled. An argument injection is a write inside their
  runner. An error string is something their whole org can read.

The strengthening roadmap called for a security review of the subprocess, HTTP,
and file-I/O surfaces (§7). It was run before publication rather than after,
because a governance tool that gets compromised is worse than no governance tool:
it carries the authority of a gate.

---

## Decision

Adopt four standing rules for the engine, each now enforced by test.

### 1. Every regex is bounded, and line length is capped

`AP-D-FINTECH.3a` combined unbounded `[\w.]*` with `\w*balance\w*` — overlapping
classes — and degraded super-quadratically: **8.7 seconds on one 20,000-character
line**, which is an ordinary minified bundle. Scaling was measured at roughly 16×
per 4× of input, so a 100 KB line would have stalled a consumer's build for
minutes.

Rules now use bounded quantifiers, and `scan_text` skips lines longer than
`MAX_LINE_LENGTH` (4000). The cap is defence in depth: regex cost is a function
of line length, so the length is capped rather than every future rule trusted. A
parameterised test times **every** rule against ten adversarial payloads.

Accepted trade-off: a violation hidden on a >4000-character line is not detected.
Such a line is not human-reviewable, the standards do not meaningfully govern
generated blobs, and the alternative is a denial of service.

### 2. Anything reaching a subprocess argument is validated as what it claims to be

`git diff … "{base}...HEAD"` interpolated caller input into an argument vector.
There is no shell, so this was never shell injection — it was **git's own option
parsing** being handed caller-controlled text. Confirmed exploitable: a `base` of
`--output=<path>` makes git write an attacker-chosen file.

The value arrives from a workflow input. A consumer wiring it from a branch name
or a `pull_request_target` payload hands that capability to any pull-request
author. Revisions are now validated against a strict pattern and the argument
list is terminated with `--`.

### 3. Outbound URLs are http/https only, validated in one place

Both network surfaces passed operator-supplied URLs to `urlopen`, which honours
every scheme it knows — including `file://`. Neither was a remote-attacker
capability, since both come from environment variables; but a typo'd, templated,
or inherited org-level value is exactly how these become real. Validation lives
in `governova_checks.net` so a third network surface cannot forget it.

### 4. Errors never echo URLs or credentials

`urllib` includes the request URL in its exceptions, and an endpoint configured
as `https://user:key@host` would put those credentials into a CI log many people
can read. Transport failures now report the exception **type** only, and the URL
validator names the rejected scheme but never the URL.

### Evidence must resolve inside the repository

A separate finding from the same pass: `_evidence_resolves` checked existence
only, so a project profile could cite an absolute path to any file on the
machine. `/etc/hostname` exists and evidences nothing. Evidence is only meaningful
if a third party reading the repository can check it, so citations that are
absolute or traverse outside the root are reported as unresolved claims.

---

## Consequences

### What becomes easier

- The engine can be published without shipping a denial of service into every
  consumer's pipeline.
- The four rules are testable properties rather than review habits, so they hold
  as the rule set grows — and the rule set is the part expected to grow most.

### What becomes harder

- New rules must be written with bounded quantifiers, and the ReDoS test will
  fail those that are not. This is intended friction.
- Operators pointing a surface at a non-http endpoint now get a refusal rather
  than a surprising success.

### Constitutional alignment

Reinforces `S2.81` (external calls are bounded and defended), `S8.84`
(supply-chain and dependency discipline), and `S10.8` — the engine that enforces
the human-only L4 boundary must itself be trustworthy, or the boundary is
decorative.

### Not addressed here

- The bundled constitution and `GOVERNOVA_CONSTITUTION` are operator-supplied and
  loaded through Pydantic validation; a hostile index is treated as an operator
  compromise, not a threat boundary.
- No dependency vulnerability gate runs in CI yet, which `S8.84` requires. Tracked
  separately.
