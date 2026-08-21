# The Cloud schema, and what analysing it found

`#255` asks for one thing before any of this is built on:

> **Run `governova schema` on our own Prisma schema before writing the migrations.** That command
> analyses data-model soundness against C14 and has never had a real customer. This is its first.
> A data-model analyser whose author did not run it on their own schema is a recommendation
> nobody should take.

It was run first. It found a defect in itself.

---

## What the first run reported

```
schemas=1 tables=5 certain=0 probable=1
  probable fan-trap TeamMembership — TeamMembership is the one side of 2 separate
  one-to-many relationships (Membership, Team)
```

That reads wrong on inspection. `TeamMembership` is the **many** side of both — many team
memberships per team, many per membership. It is a bridge entity, which is the structure `S14.9`
*requires* for a many-to-many.

And the genuine fan trap in this schema — `Organisation`, which is the one side of both
`Membership` and `Team` — was not reported at all.

## The cause

`Relation.source_to_many` meant **opposite things in the two parsers**.

| | what it set `source_to_many` from | reading |
|---|---|---|
| SQL | `not (column.unique or primary_key)` on the foreign key | "this end is the many end" |
| Prisma | whether that side declares a list | "this end has many of the other" |

Those are the two ends of the same relationship. Every check that consults cardinality was
therefore correct in one dialect and inverted in the other.

**Only the many-to-many check was unaffected**, because it reads both flags and is symmetric —
which is why the disagreement survived. The SQL fixtures passed throughout, and nothing compared
the two dialects against the same model.

`check_fan_trap` also handled only one of the two orientations. `source` and `target` are named
*alphabetically* by the Prisma parser so a relation declared from both ends pairs up, so either
end can be the many one — half of every Prisma schema's relations were skipped outright.

## What was done

- The Prisma parser now reads the **other** side's declaration, so `X_to_many` means X is the
  many end in both dialects.
- `Relation`'s docstring states that meaning explicitly. The ambiguity is what allowed this.
- `check_fan_trap` handles both orientations, and takes the parent to be the end that is *not*
  to-many.
- Four regression tests, the load-bearing one being
  `test_the_same_model_gets_the_same_verdict_in_both_dialects` — the same logical schema written
  as Prisma and as SQL DDL must produce the same finding. Nothing compared them before.

**Every rule the analyser ships was correct about SQL and wrong about Prisma, and it took
pointing it at a real Prisma schema to find out.** That is the whole argument for `#255`'s
instruction.

---

---

## The finding that survives, and how it is resolved

```
probable fan-trap Organisation — Organisation is the one side of 2 separate
one-to-many relationships (Membership, Team)
```

**This one is real, and the arithmetic is in a test.** An organisation with 10 members and 4
teams returns **40 rows** from a join through it — `test_the_fanning_join_really_does_fan`
builds exactly that and asserts the 40. Any `COUNT` or `SUM` over it is wrong, and wrong
quietly: the query succeeds and returns a number.

`S14.10` allows *resolved or documented*. The shape cannot be removed — an organisation
genuinely has both members and teams — so it is resolved where a fan trap actually can be:
**nothing has to write that join.**

Every question somebody would reach for it to answer is answered by a path that does not fan:

| question | path | fans |
|---|---|---|
| who is in this organisation | `members_of` | no |
| what teams does it have | `teams_of` | no |
| who is on this team | `Team → TeamMembership → Membership`, via `members_of_team` | no |

Reaching team members through `Organisation` does not merely multiply rows — it returns every
member of the *organisation* rather than every member of the *team*, which is a different and
wrong answer. That is asserted too.

Documenting the trap would have left the next person to read the note. This makes it
unreachable through the API they will actually use.

## The second gap, closed in the schema

`TeamMembership` reaches an organisation by two paths — through its team and through its
membership — and nothing stopped a team in organisation A from holding a member of
organisation B.

**It is now impossible.** `TeamMembership` carries `organisation_id`, and both foreign keys are
composite on `(organisation_id, id)` **sharing that one column**:

```prisma
team       Team       @relation(fields: [organisation_id, team_id],       references: [organisation_id, id])
membership Membership @relation(fields: [organisation_id, membership_id], references: [organisation_id, id])
```

A row cannot name two different organisations in one column, so the two references cannot
disagree.

**This was first written as an application check, and that was wrong.** An application
invariant holds only for code that calls it. A migration, a bulk import, a support script and a
direct `INSERT` all bypass it, and every one of those is an ordinary thing to do to a
production database. The cost of the real fix is one column and two composite unique
constraints — considerably less than the cost of finding out later that it did not hold.

`S14.8` requires a denormalisation to be **recorded, never assumed**. `organisation_id` on
`TeamMembership` is one: it duplicates a fact reachable through either parent. It is recorded
here and in the schema, and it exists for a reason the schema states — one shared column is what
makes the keys composite.

`test_the_schema_keys_team_membership_on_the_organisation` reads the schema file itself, so if
somebody simplifies these back to single-column references the invariant does not silently stop
being enforced.

## What the analyser declines to answer

```
unanswered: third normal form — a schema does not declare functional dependencies,
and guessing them would discredit the rest.
```

That is the tier's founding rule showing up: a check that cannot determine an answer says so,
rather than guessing. Third normal form is a claim about which attributes determine which, and
a DDL does not carry that. Reviewing it stays a human job.

---

## Re-running it

```
governova schema platform/cloud/prisma/schema.prisma
```

`--strict` exits non-zero on certain findings. It is not in CI yet: the schema is not wired to
a database, so there is nothing to drift from. That belongs with the migrations.
