# SaaS / B2B — `D-SAAS`

**Status:** Ratified — 4 standards (`D-SAAS.1`–`D-SAAS.4`)
**Regulatory basis:** General — contractual (DPA, SLA) rather than statutory
**Seeded from:** SyncUp Creator Platform

The domain constitution is [`D-SAAS-domain-constitution.md`](./D-SAAS-domain-constitution.md).

| ID | Standard |
|----|----------|
| `D-SAAS.1` | Tenant isolation is enforced by the data layer, not by query discipline |
| `D-SAAS.2` | One tenant cannot consume another's capacity |
| `D-SAAS.3` | Entitlement is derived from an authoritative billing record |
| `D-SAAS.4` | A tenant can leave with their data |

Applies to any system serving multiple customers from shared infrastructure — not only to
the reference system it was seeded from. See `constitution/domains/README.md` for the full
registry and `framework/format-specification.md` for the format.
