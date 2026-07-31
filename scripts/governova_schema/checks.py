"""Schema soundness checks — and the questions this analyser refuses to answer.

C05 governs how data is *accessed*. Nothing in the corpus asked whether a schema is
**sound**, which is the other half of the most expensive place in software to be wrong.

Every check here is a decidable property of a schema as written, not a design opinion.
That line is load-bearing, and it is drawn twice:

**`CERTAIN` versus `PROBABLE`.** A foreign key pointing at no table is wrong under every
design philosophy. An array column is a repeating group under the relational model and a
deliberate, correct choice in a document store or a Postgres schema that means it — so it
is reported as probable, and probable findings never block.

**Normalisation is not answered at all.** 2NF and 3NF are properties of *functional
dependencies*, and a schema does not declare them. Inferring them from column names would
mean guessing, and a false 3NF finding on a deliberately denormalised reporting table
destroys trust in every other check beside it. Those questions are returned as `Unknown`,
explicitly, so the gap is visible rather than looking like a clean result.

That refusal is the most important behaviour in this module.
"""

from __future__ import annotations

from governova_schema.model import Confidence, Finding, Schema, Table, Unknown

# Columns whose presence implies the row is a version of something over time. A table
# with these and no temporal component in its key cannot hold two versions of one entity.
_TEMPORAL_HINTS = frozenset(
    {"valid_from", "valid_to", "effective_from", "effective_to", "start_date", "end_date", "version"}
)


def check_entity_integrity(schema: Schema) -> list[Finding]:
    """Every entity has a primary key, and no part of it is nullable.

    The relational model's first guarantee: a row must be identifiable. Without it,
    duplicates cannot be prevented, an update cannot be aimed at one row, and no other
    table can reference this one — which is why this is `CERTAIN` rather than a matter
    of taste.
    """
    findings: list[Finding] = []
    for table in schema.tables:
        key = table.primary_key
        if not key:
            findings.append(
                Finding(
                    code="no-primary-key",
                    message=(
                        f"{table.name} declares no primary key — its rows are not "
                        f"identifiable, so they cannot be reliably updated or referenced"
                    ),
                    table=table.name,
                    source_path=schema.source_path,
                )
            )
            continue
        findings.extend(
            Finding(
                code="nullable-primary-key",
                message=(
                    f"{table.name}.{column.name} is part of the primary key but is "
                    f"nullable — a null identifier identifies nothing"
                ),
                table=table.name,
                column=column.name,
                source_path=schema.source_path,
            )
            for column in key
            if column.nullable
        )
    return findings


def check_referential_integrity(schema: Schema) -> list[Finding]:
    """Every foreign key resolves to a table that exists, and to a key within it.

    A dangling reference is decidably wrong: the constraint cannot be enforced, so the
    column holds values the database will never validate.
    """
    findings: list[Finding] = []
    for table in schema.tables:
        for column in table.columns:
            if not column.references:
                continue
            target = schema.table(column.references)
            if target is None:
                findings.append(
                    Finding(
                        code="dangling-foreign-key",
                        message=(
                            f"{table.name}.{column.name} references {column.references}, "
                            f"which is not a table in this schema"
                        ),
                        table=table.name,
                        column=column.name,
                        source_path=schema.source_path,
                    )
                )
                continue
            findings.extend(_check_target_column(schema, table, column, target))
    return findings


def _check_target_column(schema: Schema, table: Table, column, target: Table) -> list[Finding]:
    if column.references_column is None:
        return []  # target column not named — the dialect resolves it to the PK
    referenced = target.column(column.references_column)
    if referenced is None:
        return [
            Finding(
                code="dangling-foreign-key",
                message=(
                    f"{table.name}.{column.name} references "
                    f"{target.name}.{column.references_column}, which does not exist"
                ),
                table=table.name,
                column=column.name,
                source_path=schema.source_path,
            )
        ]
    if not (referenced.primary_key or referenced.unique):
        return [
            Finding(
                code="foreign-key-to-non-key",
                message=(
                    f"{table.name}.{column.name} references "
                    f"{target.name}.{referenced.name}, which is neither a primary key "
                    f"nor unique — the reference can match many rows"
                ),
                table=table.name,
                column=column.name,
                source_path=schema.source_path,
            )
        ]
    return []


def check_repeating_groups(schema: Schema) -> list[Finding]:
    """First normal form — an attribute holds one value, not a list.

    **Probable, never certain.** A Postgres array or a Prisma scalar list is a repeating
    group under the relational model, and it is also a legitimate, deliberate choice in
    plenty of real schemas. The concern is named universally; the verdict is left to the
    designer who knows whether the trade was made on purpose.
    """
    return [
        Finding(
            code="repeating-group",
            message=(
                f"{table.name}.{column.name} holds a list of values — under the "
                f"relational model this is a repeating group. If the denormalisation is "
                f"deliberate, record why; if not, it belongs in its own table"
            ),
            table=table.name,
            column=column.name,
            confidence=Confidence.PROBABLE,
            source_path=schema.source_path,
        )
        for table in schema.tables
        for column in table.columns
        if column.is_list
    ]


def check_unresolved_many_to_many(schema: Schema) -> list[Finding]:
    """A many-to-many with no bridge entity.

    Decidable and worth catching: a relational store cannot represent M:N directly, so
    either a bridge table exists or the ORM is synthesising one invisibly. In the second
    case the join table's name, keys, and indexes were chosen by a tool — and it is the
    place any attribute *of the association itself* would have to live, which is
    precisely what cannot be added later without a migration.
    """
    return [
        Finding(
            code="unresolved-many-to-many",
            message=(
                f"{relation.source} ↔ {relation.target} is many-to-many with no bridge "
                f"entity in the schema — the join table is implicit, so it can carry no "
                f"attributes of the association itself"
            ),
            table=relation.source,
            confidence=Confidence.PROBABLE,
            source_path=schema.source_path,
        )
        for relation in schema.relations
        if relation.source_to_many and relation.target_to_many
    ]


def check_fan_trap(schema: Schema) -> list[Finding]:
    """A fan trap — one parent, two one-to-many children, joined through the parent.

    A structural property of the relationship graph, not an opinion: a query joining
    both children through the shared parent multiplies their rows against each other
    and silently returns wrong aggregates. The shape is legitimate; the trap is what
    happens when somebody joins across it, so this is probable and advisory.
    """
    children: dict[str, list[str]] = {}
    for relation in schema.relations:
        if relation.source_to_many and not relation.target_to_many:
            children.setdefault(relation.target, []).append(relation.source)

    findings: list[Finding] = []
    for parent, kids in sorted(children.items()):
        unique_kids = sorted(set(kids))
        if len(unique_kids) < 2:
            continue
        findings.append(
            Finding(
                code="fan-trap",
                message=(
                    f"{parent} is the one side of {len(unique_kids)} separate "
                    f"one-to-many relationships ({', '.join(unique_kids)}) — joining two "
                    f"of them through {parent} multiplies their rows and returns wrong "
                    f"aggregates"
                ),
                table=parent,
                confidence=Confidence.PROBABLE,
                source_path=schema.source_path,
            )
        )
    return findings


def check_redundant_relationship(schema: Schema) -> list[Finding]:
    """A cycle in the relationship graph — the same fact reachable by two paths.

    Two routes between the same entities can disagree, and nothing in the schema
    prevents it. Sometimes the shortcut is a deliberate denormalisation for query cost;
    that is why this is probable and asks for the trade to be recorded rather than
    removed.
    """
    edges: dict[str, set[str]] = {}
    for relation in schema.relations:
        edges.setdefault(relation.source, set()).add(relation.target)
        edges.setdefault(relation.target, set()).add(relation.source)

    findings: list[Finding] = []
    for relation in schema.relations:
        a, b = relation.source, relation.target
        # A third entity adjacent to both closes a triangle: A→B directly, and A→C→B.
        shared = sorted((edges.get(a, set()) & edges.get(b, set())) - {a, b})
        if not shared:
            continue
        findings.append(
            Finding(
                code="redundant-relationship",
                message=(
                    f"{a} and {b} are related directly and also through "
                    f"{', '.join(shared)} — the same fact is reachable by two paths, "
                    f"which can disagree. Record the trade if the shortcut is deliberate"
                ),
                table=a,
                confidence=Confidence.PROBABLE,
                source_path=schema.source_path,
            )
        )
    # One finding per unordered pair — a cycle is a property of the pair, not a direction.
    seen: set[tuple[str, str]] = set()
    unique: list[Finding] = []
    for finding in findings:
        left, right = sorted((finding.table or "", finding.message[:40]))
        if (left, right) in seen:
            continue
        seen.add((left, right))
        unique.append(finding)
    return unique


def check_time_variant_key(schema: Schema) -> list[Finding]:
    """Time-variant data whose key cannot hold two versions of the same entity.

    A table carrying `valid_from` / `effective_to` / `version` is recording history. If
    no temporal column participates in its key, the second version of an entity collides
    with the first — so either history is silently lost or the key is doing something
    other than identifying.
    """
    findings: list[Finding] = []
    for table in schema.tables:
        temporal = [c for c in table.columns if c.name.lower() in _TEMPORAL_HINTS]
        if not temporal:
            continue
        key = table.primary_key
        if not key:
            continue  # `no-primary-key` already covers this, and one defect is one finding
        if any(c.name.lower() in _TEMPORAL_HINTS for c in key):
            continue
        findings.append(
            Finding(
                code="time-variant-without-temporal-key",
                message=(
                    f"{table.name} records history ({', '.join(c.name for c in temporal)}) "
                    f"but no temporal column is part of its key — two versions of the "
                    f"same entity cannot coexist"
                ),
                table=table.name,
                confidence=Confidence.PROBABLE,
                source_path=schema.source_path,
            )
        )
    return findings


# ─── The questions this analyser declines to answer ──────────────────────────


def normalisation_unknowns(schema: Schema) -> list[Unknown]:
    """2NF and 3NF, reported as `unknown` rather than guessed.

    Both are properties of **functional dependencies**, which a schema does not declare.
    Inferring them would mean reading meaning out of column names — deciding that
    `city` depends on `postcode` because it usually does — and being wrong about that on
    a deliberately denormalised reporting table would teach the reader to discount every
    other finding this analyser makes.

    Reported rather than omitted. A silent gap looks like a clean result.
    """
    unknowns = [
        Unknown(
            question="second normal form",
            reason=(
                "partial dependency needs functional dependencies, which a schema does "
                "not declare; inferring them from column names would be a guess"
            ),
            table=table.name,
        )
        for table in schema.tables
        if table.composite_key
    ]
    if schema.tables:
        unknowns.append(
            Unknown(
                question="third normal form",
                reason=(
                    "transitive dependency needs functional dependencies, which a schema "
                    "does not declare; a false finding on a deliberately denormalised "
                    "table would discredit every other check"
                ),
            )
        )
    return unknowns


ALL_CHECKS = (
    check_entity_integrity,
    check_referential_integrity,
    check_repeating_groups,
    check_unresolved_many_to_many,
    check_fan_trap,
    check_redundant_relationship,
    check_time_variant_key,
)


def analyse(schema: Schema) -> tuple[list[Finding], list[Unknown]]:
    """Run every check. A check that raises is skipped, never silently passed."""
    findings: list[Finding] = []
    for check in ALL_CHECKS:
        try:
            findings.extend(check(schema))
        except Exception:
            # A broken check must not report a clean schema. Its questions become
            # unanswered rather than answered favourably.
            schema.notes.append(f"check {check.__name__} failed and was skipped")
    findings.sort(key=lambda f: (f.table or "", f.code, f.column or ""))
    return findings, normalisation_unknowns(schema)
