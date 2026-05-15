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

**Cross-References:** `S8.2` (Railway), `S6.29` (deploy order)

---

### S8.4–S8.8 — Additional Platform Standards

> **S8.4** — Preview deployments are generated for every PR on both stacks. Next.js: Vercel preview URL. Angular: Vercel preview URL for frontend + Railway staging for API PRs. E2E tests run against preview deployments.

> **S8.5** — Three environments — Development (local Docker Compose), Staging (auto-deployed from main merge), Production (manually promoted from staging). Code never goes directly from development to production.

> **S8.6** — Zero-downtime deploys on all production deployments. Vercel: atomic deployment with instant rollover. Railway: rolling restart with minimum 1 healthy replica before killing old container.

> **S8.7** — Production deployment rollback available in under 5 minutes via one action. Vercel: one-click rollback to previous deployment. Railway: redeploy previous build. Rollback procedures are tested in staging quarterly.

> **S8.8** — ChromaDB on Railway as a separate service with persistent volume. No public port exposed — FastAPI accesses ChromaDB via Railway internal networking only (FundsLink).

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

> **S8.14** — Prisma migrations validated in CI: `prisma migrate diff` runs on every PR that changes `schema.prisma`. Detects missing migration files before merge.

> **S8.15** — Build artefacts use Docker layer caching with GitHub Container Registry as cache source — unchanged layers (dependencies, base image) reuse cache, reducing build time from 5+ minutes to under 1 minute.

> **S8.16** — Angular stack CI deploy is orchestrated: (1) trigger Railway FastAPI deploy and wait for health check, (2) only if FastAPI succeeds, trigger Vercel Angular deploy. FastAPI deploy failure skips Angular deploy — per S6.29.

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

> **S8.19** — Multi-stage Docker builds for production images: `build` stage (dependencies + compilation), `production` stage (runtime only — no build tools, no dev dependencies). Production image size target: under 200MB.

> **S8.20** — `.dockerignore` excludes: `node_modules/`, `.git/`, `.env*`, test files, `__pycache__/`, coverage reports. Build context must be minimal.

> **S8.21** — Docker Compose PostgreSQL container uses a named volume for data persistence across `docker-compose down` calls. Test database uses a separate, ephemeral volume.

> **S8.22** — Health checks defined for all Docker Compose services — dependent services wait for health check success before starting. No `depends_on` without a `condition: service_healthy`.

> **S8.23** — Hot reload enabled in Docker Compose development configuration: `volumes: ['.:/app']` with `command: uvicorn app.main:app --reload` (FastAPI) or `next dev` (Next.js).

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

> **S8.26** — Environment variables are validated at application startup using Zod (TypeScript) or Pydantic Settings (Python). Application refuses to start if required variables are missing or invalid.

> **S8.27** — Production secrets are stored in Vercel Environment Variables (Next.js/Angular frontend) and Railway Secrets (FastAPI). Never in application code, never in git history.

> **S8.28** — Database URLs use connection string format with password URL-encoded. PgBouncer connection pooler URL for production PostgreSQL (Railway). Direct URL for migrations only.

> **S8.29** — Feature flags stored in the `FeatureFlag` PostgreSQL table — not in environment variables. Environment variables govern infrastructure behaviour; feature flags govern application behaviour.

> **S8.30** — All environment variables are documented in the system context file with their purpose and the service that consumes them. A new environment variable without documentation is a code review block.

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

> **S8.34** — `/health` endpoint returns: `{ status: "ok"|"degraded", database: "connected"|"error", version: "...", uptime: seconds }`. A degraded database triggers the SEV0 alert even if the application is running.

> **S8.35** — Alert thresholds: error rate >1% on any endpoint → SEV1 evaluation. p95 latency >500ms → warning. p95 latency >2s on critical endpoints sustained 5 minutes → SEV2. Memory above 90% for 5 minutes → SEV1. CPU above 85% for 5 minutes → SEV2.

> **S8.36** — Railway Metrics alerts for Angular stack: FastAPI CPU, memory, and database connection pool utilisation — per threshold table in S8.35.

> **S8.37** — Vercel Analytics enabled on all Next.js and Angular frontends — Core Web Vitals (LCP, CLS, FID) tracked per deployment.

> **S8.38** — Alert delivery chain is tested monthly: SEV0/SEV1 alerts via email AND WhatsApp to Maluleke Kurhula Success. SEV2 and below: email only, reviewed during working hours.

> **S8.39** — Log retention: ERROR level logs retained 90 days. INFO level logs retained 30 days. DEBUG level logs not stored in production.

> **S8.40** — Dashboard: Better Stack creates a status page per system showing uptime, incident history, and current status. URL is public and linked from the system's README.

---

## Part 6 — Security & Secrets (`S8.41`–`S8.46`)

> **S8.41** — Secret scanning enabled on all repositories via GitHub Advanced Security — any accidental commit of secrets is detected and alerts the owner immediately.

> **S8.42** — Dependencies scanned with `npm audit` (TypeScript) and `safety` (Python) in CI — known vulnerabilities block merge.

> **S8.43** — Docker images scanned for vulnerabilities in CI before push to registry.

> **S8.44** — All production secrets rotated at minimum quarterly — documented rotation schedule in the system context file.

> **S8.45** — SSH access to Railway and Vercel uses organisation SSO — no personal access tokens with admin scope committed anywhere.

> **S8.46** — Production database access is through the application only — no direct developer access to production PostgreSQL in normal operations. Emergency access requires documented justification and is audited.

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

> **S8.50** — Reserve Bank financial incidents are automatically SEV0 regardless of user impact scale: any incident involving incorrect balances, failed deposits, interest miscalculation, or transaction duplication. `DEPOSITS_ENABLED` and `WITHDRAWALS_ENABLED` feature flags set to `false` as the first action. No financial operations resume until data integrity is verified.

> **S8.51** — FundsLink AI incidents: when LangChain/ChromaDB AI matching fails, the circuit breaker triggers (S2.47) and users see a static "AI matching temporarily unavailable — apply manually" screen. This is SEV2, not SEV0.

> **S8.52** — SEV0 and SEV1 incidents: GitHub Issue opened within 10 minutes, tagged `incident` and `sev0`/`sev1`. Issue title format: `[SEV0] Platform outage — auth service down`.

> **S8.53** — Incident Commander assigned within 15 minutes for SEV0/SEV1 — single point of coordination who makes all decisions and owns communication. Not necessarily the technical responder.

> **S8.54** — Incident status updates every 30 minutes during active SEV0/SEV1 on the GitHub Issue. "Still investigating" is acceptable — silence is not.

---

## Part 8 — Detection & Alerting (`S8.55`–`S8.60`)

> **S8.55** — Sentry error rate alert: >1% error rate on any endpoint over a 5-minute window triggers SEV1 evaluation. New unique issue on auth, financial, or data integrity path triggers SEV1 immediately.

> **S8.56** — Better Stack: three consecutive `/health` failures → SEV0 alert to incident commander. Next.js: monitors `Vercel URL/api/health`. FastAPI: monitors `Railway URL/health`.

> **S8.57** — Railway metrics: CPU >85% for 5 minutes → SEV2 alert. Memory >90% for 5 minutes → SEV1 alert (memory leak). DB connection pool >80% → SEV2 warning. Service restart detected → SEV1 alert.

> **S8.58** — Vercel deploy failures on main branch trigger immediate GitHub notification and email. Treated as SEV2 — previous deployment remains live.

> **S8.59** — Latency degradation: p95 >2s on any critical endpoint sustained 5 minutes → SEV2. Financial endpoints: p95 >1s → SEV2.

> **S8.60** — SEV0/SEV1 alerts delivered via email AND WhatsApp to Maluleke Kurhula Success 24/7. Alert delivery chain tested monthly.

---

## Part 9 — Response Runbooks (`S8.61`–`S8.66`)

Response runbooks are the step-by-step execution guides for common incident types. They live in `runbooks/` as standalone files. Standards here govern their existence and maintenance.

> **S8.61** — A runbook exists for every SEV0 and SEV1 scenario identified in the Common Failure Register (C0 §13). Runbooks are in `runbooks/` and referenced from the GitHub incident issue.

> **S8.62** — Runbook format: Title, Severity, Trigger condition, First 5 actions (numbered, executable without thinking), Escalation path, Resolution criteria, Post-mortem trigger.

> **S8.63** — Runbooks are tested in staging quarterly — a test incident is simulated, the runbook is followed, and gaps are corrected. An untested runbook is an unreliable runbook.

> **S8.64** — `runbooks/SEV0-response-runbook.md` is the first-read document at the start of every SEV0. It is the generic template. System-specific runbooks (financial-freeze, ai-degradation) extend it.

> **S8.65** — Runbook execution is logged in the GitHub incident issue: each step completed is checked off with a timestamp. This produces a timeline for the post-mortem.

> **S8.66** — New runbooks are created within one sprint of any incident where the responder had to improvise. The improvised solution becomes the documented runbook.

---

## Part 10 — Rollback Procedures (`S8.67`–`S8.72`)

> **S8.67** — Every production deployment must be rollbackable within 5 minutes. Rollback capability is tested as part of quarterly staging exercises.

> **S8.68** — Next.js rollback: Vercel dashboard one-click rollback to previous deployment — instant, zero downtime.

> **S8.69** — FastAPI rollback: Railway dashboard redeploy previous build. If the deployment introduced a schema migration, follow `runbooks/database-migration-runbook.md` for the migration rollback sequence.

> **S8.70** — Database migration rollback: never run a destructive migration in production without first testing the rollback in staging. `prisma migrate resolve --rolled-back <migration_name>` for failed migrations. Column deletion is never part of a same-deployment migration (S5.61).

> **S8.71** — Rollback triggers: Sentry error rate spike >5% within 5 minutes of deploy. p95 latency >3x baseline within 5 minutes of deploy. Any SEV0/SEV1 detected within 15 minutes of deploy.

> **S8.72** — Post-rollback: the deployment is not re-attempted until the root cause is identified and fixed. A "roll forward" (fix deployed immediately after rollback) follows the same CI/staging/production pipeline as any deployment.

---

## Part 11 — Incident Communication (`S8.73`–`S8.76`)

> **S8.73** — SEV0 public communication: Better Stack status page updated within 15 minutes of incident declaration. Message format: "We are experiencing [impact description]. Our team is actively investigating. Next update in 30 minutes."

> **S8.74** — SEV1 communication: Status page updated, internal team notified. No public communication until impact is confirmed.

> **S8.75** — Resolution communication: "The issue has been resolved. [One sentence: what happened and what was fixed]. Post-mortem will be published within 5 business days."

> **S8.76** — Never speculate publicly about root cause during an active incident. Communicate what is known — impact, affected systems, next update time — not what is suspected.

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

> **S8.79** — Action items from post-mortems are GitHub Issues with the `post-mortem-action` label — tracked in the sprint, not deferred indefinitely.

> **S8.80** — Every post-mortem adds at least one entry to C0 Common Failure Register (§13) — the register grows with every incident.

> **S8.81** — Post-mortems are published internally to the team — not kept private by the incident commander. Shared knowledge prevents recurrence across systems.

> **S8.82** — Quarterly review includes a review of all post-mortem action items — items that are overdue are escalated. An action item that was never addressed is a systemic risk.

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

---

> **LOCKED — v1.0 — 2026-05-08**
>
> This document is locked. No standard may be added, removed, or modified
> without following the Amendment Protocol defined in C0 §8.
> Amendments take effect only after commit to `system-design-template`
> with a version bump and amendment log entry.
