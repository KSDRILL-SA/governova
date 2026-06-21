# C8 â€” Platform Reliability Constitution

---

| Attribute          | Value                                                              |
|--------------------|--------------------------------------------------------------------|
| **Document**       | C8 â€” Platform Reliability Constitution                             |
| **Organisation**   | KSDRILL SA                                                         |
| **Version**        | v1.0                                                               |
| **Status**         | LOCKED                                                             |
| **Locked**         | 2026-05-08                                                         |
| **Next Review**    | 2026-08-08                                                         |
| **Applies To**     | Both Stacks Â· All Systems                                          |
| **Paired With**    | â€” (Runbooks in `runbooks/` folder)                                 |

---

> *"Infrastructure that breaks silently is infrastructure that was never tested. When something breaks, the process is the product."*

---

## Opening Statement

The Platform Reliability Constitution governs everything between writing code and running it in production. It covers deployment platforms, CI/CD pipelines, environment governance, observability, incident response, rollback procedures, and post-mortem protocol. This constitution was formed by merging the Infrastructure Constitution and Incident Response Constitution â€” two documents that were always read together because deploying a system and responding to that system's failures are inseparable concerns.

This constitution does not govern how the application code is written â€” that is C2 through C5. It does not govern what features are built â€” that is C9. What this constitution governs is the operational layer: the machinery that gets code to users reliably, the detection layer that knows when something is wrong, the response protocol that minimises blast radius, and the learning process that prevents recurrence.

---

## Table of Contents

| Part | Title | Standards |
|------|-------|-----------|
| Part 1 | Deployment Platforms | S8.1â€“S8.8 |
| Part 2 | CI/CD Pipeline | S8.9â€“S8.16 |
| Part 3 | Docker & Local Development | S8.17â€“S8.23 |
| Part 4 | Environment & Configuration Governance | S8.24â€“S8.30 |
| Part 5 | Monitoring & Observability | S8.31â€“S8.40 |
| Part 6 | Security & Secrets | S8.41â€“S8.46 |
| Part 7 | Severity Framework | S8.47â€“S8.54 |
| Part 8 | Detection & Alerting | S8.55â€“S8.60 |
| Part 9 | Response Runbooks | S8.61â€“S8.66 |
| Part 10 | Rollback Procedures | S8.67â€“S8.72 |
| Part 11 | Incident Communication | S8.73â€“S8.76 |
| Part 12 | Post-Mortem Protocol | S8.77â€“S8.82 |
| Anti-Patterns Index | â€” | AP-S8.* |
| Cross-Constitution Dependency Map | â€” | â€” |
| Amendment Log | â€” | â€” |

---

## Part 1 â€” Deployment Platforms (`S8.1`â€“`S8.8`)

---

### S8.1 â€” Vercel for All Next.js Deployments â€” Unified Full-Stack

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S8.1 |
| **Priority**    | Critical |
| **Applies To**  | Next.js Only |
| **Phase**       | Phase 2 â€” Quality & Reliability |
| **Depends On**  | `S6.12` (Next.js topology) |
| **Enforced By** | Architecture Review |

**Standard:**
All Next.js systems (Maphophe, SyncUp) deploy to Vercel. Frontend, API routes, and edge functions are co-deployed in one Vercel project. Vercel handles automatic preview deployments for every PR, production deployment on main branch push, and environment variable management via the Vercel dashboard. No custom server configuration.

**Anti-Patterns:**
- `AP-S8.1a` â€” Deploying Next.js to Railway or a custom Docker container â€” loses Vercel's zero-config Next.js optimisation, automatic preview deployments, and edge runtime support.

**Cross-References:** `S6.12` (Next.js topology), `S8.4` (preview deployments)

---

### S8.2 â€” Railway for FastAPI â€” Angular Stack Backend Exclusively

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S8.2 |
| **Priority**    | Critical |
| **Applies To**  | Angular Only |
| **Phase**       | Phase 2 â€” Quality & Reliability |
| **Depends On**  | `S6.13` (Angular topology) |
| **Enforced By** | Architecture Review |

**Standard:**
All FastAPI backends (FundsLink, Reserve Bank) deploy to Railway with Python runtime and Uvicorn. Railway provides managed PostgreSQL, managed MongoDB, managed Redis, and zero-downtime deploys. FastAPI is never deployed to Vercel serverless functions â€” Python cold starts and long-running database connections are incompatible with serverless architecture.

**Anti-Patterns:**
- `AP-S8.2a` â€” Deploying FastAPI to Vercel serverless functions â€” Python cold starts take 2-5 seconds; database connections cannot be persistent; the deployment model is incompatible with FastAPI's connection pooling.

**Cross-References:** `S6.13` (Angular topology), `S6.29` (deploy order)

---

### S8.3 â€” Angular Frontend on Vercel â€” Separate Project from FastAPI

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S8.3 |
| **Priority**    | Critical |
| **Applies To**  | Angular Only |
| **Phase**       | Phase 2 â€” Quality & Reliability |
| **Depends On**  | `S6.13`, `S8.2` |
| **Enforced By** | Architecture Review |

**Standard:**
The Angular frontend deploys as a separate Vercel project from the FastAPI backend. Angular is a static SPA build â€” Vercel serves it correctly. The two deployments coordinate via `S6.29` (FastAPI first). `environment.prod.ts` points to the Railway FastAPI URL.

**Cross-References:** `S8.2` (Railway), `S6.29` (deploy order)

---

### S8.4â€“S8.8 â€” Additional Platform Standards

> **S8.4** â€” Preview deployments are generated for every PR on both stacks. Next.js: Vercel preview URL. Angular: Vercel preview URL for frontend + Railway staging for API PRs. E2E tests run against preview deployments.

> **S8.5** â€” Three environments â€” Development (local Docker Compose), Staging (auto-deployed from main merge), Production (manually promoted from staging). Code never goes directly from development to production.

> **S8.6** â€” Zero-downtime deploys on all production deployments. Vercel: atomic deployment with instant rollover. Railway: rolling restart with minimum 1 healthy replica before killing old container.

> **S8.7** â€” Production deployment rollback available in under 5 minutes via one action. Vercel: one-click rollback to previous deployment. Railway: redeploy previous build. Rollback procedures are tested in staging quarterly.

> **S8.8** â€” ChromaDB on Railway as a separate service with persistent volume. No public port exposed â€” FastAPI accesses ChromaDB via Railway internal networking only (FundsLink).

---

## Part 2 â€” CI/CD Pipeline (`S8.9`â€“`S8.16`)

---

### S8.9 â€” GitHub Actions for All CI â€” Separate Workflow Per Repository

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S8.9 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 2 â€” Quality & Reliability |
| **Depends On**  | `S7.6` (test suite in CI) |
| **Enforced By** | Repository configuration |

**Standard:**
All CI/CD runs on GitHub Actions. Every repository has: `ci.yml` (runs on PR â€” lint, typecheck, tests, coverage gate, critical E2E), `deploy-staging.yml` (runs on main merge â€” auto-deploy to staging), `deploy-production.yml` (manually triggered â€” requires explicit approval).

**Anti-Patterns:**
- `AP-S8.9a` â€” Manual deploys to staging by pushing directly to a deploy branch â€” bypasses CI gates and produces an untested staging environment.

**Cross-References:** `S7.6` (CI test requirements), `S8.12` (production approval gate)

---

### S8.10 â€” CI Runs in Under 5 Minutes â€” Parallelise Tests

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S8.10 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 2 â€” Quality & Reliability |
| **Depends On**  | `S8.9` (GitHub Actions) |
| **Enforced By** | CI timing alert |

**Standard:**
PR CI completes in under 5 minutes. Achieve via: parallel job matrix (lint, typecheck, tests run simultaneously), test file sharding for large test suites, Docker layer caching, and dependency caching. A CI run exceeding 10 minutes is a performance bug fixed within one sprint.

**Anti-Patterns:**
- `AP-S8.10a` â€” Sequential CI steps (lint then test then build) when they can run in parallel â€” triples CI time unnecessarily.

**Cross-References:** `S7.6` (critical paths on every PR, full suite nightly)

---

### S8.11 â€” Automatic Staging Deploy on Main Merge

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S8.11 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 2 â€” Quality & Reliability |
| **Depends On**  | `S8.9` (GitHub Actions), `S6.29` (Angular deploy order) |
| **Enforced By** | GitHub Actions `deploy-staging.yml` |

**Standard:**
Every merge to main automatically deploys to staging. Angular stack: Railway (FastAPI) deploys first, then Vercel (Angular) â€” per S6.29. Staging is the canonical test environment for final QA and E2E validation before production. Never manually deploy to staging.

**Anti-Patterns:**
- `AP-S8.11a` â€” Manual staging deploy by directly pushing to a deploy branch â€” bypasses CI; untested code enters staging.

**Cross-References:** `S6.29` (Angular deploy order), `S8.9` (GitHub Actions)

---

### S8.12 â€” Production Deploy Is Manual and Gated â€” Explicit Approval Required

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S8.12 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 2 â€” Quality & Reliability |
| **Depends On**  | `S8.9` (GitHub Actions) |
| **Enforced By** | GitHub Actions environment protection rule |

**Standard:**
Production deployments are triggered via GitHub Actions `workflow_dispatch` with an `environment: production` protection rule requiring explicit owner approval. No automatic production deploys. Production deploy only runs after staging has been validated and owner approval is granted.

**Anti-Patterns:**
- `AP-S8.12a` â€” Automatic production deploy on main merge â€” removes the human validation gate between staging and production.

**Cross-References:** `S8.5` (three environments), `CF-15` (production deploy without staging validation = SEV1)

---

### S8.13â€“S8.16 â€” Additional CI/CD Standards

> **S8.13** â€” Dependency caching in CI: TypeScript `~/.npm` cached keyed on `package-lock.json` hash. Python `~/.cache/pip` cached keyed on `requirements.txt` hash. Uncached CI runs are 3Ã— slower.

> **S8.14** â€” Prisma migrations validated in CI: `prisma migrate diff` runs on every PR that changes `schema.prisma`. Detects missing migration files before merge.

> **S8.15** â€” Build artefacts use Docker layer caching with GitHub Container Registry as cache source â€” unchanged layers (dependencies, base image) reuse cache, reducing build time from 5+ minutes to under 1 minute.

> **S8.16** â€” Angular stack CI deploy is orchestrated: (1) trigger Railway FastAPI deploy and wait for health check, (2) only if FastAPI succeeds, trigger Vercel Angular deploy. FastAPI deploy failure skips Angular deploy â€” per S6.29.

---

## Part 3 â€” Docker & Local Development (`S8.17`â€“`S8.23`)

---

### S8.17 â€” `docker-compose up` â€” Full Stack in One Command

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S8.17 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 2 â€” Quality & Reliability |
| **Depends On**  | â€” |
| **Enforced By** | New developer onboarding check |

**Standard:**
Every system runs locally with `docker-compose up` as a single command. The `docker-compose.yml` includes all services: application server, PostgreSQL, MongoDB (Angular stack), Redis (where used), ChromaDB (FundsLink). A developer who clones the repository and runs `docker-compose up` has a working development environment without additional manual configuration steps.

**Anti-Patterns:**
- `AP-S8.17a` â€” "Run PostgreSQL manually on port 5432, start Redis separately, then run `npm run dev`" â€” multiple manual steps create setup inconsistency and block new contributors.

**Cross-References:** `S8.21` (database containers in Docker Compose), `S7.39` (test database via Docker)

---

### S8.18â€“S8.23 â€” Docker Standards

> **S8.18** â€” Docker images use specific version tags â€” never `latest`. `node:20.11-alpine`, `python:3.12-slim`. `latest` produces non-reproducible builds.

> **S8.19** â€” Multi-stage Docker builds for production images: `build` stage (dependencies + compilation), `production` stage (runtime only â€” no build tools, no dev dependencies). Production image size target: under 200MB.

> **S8.20** â€” `.dockerignore` excludes: `node_modules/`, `.git/`, `.env*`, test files, `__pycache__/`, coverage reports. Build context must be minimal.

> **S8.21** â€” Docker Compose PostgreSQL container uses a named volume for data persistence across `docker-compose down` calls. Test database uses a separate, ephemeral volume.

> **S8.22** â€” Health checks defined for all Docker Compose services â€” dependent services wait for health check success before starting. No `depends_on` without a `condition: service_healthy`.

> **S8.23** â€” Hot reload enabled in Docker Compose development configuration: `volumes: ['.:/app']` with `command: uvicorn app.main:app --reload` (FastAPI) or `next dev` (Next.js).

---

## Part 4 â€” Environment & Configuration Governance (`S8.24`â€“`S8.30`)

---

### S8.24 â€” Three Environments â€” Development, Staging, Production

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S8.24 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 2 â€” Quality & Reliability |
| **Depends On**  | `S8.5` |
| **Enforced By** | Environment configuration audit |

**Standard:**
Every system has three isolated environments with separate databases, secrets, and URLs. Development: local Docker Compose, developer machine. Staging: cloud-deployed from main, mirrors production configuration. Production: manually promoted from staging. No shared infrastructure between environments.

**Anti-Patterns:**
- `AP-S8.24a` â€” Staging and production sharing the same PostgreSQL database â€” a staging test that corrupts data corrupts production data.

**Cross-References:** `S8.5`, `S8.39` (environment variables per environment)

---

### S8.25â€“S8.30 â€” Environment Configuration Standards

> **S8.25** â€” `.env.example` is committed to version control with all required variable names and descriptions but no values. `.env` is in `.gitignore` and never committed.

> **S8.26** â€” Environment variables are validated at application startup using Zod (TypeScript) or Pydantic Settings (Python). Application refuses to start if required variables are missing or invalid.

> **S8.27** â€” Production secrets are stored in Vercel Environment Variables (Next.js/Angular frontend) and Railway Secrets (FastAPI). Never in application code, never in git history.

> **S8.28** â€” Database URLs use connection string format with password URL-encoded. PgBouncer connection pooler URL for production PostgreSQL (Railway). Direct URL for migrations only.

> **S8.29** â€” Feature flags stored in the `FeatureFlag` PostgreSQL table â€” not in environment variables. Environment variables govern infrastructure behaviour; feature flags govern application behaviour.

> **S8.30** â€” All environment variables are documented in the system context file with their purpose and the service that consumes them. A new environment variable without documentation is a code review block.

---

## Part 5 â€” Monitoring & Observability (`S8.31`â€“`S8.40`)

---

### S8.31 â€” Structured JSON Logging â€” Mandatory Fields on Every Log Entry

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S8.31 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 2 â€” Quality & Reliability |
| **Depends On**  | `S2.56` (C2 observability standards) |
| **Enforced By** | Log format linter in CI |

**Standard:**
Every log entry is structured JSON with mandatory fields: `timestamp` (ISO 8601), `level` (DEBUG/INFO/WARN/ERROR), `service` (application name), `request_id` (X-Request-ID for correlation), `message`, and `context` (JSONB â€” additional structured data relevant to the event). Plain text logs are forbidden in production.

**Rationale:**
Structured logs can be queried, filtered, and correlated programmatically. Plain text logs require regex parsing to extract any information, making observability tooling ineffective.

**Anti-Patterns:**
- `AP-S8.31a` â€” `console.log("User logged in:", userId)` â€” unstructured log that cannot be correlated, filtered, or queried efficiently.

**Cross-References:** `S2.56` (backend observability), `S2.60` (X-Request-ID propagation)

---

### S8.32 â€” Sentry for Error Tracking â€” Both Frontend and Backend

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S8.32 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 2 â€” Quality & Reliability |
| **Depends On**  | `S4.65` (frontend Sentry), `S2.57` (backend Sentry) |
| **Enforced By** | Sentry project verification |

**Standard:**
Sentry is initialised in every frontend and backend application with: DSN from environment variable, environment tag, release version from build metadata, and user context on authentication. Every unhandled exception reaches Sentry. Sentry alerts are configured for new issue types and error rate spikes.

**Anti-Patterns:**
- `AP-S8.32a` â€” Sentry initialised without user context â€” errors arrive with no way to identify affected users or correlate frontend and backend errors from the same session.

**Cross-References:** `S4.65` (frontend Sentry), `S2.57` (backend Sentry), `S8.55` (Sentry alerts)

---

### S8.33â€“S8.40 â€” Additional Observability Standards

> **S8.33** â€” Better Stack monitors the `/health` endpoint of every production service every 60 seconds. Three consecutive health check failures trigger a SEV0 alert to the incident commander.

> **S8.34** â€” `/health` endpoint returns: `{ status: "ok"|"degraded", database: "connected"|"error", version: "...", uptime: seconds }`. A degraded database triggers the SEV0 alert even if the application is running.

> **S8.35** â€” Alert thresholds: error rate >1% on any endpoint â†’ SEV1 evaluation. p95 latency >500ms â†’ warning. p95 latency >2s on critical endpoints sustained 5 minutes â†’ SEV2. Memory above 90% for 5 minutes â†’ SEV1. CPU above 85% for 5 minutes â†’ SEV2.

> **S8.36** â€” Railway Metrics alerts for Angular stack: FastAPI CPU, memory, and database connection pool utilisation â€” per threshold table in S8.35.

> **S8.37** â€” Vercel Analytics enabled on all Next.js and Angular frontends â€” Core Web Vitals (LCP, CLS, FID) tracked per deployment.

> **S8.38** â€” Alert delivery chain is tested monthly: SEV0/SEV1 alerts via email AND WhatsApp to Maluleke Kurhula Success. SEV2 and below: email only, reviewed during working hours.

> **S8.39** â€” Log retention: ERROR level logs retained 90 days. INFO level logs retained 30 days. DEBUG level logs not stored in production.

> **S8.40** â€” Dashboard: Better Stack creates a status page per system showing uptime, incident history, and current status. URL is public and linked from the system's README.

---

## Part 6 â€” Security & Secrets (`S8.41`â€“`S8.46`)

> **S8.41** â€” Secret scanning enabled on all repositories via GitHub Advanced Security â€” any accidental commit of secrets is detected and alerts the owner immediately.

> **S8.42** â€” Dependencies scanned with `npm audit` (TypeScript) and `safety` (Python) in CI â€” known vulnerabilities block merge.

> **S8.43** â€” Docker images scanned for vulnerabilities in CI before push to registry.

> **S8.44** â€” All production secrets rotated at minimum quarterly â€” documented rotation schedule in the system context file.

> **S8.45** â€” SSH access to Railway and Vercel uses organisation SSO â€” no personal access tokens with admin scope committed anywhere.

> **S8.46** â€” Production database access is through the application only â€” no direct developer access to production PostgreSQL in normal operations. Emergency access requires documented justification and is audited.

---

## Part 7 â€” Severity Framework (`S8.47`â€“`S8.54`)

---

### S8.47 â€” Severity Classification â€” Four Levels

| Severity | Definition | Response SLA | Resolution SLA | Communication |
|----------|-----------|--------------|----------------|---------------|
| **SEV0** | Complete platform outage, data loss, auth system down, financial transaction failure (Reserve Bank) | 15 minutes | 2 hours | Immediate â€” public + user |
| **SEV1** | Major feature failure >50% users, AI matching down (FundsLink), payment endpoint failing, database degraded | 30 minutes | 4 hours | Status page update |
| **SEV2** | Partial feature degradation, performance >500ms p95, RAG pipeline slow, non-critical background jobs failing | 2 hours | 24 hours | Internal only |
| **SEV3** | Minor issue, no user impact, UI cosmetic bug, slow background job, documentation drift | Next sprint | 1 week | GitHub Issue only |

---

### S8.48 â€” Every Incident Classified Within 5 Minutes of Detection

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S8.48 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 2 â€” Quality & Reliability |
| **Depends On**  | `S8.47` (severity definitions) |
| **Enforced By** | Incident response protocol |

**Standard:**
The first action on detecting any production issue is severity classification within 5 minutes. Classification determines the response SLA, incident commander, and communication requirements. When uncertain between two levels, classify at the higher severity â€” it can be downgraded with more information.

**Anti-Patterns:**
- `AP-S8.48a` â€” Investigating without classifying first â€” unclassified incidents have no response SLA, no incident commander, and no communication requirements; they are invisible to the rest of the process.

**Cross-References:** `S8.47` (severity definitions), `S8.60` (incident commander assignment)

---

### S8.49â€“S8.54 â€” Additional Severity Standards

> **S8.49** â€” SEV0 response priority: (1) restore service first â€” rollback, failover, hotfix, whatever works fastest. (2) Document what was done. (3) Investigate root cause after service is restored. Never delay a rollback to investigate.

> **S8.50** â€” Reserve Bank financial incidents are automatically SEV0 regardless of user impact scale: any incident involving incorrect balances, failed deposits, interest miscalculation, or transaction duplication. `DEPOSITS_ENABLED` and `WITHDRAWALS_ENABLED` feature flags set to `false` as the first action. No financial operations resume until data integrity is verified.

> **S8.51** â€” FundsLink AI incidents: when LangChain/ChromaDB AI matching fails, the circuit breaker triggers (S2.47) and users see a static "AI matching temporarily unavailable â€” apply manually" screen. This is SEV2, not SEV0.

> **S8.52** â€” SEV0 and SEV1 incidents: GitHub Issue opened within 10 minutes, tagged `incident` and `sev0`/`sev1`. Issue title format: `[SEV0] Platform outage â€” auth service down`.

> **S8.53** â€” Incident Commander assigned within 15 minutes for SEV0/SEV1 â€” single point of coordination who makes all decisions and owns communication. Not necessarily the technical responder.

> **S8.54** â€” Incident status updates every 30 minutes during active SEV0/SEV1 on the GitHub Issue. "Still investigating" is acceptable â€” silence is not.

---

## Part 8 â€” Detection & Alerting (`S8.55`â€“`S8.60`)

> **S8.55** â€” Sentry error rate alert: >1% error rate on any endpoint over a 5-minute window triggers SEV1 evaluation. New unique issue on auth, financial, or data integrity path triggers SEV1 immediately.

> **S8.56** â€” Better Stack: three consecutive `/health` failures â†’ SEV0 alert to incident commander. Next.js: monitors `Vercel URL/api/health`. FastAPI: monitors `Railway URL/health`.

> **S8.57** â€” Railway metrics: CPU >85% for 5 minutes â†’ SEV2 alert. Memory >90% for 5 minutes â†’ SEV1 alert (memory leak). DB connection pool >80% â†’ SEV2 warning. Service restart detected â†’ SEV1 alert.

> **S8.58** â€” Vercel deploy failures on main branch trigger immediate GitHub notification and email. Treated as SEV2 â€” previous deployment remains live.

> **S8.59** â€” Latency degradation: p95 >2s on any critical endpoint sustained 5 minutes â†’ SEV2. Financial endpoints: p95 >1s â†’ SEV2.

> **S8.60** â€” SEV0/SEV1 alerts delivered via email AND WhatsApp to Maluleke Kurhula Success 24/7. Alert delivery chain tested monthly.

---

## Part 9 â€” Response Runbooks (`S8.61`â€“`S8.66`)

Response runbooks are the step-by-step execution guides for common incident types. They live in `runbooks/` as standalone files. Standards here govern their existence and maintenance.

> **S8.61** â€” A runbook exists for every SEV0 and SEV1 scenario identified in the Common Failure Register (C0 Â§13). Runbooks are in `runbooks/` and referenced from the GitHub incident issue.

> **S8.62** â€” Runbook format: Title, Severity, Trigger condition, First 5 actions (numbered, executable without thinking), Escalation path, Resolution criteria, Post-mortem trigger.

> **S8.63** â€” Runbooks are tested in staging quarterly â€” a test incident is simulated, the runbook is followed, and gaps are corrected. An untested runbook is an unreliable runbook.

> **S8.64** â€” `runbooks/SEV0-response-runbook.md` is the first-read document at the start of every SEV0. It is the generic template. System-specific runbooks (financial-freeze, ai-degradation) extend it.

> **S8.65** â€” Runbook execution is logged in the GitHub incident issue: each step completed is checked off with a timestamp. This produces a timeline for the post-mortem.

> **S8.66** â€” New runbooks are created within one sprint of any incident where the responder had to improvise. The improvised solution becomes the documented runbook.

---

## Part 10 â€” Rollback Procedures (`S8.67`â€“`S8.72`)

> **S8.67** â€” Every production deployment must be rollbackable within 5 minutes. Rollback capability is tested as part of quarterly staging exercises.

> **S8.68** â€” Next.js rollback: Vercel dashboard one-click rollback to previous deployment â€” instant, zero downtime.

> **S8.69** â€” FastAPI rollback: Railway dashboard redeploy previous build. If the deployment introduced a schema migration, follow `runbooks/database-migration-runbook.md` for the migration rollback sequence.

> **S8.70** â€” Database migration rollback: never run a destructive migration in production without first testing the rollback in staging. `prisma migrate resolve --rolled-back <migration_name>` for failed migrations. Column deletion is never part of a same-deployment migration (S5.61).

> **S8.71** â€” Rollback triggers: Sentry error rate spike >5% within 5 minutes of deploy. p95 latency >3x baseline within 5 minutes of deploy. Any SEV0/SEV1 detected within 15 minutes of deploy.

> **S8.72** â€” Post-rollback: the deployment is not re-attempted until the root cause is identified and fixed. A "roll forward" (fix deployed immediately after rollback) follows the same CI/staging/production pipeline as any deployment.

---

## Part 11 â€” Incident Communication (`S8.73`â€“`S8.76`)

> **S8.73** â€” SEV0 public communication: Better Stack status page updated within 15 minutes of incident declaration. Message format: "We are experiencing [impact description]. Our team is actively investigating. Next update in 30 minutes."

> **S8.74** â€” SEV1 communication: Status page updated, internal team notified. No public communication until impact is confirmed.

> **S8.75** â€” Resolution communication: "The issue has been resolved. [One sentence: what happened and what was fixed]. Post-mortem will be published within 5 business days."

> **S8.76** â€” Never speculate publicly about root cause during an active incident. Communicate what is known â€” impact, affected systems, next update time â€” not what is suspected.

---

## Part 12 â€” Post-Mortem Protocol (`S8.77`â€“`S8.82`)

---

### S8.77 â€” Post-Mortem Required for All SEV0 and SEV1 Incidents

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S8.77 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 2 â€” Quality & Reliability |
| **Depends On**  | `S8.47` (severity framework) |
| **Enforced By** | Incident Commander checklist |

**Standard:**
Every SEV0 and SEV1 incident produces a post-mortem document using `templates/post-mortem-template.md`. Post-mortem is completed within 5 business days of resolution. Post-mortem is blameless â€” the goal is system improvement, not individual fault.

**Anti-Patterns:**
- `AP-S8.77a` â€” No post-mortem after a SEV0 â€” the incident recurs without the systemic changes that would have prevented it.

**Cross-References:** `templates/post-mortem-template.md`, `C0 Â§12` (review calendar â€” post-mortem review trigger)

---

### S8.78â€“S8.82 â€” Post-Mortem Standards

> **S8.78** â€” Post-mortem document fields: title, severity, date/time of detection, date/time of resolution, total duration, incident commander, systems affected, impact summary, timeline (minute-by-minute from detection to resolution), root cause analysis (5 Whys), contributing factors, what went well, action items (each with owner and due date).

> **S8.79** â€” Action items from post-mortems are GitHub Issues with the `post-mortem-action` label â€” tracked in the sprint, not deferred indefinitely.

> **S8.80** â€” Every post-mortem adds at least one entry to C0 Common Failure Register (Â§13) â€” the register grows with every incident.

> **S8.81** â€” Post-mortems are published internally to the team â€” not kept private by the incident commander. Shared knowledge prevents recurrence across systems.

> **S8.82** â€” Quarterly review includes a review of all post-mortem action items â€” items that are overdue are escalated. An action item that was never addressed is a systemic risk.

---

## Part â€” External-Surface & Brownfield Reliability (`S8.83`â€“`S8.87`)

> **S8.83** â€” Every brownfield conversion step is individually reversible with a ready rollback path. A step that cannot be rolled back is not a step â€” it is a risk. Pairs with `protocols/brownfield-adoption.md`. Anti-pattern `AP-S8.83a`: shipping a non-reversible conversion step with no rollback prepared.

> **S8.84** â€” Dependency installs run behind a committed lockfile and a CI vulnerability (SCA) gate; SEV0/SEV1 dependency CVEs **block merge** (deterministic detection â€” hard block allowed). Pairs with `protocols/external-governance.md` Â§2. Anti-pattern `AP-S8.84a`: merging with a known SEV0/SEV1 dependency CVE or no SCA gate.

> **S8.85** â€” Every dependency's license is checked against an allowlist; unknown/copyleft licenses require a recorded L4 exception. An SBOM is generated for releases. Anti-pattern `AP-S8.85a`: shipping a dependency with an unvetted license or no SBOM.

> **S8.86** â€” Every critical external vendor has a register entry (what it does, what data it holds, its SLA) and a documented exit/portability plan. Undocumented lock-in requires an L4-acknowledged contingency. Anti-pattern `AP-S8.86a`: depending on a critical vendor with no exit plan.

> **S8.87** â€” The external surface is under continuous temporal governance: framework changelogs, CVE/advisory databases, and dependency releases are monitored; items past their review window are flagged `TEMPORAL-ALERT` / `UNVALIDATED`. Anti-pattern `AP-S8.87a`: treating dependency/framework currency as a one-time check that then rots.

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
| `C0 â€” Constitutional Order` | Amendment protocol, Common Failure Register, review calendar |
| `C2 â€” Backend Constitution` | Deployment standards for backend services, observability (S2.56â€“S2.62) |
| `C5 â€” Database Constitution` | Migration governance in deployment pipeline (S5.59) |
| `C6 â€” Full-Stack Architecture` | Deployment coordination (S6.29), platform topology |
| `C7 â€” Testing Constitution` | CI gate: all tests must pass before production deploy |

**The following constitutions depend on this one:**
| Dependent | Reason |
|-----------|--------|
| `C9 â€” Product & Feature` | MVP "done" criteria includes production deployment |
| `C10 â€” AI Collaboration` | Incident response is an AI permission boundary |

---

## Amendment Log

| Version | Date | Change | Reason |
|---------|------|--------|--------|
| v1.0 | 2026-05-08 | Initial lock â€” rebuilt from Infrastructure Constitution v3.0 + Incident Response Constitution v3.0. Both documents merged into one Platform Reliability Constitution. Observability standards consolidated from Backend B41â€“B46 and Infrastructure I31â€“I38 into Part 5. All runbooks extracted to `runbooks/` folder. Severity framework aligned with backend circuit breaker and financial freeze standards. Structured JSON log format formalised in S8.31. | Full system rebuild â€” two documents merged into one authoritative source. |
| v1.1 | 2026-06-21 | **Added S8.83â€“S8.87 â€” External-Surface & Brownfield Reliability:** S8.83 per-step reversibility in brownfield conversion; S8.84 lockfile + CI CVE gate; S8.85 license allowlist + SBOM; S8.86 vendor register + exit plan; S8.87 continuous temporal governance. Anti-patterns AP-S8.83aâ€“AP-S8.87a added. Count 82â†’87. (C0 Â§8 amendment; brownfield + external/ecosystem governance; Founder L4 approval 2026-06-21.) | Supply-chain CVEs, undocumented vendor lock-in, rotting dependencies, and non-reversible conversion steps are leading reliability/security failure modes; each is now a governed reliability standard. |

---

> **LOCKED â€” v1.1 â€” 2026-06-21** (amended; originally locked v1.0 2026-05-08)
>
> This document is locked. No standard may be added, removed, or modified
> without following the Amendment Protocol defined in C0 Â§8.
> Amendments take effect only after commit to `governova`
> with a version bump and amendment log entry.
