# Govtech Domain Constitution

| Attribute | Value |
|-----------|-------|
| **Document** | Govtech Domain Constitution |
| **Layer** | 4 — Domain Extension |
| **Extends** | Universal Core (C00–C10) |
| **Regulatory basis** | POPIA · GDPR-adjacent · public-sector procurement |
| **Contributed by** | Maluleke Kurhula Success |
| **Version** | v1.0 |
| **Status** | ACTIVE |
| **Applies To** | Any system delivering a public service or holding citizen records |

---

> *A citizen cannot choose a different government. Every assumption commercial software
> is allowed to make about its users — that they can switch, upgrade their device, afford
> the data, or simply not use it — is unavailable here. A public system that excludes
> is not a system with a usability problem; it is a service that was not delivered.*

---

## Domain overview

Government technology is distinguished from commercial software by three constraints that
have no equivalent elsewhere: the user cannot opt out, the state's record about a person
carries legal force, and the system's cost falls on the public whether or not it works.

The universal core already governs accessibility (`S4.19`, `S4.21`), performance budgets
(`S4.69`), authorisation (`S3.24`), and role-change audit (`S3.25`). `S9.5` already makes
African context a design constraint rather than a retrofit. What the core does not carry
is the *public-law* obligation on top: that a citizen may see and contest what the state
records about them, that a service must function on the device and connection the citizen
actually has, that residency of citizen data is a legal question and not an infrastructure
preference, and that a public system must remain operable and exportable when the vendor
that built it is gone.

Seeded from **Maphophe Community System** — a rural ward-services platform where the
primary device is a feature phone at 320px and the primary connection is intermittent,
and where these requirements were established as design constraints before the first line
of code rather than discovered at launch.

---

## Standards

### D-GOVTECH.1 — Citizen Data Residency Is Declared and Enforced

| Attribute       | Value |
|-----------------|-------|
| **ID**          | D-GOVTECH.1 |
| **Priority**    | Critical |
| **Applies To**  | All Stacks · every system holding citizen records |
| **Enforced By** | architecture review · deployment configuration review · ADR |

**Extends:**
`S8.27` (production secrets are stored in the platform, never in code), `S5.1` (database assignment is declared)

**Standard:**
The jurisdiction in which citizen personal data is stored, processed, and backed up is declared in an ADR before deployment, and enforced in the deployment configuration by explicit region pinning on every store that holds it — primary database, replicas, backups, object storage, caches, queues, and logs. Any transfer of citizen data across a jurisdictional boundary, including to a third-party processor or an AI provider, requires a recorded legal basis and appears in the system's vendor register. A default region chosen by a hosting provider is not a declaration.

**Rationale:**
Data-protection law binds the state to where a citizen's record physically lives, and the obligation follows the data into every copy of it. The failure is almost never the primary database — it is the backup bucket, the log aggregator, or the AI provider that quietly relocated the data outside the jurisdiction while the application remained compliant on paper. Region defaults are the mechanism: a provider's default is chosen for the provider's convenience, and inheriting it is a decision the system made without recording that it made one.

**Anti-Patterns:**
- `AP-D-GOVTECH.1a` — Citizen data in a store whose region was inherited from a provider default rather than pinned explicitly.
- `AP-D-GOVTECH.1b` — Backups, logs, or a third-party processor holding citizen data outside the declared jurisdiction with no recorded legal basis.

---

### D-GOVTECH.2 — A Public Service Works on the Device and Connection Citizens Have

| Attribute       | Value |
|-----------------|-------|
| **ID**          | D-GOVTECH.2 |
| **Priority**    | Critical |
| **Applies To**  | All Stacks · every citizen-facing interface |
| **Enforced By** | CI performance budget · accessibility audit · design review |

**Extends:**
`S9.5` (African context is a design constraint), `S4.69` (Lighthouse performance budget), `S4.21` (WCAG 2.1 AA colour contrast), `S4.19` (full keyboard accessibility)

**Standard:**
Every citizen-facing interface meets WCAG 2.1 AA and functions at the smallest viewport the service's population actually uses, on an intermittent connection. The service's minimum target device, viewport, and connection profile are declared in the system's CONSTITUTION-INDEX and enforced as a CI budget on page weight and interaction latency, not merely measured. Any function a citizen needs to complete a service request degrades to a working state without JavaScript, without a persistent connection, or without a modern browser — and a citizen who cannot use the digital channel has a declared non-digital route to the same service.

**Rationale:**
A public service excludes by omission. When the interface assumes a current handset, an unmetered connection, and full sight and dexterity, the citizens filtered out are precisely those with the greatest need of the service and the least ability to complain about it — so the exclusion never appears in the metrics. Declaring the minimum profile turns exclusion into a testable property; enforcing it as a budget stops it regressing quietly with the next dependency. The non-digital route matters because no accessibility target reaches everyone, and a service that is only digital is a service that has decided some citizens do not count.

**Anti-Patterns:**
- `AP-D-GOVTECH.2a` — A service request that cannot be completed without JavaScript, on a 320px viewport, or on an intermittent connection.
- `AP-D-GOVTECH.2b` — A performance or accessibility target recorded as an aspiration rather than enforced as a CI gate, or a system with no declared non-digital route.

---

### D-GOVTECH.3 — Citizens Can See, Correct, and Export the Record Held About Them

| Attribute       | Value |
|-----------------|-------|
| **ID**          | D-GOVTECH.3 |
| **Priority**    | Critical |
| **Applies To**  | All Stacks · every system holding citizen records |
| **Enforced By** | API contract review · E2E test · code review |

**Extends:**
`S3.25` (role change audit trail — immutable history), `S5.8` (soft delete, never hard delete)

**Standard:**
Every system holding citizen records exposes, to the citizen the record concerns: access to the record in a portable machine-readable format, the ability to request correction, and a visible record of what was corrected, when, and by whom. Correction never rewrites history — the prior value is retained per `S5.8` and the change is auditable. Requests are answered within the statutory period, and the system records the date each request was received and satisfied so that compliance is demonstrable rather than asserted.

**Rationale:**
An inaccurate state record is not an inconvenience; it decides whether a person receives a grant, a service, or a right. Access and correction are the only mechanisms by which an error in a public record can be found at all, because the state has no other incentive to look. Allowing correction to overwrite silently destroys the evidence a citizen needs in a dispute — the record would then show only the corrected value, with nothing to prove what the state acted on at the time. Recording the request dates is what converts the obligation from a policy statement into something an auditor can verify.

**Anti-Patterns:**
- `AP-D-GOVTECH.3a` — A citizen record with no citizen-accessible read or export path, or export available only in a proprietary format.
- `AP-D-GOVTECH.3b` — A correction that overwrites the prior value with no retained history of what changed and who changed it.

---

### D-GOVTECH.4 — Public Systems Remain Operable Without Their Vendor

| Attribute       | Value |
|-----------------|-------|
| **ID**          | D-GOVTECH.4 |
| **Priority**    | High |
| **Applies To**  | All Stacks · every publicly funded system |
| **Enforced By** | vendor register review · procurement gate · restore drill |

**Extends:**
`S8.86` (vendor register + exit plan for every critical vendor), `S8.85` (dependency license allowlist; SBOM generated for releases)

**Standard:**
Every publicly funded system maintains, as a condition of delivery: a complete SBOM, a vendor register naming every critical dependency with a documented exit path, source and data in repositories the commissioning authority controls, and a restore drill performed at least annually and recorded. No component whose licence prevents the authority from continuing to operate, audit, or hand over the system may be introduced. Where a proprietary or hosted component is unavoidable, its exit path is documented and rehearsed before it enters production.

**Rationale:**
Public systems outlive the contracts that build them, and the authority that must keep a service running is frequently not the party that wrote it. Lock-in is therefore a public-interest failure rather than a commercial inconvenience: a ward cannot procure a replacement for a system whose data it cannot extract, and a service outage caused by a lapsed vendor relationship falls on citizens who had no part in the procurement. A restore drill is included deliberately — an untested backup is an assumption, and the moment it is needed is the worst moment to discover it.

**Anti-Patterns:**
- `AP-D-GOVTECH.4a` — A critical dependency with no documented exit path, or a component under a licence that prevents the authority operating or handing over the system.
- `AP-D-GOVTECH.4b` — Source, data, or infrastructure control held solely by the vendor, or a backup that has never been restore-tested.

---

### D-GOVTECH.5 — Decisions Affecting a Citizen Are Attributable and Explainable

| Attribute       | Value |
|-----------------|-------|
| **ID**          | D-GOVTECH.5 |
| **Priority**    | Critical |
| **Applies To**  | All Stacks · every system deciding eligibility, allocation, or status |
| **Enforced By** | audit-log review · semantic tier · code review |

**Extends:**
`S8.31` (structured JSON logging), `S3.21` (roles as database enums), `S1.103` (logic lives in its layer)

**Standard:**
Every decision that grants, denies, prioritises, or changes a citizen's status records: the deciding identity — human or automated — the rule version applied, the inputs it was applied to, the outcome, and a plain-language reason the citizen can be given. Where a decision is automated, that fact is disclosed to the citizen, and a route to human review exists and is reachable. Decision rules live in the service layer where they can be versioned and tested, never embedded in an interface or a query.

**Rationale:**
Administrative decisions are challengeable by law, and a challenge is answerable only if the state can reconstruct why the decision was made — which requires knowing the rule as it stood at the time, not as it stands now. Undisclosed automation is the modern form of an unaccountable decision: a citizen cannot contest a refusal whose existence they cannot attribute. Requiring a plain-language reason at the point of decision, rather than reconstructing one later, is what prevents post-hoc rationalisation of an outcome nobody can now explain.

**Anti-Patterns:**
- `AP-D-GOVTECH.5a` — A citizen-affecting decision recorded as an outcome only, without the rule version, inputs, or deciding identity.
- `AP-D-GOVTECH.5b` — Automated decision-making not disclosed to the affected citizen, or with no reachable route to human review.

---

## Conflict analysis

| Core standard | Interaction | Resolved? |
|---------------|-------------|-----------|
| `S9.5` — African context is a design constraint | `D-GOVTECH.2` generalises it beyond the reference systems and makes the minimum profile a declared, CI-enforced property | Yes — strictly additive; `S9.5` continues to govern design intent |
| `S4.69` — Lighthouse performance budget ≥ 80 | `D-GOVTECH.2` requires the target be derived from the service's actual population and enforced as a gate | Yes — raises a floor; the `S4.69` minimum continues to apply to all systems |
| `S4.21` / `S4.19` — WCAG AA contrast, keyboard accessibility | `D-GOVTECH.2` adopts both as a public-service obligation and adds no-JavaScript degradation | Yes — additive; no core requirement is relaxed |
| `S5.8` — Soft delete, never hard delete | `D-GOVTECH.3` relies on it so a correction cannot destroy the prior value | Yes — `D-GOVTECH.3` is `S5.8` applied to citizen corrections |
| `S3.25` — Role change audit trail | `D-GOVTECH.3` extends the same immutability reasoning from roles to citizen record corrections | Yes — additive |
| `S8.31` — Structured JSON logging | `D-GOVTECH.5` adds mandatory decision fields for citizen-affecting decisions | Yes — additive; general logging remains governed by `S8.31` |
| `S8.86` — Vendor register + exit plan | `D-GOVTECH.4` makes it a procurement condition and adds the rehearsed restore drill | Yes — raises a floor |
| `S8.85` — Licence allowlist + SBOM | `D-GOVTECH.4` narrows the allowlist to licences permitting authority operation and handover | Yes — narrows *permitted licences*, which tightens rather than weakens `S8.85` |
| `S3.21` — Roles as database enums | `D-GOVTECH.5` depends on typed roles to attribute a decision to a role | Yes — no interaction beyond dependency |
| `S1.103` — Logic lives in its layer | `D-GOVTECH.5` requires decision rules in the service layer — `S1.103` applied to administrative decisions | Yes — a domain-specific instance |
| `S8.27` — Secrets stored in the platform | `D-GOVTECH.1` extends region discipline to every store, using the same "declare it, don't inherit it" reasoning | Yes — additive |

No core standard is weakened, narrowed in obligation, or overridden. Where `D-GOVTECH.4`
narrows the permitted licence set, it restricts what is allowed rather than relaxing what
is required.

---

| Version | Date | Change | Rationale |
|---------|------|--------|-----------|
| v1.0 | 2026-07-28 | Initial govtech domain extension — `D-GOVTECH.1`–`D-GOVTECH.5`. Seeded from Maphophe Community System. | ADR-005 workstream A — Layer 4 content for the govtech domain. |
