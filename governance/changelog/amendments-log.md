# Amendments Log — Constitutional Audit Trail

> Every standard amendment is recorded here. This is an append-only audit trail.
> No entry is ever edited or deleted.

---

| Attribute | Value |
|-----------|-------|
| **Document** | Constitutional Amendments Log |
| **Version** | v1.0 |
| **Status** | Active — append only |
| **Created** | 2026-05-22 |

---

## Amendment Record

| Date | Standard ID | Constitution | Change | Rationale | Approved by |
|------|-------------|--------------|--------|-----------|-------------|
| 2026-05-22 | — | All | Initial Governova restructure — no standards changed, only repo structure | Governova v2.0 architecture | Maluleke Kurhula Success |
| 2026-06-21 | S1.99–S1.102, S2.81, S3.37, S6.45, S8.83–S8.87, S10.40 | C1, C2, C3, C6, C8, C10 | Ratified 13 standards: operating-practice governance (workflow + no-AI rule + merge authority), brownfield adoption (characterization tests, non-breaking conversion, reversibility, completeness), and external/ecosystem governance (external-call resilience, integration auth, supply-chain/CVE/license/SBOM, vendor register, temporal governance). Counts: C1 98→102, C2 80→81, C3 36→37, C6 44→45, C8 82→87, C10 39→40. Total 600→613. | Operating practices, brownfield adoption, and external governance made first-class constitutional law | Maluleke Kurhula Success |
| 2026-06-22 | S1.103–S1.107 | C1 | Ratified Part 19 — Architectural Discipline (per ADR-005 workstream A): S1.103 logic lives in its layer, S1.104 data access through repositories, S1.105 no hardcoded configuration/magic values, S1.106 DRY/shared code, S1.107 the simplest correct solution. Count: C1 102→107. Total 613→618. | Universal architectural discipline made first-class law — applicable to any stack and any sector | Maluleke Kurhula Success |
| 2026-07-28 | D-FINTECH.1–.6 | D-FINTECH (Layer 4) | Established Layer 4 as first-class in the engine and ratified the first domain extension: exact monetary values, idempotent value movement, double-entry reconciliation, immutable audit records, separation of initiation from approval, exhaustive testing of financial calculation code. Core count unchanged at 618. Layer 4: 0→6 domain standards. | ADR-005 workstream A — the domain layer existed in the architecture but not in the engine | Maluleke Kurhula Success |
| 2026-07-28 | D-GOVTECH.1–.5, D-EDTECH.1–.4, D-SAAS.1–.4 | D-GOVTECH, D-EDTECH, D-SAAS (Layer 4) | Ratified the three remaining active domain extensions, seeded from Maphophe, FundsLink Academy, and SyncUp respectively. Core count unchanged at 618. Layer 4: 6→19 domain standards across 4 domains, 38 domain anti-patterns. | ADR-005 workstream A complete — every domain with a reference system to ground it is now written | Maluleke Kurhula Success |

> Note: the six C0 §8 amendments that pre-date this log's creation
> (S1.98, S4.83, S5.65, S10.37, S10.38, S10.39) are recorded in their respective
> constitution amendment logs and in the git history. After the 2026-06-22
> ratification the live count is **618** core standards against the 594 locked baseline.
>
> Layer 4 domain standards (`D-{DOMAIN}.{N}`) are tracked separately from the core and
> are **not** included in the 618. As of 2026-07-28 the live Layer 4 count is **19
> domain standards across 4 ratified domains**. A domain may raise a floor the core
> sets; it may never lower, narrow, or override one — every domain document carries a
> completed conflict-analysis table evidencing this.

---

## Ratified 2026-06-21 (formerly pending — now in force)

> These 13 standards were ratified by Founder L4 approval on 2026-06-21 and are now
> **in force** in their constitutions (see each constitution's amendment log). The table
> below is retained as the proposal-to-ratification record.

| Standard ID | Constitution | Standard | Evidence | Paired protocol |
|-------------|--------------|----------|----------|-----------------|
| `S1.99` | C1 | Branch → Issue → PR → Merge workflow order; mandatory full issue/PR metadata (type, milestone, project, labels, assignee) | Untracked, metadata-less PRs broke traceability during the v2.0 restructure | `protocols/github-workflow.md` |
| `S1.100` | C1 | No-AI-references rule across the GitHub metadata surface (commits, PRs, branches, co-authors, filenames); human attribution only | AI co-author + AI tool names found in `main` history; credibility requirement for an AI-governance product | `protocols/github-workflow.md` §2 |
| `S10.40` | C10 | Mode-based merge authority — solo auto-merge / team human-only review; AI never holds L4 merge authority on sensitive changes | Preserves the permanent human-only L4 boundary while enabling solo speed | `protocols/github-workflow.md` §6 |
| `S1.101` | C1 | Characterization tests pin current behaviour before any brownfield refactor | Refactoring untested legacy code is the primary way adoption breaks a working system | `protocols/brownfield-adoption.md` §2 |
| `S6.45` | C6 | Brownfield adoption is incremental and non-breaking — no big-bang rewrite; strangler-fig migration | Big-bang rewrites of running systems are the highest-risk failure mode in adoption | `protocols/brownfield-adoption.md` §2 |
| `S8.83` | C8 | Every brownfield conversion step is individually reversible with a ready rollback path | Non-breaking guarantee requires per-step reversibility | `protocols/brownfield-adoption.md` §2 |
| `S1.102` | C1 | Adoption is complete only when every applicable standard is satisfied or carries an approved exception | Prevents silent partial adoption that looks compliant but isn't | `protocols/brownfield-adoption.md` §1 |
| `S8.84` | C8 | Committed lockfile + CI vulnerability gate; SEV0/SEV1 dependency CVEs block merge | Supply-chain CVEs are a leading breach vector and are deterministically detectable | `protocols/external-governance.md` §2 |
| `S8.85` | C8 | Dependency license allowlist; SBOM generated for releases | License violations and opaque dependency trees are legal and security liabilities | `protocols/external-governance.md` §2 |
| `S2.81` | C2 | Every external call has timeout + bounded retry + circuit breaker + defined fallback | A system cannot be more reliable than the third parties it calls without isolation | `protocols/external-governance.md` §3 |
| `S3.37` | C3 | Integrations use least-privilege scopes; inbound webhooks verify signatures | Over-broad scopes and unverified webhooks are common integration breach paths | `protocols/external-governance.md` §4 |
| `S8.86` | C8 | Vendor register + exit/portability plan for every critical external vendor | Undocumented lock-in is an existential operational risk | `protocols/external-governance.md` §5 |
| `S8.87` | C8 | Continuous temporal governance of the external surface (CVEs, framework/version changes) | The external surface decays on its own; one-time checks rot | `protocols/external-governance.md` §6 |

---

*This log is the compliance evidence that Governova's standards are actively maintained
and that every change was reviewed and approved through the amendment protocol.*
