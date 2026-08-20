# C8 — Platform Reliability Constitution

---

| Attribute          | Value                                                              |
|--------------------|--------------------------------------------------------------------|
| **Document**       | C8 — Platform Reliability Constitution                             |
| **Organisation**   | KSDRILL SA                                                         |
| **Version**        | v1.0                                                               |
| **Status**         | LOCKED                                                             |
| **Locked**         | 2026-05-08                                                         |
| **Next Review**    | 2026-08-08                                                         |
| **Applies To**     | Both Stacks · All Systems                                          |
| **Paired With**    | — (Runbooks in `runbooks/` folder)                                 |

---

> *"Infrastructure that breaks silently is infrastructure that was never tested. When something breaks, the process is the product."*

---

## Opening Statement

The Platform Reliability Constitution governs everything between writing code and running it in production. It covers deployment platforms, CI/CD pipelines, environment governance, observability, incident response, rollback procedures, and post-mortem protocol. This constitution was formed by merging the Infrastructure Constitution and Incident Response Constitution — two documents that were always read together because deploying a system and responding to that system's failures are inseparable concerns.

This constitution does not govern how the application code is written — that is C2 through C5. It does not govern what features are built — that is C9. What this constitution governs is the operational layer: the machinery that gets code to users reliably, the detection layer that knows when something is wrong, the response protocol that minimises blast radius, and the learning process that prevents recurrence.

---

## Table of Contents

| Part | Title | Standards |
|------|-------|-----------|
| Part 1 | Deployment Platforms | S8.1–S8.8 |
| Part 2 | CI/CD Pipeline | S8.9–S8.16 |
| Part 3 | Docker & Local Development | S8.17–S8.23 |
| Part 4 | Environment & Configuration Governance | S8.24–S8.30 |
| Part 5 | Monitoring & Observability | S8.31–S8.40 |
| Part 6 | Security & Secrets | S8.41–S8.46 |
| Part 7 | Severity Framework | S8.47–S8.54 |
| Part 8 | Detection & Alerting | S8.55–S8.60 |
| Part 9 | Response Runbooks | S8.61–S8.66 |
| Part 10 | Rollback Procedures | S8.67–S8.72 |
| Part 11 | Incident Communication | S8.73–S8.76 |
| Part 12 | Post-Mortem Protocol | S8.77–S8.82 |
| Anti-Patterns Index | — | AP-S8.* |
| Cross-Constitution Dependency Map | — | — |
| Amendment Log | — | — |

---

## Part 1 — Deployment Platforms (`S8.1`–`S8.8`)

---

### S8.1 — Vercel for All Next.js Deployments — Unified Full-Stack

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S8.1 |
| **Priority**    | Critical |
| **Applies To**  | Next.js Only |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S6.12` (Next.js topology) |
| **Enforced By** | Architecture Review |

**Standard:**
All Next.js systems (Maphophe, SyncUp) deploy to Vercel. Frontend, API routes, and edge functions are co-deployed in one Vercel project. Vercel handles automatic preview deployments for every PR, production deployment on main branch push, and environment variable management via the Vercel dashboard. No custom server configuration.

**Anti-Patterns:**
- `AP-S8.1a` — Deploying Next.js to Railway or a custom Docker container — loses Vercel's zero-config Next.js optimisation, automatic preview deployments, and edge runtime support.

**Cross-References:** `S6.12` (Next.js topology), `S8.4` (preview deployments)

---

### S8.2 — Railway for FastAPI — Angular Stack Backend Exclusively

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S8.2 |
| **Priority**    | Critical |
| **Applies To**  | Angular Only |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S6.13` (Angular topology) |
| **Enforced By** | Architecture Review |

**Standard:**
All FastAPI backends (FundsLink, Reserve Bank) deploy to Railway with Python runtime and Uvicorn. Railway provides managed PostgreSQL, managed MongoDB, managed Redis, and zero-downtime deploys. FastAPI is never deployed to Vercel serverless functions — Python cold starts and long-running database connections are incompatible with serverless architecture.

**Anti-Patterns:**
- `AP-S8.2a` — Deploying FastAPI to Vercel serverless functions — Python cold starts take 2-5 seconds; database connections cannot be persistent; the deployment model is incompatible with FastAPI's connection pooling.

**Cross-References:** `S6.13` (Angular topology), `S6.29` (deploy order)

---

### S8.3 — Angular Frontend on Vercel — Separate Project from FastAPI

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S8.3 |
| **Priority**    | Critical |
| **Applies To**  | Angular Only |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S6.13`, `S8.2` |
| **Enforced By** | Architecture Review |

**Standard:**
The Angular frontend deploys as a separate Vercel project from the FastAPI backend. Angular is a static SPA build — Vercel serves it correctly. The two deployments coordinate via `S6.29` (FastAPI first). `environment.prod.ts` points to the Railway FastAPI URL.

**Anti-Patterns:**
- `AP-S8.3a` — Frontend and API deployed as one unit — a change to either forces a redeploy of both, so a CSS fix carries the risk profile of a backend release and the two can never be rolled back independently.

**Cross-References:** `S8.2` (Railway), `S6.29` (deploy order)

---

### S8.4–S8.8 — Additional Platform Standards

> **S8.4** — Preview deployments are generated for every PR on both stacks. Next.js: Vercel preview URL. Angular: Vercel preview URL for frontend + Railway staging for API PRs. E2E tests run against preview deployments.
>
> **Anti-Patterns:**
> - `AP-S8.4a` — E2E tests run against localhost or a shared staging box rather than the PR's own preview deployment — they then pass against a build nobody is merging, and the artefact that reaches production was never exercised.

> **S8.5** — Three environments — Development (local Docker Compose), Staging (auto-deployed from main merge), Production (manually promoted from staging). Code never goes directly from development to production.
>
> **Anti-Patterns:**
> - `AP-S8.5a` — Code promoted from a developer's machine straight to production, skipping staging — the first environment that resembles production is then production itself.

> **S8.6** — Zero-downtime deploys on all production deployments. Vercel: atomic deployment with instant rollover. Railway: rolling restart with minimum 1 healthy replica before killing old container.
>
> **Anti-Patterns:**
> - `AP-S8.6a` — The old container stopped before a replacement is serving traffic — a deploy window becomes an outage window, and every deploy carries a reason to defer deploying.

> **S8.7** — Production deployment rollback available in under 5 minutes via one action. Vercel: one-click rollback to previous deployment. Railway: redeploy previous build. Rollback procedures are tested in staging quarterly.
>
> **Anti-Patterns:**
> - `AP-S8.7a` — A rollback procedure that has never been executed — an untested rollback is a plan, not a capability, and it is discovered to be neither during the incident it was written for.

> **S8.8** — ChromaDB on Railway as a separate service with persistent volume. No public port exposed — FastAPI accesses ChromaDB via Railway internal networking only (FundsLink).
>
> **Anti-Patterns:**
> - `AP-S8.8a` — ChromaDB reachable on a public port — an unauthenticated vector store holding embedded source content becomes a data-exfiltration surface that no application-layer control covers.

---

## Part 2 — CI/CD Pipeline (`S8.9`–`S8.16`)

---

### S8.9 — GitHub Actions for All CI — Separate Workflow Per Repository

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S8.9 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S7.6` (test suite in CI) |
| **Enforced By** | Repository configuration |

**Standard:**
All CI/CD runs on GitHub Actions. Every repository has: `ci.yml` (runs on PR — lint, typecheck, tests, coverage gate, critical E2E), `deploy-staging.yml` (runs on main merge — auto-deploy to staging), `deploy-production.yml` (manually triggered — requires explicit approval).

**Anti-Patterns:**
- `AP-S8.9a` — Manual deploys to staging by pushing directly to a deploy branch — bypasses CI gates and produces an untested staging environment.

**Cross-References:** `S7.6` (CI test requirements), `S8.12` (production approval gate)

---

### S8.10 — CI Runs in Under 5 Minutes — Parallelise Tests

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S8.10 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S8.9` (GitHub Actions) |
| **Enforced By** | CI timing alert |

**Standard:**
PR CI completes in under 5 minutes. Achieve via: parallel job matrix (lint, typecheck, tests run simultaneously), test file sharding for large test suites, Docker layer caching, and dependency caching. A CI run exceeding 10 minutes is a performance bug fixed within one sprint.

**Anti-Patterns:**
- `AP-S8.10a` — Sequential CI steps (lint then test then build) when they can run in parallel — triples CI time unnecessarily.

**Cross-References:** `S7.6` (critical paths on every PR, full suite nightly)

---

### S8.11 — Automatic Staging Deploy on Main Merge

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S8.11 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S8.9` (GitHub Actions), `S6.29` (Angular deploy order) |
| **Enforced By** | GitHub Actions `deploy-staging.yml` |

**Standard:**
Every merge to main automatically deploys to staging. Angular stack: Railway (FastAPI) deploys first, then Vercel (Angular) — per S6.29. Staging is the canonical test environment for final QA and E2E validation before production. Never manually deploy to staging.

**Anti-Patterns:**
- `AP-S8.11a` — Manual staging deploy by directly pushing to a deploy branch — bypasses CI; untested code enters staging.

**Cross-References:** `S6.29` (Angular deploy order), `S8.9` (GitHub Actions)

---

### S8.12 — Production Deploy Is Manual and Gated — Explicit Approval Required

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S8.12 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S8.9` (GitHub Actions) |
| **Enforced By** | GitHub Actions environment protection rule |

**Standard:**
Production deployments are triggered via GitHub Actions `workflow_dispatch` with an `environment: production` protection rule requiring explicit owner approval. No automatic production deploys. Production deploy only runs after staging has been validated and owner approval is granted.

**Anti-Patterns:**
- `AP-S8.12a` — Automatic production deploy on main merge — removes the human validation gate between staging and production.

**Cross-References:** `S8.5` (three environments), `CF-15` (production deploy without staging validation = SEV1)

---

### S8.13–S8.16 — Additional CI/CD Standards

> **S8.13** — Dependency caching in CI: TypeScript `~/.npm` cached keyed on `package-lock.json` hash. Python `~/.cache/pip` cached keyed on `requirements.txt` hash. Uncached CI runs are 3× slower.
>
> **Anti-Patterns:**
> - `AP-S8.13a` — A cache keyed on the branch name or a fixed string rather than the lockfile hash — it never invalidates when dependencies change, so CI installs a stale tree and the failure it produces is attributed to the code.

> **S8.14** — Prisma migrations validated in CI: `prisma migrate diff` runs on every PR that changes `schema.prisma`. Detects missing migration files before merge.
>
> **Anti-Patterns:**
> - `AP-S8.14a` — A pull request changing `schema.prisma` with no corresponding migration file — the schema and the database diverge silently, and the divergence surfaces on the deploy rather than in review.

> **S8.15** — Build artefacts use Docker layer caching with GitHub Container Registry as cache source — unchanged layers (dependencies, base image) reuse cache, reducing build time from 5+ minutes to under 1 minute.
>
> **Anti-Patterns:**
> - `AP-S8.15a` — `COPY . .` placed before the dependency install step — every source change invalidates the dependency layer, so no build ever reuses a cache however it is configured.

> **S8.16** — Angular stack CI deploy is orchestrated: (1) trigger Railway FastAPI deploy and wait for health check, (2) only if FastAPI succeeds, trigger Vercel Angular deploy. FastAPI deploy failure skips Angular deploy — per S6.29.
>
> **Anti-Patterns:**
> - `AP-S8.16a` — Frontend and API deployed in parallel — a frontend that ships while its API deploy is failing serves a version of the application whose backend does not exist.

---

## Part 3 — Docker & Local Development (`S8.17`–`S8.23`)

---

### S8.17 — `docker-compose up` — Full Stack in One Command

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S8.17 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | — |
| **Enforced By** | New developer onboarding check |

**Standard:**
Every system runs locally with `docker-compose up` as a single command. The `docker-compose.yml` includes all services: application server, PostgreSQL, MongoDB (Angular stack), Redis (where used), ChromaDB (FundsLink). A developer who clones the repository and runs `docker-compose up` has a working development environment without additional manual configuration steps.

**Anti-Patterns:**
- `AP-S8.17a` — "Run PostgreSQL manually on port 5432, start Redis separately, then run `npm run dev`" — multiple manual steps create setup inconsistency and block new contributors.

**Cross-References:** `S8.21` (database containers in Docker Compose), `S7.39` (test database via Docker)

---

### S8.18–S8.23 — Docker Standards

> **S8.18** — Docker images use specific version tags — never `latest`. `node:20.11-alpine`, `python:3.12-slim`. `latest` produces non-reproducible builds.
>
> **Anti-Patterns:**
> - `AP-S8.18a` — Docker images using `latest` — the same Dockerfile produces a different image on a different day, so a build that passes CI and the build that reaches production are not demonstrably the same artefact.

> **S8.19** — Multi-stage Docker builds for production images: `build` stage (dependencies + compilation), `production` stage (runtime only — no build tools, no dev dependencies). Production image size target: under 200MB.
>
> **Anti-Patterns:**
> - `AP-S8.19a` — Compilers, package managers and dev dependencies shipped in the production image — every one is an exploit primitive available to anyone who reaches the container, and none of them is needed to run the application.

> **S8.20** — `.dockerignore` excludes: `node_modules/`, `.git/`, `.env*`, test files, `__pycache__/`, coverage reports. Build context must be minimal.
>
> **Anti-Patterns:**
> - `AP-S8.20a` — A build context that includes `.git/` or an environment file — the secret is then baked into an image layer, where deleting it in a later layer does not remove it and anyone who pulls the image can read it.

> **S8.21** — Docker Compose PostgreSQL container uses a named volume for data persistence across `docker-compose down` calls. Test database uses a separate, ephemeral volume.
>
> **Anti-Patterns:**
> - `AP-S8.21a` — An anonymous volume for PostgreSQL data — `docker-compose down` discards the developer's database, and the loss looks like a bug in the application rather than a missing volume name.

> **S8.22** — Health checks defined for all Docker Compose services — dependent services wait for health check success before starting. No `depends_on` without a `condition: service_healthy`.
>
> **Anti-Patterns:**
> - `AP-S8.22a` — `depends_on` with no `condition: service_healthy` — the dependant starts when the container *exists*, not when the service answers, so the stack fails on a cold start and succeeds on a warm one.

> **S8.23** — Hot reload enabled in Docker Compose development configuration: `volumes: ['.:/app']` with `command: uvicorn app.main:app --reload` (FastAPI) or `next dev` (Next.js).
>
> **Anti-Patterns:**
> - `AP-S8.23a` — A development compose file that requires an image rebuild to observe a source change — the edit-run loop lengthens until developers stop using the container and test against something production does not resemble.

---

## Part 4 — Environment & Configuration Governance (`S8.24`–`S8.30`)

---

### S8.24 — Three Environments — Development, Staging, Production

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S8.24 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S8.5` |
| **Enforced By** | Environment configuration audit |

**Standard:**
Every system has three isolated environments with separate databases, secrets, and URLs. Development: local Docker Compose, developer machine. Staging: cloud-deployed from main, mirrors production configuration. Production: manually promoted from staging. No shared infrastructure between environments.

**Anti-Patterns:**
- `AP-S8.24a` — Staging and production sharing the same PostgreSQL database — a staging test that corrupts data corrupts production data.

**Cross-References:** `S8.5`, `S8.39` (environment variables per environment)

---

### S8.25–S8.30 — Environment Configuration Standards

> **S8.25** — `.env.example` is committed to version control with all required variable names and descriptions but no values. `.env` is in `.gitignore` and never committed.
>
> **Anti-Patterns:**
> - `AP-S8.25a` — An example environment file carrying real values — it is committed precisely because it looks like documentation, which is what makes it the least examined place a credential can sit.

> **S8.26** — Environment variables are validated at application startup using Zod (TypeScript) or Pydantic Settings (Python). Application refuses to start if required variables are missing or invalid.
>
> **Anti-Patterns:**
> - `AP-S8.26a` — An application that starts with a required variable missing and fails later at the point of use — the failure surfaces as a request error in production rather than as a refusal to boot in staging.

> **S8.27** — Production secrets are stored in Vercel Environment Variables (Next.js/Angular frontend) and Railway Secrets (FastAPI). Never in application code, never in git history.
>
> **Anti-Patterns:**
> - `AP-S8.27a` — A production secret committed to version control — history cannot be effectively rewritten, so the repository must be treated as permanently compromised and the credential rotated rather than deleted.

> **S8.28** — Database URLs use connection string format with password URL-encoded. PgBouncer connection pooler URL for production PostgreSQL (Railway). Direct URL for migrations only.
>
> **Anti-Patterns:**
> - `AP-S8.28a` — Application traffic pointed at the direct database URL instead of the pooler — connections are exhausted under ordinary load, and the outage reads as a database capacity problem rather than a configuration one.

> **S8.29** — Feature flags stored in the `FeatureFlag` PostgreSQL table — not in environment variables. Environment variables govern infrastructure behaviour; feature flags govern application behaviour.
>
> **Anti-Patterns:**
> - `AP-S8.29a` — A feature flag held in an environment variable — turning a feature off then requires a redeploy, which is the one thing a flag exists to avoid during an incident.

> **S8.30** — All environment variables are documented in the system context file with their purpose and the service that consumes them. A new environment variable without documentation is a code review block.
>
> **Anti-Patterns:**
> - `AP-S8.30a` — An environment variable introduced without documenting what consumes it — nobody can later determine whether it is still read, so it is never removed and never safely changed.

---

## Part 5 — Monitoring & Observability (`S8.31`–`S8.40`)

---

### S8.31 — Structured JSON Logging — Mandatory Fields on Every Log Entry

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S8.31 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S2.56` (C2 observability standards) |
| **Enforced By** | Log format linter in CI |

**Standard:**
Every log entry is structured JSON with mandatory fields: `timestamp` (ISO 8601), `level` (DEBUG/INFO/WARN/ERROR), `service` (application name), `request_id` (X-Request-ID for correlation), `message`, and `context` (JSONB — additional structured data relevant to the event). Plain text logs are forbidden in production.

**Rationale:**
Structured logs can be queried, filtered, and correlated programmatically. Plain text logs require regex parsing to extract any information, making observability tooling ineffective.

**Anti-Patterns:**
- `AP-S8.31a` — `console.log("User logged in:", userId)` — unstructured log that cannot be correlated, filtered, or queried efficiently.

**Cross-References:** `S2.56` (backend observability), `S2.60` (X-Request-ID propagation)

---

### S8.32 — Sentry for Error Tracking — Both Frontend and Backend

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S8.32 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S4.65` (frontend Sentry), `S2.57` (backend Sentry) |
| **Enforced By** | Sentry project verification |

**Standard:**
Sentry is initialised in every frontend and backend application with: DSN from environment variable, environment tag, release version from build metadata, and user context on authentication. Every unhandled exception reaches Sentry. Sentry alerts are configured for new issue types and error rate spikes.

**Anti-Patterns:**
- `AP-S8.32a` — Sentry initialised without user context — errors arrive with no way to identify affected users or correlate frontend and backend errors from the same session.

**Cross-References:** `S4.65` (frontend Sentry), `S2.57` (backend Sentry), `S8.55` (Sentry alerts)

---

### S8.33–S8.40 — Additional Observability Standards

> **S8.33** — Better Stack monitors the `/health` endpoint of every production service every 60 seconds. Three consecutive health check failures trigger a SEV0 alert to the incident commander.
>
> **Anti-Patterns:**
> - `AP-S8.33a` — An outage first reported by a user — monitoring that nobody configured is indistinguishable from monitoring that is passing, and the difference is only ever discovered during an incident.

> **S8.34** — `/health` endpoint returns: `{ status: "ok"|"degraded", database: "connected"|"error", version: "...", uptime: seconds }`. A degraded database triggers the SEV0 alert even if the application is running.
>
> **Anti-Patterns:**
> - `AP-S8.34a` — A `/health` endpoint that returns `200` without checking its dependencies — it reports the web server is up, which was never in question, while the database it needs is unreachable.

> **S8.35** — Alert thresholds: error rate >1% on any endpoint → SEV1 evaluation. p95 latency >500ms → warning. p95 latency >2s on critical endpoints sustained 5 minutes → SEV2. Memory above 90% for 5 minutes → SEV1. CPU above 85% for 5 minutes → SEV2.
>
> **Anti-Patterns:**
> - `AP-S8.35a` — Thresholds set where they will never fire — an alert calibrated to avoid waking anyone is an alert that will not wake anyone during the outage it exists for.

> **S8.36** — Railway Metrics alerts for Angular stack: FastAPI CPU, memory, and database connection pool utilisation — per threshold table in S8.35.
>
> **Anti-Patterns:**
> - `AP-S8.36a` — Connection-pool utilisation unmonitored — pool exhaustion presents as slow requests rather than errors, so it is diagnosed as a database capacity problem and answered by scaling the wrong thing.

> **S8.37** — Vercel Analytics enabled on all Next.js and Angular frontends — Core Web Vitals (LCP, CLS, FID) tracked per deployment.
>
> **Anti-Patterns:**
> - `AP-S8.37a` — Front-end performance measured only on a developer's machine — a fast laptop on a fast network is the one environment in which the regression cannot be observed.

> **S8.38** — Alert delivery chain is tested monthly: SEV0/SEV1 alerts via email AND WhatsApp to Maluleke Kurhula Success. SEV2 and below: email only, reviewed during working hours.
>
> **Anti-Patterns:**
> - `AP-S8.38a` — An alert route that has never delivered a test alert — a silent channel and a quiet month look identical, and which one it was is learned from the incident.

> **S8.39** — Log retention: ERROR level logs retained 90 days. INFO level logs retained 30 days. DEBUG level logs not stored in production.
>
> **Anti-Patterns:**
> - `AP-S8.39a` — Retention shorter than the time it takes to notice the problem — the post-mortem opens with the evidence already expired, so the cause is inferred rather than established.

> **S8.40** — Dashboard: Better Stack creates a status page per system showing uptime, incident history, and current status. URL is public and linked from the system's README.
>
> **Anti-Patterns:**
> - `AP-S8.40a` — No public status page — every affected user contacts support individually to ask the same question, during the window when there is least capacity to answer it.

---

## Part 6 — Security & Secrets (`S8.41`–`S8.46`)

> **S8.41** — Secret scanning enabled on all repositories via GitHub Advanced Security — any accidental commit of secrets is detected and alerts the owner immediately.
>
> **Anti-Patterns:**
> - `AP-S8.41a` — Secret scanning left disabled — a committed credential is then found by whoever is looking for one, and the repository's history cannot be rewritten to take it back.

> **S8.42** — Dependencies scanned with `npm audit` (TypeScript) and `safety` (Python) in CI — known vulnerabilities block merge.
>
> **Anti-Patterns:**
> - `AP-S8.42a` — A dependency scan that runs only on change — the advisory database moves without this repository moving, so an untouched project is reported clean for as long as nobody touches it.

> **S8.43** — Docker images scanned for vulnerabilities in CI before push to registry.
>
> **Anti-Patterns:**
> - `AP-S8.43a` — Images scanned after they are pushed, or not at all — the vulnerable artefact is already in the registry and already pullable while the finding is being triaged.

> **S8.44** — All production secrets rotated at minimum quarterly — documented rotation schedule in the system context file.
>
> **Anti-Patterns:**
> - `AP-S8.44a` — A credential that has never been rotated — its blast radius is every person who has held it since it was issued, and nobody can now enumerate that list.

> **S8.45** — SSH access to Railway and Vercel uses organisation SSO — no personal access tokens with admin scope committed anywhere.
>
> **Anti-Patterns:**
> - `AP-S8.45a` — An admin-scoped personal access token used for automation — it outlives the person's access, cannot be revoked by removing them from the organisation, and is attributed to them long after they have left.

> **S8.46** — Production database access is through the application only — no direct developer access to production PostgreSQL in normal operations. Emergency access requires documented justification and is audited.
>
> **Anti-Patterns:**
> - `AP-S8.46a` — Routine direct access to the production database — every constraint, audit trail and validation the application enforces is bypassed, and the write that caused the incident has no record of who made it.

---

## Part 7 — Severity Framework (`S8.47`–`S8.54`)

---

### S8.47 — Severity Classification — Four Levels

| Severity | Definition | Response SLA | Resolution SLA | Communication |
|----------|-----------|--------------|----------------|---------------|
| **SEV0** | Complete platform outage, data loss, auth system down, financial transaction failure (Reserve Bank) | 15 minutes | 2 hours | Immediate — public + user |
| **SEV1** | Major feature failure >50% users, AI matching down (FundsLink), payment endpoint failing, database degraded | 30 minutes | 4 hours | Status page update |
| **SEV2** | Partial feature degradation, performance >500ms p95, RAG pipeline slow, non-critical background jobs failing | 2 hours | 24 hours | Internal only |
| **SEV3** | Minor issue, no user impact, UI cosmetic bug, slow background job, documentation drift | Next sprint | 1 week | GitHub Issue only |

**Anti-Patterns:**
- `AP-S8.47a` — An incident whose severity is assigned after the response rather than before it — the classification then describes how the response went instead of governing it, and every incident is retroactively the severity that makes the SLA look met.

---

### S8.48 — Every Incident Classified Within 5 Minutes of Detection

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S8.48 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S8.47` (severity definitions) |
| **Enforced By** | Incident response protocol |

**Standard:**
The first action on detecting any production issue is severity classification within 5 minutes. Classification determines the response SLA, incident commander, and communication requirements. When uncertain between two levels, classify at the higher severity — it can be downgraded with more information.

**Anti-Patterns:**
- `AP-S8.48a` — Investigating without classifying first — unclassified incidents have no response SLA, no incident commander, and no communication requirements; they are invisible to the rest of the process.

**Cross-References:** `S8.47` (severity definitions), `S8.60` (incident commander assignment)

---

### S8.49–S8.54 — Additional Severity Standards

> **S8.49** — SEV0 response priority: (1) restore service first — rollback, failover, hotfix, whatever works fastest. (2) Document what was done. (3) Investigate root cause after service is restored. Never delay a rollback to investigate.
>
> **Anti-Patterns:**
> - `AP-S8.49a` — Diagnosis attempted before service is restored — the outage is extended by exactly the length of the investigation, and the evidence being gathered survives the rollback anyway.

> **S8.50** — Reserve Bank financial incidents are automatically SEV0 regardless of user impact scale: any incident involving incorrect balances, failed deposits, interest miscalculation, or transaction duplication. `DEPOSITS_ENABLED` and `WITHDRAWALS_ENABLED` feature flags set to `false` as the first action. No financial operations resume until data integrity is verified.
>
> **Anti-Patterns:**
> - `AP-S8.50a` — A balance discrepancy triaged by how many users it touched — money incidents compound while they are being sized, and one wrong balance is evidence the mechanism is wrong for all of them.

> **S8.51** — FundsLink AI incidents: when LangChain/ChromaDB AI matching fails, the circuit breaker triggers (S2.47) and users see a static "AI matching temporarily unavailable — apply manually" screen. This is SEV2, not SEV0.
>
> **Anti-Patterns:**
> - `AP-S8.51a` — An AI-tier failure that blocks the manual path behind it — a degraded optional feature is escalated into a full outage by a fallback that was never built.

> **S8.52** — SEV0 and SEV1 incidents: GitHub Issue opened within 10 minutes, tagged `incident` and `sev0`/`sev1`. Issue title format: `[SEV0] Platform outage — auth service down`.
>
> **Anti-Patterns:**
> - `AP-S8.52a` — An incident coordinated entirely in chat — there is no artefact to hand to the post-mortem, and the timeline has to be reconstructed from memory by the people least able to recall it accurately.

> **S8.53** — Incident Commander assigned within 15 minutes for SEV0/SEV1 — single point of coordination who makes all decisions and owns communication. Not necessarily the technical responder.
>
> **Anti-Patterns:**
> - `AP-S8.53a` — No named commander — the person best placed to fix the problem is also answering status questions, so both jobs are done badly and neither has an owner.

> **S8.54** — Incident status updates every 30 minutes during active SEV0/SEV1 on the GitHub Issue. "Still investigating" is acceptable — silence is not.
>
> **Anti-Patterns:**
> - `AP-S8.54a` — Silence held until there is something conclusive to report — stakeholders read no news as no progress and begin interrupting the responders to ask, which is the cost the update exists to avoid.

---

## Part 8 — Detection & Alerting (`S8.55`–`S8.60`)

> **S8.55** — Sentry error rate alert: >1% error rate on any endpoint over a 5-minute window triggers SEV1 evaluation. New unique issue on auth, financial, or data integrity path triggers SEV1 immediately.
>
> **Anti-Patterns:**
> - `AP-S8.55a` — Error alerting on volume alone — a *new* fault on an auth or money path is severe on its first occurrence, and a rate threshold cannot fire until it has already happened repeatedly.

> **S8.56** — Better Stack: three consecutive `/health` failures → SEV0 alert to incident commander. Next.js: monitors `Vercel URL/api/health`. FastAPI: monitors `Railway URL/health`.
>
> **Anti-Patterns:**
> - `AP-S8.56a` — Alerting on a single failed check — one timeout is noise, and a channel that cries wolf is muted long before the outage it was meant to catch.

> **S8.57** — Railway metrics: CPU >85% for 5 minutes → SEV2 alert. Memory >90% for 5 minutes → SEV1 alert (memory leak). DB connection pool >80% → SEV2 warning. Service restart detected → SEV1 alert.
>
> **Anti-Patterns:**
> - `AP-S8.57a` — Silent restarts — a process that crashes and is restarted by the platform looks healthy from outside, so a crash loop is observed only as intermittent errors nobody can reproduce.

> **S8.58** — Vercel deploy failures on main branch trigger immediate GitHub notification and email. Treated as SEV2 — previous deployment remains live.
>
> **Anti-Patterns:**
> - `AP-S8.58a` — A failed deploy that notifies nobody — because the previous deployment is still serving, the failure is invisible, and the next several merges pile up behind a pipeline everyone believes is green.

> **S8.59** — Latency degradation: p95 >2s on any critical endpoint sustained 5 minutes → SEV2. Financial endpoints: p95 >1s → SEV2.
>
> **Anti-Patterns:**
> - `AP-S8.59a` — Latency judged on the mean — the average hides the tail entirely, and the tail is the set of users actually experiencing the outage.

> **S8.60** — SEV0/SEV1 alerts delivered via email AND WhatsApp to Maluleke Kurhula Success 24/7. Alert delivery chain tested monthly.
>
> **Anti-Patterns:**
> - `AP-S8.60a` — A single delivery channel for SEV0 — the one failure mode that matters is the channel itself being down, and email alone cannot report that it did not arrive.

---

## Part 9 — Response Runbooks (`S8.61`–`S8.66`)

Response runbooks are the step-by-step execution guides for common incident types. They live in `runbooks/` as standalone files. Standards here govern their existence and maintenance.

> **S8.61** — A runbook exists for every SEV0 and SEV1 scenario identified in the Common Failure Register (C0 §13). Runbooks are in `runbooks/` and referenced from the GitHub incident issue.
>
> **Anti-Patterns:**
> - `AP-S8.61a` — A known failure mode with no runbook — it was foreseeable enough to register and will still be improvised, by whoever is on call, at the hour it happens.

> **S8.62** — Runbook format: Title, Severity, Trigger condition, First 5 actions (numbered, executable without thinking), Escalation path, Resolution criteria, Post-mortem trigger.
>
> **Anti-Patterns:**
> - `AP-S8.62a` — A runbook written as prose rather than numbered actions — it has to be *comprehended* before it can be followed, at the moment its reader is least able to comprehend anything.

> **S8.63** — Runbooks are tested in staging quarterly — a test incident is simulated, the runbook is followed, and gaps are corrected. An untested runbook is an unreliable runbook.
>
> **Anti-Patterns:**
> - `AP-S8.63a` — A runbook whose commands nobody has run — it drifts silently as the system changes, and its first execution is the incident it was written for.

> **S8.64** — `runbooks/SEV0-response-runbook.md` is the first-read document at the start of every SEV0. It is the generic template. System-specific runbooks (financial-freeze, ai-degradation) extend it.
>
> **Anti-Patterns:**
> - `AP-S8.64a` — No single entry point for a SEV0 — the first minutes are spent deciding which document applies, which is the one decision nobody should be making under pressure.

> **S8.65** — Runbook execution is logged in the GitHub incident issue: each step completed is checked off with a timestamp. This produces a timeline for the post-mortem.
>
> **Anti-Patterns:**
> - `AP-S8.65a` — Steps performed without being recorded — a second responder cannot tell what has already been tried, and repeats it.

> **S8.66** — New runbooks are created within one sprint of any incident where the responder had to improvise. The improvised solution becomes the documented runbook.
>
> **Anti-Patterns:**
> - `AP-S8.66a` — An improvised recovery never written down — the same incident costs the same improvisation next time, and the knowledge leaves with the person who happened to be on call.

---

## Part 10 — Rollback Procedures (`S8.67`–`S8.72`)

> **S8.67** — Every production deployment must be rollbackable within 5 minutes. Rollback capability is tested as part of quarterly staging exercises.
>
> **Anti-Patterns:**
> - `AP-S8.67a` — A deployment with no rollback path — the only remaining recovery is a forward fix written under incident pressure, which is the worst condition in which to write anything.

> **S8.68** — Next.js rollback: Vercel dashboard one-click rollback to previous deployment — instant, zero downtime.
>
> **Anti-Patterns:**
> - `AP-S8.68a` — Reverting the commit and redeploying instead of rolling back — a full build and deploy cycle is spent reaching a state that was already sitting there ready to serve.

> **S8.69** — FastAPI rollback: Railway dashboard redeploy previous build. If the deployment introduced a schema migration, follow `runbooks/database-migration-runbook.md` for the migration rollback sequence.
>
> **Anti-Patterns:**
> - `AP-S8.69a` — Application code rolled back while its migration stays applied — the old code meets a schema it was never written against, so the rollback produces a second, less familiar outage.

> **S8.70** — Database migration rollback: never run a destructive migration in production without first testing the rollback in staging. `prisma migrate resolve --rolled-back <migration_name>` for failed migrations. Column deletion is never part of a same-deployment migration (S5.61).
>
> **Anti-Patterns:**
> - `AP-S8.70a` — A destructive migration whose rollback has never been rehearsed — dropping a column is not reversible by re-running anything, and the data it held is gone before anyone establishes whether it was needed.

> **S8.71** — Rollback triggers: Sentry error rate spike >5% within 5 minutes of deploy. p95 latency >3x baseline within 5 minutes of deploy. Any SEV0/SEV1 detected within 15 minutes of deploy.
>
> **Anti-Patterns:**
> - `AP-S8.71a` — Rollback left to judgement in the moment — without a pre-agreed trigger the decision becomes a negotiation about whether the deploy is really at fault, and it is had while users are affected.

> **S8.72** — Post-rollback: the deployment is not re-attempted until the root cause is identified and fixed. A "roll forward" (fix deployed immediately after rollback) follows the same CI/staging/production pipeline as any deployment.
>
> **Anti-Patterns:**
> - `AP-S8.72a` — The same deployment retried in the hope the failure was transient — it reproduces the outage deliberately, and a fix rushed straight to production bypasses the pipeline that would have caught it.

---

## Part 11 — Incident Communication (`S8.73`–`S8.76`)

> **S8.73** — SEV0 public communication: Better Stack status page updated within 15 minutes of incident declaration. Message format: "We are experiencing [impact description]. Our team is actively investigating. Next update in 30 minutes."
>
> **Anti-Patterns:**
> - `AP-S8.73a` — A public outage with no public acknowledgement — users conclude the problem is theirs and start changing their own configuration, which makes their situation worse and the support load larger.

> **S8.74** — SEV1 communication: Status page updated, internal team notified. No public communication until impact is confirmed.
>
> **Anti-Patterns:**
> - `AP-S8.74a` — Announcing an impact before it is confirmed — a retracted outage notice costs more credibility than the outage did, and the next real notice is believed less.

> **S8.75** — Resolution communication: "The issue has been resolved. [One sentence: what happened and what was fixed]. Post-mortem will be published within 5 business days."
>
> **Anti-Patterns:**
> - `AP-S8.75a` — An incident closed without a resolution notice — the last thing users were told is that something was broken, so as far as they know it still is.

> **S8.76** — Never speculate publicly about root cause during an active incident. Communicate what is known — impact, affected systems, next update time — not what is suspected.
>
> **Anti-Patterns:**
> - `AP-S8.76a` — A cause named publicly before it is established — the correction is read as an evasion, and every subsequent statement in the same incident is discounted.

---

## Part 12 — Post-Mortem Protocol (`S8.77`–`S8.82`)

---

### S8.77 — Post-Mortem Required for All SEV0 and SEV1 Incidents

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S8.77 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S8.47` (severity framework) |
| **Enforced By** | Incident Commander checklist |

**Standard:**
Every SEV0 and SEV1 incident produces a post-mortem document using `templates/post-mortem-template.md`. Post-mortem is completed within 5 business days of resolution. Post-mortem is blameless — the goal is system improvement, not individual fault.

**Anti-Patterns:**
- `AP-S8.77a` — No post-mortem after a SEV0 — the incident recurs without the systemic changes that would have prevented it.

**Cross-References:** `templates/post-mortem-template.md`, `C0 §12` (review calendar — post-mortem review trigger)

---

### S8.78–S8.82 — Post-Mortem Standards

> **S8.78** — Post-mortem document fields: title, severity, date/time of detection, date/time of resolution, total duration, incident commander, systems affected, impact summary, timeline (minute-by-minute from detection to resolution), root cause analysis (5 Whys), contributing factors, what went well, action items (each with owner and due date).
>
> **Anti-Patterns:**
> - `AP-S8.78a` — A post-mortem naming a person as the root cause — it stops the analysis one level above the system that let a single mistake reach production, which is the level where the fix actually is.

> **S8.79** — Action items from post-mortems are GitHub Issues with the `post-mortem-action` label — tracked in the sprint, not deferred indefinitely.
>
> **Anti-Patterns:**
> - `AP-S8.79a` — Action items that live only in the post-mortem document — nothing scheduled is nothing done, and the same incident recurs with its own remedy already written down.

> **S8.80** — Every post-mortem adds at least one entry to C0 Common Failure Register (§13) — the register grows with every incident.
>
> **Anti-Patterns:**
> - `AP-S8.80a` — An incident that teaches the register nothing — the organisation learns per-incident instead of cumulatively, so the next system repeats a failure the last one already paid for.

> **S8.81** — Post-mortems are published internally to the team — not kept private by the incident commander. Shared knowledge prevents recurrence across systems.
>
> **Anti-Patterns:**
> - `AP-S8.81a` — A post-mortem kept private — the lesson stays with the one person who least needs it, and treating incidents as embarrassing is what makes the next one slower to report.

> **S8.82** — Quarterly review includes a review of all post-mortem action items — items that are overdue are escalated. An action item that was never addressed is a systemic risk.
>
> **Anti-Patterns:**
> - `AP-S8.82a` — Action items never reviewed after the sprint they were filed in — the backlog becomes a record of accepted risk that nobody has agreed to accept.

---

## Part — External-Surface & Brownfield Reliability (`S8.83`–`S8.87`)

> **S8.83** — Every brownfield conversion step is individually reversible with a ready rollback path. A step that cannot be rolled back is not a step — it is a risk. Pairs with `protocols/brownfield-adoption.md`.
>
> **Anti-Patterns:**
> - `AP-S8.83a` — Shipping a non-reversible conversion step with no rollback prepared — on first contact with somebody else's repository, an unrecoverable step is the one that ends the adoption.

> **S8.84** — Dependency installs run behind a committed lockfile and a CI vulnerability (SCA) gate; SEV0/SEV1 dependency CVEs **block merge** (deterministic detection — hard block allowed). Pairs with `protocols/external-governance.md` §2.
>
> **Anti-Patterns:**
> - `AP-S8.84a` — Merging with a known SEV0/SEV1 dependency CVE, or with no SCA gate at all — a gate-shaped log line reports "clean" for every advisory it never heard of.

> **S8.85** — Every dependency's license is checked against an allowlist; unknown/copyleft licenses require a recorded L4 exception. An SBOM is generated for releases.
>
> **Anti-Patterns:**
> - `AP-S8.85a` — Shipping a dependency with an unvetted licence or no SBOM — the obligation is discovered by the counterparty's legal review, at the point where the cost of complying is highest.

> **S8.86** — Every critical external vendor has a register entry (what it does, what data it holds, its SLA) and a documented exit/portability plan. Undocumented lock-in requires an L4-acknowledged contingency.
>
> **Anti-Patterns:**
> - `AP-S8.86a` — Depending on a critical vendor with no exit plan — the plan is then written during the vendor's outage, price change, or discontinuation, which is when it is least possible to write.

> **S8.87** — The external surface is under continuous temporal governance: framework changelogs, CVE/advisory databases, and dependency releases are monitored; items past their review window are flagged `TEMPORAL-ALERT` / `UNVALIDATED`.
>
> **Anti-Patterns:**
> - `AP-S8.87a` — Treating dependency currency as a one-time check — the dependency surface decays without the repository changing, so a build that was green in July is wrong in August with nothing committed in between.

---

## Anti-Patterns Index

| ID | Description | Violated Standard | Severity |
|----|-------------|-------------------|----------|
| `AP-S8.1a` | Next.js deployed to Railway or custom Docker | S8.1 | High |
| `AP-S8.2a` | FastAPI deployed to Vercel serverless | S8.2 | Critical |
| `AP-S8.9a` | Manual deploys to staging by pushing to deploy branch | S8.9 | High |
| `AP-S8.10a` | Sequential CI steps when parallel is possible | S8.10 | Standard |
| `AP-S8.11a` | Manual staging deploy bypassing CI | S8.11 | High |
| `AP-S8.12a` | Automatic production deploy on main merge | S8.12 | Critical |
| `AP-S8.17a` | Multiple manual setup steps for local development | S8.17 | Standard |
| `AP-S8.18a` | Docker images using `latest` tag | S8.18 | High |
| `AP-S8.24a` | Staging and production sharing same database | S8.24 | Critical |
| `AP-S8.31a` | Unstructured plain-text logs in production | S8.31 | High |
| `AP-S8.32a` | Sentry without user context | S8.32 | High |
| `AP-S8.48a` | Investigating without classifying severity | S8.48 | High |
| `AP-S8.77a` | No post-mortem after SEV0 | S8.77 | Critical |

---

## Cross-Constitution Dependency Map

**This constitution depends on:**
| Dependency | Reason |
|------------|--------|
| `C0 — Constitutional Order` | Amendment protocol, Common Failure Register, review calendar |
| `C2 — Backend Constitution` | Deployment standards for backend services, observability (S2.56–S2.62) |
| `C5 — Database Constitution` | Migration governance in deployment pipeline (S5.59) |
| `C6 — Full-Stack Architecture` | Deployment coordination (S6.29), platform topology |
| `C7 — Testing Constitution` | CI gate: all tests must pass before production deploy |

**The following constitutions depend on this one:**
| Dependent | Reason |
|-----------|--------|
| `C9 — Product & Feature` | MVP "done" criteria includes production deployment |
| `C10 — AI Collaboration` | Incident response is an AI permission boundary |

---

## Amendment Log

| Version | Date | Change | Reason |
|---------|------|--------|--------|
| v1.0 | 2026-05-08 | Initial lock — rebuilt from Infrastructure Constitution v3.0 + Incident Response Constitution v3.0. Both documents merged into one Platform Reliability Constitution. Observability standards consolidated from Backend B41–B46 and Infrastructure I31–I38 into Part 5. All runbooks extracted to `runbooks/` folder. Severity framework aligned with backend circuit breaker and financial freeze standards. Structured JSON log format formalised in S8.31. | Full system rebuild — two documents merged into one authoritative source. |
| v1.1 | 2026-06-21 | **Added S8.83–S8.87 — External-Surface & Brownfield Reliability:** S8.83 per-step reversibility in brownfield conversion; S8.84 lockfile + CI CVE gate; S8.85 license allowlist + SBOM; S8.86 vendor register + exit plan; S8.87 continuous temporal governance. Anti-patterns AP-S8.83a–AP-S8.87a added. Count 82→87. (C0 §8 amendment; brownfield + external/ecosystem governance; Founder L4 approval 2026-06-21.) | Supply-chain CVEs, undocumented vendor lock-in, rotting dependencies, and non-reversible conversion steps are leading reliability/security failure modes; each is now a governed reliability standard. |

---

> **LOCKED — v1.1 — 2026-06-21** (amended; originally locked v1.0 2026-05-08)
>
> This document is locked. No standard may be added, removed, or modified
> without following the Amendment Protocol defined in C0 §8.
> Amendments take effect only after commit to `governova`
> with a version bump and amendment log entry.
