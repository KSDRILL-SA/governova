# C2 — Backend Constitution

---

| Attribute          | Value                                                              |
|--------------------|--------------------------------------------------------------------|
| **Document**       | C2 — Backend Constitution                                          |
| **Organisation**   | KSDRILL SA                                                         |
| **Version**        | v1.0                                                               |
| **Status**         | LOCKED                                                             |
| **Locked**         | 2026-05-08                                                         |
| **Next Review**    | 2026-08-08                                                         |
| **Applies To**     | Both Stacks                                                        |
| **Paired With**    | C2 — Backend Implementation Guide                                  |

---

> *"The backend is not a dumping ground for logic that doesn't fit anywhere else —
> it is a precise contract between data and the systems that need it."*

---

## Opening Statement

The Backend Constitution governs every server-side decision in every KSDRILL SA system.
It defines the architectural boundaries of the service layer, the contract-first discipline
that governs all API design, the database access patterns that protect data integrity, the
observability and security standards that make backend services production-worthy from the
first deployment, and the extension-first principle that ensures today's decisions do not
become tomorrow's rewrites.

This constitution governs two distinct backend implementations operating under the same
standards: the Next.js API Routes implementation used in Maphophe and SyncUp, and the
FastAPI implementation used in FundsLink Academy and KSDRILL Reserve Bank. Where a
standard applies to only one stack, it is explicitly scoped. Where no scope is stated,
the standard applies to both stacks without exception.

This constitution does not govern authentication strategy — that is C3. It does not govern
database schema design or assignment — that is C5. It does not govern how the frontend
consumes the API — that is C4. What this constitution governs is the service layer between
the database and the client: how it is structured, what contracts it honours, how it fails,
how it recovers, how it is observed in production, and how it extends without modification.

The paired implementation guide contains code patterns, commands, and file structures
that satisfy these standards. This document contains standards and rationale — not
implementation. When you need to know what to build, read this. When you need to know
how to build it, read the implementation guide.

---

## Table of Contents

| Part | Title | Standards |
|------|-------|-----------|
| Part 1 | Service Layer Architecture | S2.1–S2.6 |
| Part 2 | Extension-First Backend Design | S2.7–S2.10 |
| Part 3 | API Contract & Design | S2.11–S2.18 |
| Part 4 | Standard Response Shape Contract | S2.19–S2.22 |
| Part 5 | Validation Layer | S2.23–S2.27 |
| Part 6 | Database Access from Backend | S2.28–S2.35 |
| Part 7 | Performance Standards | S2.36–S2.41 |
| Part 8 | Resilience & Error Handling | S2.42–S2.48 |
| Part 9 | Security Standards | S2.49–S2.55 |
| Part 10 | Observability | S2.56–S2.62 |
| Part 11 | FastAPI-Specific Standards | S2.63–S2.69 |
| Part 12 | Next.js API Route Standards | S2.70–S2.75 |
| Part 13 | API Versioning Governance | S2.76–S2.80 |


---

## Part 1 — Service Layer Architecture (`S2.1`–`S2.6`)

The service layer is the contractual boundary between the data layer and everything that
consumes it. Every architectural decision in the backend flows from maintaining this
boundary with absolute discipline.

---

### S2.1 — Business Logic Lives Exclusively in the Service Layer

| Attribute | Value |
|-----------|-------|
| **ID** | S2.1 |
| **Priority** | Critical |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | — |
| **Enforced By** | Code Review · Architecture Review |

**Standard:**
All business logic — rules, calculations, orchestration, workflow decisions, and
authorization checks — lives exclusively in the service layer. Route handlers receive a
validated request, call service functions, and return the result. They make no business
decisions. Database access functions translate service intent into queries — they make no
business decisions. The service layer is the only layer that decides what is allowed.

**Rationale:**
When business logic is distributed across route handlers, queries, and UI components, it
cannot be tested independently, replaced cleanly, or audited reliably. Centralising it in
the service layer makes every business rule findable, testable in isolation, and
replaceable without cascading changes.

**Anti-Patterns:**
- `AP-S2.1a` — Business logic written directly inside a route handler or API controller.
- `AP-S2.1b` — Authorization checks performed inside a database query.
- `AP-S2.1c` — A service function that formats the HTTP response.

**Cross-References:** `S2.2` (layer contracts), `S4.1` (frontend mirrors this pattern)

---

### S2.2 — Each Layer Communicates Only Through Its Defined Contract

| Attribute | Value |
|-----------|-------|
| **ID** | S2.2 |
| **Priority** | Critical |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.1` |
| **Enforced By** | Code Review · Architecture Review |

**Standard:**
Each backend layer communicates only with the layer directly adjacent to it. The route
handler calls the service layer — never the database directly. The service layer calls
the data access layer — never writes raw queries inline. The data access layer executes
queries — never makes business decisions. No layer skips a layer. Any layer must be
replaceable without changes in non-adjacent layers.

**Rationale:**
Layer skipping creates invisible coupling. When a route handler calls the database
directly, replacing the database requires changing the route handler — a non-adjacent
layer. This is how systems become unmaintainable.

**Anti-Patterns:**
- `AP-S2.2a` — A Next.js API route calling `prisma.user.findMany()` directly inside the route file.
- `AP-S2.2b` — A FastAPI route handler calling a query function without a service module.
- `AP-S2.2c` — A service function building an HTTP response object.

**Cross-References:** `S2.1`, `S2.28`, `S6.4` (Layer Independence Standard)

---

### S2.3 — Services Are Stateless

| Attribute | Value |
|-----------|-------|
| **ID** | S2.3 |
| **Priority** | Critical |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.1` |
| **Enforced By** | Code Review |

**Standard:**
All service functions are stateless. They receive all required data as parameters, perform
their operation, and return a result. No service function stores state between calls in
module-level variables, closures that persist across requests, or in-memory caches that
are not explicitly managed. Stateless services can be deployed across multiple instances
with zero coordination — the horizontal scaling guarantee.

**Anti-Patterns:**
- `AP-S2.3a` — Module-level variables that accumulate request data across calls.
- `AP-S2.3b` — In-memory user session storage inside a service module.

**Cross-References:** `S2.7` (extension-first), `S2.8` (horizontal scaling)

---

### S2.4 — One Service Per Domain

| Attribute | Value |
|-----------|-------|
| **ID** | S2.4 |
| **Priority** | High |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S1.3` (one concern per unit) |
| **Enforced By** | Code Review · Module Structure |

**Standard:**
Each service module owns exactly one domain. A student service owns student operations.
A scholarship service owns scholarship operations. Services do not reach into other
services' domains. When a feature requires data from two domains, orchestration happens
in a dedicated orchestration service or in the route handler by composing two separate
service calls — not by one service importing another's internal functions.

**Anti-Patterns:**
- `AP-S2.4a` — A student service function directly calling scholarship service functions.
- `AP-S2.4b` — A single service file handling two unrelated domains.

**Cross-References:** `S1.3`, `S2.7` (new domains are new services)

---

### S2.5 — Service Functions Have Explicit Return Types

| Attribute | Value |
|-----------|-------|
| **ID** | S2.5 |
| **Priority** | High |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S1.50` (TypeScript), `S1.57` (Python) |
| **Enforced By** | TypeScript compiler · mypy · Code Review |

**Standard:**
Every service function has an explicit return type annotation. For TypeScript: declared
on the function signature, not inferred. For Python: type hint on every public function.
A service function's return type is the contract between the service layer and the route
handler — when inferred, it changes silently when the function body changes.

**Anti-Patterns:**
- `AP-S2.5a` — TypeScript service function with no return type relying on inference.

**Cross-References:** `S1.50`, `S1.57`

---

### S2.6 — No Business Logic in Middleware

| Attribute | Value |
|-----------|-------|
| **ID** | S2.6 |
| **Priority** | High |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.1` |
| **Enforced By** | Code Review |

**Standard:**
Middleware handles cross-cutting concerns only: authentication token validation, request
logging, CORS headers, rate limiting, and request ID injection. Middleware never makes
business decisions, never determines what data a user can see, and never applies domain
rules. It validates the caller is who they claim to be — the service layer determines
what that caller is allowed to do.

**Anti-Patterns:**
- `AP-S2.6a` — Middleware filtering query results based on user role.
- `AP-S2.6b` — Middleware applying a business rule before passing to the route handler.

**Cross-References:** `S2.1`, `S3.5` (auth middleware scope)


---

## Part 2 — Extension-First Backend Design (`S2.7`–`S2.10`)

Extension-first design governs how the backend grows. New capabilities always mean new
code alongside existing code — never modifications to working code. This principle,
extracted from the Ubuntu Campus Clinic system design and adapted to KSDRILL SA, is what
prevents the forced choice between "rewrite everything" and "layer hacks until collapse."

---

### S2.7 — New Capabilities Are New Modules, Not Modifications to Existing Ones

| Attribute | Value |
|-----------|-------|
| **ID** | S2.7 |
| **Priority** | Critical |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.4` |
| **Enforced By** | Architecture Review · Feature Proposal (S1.29) · Code Review |

**Standard:**
When a new capability is added, it is implemented as a new module, service, route group,
or permission class alongside existing ones. Existing working modules are not modified
to accommodate new requirements unless the existing module's own domain is genuinely
changing. The test: "Am I adding behaviour, or changing existing behaviour?" Adding is
extension. Changing is modification. Extension is the default. Modification requires
explicit justification in the feature proposal.

**Anti-Patterns:**
- `AP-S2.7a` — New user role added by modifying an existing permission class.
- `AP-S2.7b` — New notification channel added by modifying existing service logic.
- `AP-S2.7c` — New report type added as a conditional branch inside an existing function.

**Cross-References:** `S2.4`, `S1.29`, `S6.7` (extension-first at system level)

---

### S2.8 — Services Are Designed for Horizontal Scaling from Day One

| Attribute | Value |
|-----------|-------|
| **ID** | S2.8 |
| **Priority** | High |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.3` |
| **Enforced By** | Code Review · Architecture Review |

**Standard:**
All backend services run as multiple identical instances behind a load balancer with zero
configuration changes. Requirements: stateless service functions (S2.3), no in-process
state shared between requests, all session data in the database or managed cache, and
environment-variable-driven configuration. Horizontal scaling is achieved by increasing
instance count — not by changing code.

**Anti-Patterns:**
- `AP-S2.8a` — Module-level variables storing per-request or per-user state.
- `AP-S2.8b` — Hardcoded values that would differ between instances.

**Cross-References:** `S2.3`, `S2.10`

---

### S2.9 — Schema Changes Are Additive by Default

| Attribute | Value |
|-----------|-------|
| **ID** | S2.9 |
| **Priority** | Critical |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S5.N` (migration governance) |
| **Enforced By** | Migration Review · Code Review |

**Standard:**
Schema changes supporting new backend features are additive by default: new columns have
database-level defaults and are nullable until data is backfilled, new tables carry no FK
dependencies that require coordinated deployment, new fields in API responses do not
remove or rename existing fields. Destructive schema changes require a dedicated migration
PR, a documented rollback plan, and explicit justification in the feature proposal.

**Anti-Patterns:**
- `AP-S2.9a` — Column renamed without a two-phase migration plan (add → backfill → remove).
- `AP-S2.9b` — Non-nullable column added without a database default.
- `AP-S2.9c` — API response field removed without a versioning plan per S2.76.

**Cross-References:** `S5.N`, `S2.76`

---

### S2.10 — Environment Configuration Is the Only Infrastructure Variability

| Attribute | Value |
|-----------|-------|
| **ID** | S2.10 |
| **Priority** | Critical |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S8.20` |
| **Enforced By** | CI · Code Review |

**Standard:**
All configuration varying between environments is driven exclusively by environment
variables. No environment-specific logic exists in application code. No credentials,
connection strings, or API keys are hardcoded. Replacing the hosting platform, database
provider, or external service requires only environment variable changes — zero code changes.

**Anti-Patterns:**
- `AP-S2.10a` — `if (process.env.NODE_ENV === 'production')` blocks that change behaviour.
- `AP-S2.10b` — Database connection string hardcoded in the codebase.
- `AP-S2.10c` — API key committed to version control in any file.

**Cross-References:** `S8.20`, `S1.68`

---

## Part 3 — API Contract & Design (`S2.11`–`S2.18`)

API contracts are the binding agreement between the backend and every consumer. Contract
discipline is what makes parallel frontend and backend development possible.

---

### S2.11 — OpenAPI Contract Written Before Any Endpoint Is Implemented

| Attribute | Value |
|-----------|-------|
| **ID** | S2.11 |
| **Priority** | Critical |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S1.1` |
| **Enforced By** | Feature Proposal Review · Code Review |

**Standard:**
The OpenAPI specification for every new endpoint is written and reviewed before any
implementation code is written. The specification defines: endpoint path and HTTP method,
all request parameters and body fields with types and constraints, all response shapes for
all response codes (200, 201, 400, 401, 403, 404, 409, 422, 500), and example values.
The specification is the contract — not documentation of what was built.

**Anti-Patterns:**
- `AP-S2.11a` — OpenAPI spec written after implementing the endpoint.
- `AP-S2.11b` — Frontend development started before OpenAPI spec is approved.

**Cross-References:** `S1.1`, `S1.52`, `S1.58`, `S1.83`

---

### S2.12 — All Endpoints Are RESTful and Resource-Oriented

| Attribute | Value |
|-----------|-------|
| **ID** | S2.12 |
| **Priority** | High |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.11` |
| **Enforced By** | OpenAPI Review · Code Review |

**Standard:**
URLs identify resources using nouns not verbs. HTTP methods convey the action: GET
retrieves, POST creates, PUT replaces, PATCH partially updates, DELETE removes. Paths use
lowercase hyphenated segments. Nested resources use at most two levels of nesting.

**Anti-Patterns:**
- `AP-S2.12a` — Verb-based endpoints: `/api/v1/getStudentProfile`.
- `AP-S2.12b` — GET used for operations that mutate state.
- `AP-S2.12c` — More than two levels of URL nesting.

---

### S2.13 — All Protected Endpoints Declare Auth Requirements Explicitly

| Attribute | Value |
|-----------|-------|
| **ID** | S2.13 |
| **Priority** | Critical |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S3.1`, `S2.11` |
| **Enforced By** | OpenAPI Security Scheme · Code Review · Security Audit |

**Standard:**
Every endpoint explicitly declares whether it is public or protected and, if protected,
which roles are permitted. No endpoint is left unprotected by omission or default. The
OpenAPI spec marks every protected endpoint. In code, every route handler declares its
auth requirements at the function level — not inherited silently from a parent router.

**Anti-Patterns:**
- `AP-S2.13a` — Relying on parent router middleware to protect all child routes with no explicit declaration per handler.
- `AP-S2.13b` — Endpoint "protected" by requiring a body field only authenticated users would know.

**Cross-References:** `S3.1`, `S3.5`

---

### S2.14 — List Endpoints Support Pagination

| Attribute | Value |
|-----------|-------|
| **ID** | S2.14 |
| **Priority** | High |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.11`, `S2.20` |
| **Enforced By** | OpenAPI Review · Code Review |

**Standard:**
All list endpoints support cursor-based or offset-based pagination. No list endpoint
returns an unbounded result set. Default page size is defined per endpoint in the OpenAPI
spec. Response shape includes `data`, `count`, `page`, and `totalPages` per S2.20.

**Anti-Patterns:**
- `AP-S2.14a` — `prisma.student.findMany()` with no `take` or `skip`.
- `AP-S2.14b` — List endpoint without pagination "because the set is small now."

---

### S2.15 — All Endpoints Return JSON

| Attribute | Value |
|-----------|-------|
| **ID** | S2.15 |
| **Priority** | High |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.11` |
| **Enforced By** | Content-Type Header · Code Review |

**Standard:**
All API endpoints return `Content-Type: application/json`. No endpoint returns plain text,
HTML, XML, or unstructured data. The response body always follows one of the three
standard response shapes defined in Part 4.

---

### S2.16 — Sensitive Data Is Never Returned in API Responses

| Attribute | Value |
|-----------|-------|
| **ID** | S2.16 |
| **Priority** | Critical |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.11` |
| **Enforced By** | OpenAPI Review · Security Audit · Code Review |

**Standard:**
API responses never include: password hashes, raw JWT tokens, internal IDs used for
security decisions, secret keys, or any field not explicitly declared in the OpenAPI
response schema. Response serialisation uses an explicit allowlist of fields — not a
database model dump. Every field in every response is there because it was deliberately
included.

**Anti-Patterns:**
- `AP-S2.16a` — Returning a full Prisma model object as the API response.
- `AP-S2.16b` — Response including `passwordHash`, `refreshToken`, or any secret field.

**Cross-References:** `S2.31`, `S3.14`

---

### S2.17 — CORS Is Configured Explicitly per Environment

| Attribute | Value |
|-----------|-------|
| **ID** | S2.17 |
| **Priority** | Critical |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.10` |
| **Enforced By** | CI · Environment Audit · Code Review |

**Standard:**
CORS is configured explicitly per environment via environment variables. Allowed origins
list is a named environment variable — never a wildcard (`*`) in production. In
development, localhost is permitted. In staging and production, only the specific deployed
frontend origin is permitted. CORS wildcard in production is a Critical security violation.

**Anti-Patterns:**
- `AP-S2.17a` — `cors({ origin: '*' })` in production.
- `AP-S2.17b` — CORS allowed origins hardcoded in application code.

---

### S2.18 — APIs Do Not Expose Internal System Details in Error Messages

| Attribute | Value |
|-----------|-------|
| **ID** | S2.18 |
| **Priority** | Critical |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.22` |
| **Enforced By** | Code Review · Security Audit |

**Standard:**
Error responses never contain: database error messages, stack traces, internal file paths,
table names, column names, SQL fragments, or any internal implementation detail. In all
environments, error responses contain only the standard error shape (S2.22). Stack traces
are in logs — not in responses.

**Anti-Patterns:**
- `AP-S2.18a` — Raw database error message returned in the API response.
- `AP-S2.18b` — `error.message` or `error.stack` sent directly to the client.

**Cross-References:** `S2.22`, `S2.56`


---

## Part 4 — Standard Response Shape Contract (`S2.19`–`S2.22`)

Every KSDRILL SA API endpoint returns one of three standard response shapes. No endpoint
invents its own format. A consumer that knows these three shapes can handle every API
response without endpoint-specific parsing logic.

---

### S2.19 — Single Object Response Shape Is Mandatory

| Attribute | Value |
|-----------|-------|
| **ID** | S2.19 |
| **Priority** | Critical |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.11` |
| **Enforced By** | Code Review · OpenAPI Validation |

**Standard:**
All endpoints returning a single resource use this exact shape:
```json
{ "data": {}, "message": "Resource retrieved successfully" }
```
Both fields required. `data` is never null on a 200 response. If the resource is not
found, the response is 404 — not 200 with null data.

**Anti-Patterns:**
- `AP-S2.19a` — Object returned at response root without `data` wrapper.
- `AP-S2.19b` — `data: null` on a 200 response.

---

### S2.20 — List Response Shape Is Mandatory

| Attribute | Value |
|-----------|-------|
| **ID** | S2.20 |
| **Priority** | Critical |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.14`, `S2.11` |
| **Enforced By** | Code Review · OpenAPI Validation |

**Standard:**
All endpoints returning a collection use this exact shape:
```json
{ "data": [], "count": 0, "page": 1, "totalPages": 1 }
```
All four fields required. `data` is always an array — empty array for zero results, never
null. `count` is the total records matching the query before pagination.

**Anti-Patterns:**
- `AP-S2.20a` — `data: null` when list is empty — use `data: []`.
- `AP-S2.20b` — Raw array returned without pagination envelope.

---

### S2.21 — Created Resource Returns 201 With the Full Created Object

| Attribute | Value |
|-----------|-------|
| **ID** | S2.21 |
| **Priority** | High |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.19` |
| **Enforced By** | Code Review · OpenAPI Validation |

**Standard:**
All POST endpoints that create a resource return HTTP 201 with the created resource in
the single object shape (S2.19), including all server-generated fields. The client
receives the complete created resource without a follow-up GET.

**Anti-Patterns:**
- `AP-S2.21a` — POST endpoint returning 200 instead of 201.
- `AP-S2.21b` — POST returning only the new resource's ID.

---

### S2.22 — Error Response Shape Is Mandatory and Uniform

| Attribute | Value |
|-----------|-------|
| **ID** | S2.22 |
| **Priority** | Critical |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.18` |
| **Enforced By** | Code Review · OpenAPI Validation · Global Error Handler |

**Standard:**
All error responses across all endpoints use this exact shape:
```json
{ "error": "Human-readable description", "code": "SCREAMING_SNAKE_CASE", "status": 409 }
```
- `error` — safe for display to end user. Never contains internal details.
- `code` — machine-readable constant from the shared error codes enum. Never freeform.
- `status` — HTTP status code mirrored in the body.

All three fields required. The global error handler enforces this for all unhandled
exceptions — no endpoint can return a different format by forgetting to catch an error.

**Standard error codes by HTTP status:**

| Status | Codes |
|--------|-------|
| 400 | `VALIDATION_ERROR` · `INVALID_INPUT` · `MISSING_REQUIRED_FIELD` |
| 401 | `UNAUTHORIZED` · `TOKEN_EXPIRED` · `TOKEN_INVALID` · `TOKEN_BLACKLISTED` |
| 403 | `FORBIDDEN` · `INSUFFICIENT_PERMISSIONS` · `ACCOUNT_LOCKED` |
| 404 | `NOT_FOUND` · `RESOURCE_NOT_FOUND` |
| 409 | `CONFLICT` · `DUPLICATE_RECORD` · `RECORD_IN_USE` |
| 422 | `UNPROCESSABLE_ENTITY` · `SCHEMA_VALIDATION_FAILED` |
| 429 | `RATE_LIMIT_EXCEEDED` |
| 500 | `INTERNAL_SERVER_ERROR` |
| 503 | `SERVICE_UNAVAILABLE` |

**Anti-Patterns:**
- `AP-S2.22a` — Error response missing `code` or `status` field.
- `AP-S2.22b` — Freeform `code` string not from the shared enum.
- `AP-S2.22c` — Different error shapes from different endpoints.

**Cross-References:** `S2.18`, `S2.56`

---

## Part 5 — Validation Layer (`S2.23`–`S2.27`)

The validation layer is an architectural boundary — not a coding practice. No external
data reaches the service layer without passing this boundary. This is the first line of
defence. Database constraints are the second. Between them, no invalid data survives.

---

### S2.23 — The Validation Layer Is an Architectural Boundary

| Attribute | Value |
|-----------|-------|
| **ID** | S2.23 |
| **Priority** | Critical |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S1.52`, `S1.58` |
| **Enforced By** | Code Review · Architecture Review |

**Standard:**
All data from any external source — HTTP request bodies, query parameters, path
parameters, environment variables, third-party API responses, webhook payloads — is
validated at the boundary before reaching the service layer. No exceptions. Validation
is not skipped for "trusted" sources or deferred to the database.

**Anti-Patterns:**
- `AP-S2.23a` — `request.body.fieldName` accessed in service without prior validation.
- `AP-S2.23b` — Validation skipped for internal API calls between services.
- `AP-S2.23c` — Third-party API responses trusted without shape validation.

**Cross-References:** `S1.52`, `S1.58`

---

### S2.24 — Validation Schemas Are Generated From the OpenAPI Contract

| Attribute | Value |
|-----------|-------|
| **ID** | S2.24 |
| **Priority** | High |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.11`, `S2.23` |
| **Enforced By** | Code Review · Schema Generation Tool |

**Standard:**
Zod schemas (Next.js) and Pydantic models (FastAPI) are generated from the OpenAPI
specification — not written manually. The OpenAPI spec is the single source of truth.
Manual schemas that duplicate the spec create two sources of truth that diverge over time.

**Anti-Patterns:**
- `AP-S2.24a` — Manually written Zod schema that does not match the OpenAPI spec.
- `AP-S2.24b` — Pydantic model written before the OpenAPI spec is finalised.

---

### S2.25 — Seven Validation Categories Are Applied at Every Boundary

| Attribute | Value |
|-----------|-------|
| **ID** | S2.25 |
| **Priority** | High |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.23` |
| **Enforced By** | Code Review · OpenAPI Review |

**Standard:**
Every validation schema addresses all applicable categories:

| Category | What It Validates |
|----------|-------------------|
| Required fields | All non-optional fields are present |
| Format validation | Email format · ISO 8601 dates · positive integer IDs |
| Business rule validation | Date not in past · amount within allowed range |
| Ownership validation | Resource belongs to requesting user |
| Role-based restrictions | Certain fields settable only by certain roles |
| Unique pre-check | Friendly duplicate check before DB constraint fires |
| Referential validation | Referenced IDs exist before write is attempted |

---

### S2.26 — Validation Errors Return 400 or 422 With Field-Level Detail

| Attribute | Value |
|-----------|-------|
| **ID** | S2.26 |
| **Priority** | High |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.22` |
| **Enforced By** | Code Review |

**Standard:**
Validation failures return HTTP 400 or 422 with the standard error shape (S2.22) extended
to include a `fields` array identifying which fields failed and why:
```json
{
  "error": "Validation failed", "code": "VALIDATION_ERROR", "status": 400,
  "fields": [{ "field": "email", "message": "Invalid email format" }]
}
```

**Anti-Patterns:**
- `AP-S2.26a` — Validation error with no field-level detail — client cannot tell user which field to fix.

---

### S2.27 — Input Is Sanitised Before Reaching the Service Layer

| Attribute | Value |
|-----------|-------|
| **ID** | S2.27 |
| **Priority** | Critical |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.23` |
| **Enforced By** | Code Review · Security Audit |

**Standard:**
All string input is sanitised at the validation boundary: whitespace trimmed, HTML escaped
for fields rendered in UI, SQL injection prevented by the ORM exclusively. No string
interpolation in any query. Sanitisation is applied by the validation schema — not by
service functions on already-validated data.

**Anti-Patterns:**
- `AP-S2.27a` — String interpolation in a database query: `` `SELECT * FROM users WHERE id = ${userId}` ``
- `AP-S2.27b` — Service functions sanitising input they already received from the validation layer.


---

## Part 6 — Database Access from Backend (`S2.28`–`S2.35`)

Database access standards protect data integrity at the application boundary, working in
concert with the database-level constraints governed by C5.

---

### S2.28 — Prisma Is the Source of Truth for Relational Data Access

| Attribute | Value |
|-----------|-------|
| **ID** | S2.28 |
| **Priority** | Critical |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S5.1`, `S5.9` |
| **Enforced By** | Code Review · ESLint no-raw-sql rule |

**Standard:**
All relational database access uses Prisma ORM exclusively. No raw SQL bypasses Prisma
in production code. Prisma is instantiated as a singleton per service. All queries include
appropriate `where` clauses. Soft-deleted records are excluded from all standard queries
via `where: { deletedAt: null }`.

**Anti-Patterns:**
- `AP-S2.28a` — Raw SQL via `pg` or `psycopg2` in any service file.
- `AP-S2.28b` — Multiple Prisma client instances per service.
- `AP-S2.28c` — `prisma.student.findMany()` with no `where` clause in a user-facing endpoint.
- `AP-S2.28d` — Standard queries without `deletedAt: null` on soft-deletable entities.
- `AP-S2.28e` — Raw SQL written directly in a service file, route handler, or middleware.
- `AP-S2.28f` — Raw SQL using string interpolation: `` `SELECT * WHERE id = ${id}` `` — always parameterised.

**Cross-References:** `S5.9`, `CF-02`

---

### S2.28e — Raw SQL Is Permitted Only in Designated Repository Files

| Attribute | Value |
|-----------|-------|
| **ID** | S2.28e |
| **Priority** | High |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.28` |
| **Enforced By** | Code Review · Architecture Review |

**Standard:**
Raw SQL via `prisma.$queryRaw`, `prisma.$executeRaw` (Next.js), or equivalent raw
execution methods (FastAPI) is permitted exclusively in dedicated repository files
named `*.repository.ts` or `*_repository.py`. Raw SQL never appears in service files,
route handlers, middleware, or any other layer. Repository files are the only layer
authorised to contain raw SQL and are subject to heightened security review at every
PR. The repository layer sits between the service layer and the database — it is called
by the service layer and returns typed results, never raw database objects.

**Rationale:**
The ORM has a performance ceiling for complex aggregations, window functions, recursive
CTEs, full-text search, and bulk upserts with conflict resolution. Prohibiting raw SQL
entirely forces engineers to either use inefficient ORM workarounds or violate the
constitution. The repository pattern provides a governed escape hatch: raw SQL is
permitted but contained, reviewed, and type-safe. The service layer never knows whether
its data came from an ORM query or a raw SQL query — it receives a typed result either way.

**When raw SQL in a repository is justified:**
- Complex aggregations: `GROUP BY`, `HAVING`, `ROLLUP`, window functions
- Reporting queries across many tables that produce inefficient ORM query plans
- Full-text search using PostgreSQL `tsvector` and `plainsearch`
- Recursive queries using `WITH RECURSIVE` CTEs
- Bulk upserts using `ON CONFLICT DO UPDATE`
- Any query where the ORM-generated SQL demonstrably exceeds the two-second response target (S2.36)

**Anti-Patterns:**
- `AP-S2.28e` — Raw SQL written in a service file, route handler, or middleware — it belongs only in a repository file.
- `AP-S2.28ea` — A repository file created without documented justification for why the ORM is insufficient for that query.

**Cross-References:** `S2.28f` (safety requirements), `S2.36` (performance target that justifies raw SQL)

---

### S2.28f — Raw SQL Must Satisfy Four Safety Requirements

| Attribute | Value |
|-----------|-------|
| **ID** | S2.28f |
| **Priority** | Critical |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.28e` (repository files only) |
| **Enforced By** | Code Review · Security Audit |

**Standard:**
Every raw SQL query in every repository file must satisfy all four safety requirements
before it is considered complete. A raw SQL query failing any requirement is a Critical
violation regardless of which requirement it fails:

**Requirement 1 — Parameterised inputs only.**
All user-supplied values and external inputs are passed as query parameters — never
interpolated into the SQL string. Template literals with variable interpolation inside
raw SQL are a SQL injection vulnerability.

```typescript
// WRONG — string interpolation
await prisma.$queryRaw`SELECT * FROM students WHERE id = ${studentId}`

// CORRECT — tagged template literal (Prisma handles parameterisation)
await prisma.$queryRaw`SELECT * FROM students WHERE id = ${Prisma.sql`${studentId}`}`

// CORRECT — explicit parameter binding
await prisma.$queryRawUnsafe(
  'SELECT * FROM students WHERE id = $1', studentId
)
```

**Requirement 2 — Soft delete filter on every applicable table.**
Every raw SQL query that reads from a soft-deletable table includes
`WHERE deleted_at IS NULL` (or `AND deleted_at IS NULL` if other WHERE conditions
exist) for every soft-deletable table in the query. The ORM helper `activeWhere()`
does not apply to raw SQL — the filter must be written explicitly.

```sql
-- Every soft-deletable table must include the filter
SELECT s.id, s.name, COUNT(a.id) as app_count
FROM students s
LEFT JOIN applications a ON a.student_id = s.id
WHERE s.deleted_at IS NULL          -- required
  AND a.deleted_at IS NULL          -- required on every joined table
GROUP BY s.id, s.name
```

**Requirement 3 — Documented justification in a comment.**
Every raw SQL query is preceded by a comment explaining why Prisma cannot satisfy this
query and what specific capability requires raw SQL. This comment is reviewed at PR time.

```typescript
// JUSTIFICATION: Prisma has no native support for PostgreSQL window functions.
// This query calculates each student's GPA rank within their faculty cohort.
// Equivalent Prisma query would require N+1 pattern or post-query processing.
const results = await prisma.$queryRaw`
  SELECT id, gpa,
    RANK() OVER (PARTITION BY faculty_id ORDER BY gpa DESC) as faculty_rank
  FROM students
  WHERE deleted_at IS NULL
`
```

**Requirement 4 — Output validated with a schema before leaving the repository.**
The result of every raw SQL query is validated against a Zod schema (Next.js) or
Pydantic model (FastAPI) before the repository function returns it. Raw SQL results
are untyped at the database level — schema validation restores type safety at the
application boundary.

```typescript
// Repository function — validates raw SQL output before returning (S2.28f)
export async function getStudentRankings(): Promise<StudentRanking[]> {
  const raw = await prisma.$queryRaw`
    SELECT id, gpa, RANK() OVER (ORDER BY gpa DESC) as rank
    FROM students WHERE deleted_at IS NULL
  `
  return StudentRankingSchema.array().parse(raw)  // Zod validates — type safe from here
}
```

**Anti-Patterns:**
- `AP-S2.28f` — Raw SQL with string interpolation in any form.
- `AP-S2.28fa` — Raw SQL query missing `deleted_at IS NULL` on a soft-deletable table.
- `AP-S2.28fb` — Raw SQL query with no justification comment.
- `AP-S2.28fc` — Raw SQL result returned without schema validation — raw database output leaves the repository layer unvalidated.

---

### S2.29 — MongoDB Access Uses Beanie ODM Exclusively

| Attribute | Value |
|-----------|-------|
| **ID** | S2.29 |
| **Priority** | Critical |
| **Applies To** | Angular Stack |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S5.21`, `S5.25` |
| **Enforced By** | Code Review |

**Standard:**
All MongoDB access in FastAPI services uses Beanie ODM exclusively. Raw PyMongo operations
are not used in service code. Every Beanie document referencing a PostgreSQL entity stores
the PostgreSQL CUID as a string field — not as an ObjectId.

**Anti-Patterns:**
- `AP-S2.29a` — Raw PyMongo collection operations inside a FastAPI service.
- `AP-S2.29b` — Beanie document storing a PostgreSQL FK as an ObjectId.

**Cross-References:** `S5.25`, `S5.30`

---

### S2.30 — Multi-Step Database Writes Are Wrapped in Transactions

| Attribute | Value |
|-----------|-------|
| **ID** | S2.30 |
| **Priority** | Critical |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S5.N` (ACID) |
| **Enforced By** | Code Review · Architecture Review |

**Standard:**
Any operation writing to the database in more than one step is wrapped in a database
transaction ensuring atomicity. Either all steps succeed and commit, or any failure rolls
back all steps. For Prisma: `prisma.$transaction()`. No multi-step write leaves the
database in a partial state.

**Anti-Patterns:**
- `AP-S2.30a` — Two sequential `prisma.create()` calls for related entities without `prisma.$transaction()`.
- `AP-S2.30b` — Manually "undoing" the first write after the second fails — not equivalent to rollback.

---

### S2.31 — Explicit Field Selection Prevents Data Leakage

| Attribute | Value |
|-----------|-------|
| **ID** | S2.31 |
| **Priority** | Critical |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.16`, `S2.28` |
| **Enforced By** | Code Review · Security Audit |

**Standard:**
All Prisma and Beanie queries use explicit `select` or projection to specify exactly
which fields are retrieved. No query returns a complete model then filters at the
application layer. The database returns only what is needed.

**Anti-Patterns:**
- `AP-S2.31a` — `prisma.user.findUnique({ where: { id } })` with no `select` when `passwordHash` exists in the model.
- `AP-S2.31b` — Query all fields then delete sensitive keys before returning.

---

### S2.32 — N+1 Query Problems Are Prevented at Query Design Time

| Attribute | Value |
|-----------|-------|
| **ID** | S2.32 |
| **Priority** | High |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.28`, `S2.36` |
| **Enforced By** | Code Review |

**Standard:**
Related data required for an API response is fetched in a single query using Prisma
`include` or a JOIN — never fetched inside a loop over the primary result. N+1 queries
are identified during code review by the pattern: "for each item in the result, a query
is executed." Every such pattern is rewritten to a single query before merge.

**Anti-Patterns:**
- `AP-S2.32a` — Fetching a list of students then looping to fetch each student's applications individually.
- `AP-S2.32b` — A `forEach` or `map` over a query result that contains another `await prisma.findMany()`.

---

### S2.33 — Database Migrations Run Before Service Starts

| Attribute | Value |
|-----------|-------|
| **ID** | S2.33 |
| **Priority** | Critical |
| **Applies To** | Both Stacks |
| **Phase** | Phase 2 — Quality & Reliability |
| **Depends On** | `S5.N` |
| **Enforced By** | CI Pipeline · Deployment Scripts |

**Standard:**
`prisma migrate deploy` runs as part of the deployment pipeline before the service
process starts. The pipeline enforces the order: migrate → start. If migration fails,
deployment fails — the service does not start against an incompatible schema.

**Anti-Patterns:**
- `AP-S2.33a` — Service starting before migrations complete.
- `AP-S2.33b` — Migrations run manually in production outside the automated pipeline.

---

### S2.34 — All Financial Data Writes Are Idempotent

| Attribute | Value |
|-----------|-------|
| **ID** | S2.34 |
| **Priority** | Critical |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.30` |
| **Enforced By** | Code Review · Financial Feature Review |

**Standard:**
All service functions writing financial data are idempotent — executing the same operation
multiple times produces the same result as once. Enforced by idempotency keys (a unique
key per operation the database rejects on duplicate write) and by checking existing state
before writing. Network retries, duplicate webhooks, and user double-submits must not
create duplicate financial records.

**Anti-Patterns:**
- `AP-S2.34a` — Fund disbursement service with no existing disbursement check before creating.
- `AP-S2.34b` — Financial write operation with no idempotency key.

**Cross-References:** `S2.30`

---

### S2.35 — Soft Delete Is Mandatory for All Auditable Entities

| Attribute | Value |
|-----------|-------|
| **ID** | S2.35 |
| **Priority** | Critical |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S5.N` |
| **Enforced By** | Code Review · Architecture Review |

**Standard:**
Any entity appearing in an audit log, having financial transactions attached, referenced
by a permanent record, or subject to legal data retention requirements is never
hard-deleted. Use soft delete: `deletedAt TIMESTAMP NULL` set to current timestamp on
deletion, excluded from standard queries via `where: { deletedAt: null }`.

**Auditable entities in KSDRILL SA systems (minimum):**

| System | Auditable Entities |
|--------|--------------------|
| FundsLink Academy | Student · Funder · Application · Disbursement · Review |
| KSDRILL Reserve Bank | Account · Transaction · Officer · Approval · Report |
| Maphophe | User · Listing · Review · Verification |
| SyncUp | User · Creator · Subscription · Payment |

All other entities default to soft delete. Hard delete requires explicit justification in
the feature proposal citing why the entity carries no audit or financial obligation.

**Anti-Patterns:**
- `AP-S2.35a` — `prisma.student.delete({ where: { id } })` on any auditable entity.
- `AP-S2.35b` — Standard query without `deletedAt: null` on soft-deletable entity.

**Cross-References:** `S5.N`, `CF-16`


---

## Part 7 — Performance Standards (`S2.36`–`S2.41`)

Performance is not a post-launch concern — it is a first-deployment requirement.

---

### S2.36 — API Response Time Target Is Under Two Seconds

| Attribute | Value |
|-----------|-------|
| **ID** | S2.36 |
| **Priority** | High |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.32`, `S2.28` |
| **Enforced By** | Performance Testing · Observability Alerts |

**Standard:**
All standard read endpoints respond in under two seconds at current system scale.
Endpoints that cannot meet this target require query optimisation, an added index, or
explicit architectural justification before merge. Performance is a merge requirement.

**Anti-Patterns:**
- `AP-S2.36a` — Merging an endpoint consistently exceeding two seconds in staging with "we'll optimise later."

---

### S2.37 — Database Queries Include Only the Data Required

| Attribute | Value |
|-----------|-------|
| **ID** | S2.37 |
| **Priority** | High |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.31`, `S2.28` |
| **Enforced By** | Code Review |

**Standard:**
Queries fetch only the data required for the request. Prisma `select` specifies exactly
which fields are returned. Prisma `include` includes only the relations needed. Over-fetching
degrades performance, increases network payload, and unnecessarily exposes database content
in application memory.

---

### S2.38 — Background Jobs Handle Long-Running Operations

| Attribute | Value |
|-----------|-------|
| **ID** | S2.38 |
| **Priority** | High |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.36` |
| **Enforced By** | Architecture Review · Code Review |

**Standard:**
Any operation that cannot complete within two seconds — email delivery, PDF generation,
bulk data processing, AI inference — is handled by a background job. The API endpoint
enqueues the job and immediately returns 202 Accepted. The client polls for status or
receives a notification on completion.

**Anti-Patterns:**
- `AP-S2.38a` — Email sent synchronously inside an API request handler.
- `AP-S2.38b` — AI inference blocking API response beyond two seconds.

---

### S2.39 — Caching Is Used for Stable Reference Data

| Attribute | Value |
|-----------|-------|
| **ID** | S2.39 |
| **Priority** | Standard |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.3` |
| **Enforced By** | Architecture Review |

**Standard:**
Data read frequently and changed rarely — reference tables, system config, role
definitions — is cached using HTTP cache headers or an external cache. Cache is never
stored in service memory (violates S2.3). Cache TTL is set by change frequency — not
indefinite. Cache invalidation is explicit and triggered by the service that mutates it.

---

### S2.40 — Indexes Are Defined at Schema Time

| Attribute | Value |
|-----------|-------|
| **ID** | S2.40 |
| **Priority** | High |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S5.N` |
| **Enforced By** | Prisma Schema Review |

**Standard:**
Database indexes are defined in the Prisma schema when the model is created — not added
reactively when performance degrades in production. Every foreign key column has an index.
Every column used in a `WHERE` clause in a common query has an index.

---

### S2.41 — Rate Limiting Is Enabled on All Public Endpoints

| Attribute | Value |
|-----------|-------|
| **ID** | S2.41 |
| **Priority** | High |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.10` |
| **Enforced By** | API Gateway · Middleware Configuration |

**Standard:**
All public (unauthenticated) endpoints have rate limiting enabled from the first
deployment, configured via environment variables. Auth endpoints have stricter limits.
Rate limit responses return HTTP 429 with the standard error shape and `RATE_LIMIT_EXCEEDED`
code plus a `Retry-After` header.

**Cross-References:** `S2.22`, `S2.55`

---

## Part 8 — Resilience & Error Handling (`S2.42`–`S2.48`)

A resilient backend fails predictably, communicates failures clearly, and recovers without
human intervention wherever possible.

---

### S2.42 — All External Service Calls Have Timeouts

| Attribute | Value |
|-----------|-------|
| **ID** | S2.42 |
| **Priority** | Critical |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | — |
| **Enforced By** | Code Review |

**Standard:**
Every HTTP call to an external service — third-party APIs, payment providers, AI inference
endpoints, email services — has an explicit timeout. When a timeout fires, the error is
caught, logged to the observability layer, and the API returns 503 or 504 with the
standard error shape. No external call blocks indefinitely.

**Anti-Patterns:**
- `AP-S2.42a` — External API call with no timeout configured.

---

### S2.43 — Database Errors Are Caught and Translated

| Attribute | Value |
|-----------|-------|
| **ID** | S2.43 |
| **Priority** | Critical |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.22`, `S2.18` |
| **Enforced By** | Code Review · Global Error Handler |

**Standard:**
Database errors are caught at the service layer, translated into domain-meaningful errors,
and returned in the standard error shape. The raw database error is logged — never returned
in the response. Unique constraint violation → `DUPLICATE_RECORD`. FK protection error →
`RECORD_IN_USE`. Connection failure → `SERVICE_UNAVAILABLE`.

**Anti-Patterns:**
- `AP-S2.43a` — Prisma error propagating uncaught to the client, exposing table/column names.

---

### S2.44 — A Global Error Handler Is the Last Line of Response Defence

| Attribute | Value |
|-----------|-------|
| **ID** | S2.44 |
| **Priority** | Critical |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.22`, `S2.18` |
| **Enforced By** | Code Review · Architecture Review |

**Standard:**
A global error handler is registered at the application level and catches all unhandled
exceptions. It logs the full error with stack trace to the observability layer and returns
the standard error shape with `INTERNAL_SERVER_ERROR` and HTTP 500 to the client. No
exception reaches the client without passing through the global handler.

**Anti-Patterns:**
- `AP-S2.44a` — Unhandled promise rejections in Next.js API routes producing an empty response.

---

### S2.45 — Circuit Breaker for Critical External Dependencies

| Attribute | Value |
|-----------|-------|
| **ID** | S2.45 |
| **Priority** | Standard |
| **Applies To** | Both Stacks |
| **Phase** | Phase 2 — Quality & Reliability |
| **Depends On** | `S2.42` |
| **Enforced By** | Architecture Review |

**Standard:**
Any external service called on every request or handling financial transactions implements
a circuit breaker. The breaker trips after configurable consecutive failures, fast-fails
without calling the service, and retries after a recovery window. Prevents a failing
external dependency from cascading failures into KSDRILL SA services.

---

### S2.46 — Retry Logic for Transient Failures

| Attribute | Value |
|-----------|-------|
| **ID** | S2.46 |
| **Priority** | Standard |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.42` |
| **Enforced By** | Code Review |

**Standard:**
Transient failures — network calls, database connections under load — implement
exponential backoff retry with a maximum retry count. Retry is not applied to
non-idempotent operations. Financial writes are never retried automatically without
idempotency key protection.

---

### S2.47 — Graceful Shutdown Completes In-Flight Requests

| Attribute | Value |
|-----------|-------|
| **ID** | S2.47 |
| **Priority** | High |
| **Applies To** | Both Stacks |
| **Phase** | Phase 2 — Quality & Reliability |
| **Depends On** | `S2.30` |
| **Enforced By** | Deployment Configuration |

**Standard:**
All backend services handle SIGTERM gracefully: stop accepting new requests, complete
in-flight requests within a grace period, commit or roll back open transactions, close
database connections, then exit cleanly. Hard-exit on SIGTERM abandons in-flight
transactions leaving the database in a partial write state.

---

### S2.48 — Health Check Endpoints Are Implemented on All Services

| Attribute | Value |
|-----------|-------|
| **ID** | S2.48 |
| **Priority** | High |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | — |
| **Enforced By** | Deployment Configuration · CI |

**Standard:**
Every backend service exposes `GET /health` (public, no auth) returning HTTP 200:
`{ "status": "healthy", "database": "connected", "timestamp": "<ISO 8601>" }`.
If the database is unreachable, returns HTTP 503. The deployment platform uses this
endpoint for readiness checks.


---

## Part 9 — Security Standards (`S2.49`–`S2.55`)

Security is present from the first endpoint — not added to a working system.

---

### S2.49 — HTTPS Is Enforced in All Non-Local Environments

| Attribute | Value |
|-----------|-------|
| **ID** | S2.49 |
| **Priority** | Critical |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.10` |
| **Enforced By** | Hosting Configuration · CI |

**Standard:**
HTTPS is enforced in staging and production at the infrastructure level. HTTP requests
are redirected to HTTPS by the hosting platform — not by application code.
`Strict-Transport-Security` header is set on all responses in staging and production.

**Anti-Patterns:**
- `AP-S2.49a` — API endpoint accessible over HTTP in staging.
- `AP-S2.49b` — HTTPS redirect implemented in application code.

---

### S2.50 — Sensitive Operation Re-Verification Is Mandatory

| Attribute | Value |
|-----------|-------|
| **ID** | S2.50 |
| **Priority** | Critical |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S3.1`, `S3.N` |
| **Enforced By** | Code Review · Security Audit |

**Standard:**
For sensitive operations — financial writes, data deletion, role escalation, audit log
access, access to another user's data — the service layer re-verifies the requesting
user's current status and role against the database. A JWT may be valid while the
account was locked or role changed after token issuance. Re-verification catches that
window.

**Sensitive operations requiring re-verification:**

| Operation | Why |
|-----------|-----|
| Financial write (disbursement, payment) | Funder account may have been suspended after token issued |
| Deletion of any record | Role may have been demoted after token issued |
| Audit log access | Admin role may have been revoked |
| Application approval | Approver status may have changed |
| Action on another user's data | Ownership and role must be current |

**Anti-Patterns:**
- `AP-S2.50a` — Financial write checking only JWT payload role without database re-verification.

**Cross-References:** `S3.N` (auth re-verification)

---

### S2.51 — Input Length and Type Limits Are Enforced at the API Boundary

| Attribute | Value |
|-----------|-------|
| **ID** | S2.51 |
| **Priority** | High |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.23` |
| **Enforced By** | Validation Schema · Code Review |

**Standard:**
All string fields have maximum length. All numeric fields have min/max value constraints.
All array fields have maximum length. Limits are defined in the OpenAPI spec and enforced
by the validation schema. Prevents oversized payloads, database truncation, and
denial-of-service via payload size.

**Anti-Patterns:**
- `AP-S2.51a` — A text field with no `maxLength` constraint.

---

### S2.52 — Secrets Are Never Logged

| Attribute | Value |
|-----------|-------|
| **ID** | S2.52 |
| **Priority** | Critical |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.56` |
| **Enforced By** | Code Review · Security Audit · Log Scanning |

**Standard:**
Passwords, tokens, API keys, and session identifiers are never written to any log output.
Request logging middleware scrubs the `Authorization` header before logging. Validation
error logging does not include raw values for sensitive fields. A log entry containing
a secret is a security incident.

**Anti-Patterns:**
- `AP-S2.52a` — `console.log(req.headers)` — logs the Authorization header.
- `AP-S2.52b` — Validation failure logging including the password field value.

---

### S2.53 — Ownership Is Validated Before Any User-Scoped Operation

| Attribute | Value |
|-----------|-------|
| **ID** | S2.53 |
| **Priority** | Critical |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.1`, `S2.25` |
| **Enforced By** | Code Review · Security Audit |

**Standard:**
Any operation modifying or reading a user-owned resource validates that the requesting
user owns that resource before executing. Validation is in the service layer — not only
in the route handler guard. The service queries the resource, confirms owner ID matches
the authenticated user ID, and rejects with 403 on mismatch.

**Anti-Patterns:**
- `AP-S2.53a` — Route-level guard checking JWT role but not specific resource ownership.

**Cross-References:** `S2.25`, `S2.50`

---

### S2.54 — Password Storage Uses bcrypt at Minimum Cost Factor 12

| Attribute | Value |
|-----------|-------|
| **ID** | S2.54 |
| **Priority** | Critical |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S3.N` |
| **Enforced By** | Code Review · Security Audit |

**Standard:**
Passwords are hashed using bcrypt with minimum cost factor 12 before storage. Plain text
passwords are never stored, logged, or transmitted beyond the initial authentication
request. Hash comparison uses the bcrypt comparison function — not string comparison.

**Anti-Patterns:**
- `AP-S2.54a` — bcrypt cost factor below 12.
- `AP-S2.54b` — MD5 or SHA-256 used for password hashing.

---

### S2.55 — Brute Force Protection on Auth Endpoints

| Attribute | Value |
|-----------|-------|
| **ID** | S2.55 |
| **Priority** | Critical |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.41` |
| **Enforced By** | Auth Middleware · Rate Limiter |

**Standard:**
Auth endpoints (login, password reset, token refresh) have stricter rate limits than
general API endpoints. Failed attempts are counted per IP per time window. Progressive
delay applied after three consecutive failures. After ten consecutive failures, IP is
temporarily blocked. All thresholds are configurable via environment variables.

**Cross-References:** `S2.41`, `S3.N`

---

## Part 10 — Observability (`S2.56`–`S2.62`)

A system that cannot be observed cannot be debugged. Observability is an architectural
requirement from the first deployment — not an operational concern added later.

---

### S2.56 — Structured JSON Logging Is Mandatory

| Attribute | Value |
|-----------|-------|
| **ID** | S2.56 |
| **Priority** | Critical |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.52` |
| **Enforced By** | Logger Configuration · CI Log Format Check |

**Standard:**
All backend services emit logs in structured JSON. Every log entry includes mandatory
fields: `timestamp` (ISO 8601), `level` (debug/info/warn/error), `message`, `requestId`
(X-Request-ID), `service` (service name), and for errors: `errorCode`, `stack`. Logs
are emitted to stdout — never to files, never to a database.

**Anti-Patterns:**
- `AP-S2.56a` — `console.log('User logged in')` — unstructured, missing mandatory fields.
- `AP-S2.56b` — Writing logs to a file rather than stdout.

---

### S2.57 — Every Request Gets a Unique X-Request-ID

| Attribute | Value |
|-----------|-------|
| **ID** | S2.57 |
| **Priority** | High |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.56` |
| **Enforced By** | Request ID Middleware |

**Standard:**
Every incoming request receives a unique `X-Request-ID`. If the client sends one, it is
used. If not, the server generates a UUID4. The ID is included in every log entry for the
request duration and in every outgoing call to downstream services. Returned in response
headers. Enables full request tracing across services.

---

### S2.58 — Errors Are Reported to the External Observability Platform

| Attribute | Value |
|-----------|-------|
| **ID** | S2.58 |
| **Priority** | High |
| **Applies To** | Both Stacks |
| **Phase** | Phase 2 — Quality & Reliability |
| **Depends On** | `S2.56` |
| **Enforced By** | Sentry Configuration · Better Stack Configuration |

**Standard:**
All unhandled exceptions and caught errors at `error` level or above are reported to the
configured external observability platform (Sentry for error tracking, Better Stack for
log aggregation). Configured from day one — not after the first production incident.
Staging errors are also reported.

---

### S2.59 — Response Times Are Measured and Alerted

| Attribute | Value |
|-----------|-------|
| **ID** | S2.59 |
| **Priority** | High |
| **Applies To** | Both Stacks |
| **Phase** | Phase 2 — Quality & Reliability |
| **Depends On** | `S2.36` |
| **Enforced By** | Performance Middleware · Alert Configuration |

**Standard:**
Response time is measured for every request and included in the structured log as
`durationMs`. Alerts fire when the P95 response time for any endpoint exceeds two seconds
for more than one minute.

---

### S2.60 — Slow Request Query Count and Duration Are Logged

| Attribute | Value |
|-----------|-------|
| **ID** | S2.60 |
| **Priority** | Standard |
| **Applies To** | Both Stacks |
| **Phase** | Phase 2 — Quality & Reliability |
| **Depends On** | `S2.56`, `S2.28` |
| **Enforced By** | Prisma Query Logging |

**Standard:**
For any request exceeding one second total, the number of database queries and individual
durations are logged. Enables instant identification of N+1 problems and missing indexes
in production. Prisma query logging is at `query` level in staging, `warn`/`error` in
production.

---

### S2.61 — Alert Thresholds Are Configured Before First Production Deployment

| Attribute | Value |
|-----------|-------|
| **ID** | S2.61 |
| **Priority** | High |
| **Applies To** | Both Stacks |
| **Phase** | Phase 2 — Quality & Reliability |
| **Depends On** | `S8.N` |
| **Enforced By** | Platform Reliability Constitution C8 |

**Standard:**
The following alert thresholds are active before first production deployment:

| Metric | Threshold |
|--------|-----------|
| API error rate | >1% of requests in any 5-minute window |
| P95 response time | >2 seconds sustained >1 minute |
| Database connection failures | Any failure |
| Health check failures | 2 consecutive failures |
| Disk usage | >80% |

---

### S2.62 — Audit Logs Are Written for All Sensitive Operations

| Attribute | Value |
|-----------|-------|
| **ID** | S2.62 |
| **Priority** | Critical |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.35`, `S5.N` |
| **Enforced By** | Code Review · Security Audit |

**Standard:**
Every sensitive operation writes an audit log record: `userId`, `action`
(CREATE/READ/UPDATE/DELETE), `entity`, `entityId`, `timestamp`, `ipAddress`, `metadata`
(JSON). Audit log records are never deleted — the table is append-only. The soft delete
standard (S2.35) exists partly because hard-deleting a record with audit log entries
creates an incomplete audit trail.

**Cross-References:** `S2.35`, `S5.N`


---

## Part 11 — FastAPI-Specific Standards (`S2.63`–`S2.69`)

Applies exclusively to the Angular + FastAPI stack: FundsLink Academy and KSDRILL
Reserve Bank. Complements universal backend standards (Parts 1–10).

---

### S2.63 — FastAPI Application Structure Is Domain-Driven

| Attribute | Value |
|-----------|-------|
| **ID** | S2.63 |
| **Priority** | Critical |
| **Applies To** | Angular Stack |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.4` |
| **Enforced By** | Code Review · Module Structure |

**Standard:**
The FastAPI application is organised by domain, not by technical layer. Each domain has
its own directory with: `router.py`, `service.py`, Pydantic models, and domain utilities.
Shared utilities (database, auth, logging) live in `core/`. The entry point `main.py`
registers routers and configures middleware only — no business logic.

```
app/
├── main.py
├── core/
│   ├── database.py
│   ├── security.py
│   └── config.py
├── students/
│   ├── router.py
│   ├── service.py
│   └── models.py
└── scholarships/
    ├── router.py
    ├── service.py
    └── models.py
```

**Anti-Patterns:**
- `AP-S2.63a` — Flat structure with all routes in `routes.py` and all logic in `services.py`.

---

### S2.64 — FastAPI Dependency Injection Manages All Shared Resources

| Attribute | Value |
|-----------|-------|
| **ID** | S2.64 |
| **Priority** | Critical |
| **Applies To** | Angular Stack |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S1.59` |
| **Enforced By** | Code Review |

**Standard:**
Database sessions, authentication context, current user objects, and all request-scoped
shared resources are provided via `Depends()`. No shared resource is instantiated inside
a route handler or service function. FastAPI manages the lifecycle ensuring proper cleanup
regardless of success or failure.

**Anti-Patterns:**
- `AP-S2.64a` — Database session created inside route handler body and manually closed.

---

### S2.65 — FastAPI Routers Use Consistent Prefix and Tag Conventions

| Attribute | Value |
|-----------|-------|
| **ID** | S2.65 |
| **Priority** | Standard |
| **Applies To** | Angular Stack |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.12`, `S2.76` |
| **Enforced By** | Code Review |

**Standard:**
Every router is registered with a versioned prefix (`/api/v1/`) and a descriptive tag
matching the domain name. Prefixes are set at router registration in `main.py` — not
hardcoded in individual route decorators. Routes within a router are relative paths
without the version prefix.

---

### S2.66 — FastAPI Background Tasks for Post-Response Operations

| Attribute | Value |
|-----------|-------|
| **ID** | S2.66 |
| **Priority** | High |
| **Applies To** | Angular Stack |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.38` |
| **Enforced By** | Code Review |

**Standard:**
Operations that occur after the API response is sent — email notifications, audit log
writes to external systems, analytics events — use FastAPI's `BackgroundTasks`. The route
handler adds the background task and returns the response. The task runs after the
response is sent without blocking the client.

---

### S2.67 — Pydantic Settings Manages All Environment Configuration

| Attribute | Value |
|-----------|-------|
| **ID** | S2.67 |
| **Priority** | Critical |
| **Applies To** | Angular Stack |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.10`, `S1.68` |
| **Enforced By** | Code Review |

**Standard:**
All environment configuration in FastAPI services uses a Pydantic `BaseSettings` class
in `core/config.py`. All required variables are declared as typed fields. Missing variables
cause a startup failure with a clear error identifying what is missing — before the service
accepts any request.

**Anti-Patterns:**
- `AP-S2.67a` — `os.getenv('DATABASE_URL')` called inline at the point of use.

---

### S2.68 — FastAPI AI/ML Service Is a Separate Router Group

| Attribute | Value |
|-----------|-------|
| **ID** | S2.68 |
| **Priority** | High |
| **Applies To** | Angular Stack |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.4`, `S2.7` |
| **Enforced By** | Code Review · Architecture Review |

**Standard:**
AI and ML capabilities — LangChain RAG, embedding generation, scholarship matching,
prediction endpoints — are grouped in a dedicated `ai/` or `intelligence/` router and
service module. AI services may depend on domain services (reading from student or
scholarship domain) but domain services never depend on AI services. AI capabilities
can be replaced, upgraded, or disabled without touching any core domain logic.

---

### S2.69 — FastAPI Exception Handlers Are Registered Globally

| Attribute | Value |
|-----------|-------|
| **ID** | S2.69 |
| **Priority** | Critical |
| **Applies To** | Angular Stack |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.44` |
| **Enforced By** | Code Review |

**Standard:**
Exception handlers for all custom exception classes and for generic `Exception` are
registered on the FastAPI application object in `main.py`. Every handler returns the
standard error response shape (S2.22). No route handler catches raw `Exception` and
formats its own error response.

---

## Part 12 — Next.js API Route Standards (`S2.70`–`S2.75`)

Applies exclusively to the Next.js stack: Maphophe and SyncUp.

---

### S2.70 — API Routes Live in `app/api/` Using App Router Convention

| Attribute | Value |
|-----------|-------|
| **ID** | S2.70 |
| **Priority** | Critical |
| **Applies To** | Next.js Stack |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | — |
| **Enforced By** | Code Review · File Structure |

**Standard:**
All Next.js API routes use the App Router convention (`app/api/`). Pages Router
(`pages/api/`) is not used. Each route file exports only named HTTP method handlers
(`GET`, `POST`, `PUT`, `PATCH`, `DELETE`). Route handlers delegate immediately to service
functions — no business logic in the route file.

```
app/api/v1/
├── students/
│   ├── route.ts          # GET (list), POST (create)
│   └── [id]/route.ts     # GET (single), PATCH, DELETE
└── scholarships/
    ├── route.ts
    └── [id]/route.ts
```

**Anti-Patterns:**
- `AP-S2.70a` — Business logic written inside the route handler function.

---

### S2.71 — Next.js API Routes Validate Session Before Any Service Call

| Attribute | Value |
|-----------|-------|
| **ID** | S2.71 |
| **Priority** | Critical |
| **Applies To** | Next.js Stack |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S3.N` |
| **Enforced By** | Code Review |

**Standard:**
All protected Next.js API routes validate the session using NextAuth's `auth()` function
at the start of the route handler — before any service function is called. Invalid or
absent session returns the standard error shape with HTTP 401.

**Anti-Patterns:**
- `AP-S2.71a` — Protected route handler calling service before session validation.

---

### S2.72 — Server Actions Are Used Only for Form Mutations

| Attribute | Value |
|-----------|-------|
| **ID** | S2.72 |
| **Priority** | Standard |
| **Applies To** | Next.js Stack |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.1`, `S2.23` |
| **Enforced By** | Code Review |

**Standard:**
Server Actions are used exclusively for form-based mutations from Server Components.
Client Components use API routes. All Server Actions validate session and input before
calling service functions — they are not exempt from the validation boundary.

---

### S2.73 — Next.js API Routes Use the Shared Error Handler

| Attribute | Value |
|-----------|-------|
| **ID** | S2.73 |
| **Priority** | Critical |
| **Applies To** | Next.js Stack |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.22`, `S2.44` |
| **Enforced By** | Code Review |

**Standard:**
All Next.js API route handlers wrap execution in try-catch. Caught errors are passed to
a shared error handler utility that formats them into the standard error shape and returns
the appropriate `NextResponse`. The shared handler is used across all route files — no
route implements its own error formatting.

---

### S2.74 — Next.js Middleware Handles Auth at the Edge

| Attribute | Value |
|-----------|-------|
| **ID** | S2.74 |
| **Priority** | High |
| **Applies To** | Next.js Stack |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S3.N`, `S2.6` |
| **Enforced By** | Code Review |

**Standard:**
Next.js middleware (`middleware.ts`) handles route-level auth checks using NextAuth.
Middleware confirms the session exists and redirects unauthenticated requests to login.
Middleware does not check roles or resource ownership — those decisions happen in the
service layer.

---

### S2.75 — Prisma Client Is a Singleton in Next.js

| Attribute | Value |
|-----------|-------|
| **ID** | S2.75 |
| **Priority** | Critical |
| **Applies To** | Next.js Stack |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.28` |
| **Enforced By** | Code Review |

**Standard:**
The Prisma client is instantiated once as a singleton in `lib/prisma.ts` and imported
from that single location throughout the application. In development, the global object
prevents hot-reload from creating multiple instances. Multiple Prisma instances exhaust
the database connection pool under load.

**Anti-Patterns:**
- `AP-S2.75a` — `new PrismaClient()` called inside a route handler or service function.

---

## Part 13 — API Versioning Governance (`S2.76`–`S2.80`)

Versioning governs how the backend evolves its public contract without breaking consumers.
Applied from the first endpoint — retrofitting versioning to an existing API requires
breaking all existing clients simultaneously.

---

### S2.76 — All API Endpoints Are Versioned from the First Deployment

| Attribute | Value |
|-----------|-------|
| **ID** | S2.76 |
| **Priority** | Critical |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.11` |
| **Enforced By** | Code Review |

**Standard:**
All API endpoints are prefixed with `/api/v1/` from the first endpoint implemented.
Version is in the URL path — not in a header or query parameter. An unversioned endpoint
cannot be added to any KSDRILL SA system.

**Anti-Patterns:**
- `AP-S2.76a` — Endpoint at `/api/students` without the version prefix.

---

### S2.77 — Breaking vs Non-Breaking Changes Are Formally Classified

| Attribute | Value |
|-----------|-------|
| **ID** | S2.77 |
| **Priority** | Critical |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.76`, `S2.9` |
| **Enforced By** | Code Review · API Review |

**Standard:**
Every API change is classified before implementation.

**Non-breaking (permitted in existing version):**
- Adding a new optional field to a response
- Adding a new optional request parameter
- Adding a new endpoint
- Relaxing a validation constraint

**Breaking (require a new version):**
- Removing or renaming a response or request field
- Changing a field's type
- Tightening a validation constraint
- Changing an endpoint's URL or HTTP method
- Changing the error response shape

Breaking changes are never made to an existing API version.

**Anti-Patterns:**
- `AP-S2.77a` — Response field renamed in `/api/v1/` without creating `/api/v2/`.

---

### S2.78 — API Deprecation Requires Announced Sunset Period

| Attribute | Value |
|-----------|-------|
| **ID** | S2.78 |
| **Priority** | High |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.77`, `S2.76` |
| **Enforced By** | API Governance |

**Standard:**
When a new version is introduced and the previous is to be retired, the retirement follows
a minimum three-month sunset period. During sunset: the deprecated version continues to
function, every response includes a `Deprecation` header with the sunset date, the OpenAPI
spec is marked deprecated, and all internal consumers are migrated before the sunset date.

---

### S2.79 — v1 and v2 Versions Coexist During Transition

| Attribute | Value |
|-----------|-------|
| **ID** | S2.79 |
| **Priority** | High |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.78` |
| **Enforced By** | Deployment Configuration |

**Standard:**
When a new version is introduced, the previous version continues from the same deployment.
Version routing directs requests to the appropriate handlers. Shared service logic is
called by both versions — the service layer is version-agnostic. Only route handlers
and response serialisation differ between versions.

---

### S2.80 — New Features Default to the Current Latest Version

| Attribute | Value |
|-----------|-------|
| **ID** | S2.80 |
| **Priority** | Standard |
| **Applies To** | Both Stacks |
| **Phase** | Phase 1 — Core Architecture |
| **Depends On** | `S2.76` |
| **Enforced By** | Code Review |

**Standard:**
New endpoints are always added to the current latest API version. New endpoints are never
added to a deprecated version. If the new feature introduces a breaking change, a new
version is created. Otherwise, the new endpoint is added to the existing latest version.


---

## Anti-Patterns Index

| ID | Anti-Pattern | Standard | Priority |
|----|-------------|----------|----------|
| AP-S2.1a | Business logic inside route handler | S2.1 | Critical |
| AP-S2.1b | Authorization check inside a database query | S2.1 | Critical |
| AP-S2.1c | Service function formatting the HTTP response | S2.1 | High |
| AP-S2.2a | Next.js API route calling `prisma.findMany()` directly | S2.2 | Critical |
| AP-S2.2b | FastAPI route calling query function without service module | S2.2 | Critical |
| AP-S2.2c | Service function building an HTTP response object | S2.2 | High |
| AP-S2.3a | Module-level variables accumulating request data | S2.3 | Critical |
| AP-S2.3b | In-memory user session storage in a service module | S2.3 | Critical |
| AP-S2.4a | Student service directly calling scholarship service functions | S2.4 | High |
| AP-S2.4b | Single service file handling two unrelated domains | S2.4 | High |
| AP-S2.5a | TypeScript service function with no return type annotation | S2.5 | High |
| AP-S2.6a | Middleware filtering query results based on user role | S2.6 | High |
| AP-S2.6b | Middleware applying a business rule before passing to handler | S2.6 | High |
| AP-S2.7a | New user role added by modifying existing permission class | S2.7 | Critical |
| AP-S2.7b | New notification channel added by modifying existing service | S2.7 | Critical |
| AP-S2.7c | New report type as conditional branch inside existing function | S2.7 | High |
| AP-S2.8a | Module-level variable storing per-request state | S2.8 | Critical |
| AP-S2.8b | Hardcoded value that differs between instances | S2.8 | Critical |
| AP-S2.9a | Column renamed without two-phase migration plan | S2.9 | Critical |
| AP-S2.9b | Non-nullable column added without database default | S2.9 | Critical |
| AP-S2.9c | API response field removed without versioning plan | S2.9 | Critical |
| AP-S2.10a | `if (NODE_ENV === 'production')` blocks in application code | S2.10 | Critical |
| AP-S2.10b | Database connection string hardcoded in codebase | S2.10 | Critical |
| AP-S2.10c | API key committed to version control | S2.10 | Critical |
| AP-S2.11a | OpenAPI spec written after implementing the endpoint | S2.11 | Critical |
| AP-S2.11b | Frontend development started before OpenAPI spec is approved | S2.11 | Critical |
| AP-S2.12a | Verb-based endpoint: `/api/v1/getStudentProfile` | S2.12 | High |
| AP-S2.12b | GET used for operations that mutate state | S2.12 | Critical |
| AP-S2.12c | More than two levels of URL nesting | S2.12 | Standard |
| AP-S2.13a | Child routes protected only by parent router middleware | S2.13 | Critical |
| AP-S2.13b | Endpoint "protected" by required body fields only | S2.13 | Critical |
| AP-S2.14a | `prisma.student.findMany()` with no `take` or `skip` | S2.14 | High |
| AP-S2.14b | List endpoint without pagination "because the set is small" | S2.14 | High |
| AP-S2.16a | Full Prisma model returned as API response | S2.16 | Critical |
| AP-S2.16b | Response including `passwordHash` or any secret field | S2.16 | Critical |
| AP-S2.17a | `cors({ origin: '*' })` in production | S2.17 | Critical |
| AP-S2.17b | CORS allowed origins hardcoded in application code | S2.17 | Critical |
| AP-S2.18a | Raw database error message in API response | S2.18 | Critical |
| AP-S2.18b | `error.message` or `error.stack` sent to client | S2.18 | Critical |
| AP-S2.19a | Object returned at root without `data` wrapper | S2.19 | Critical |
| AP-S2.19b | `data: null` on a 200 response | S2.19 | High |
| AP-S2.20a | `data: null` when list is empty | S2.20 | Critical |
| AP-S2.20b | Raw array returned without pagination envelope | S2.20 | Critical |
| AP-S2.21a | POST endpoint returning 200 instead of 201 | S2.21 | High |
| AP-S2.21b | POST returning only the new resource's ID | S2.21 | High |
| AP-S2.22a | Error response missing `code` or `status` field | S2.22 | Critical |
| AP-S2.22b | Freeform `code` string not from the shared enum | S2.22 | High |
| AP-S2.22c | Different error shapes from different endpoints | S2.22 | Critical |
| AP-S2.23a | `request.body.fieldName` accessed without prior validation | S2.23 | Critical |
| AP-S2.23b | Validation skipped for internal API calls between services | S2.23 | Critical |
| AP-S2.23c | Third-party API responses trusted without shape validation | S2.23 | High |
| AP-S2.24a | Manually written Zod schema diverging from OpenAPI spec | S2.24 | High |
| AP-S2.24b | Pydantic model written before OpenAPI spec is finalised | S2.24 | High |
| AP-S2.26a | Validation error with no field-level detail | S2.26 | High |
| AP-S2.27a | String interpolation in a database query | S2.27 | Critical |
| AP-S2.27b | Service functions sanitising already-validated input | S2.27 | Standard |
| AP-S2.28a | Raw SQL via `pg` or `psycopg2` in service code | S2.28 | Critical |
| AP-S2.28b | Multiple Prisma client instances per service | S2.28 | Critical |
| AP-S2.28c | `prisma.findMany()` with no `where` clause in user-facing endpoint | S2.28 | Critical |
| AP-S2.28d | Standard query without `deletedAt: null` on soft-deletable entity | S2.28 | Critical |
| AP-S2.28e | Raw SQL in a service file, route handler, or middleware | S2.28e | High |
| AP-S2.28ea | Repository file created without documented ORM justification | S2.28e | High |
| AP-S2.28f | Raw SQL using string interpolation in any form | S2.28f | Critical |
| AP-S2.28fa | Raw SQL missing `deleted_at IS NULL` on a soft-deletable table | S2.28f | Critical |
| AP-S2.28fb | Raw SQL query with no justification comment | S2.28f | High |
| AP-S2.28fc | Raw SQL result returned without schema validation | S2.28f | Critical |
| AP-S2.29a | Raw PyMongo operations inside FastAPI service | S2.29 | Critical |
| AP-S2.29b | Beanie document storing PostgreSQL FK as ObjectId | S2.29 | High |
| AP-S2.30a | Two `prisma.create()` calls without `$transaction()` | S2.30 | Critical |
| AP-S2.30b | Manual undo of first write after second write fails | S2.30 | Critical |
| AP-S2.31a | `prisma.user.findUnique()` with no `select` when `passwordHash` exists | S2.31 | Critical |
| AP-S2.31b | Query all fields then delete sensitive keys before returning | S2.31 | Critical |
| AP-S2.32a | Loop over result set making individual queries per item (N+1) | S2.32 | High |
| AP-S2.32b | `forEach` over query result containing another `prisma.findMany()` | S2.32 | High |
| AP-S2.33a | Service starting before migrations complete | S2.33 | Critical |
| AP-S2.33b | Migrations run manually in production outside pipeline | S2.33 | Critical |
| AP-S2.34a | Disbursement service with no existing disbursement check | S2.34 | Critical |
| AP-S2.34b | Financial write with no idempotency key | S2.34 | Critical |
| AP-S2.35a | `prisma.student.delete()` on any auditable entity | S2.35 | Critical |
| AP-S2.35b | Standard query without `deletedAt: null` on soft-deletable entity | S2.35 | Critical |
| AP-S2.36a | Merging endpoint consistently exceeding 2s in staging | S2.36 | High |
| AP-S2.38a | Email sent synchronously inside API request handler | S2.38 | High |
| AP-S2.38b | AI inference blocking API response beyond 2 seconds | S2.38 | High |
| AP-S2.42a | External API call with no timeout configured | S2.42 | Critical |
| AP-S2.43a | Prisma error propagating uncaught to client response | S2.43 | Critical |
| AP-S2.44a | Unhandled promise rejection producing empty response | S2.44 | Critical |
| AP-S2.49a | API endpoint accessible over HTTP in staging | S2.49 | Critical |
| AP-S2.49b | HTTPS redirect in application code instead of infrastructure | S2.49 | High |
| AP-S2.50a | Financial write checking only JWT payload without DB re-verify | S2.50 | Critical |
| AP-S2.51a | String field with no `maxLength` constraint | S2.51 | High |
| AP-S2.52a | `console.log(req.headers)` — logs the Authorization header | S2.52 | Critical |
| AP-S2.52b | Validation failure logging including password field value | S2.52 | Critical |
| AP-S2.53a | Route guard checking JWT role but not resource ownership | S2.53 | Critical |
| AP-S2.54a | bcrypt cost factor below 12 | S2.54 | Critical |
| AP-S2.54b | MD5 or SHA-256 used for password hashing | S2.54 | Critical |
| AP-S2.56a | `console.log('User logged in')` — unstructured log | S2.56 | Critical |
| AP-S2.56b | Logs written to file rather than stdout | S2.56 | High |
| AP-S2.63a | Flat FastAPI structure with no domain boundaries | S2.63 | Critical |
| AP-S2.64a | Database session created inside route handler body | S2.64 | Critical |
| AP-S2.67a | `os.getenv('DATABASE_URL')` called inline at point of use | S2.67 | Critical |
| AP-S2.70a | Business logic inside Next.js route handler function | S2.70 | Critical |
| AP-S2.71a | Protected route calling service before session validation | S2.71 | Critical |
| AP-S2.75a | `new PrismaClient()` inside route handler or service function | S2.75 | Critical |
| AP-S2.76a | Endpoint at `/api/students` without version prefix | S2.76 | Critical |
| AP-S2.77a | Response field renamed in `/api/v1/` without creating `/api/v2/` | S2.77 | Critical |

---

## Cross-Constitution Dependency Map

**C2 depends on:**
- `C0` — Governance, terminology, amendment protocol
- `C1` — Feature lifecycle (S1.27), one concern (S1.3), TypeScript (S1.48–S1.56), Python (S1.57–S1.63)
- `C3` — Auth strategy (S3.1), JWT standard, sensitive operation re-verification
- `C5` — PostgreSQL and Prisma standard, MongoDB and Beanie standard, migration governance,
  soft delete, audit log, index strategy, two-layer integrity enforcement

**The following constitutions depend on C2:**
- `C4` Frontend — frontend consumes API contracts defined here
- `C6` Full-Stack Architecture — request flows and cross-stack communication reference C2 standards
- `C7` Testing — API testing shapes defined by response contracts in Part 4
- `C8` Platform Reliability — deployment pipeline references S2.33, S2.47, S2.48, S2.61
- `C9` Product & Feature — API versioning governance (Part 13) constrains product breaking-change decisions
- `C10` AI Collaboration — AI cannot propose bypassing S2.23, S2.2, or S2.50

---

## Amendment Log

| Version | Date | Change | Reason |
|---------|------|--------|--------|
| v1.0 | 2026-05-08 | Initial lock | New constitution. Incorporates service layer architecture (Part 1), extension-first backend design extracted from Ubuntu Campus Clinic system design (Part 2), API contract standards (Part 3), standard response shape contract (Part 4), validation layer as architectural boundary (Part 5), database access including soft delete and idempotent financial writes (Part 6), performance (Part 7), resilience (Part 8), security including sensitive operation re-verification (Part 9), observability (Part 10), FastAPI-specific standards (Part 11), Next.js API route standards (Part 12), API versioning governance (Part 13). |
| v1.1 | 2026-05-08 | Added S2.28e (Raw SQL in repository files only) and S2.28f (Four safety requirements for raw SQL). Added 6 new anti-patterns (AP-S2.28e through AP-S2.28fc). | Industry best practice: ORM-first with governed raw SQL escape hatch for complex aggregations, window functions, CTEs, full-text search, and reporting queries that exceed ORM capability. Pure ORM prohibition is too restrictive for production analytical queries in FundsLink Academy and KSDRILL Reserve Bank. |

---

> **LOCKED — v1.0 — 2026-05-08**
>
> This document is locked. No standard may be added, removed, or modified
> without following the Amendment Protocol defined in C0 §8.
> Amendments take effect only after commit to `system-design-template`
> with a version bump and amendment log entry.
