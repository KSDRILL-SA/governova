# ADR-001 — FundsLink Academy: Angular + FastAPI Stack Assignment

---

| Attribute      | Value |
|----------------|-------|
| **ID**         | ADR-001 |
| **Date**       | 2026-05-08 |
| **Status**     | accepted |
| **Supersedes** | — |
| **Relates To** | `S6.1` (SEO), `S6.2` (Enterprise/Financial), `S6.3` (Financial Precision), `S6.4` (Python AI) |

---

## Context

FundsLink Academy is a funding discovery and application platform serving 342,000+ South African students excluded from education funding yearly. The platform requires:

1. **Multi-role enterprise dashboard** — students, funders, administrators each have distinct complex workflows with role-gated views, form-heavy data entry, and reactive state across multiple data sources.
2. **AI-powered eligibility matching** — a LangChain RAG pipeline with ChromaDB semantic search requires a native Python backend. This is a core feature, not an add-on.
3. **Funding calculations** — scholarship amounts, eligibility thresholds, and funding totals require decimal precision arithmetic. JavaScript floating-point (`0.1 + 0.2 = 0.30000000000000004`) is structurally unsuitable.
4. **Three-database architecture** — PostgreSQL for structured entity data, MongoDB for AI-generated scholarship reasoning content, ChromaDB for vector embeddings. All three need native Python support.
5. **Not SEO-critical at launch** — the primary access path is institutional referral and student portal login, not search engine discovery. SSR/SSG are not primary requirements.

---

## Decision

**FundsLink Academy is assigned to the Angular + FastAPI stack.**

Angular with strict TypeScript and Reactive Forms handles the enterprise multi-role dashboard requirements. FastAPI with Python provides: native LangChain integration, Python `Decimal` arithmetic for financial calculations, Beanie ODM for MongoDB, and ChromaDB HTTP client — all in their native ecosystem without wrappers.

The decision is immutable for the v1 lifetime of FundsLink Academy. A stack change requires a new ADR superseding this one and a Major amendment to C6.

---

## Consequences

### What becomes easier
- LangChain RAG pipeline runs natively in Python with full ecosystem access
- `Decimal` precision for all financial calculations without library workarounds
- Angular Reactive Forms handle the complex multi-field scholarship application forms natively
- Beanie ODM and ChromaDB client integrate directly with FastAPI's async model
- FastAPI's `Depends()` injection provides clean RBAC for multi-role access

### What becomes harder
- Two separate deployment targets (Vercel for Angular, Railway for FastAPI) require coordinated deploys (S6.29)
- Angular+FastAPI JWT auth is more complex than NextAuth database sessions (S3.13–S3.20)
- Two separate build pipelines in CI (S8.16)

### Constitutional alignment
- S6.2 — Enterprise dashboard criteria met: complex multi-role dashboards with form-heavy workflows
- S6.3 — Financial precision criteria met: scholarship amounts and funding calculations
- S6.4 — Python AI criteria met: LangChain, ChromaDB, embedding pipeline
- C0 §10 — Stack assignment registered in Constitutional Order

---

## Alternatives Considered

| Option | Why Rejected |
|--------|-------------|
| Next.js + Node.js | Cannot run LangChain natively. `number` float type unsuitable for financial calculations. No native Python ecosystem for AI pipeline. |
| Next.js + FastAPI (hybrid) | Angular is the correct choice for enterprise dashboards — React/Next.js would require significantly more custom implementation for the form complexity. The decision criteria clearly point to Angular. |
| Angular + FastAPI + separate AI microservice | Adds infrastructure complexity without benefit. FastAPI already runs Python — LangChain belongs in the same service, not a separate deployment. |

---

## Approved Deviations

*None — this system applies all constitutional standards without deviation at v1.0.*

---

> **Status: accepted — 2026-05-08**
> *Owner approval: Maluleke Kurhula Success*
