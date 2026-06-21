# C7 — Testing Constitution

---

| Attribute          | Value                                                              |
|--------------------|--------------------------------------------------------------------|
| **Document**       | C7 — Testing Constitution                                          |
| **Organisation**   | KSDRILL SA                                                         |
| **Version**        | v1.0                                                               |
| **Status**         | LOCKED                                                             |
| **Locked**         | 2026-05-08                                                         |
| **Next Review**    | 2026-08-08                                                         |
| **Applies To**     | Both Stacks                                                        |
| **Paired With**    | — (No implementation guide — toolchain reference in §7.44)        |

---

> *"Untested code is broken code waiting to be discovered. Tests written after the feature test the implementation, not the behaviour."*

---

## Opening Statement

The Testing Constitution governs the strategy, toolchain, coverage requirements, and quality gates for every test written across all KSDRILL SA systems. Testing is not a phase that comes after development — it is a practice concurrent with development. Tests are written alongside features in the same pull request. Coverage gates are hard CI gates. The testing toolchain is assigned by stack and cannot be mixed.

This constitution is the enforcement layer for the quality promises made in other constitutions. C2 says the service layer is the business logic boundary — C7 says every function in that service layer has a unit test. C3 says auth protects every route — C7 says every protected route has tests for both authenticated and unauthenticated states. C4 says UI is mobile-first — C7 says visual regression runs at 320/375/390px on every PR.

This constitution does not govern what features are built — that is C9. It does not govern how features are designed — that is C1. What this constitution governs is the quality validation layer that confirms every feature meets the standards it was built against.

---

## Table of Contents

| Part | Title | Standards |
|------|-------|-----------|
| Part 1 | Test Strategy & Toolchain | S7.1–S7.6 |
| Part 2 | Unit & Integration Testing | S7.7–S7.16 |
| Part 3 | E2E & Visual Regression | S7.17–S7.24 |
| Part 4 | Coverage & CI Gates | S7.25–S7.30 |
| Part 5 | Python / FastAPI Testing | S7.31–S7.38 |
| Part 6 | Test Database Governance | S7.39–S7.43 |
| Toolchain Reference | — | §7.44 |
| Anti-Patterns Index | — | AP-S7.* |
| Cross-Constitution Dependency Map | — | — |
| Amendment Log | — | — |

---

## Part 1 — Test Strategy & Toolchain (`S7.1`–`S7.6`)

---

### S7.1 — Tests Written Alongside Code — Never After

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S7.1 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S1.27` (feature lifecycle — tests in the same PR) |
| **Enforced By** | PR review — tests required before approval |

**Standard:**
Tests are written in the same PR as the feature code they validate. "I'll write tests later" is a constitutional violation. A feature PR without corresponding tests is not approved for merge. The only exception is a pure refactor PR that changes no behaviour and relies on existing test coverage to validate correctness.

**Rationale:**
Tests written after a feature are written to match the implementation, not the specification. They verify that the code does what it currently does — which may include the bugs. Tests written alongside a feature are written against the acceptance criteria, which means they catch implementation bugs before merge.

**Anti-Patterns:**
- `AP-S7.1a` — Separate "test tickets" in the sprint for tests to be written after features — tests written in a separate PR have no way to validate the feature against its original acceptance criteria.

**Cross-References:** `S1.27` (feature lifecycle), `S1.45` (author self-review checklist includes test verification), `CF-10`

---

### S7.2 — Test Runner Assignment — Locked by Stack, Never Mixed

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S7.2 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S6.1` (stack assignment) |
| **Enforced By** | CI — fails if wrong runner is installed |

**Standard:**
Test runner assignment is locked by stack. Next.js: Jest + React Testing Library for unit/integration, Playwright for E2E and visual regression. Angular: Vitest + `@analogjs/vitest-angular` for unit/integration, Playwright for E2E. Python/FastAPI: pytest + pytest-asyncio for all backend tests. Installing a non-assigned test runner in a repository is a CI failure.

**Rationale:**
Mixed test runner configurations produce inconsistent results, conflicting configuration files, and knowledge fragmentation. The single test runner per context ensures all team members share the same tooling knowledge.

**Anti-Patterns:**
- `AP-S7.2a` — Karma + Jasmine in an Angular project — legacy test runner; Vitest is the assigned runner.
- `AP-S7.2b` — Jest in an Angular project — creates configuration conflicts with Vitest.
- `AP-S7.2c` — Enzyme in a Next.js project — tests implementation details; RTL is the assigned library.

**Cross-References:** `S4.56` (Angular Vitest standard), `S7.8` (Angular TestBed)

---

### S7.3 — Test the Behaviour, Not the Implementation

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S7.3 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | — |
| **Enforced By** | Code Review |

**Standard:**
Tests assert what a function, component, or endpoint does — its outputs, its side effects, its rendered UI — not how it does it. Tests that assert on internal state, private methods, implementation details, or internal component properties break on every refactor. A test suite that requires updating on every refactor is not a safety net — it is a maintenance burden.

**Rationale:**
Tests that survive refactors are tests that describe behaviour. "This endpoint returns 200 with a list of scholarships when authenticated" survives a complete service layer rewrite. "This service calls the repository's `findAll` method" does not survive any internal refactor.

**Anti-Patterns:**
- `AP-S7.3a` — `expect(component.isLoading).toBe(false)` on a private property — tests internal state; testing what the user sees (`expect(screen.queryByRole('progressbar')).not.toBeInTheDocument()`) is correct.

**Cross-References:** `S7.8` (Angular TestBed uses fixture assertions, not internal properties)

---

### S7.4 — Tests Are Independent — No Shared Mutable State Between Tests

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S7.4 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | — |
| **Enforced By** | Code Review · Test isolation audit |

**Standard:**
Each test runs in isolation and produces the same result regardless of execution order. `beforeEach`/`afterEach` reset state between tests. Database tests use transactions that roll back after each test. Shared mutable state between tests is the primary cause of flaky tests.

**Anti-Patterns:**
- `AP-S7.4a` — `let user` declared at describe scope and mutated by multiple `it` blocks — the mutation from one test affects subsequent tests; order of execution determines correctness.

**Cross-References:** `S7.13` (mocks reset between tests), `S7.39` (test database transactions)

---

### S7.5 — Test Names Describe Behaviour in Plain English

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S7.5 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | — |
| **Enforced By** | Code Review |

**Standard:**
Test names describe the behaviour being tested, not the function name. Format: `it("returns empty array when no scholarships match the threshold")` not `it("findMatches works")`. A failing test name must explain what broke without the reader needing to open the test body.

**Anti-Patterns:**
- `AP-S7.5a` — `it("test1")` or `it("works correctly")` — meaningless test name; the failure message is uninformative.
- `AP-S7.5b` — `it("fetchScholarships")` describing the function name — when it fails, the message says "fetchScholarships" which explains nothing about what broke.

**Cross-References:** `S1.83` (documentation standards — same clarity principle)

---

### S7.6 — Critical Paths Run on Every PR — Full Suite Runs Nightly

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S7.6 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S8.9` (CI/CD pipeline) |
| **Enforced By** | GitHub Actions CI config |

**Standard:**
PR CI runs: lint + typecheck, unit tests, integration tests, and critical path E2E tests. PR CI completes in under 5 minutes. The full E2E suite and visual regression suite run on a nightly CI job against the staging environment. This balance keeps PR feedback fast while ensuring comprehensive coverage is validated daily.

**Anti-Patterns:**
- `AP-S7.6a` — Full Playwright E2E suite on every PR — a 45-minute CI job on every PR makes the PR process unusable; reserve full E2E for nightly runs.

**Cross-References:** `S8.10` (CI pipeline time gate — under 5 minutes)

---

## Part 2 — Unit & Integration Testing (`S7.7`–`S7.16`)

---

### S7.7 — Every Service Function Has a Unit Test

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S7.7 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S2.1` (service layer), `S7.1` (tests alongside code) |
| **Enforced By** | Coverage gate (S7.25) · Code Review |

**Standard:**
Every function in the service layer (Angular services, Next.js API utilities, Python FastAPI services) has at least one unit test covering the primary success path and one covering the primary failure path. Service functions without tests block PR merge.

**Anti-Patterns:**
- `AP-S7.7a` — Service functions with 0% unit test coverage — the service layer is the business logic boundary; untested services are the highest-risk untested code.

**Cross-References:** `S2.1` (service layer), `S7.25` (coverage gate)

---

### S7.8 — Angular: Test With TestBed and Fixture Assertions — Not Internal Properties

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S7.8 |
| **Priority**    | Critical |
| **Applies To**  | Angular Only |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S7.2` (Vitest + Angular utilities), `S7.3` (behaviour, not implementation) |
| **Enforced By** | Code Review |

**Standard:**
Angular component tests use `TestBed.createComponent()` and assert on rendered output via `fixture.nativeElement` queries and `fixture.debugElement.query()`. Use `@testing-library/angular` for accessible query patterns. Never assert on component class properties directly — test what the user sees.

**Anti-Patterns:**
- `AP-S7.8a` — `expect(component.scholarships.length).toBe(3)` — tests internal array state; the user sees a rendered list.  Test `expect(screen.getAllByRole('listitem')).toHaveLength(3)` instead.

**Cross-References:** `S7.3` (behaviour not implementation), `S4.53` (OnPush — requires `detectChanges()` in tests)

---

### S7.9 — Next.js: React Components Tested With RTL — No Enzyme

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S7.9 |
| **Priority**    | Critical |
| **Applies To**  | Next.js Only |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S7.2` (Jest + RTL) |
| **Enforced By** | Code Review · package.json audit |

**Standard:**
React component tests use React Testing Library exclusively. Enzyme is forbidden — it encourages testing implementation details. RTL queries by accessible role, text, or label mirror how users interact with UI. `getByRole`, `getByText`, and `findBy*` async queries are the standard patterns.

**Anti-Patterns:**
- `AP-S7.9a` — `wrapper.find('Button').simulate('click')` (Enzyme) — tests the component tree structure, not user interaction.

**Cross-References:** `S7.3` (behaviour not implementation), `S7.2` (RTL assignment)

---

### S7.10 — API Integration Tests Use a Real Test Database — Not Mocked DB

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S7.10 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S7.39` (test database governance), `S7.4` (test isolation) |
| **Enforced By** | CI — Docker Compose spins up test DB |

**Standard:**
Integration tests for API endpoints run against a real test PostgreSQL database — not SQLite, not an in-memory mock, not a mocked Prisma client. The test database is seeded with fixtures before each test suite and reset via transaction rollback after each test. Docker Compose provides the test database locally and in CI.

**Rationale:**
Mocked databases test that the mock behaves correctly, not that the application behaves correctly against a real database. SQL dialects, constraint violations, and transaction behaviour differ between SQLite and PostgreSQL. Real database tests catch these differences.

**Anti-Patterns:**
- `AP-S7.10a` — `jest.mock('../../lib/prisma')` and mocking all Prisma client calls for integration tests — this tests that the mock returns the right values, not that the database query is correct.

**Cross-References:** `S7.39` (test database setup), `S7.40` (transaction rollback per test)

---

### S7.11 — Auth Routes Tested for Authenticated and Unauthenticated States

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S7.11 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S3.7` (Next.js route protection), `S3.17` (FastAPI Depends()) |
| **Enforced By** | Code Review · Integration tests |

**Standard:**
Every protected API endpoint has integration tests verifying: (1) authenticated user with correct role can access it and receives 200, (2) unauthenticated request receives 401, (3) authenticated user with wrong role receives 403. Auth test coverage is non-negotiable regardless of overall coverage percentage.

**Anti-Patterns:**
- `AP-S7.11a` — Only testing the happy path (authenticated success) for a protected endpoint — the security of the endpoint is untested; a misconfigured `Depends()` is not caught.

**Cross-References:** `S3.7` (Next.js auth), `S3.17` (FastAPI Depends()), `S3.22` (ownership verification — should also be tested)

---

### S7.12 — Angular HTTP Interceptor Tests — JWT Attachment and 401 Refresh

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S7.12 |
| **Priority**    | Critical |
| **Applies To**  | Angular Only |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S3.15` (interceptor with deduplication), `S7.2` (Vitest) |
| **Enforced By** | Code Review · CI |

**Standard:**
The Angular auth HTTP interceptor must have dedicated integration tests covering: (1) access token is attached to requests as Bearer header, (2) 401 triggers silent refresh, (3) refresh success — original request retried with new token, (4) refresh failure — user redirected to login, (5) multiple concurrent 401s trigger exactly one refresh request (deduplication). Use `HttpClientTestingModule` to mock HTTP responses.

**Anti-Patterns:**
- `AP-S7.12a` — No test for the concurrent 401 deduplication scenario — the most critical and complex interceptor behaviour is untested; a broken deduplication causes unexpected logouts in production.

**Cross-References:** `S3.15` (interceptor deduplication standard), `S4.56` (Angular Vitest)

---

### S7.13 — Mocks Are Reset Between Tests

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S7.13 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S7.4` (test independence) |
| **Enforced By** | Jest/Vitest config (`clearMocks: true`) |

**Standard:**
All mocks, stubs, and spies are cleared and reset after each test. Jest: `clearMocks: true` in Jest config or `jest.clearAllMocks()` in `afterEach`. Vitest: equivalent config. Python: `@pytest.fixture(autouse=True)` with patch teardown. Persistent mock state between tests is the second most common cause of flaky tests (after shared mutable state).

**Anti-Patterns:**
- `AP-S7.13a` — `jest.spyOn(service, 'fetchScholarships')` without `mockRestore()` or `clearMocks: true` — the spy persists between tests; a test that doesn't set up the spy inherits the previous test's mock.

**Cross-References:** `S7.4` (test independence)

---

### S7.14 — MSW for API Mocking in Next.js — Never `fetch()` Mocks

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S7.14 |
| **Priority**    | High |
| **Applies To**  | Next.js Only |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S7.2` (Jest + RTL) |
| **Enforced By** | Code Review |

**Standard:**
Frontend API mocking in Next.js uses Mock Service Worker (MSW). `jest.fn()` patches on `global.fetch` are forbidden for API mocking. MSW intercepts at the network layer — it tests the actual fetch call, error handling, and retry logic, not just the function that calls fetch.

**Anti-Patterns:**
- `AP-S7.14a` — `global.fetch = jest.fn().mockResolvedValue(...)` — mocks the function, not the network; does not test the actual fetch implementation, error handling, or response parsing.

**Cross-References:** `S7.2` (Next.js test toolchain)

---

### S7.15 — Cross-Database Write Operations Have Integration Tests

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S7.15 |
| **Priority**    | High |
| **Applies To**  | Angular Only |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S5.53` (cross-database sync standards), `S7.10` (real test DB) |
| **Enforced By** | Code Review |

**Standard:**
Every operation writing to multiple databases (PostgreSQL + MongoDB, PostgreSQL + ChromaDB) has integration tests for: (1) both writes succeed correctly, and (2) when the second write fails, the first write rolls back or is marked for retry. Cross-database failure scenarios are explicitly tested.

**Anti-Patterns:**
- `AP-S7.15a` — Integration test covers only the success path of a cross-database write — the failure path (PostgreSQL succeeds, MongoDB fails) produces data inconsistency that is never tested and therefore never caught.

**Cross-References:** `S5.53` (cross-DB sync standards), `S5.20` (raw SQL transactions)

---

### S7.16 — Snapshot Tests Are Banned — Use Explicit Assertions

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S7.16 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S7.3` (behaviour not implementation) |
| **Enforced By** | Code Review |

**Standard:**
Jest/Vitest snapshot tests (`expect(component).toMatchSnapshot()`) are forbidden for component testing. Snapshots encode implementation details and are blindly updated when they fail, providing no regression protection. Use explicit assertions: `expect(screen.getByRole('button')).toHaveTextContent('Submit')`.

**Anti-Patterns:**
- `AP-S7.16a` — `expect(wrapper.html()).toMatchSnapshot()` — the snapshot captures every CSS class, every attribute, every child element; any non-breaking refactor fails the snapshot and it gets updated without review.

**Cross-References:** `S7.3` (behaviour not implementation), `S7.17` (Playwright for visual regression)

---

## Part 3 — E2E & Visual Regression (`S7.17`–`S7.24`)

---

### S7.17 — Playwright for E2E — Both Stacks, Same Test Patterns

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S7.17 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S7.2` (toolchain assignment) |
| **Enforced By** | CI — Playwright nightly job |

**Standard:**
All E2E tests use Playwright for both Next.js and Angular systems. Same test patterns, same Playwright config, same CI integration. Cypress is not used. Playwright provides better async handling, true parallel execution, and built-in visual comparison capabilities.

**Anti-Patterns:**
- `AP-S7.17a` — Cypress in any KSDRILL SA project — Cypress's single-tab limitation and iframe restrictions create test reliability issues for the authentication flows used in both stacks.

**Cross-References:** `S7.2` (test runner assignment)

---

### S7.18 — E2E Tests Cover Every Critical Path — Auth, Primary Feature, Error

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S7.18 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S7.17` (Playwright) |
| **Enforced By** | CI — nightly E2E job |

**Standard:**
The minimum E2E test suite for every platform: (1) full registration and email verification flow, (2) login with valid credentials, (3) login with invalid credentials — error shown correctly, (4) primary platform feature end-to-end, (5) logout and verify session cleared. These 5 paths are the minimum viable E2E suite. Every system ships with these before v1.

**Anti-Patterns:**
- `AP-S7.18a` — E2E tests only for the happy path — a login form that shows nothing on invalid credentials is only discovered in production.

**Cross-References:** `S7.17` (Playwright), `S7.11` (auth tests), `C9` (primary workflow definition)

---

### S7.19 — Visual Regression at 320/375/390px — Every PR Changing UI

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S7.19 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S4.10` (C4 — visual regression standard), `S7.17` (Playwright) |
| **Enforced By** | CI — Playwright visual test job on UI PRs |

**Standard:**
Every PR that changes frontend code runs Playwright visual regression tests at 320px, 375px, and 390px. Layout failure at these widths is a build failure. Baseline screenshots are committed to the repository and updated intentionally — not automatically on failure. Tests live in `tests/visual/` (Next.js) or `e2e/visual/` (Angular).

**Anti-Patterns:**
- `AP-S7.19a` — Visual regression tests at 1280px only — the breakpoints that matter for the user base are 320/375/390px.

**Cross-References:** `S4.10` (C4 — mobile-first visual standard), `S4.2` (320px baseline)

---

### S7.20 — Accessibility Automated Tests in CI — axe-core

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S7.20 |
| **Priority**    | High |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S4.21` (WCAG 2.1 AA), `S7.17` (Playwright) |
| **Enforced By** | CI — axe-core Playwright integration |

**Standard:**
axe-core accessibility checks run on every page in the PR CI pipeline via Playwright's `@axe-core/playwright` integration. Violations with impact `critical` or `serious` are build failures. Violations with impact `moderate` or `minor` are warnings. WCAG 2.1 AA rule set is applied.

**Anti-Patterns:**
- `AP-S7.20a` — Manual accessibility review only — manual review is inconsistent and not performed on every PR; automated CI gates are the baseline.

**Cross-References:** `S4.21` (WCAG 2.1 AA), `S4.19` (keyboard accessibility)

---

### S7.21–S7.24 — Additional E2E Standards

> **S7.21** — Playwright tests use the `page.getByRole()` and `page.getByLabel()` locators — never `page.locator('.some-class')`. CSS class selectors break on every styling refactor.

> **S7.22** — E2E tests run against preview deployments when available — not against localhost in CI. Preview deployment E2E validates the actual deployed artifact.

> **S7.23** — E2E test data is isolated per test run using unique identifiers (timestamp-based email addresses, test-specific user accounts) — tests never depend on pre-existing production data.

> **S7.24** — Playwright's `--reporter=html` generates a test report on every nightly run — stored as a CI artifact for 7 days.

---

## Part 4 — Coverage & CI Gates (`S7.25`–`S7.30`)

---

### S7.25 — Coverage Gates — Locked Thresholds by Stack

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S7.25 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S7.7` (service layer coverage) |
| **Enforced By** | CI — coverage gate fails build below threshold |

**Standard:**
Minimum coverage thresholds enforced by CI: Next.js (Jest): 70% line/statement coverage. Angular (Vitest): 75% line/statement coverage. Python/FastAPI (pytest-cov): 80% line coverage. Dropping below these thresholds fails the build. Coverage is a minimum bar — not a target. 70% with meaningful tests is better than 90% with trivial tests.

**Anti-Patterns:**
- `AP-S7.25a` — Tests written to increase the coverage number by testing trivial getter/setter functions — coverage that doesn't reflect business logic validation provides false confidence.

**Cross-References:** `S7.7` (service coverage), `S7.31` (pytest-cov)

---

### S7.26–S7.30 — Additional Coverage and CI Standards

> **S7.26** — Coverage exclusions are explicit and documented: `/* istanbul ignore next */` requires a comment explaining why the code is intentionally uncovered. Blanket coverage exclusions are a code review block.

> **S7.27** — Coverage reports are generated as CI artifacts on every PR — reviewers can see which lines were added without test coverage.

> **S7.28** — Branch coverage is tracked alongside line coverage — a function that is called but whose error branches are never exercised has misleading line coverage.

> **S7.29** — Auth-related code has 100% branch coverage — the security implications make partial branch coverage unacceptable for authentication logic.

> **S7.30** — Performance budget: CI fails if the bundle size increases by more than 10% from the previous baseline without an explicit justification comment in the PR.

---

## Part 5 — Python / FastAPI Testing (`S7.31`–`S7.38`)

---

### S7.31 — pytest + pytest-asyncio for All FastAPI Tests

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S7.31 |
| **Priority**    | Critical |
| **Applies To**  | Angular Only |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S7.2` (toolchain assignment) |
| **Enforced By** | CI · `requirements.txt` audit |

**Standard:**
All FastAPI tests use pytest with pytest-asyncio for async test functions. `httpx.AsyncClient` with the ASGI TestClient wraps the FastAPI app for API-level integration tests. Coverage via pytest-cov with minimum 80% threshold.

**Anti-Patterns:**
- `AP-S7.31a` — `unittest.TestCase` for FastAPI tests — pytest fixtures, parametrize, and the async ecosystem are not available in unittest; pytest is the assigned runner.

**Cross-References:** `S7.2` (toolchain), `S7.25` (80% coverage gate for Python)

---

### S7.32 — FastAPI Endpoints Tested with httpx ASGI Client

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S7.32 |
| **Priority**    | Critical |
| **Applies To**  | Angular Only |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S7.31` (pytest), `S7.10` (real test database) |
| **Enforced By** | Code Review |

**Standard:**
FastAPI endpoint integration tests use `httpx.AsyncClient(app=app, base_url="http://test")` as the ASGI client — not the Flask-style `TestClient`. The ASGI client runs the full FastAPI middleware stack including auth, validation, and CORS. Integration tests cover: success response with correct schema, validation error (422), auth failure (401), permission failure (403).

**Anti-Patterns:**
- `AP-S7.32a` — Calling service functions directly in tests instead of going through the FastAPI endpoint — bypasses middleware, validation, and auth; tests the service but not the endpoint.

**Cross-References:** `S7.31` (pytest), `S7.11` (auth states tested)

---

### S7.33–S7.38 — Additional Python Testing Standards

> **S7.33** — Pydantic models are unit-tested with valid input, invalid input (expecting ValidationError), and edge cases — Pydantic validation is business logic.

> **S7.34** — pytest fixtures provide test data — no hardcoded test data in test functions. Fixtures are defined in `conftest.py` and scope-labeled (`function`, `session`).

> **S7.35** — FastAPI dependency overrides (`app.dependency_overrides`) are used to inject test dependencies (mock auth, test database) — not monkey-patching.

> **S7.36** — Async pytest tests use `@pytest.mark.asyncio` and the asyncio event loop fixture — never mix sync and async test functions in the same test file.

> **S7.37** — LangChain pipeline tests use fixtures with pre-computed embeddings — never call the actual embedding model in unit tests (cost and latency).

> **S7.38** — Financial calculation tests use `Decimal` for all expected values — not floats. Tests that compare float financial results are incorrect.

---

## Part 6 — Test Database Governance (`S7.39`–`S7.43`)

---

### S7.39 — Separate Test Database — Never Test Against Production or Staging

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S7.39 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks |
| **Phase**       | Phase 2 — Quality & Reliability |
| **Depends On**  | `S7.10` (real test database), `S8.5` (three environments) |
| **Enforced By** | CI Docker Compose · Environment variable audit |

**Standard:**
Integration tests run against a dedicated test database — never production, never staging. The test database URL is configured via `DATABASE_URL_TEST` environment variable in CI. Docker Compose spins up a fresh PostgreSQL instance for CI and local test runs. The test database is seeded and reset per test run — never shared between concurrent CI runs.

**Anti-Patterns:**
- `AP-S7.39a` — Using the staging database URL for integration tests — test writes corrupt staging data; staging can no longer be used for final validation.

**Cross-References:** `S8.5` (three environments), `S7.10` (real test database)

---

### S7.40–S7.43 — Test Database Standards

> **S7.40** — Each integration test runs inside a database transaction that rolls back after the test completes — the database is in a clean state for every test without truncating tables.

> **S7.41** — Prisma migrations are applied to the test database before the test suite runs — `prisma migrate deploy` is part of the CI test setup script.

> **S7.42** — Test fixtures seed the minimum data required for the test — not the entire dataset. Over-seeded fixtures slow down tests and create implicit dependencies.

> **S7.43** — ChromaDB and MongoDB test instances use in-memory or temporary collections that are cleared after each test suite (Angular/FundsLink only).

---

## §7.44 — Testing Toolchain Reference

| Layer | Next.js Stack | Angular Stack | Python/FastAPI |
|-------|--------------|---------------|----------------|
| Unit | Jest + React Testing Library | Vitest + `@analogjs/vitest-angular` | pytest + pytest-asyncio |
| Integration | Jest + MSW | Vitest + `HttpClientTestingModule` | pytest + httpx ASGI client |
| E2E | Playwright | Playwright | pytest E2E via FastAPI TestClient |
| Visual Regression | Playwright at 320/375/390px | Playwright at 320/375/390px | N/A |
| Accessibility | axe-core via Playwright | axe-core via Playwright | N/A |
| Coverage | Jest `--coverage` — min 70% | Vitest `--coverage` — min 75% | pytest-cov — min 80% |
| API mocking | MSW | Angular `HttpClientTestingModule` | pytest fixtures + Beanie mock |

---

## Anti-Patterns Index

| ID | Description | Violated Standard | Severity |
|----|-------------|-------------------|----------|
| `AP-S7.1a` | Separate test tickets written after features | S7.1 | Critical |
| `AP-S7.2a` | Karma + Jasmine in Angular project | S7.2 | Critical |
| `AP-S7.2b` | Jest in Angular project | S7.2 | High |
| `AP-S7.2c` | Enzyme in Next.js project | S7.2 | High |
| `AP-S7.3a` | Assertion on private component property | S7.3 | High |
| `AP-S7.4a` | Shared mutable state between test cases | S7.4 | Critical |
| `AP-S7.5a` | `it("test1")` or meaningless test name | S7.5 | Standard |
| `AP-S7.5b` | Test name is the function name | S7.5 | Standard |
| `AP-S7.6a` | Full Playwright suite on every PR | S7.6 | High |
| `AP-S7.7a` | Service functions with 0% test coverage | S7.7 | Critical |
| `AP-S7.8a` | Assert on component's internal array property | S7.8 | High |
| `AP-S7.9a` | Enzyme `wrapper.find().simulate()` in Next.js | S7.9 | High |
| `AP-S7.10a` | Mocked Prisma client for integration tests | S7.10 | Critical |
| `AP-S7.11a` | Protected endpoint tested for success only | S7.11 | Critical |
| `AP-S7.12a` | No test for concurrent 401 deduplication | S7.12 | Critical |
| `AP-S7.13a` | Spy without mock restore between tests | S7.13 | High |
| `AP-S7.14a` | `global.fetch = jest.fn()` for API mocking | S7.14 | High |
| `AP-S7.15a` | Cross-DB write test covers success path only | S7.15 | High |
| `AP-S7.16a` | `toMatchSnapshot()` for component testing | S7.16 | High |
| `AP-S7.17a` | Cypress in any project | S7.17 | High |
| `AP-S7.18a` | E2E only for happy paths | S7.18 | High |
| `AP-S7.19a` | Visual regression at 1280px only | S7.19 | Critical |
| `AP-S7.20a` | Manual-only accessibility review | S7.20 | High |
| `AP-S7.21a` | Playwright `page.locator('.css-class')` | S7.21 | Standard |
| `AP-S7.25a` | Tests written to hit coverage number | S7.25 | Standard |
| `AP-S7.31a` | `unittest.TestCase` for FastAPI | S7.31 | High |
| `AP-S7.32a` | Service called directly bypassing FastAPI endpoint | S7.32 | High |
| `AP-S7.38a` | Float comparison in financial calculation tests | S7.38 | Critical |
| `AP-S7.39a` | Staging database URL in integration tests | S7.39 | Critical |

---

## Cross-Constitution Dependency Map

**This constitution depends on:**
| Dependency | Reason |
|------------|--------|
| `C0 — Constitutional Order` | Amendment protocol, terminology |
| `C2 — Backend Constitution` | API test shapes (endpoints, response schemas) |
| `C3 — Auth Constitution` | Auth test requirements (401, 403, role tests) |
| `C4 — Frontend Constitution` | Frontend toolchain assignment, visual regression standards |
| `C5 — Database Constitution` | Test database standards, cross-DB integration tests |

**The following constitutions depend on this one:**
| Dependent | Reason |
|-----------|--------|
| `C8 — Platform Reliability` | CI gate: all tests must pass before production deploy |

---

## Amendment Log

| Version | Date | Change | Reason |
|---------|------|--------|--------|
| v1.0 | 2026-05-08 | Initial lock — rebuilt from Testing Constitution v3.0. Test runner assignments updated (Vitest replaces Karma, RTL replaces Enzyme). Cross-database integration test standards (S7.15) added. axe-core CI accessibility gate (S7.20) added. Financial calculation Decimal test requirement (S7.38) added. Toolchain reference table consolidated in §7.44. | Full system rebuild — HTML to Markdown, version reset. |

---

> **LOCKED — v1.0 — 2026-05-08**
>
> This document is locked. No standard may be added, removed, or modified
> without following the Amendment Protocol defined in C0 §8.
> Amendments take effect only after commit to `system-design-template`
> with a version bump and amendment log entry.
