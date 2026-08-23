# ADR-016 — The Cloud data model: five decisions, and the numbers that reopen three of them

| | |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-08-23 |
| **Authority** | L4 — `C0 §8`. Completes `S14.13`'s three design stages for Stage 1, and settles what Stage 2 builds on. Ratified on the owner's explicit delegation, not by the owner reading it |
| **Supersedes** | Nothing. Records decisions `ADR-010` and `planning/phase-4-cloud.md` left open |
| **Relates To** | `S5.6`, `S5.14`, `S5.59`, `S5.65`, `S14.7`, `S14.8`, `S14.10`, `S14.13`, `ADR-010 §4`, `ADR-015` |

---

## Context

`S14.13` requires a data model to pass three stages — conceptual, then logical, then physical —
each completed before the next begins, because *"starting at physical design produces entities
shaped by what was convenient to index, and that shape then outlives the engine that suggested
it."*

Stage 1's six tables were built without that sequence. They are good tables — every foreign key
indexed, uniqueness in the database rather than in application code, one denormalisation bought
deliberately and documented at length. But the stages were collapsed, and the audit that followed
found four defects in a schema nobody had walked through.

Two were found by executing the SQL for the first time (`#351`, `#355`). One was found by reading
it against `S5.14` (`#356`). One was found by re-running the schema analyser and noticing its
output had changed since the note describing it was written.

**The audit also found what the constitution does not cover.** Checked against `Ch09 — Database
Design` from the source course, physical design has three steps and this repository had
addressed one and a half. The missing ones are not small.

This ADR records the five decisions Stage 2 cannot be built without, and the three gaps that
belong to the constitution rather than to any schema.

---

## Decision

### 1 · Accrual materialises lazily, not hourly

`ADR-010 §4` fixes hourly accrual. Read literally — one `LedgerEntry` per hour per organisation —
the arithmetic does not survive the product succeeding:

| Organisations | Entries per year | Storage per year |
|---|---|---|
| 100 | 876,000 | ~0.2 GB |
| 1,000 | 8,760,000 | ~2.2 GB |
| 10,000 | **87,600,000** | ~21.9 GB |

Each row records an accrual of `1.111111` credits on the Pro tier, hashed and chained, in an
append-only table that can never be compacted.

**Accrual is stored as a rate and a last-accrued instant, and materialises one entry covering the
elapsed hours when credit is next consumed.** Every *balance change* remains an entry in the
chain; what stops existing is an entry per hour in which nothing happened.

`ADR-010 §4`'s guarantee is untouched — credits still accrue rather than resetting, and a
subscriber who works in bursts is still not punished for the shape of their week. What changes is
how many rows say so.

`accrue()` already keys idempotency on the hour, which is exactly what makes a lazy catch-up safe
to run twice.

### 2 · The balance is not checkpointed, and here is the condition that changes that

`Ledger.balance()` sums every entry. A checkpoint — a stored balance at a sequence number, with
the sum taken only over later entries — is a **cache**, and `governova_ledger` is explicit that
if a projection and its entries can disagree it must be labelled one.

A SQL `SUM` with a `CASE` over direction is also a second implementation of `_DIRECTION`, which is
the "storage layer acquires a second opinion about what a balance is" failure the module exists
to prevent.

**Not done, and reopened by a measured slow balance** — not by an estimate. When it is done, it
is pinned by a test that computes both ways over the same entries and asserts they agree, in the
shape `test_hosted.py` already uses for the hosted Score.

### 3 · `LedgerEntry` is not partitioned, and the trigger is 50 million rows

It is the only table that grows without bound and the only one that can never be compacted. Two
candidates, both defensible:

- **by organisation** — matches every access path, since every query filters `organisation_id`
  first; uneven, because one large customer makes one large partition.
- **by time** — even growth, old partitions become read-only, which suits an append-only table;
  cuts across the chain, so verifying one organisation touches every partition.

Choosing before there is a row count is physical design driving the model. **The decision is
deferred and the trigger is recorded: 50 million rows in `LedgerEntry`.**

### 4 · Migrations run before the service starts

`S5.59` requires it and the runner already exists — each migration applies inside a transaction
with the row recording it, so a database cannot run the SQL without knowing it did.

What does not exist is the deployment step that calls it. **A release job runs the migrator and
fails the deploy on error, before any process serves a request.** PostgreSQL runs DDL
transactionally, so the risk being managed is not a half-applied schema; it is a service booting
against a schema it does not expect.

### 5 · The ledger is immutable at the grant layer **and** at a trigger

This turned out not to be a decision at all. `S5.65` already requires it, in terms:

> The application role holds `INSERT` and `SELECT` only; `UPDATE` and `DELETE` are revoked at the
> grant layer **and additionally blocked by a trigger**.

Today Stage 1 has neither. Immutability is enforced by a docstring, which is a preference rather
than a property, and the difference appears exactly once — in the incident where it mattered.

**Both are implemented, as written.** An earlier draft of this ADR proposed the grant alone and
rejected the trigger on the grounds that it would also block a migration legitimately rewriting
the table. `S5.65` answers that directly and is right: under this standard there *is* no
legitimate rewrite, because a wrong entry is corrected by a reversing entry that references it.
The grant stops the application; the trigger stops every path the grant misses, including a
mistaken superuser session.

Recorded here because the draft nearly shipped a Critical standard's requirement as an
alternative it had considered and declined.

---

## The three gaps that belong to the constitution

These are not schema decisions. They are things `C05` does not require of any database.

### A · Nothing requires a backup

`C05` governs 35 things about databases and not one of them is *the data still exists tomorrow*.
Searching for a recovery standard returns `S1.93`–`S1.97`, which are all about recovering a **git**
mistake.

**A hash chain proves tampering. It does not survive a dropped table.** Every guarantee in the
ledger concerns detecting a change to a row; none concerns the row existing. For financial records
that is half the problem solved, and the missing half is the one that ends a company.

`Ch09` names three levels — full, differential, and transaction log. A standard requiring them,
with a stated recovery point and recovery time, is proposed separately and is an amendment rather
than an ADR.

### B · There is no performance requirement to measure against

`Ch09`'s third step of physical design is that *"the actual performance of the physical database
implementation must be measured and assessed for compliance with user performance requirements."*

There are none. The repository declares eight requirements, all behavioural. So *is this fast
enough* has no answer that is not an opinion — and `#356`, where every write read the entire
ledger, would have been a failing test rather than something noticed while reading SQL.

### C · The model is not traced to requirements

`REQ-005` anchors the ledger well: *the audit trail shall link each record to its predecessor with
a hash that detects any later edit.* Nothing anchors organisations, memberships, teams or seats.

Each Stage 2 entity names the requirement it serves. An entity nobody can trace to a requirement
is one nobody can justify keeping, and `governova trace` already checks that in both directions.

---

## Consequences

### What becomes easier

- **Stage 2 starts from settled ground.** The accrual shape decides the entity set, and it is
  decided.
- **Three deferrals have numbers rather than intentions.** A trigger of 50 million rows is
  checkable; "when it gets slow" is not.
- **The ledger becomes immutable in fact.** Decision 5 costs one `GRANT`.

### What becomes harder

- **Lazy accrual is more code than a cron job.** The rate and the last-accrued instant are state
  that must be correct, and a catch-up spanning a tier change has to decide which rate applied
  when — which is the mid-period tier change question `ADR-014` did not settle either.
- **Deferring partitioning means someone must watch the row count.** A trigger nobody measures is
  a trigger that never fires.

### Constitutional alignment

- `S14.13` — the three stages are completed and recorded for the first time.
- `S14.7` / `S14.8` — third normal form was answered by hand, because `governova schema` correctly
  declines to guess functional dependencies. Four of six tables are in 3NF; the two that are not
  break it deliberately, and **both are now recorded** — `TeamMembership.organisation_id` already
  was, and `LedgerEntry.record_hash` was not until this change.
- `S14.10` — the fan trap spans three relationships since Stage 1, not the two the note described.
  The balance path does not join, and a test asserts the absence.
- `S5.14` — the write path is bounded. `load()` stays unbounded and says why: a chain cannot be
  verified from part of itself.
- `S5.65` — Decision 5 implements it rather than deciding it. The standard already specified
  the grant *and* the trigger; Stage 1 shipped neither, and an earlier draft of this ADR would
  have shipped one.

---

## Alternatives Considered

| Option | Why rejected |
|---|---|
| **One `LedgerEntry` per hour, as written** | Simplest, and the only shape where the chain literally contains every hour. 87.6 million rows a year at 10,000 customers, permanently, to record that nothing happened. |
| **One entry per billing window, balance as a function of time** | Fewest rows. The balance stops being a sum over entries, which costs the property that makes the ledger checkable by anyone holding the rows. |
| **Partition now, by organisation** | Matches the access path and would probably be right. Rejected on sequencing: choosing a physical strategy before a row count exists is precisely what `S14.13` forbids, and the cost of deciding later is one migration. |
| **Enforce ledger immutability with a grant alone, no trigger** | What an earlier draft of this ADR proposed, on the grounds that a trigger blocks a legitimate rewrite. `S5.65` requires both and answers the objection: under it there is no legitimate rewrite, because corrections are reversing entries. Rejected in favour of following the standard. |

---

## Approved Deviations

| Standard | Deviation | Approved alternative |
|---|---|---|
| `S14.7` — third normal form is the default | `LedgerEntry.record_hash` and `prev_hash` are stored derived values | Recorded under `S14.8` in the schema. A hash computed on read is computed from whatever the row now says and therefore always matches; storing it is the mechanism by which an edit becomes detectable. |
| `ADR-010 §4` — credits accrue hourly | Accrual materialises on consumption rather than each hour | The guarantee is that credits accrue rather than reset. That is unchanged; only the row count is. |

---

> **Status: ACCEPTED — 2026-08-23**
>
> L4 — `C0 §8`. Ratified on the owner's explicit delegation (*"i approve all you have recommended
> and planned"*), recorded here rather than implied: the owner did not read and sign this
> document. Reversible by the owner at any time.
>
> **Gap A is the one to act on first.** Everything else here makes the model better; a missing
> backup makes the rest of it irrelevant.
