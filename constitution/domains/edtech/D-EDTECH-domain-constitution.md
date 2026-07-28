# Edtech Domain Constitution

| Attribute | Value |
|-----------|-------|
| **Document** | Edtech Domain Constitution |
| **Layer** | 4 — Domain Extension |
| **Extends** | Universal Core (C00–C10) |
| **Regulatory basis** | FERPA · COPPA · POPIA (children's data) |
| **Contributed by** | Maluleke Kurhula Success |
| **Version** | v1.0 |
| **Status** | ACTIVE |
| **Applies To** | Any system holding learner records or serving users under the age of majority |

---

> *A learner is frequently a minor, usually cannot consent for themselves, and never
> chose the institution that holds their record. Everything a commercial platform is
> permitted to do with a user's data — profile them, retain indefinitely, monetise
> attention, experiment on them — is either restricted or prohibited here.*

---

## Domain overview

Education technology holds records about people who, in law, cannot consent to their own
data being processed, and whose records determine access to funding, progression, and
employment for decades afterwards.

The universal core already governs least-privilege access (`S3.24`), immutable role
history (`S3.25`), soft delete (`S5.8`), and audit logging (`S8.31`). It does not carry
the obligations specific to minors and to educational records: that consent may need to
come from a guardian rather than the user, that an education record has a defined
disclosure boundary the platform may not cross, that attention and engagement are not
legitimate optimisation targets when the user is a child, and that a learner's record
must remain intelligible and portable after they leave the institution.

Seeded from **FundsLink Academy** — a student-funding platform where applicants are
routinely minors, where the record determines whether a person receives funding, and
where a disclosure error is not a privacy incident but a change in someone's life
outcome.

---

## Standards

### D-EDTECH.1 — Age Is Determined Before Processing, and Consent Follows From It

| Attribute       | Value |
|-----------------|-------|
| **ID**          | D-EDTECH.1 |
| **Priority**    | Critical |
| **Applies To**  | All Stacks · every system that may serve users under the age of majority |
| **Enforced By** | registration-flow review · E2E test · code review |

**Extends:**
`S3.24` (least privilege default — minimum role on account creation), `S2.25` (validation applied at every boundary)

**Standard:**
A system that may serve minors determines the user's age category before any personal data beyond that determination is processed, and records the basis of the determination. Where the user is below the applicable age of consent, processing proceeds only on verifiable guardian consent, which is recorded with its scope, the identity that granted it, and the date. Consent is revocable, and revocation is honoured across every downstream processor. A date-of-birth field collected after the account already holds personal data does not satisfy this standard.

**Rationale:**
Consent obtained from someone who cannot legally give it is not consent, so every processing activity that follows it is unlawful regardless of how carefully it is performed. Ordering matters more than intent: a registration flow that collects a name, an email, and a school before asking for a birth date has already processed a minor's data without a lawful basis, and no later correction can undo that. Recording the scope of guardian consent is what makes revocation actionable — a consent record that says only "yes" cannot tell the system what to stop doing.

**Anti-Patterns:**
- `AP-D-EDTECH.1a` — Personal data collected before the user's age category is determined, or an age check performed only in the client.
- `AP-D-EDTECH.1b` — Guardian consent recorded as a boolean with no scope, granting identity, or date — or revocation that does not propagate to downstream processors.

---

### D-EDTECH.2 — Education Records Have a Declared Disclosure Boundary

| Attribute       | Value |
|-----------------|-------|
| **ID**          | D-EDTECH.2 |
| **Priority**    | Critical |
| **Applies To**  | All Stacks · every system holding learner records |
| **Enforced By** | authorisation review · access-control tests · audit-log review |

**Extends:**
`S3.24` (least privilege default), `S3.21` (roles as database enums), `S8.31` (structured JSON logging)

**Standard:**
Every category of learner record declares who may see it — the learner, a consented guardian, named institutional roles, and no one else — and that boundary is enforced server-side on every read path, including exports, reports, aggregate views, and support tooling. Every disclosure to a party other than the learner is logged with the recipient, the legal or consented basis, and the fields disclosed. Aggregate and anonymised outputs are checked for re-identification against small cohorts before release; a class of four is not anonymous.

**Rationale:**
Educational records follow a person for life and are routinely requested by parties with no right to them — employers, relatives, other institutions, and internal staff acting outside their role. The dominant failure is not a breach but ordinary over-disclosure through paths nobody classified as disclosure: a support tool that shows everything, a CSV export with unfiltered columns, or a dashboard that reveals an individual because the cohort was too small to hide them. Logging the basis for each disclosure is what makes an improper one findable, since the disclosure itself will otherwise look identical to a legitimate read.

**Anti-Patterns:**
- `AP-D-EDTECH.2a` — A learner record reachable through an export, report, or support tool that bypasses the declared disclosure boundary.
- `AP-D-EDTECH.2b` — An aggregate or "anonymised" output released without a small-cohort re-identification check.

---

### D-EDTECH.3 — Learner Data Is Not Monetised or Used to Optimise Engagement

| Attribute       | Value |
|-----------------|-------|
| **ID**          | D-EDTECH.3 |
| **Priority**    | Critical |
| **Applies To**  | All Stacks · every system serving learners |
| **Enforced By** | design review · vendor register review · semantic tier |

**Extends:**
`S9.1` (every platform solves a real problem felt by real people), `S9.7` (five gate questions every feature must pass), `S8.86` (vendor register + exit plan)

**Standard:**
Learner personal data is not sold, shared for advertising, or used to train models outside the educational purpose it was collected for. No feature optimises for engagement, session length, streak maintenance, or notification response as a goal in itself; features are justified by learning or access outcomes, and the justification is recorded at the gate. Every third party receiving learner data appears in the vendor register with its purpose and its data-handling terms, and behavioural advertising or profiling identifiers are absent from learner-facing surfaces.

**Rationale:**
Engagement optimisation and education diverge: the most engaging product keeps a learner returning, while the best educational product gets them to competence and lets them leave. When the user is a minor, that divergence stops being a product-strategy question — techniques that are merely persuasive for an adult are exploitative against a developing capacity for self-regulation, and the platform holds the record that makes the targeting effective. Third-party analytics is the usual route by which this happens without a decision ever being made, which is why the vendor register is the enforcement point rather than a policy statement.

**Anti-Patterns:**
- `AP-D-EDTECH.3a` — Learner data shared with an advertising, profiling, or model-training recipient outside the declared educational purpose.
- `AP-D-EDTECH.3b` — A feature whose recorded justification is engagement, streaks, or session length rather than a learning or access outcome.

---

### D-EDTECH.4 — A Learner's Record Outlives the Platform and Travels With Them

| Attribute       | Value |
|-----------------|-------|
| **ID**          | D-EDTECH.4 |
| **Priority**    | High |
| **Applies To**  | All Stacks · every system holding learner records |
| **Enforced By** | export contract review · retention policy · restore drill |

**Extends:**
`S5.8` (soft delete, never hard delete), `S8.86` (vendor register + exit plan), `S8.87` (continuous temporal governance of the external surface)

**Standard:**
A learner can export their complete record — enrolments, submissions, results, awards, and applications — in a documented, machine-readable format that remains intelligible without the platform that produced it. Retention periods are declared per record category and enforced by an automated process, distinguishing records with a statutory retention obligation from those a learner may have deleted. Deletion of a learner account never silently destroys a record the institution is legally required to retain, and never retains one it is required to delete.

**Rationale:**
A learner's record is the evidence of what they achieved, and it must survive the institution's choice of supplier, since the learner had no part in that choice. Export formats that are technically machine-readable but semantically opaque — a database dump, an undocumented JSON blob — satisfy the letter of portability while defeating it entirely, because no receiving institution can interpret them. The two-sided retention requirement is deliberate: over-retention and premature deletion are both failures, and a system that only implements one of them will reliably commit the other.

**Anti-Patterns:**
- `AP-D-EDTECH.4a` — Learner export available only as an undocumented dump, a rendered document, or a proprietary format.
- `AP-D-EDTECH.4b` — Retention applied uniformly across record categories, so statutory records are destroyed or deleted records are retained.

---

## Conflict analysis

| Core standard | Interaction | Resolved? |
|---------------|-------------|-----------|
| `S3.24` — Least privilege default | `D-EDTECH.1` and `D-EDTECH.2` apply it to age determination and disclosure boundaries | Yes — additive; the core default continues to govern account creation |
| `S3.21` — Roles as database enums | `D-EDTECH.2` relies on typed institutional roles to express a disclosure boundary | Yes — dependency only |
| `S2.25` — Validation at every boundary | `D-EDTECH.1` requires age determination to be one of those boundary validations, server-side | Yes — a domain-specific instance |
| `S5.8` — Soft delete, never hard delete | `D-EDTECH.4` requires category-specific retention, including genuine deletion where law requires it | Yes — `S5.8` governs application deletes; `D-EDTECH.4` adds a lawful, audited erasure path above it, and does not permit ad-hoc hard deletion |
| `S8.31` — Structured JSON logging | `D-EDTECH.2` adds mandatory disclosure fields | Yes — additive |
| `S8.86` — Vendor register + exit plan | `D-EDTECH.3` and `D-EDTECH.4` make it the enforcement point for third-party learner-data recipients | Yes — additive |
| `S8.87` — Temporal governance of the external surface | `D-EDTECH.4` extends periodic review to retention obligations, which change with law | Yes — additive |
| `S9.1` — Every platform solves a real problem | `D-EDTECH.3` narrows legitimate feature justification for learner-facing features | Yes — narrows *acceptable justifications*, tightening rather than relaxing `S9.1` |
| `S9.7` — Five gate questions | `D-EDTECH.3` adds a further gate condition for learner-facing features | Yes — raises a floor |

One interaction required explicit resolution: `S5.8` prohibits hard deletion, while data-protection
law grants a right to erasure. Resolved as stated in `D-EDTECH.4` — erasure is a declared,
audited, category-specific process with a recorded legal basis, not a bypass of `S5.8`. All
other standards are strictly additive.

---

| Version | Date | Change | Rationale |
|---------|------|--------|-----------|
| v1.0 | 2026-07-28 | Initial edtech domain extension — `D-EDTECH.1`–`D-EDTECH.4`. Seeded from FundsLink Academy. | ADR-005 workstream A — Layer 4 content for the edtech domain. |
