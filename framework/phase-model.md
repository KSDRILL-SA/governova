# Phase Model — Universal Primitive

| Attribute | Value |
|-----------|-------|
| **Layer** | 1 — Framework |
| **Type** | Universal primitive |
| **Source** | Extracted from C00-constitutional-order.md §6 |

---

The four phases are the read order, the dependency order, and the failure order.

| Phase | Name | Read Before | If Skipped |
|-------|------|-------------|------------|
| 0 | Foundation | Any code is written | No shared definition of done; first PR embeds unremovable patterns |
| 1 | Core Architecture | First line of application code | No boundaries, no auth, no database assignment; first endpoint corrupts all |
| 2 | Quality & Reliability | Any feature is production-ready | Ships without testing strategy, deployment governance, or incident response |
| 3 | Product & Intelligence | Any roadmap or AI session | Product decisions made against unstable technical foundation |

## Phase dependency

Phase 1 depends on Phase 0.
Phase 2 depends on Phase 1.
Phase 3 depends on Phase 2.

C6 (Full-Stack Architecture) is in Phase 1 but depends on all other Phase 1
constitutions — it synthesises C2, C3, C4, C5 rather than introducing new standards.
