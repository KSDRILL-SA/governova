# Spring Boot — Implementation Binding (Layer 3)

**Status:** Active — first non-reference binding
**Binds:** C02 — Backend
**Stack:** Spring Boot 3.x · Java 21 / Kotlin · Spring Web · Spring Data JPA · Bean Validation · Resilience4j · springdoc-openapi

The Spring Boot binding of the universal C2 Backend standards. Each `### S2.N/spring-boot`
binding maps one universal standard to a concrete Spring Boot pattern (with its anti-pattern),
proving the universal core — written against a FastAPI reference — governs the JVM/Spring stack
without changing a single core standard.

| File | Purpose |
|------|---------|
| `C02-backend-spring-boot.md` | The C2 → Spring Boot bindings (registered in the engine; compiled into the index) |

This binding is registered in `scripts/governova_compile/discovery.py` and is parsed into the
compiled index (`compiled/constitution.json`) by `governova-compile`. See
`constitution/implementation/README.md` and `constitution/indexes/stack-selection-guide.md`.
