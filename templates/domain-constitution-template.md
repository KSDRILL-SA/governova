# {Domain Name} Domain Constitution

| Attribute | Value |
|-----------|-------|
| **Document** | {Domain} Domain Constitution |
| **Layer** | 4 — Domain Extension |
| **Extends** | Universal Core (C00–C10) |
| **Regulatory basis** | {regulations this domain encodes} |
| **Contributed by** | {author} |
| **Version** | v1.0 |
| **Status** | DRAFT |
| **Applies To** | {which systems this domain governs} |

---

> *{Opening principle for this domain — what this industry demands that general
> software does not.}*

---

## Domain overview

{What this domain covers, which core standards already apply, and what those
standards do **not** cover that this industry requires. A domain exists to add
to the core, never to restate it.}

---

## Standards

> Domain standards use the same block shape as core standards. `{DOMAIN}` is the
> upper-case identifier registered in `constitution/domains/README.md`, and the
> domain must be present in `DOMAIN_REGISTRY` (`scripts/governova_compile/discovery.py`)
> before its standards will compile. See `framework/format-specification.md`.

### D-{DOMAIN}.1 — {Standard title, stated positively}

| Attribute       | Value |
|-----------------|-------|
| **ID**          | D-{DOMAIN}.1 |
| **Priority**    | Critical \| High \| Standard |
| **Applies To**  | {all systems in domain \| specific stack} |
| **Enforced By** | {review · CI · reliable-tier rules · semantic tier} |

**Extends:**
`S{C}.{N}` ({why this core standard is the anchor}), `S{C}.{N}` ({…})

**Standard:**
{The requirement. State what must be true, not what must not happen.}

**Rationale:**
{Why the universal core alone is insufficient here — the production or regulatory
consequence specific to this industry.}

**Anti-Patterns:**
- `AP-D-{DOMAIN}.1a` — {What the failure looks like in real code.}
- `AP-D-{DOMAIN}.1b` — {A second, distinct failure mode.}

---

{Repeat for each standard. Numbering is sequential with no gaps, and IDs are
permanent once published — see `framework/format-specification.md`.}

---

## Conflict analysis

Every core standard this domain interacts with, and the resolution. **Mandatory** —
a domain that has not been conflict-checked against the core cannot be ratified.

| Core standard | Interaction | Resolved? |
|---------------|-------------|-----------|
| `S{C}.{N}` | {how they interact} | Yes — {resolution} |

A domain may **raise** a floor the core sets; it may never lower, narrow, or override
one. If an apparent conflict cannot be resolved as additive, it is escalated under
`framework/conflict-resolution.md` rather than resolved in this document.

---

| Version | Date | Change | Rationale |
|---------|------|--------|-----------|
| v1.0 | {YYYY-MM-DD} | Initial {domain} domain extension — `D-{DOMAIN}.1`–`D-{DOMAIN}.{N}`. | {why now} |
