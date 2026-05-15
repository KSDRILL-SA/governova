# KSDRILL SA — Constitutional System

> *"Build constitutions in the order your system would fail without them."*

[![Constitutions](https://img.shields.io/badge/Constitutions-11-blue)](constitutions/)
[![Version](https://img.shields.io/badge/Version-v1.0-green)](constitutions/C00-constitutional-order.md)
[![Status](https://img.shields.io/badge/Status-LOCKED-red)](constitutions/C00-constitutional-order.md)
[![Locked](https://img.shields.io/badge/Locked-2026--05--08-orange)](constitutions/C00-constitutional-order.md)

---

## What This Is

`system-design-template` is the constitutional governance system for all KSDRILL SA engineering work. It contains 11 constitutions governing every technical and product decision, 4 implementation guides with production-ready code patterns, supporting indexes, overlays, runbooks, and templates.

**This repo is never committed into an application.** Clone it beside your project:

```bash
# Solo development
git clone https://github.com/MALULEKE-KS/system-design-template.git .ksdrill

# Team development
git clone https://github.com/MALULEKE-KS/system-design-template.git _governance
```

Add to your application's `.gitignore`:
```
.ksdrill/
_governance/
```

---

## Quick Start

```bash
# 1. Clone this repo alongside your project (above)
# 2. AI reads first — every session
cat AI-INSTRUCTIONS.md

# 3. Check the complete repo map (reading clusters + ordered file list)
open MANIFEST.md

# 4. Read the constitutional order
open constitutions/C00-constitutional-order.md

# 5. Find the right standard fast
open indexes/quick-reference.md

# 6. Create your system context file
cp system-contexts/fundslink-context.md system-contexts/{your-system}-context.md
```

---

## Repository Structure

```
system-design-template/
│
├── AI-INSTRUCTIONS.md                         ← AI reads this first, every session
├── MANIFEST.md                                ← AI reading graph — complete file map
├── README.md
├── LICENSE
│
├── constitutions/                             ← Constitutions C00–C10, paired with implementation guides
│   ├── C00-constitutional-order.md            ← Master — governs all
│   ├── C01-engineering-standards.md           ← Phase 0 — 97 standards
│   ├── C02-backend-constitution.md            ← Phase 1 — 80 standards
│   ├── C02-backend-implementation.md          ←   └─ paired implementation guide
│   ├── C03-auth-constitution.md               ← Phase 1 — 36 standards (highest security authority)
│   ├── C03-auth-implementation.md             ←   └─ paired implementation guide
│   ├── C04-frontend-constitution.md           ← Phase 1 — 82 standards
│   ├── C04-frontend-implementation.md         ←   └─ paired implementation guide
│   ├── C05-database-constitution.md           ← Phase 1 — 64 standards
│   ├── C05-database-implementation.md         ←   └─ paired implementation guide
│   ├── C06-fullstack-architecture-constitution.md ← Phase 1 — 44 standards
│   ├── C07-testing-constitution.md            ← Phase 2 — 43 standards
│   ├── C08-platform-reliability-constitution.md ← Phase 2 — 82 standards
│   ├── C09-product-feature-constitution.md    ← Phase 3 — 30 standards (The Crown Jewel)
│   └── C10-ai-collaboration-constitution.md   ← Phase 3 — 36 standards
│
├── workflow/                                  ← Studio operating standards
│   └── ksdrill-sa-ai-workflow.md              ← 5-engineer relay model + Handoff Protocol
│
├── overlays/                                  ← Process adaptations by operating mode
│   ├── solo-dev-overlay.md
│   └── team-overlay.md
│
├── indexes/                                   ← Fast navigation layer
│   ├── quick-reference.md                     ← Fastest path to the right standard
│   ├── standards-index.md                     ← All 594 standards with descriptions
│   ├── anti-patterns-index.md                 ← All anti-patterns for code review
│   └── stack-assignment-matrix.md             ← Stack decision framework
│
├── adrs/                                      ← Architecture Decision Records
│   ├── ADR-000-template.md
│   ├── ADR-001-fundslink-stack.md             ← Angular + FastAPI — accepted
│   ├── ADR-002-maphophe-stack.md              ← Next.js — accepted
│   ├── ADR-003-reserve-bank-stack.md          ← Angular + FastAPI — accepted
│   └── ADR-004-syncup-stack.md                ← Next.js — accepted
│
├── templates/                                 ← Mandatory document templates
│   ├── CONSTITUTION-INDEX-template.md         ← Per-project AI session index
│   ├── feature-proposal-template.md
│   ├── incident-report-template.md
│   ├── post-mortem-template.md
│   └── sprint-retro-template.md
│
├── runbooks/                                  ← Step-by-step operational response
│   ├── SEV0-response-runbook.md
│   ├── SEV1-response-runbook.md
│   ├── financial-freeze-runbook.md            ← Reserve Bank financial incident
│   ├── vercel-rollback-runbook.md
│   ├── railway-deployment-runbook.md
│   ├── database-migration-runbook.md
│   └── ai-degradation-runbook.md             ← FundsLink LangChain/ChromaDB
│
└── system-contexts/                           ← Per-system AI session startup files
    ├── fundslink-context.md
    ├── maphophe-context.md
    ├── reserve-bank-context.md
    └── syncup-context.md
```

---

## Constitution Register

| # | Constitution | Phase | Standards | Paired With | Status |
|---|---|---|---|---|---|
| **C0** | Constitutional Order | Master | §1–§14 | — | LOCKED |
| **C1** | Engineering Standards | Phase 0 | 97 | — | LOCKED |
| **C2** | Backend Constitution | Phase 1 | 80 | C2 Implementation | LOCKED |
| **C3** | Auth Constitution | Phase 1 | 36 | C3 Implementation | LOCKED |
| **C4** | Frontend Constitution | Phase 1 | 82 | C4 Implementation | LOCKED |
| **C5** | Database Constitution | Phase 1 | 64 | C5 Implementation | LOCKED |
| **C6** | Full-Stack Architecture | Phase 1 | 44 | — | LOCKED |
| **C7** | Testing Constitution | Phase 2 | 43 | — | LOCKED |
| **C8** | Platform Reliability | Phase 2 | 82 | — | LOCKED |
| **C9** | Product & Feature | Phase 3 | 30 | — | LOCKED |
| **C10** | AI Collaboration | Phase 3 | 36 | — | LOCKED |

**Total: 594 unique standards · 11 constitutions · 4 implementation guides · Lock date: 2026-05-08**

---

## Flagship Systems

| System | Stack | Build Phase | Primary Problem |
|--------|-------|-------------|----------------|
| **FundsLink Academy** | Angular + FastAPI | Q2 2026 — Active | 342,000+ students excluded from education funding |
| **Maphophe Community System** | Next.js | Q3 2026 | Rural villages with no digital governance infrastructure |
| **KSDRILL Reserve Bank** | Angular + FastAPI | Q4 2026 | Passive savings tools with no discipline enforcement |
| **SyncUp Creator Platform** | Next.js | Q1 2027 | Unstructured creator negotiations with no formal process |

---

## Key Design Decisions

| Decision | What Was Decided |
|----------|-----------------|
| **Document format** | Markdown only — HTML eliminated |
| **Version** | All constitutions at v1.0, locked 2026-05-08 |
| **Terminology** | Standards / Anti-Patterns / Practices / Adaptations / Extensions |
| **Standard IDs** | `S{C}.{N}` — constitution-scoped for unambiguous cross-references |
| **Styling** | Tailwind (layout) + Custom CSS (brand) — both first-class, neither optional |
| **Database access** | Prisma ORM (primary) + Raw SQL (governed, first-class) — both tools, clear criteria |
| **Solo/team split** | Overlays only — constitutions are universal |
| **Auth Override Rule** | C3 beats all constitutions on security decisions — C0 §7.3 |
| **AI governance** | 5-engineer relay (Claude→Claude Code→ChatGPT→DeepSeek→Kimi) + Founder approval gate — S10.8 |
| **AI engineer workflow** | `workflow/ksdrill-sa-ai-workflow.md` — constitutionalized relay operating standard |

---

## Amendment Process

All constitutional amendments follow **C0 §8 Amendment Protocol**. No standard changes without:
1. GitHub Issue in this repo tagged `constitutional-amendment`
2. AI adversarial review (solo) or 48h team review
3. Owner approval: Maluleke Kurhula Success
4. Version bump + amendment log entry + cross-constitution updates

---

## Industry References

- [Google SRE Book](https://sre.google/sre-book/table-of-contents/) — Incident management patterns
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/) — Reliability principles
- [OWASP Top 10](https://owasp.org/www-project-top-ten/) — Security baseline
- [Shape Up (Basecamp)](https://basecamp.com/shapeup) — Feature scoping methodology
- [Prisma Documentation](https://www.prisma.io/docs) — ORM standards source

---

**Organisation:** KSDRILL SA  
**Owner:** Maluleke Kurhula Success  
**Repository:** `system-design-template`  
**Licence:** MIT
