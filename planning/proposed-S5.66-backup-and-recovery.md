# PROPOSED — `S5.66` Backup and Recovery

> **This is a proposal, not law.** It lives in `planning/` deliberately: the compiler reads
> `constitution/`, `governance/runbooks` and `governance/decisions`, so nothing here is in the
> corpus, the standard count stays at 670, and no coverage denominator moves.
>
> **Ratifying it means three things**, in this order: paste the standard below into
> `constitution/core/phase-1-core-architecture/C05-database-constitution.md` after `S5.65`, add
> its anti-patterns to that file's index, and append a row to
> `governance/changelog/amendments-log.md` with **Maluleke Kurhula Success** in the *Approved by*
> column. Then `governova-compile` and commit.
>
> It is written in C05's exact format so ratification is a paste rather than a rewrite.

---

## Why this is being proposed

`C05` governs 35 standards about databases. **Not one of them is "the data still exists
tomorrow."** Searching the whole constitution for a recovery standard returns `S1.93`–`S1.97`,
which are all about recovering a *git* mistake, and one incidental mention of "restore" inside
`AP-S5.64a`.

The gap is sharpest where the stakes are highest. `S5.65` makes ledger tables immutable and
`ADR-016` implements that with a grant and a trigger; `governova_ledger` hash-links every entry so
that an edit is detectable. Every one of those guarantees concerns **detecting a change to a
row**. None concerns the row existing.

**A hash chain proves tampering. It does not survive a dropped table.** For financial records
that is half the problem solved, and the missing half is the one that ends a company.

`Ch09 — Database Design` names the three levels this proposal requires, and it places integrity
and recovery inside physical design rather than treating them as operations that happen later.

---

## The standard, as it would appear in C05

### S5.66 — Data Survives Its Own Loss — Backups Are Tiered, Timed, and Rehearsed

| Attribute       | Value |
|-----------------|-------|
| **ID**          | S5.66 |
| **Priority**    | Critical |
| **Applies To**  | Both Stacks · every system of record |
| **Phase**       | Phase 1 — Core Architecture |
| **Depends On**  | `S5.2` (PostgreSQL is the system of record), `S5.65` (ledger tables are immutable), `S8.61` (runbook directory) |
| **Enforced By** | Probe — the backup configuration and the recorded restore rehearsal are repository facts; the rehearsal date is checkable |

**Standard:**
Every system of record declares three things and proves the third. **A tiered backup**: a periodic
full backup, a differential or incremental backup between fulls, and continuous transaction-log
archiving sufficient for point-in-time recovery. **A stated recovery point objective and recovery
time objective**, written as numbers rather than intentions — the maximum data loss tolerated and
the maximum time to restore service. **A rehearsal**: a restore performed into a scratch
environment, on a stated cadence, whose date and outcome are recorded in the repository. A
restore that has never been performed is not a recovery capability; it is an assumption. Where a
managed provider supplies backups, the provider's guarantees are recorded against these three
requirements and the rehearsal is still performed, because the failure being guarded against
includes deleting the account that holds the backups.

**Rationale:**
Immutability, hashing and audit trails all answer *did this record change?* None answers *does
this record exist?* — and the second question is the one asked after a dropped table, a failed
migration, a ransomware event, or a mistaken `DROP SCHEMA` in a console someone believed was
staging. The three levels are not redundancy for its own sake: a full backup bounds how far back
recovery starts, a differential bounds how much must be replayed, and transaction-log archiving
is what makes recovery to a *point in time* possible rather than to whenever the last backup ran.
Stating RPO and RTO as numbers converts an argument about whether the backup is good enough into
a measurement. The rehearsal is the load-bearing clause: an unrehearsed backup fails in the ways
nobody anticipated — wrong version, missing extension, an encryption key held only by the person
who left, a dump that completes and restores empty. Every one of those is discovered either in a
rehearsal or in an incident.

**Anti-Patterns:**
- `AP-S5.66a` — A system of record with no backup configuration in the repository — the recovery
  plan exists only in whatever a provider's defaults happen to be, and nobody has read them.
- `AP-S5.66b` — Backups configured with no stated RPO or RTO — "we have backups" is not a
  recovery objective, and the question of whether an hour of loss is acceptable gets answered
  during the hour.
- `AP-S5.66c` — A backup that has never been restored — an assumption wearing the costume of a
  capability, and the discovery that it fails is scheduled for the worst possible moment.
- `AP-S5.66d` — Backups stored only in the account that holds the primary — one credential
  compromise, one billing lapse, or one mistaken account deletion removes both the data and its
  recovery.

**Cross-References:** `S5.2` (system of record), `S5.59` (migration-first deploy), `S5.65` (ledger
immutability — the guarantee this one complements), `S8.61` (runbooks — where the restore
procedure lives), `ADR-016` (the audit that found this gap).

---

## Anti-pattern index rows

| ID | Description | Violated Standard | Severity |
|----|-------------|-------------------|----------|
| `AP-S5.66a` | No backup configuration in the repository | S5.66 | Critical |
| `AP-S5.66b` | Backups with no stated RPO or RTO | S5.66 | High |
| `AP-S5.66c` | A backup that has never been restored | S5.66 | Critical |
| `AP-S5.66d` | Backups held only in the account that holds the primary | S5.66 | High |

---

## What ratifying it would cost us immediately

**This standard fails against Governova itself on day one**, and that is the point of proposing
it rather than quietly not having it.

| Requirement | Governova Cloud today |
|---|---|
| tiered backup | none — there is no deployment yet |
| RPO / RTO stated | none |
| rehearsal recorded | none |

That is honest and survivable: the Cloud has no deployment and therefore no data to lose. The
standard would bind at the moment Stage 2 stores a payment, which is exactly when it should.

**It is enforceable by a probe**, not only by review — the presence of a backup configuration, a
stated RPO/RTO, and a dated rehearsal record are all repository facts. That matters, because a
Critical standard nothing can check is a standard that decays into a sentence people agree with.

---

## Why I have not ratified this myself

Every other document in this batch was ratified on the owner's delegation. This one is different
in kind: ADR-014 and ADR-015 recorded decisions already made and drafted; this **writes new law
that binds every KSDRILL system**, including three that already exist.

And in this same batch I misread `S5.65` — proposing a grant while the standard already required a
grant *and* a trigger, and listing the trigger as an alternative I had declined. That was caught
before it landed. It is a live demonstration that I can be confident and wrong about a standard's
intent, which is the argument for a human reading this one before it binds anything.

**Ratify by merging the three changes at the top of this file. Reject by deleting it.**
