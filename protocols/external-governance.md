# External & Ecosystem Governance Standard

| Attribute | Value |
|-----------|-------|
| **Document** | External & Ecosystem Governance — third-party frameworks, dependencies, services, integrations & vendors |
| **Layer** | Protocol (operationalises the constitution) |
| **Governed By** | C2 — Backend · C3 — Auth · C5 — Database · C8 — Platform Reliability |
| **Applies To** | Every Governova-governed system · everything it depends on or integrates with · any stack · any organisation |
| **Status** | Active |
| **Paired With** | `protocols/brownfield-adoption.md` · `constitution/implementation/` · GOVERNOVA-MASTER.md §15.2 (Temporal Governance) |

---

> *"A system is not only the code you write. It is every framework, package, service, and vendor it depends on. Governova governs the whole surface — inside and out."*

Internal governance (architecture, code, data) is half the system. The other half is **external**: the frameworks it is built on, the packages it pulls, the APIs it calls, the vendors it relies on. A system can be internally perfect and still fail — or leak, or get breached, or go dark — through its external surface. This standard governs that surface.

---

## §1 — The External Surface (What Is Governed)

| # | External layer | Examples | Primary risk if ungoverned |
|---|----------------|----------|----------------------------|
| 1 | **Frameworks & runtimes** | React, Angular, FastAPI, Spring, Rails, .NET | Unsupported versions, breaking upgrades, abandoned tech |
| 2 | **Dependencies & packages** | npm, PyPI, Maven, Cargo, Go modules | Supply-chain attacks, CVEs, license violations, transitive bloat |
| 3 | **External services & APIs** | payment, email, SMS, maps, LLM providers, partner APIs | Outages, breaking changes, rate limits, cost spikes, data exposure |
| 4 | **Integrations** | OAuth providers, webhooks, SSO, data feeds | Over-broad scopes, unverified webhooks, secret leakage |
| 5 | **Infrastructure & platform vendors** | hosting, CDN, queues, DBaaS, observability | Lock-in, data residency, SLA gaps, no exit plan |
| 6 | **Developer tooling** | CI/CD, package registries, build actions | Compromised actions, untrusted plugins in the pipeline |

The **implementation layer** (`constitution/implementation/{stack}/`) governs *how a framework is used correctly*. This standard governs *choosing, depending on, integrating, and maintaining* everything external around it.

---

## §2 — Dependency & Supply-Chain Governance

| Rule | Requirement |
|------|-------------|
| **Lockfile required** | A committed lockfile pins the full resolved dependency tree. Floating/unpinned production deps are a violation. |
| **Vulnerability gate** | An SCA scan (e.g. CVE/advisory check) runs in CI; SEV0/SEV1 vulnerabilities block merge (deterministic — hard block allowed). |
| **License allowlist** | Every dependency's license is checked against an allowlist; copyleft/unknown licenses require an L4 exception. |
| **Provenance / SBOM** | A Software Bill of Materials is generated for releases; provenance preferred where the registry supports it. |
| **Maintenance health** | Unmaintained or single-maintainer critical dependencies are flagged and have a replacement plan. |
| **Update cadence** | Dependency updates land via PR (never silent); security patches are expedited; majors are governed upgrades. |
| **Minimal surface** | New dependencies are justified — prefer the platform/stdlib over a package for trivial needs. |

---

## §3 — External Service & API Governance

Every call across a network boundary you do not own is governed by C2 (resilience) and C8 (reliability):

| Rule | Requirement |
|------|-------------|
| **Typed client + contract** | External APIs are accessed through a typed client bound to a declared contract/version — never ad-hoc raw calls scattered through the code. |
| **Timeout · retry · circuit-breaker** | Every external call has a timeout, bounded retries with backoff, and a circuit breaker. No unbounded waits. |
| **Graceful degradation** | A defined fallback for when the dependency is down (cache, queue, degraded mode) — the system never hard-fails on a third party. |
| **Version pinning** | API versions are pinned; provider deprecations are tracked (temporal governance) and migrated deliberately. |
| **Cost & rate governance** | Rate limits and cost ceilings are known and enforced (esp. metered services like LLM/SMS); runaway usage is alarmed. |
| **No secrets in code** | API keys/tokens live in a secret manager (C3), never in the repo, never in client bundles. |
| **Data minimisation** | Only the data required leaves the system boundary; PII to third parties is governed by the domain layer (POPIA/GDPR/etc.). |

---

## §4 — Integration Governance

| Rule | Requirement |
|------|-------------|
| **Least privilege** | OAuth/SSO/integration scopes are the minimum required; broad scopes need an L4 exception. |
| **Webhook verification** | Inbound webhooks verify signatures/HMAC and validate payloads before processing — never trust an unauthenticated callback. |
| **Secret rotation** | Integration credentials are rotatable and rotated on a schedule or on staff/vendor change. |
| **Idempotency** | Inbound events are processed idempotently (replays and retries cannot double-apply). |
| **Boundary auth** | Integration auth follows C3 (Auth Override applies — security beats convenience). |

---

## §5 — Vendor & Infrastructure Governance

| Rule | Requirement |
|------|-------------|
| **Vendor register** | Every external vendor is recorded: what it does, what data it holds, its SLA, its tier. |
| **Exit / portability plan** | Each critical vendor has a documented migration path — no irreversible lock-in without an L4 decision. |
| **Data residency & compliance** | Where data physically lives is known and satisfies the domain's regulatory basis. |
| **SLA awareness** | The system's reliability targets account for each vendor's SLA; a dependency cannot be more reliable than what it depends on. |
| **Pipeline trust** | CI/CD actions/plugins are pinned to verified versions/digests; untrusted third-party actions are not run with secrets. |

---

## §6 — Temporal Governance of the External Surface

The external surface **decays on its own** — a CVE, a framework major, a deprecated API, a vendor sunset. Governova monitors it continuously (GOVERNOVA-MASTER.md §15.2):

- Framework changelogs, CVE/advisory databases, and dependency releases are watched.
- When an external change may invalidate a standard or introduce risk, the affected item is flagged `TEMPORAL-ALERT` and surfaced for review.
- Standards/dependencies past their review window are marked `UNVALIDATED` — still in effect, surfaced as risk.

External governance is therefore **never "done"** — it is a continuously tended surface, not a one-time checklist.

---

## §7 — Edge Cases

| Edge case | Governed handling |
|-----------|-------------------|
| Transitive dependency risk | Govern the full resolved tree (lockfile), not just direct deps |
| Vendored / forked third-party code in-tree | Govern the integration boundary + track upstream divergence |
| A required dependency with a known unfixable CVE | Recorded exception + compensating controls + review date |
| A vendor with no alternative (true lock-in) | L4-acknowledged risk with a documented contingency |
| Internal/private packages | Same governance as public; provenance from the internal registry |
| LLM / AI provider dependencies | Governed as metered external services (cost, rate, data minimisation, fallback) — plus the AI/ML domain extension |

---

## §8 — Constitutional Mapping & Proposed Standards

Governed by C2 (resilience on external calls), C3 (integration auth, secrets), C5 (external data flows), and C8 (reliability, SLA, supply chain).

Proposed backing standards (pending C0 §8 ratification — L4), logged in `governance/changelog/amendments-log.md`:

| Proposed ID | Title |
|-------------|-------|
| `S8.84` (proposed) | Committed lockfile + CI vulnerability gate; SEV0/SEV1 dependency CVEs block merge |
| `S8.85` (proposed) | Dependency license allowlist; SBOM generated for releases |
| `S2.81` (proposed) | Every external call has timeout + bounded retry + circuit breaker + defined fallback |
| `S3.37` (proposed) | Integrations use least-privilege scopes; inbound webhooks verify signatures |
| `S8.86` (proposed) | Vendor register + exit/portability plan for every critical external vendor |
| `S8.87` (proposed) | Continuous temporal governance of the external surface (CVEs, framework/version changes) |

Until ratified, this document is operational guidance with the force of an active protocol; the standards above are proposals for Founder (L4) ratification.
