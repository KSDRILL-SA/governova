# Spring Boot Implementation Binding — C2 Backend

| Attribute | Value |
|-----------|-------|
| **Document** | C2 Backend Constitution — Spring Boot Implementation Bindings |
| **Layer** | 3 — Implementation |
| **Binds** | `constitution/core/phase-1-core-architecture/C02-backend-constitution.md` |
| **Stack** | Spring Boot 3.x · Java 21 / Kotlin · Spring Web · Spring Data JPA · Bean Validation · Resilience4j · springdoc-openapi |
| **Version** | v1.0 |
| **Status** | Active |

---

> *"A standard tells you what must be true. This binding shows exactly how to make it true in Spring Boot."*

This is the first non-reference binding — proof that Governova's universal core (written against a FastAPI reference) governs a maximally different stack (JVM, Spring) without changing a single core standard. Each `### S2.N/spring-boot` below binds one universal C2 standard to a concrete Spring Boot pattern, with the failure mode that violates it. Read C2 first; use this when building on Spring Boot.

---

## Architecture

### S2.1/spring-boot — Business Logic Lives Exclusively in the Service Layer

**Universal rule (from C2):**
> Business logic lives exclusively in the service layer; controllers orchestrate, they do not decide.

**Spring Boot binding:**
Business logic lives in `@Service` beans. `@RestController` methods only bind/validate the request, call a service method, and map the result to a response — no branching business rules, no repository calls, no calculations in the controller. Controllers depend on services via constructor injection; services depend on repositories.

```java
@RestController
@RequestMapping("/api/v1/accounts")
class AccountController {
    private final AccountService accounts; // constructor-injected
    @PostMapping
    ResponseEntity<ApiResponse<AccountDto>> open(@Valid @RequestBody OpenAccountRequest req) {
        return ResponseEntity.status(CREATED).body(ApiResponse.of(accounts.open(req)));
    }
}
```

**Spring Boot anti-pattern:**
`AP-S2.1a/spring-boot` — A `@RestController` method that queries a `Repository` directly or contains business branching/calculations — logic leaks out of the service layer and cannot be reused or tested in isolation.

---

### S2.3/spring-boot — Services Are Stateless

**Universal rule (from C2):**
> Services are stateless; no request state is held on the service between calls.

**Spring Boot binding:**
`@Service` beans are singletons by default — keep them stateless. No mutable instance fields holding per-request data; pass all request state as method parameters. Per-request scoped state, if ever needed, uses `@RequestScope`, never a mutable field on a singleton.

**Spring Boot anti-pattern:**
`AP-S2.3a/spring-boot` — A mutable instance field on a singleton `@Service` that holds per-request data — concurrent requests corrupt each other's state.

---

### S2.5/spring-boot — Service Functions Have Explicit Return Types

**Universal rule (from C2):**
> Every service function declares an explicit return type — never an untyped map or generic object.

**Spring Boot binding:**
Service methods return typed DTOs or domain records (`record AccountDto(...)`), never `Map<String,Object>`, `Object`, or a raw entity. Entities never cross the controller boundary — map to a DTO inside the service.

**Spring Boot anti-pattern:**
`AP-S2.5a/spring-boot` — A service returning `Map<String,Object>` or a JPA entity directly — the contract is untyped and leaks persistence structure to the API.

---

## API Contract

### S2.11/spring-boot — OpenAPI Contract Written Before Any Endpoint Is Implemented

**Universal rule (from C2):**
> The OpenAPI contract is written before any endpoint is implemented.

**Spring Boot binding:**
Contract-first: author `openapi.yaml`, generate DTOs and API interfaces with `openapi-generator` (`org.openapitools:openapi-generator-maven-plugin`), and implement the generated interfaces. `springdoc-openapi` is used only to verify the served spec matches the committed contract — not to derive it after the fact.

**Spring Boot anti-pattern:**
`AP-S2.11a/spring-boot` — Implementing controllers first and letting springdoc generate the spec afterward — the contract follows the code instead of governing it.

---

### S2.13/spring-boot — Protected Endpoints Declare Auth Requirements Explicitly

**Universal rule (from C2):**
> Every protected endpoint declares its auth requirement explicitly (governed by C3).

**Spring Boot binding:**
Protected endpoints declare authorization with `@PreAuthorize("hasRole('...')")` (method security enabled via `@EnableMethodSecurity`) and the route is matched in the `SecurityFilterChain`. There is no "secure by accident" — every endpoint is either explicitly permitted (`permitAll`) or explicitly authorized. C3 (Auth Override) governs the strategy.

**Spring Boot anti-pattern:**
`AP-S2.13a/spring-boot` — An endpoint with no `@PreAuthorize` and no explicit `SecurityFilterChain` rule, relying on a default — its protection is implicit and unauditable.

---

### S2.14/spring-boot — List Endpoints Support Pagination

**Universal rule (from C2):**
> List endpoints support pagination; they never return an unbounded collection.

**Spring Boot binding:**
List endpoints accept `Pageable` and return `Page<T>` (Spring Data), mapped to the standard list response shape (S2.20). A default and maximum page size are enforced via `@PageableDefault(size = 20)`; the maximum is capped so a client cannot request an unbounded page.

**Spring Boot anti-pattern:**
`AP-S2.14a/spring-boot` — `repository.findAll()` returned directly from a list endpoint — an unbounded result set that degrades and leaks at scale.

---

### S2.16/spring-boot — Sensitive Data Is Never Returned in API Responses

**Universal rule (from C2):**
> Sensitive fields are never serialised into an API response.

**Spring Boot binding:**
Responses are explicit DTOs that simply do not contain sensitive fields (password hashes, tokens, internal flags). Never serialise entities; if an entity is ever exposed, sensitive fields carry `@JsonIgnore`. DTO projection at the service boundary is the rule.

**Spring Boot anti-pattern:**
`AP-S2.16a/spring-boot` — Returning a JPA entity that contains a `passwordHash`/`secret` field — sensitive data leaks through default serialisation.

---

## Response & Error Shape

### S2.19/spring-boot — Single Object Response Shape Is Mandatory

**Universal rule (from C2):**
> Every single-object response uses the one mandated envelope shape.

**Spring Boot binding:**
All responses use a shared generic envelope `ApiResponse<T>` (`record ApiResponse<T>(boolean success, T data, Object error)`), produced by a small factory (`ApiResponse.of(data)`). Controllers never hand-roll an ad-hoc JSON map.

**Spring Boot anti-pattern:**
`AP-S2.19a/spring-boot` — Returning a bare DTO or a hand-built `Map` from one endpoint and the envelope from another — inconsistent shapes break clients.

---

### S2.22/spring-boot — Error Response Shape Is Mandatory and Uniform

**Universal rule (from C2):**
> Every error response uses the one mandated, uniform error shape.

**Spring Boot binding:**
A single `@RestControllerAdvice` (`GlobalExceptionHandler`) maps every exception to the uniform error envelope. `MethodArgumentNotValidException` → 422 with field-level detail (S2.26); domain exceptions → their mapped status; everything else → 500 with a generic message (S2.18 — no internals leaked). Status and shape are produced in exactly one place.

```java
@RestControllerAdvice
class GlobalExceptionHandler {
    @ExceptionHandler(MethodArgumentNotValidException.class)
    ResponseEntity<ApiResponse<Void>> onValidation(MethodArgumentNotValidException e) {
        return ResponseEntity.unprocessableEntity().body(ApiResponse.error(fieldErrors(e)));
    }
}
```

**Spring Boot anti-pattern:**
`AP-S2.22a/spring-boot` — Per-controller `try/catch` blocks returning differently-shaped error bodies — error structure becomes non-uniform and unpredictable.

---

## Validation

### S2.23/spring-boot — The Validation Layer Is an Architectural Boundary

**Universal rule (from C2):**
> Validation is an architectural boundary; invalid input never reaches the service layer.

**Spring Boot binding:**
Request DTOs carry Bean Validation constraints (`@NotNull`, `@Size`, `@Email`, `@Positive`, custom validators); controllers bind them with `@Valid`. Invalid input is rejected at the controller boundary before any service method runs. The service layer may assume its inputs are already valid.

**Spring Boot anti-pattern:**
`AP-S2.23a/spring-boot` — A `@RequestBody` without `@Valid`, or manual `if (req.x == null)` checks inside the service — validation leaks past the boundary and is duplicated.

---

### S2.26/spring-boot — Validation Errors Return 400/422 With Field-Level Detail

**Universal rule (from C2):**
> Validation failures return 400/422 with per-field error detail.

**Spring Boot binding:**
The `MethodArgumentNotValidException` handler (S2.22) builds a field→message map from `BindingResult.getFieldErrors()` and returns 422 in the uniform error envelope. The client receives exactly which fields failed and why.

**Spring Boot anti-pattern:**
`AP-S2.26a/spring-boot` — Returning a 500 or a single opaque "invalid request" string on validation failure — the client cannot tell which field is wrong.

---

## Data Access

### S2.30/spring-boot — Multi-Step Database Writes Are Wrapped in Transactions

**Universal rule (from C2):**
> Any operation that performs multiple dependent writes runs inside a transaction.

**Spring Boot binding:**
Multi-step writes run in a `@Transactional` service method (Spring's declarative transactions). The annotation is on the service method, not the repository, so the whole unit of work commits or rolls back atomically. Checked-exception rollback is configured explicitly where needed (`@Transactional(rollbackFor = ...)`).

**Spring Boot anti-pattern:**
`AP-S2.30a/spring-boot` — Two `repository.save(...)` calls in sequence with no `@Transactional` — a failure between them leaves the database in a half-written, inconsistent state.

---

### S2.34/spring-boot — All Financial Data Writes Are Idempotent

**Universal rule (from C2):**
> Every financial write is idempotent; a retried request never double-applies.

**Spring Boot binding:**
Financial writes carry a client-supplied idempotency key persisted with a unique constraint; a replay hits the constraint and returns the original result instead of re-applying. Monetary amounts use `BigDecimal` (never `double`/`float`), mirroring the Decimal mandate (C6 §financial-precision).

**Spring Boot anti-pattern:**
`AP-S2.34a/spring-boot` — A transfer endpoint with no idempotency key, or monetary fields typed as `double` — a retry double-applies, and float arithmetic corrupts balances.

---

### S2.35/spring-boot — Soft Delete Is Mandatory for All Auditable Entities

**Universal rule (from C2):**
> Auditable entities are soft-deleted, never physically removed.

**Spring Boot binding:**
Auditable entities use Hibernate `@SQLDelete(sql = "UPDATE ... SET deleted_at = now() WHERE id = ?")` and `@SQLRestriction("deleted_at is null")` (Hibernate 6) so deletes set a timestamp and default queries exclude soft-deleted rows. A physical delete requires an explicit, audited admin path.

**Spring Boot anti-pattern:**
`AP-S2.35a/spring-boot` — `repository.delete(entity)` issuing a physical `DELETE` on an auditable entity — the audit trail is destroyed.

---

## Resilience

### S2.81/spring-boot — External Call Resilience (Timeout · Retry · Circuit Breaker · Fallback)

**Universal rule (from C2):**
> Every call across a network boundary has a timeout, bounded retries, a circuit breaker, and a defined fallback.

**Spring Boot binding:**
External calls go through a typed client (`RestClient`/`WebClient` or a generated Feign client) wrapped with Resilience4j: `@TimeLimiter`, `@Retry` (bounded, with backoff), and `@CircuitBreaker(name = "...", fallbackMethod = "...")` with an explicit fallback method (cached/degraded result). No external call blocks unbounded or hard-fails the request when the dependency is down.

```java
@CircuitBreaker(name = "rates", fallbackMethod = "cachedRate")
@Retry(name = "rates")
@TimeLimiter(name = "rates")
CompletableFuture<Rate> fetchRate(String pair) { ... }
Rate cachedRate(String pair, Throwable t) { return rateCache.lastKnown(pair); }
```

**Spring Boot anti-pattern:**
`AP-S2.81a/spring-boot` — A raw `RestTemplate` call with no timeout, retry, or circuit breaker — one slow third party cascades into total request failure.

---

## Cross-Cutting

### S2.17/spring-boot — CORS Is Configured Explicitly per Environment

**Universal rule (from C2):**
> CORS allowed origins are configured explicitly per environment — never a wildcard in production.

**Spring Boot binding:**
A `CorsConfigurationSource` reads allowed origins from environment-specific configuration (`application-{profile}.yaml`); production lists exact origins. `*` is never used in production. CORS is wired into the `SecurityFilterChain`.

**Spring Boot anti-pattern:**
`AP-S2.17a/spring-boot` — `setAllowedOrigins(List.of("*"))` in a production profile — any origin can call the API with credentials.

---

### S2.18/spring-boot — APIs Do Not Expose Internal System Details in Error Messages

**Universal rule (from C2):**
> Error responses never expose stack traces, SQL, or internal system details.

**Spring Boot binding:**
The global handler maps unexpected exceptions to a generic 500 message and logs the detail server-side with a correlation id. `server.error.include-stacktrace=never` and `include-message=never` are set so the framework never leaks internals to the client.

**Spring Boot anti-pattern:**
`AP-S2.18a/spring-boot` — Returning `e.getMessage()` or a stack trace in the response body — internal structure and SQL leak to clients.

---

## Coverage note

This binding maps the architecturally load-bearing C2 standards to Spring Boot. The remaining C2 standards either bind identically to the patterns above (same envelope, same handler, same `@Service`/`@Transactional` discipline) or are stack-neutral. Additional bindings are added as real Spring Boot systems are built under Governova, using `templates/implementation-guide-template.md`.
