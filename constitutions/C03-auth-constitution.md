# C3 — Auth Constitution

---

| Attribute          | Value                                                              |
|--------------------|--------------------------------------------------------------------|
| **Document**       | C3 — Auth Constitution                                             |
| **Organisation**   | KSDRILL SA                                                         |
| **Version**        | v1.0                                                               |
| **Status**         | LOCKED                                                             |
| **Locked**         | 2026-05-08                                                         |
| **Next Review**    | 2026-08-08                                                         |
| **Applies To**     | All Systems · Both Stacks                                          |
| **Paired With**    | C3 — Auth Implementation Guide                                     |

---

> *"Authentication is the first system. Every platform built on top of it inherits its security or its vulnerabilities."*

---

## Opening Statement

Authentication is not a feature. It is the foundation that every other system component assumes is correct. If authentication is inconsistent, insecure, or confusingly implemented across the two stacks, every system built on top of it is compromised before a single user interacts with it.

This constitution governs how identity is verified, how sessions are established and maintained, how tokens are stored and rotated, how roles are assigned and enforced, and how every authentication event is logged — across all KSDRILL SA platforms. The two stacks (Next.js and Angular+FastAPI) use fundamentally different authentication strategies because their architectures demand it. NextAuth.js with database-backed sessions fits the unified Next.js full-stack model. JWT with split token storage fits the decoupled Angular+FastAPI enterprise model. Both strategies are governed here with equal rigour.

This constitution does not govern the frontend components that trigger authentication flows — that is C4. It does not govern how the service layer checks authentication headers — that is C2. It does not govern where authentication data is stored at the database level — that is C5 (though the assignment is mandated here: PostgreSQL only). What this constitution governs is the authentication system itself: its strategies, its token lifecycle, its security baseline, and its audit trail.

This is the most cross-referenced constitution in the system. C2 depends on it for middleware. C4 depends on it for route guards and auth state. C6 depends on it for integration flows. C7 depends on it for auth test requirements. C8 depends on it for security alerts. The Auth Override Rule in C0 §7.3 designates this constitution as holding supreme authority over all security-touching decisions regardless of constitutional hierarchy. No other constitution, implementation guide, overlay, AI recommendation, or developer preference overrides a standard in this document.

The paired implementation guide contains the concrete code for every strategy, every endpoint, every token rotation flow, and every audit log schema. This document contains the governing standards and their rationale. When you need to know what authentication must do, read this. When you need to know how to build it, read the implementation guide.

---

## Table of Contents

| Part | Title | Standards |
|------|-------|-----------|
| Part 0 | Authentication Strategy Selection | S3.1–S3.4 |
| Part 1 | NextAuth.js — Next.js Stack | S3.5–S3.12 |
| Part 2 | JWT Authentication — Angular+FastAPI Stack | S3.13–S3.20 |
| Part 3 | Role-Based Access Control | S3.21–S3.25 |
| Part 4 | OAuth & External Identity Providers | S3.26–S3.27 |
| Part 5 | Security Baseline | S3.28–S3.32 |
| Part 6 | Audit Logging & Governance | S3.33–S3.36 |
| Anti-Patterns Index | — | AP-S3.* |
| Cross-Constitution Dependency Map | — | — |
| Amendment Log | — | — |

---

## Part 0 — Authentication Strategy Selection (`S3.1`–`S3.4`)

The strategy decision is made once at system design time, is immutable for the lifetime of that system's major version, and is driven entirely by stack assignment. There is no scenario in which a KSDRILL SA system runs two auth strategies simultaneously or switches strategy mid-build.

---

### S3.1 — One Authentication Strategy Per System, Determined by Stack

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S3.1 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S6.1` (stack assignment drives strategy selection) |
| **Enforced By** | Code Review · Architecture Review |

**Standard:**
Every KSDRILL SA system uses exactly one authentication strategy, determined by its technology stack. Next.js systems use NextAuth.js with database-backed sessions. Angular+FastAPI systems use RS256-signed JWT issued by FastAPI. No system runs two strategies simultaneously. No stack changes its strategy without a Major constitutional amendment to both C3 and C6.

**Rationale:**
Two auth strategies in one system create session validation ambiguity, duplicated security surfaces, and untestable edge cases where one strategy's tokens are presented to the other strategy's validation logic. The single-strategy rule is the only engineering position that makes auth behaviour predictable across all scenarios.

**Anti-Patterns:**
- `AP-S3.1a` — Implementing NextAuth.js in an Angular+FastAPI system because "it's simpler" — Angular's interceptor model requires server-issued JWTs; NextAuth cannot work correctly without the Next.js runtime.
- `AP-S3.1b` — Running "temporary" JWT alongside NextAuth during a migration — dual strategies in one system create a security gap for the entire duration of the migration.

**Cross-References:** `S6.1` (stack assignment), `S6.2` (Angular stack criteria), `C0 §7.3` (Auth Override Rule)

---

### S3.2 — All Authentication Data in PostgreSQL — Never MongoDB, Never Redis as Primary

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S3.2 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S5.4` (auth data PostgreSQL assignment), `S5.3` (financial data rule — same principle) |
| **Enforced By** | Code Review · Schema Review |

**Standard:**
Every piece of authentication data — user credentials, password hashes, JWT refresh tokens, reset tokens, email verification tokens, sessions, role assignments — resides in PostgreSQL. Redis is used as a cache and deny-list only (TTL-backed, non-primary). MongoDB is never used for authentication data under any circumstance, even on systems where MongoDB exists for AI-generated content.

**Rationale:**
Authentication requires ACID consistency. Token validation, session invalidation, and refresh token rotation all require transactional guarantees that prevent race conditions. MongoDB's eventual consistency makes it structurally unsuitable. Redis without persistence creates a recovery failure on restart — all sessions lost, all users logged out simultaneously.

**Anti-Patterns:**
- `AP-S3.2a` — Storing session data or refresh tokens in MongoDB because "the system already has Mongo" — the database choice for auth is mandatory, not opportunistic.
- `AP-S3.2b` — Using Redis as the primary session store without PostgreSQL backing — Redis restart clears all sessions with no recovery path.

**Cross-References:** `S5.4` (PostgreSQL for auth data), `S5.3` (financial data — same reasoning), `CF-07` (Common Failure Register)

---

### S3.3 — Password Hashing — bcrypt at Minimum Cost Factor 12

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S3.3 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | — |
| **Enforced By** | Code Review · Security Audit |

**Standard:**
Every password on every system is hashed with bcrypt at cost factor 12 or higher. The cost factor is read from the `BCRYPT_ROUNDS` environment variable — never hardcoded. MD5, SHA-1, SHA-256, reversible encryption, and plaintext storage are absolutely forbidden. Cost factor can be increased across environments without code changes.

**Rationale:**
At cost factor 12, each hash takes approximately 300ms — imperceptible to users during login, computationally infeasible for an attacker with a stolen database. Lower cost factors reduce attacker cost disproportionately. The environment variable requirement ensures the cost factor can be increased when hardware advances make 12 insufficient, without a code deployment.

**Anti-Patterns:**
- `AP-S3.3a` — Hardcoding `bcrypt.hash(password, 10)` — cost factor in source code cannot be changed without a deployment; environment variable is mandatory.
- `AP-S3.3b` — Using SHA-256 or SHA-512 for password storage — cryptographic hash functions are not password hashing functions; they are designed to be fast, making them unsuitable for password storage.

**Cross-References:** `S3.28` (security baseline), `S3.32` (password strength)

---

### S3.4 — Rate Limiting — Three Protection Layers on All Auth Endpoints

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S3.4 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S2.49` (security middleware in backend) |
| **Enforced By** | Code Review · Security Audit |

**Standard:**
All authentication endpoints are protected by three rate-limiting layers operating simultaneously. Layer 1: 10 requests per IP per 15 minutes (Redis counter with TTL). Layer 2: 5 failed login attempts triggers a 15-minute account lock plus a security email to the verified address; during lock, even correct credentials return the identical error response. Layer 3: 1,000 authentication requests per minute globally. All three layers are active in production at all times.

**Rationale:**
Layer 1 blocks single-IP brute force. Layer 2 blocks distributed brute force targeting one account. Layer 3 prevents platform-wide credential stuffing attacks. The identical error response during account lock is critical — distinguishable errors enable account enumeration even when the account is locked.

**Anti-Patterns:**
- `AP-S3.4a` — Implementing only IP-based rate limiting and skipping account-level locking — distributed attacks from multiple IPs bypass IP-only rate limiting entirely.
- `AP-S3.4b` — Returning "Account locked" vs "Invalid credentials" as distinguishable responses — enables attackers to identify valid accounts without knowing the password.

**Cross-References:** `S2.49` (backend security middleware), `S3.28` (HTTPS enforcement), `S3.30` (password reset enumeration-proofing)

---

## Part 1 — NextAuth.js Strategy (`S3.5`–`S3.12`)

Standards S3.5–S3.12 apply exclusively to Next.js systems (Maphophe, SyncUp). Angular+FastAPI systems use Part 2. These standards govern every aspect of the NextAuth.js implementation — from session strategy to cookie configuration to OAuth handling.

---

### S3.5 — Database Sessions, Never JWT Sessions on Next.js

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S3.5 |
| **Priority**    | Critical |
| **Applies To**  | Next.js Only |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S3.2` (auth data in PostgreSQL), `S5.9` (Prisma as source of truth) |
| **Enforced By** | Code Review · NextAuth config audit |

**Standard:**
NextAuth.js is configured with `session: { strategy: "database" }` and the Prisma Adapter. JWT session strategy is forbidden on Next.js systems. Session rows in PostgreSQL are the authoritative session state — deleting a session row invalidates that session instantly across all devices.

**Rationale:**
JWT sessions cannot be revoked without a deny-list. Database sessions revoke instantly — a compromised session is terminated by deleting its row, not by waiting for a token to expire. Instant revocation is non-negotiable for systems where user accounts can have administrative or financial impact.

**Anti-Patterns:**
- `AP-S3.5a` — Configuring `session: { strategy: "jwt" }` in NextAuth because "it's stateless" — stateless sessions cannot be revoked; a stolen session persists until token expiry regardless of password changes or explicit logout.

**Cross-References:** `S3.2` (PostgreSQL for auth data), `S5.9` (Prisma schema ownership), `S3.35` (session invalidation on password change)

---

### S3.6 — HTTP-Only Session Cookies — Never localStorage or sessionStorage

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S3.6 |
| **Priority**    | Critical |
| **Applies To**  | Next.js Only |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S3.5` (database sessions) |
| **Enforced By** | Code Review · Browser DevTools audit |

**Standard:**
NextAuth.js session cookies are configured with `HttpOnly: true`, `Secure: true`, `SameSite: Lax`. Session tokens are never stored in localStorage or sessionStorage. XSS attacks cannot read HttpOnly cookies — this is the primary XSS defence for session security.

**Rationale:**
localStorage is accessible to any JavaScript running on the page. A single XSS vulnerability — including one in a third-party script — can steal a localStorage token and fully impersonate the user. HttpOnly cookies are not accessible to JavaScript regardless of the execution context.

**Anti-Patterns:**
- `AP-S3.6a` — Storing the NextAuth session token in localStorage for "easier client-side access" — this directly negates the XSS protection that HttpOnly cookies provide.

**Cross-References:** `S3.14` (Angular in-memory storage — same principle, different implementation), `CF-01` (Common Failure Register — localStorage token theft)

---

### S3.7 — Middleware-Based Route Protection — Session Verified on Every Request

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S3.7 |
| **Priority**    | Critical |
| **Applies To**  | Next.js Only |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S3.5` (database sessions), `S3.6` (HttpOnly cookies) |
| **Enforced By** | Code Review · Playwright auth tests |

**Standard:**
Next.js middleware (`middleware.ts`) verifies the session on every request to protected routes. API routes independently verify the session regardless of middleware. Protection exists at both the routing layer and the API layer — never relying on one layer alone.

**Rationale:**
Middleware-only protection means a direct API call without going through the Next.js router bypasses authentication entirely. Double-layer protection ensures that even if the middleware is misconfigured or bypassed, the API route rejects the unauthenticated request.

**Anti-Patterns:**
- `AP-S3.7a` — Protecting only the frontend route via middleware without verifying the session in the API route handler — API calls from external clients, Postman, or direct fetch calls bypass the middleware and reach the handler unauthenticated.

**Cross-References:** `S3.21` (RBAC — authorization after authentication), `S2.49` (backend security middleware)

---

### S3.8 — Session Callback — Safe Fields Only in Session Object

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S3.8 |
| **Priority**    | High |
| **Applies To**  | Next.js Only |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S3.5` (database sessions) |
| **Enforced By** | Code Review · Session shape audit |

**Standard:**
The NextAuth session callback exposes only these fields to the client: `id`, `email`, `name`, `role`, `image`. Fields that must never appear in the session object: `password_hash`, `reset_token`, `refresh_token`, `deleted_at`, `internal_notes`, and any two-factor secrets. The session object is client-accessible — it is treated as a public document.

**Rationale:**
Any field in the session object is accessible via `getSession()` on the client. Sensitive fields in the session object are directly exposed to the browser and any JavaScript running on the page.

**Anti-Patterns:**
- `AP-S3.8a` — Including `password_hash` or security tokens in the session callback because "it's convenient for server components" — session objects are client-readable and must only contain what is safe to expose publicly.

**Cross-References:** `S5.11` (no SELECT * — explicit field selection), `S2.51` (response data sanitisation)

---

### S3.9 — Session Lifetime — Environment-Configurable, Sliding Expiration

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S3.9 |
| **Priority**    | Standard |
| **Applies To**  | Next.js Only |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S3.5` (database sessions) |
| **Enforced By** | Code Review · Session config audit |

**Standard:**
Session lifetime is configured via the `SESSION_MAX_AGE_SECONDS` environment variable (default 30 days). Sliding expiration is active — sessions extend on active use. A daily cron job removes expired session rows from the database. Session lifetime is not hardcoded.

**Rationale:**
Hardcoded session lifetimes cannot be adjusted for security incidents or compliance requirements without a deployment. The environment variable enables instant reduction of session lifetime if a security event requires it.

**Anti-Patterns:**
- `AP-S3.9a` — Hardcoding `maxAge: 2592000` in the NextAuth config — session lifetime becomes a deployment-time constraint rather than an operational configuration.

**Cross-References:** `S3.35` (session invalidation on password change)

---

### S3.10 — OAuth Through NextAuth Exclusively — No Custom OAuth Flows

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S3.10 |
| **Priority**    | Critical |
| **Applies To**  | Next.js Only |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S3.1` (one strategy per system) |
| **Enforced By** | Code Review |

**Standard:**
All OAuth authentication (Google, GitHub, LinkedIn) on Next.js systems is handled exclusively through NextAuth.js providers. Custom OAuth flows — manual PKCE implementation, manual state validation, manual token exchange — are forbidden. NextAuth handles all OAuth security concerns correctly; custom implementations routinely miss security-critical details.

**Rationale:**
OAuth PKCE, state parameter validation, and token exchange have subtle security requirements. NextAuth has implemented these correctly and maintains them across provider API changes. Custom OAuth flows introduce implementation risk without any architectural benefit.

**Anti-Patterns:**
- `AP-S3.10a` — Building a custom Google OAuth flow outside of NextAuth because "it's more flexible" — custom OAuth implementations consistently miss state validation, creating CSRF vulnerabilities in the auth flow.

**Cross-References:** `S3.26` (OAuth provider configuration), `S3.27` (institutional email domain validation)

---

### S3.11 — CSRF Protection Never Disabled

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S3.11 |
| **Priority**    | Critical |
| **Applies To**  | Next.js Only |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S3.6` (SameSite cookies) |
| **Enforced By** | Code Review · Security audit |

**Standard:**
NextAuth's built-in CSRF protection is never disabled. The `csrf` option is never set to `false`. State parameters in OAuth flows are never skipped. SameSite cookie settings are never downgraded to `None` without explicit security justification documented in an ADR.

**Rationale:**
CSRF attacks trick authenticated browsers into making requests to the application. NextAuth's CSRF protection, combined with SameSite cookies, blocks this attack class entirely. Disabling either creates a CSRF vulnerability that can be exploited by any site that can predict or enumerate action URLs.

**Anti-Patterns:**
- `AP-S3.11a` — Setting `SameSite: None` without `Secure: true` and a documented reason — this disables the primary CSRF defence at the cookie level.

**Cross-References:** `S3.6` (HttpOnly and SameSite configuration)

---

### S3.12 — Email Verification — Configurable Mode, 24-Hour Token Expiry

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S3.12 |
| **Priority**    | High |
| **Applies To**  | Next.js Only |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S3.2` (verification tokens in PostgreSQL) |
| **Enforced By** | Code Review |

**Standard:**
Email verification operates in one of two modes determined by system context. Strict mode (no access until verified) for security-sensitive systems. Progressive mode (limited access, sensitive operations require verification) for community and creator systems. Verification tokens expire after 24 hours. Resend rate is limited to 3 per hour per user. Mode is configured via environment variable.

**Rationale:**
Strict and progressive modes serve different user experience contexts. Reserve Bank requires strict verification before any financial access. Maphophe and SyncUp can allow exploration before requiring verification for writes. The configuration prevents mode mismatches between environments.

**Anti-Patterns:**
- `AP-S3.12a` — Verification tokens with no expiry — an intercepted verification email sent weeks later can verify a compromised account.

**Cross-References:** `S3.2` (tokens in PostgreSQL), `S3.30` (password reset same principles)

---

## Part 2 — JWT Authentication Strategy (`S3.13`–`S3.20`)

Standards S3.13–S3.20 apply exclusively to Angular+FastAPI systems (FundsLink Academy, KSDRILL Reserve Bank). These standards govern the complete JWT lifecycle — issuance, storage, rotation, validation, and revocation.

---

### S3.13 — RS256-Signed JWT Issued by FastAPI

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S3.13 |
| **Priority**    | Critical |
| **Applies To**  | Angular Only |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S3.1` (one strategy per system), `S3.20` (secrets in Railway only) |
| **Enforced By** | Code Review · Security audit |

**Standard:**
FastAPI issues RS256-signed JWTs. Access tokens contain: `sub` (user ID), `role`, `email`, `jti` (unique token ID), `version`. Refresh tokens are 64-byte random values, SHA-256 hashed before storage in PostgreSQL, with the raw value transmitted once in an HttpOnly cookie. RS256 asymmetric signing means the private key signs (Railway Secrets only) and the public key verifies (safely distributable). HS256 is forbidden.

**Rationale:**
HS256 uses a single symmetric key for both signing and verification — any service that can verify a token can also forge one. RS256's asymmetric design means verification keys can be distributed to other services without granting them the ability to issue tokens. This is architecturally correct for a multi-service system.

**Anti-Patterns:**
- `AP-S3.13a` — Using HS256 because "it's simpler to configure" — the simplicity eliminates the core security benefit of asymmetric signing; a leaked verification key becomes an attack vector.
- `AP-S3.13b` — Storing sensitive data beyond the defined claims in the JWT payload — JWT payloads are base64-encoded, not encrypted; any field is readable by anyone with the token.

**Cross-References:** `S3.20` (Railway Secrets for keys), `S3.14` (split token storage), `S3.16` (refresh rotation)

---

### S3.14 — Split Token Storage — Refresh in Cookie, Access in Angular Memory

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S3.14 |
| **Priority**    | Critical |
| **Applies To**  | Angular Only |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S3.13` (JWT issuance), `S3.15` (HTTP interceptor) |
| **Enforced By** | Code Review · Browser DevTools audit |

**Standard:**
Refresh tokens are stored exclusively in HttpOnly, `SameSite=Strict` cookies scoped to `/api/v1/auth`. Access tokens are stored exclusively in Angular in-memory state — never in localStorage, never in sessionStorage, never in cookies. The access token is lost on tab close; the refresh token persists for 7 days. This split design limits XSS attack impact to the 15-minute access token window only.

**Rationale:**
localStorage access tokens are the most common Angular auth vulnerability. An XSS attack stealing an in-memory access token gains only 15 minutes of access with no refresh capability. An XSS attack stealing a localStorage token has indefinite access until manual revocation. The split storage model is the correct security position.

**Anti-Patterns:**
- `AP-S3.14a` — Storing the access token in localStorage for "persistence across page loads" — this is the CF-01 vulnerability; XSS attack steals the token with no time limit and no automatic revocation.
- `AP-S3.14b` — Storing the access token in an HttpOnly cookie — makes it inaccessible to the Angular interceptor for Bearer header attachment, breaking all authenticated API calls.

**Cross-References:** `S3.15` (interceptor reads from memory), `CF-01` (Common Failure Register — localStorage token), `C0 §7.3` (Auth Override Rule — this standard is immutable)

---

### S3.15 — HTTP Interceptor — Single Auth Handler with Refresh Deduplication

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S3.15 |
| **Priority**    | Critical |
| **Applies To**  | Angular Only |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S3.14` (access token in memory), `S3.16` (refresh rotation) |
| **Enforced By** | Code Review · Angular interceptor test (S7.12) |

**Standard:**
A single Angular HTTP interceptor handles all outbound API requests. It attaches the Bearer token from memory and the `X-Request-ID` header to every request. On receiving a 401 response, it triggers a silent token refresh with concurrent request deduplication — multiple simultaneous 401 responses trigger exactly one refresh request, then all waiting requests retry with the new token.

**Rationale:**
Without deduplication, three simultaneous API calls that all receive 401s trigger three parallel refresh requests. The second and third refresh requests present a token that was revoked by the first refresh — triggering replay detection and logging the user out. Deduplication is security-critical, not an optimisation.

**Anti-Patterns:**
- `AP-S3.15a` — Implementing refresh without deduplication — concurrent requests cause token revocation, replay detection, and unexpected logouts during normal dashboard operation.
- `AP-S3.15b` — Using multiple HTTP interceptors for auth — split handling creates race conditions between interceptors competing to refresh the same expired token.

**Cross-References:** `S3.16` (replay detection), `S4.68` (frontend interceptor implementation), `S7.12` (interceptor test requirements)

---

### S3.16 — Refresh Token Rotation with Replay Detection

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S3.16 |
| **Priority**    | Critical |
| **Applies To**  | Angular Only |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S3.13` (JWT issuance), `S3.15` (interceptor) |
| **Enforced By** | Code Review · Token rotation integration tests |

**Standard:**
Every token refresh issues a new access-refresh pair and revokes the old refresh token. Replay detection: if a revoked token is presented for refresh, all tokens for that user are immediately revoked, a Sentry alert is raised, a security email is sent, and all sessions are universally logged out. Token family chains (`replaced_by` field) enable forensic tracing of the compromise path.

**Rationale:**
Without replay detection, a stolen refresh token can be silently used in parallel with the legitimate user's token — the legitimate user keeps getting new tokens via rotation, and so does the attacker. Replay detection terminates both sessions on first detection, protecting the user at the cost of one legitimate logout.

**Anti-Patterns:**
- `AP-S3.16a` — Rotating tokens without replay detection — a stolen refresh token is undetectable; the attacker maintains indefinite access while the legitimate user continues using the app normally.

**Cross-References:** `S3.13` (RS256 JWT), `S3.15` (deduplication prerequisite), `S3.34` (security alerts)

---

### S3.17 — FastAPI Dependency Injection for JWT Validation

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S3.17 |
| **Priority**    | High |
| **Applies To**  | Angular Only |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S3.13` (RS256 JWT), `S3.21` (RBAC) |
| **Enforced By** | Code Review |

**Standard:**
JWT validation in FastAPI uses `Depends()` injection exclusively. `get_current_user` decodes RS256, verifies expiry, checks JTI against the Redis deny-list, queries the User record, and verifies the account is not soft-deleted. `require_role(Role)` wraps `get_current_user` and checks role or ADMIN override. Business logic functions never check roles or validate tokens directly — the dependency layer is the sole authorisation gate.

**Rationale:**
Role checks scattered through business logic are inconsistent by design — different endpoints implement the check differently, creating gaps. Centralised dependency injection ensures every protected endpoint uses identical validation logic with no possibility of omission.

**Anti-Patterns:**
- `AP-S3.17a` — Checking `if user.role == "ADMIN":` inside a service function rather than at the `Depends()` layer — role checks in business logic are duplicated inconsistently and routinely missed on new endpoints.

**Cross-References:** `S3.21` (RBAC), `S2.1` (service layer separation), `S2.52` (auth headers validation)

---

### S3.18 — Logout — Revoke, Deny-List, BroadcastChannel All Tabs

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S3.18 |
| **Priority**    | High |
| **Applies To**  | Angular Only |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S3.14` (split token storage), `S3.16` (token rotation) |
| **Enforced By** | Code Review · Logout integration tests |

**Standard:**
Logout follows this three-step sequence: (1) Revoke refresh token in PostgreSQL. (2) Add JTI to Redis deny-list with TTL equal to remaining access token lifetime. (3) Clear the HttpOnly cookie, clear Angular in-memory state, BroadcastChannel notifies all open tabs. If Redis is unavailable, the access token remains valid for up to 15 minutes — this is an accepted and documented risk.

**Rationale:**
Without BroadcastChannel, a user logged out in one tab continues authenticated in all other open tabs. Without JTI deny-listing, the access token continues to authenticate API calls for up to 15 minutes post-logout. The 15-minute Redis failure window is acceptable given the alternative (synchronous Redis dependency causing logout failures in production).

**Anti-Patterns:**
- `AP-S3.18a` — Only clearing Angular state without revoking the PostgreSQL refresh token — the HttpOnly cookie persists; a page reload re-authenticates using the still-valid refresh token.

**Cross-References:** `S3.14` (split storage), `S3.16` (refresh rotation), `S3.35` (password change invalidation)

---

### S3.19 — Angular Route Guards — UX Layer Only, Server Is Authoritative

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S3.19 |
| **Priority**    | Standard |
| **Applies To**  | Angular Only |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S3.17` (FastAPI Depends() is authoritative) |
| **Enforced By** | Code Review |

**Standard:**
Angular route guards redirect unauthenticated users to the login page for UX purposes. They are not the authorisation mechanism. The FastAPI `Depends()` layer is the sole authoritative authorisation gate. A user who bypasses an Angular route guard (via direct URL navigation, browser back button, or JavaScript manipulation) receives a 401 or 403 from the API — not unauthorised data.

**Rationale:**
Client-side route guards can always be bypassed by a determined attacker. Security that relies on client-side code is not security — it is UX. The server-side validation is what enforces the security boundary; the route guard enforces the user experience.

**Anti-Patterns:**
- `AP-S3.19a` — Treating Angular route guards as the security boundary and skipping `Depends()` validation on API endpoints — client-side guards are bypassed with one browser developer tools command.

**Cross-References:** `S3.17` (FastAPI Depends()), `S3.23` (authorisation at route entry not business logic)

---

### S3.20 — Secrets in Railway Secrets Exclusively — Never Committed to Version Control

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S3.20 |
| **Priority**    | Critical |
| **Applies To**  | Angular Only |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S2.55` (secrets management in backend) |
| **Enforced By** | CI secret scanning · Code Review |

**Standard:**
All Angular+FastAPI authentication secrets — RS256 private and public keys, bcrypt cost factor, JWT secret seeds — are stored exclusively in Railway Secrets. Never committed to version control. Development, staging, and production use separate key pairs. `.env.example` lists variable names with placeholder descriptions only — never values.

**Rationale:**
A committed secret is a compromised secret, regardless of how quickly it is removed. Git history retains committed secrets indefinitely. Key separation across environments prevents a staging key compromise from affecting production.

**Anti-Patterns:**
- `AP-S3.20a` — Committing a `.env` file containing actual secret values "for team convenience" — secrets in git history cannot be effectively removed; the repository must be treated as permanently compromised.

**Cross-References:** `S2.55` (secrets management), `S8.39` (environment variable governance), `CF-04` (secrets committed pattern)

---

## Part 3 — Role-Based Access Control (`S3.21`–`S3.25`)

Role-based access control applies across both stacks. The mechanism differs (NextAuth session roles vs FastAPI `Depends()` roles) but the governance — how roles are defined, assigned, verified, and audited — is identical.

---

### S3.21 — Roles as Database Enums — Never String Literals in Code

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S3.21 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S5.9` (Prisma schema as source of truth) |
| **Enforced By** | ESLint · Code Review |

**Standard:**
Roles are defined as PostgreSQL enum types in the Prisma schema. System-specific roles: `USER`, `ADMIN` (both stacks); `CREATOR` (SyncUp); `STUDENT`, `FUNDER` (FundsLink); `ACCOUNT_HOLDER` (Reserve Bank); `WARD_ADMIN` (Maphophe). Role assignment is ADMIN-only, audit-logged. New accounts default to the minimum role via database default. Role strings are never hardcoded — always referenced via the generated Prisma enum.

**Rationale:**
Hardcoded role strings (`"admin"`, `"ADMIN"`, `"Admin"`) create case-sensitivity bugs and make refactoring impossible without grepping for every string occurrence. Enum types catch invalid role values at the TypeScript/Python type level before they reach the database.

**Anti-Patterns:**
- `AP-S3.21a` — Comparing `user.role === "admin"` in application code — case mismatch, typo, or string constant change causes silent authorisation failures.
- `AP-S3.21b` — Adding a new system-specific role without adding it to the Prisma enum first — application code references a role that doesn't exist at the database level.

**Cross-References:** `S5.9` (Prisma schema), `S5.10` (required fields), `S3.25` (role change audit trail)

---

### S3.22 — Ownership Verification on Every User-Owned Resource

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S3.22 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S3.21` (RBAC), `S3.17` (FastAPI auth) or `S3.7` (NextAuth) |
| **Enforced By** | Code Review · Integration tests |

**Standard:**
Every operation on a user-owned resource follows this pattern: Authenticate → Authorise (role check) → Verify Ownership (confirm the authenticated user owns the resource being accessed) → Process. Role-based access alone is insufficient — two users with identical roles must not be able to access each other's data.

**Rationale:**
RBAC governs what roles can do. Ownership verification governs who can do it to which resource. A system with RBAC but without ownership verification allows any `STUDENT` to view any other `STUDENT`'s application data — a data breach within the authenticated user population.

**Anti-Patterns:**
- `AP-S3.22a` — Checking role but not ownership: `if user.role == STUDENT: return application` without verifying `application.student_id == user.id` — every student can access every other student's application.

**Cross-References:** `S3.21` (role definitions), `S2.1` (service layer owns this verification)

---

### S3.23 — Authorisation at Route Entry — Not Inside Business Logic

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S3.23 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S3.21` (RBAC), `S3.17` (FastAPI Depends()) or `S3.7` (Next.js middleware) |
| **Enforced By** | Code Review |

**Standard:**
Authorisation (role and permission checks) occurs at the entry point of each route — in `Depends()` for FastAPI, in API route handlers before service layer calls for Next.js. Business logic functions never perform role checks. Service layer functions assume the caller has already been authorised.

**Rationale:**
Role checks inside business logic are duplicated across every function that calls that logic. When authorisation requirements change, every duplication point requires update. Centralised entry-point authorisation means one change governs all paths.

**Anti-Patterns:**
- `AP-S3.23a` — Role checks inside service layer functions — identical logic duplicated across multiple callers; one missed duplication creates an authorisation gap.

**Cross-References:** `S3.17` (FastAPI Depends()), `S3.7` (Next.js middleware), `S2.1` (service layer boundary)

---

### S3.24 — Least Privilege Default — Minimum Role on Account Creation

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S3.24 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S3.21` (roles as enums with database default) |
| **Enforced By** | Code Review · Registration integration tests |

**Standard:**
New accounts default to the minimum role for their system (`USER` or the system-specific equivalent) via the Prisma schema `@default()`. Admin role assignment requires explicit ADMIN action and is audit-logged. No endpoint, registration flow, or OAuth callback assigns elevated roles automatically.

**Rationale:**
A bug in registration logic that accidentally assigns ADMIN roles to new users is a catastrophic security event. Database-level default assignments mean even buggy code that omits role assignment produces the minimum-privilege account.

**Anti-Patterns:**
- `AP-S3.24a` — Setting role in registration business logic rather than relying on database default — a code change that removes the role assignment silently creates accounts without a role, causing runtime errors.

**Cross-References:** `S3.21` (role enums), `S3.25` (audit trail for role changes)

---

### S3.25 — Role Change Audit Trail — Immutable History

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S3.25 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S3.33` (universal auth event logging) |
| **Enforced By** | Code Review · Audit log integration tests |

**Standard:**
Every role change is logged to the `AuditLog` table: target user, old role, new role, acting admin user ID, IP address, timestamp, and reason. Audit entries are never updated or deleted. The complete role history for any user is always queryable. Role changes without a logged reason string are rejected at the service layer.

**Rationale:**
Role escalation is one of the most common insider threat vectors. An immutable audit trail makes every role change attributable and reversible. "Who had ADMIN access and when?" is a question that must always be answerable.

**Anti-Patterns:**
- `AP-S3.25a` — Updating role without creating an AuditLog entry — role escalation becomes undetectable and non-attributable; any security review of "how did this user get ADMIN?" cannot be answered.

**Cross-References:** `S3.33` (universal auth logging), `S5.10` (Prisma required fields include immutable timestamps)

---

## Part 4 — OAuth & External Identity Providers (`S3.26`–`S3.27`)

OAuth integration adds external identity verification on top of the base authentication strategy. Provider configuration is system-specific and database-driven — adding or removing providers is an operational change, not a development task.

---

### S3.26 — OAuth Provider Configuration — Database-Backed, Per System

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S3.26 |
| **Priority**    | Standard |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S3.10` (NextAuth for Next.js OAuth), `S5.4` (SystemConfig in PostgreSQL) |
| **Enforced By** | Code Review |

**Standard:**
Supported OAuth providers per system: Maphophe (Google), SyncUp (Google, GitHub), FundsLink (Google, LinkedIn), Reserve Bank (credential-only, no OAuth). Provider configuration is stored in the `SystemConfig` PostgreSQL table — adding or removing a provider is a database change, not a code deployment. Each system's enabled providers are documented in its system context file.

**Rationale:**
Hardcoded provider lists require a deployment to add or remove a provider. Database-driven configuration enables responding to a provider security incident (e.g., removing a compromised provider) without a deployment.

**Anti-Patterns:**
- `AP-S3.26a` — Hardcoding provider lists in the NextAuth config rather than reading from `SystemConfig` — disabling a compromised OAuth provider requires a code change and deployment rather than a database update.

**Cross-References:** `S3.10` (NextAuth OAuth), `S5.4` (SystemConfig table)

---

### S3.27 — Institutional Email Domain Validation on OAuth

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S3.27 |
| **Priority**    | Standard |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S3.26` (OAuth provider config), `S5.4` (SystemConfig) |
| **Enforced By** | Code Review · Registration integration tests |

**Standard:**
Systems requiring institutional email restriction (FundsLink: SA university and TVET domains) check the OAuth account's email domain against an allowlist stored in `SystemConfig`. Non-matching email domains receive a clear error message with guidance. Allowlist is managed via database — no deployment required to add or remove domains.

**Rationale:**
FundsLink's funding eligibility is tied to institutional enrolment. A non-student OAuth login bypassing the domain check would corrupt the eligibility model. Database-driven allowlists enable responding to new institutions without deployment.

**Anti-Patterns:**
- `AP-S3.27a` — Hardcoding the domain allowlist in application code — adding a new institution requires a deployment; removing a compromised institution requires a deployment.

**Cross-References:** `S3.26` (provider configuration), `S5.4` (SystemConfig table)

---

## Part 5 — Security Baseline (`S3.28`–`S3.32`)

Security baseline standards apply to all authentication endpoints across both stacks. These are the minimum security requirements — not the aspirational targets.

---

### S3.28 — HTTPS Only in Production — HSTS Enforced

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S3.28 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | — |
| **Enforced By** | Vercel/Railway platform enforcement · Security audit |

**Standard:**
All authentication traffic in production uses HTTPS exclusively. HSTS (`Strict-Transport-Security: max-age=31536000; includeSubDomains`) is set on all responses. Vercel and Railway enforce HTTPS by default — this is never disabled. HTTP redirects to HTTPS and never serves auth content on HTTP.

**Rationale:**
Authentication credentials, session tokens, and JWT refresh tokens transmitted over HTTP are visible to any network observer on the same network. HSTS prevents downgrade attacks where an attacker forces HTTP after the first HTTPS visit.

**Anti-Patterns:**
- `AP-S3.28a` — Disabling HTTPS enforcement in "staging-like" environments accessed over the internet — credentials transmitted in staging are often real developer credentials; HTTP exposure is equally dangerous.

**Cross-References:** `S8.1` (Vercel deployment), `S8.2` (Railway deployment)

---

### S3.29 — CORS Locked to Known Origins — No Wildcard in Production

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S3.29 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S2.49` (security middleware) |
| **Enforced By** | Code Review · Security audit |

**Standard:**
CORS is configured with an explicit origin allowlist per environment — never `*` in production or staging. Preflight requests from origins not on the allowlist receive 403. The allowlist is configured via environment variable, not hardcoded. Each environment (development, staging, production) has its own CORS origin list.

**Rationale:**
Wildcard CORS allows any website to make authenticated cross-origin requests using the victim's session credentials. With SameSite cookies and a strict CORS origin list, cross-site request attacks are blocked at the network boundary.

**Anti-Patterns:**
- `AP-S3.29a` — Setting `allow_origins=["*"]` in FastAPI CORS middleware or `Access-Control-Allow-Origin: *` in Next.js headers — any website can make authenticated requests on behalf of logged-in users.

**Cross-References:** `S2.49` (security middleware), `CF-08` (Angular direct API call — same CORS violation)

---

### S3.30 — Password Reset — Time-Limited, Single-Use, Enumeration-Proof

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S3.30 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S3.2` (reset tokens in PostgreSQL), `S3.35` (session invalidation on password change) |
| **Enforced By** | Code Review · Security audit |

**Standard:**
Password reset tokens are 32-byte cryptographically random values, SHA-256 hashed before storage in PostgreSQL. Token lifetime is 1 hour. Tokens are single-use — consumed on successful reset. The reset response is always identical: "If an account exists with that email, a reset link has been sent." Post-reset: all sessions and refresh tokens for that user are immediately revoked.

**Rationale:**
Distinguishable responses between "email exists" and "email not found" enable account enumeration — an attacker can identify all registered emails by checking the reset endpoint. The identical response prevents this.

**Anti-Patterns:**
- `AP-S3.30a` — Returning "No account found with that email" as a distinct response — enables enumeration of all registered email addresses via the unauthenticated reset endpoint.
- `AP-S3.30b` — Storing reset tokens in plaintext in the database — a database read compromise exposes reset tokens that can be used to take over accounts.

**Cross-References:** `S3.35` (session invalidation), `S3.2` (tokens in PostgreSQL), `S3.3` (SHA-256 hashing of tokens)

---

### S3.31 — Security Headers on All Responses

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S3.31 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S2.49` (security middleware) |
| **Enforced By** | Security header scanner · CI |

**Standard:**
All responses include the following security headers: `Content-Security-Policy` (restricts script sources), `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy` (disables unnecessary browser APIs). Headers are configured at the platform level (Next.js `next.config.js` headers, FastAPI middleware) — never on individual routes.

**Rationale:**
Security headers are the browser-level defence layer against XSS, clickjacking, and MIME-sniffing attacks. Missing headers are frequently exploited in combination with other vulnerabilities. Platform-level configuration ensures no route is accidentally unprotected.

**Anti-Patterns:**
- `AP-S3.31a` — Adding security headers to individual route handlers instead of platform-level middleware — any route added after the fact lacks headers unless the developer explicitly remembers to add them.

**Cross-References:** `S2.49` (backend security middleware), `S2.50` (FastAPI security config)

---

### S3.32 — Password Strength Validation and Breach Detection

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S3.32 |
| **Priority**    | Standard |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S3.3` (bcrypt hashing) |
| **Enforced By** | Code Review · Registration integration tests |

**Standard:**
Password validation enforces: minimum 8 characters, at least one uppercase letter, one digit, one special character. Passwords are checked against a common passwords list. Breach detection via the HIBP API uses k-anonymity (the first 5 characters of the SHA-1 hash only — the full hash is never sent). Client-side validation provides UX feedback. Server-side validation is authoritative.

**Rationale:**
Common password lists prevent the most frequently compromised passwords. HIBP k-anonymity breach detection rejects passwords known to be compromised in data breaches without exposing the full password hash to the external service.

**Anti-Patterns:**
- `AP-S3.32a` — Relying on client-side password validation only — client-side validation is bypassed with developer tools; any POST directly to the API endpoint bypasses it entirely.

**Cross-References:** `S3.3` (bcrypt), `S3.30` (password reset)

---

## Part 6 — Audit Logging & Governance (`S3.33`–`S3.36`)

Authentication events are security events. The audit log is the system's memory for every security-relevant action — it is append-only, immutable, and never subject to deletion.

---

### S3.33 — Universal Auth Event Logging — Every Event, Every System

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S3.33 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S5.9` (AuditLog table in PostgreSQL), `S2.56` (structured logging) |
| **Enforced By** | Code Review · Auth integration tests |

**Standard:**
Every authentication event on every system is logged to the `AuditLog` PostgreSQL table: login success, login failure (with reason in JSONB metadata), logout, token refresh, token theft detection, password change, password reset (request and completion), email verification, role change, account lock, account unlock, registration, OAuth link, OAuth rejection. The `AuditLog` table has no `deleted_at` column — it is immutable by design. Audit entries are never updated or deleted.

**Rationale:**
Audit logs are the forensic record of authentication events. An incomplete log means a security incident cannot be reconstructed. "How many OAuth vs credential logins this month?" and "What was this user's authentication path before the account was compromised?" must always be answerable.

**Anti-Patterns:**
- `AP-S3.33a` — Logging only failed login attempts while omitting successful logins — a credential stuffing attack that succeeds on the first attempt leaves no audit record of the compromise.
- `AP-S3.33b` — Storing audit logs in a table with a `deleted_at` column — audit entries that can be soft-deleted provide no forensic guarantee.

**Cross-References:** `S5.9` (Prisma schema — AuditLog model), `S2.56` (structured logging), `S3.25` (role change audit)

---

### S3.34 — Security Alerts on Threat Indicators

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S3.34 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S3.33` (audit logging), `S8.11` (Sentry alert configuration) |
| **Enforced By** | Code Review · Alert integration tests |

**Standard:**
Automated alerts are sent immediately on: token replay detection (possible token theft), 5+ consecutive failed login attempts from one IP, account lock triggered, OAuth account linked to a new provider unexpectedly, and admin role assignment. Alerts are sent via Sentry and email to the system owner. Alert delivery is tested monthly.

**Rationale:**
Security events that are logged but not alerted on are invisible until a human audits the log. The alert-on-detection model reduces the response window from "next audit review" to "minutes after detection."

**Anti-Patterns:**
- `AP-S3.34a` — Logging token theft events without triggering an alert — the detection exists in the log but the response only happens when someone reads the log, which may be days or weeks later.

**Cross-References:** `S3.16` (replay detection triggers alert), `S8.11` (Sentry configuration), `IR9` (Sentry alert thresholds)

---

### S3.35 — Session Invalidation on Password Change — All Devices

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S3.35 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S3.5` (database sessions — Next.js) or `S3.16` (refresh rotation — Angular) |
| **Enforced By** | Code Review · Password change integration tests |

**Standard:**
Password change immediately invalidates all existing sessions and tokens across all devices. Next.js: `DELETE FROM Session WHERE userId = ?`. Angular+FastAPI: revoke all refresh tokens for the user, add all active JTIs to the Redis deny-list. The user is forced to re-authenticate on all devices after a password change.

**Rationale:**
A compromised session that was established before a password change should not survive the password change. The password change is the primary recovery action for a compromised account — if sessions survive the change, the attacker retains access despite the recovery action.

**Anti-Patterns:**
- `AP-S3.35a` — Only hashing the new password without invalidating existing sessions — an attacker with a stolen session token continues to have access even after the victim changes their password.

**Cross-References:** `S3.5` (database sessions), `S3.18` (logout flow), `S3.30` (password reset — same invalidation on completion)

---

### S3.36 — Cross-Constitution Security Review — Auth Changes Require Multi-Layer Review

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S3.36 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `C0 §8` (amendment protocol) |
| **Enforced By** | GitHub PR labels · CI gate |

**Standard:**
Any PR that changes authentication logic requires two GitHub PR labels: `backend-review-required` and `frontend-review-required`. CI fails without both labels. Authentication strategy-level changes require a documented security review recorded in the PR description. Auth touches every system layer — no single review perspective can assess full impact.

**Rationale:**
Auth changes have frontend implications (route guards, interceptors, session callbacks), backend implications (middleware, validation logic), and database implications (schema, token storage). A review scoped to one layer misses cross-layer impact. Mandatory multi-layer review is the structural defence against incomplete auth change assessment.

**Anti-Patterns:**
- `AP-S3.36a` — Merging auth changes with only a backend review — frontend session handling and Angular interceptor logic that depends on the backend change is reviewed after the change is already in production.

**Cross-References:** `C0 §7.3` (Auth Override Rule), `C0 §8` (amendment protocol), `S1.77` (PR review standards)

---

## Anti-Patterns Index

All anti-patterns from this constitution in one scannable table.

| ID | Description | Violated Standard | Severity |
|----|-------------|-------------------|----------|
| `AP-S3.1a` | Implementing NextAuth.js in an Angular+FastAPI system | S3.1 | Critical |
| `AP-S3.1b` | Running dual auth strategies during migration | S3.1 | Critical |
| `AP-S3.2a` | Storing session data in MongoDB | S3.2 | Critical |
| `AP-S3.2b` | Redis as primary session store without PostgreSQL backing | S3.2 | Critical |
| `AP-S3.3a` | Hardcoding bcrypt cost factor in source code | S3.3 | High |
| `AP-S3.3b` | Using SHA-256 for password storage | S3.3 | Critical |
| `AP-S3.4a` | IP-only rate limiting without account-level locking | S3.4 | High |
| `AP-S3.4b` | Distinguishable responses during account lock | S3.4 | High |
| `AP-S3.5a` | NextAuth JWT session strategy (`strategy: "jwt"`) | S3.5 | Critical |
| `AP-S3.6a` | Session token in localStorage | S3.6 | Critical |
| `AP-S3.7a` | Middleware-only protection without API route verification | S3.7 | Critical |
| `AP-S3.8a` | Sensitive fields in session callback object | S3.8 | High |
| `AP-S3.9a` | Hardcoded session maxAge | S3.9 | Standard |
| `AP-S3.10a` | Custom Google OAuth flow outside NextAuth | S3.10 | Critical |
| `AP-S3.11a` | SameSite: None without Secure and documented reason | S3.11 | High |
| `AP-S3.12a` | Verification tokens with no expiry | S3.12 | High |
| `AP-S3.13a` | Using HS256 instead of RS256 | S3.13 | Critical |
| `AP-S3.13b` | Sensitive data beyond defined claims in JWT payload | S3.13 | High |
| `AP-S3.14a` | Access token in localStorage (CF-01) | S3.14 | Critical |
| `AP-S3.14b` | Access token in HttpOnly cookie on Angular | S3.14 | High |
| `AP-S3.15a` | Refresh without concurrent request deduplication | S3.15 | Critical |
| `AP-S3.15b` | Multiple HTTP interceptors for auth | S3.15 | High |
| `AP-S3.16a` | Refresh rotation without replay detection | S3.16 | Critical |
| `AP-S3.17a` | Role checks inside service/business logic functions | S3.17 | High |
| `AP-S3.18a` | Logout clears Angular state only without PostgreSQL revocation | S3.18 | High |
| `AP-S3.19a` | Angular route guard treated as the security boundary | S3.19 | Critical |
| `AP-S3.20a` | Committing `.env` with actual secret values | S3.20 | Critical |
| `AP-S3.21a` | Hardcoded role string comparisons (`=== "admin"`) | S3.21 | High |
| `AP-S3.21b` | New role added to code before Prisma enum | S3.21 | High |
| `AP-S3.22a` | Role check without ownership verification | S3.22 | Critical |
| `AP-S3.23a` | Role checks inside service layer functions | S3.23 | High |
| `AP-S3.24a` | Role set in registration logic rather than database default | S3.24 | High |
| `AP-S3.25a` | Role change without AuditLog entry | S3.25 | High |
| `AP-S3.26a` | Hardcoded OAuth provider list in NextAuth config | S3.26 | Standard |
| `AP-S3.27a` | Hardcoded domain allowlist in application code | S3.27 | Standard |
| `AP-S3.28a` | HTTPS enforcement disabled in non-local environments | S3.28 | Critical |
| `AP-S3.29a` | CORS wildcard `*` in production or staging | S3.29 | Critical |
| `AP-S3.30a` | Distinguishable "email not found" response on password reset | S3.30 | High |
| `AP-S3.30b` | Reset tokens stored in plaintext | S3.30 | Critical |
| `AP-S3.31a` | Security headers on individual routes instead of platform middleware | S3.31 | Standard |
| `AP-S3.32a` | Client-side-only password validation | S3.32 | High |
| `AP-S3.33a` | Logging only failed logins, omitting successes | S3.33 | High |
| `AP-S3.33b` | AuditLog table with a `deleted_at` column | S3.33 | Critical |
| `AP-S3.34a` | Token theft logged but no alert triggered | S3.34 | High |
| `AP-S3.35a` | Existing sessions survive password change | S3.35 | Critical |
| `AP-S3.36a` | Auth PR merged with single-layer review only | S3.36 | High |

---

## Cross-Constitution Dependency Map

**This constitution depends on:**
| Dependency | Reason |
|------------|--------|
| `C0 — Constitutional Order` | Amendment protocol, Auth Override Rule (§7.3), conflict resolution hierarchy |
| `C2 — Backend Constitution` | Service layer hosts auth middleware; API security standards (S2.49–S2.55) |
| `C5 — Database Constitution` | PostgreSQL assignment for all auth data (S5.4); Prisma schema owns auth models (S5.9) |

**The following constitutions depend on this one:**
| Dependent | Reason |
|-----------|--------|
| `C2 — Backend Constitution` | Backend auth middleware implements this constitution's token validation standards |
| `C4 — Frontend Constitution` | Route guards, HTTP interceptors, and auth state management derive from S3.5–S3.19 |
| `C6 — Full-Stack Architecture` | Integration request flows include auth flows defined here |
| `C7 — Testing Constitution` | Auth test requirements (S7.11, S7.12) derive from this constitution's standards |
| `C8 — Platform Reliability` | Security alerts and auth incident response reference this constitution's threat model |

---

## Amendment Log

| Version | Date | Change | Reason |
|---------|------|--------|--------|
| v1.0 | 2026-05-08 | Initial lock — rebuilt from Auth Domain Specification v4.0. localStorage regression (CF-01) fixed in S3.14 with explicit anti-pattern `AP-S3.14a`. Terminology updated to Standards/Anti-Patterns format. Standard IDs introduced (`S3.N`). Cross-constitution dependency map added. Auth Override Rule reference added. | Full system rebuild — HTML to Markdown, version reset. |

---

> **LOCKED — v1.0 — 2026-05-08**
>
> This document is locked. No standard may be added, removed, or modified
> without following the Amendment Protocol defined in C0 §8.
> Amendments take effect only after commit to `system-design-template`
> with a version bump and amendment log entry.
>
> C3 Auth Constitution holds supreme authority over all security-touching decisions
> per C0 §7.3 (Auth Override Rule). No other document overrides a standard here.
