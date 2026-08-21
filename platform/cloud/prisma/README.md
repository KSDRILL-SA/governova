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

## The finding that survives, and what is done about it

```
probable fan-trap Organisation — Organisation is the one side of 2 separate
one-to-many relationships (Membership, Team)
```

**This one is real.** An organisation has many memberships and many teams. A query that joins
both through `Organisation` multiplies them: an organisation with 10 members and 4 teams
returns 40 rows, and any `COUNT` or `SUM` over that is wrong.

`S14.10` — *Fan Traps Are Resolved or Documented*. It cannot be resolved: an organisation
genuinely has both, and removing either relationship removes a fact the product needs. So it is
documented, which is the standard's other branch:

> **Never aggregate members and teams in a single join through `Organisation`.** Count them in
> separate queries, or reach team members through `Team → TeamMembership → Membership`, which is
> the real path and does not fan.

The shape is legitimate. The trap is what happens when somebody joins across it, which is why
the analyser calls it probable rather than certain.

## The second thing the analyser cannot see

`TeamMembership` reaches an organisation by two paths — through its team, and through its
membership. Nothing in the schema stops a team in organisation A from having a member whose
membership belongs to organisation B.

PostgreSQL cannot express "these two foreign keys must resolve to the same organisation" without
carrying `organisation_id` through both sides as part of a composite key. That is a real option
and it was not taken: it denormalises `organisation_id` into two more tables to enforce one
invariant, and `S14.8` requires denormalisation to be recorded rather than assumed — the cost
here is higher than the alternative.

So it is enforced in `governova_org` as an invariant with a test, and recorded here so the next
reader finds the reasoning rather than the gap.

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
