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

> Note: the six ratified C0 §8 amendments that pre-date this log's creation
> (S1.98, S4.83, S5.65, S10.37, S10.38, S10.39) are recorded in their respective
> constitution amendment logs and in the git history. The current live count is
> 600 standards against the 594 locked baseline.

---

## Pending Proposals (awaiting C0 §8 ratification — L4)

> Proposed standards are **not yet in force**. They are operational via their paired protocol
> until the Founder ratifies them per the amendment protocol.

| Proposed ID | Constitution | Proposed standard | Evidence | Paired protocol |
|-------------|--------------|-------------------|----------|-----------------|
| `S1.99` | C1 | Branch → Issue → PR → Merge workflow order; mandatory full issue/PR metadata (type, milestone, project, labels, assignee) | Untracked, metadata-less PRs broke traceability during the v2.0 restructure | `protocols/github-workflow.md` |
| `S1.100` | C1 | No-AI-references rule across the GitHub metadata surface (commits, PRs, branches, co-authors, filenames); human attribution only | AI co-author + AI tool names found in `main` history; credibility requirement for an AI-governance product | `protocols/github-workflow.md` §2 |
| `S10.40` | C10 | Mode-based merge authority — solo auto-merge / team human-only review; AI never holds L4 merge authority on sensitive changes | Preserves the permanent human-only L4 boundary while enabling solo speed | `protocols/github-workflow.md` §6 |
| `S1.101` | C1 | Characterization tests pin current behaviour before any brownfield refactor | Refactoring untested legacy code is the primary way adoption breaks a working system | `protocols/brownfield-adoption.md` §2 |
| `S6.45` | C6 | Brownfield adoption is incremental and non-breaking — no big-bang rewrite; strangler-fig migration | Big-bang rewrites of running systems are the highest-risk failure mode in adoption | `protocols/brownfield-adoption.md` §2 |
| `S8.83` | C8 | Every brownfield conversion step is individually reversible with a ready rollback path | Non-breaking guarantee requires per-step reversibility | `protocols/brownfield-adoption.md` §2 |
| `S1.102` | C1 | Adoption is complete only when every applicable standard is satisfied or carries an approved exception | Prevents silent partial adoption that looks compliant but isn't | `protocols/brownfield-adoption.md` §1 |

---

*This log is the compliance evidence that Governova's standards are actively maintained
and that every change was reviewed and approved through the amendment protocol.*
