# SaaS / B2B Domain Constitution

| Attribute | Value |
|-----------|-------|
| **Document** | SaaS / B2B Domain Constitution |
| **Layer** | 4 — Domain Extension |
| **Extends** | Universal Core (C00–C10) |
| **Regulatory basis** | General — contractual (DPA, SLA) rather than statutory |
| **Contributed by** | Maluleke Kurhula Success |
| **Version** | v1.0 |
| **Status** | ACTIVE |
| **Applies To** | Any system serving multiple customers from shared infrastructure |

---

> *One customer's data appearing in another customer's account is the only defect from
> which a SaaS business does not recover. Every other failure is an incident; this one
> is the end of the trust the whole model rests on.*

---

## Domain overview

Multi-tenant software is distinguished by a single structural risk: many customers share
one database, one process, and one cache, and the boundary between them is enforced only
by the correctness of the code. There is no physical separation to fall back on.

The universal core already governs authorisation (`S3.24`), typed roles (`S3.21`),
pagination (`S2.14`), rate limiting (`S2.41`), and query discipline (`S2.28`). What it
does not carry is tenancy itself: that every row belongs to a tenant and every query
proves it, that one customer cannot consume another's capacity, that a subscription's
state is derived from an authoritative billing record rather than a mutable flag, and
that a departing customer can leave with their data intact.

Seeded from **SyncUp Creator Platform** — a multi-party negotiation platform where every
record is jointly visible to exactly two tenants and to no one else, and where the
tenancy boundary is the product rather than a deployment detail.

---

## Standards

### D-SAAS.1 — Tenant Isolation Is Enforced by the Data Layer, Not by Query Discipline

| Attribute       | Value |
|-----------------|-------|
| **ID**          | D-SAAS.1 |
| **Priority**    | Critical |
| **Applies To**  | All Stacks · every multi-tenant system |
| **Enforced By** | schema review · reliable-tier rules · integration tests · semantic tier |

**Extends:**
`S1.104` (data access through repositories), `S2.28` (query discipline — the ORM is the source of truth for relational access), `S3.24` (least privilege default)

**Standard:**
Every tenant-scoped row carries a non-nullable tenant identifier, and the tenant filter is applied by a mechanism that cannot be omitted — row-level security, a repository layer that injects it, or an ORM-level global filter — never by each query remembering to include it. The tenant context is derived server-side from the authenticated session and never from a client-supplied parameter, header, or body field. Cross-tenant access, where the product requires it, is an explicit, named, audited operation rather than the absence of a filter. Every tenant-scoped table has an automated test asserting that a query executed in one tenant's context cannot return another tenant's rows.

**Rationale:**
Isolation enforced by convention fails the first time an engineer writes a query without the filter, and that query will look correct in review because a missing `WHERE` clause is invisible — the code reads as though it selects everything because it does. Deriving tenancy from a request parameter turns the boundary into an input, which makes cross-tenant access a matter of editing a value. The per-table test exists because isolation is not a property of the system in general but of each table individually, and the table added last is the one nobody thought about.

**Anti-Patterns:**
- `AP-D-SAAS.1a` — A tenant-scoped query whose tenant filter is supplied per call site rather than by the data layer, or a nullable tenant identifier.
- `AP-D-SAAS.1b` — Tenant context taken from a client-supplied parameter, header, or token claim the client can set.

---

### D-SAAS.2 — One Tenant Cannot Consume Another's Capacity

| Attribute       | Value |
|-----------------|-------|
| **ID**          | D-SAAS.2 |
| **Priority**    | High |
| **Applies To**  | All Stacks · every multi-tenant system |
| **Enforced By** | load test · rate-limit configuration review · monitoring |

**Extends:**
`S2.41` (rate limiting on all public endpoints), `S2.14` (list endpoints support pagination), `S2.81` (external-call resilience)

**Standard:**
Rate limits, concurrency limits, and resource quotas are applied per tenant, not only globally or per IP. Any operation whose cost scales with a tenant's data — exports, reports, bulk writes, search, webhook fan-out — is bounded, paginated, or executed asynchronously on a queue with per-tenant fairness, so that no single tenant's workload can starve another. Background jobs carry tenant context and are scheduled so that one tenant's backlog cannot indefinitely delay another's. Per-tenant saturation is monitored and alerts before it becomes a shared outage.

**Rationale:**
A global rate limit protects the platform from the internet but not tenants from each other: the largest customer, behaving entirely legitimately, becomes a denial-of-service against the smallest. Cost-scaling operations are where this concentrates, because a report that is instant for a new customer takes minutes for the largest one and holds a connection or a worker the whole time. A shared queue without fairness has the same shape — one tenant's bulk import occupies every worker, and every other tenant's jobs simply stop, which reaches the on-call engineer as an unexplained platform-wide stall.

**Anti-Patterns:**
- `AP-D-SAAS.2a` — Rate or concurrency limits applied only globally or per IP, with no per-tenant dimension.
- `AP-D-SAAS.2b` — An unbounded, synchronous operation whose cost scales with tenant data size, or a shared job queue with no per-tenant fairness.

---

### D-SAAS.3 — Entitlement Is Derived From an Authoritative Billing Record

| Attribute       | Value |
|-----------------|-------|
| **ID**          | D-SAAS.3 |
| **Priority**    | Critical |
| **Applies To**  | All Stacks · every system with paid plans or usage limits |
| **Enforced By** | authorisation review · integration tests · reconciliation job |

**Extends:**
`S3.24` (least privilege default), `S2.81` (external-call resilience), `S1.105` (no hardcoded configuration or magic values)

**Standard:**
What a tenant may do is derived from a subscription record that is the single source of truth for plan, status, and limits, and is enforced server-side on every gated path. Plan definitions and limits are configuration, never conditionals scattered through the code. Where billing is handled by an external provider, provider events are verified, processed idempotently, and reconciled against local state on a schedule; a divergence is an incident. Entitlement fails closed on an expired or unknown subscription, and every entitlement change is audited with its cause.

**Rationale:**
Entitlement drifts from billing whenever it is stored as a mutable flag that several code paths may set, and the drift is silently asymmetric — customers notice immediately when they lose access they paid for, and never report access they did not. Provider webhooks make this worse: they arrive out of order, duplicate, and are occasionally lost, so a system that treats them as commands rather than as events to reconcile will eventually hold a state the provider disagrees with. Plan logic expressed as scattered conditionals guarantees that adding a tier requires finding every one of them, and one will be missed.

**Anti-Patterns:**
- `AP-D-SAAS.3a` — Entitlement stored as a mutable flag set from multiple code paths, or plan limits hardcoded as conditionals rather than configuration.
- `AP-D-SAAS.3b` — Billing provider events processed without verification, idempotency, or scheduled reconciliation against local state.

---

### D-SAAS.4 — A Tenant Can Leave With Their Data

| Attribute       | Value |
|-----------------|-------|
| **ID**          | D-SAAS.4 |
| **Priority**    | High |
| **Applies To**  | All Stacks · every multi-tenant system |
| **Enforced By** | export contract review · deletion test · DPA review |

**Extends:**
`S8.86` (vendor register + exit plan), `S5.8` (soft delete, never hard delete), `S8.84` (committed lockfile + CI vulnerability gate)

**Standard:**
Every tenant can export their complete data in a documented, machine-readable format without contacting support, and can request deletion. Deletion is executed within a declared period across every store that holds tenant data — primary database, replicas, backups, object storage, caches, search indexes, and analytics — and completion is recorded and demonstrable. Sub-processors holding tenant data are listed publicly and bound by the same obligation. Export completeness is verified by test, not by assertion: a fixture tenant is exported and the export is checked against the schema for missing entities.

**Rationale:**
Export and deletion are contractual obligations in every enterprise agreement, and they are the two features that are never exercised during development, so they are the two most likely to be quietly broken. Deletion is the harder half: the primary database is straightforward and the derived stores — search indexes, caches, analytics warehouses, backups — are where tenant data survives a deletion that was reported as complete. Verifying export against the schema catches the ordinary failure, which is not a broken export but an incomplete one, silently missing the entity added last quarter.

**Anti-Patterns:**
- `AP-D-SAAS.4a` — Export available only by support request, in an undocumented format, or unverified against the schema for completeness.
- `AP-D-SAAS.4b` — Deletion that covers the primary database but leaves tenant data in search indexes, caches, analytics, or object storage.

---

## Conflict analysis

| Core standard | Interaction | Resolved? |
|---------------|-------------|-----------|
| `S1.104` — Data access through repositories | `D-SAAS.1` makes the repository the enforcement point for tenancy | Yes — a domain-specific instance of `S1.104` |
| `S2.28` — Query discipline, ORM as source of truth | `D-SAAS.1` requires the tenant filter be applied by that layer, not per query | Yes — additive; raw-SQL governance is unchanged |
| `S2.41` — Rate limiting on public endpoints | `D-SAAS.2` adds a per-tenant dimension above the global limit | Yes — raises a floor; the global limit still applies |
| `S2.14` — Pagination on list endpoints | `D-SAAS.2` extends bounding to every cost-scaling operation, not only list endpoints | Yes — additive |
| `S2.81` — External-call resilience | `D-SAAS.3` relies on it for billing-provider calls and adds reconciliation | Yes — additive |
| `S3.24` — Least privilege default | `D-SAAS.1` and `D-SAAS.3` apply it to tenancy and entitlement, failing closed | Yes — additive |
| `S3.21` — Roles as database enums | Tenant roles are expressed as typed enums; no additional requirement | Yes — dependency only |
| `S1.105` — No hardcoded configuration or magic values | `D-SAAS.3` applies it specifically to plan definitions and limits | Yes — a domain-specific instance |
| `S5.8` — Soft delete, never hard delete | `D-SAAS.4` requires genuine erasure on a tenant deletion request | Yes — resolved as an explicit, audited, contractually required erasure path, not an ad-hoc hard delete; `S5.8` continues to govern ordinary application deletes |
| `S8.86` — Vendor register + exit plan | `D-SAAS.4` extends the obligation to sub-processors holding tenant data | Yes — additive |
| `S8.84` — Lockfile + CI vulnerability gate | `D-SAAS.4` relies on the same supply-chain discipline for sub-processor dependencies | Yes — dependency only |

One interaction required explicit resolution: `S5.8` prohibits hard deletion, while a tenant
deletion request contractually requires erasure. Resolved in `D-SAAS.4` as a declared, audited
process across all stores with a recorded basis. All other standards are strictly additive.

---

| Version | Date | Change | Rationale |
|---------|------|--------|-----------|
| v1.0 | 2026-07-28 | Initial SaaS / B2B domain extension — `D-SAAS.1`–`D-SAAS.4`. Seeded from SyncUp Creator Platform. | ADR-005 workstream A — Layer 4 content for the SaaS domain. |
