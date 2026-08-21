"""Read a Prisma schema into the soundness model.

Prisma is the first dialect because it is declarative, widely deployed, and already in
the implementation registry — and because its relations are *stated* rather than
inferred, which is what makes referential integrity decidable rather than guessed.

This is a reader, not a validator. Anything it cannot determine becomes a note on the
schema, and a check that needed it reports `unknown`. Every quantifier below is bounded;
an unbounded one once cost 8.7 seconds on a single line in this repository.
"""

from __future__ import annotations

import re

from governova_schema.model import Column, Relation, Schema, Table

# `model User {` — the block opener. Bounded name, as every identifier here is.
_MODEL = re.compile(r"^\s{0,8}model\s+([A-Za-z_][A-Za-z0-9_]{0,63})\s*\{")
_ENUM = re.compile(r"^\s{0,8}(?:enum|type|view)\s+([A-Za-z_][A-Za-z0-9_]{0,63})\s*\{")
_CLOSE = re.compile(r"^\s{0,8}\}")

# `  email String @unique` — name, type, optional `?`/`[]`, then attributes.
_FIELD = re.compile(
    r"^\s{1,8}([A-Za-z_][A-Za-z0-9_]{0,63})\s+"
    r"([A-Za-z_][A-Za-z0-9_]{0,63})(\[\])?(\?)?"
    r"(.{0,400})$"
)

_ID_ATTR = re.compile(r"@id\b")
_UNIQUE_ATTR = re.compile(r"@unique\b")
_BLOCK_ID = re.compile(r"^\s{1,8}@@id\s*\(\s*\[([^\]]{0,300})\]")
_BLOCK_UNIQUE = re.compile(r"^\s{1,8}@@unique\s*\(\s*\[([^\]]{0,300})\]")
# `@relation(fields: [authorId], references: [id])`
_RELATION_FIELDS = re.compile(r"@relation\s*\((.{0,300})\)")
_FIELDS_LIST = re.compile(r"fields\s*:\s*\[([^\]]{0,200})\]")
_REFERENCES_LIST = re.compile(r"references\s*:\s*\[([^\]]{0,200})\]")

# Prisma scalars. A field whose type is none of these is a relation to another model.
_SCALARS = frozenset(
    {
        "string", "int", "biginit", "bigint", "float", "decimal", "boolean",
        "datetime", "json", "bytes", "unsupported",
    }
)


def _split_identifiers(raw: str) -> list[str]:
    return [part.strip().strip('"') for part in raw.split(",") if part.strip()]


def parse_prisma(text: str, *, source_path: str = "") -> Schema:
    """Parse a Prisma schema. Returns an empty schema rather than raising on junk."""
    schema = Schema(dialect="prisma", source_path=source_path)
    lines = text.splitlines()

    declared_types: set[str] = set()
    for line in lines:
        m = _ENUM.match(line)
        if m:
            declared_types.add(m.group(1).lower())

    current: Table | None = None
    # (table, field, target model, is_list) — resolved into relations after parsing,
    # because a relation's target may be declared later in the file.
    pending: list[tuple[str, str, str, bool]] = []

    for lineno, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("//"):
            continue

        opener = _MODEL.match(line)
        if opener:
            current = Table(name=opener.group(1), source_line=lineno)
            schema.tables.append(current)
            continue

        if current is None:
            continue

        if _CLOSE.match(line):
            current = None
            continue

        if _apply_block_attribute(current, line):
            continue

        if stripped.startswith("@@"):
            continue

        _parse_field(current, line, declared_types, pending)

    schema.relations.extend(_resolve_relations(pending, {t.name for t in schema.tables}))
    return schema


def _apply_block_attribute(table: Table, line: str) -> bool:
    """Handle `@@id` / `@@unique`. Returns whether the line was one of them.

    Split out of `parse_prisma` for `S13.6`: the loop was doing three unrelated
    jobs — tracking model boundaries, applying block attributes, and parsing
    fields — and each additional branch was making the other two harder to read.
    """
    block_id = _BLOCK_ID.match(line)
    if block_id:
        for name in _split_identifiers(block_id.group(1)):
            _mark(table, name, primary_key=True)
        return True

    block_unique = _BLOCK_UNIQUE.match(line)
    if block_unique:
        for name in _split_identifiers(block_unique.group(1)):
            _mark(table, name, unique=True)
        return True

    return False


def _parse_field(
    table: Table,
    line: str,
    declared_types: set[str],
    pending: list[tuple[str, str, str, bool]],
) -> None:
    """Add one field to `table`, or record it as a relation to resolve later."""
    field = _FIELD.match(line)
    if not field:
        return

    name, type_name, is_list, optional, attributes = field.groups()
    is_list = bool(is_list)
    lowered = type_name.lower()

    if lowered not in _SCALARS and lowered not in declared_types:
        # A relation field. The scalar FK column, if any, is named in `fields:`.
        pending.append((table.name, name, type_name, is_list))
        _record_foreign_key(table, type_name, attributes or "")
        return

    table.columns.append(
        Column(
            name=name,
            type=type_name,
            nullable=bool(optional) and not is_list,
            primary_key=bool(_ID_ATTR.search(attributes or "")),
            unique=bool(_UNIQUE_ATTR.search(attributes or "")),
            is_list=is_list,
        )
    )


def _mark(table: Table, column_name: str, *, primary_key: bool = False, unique: bool = False) -> None:
    """Apply a block-level `@@id` / `@@unique` to an already-parsed column.

    Block attributes appear *after* the fields they constrain, which is why this is a
    second pass over the table rather than something the field parser can do.
    """
    for i, column in enumerate(table.columns):
        if column.name.lower() == column_name.lower():
            table.columns[i] = Column(
                name=column.name,
                type=column.type,
                nullable=column.nullable,
                primary_key=column.primary_key or primary_key,
                unique=column.unique or unique,
                is_list=column.is_list,
                references=column.references,
                references_column=column.references_column,
            )
            return


def _record_foreign_key(table: Table, target: str, attributes: str) -> None:
    """Attach the target table to the scalar column a `@relation` names in `fields:`."""
    relation = _RELATION_FIELDS.search(attributes)
    if not relation:
        return
    fields = _FIELDS_LIST.search(relation.group(1))
    if not fields:
        return
    references = _REFERENCES_LIST.search(relation.group(1))
    target_columns = _split_identifiers(references.group(1)) if references else []

    for offset, column_name in enumerate(_split_identifiers(fields.group(1))):
        for i, column in enumerate(table.columns):
            if column.name.lower() == column_name.lower():
                table.columns[i] = Column(
                    name=column.name,
                    type=column.type,
                    nullable=column.nullable,
                    primary_key=column.primary_key,
                    unique=column.unique,
                    is_list=column.is_list,
                    references=target,
                    references_column=(
                        target_columns[offset] if offset < len(target_columns) else None
                    ),
                )
                break


def _resolve_relations(
    pending: list[tuple[str, str, str, bool]], known: set[str]
) -> list[Relation]:
    """Pair the two halves of each declared association.

    Prisma states a relation from both ends, so `Post.author` and `User.posts` are one
    association seen twice. Pairing them is what makes a many-to-many visible: it is
    exactly the case where both halves are lists.
    """
    by_pair: dict[tuple[str, str], list[tuple[str, str, bool]]] = {}
    for source, field_name, target, is_list in pending:
        if target not in known:
            continue
        left, right = sorted((source, target))
        by_pair.setdefault((left, right), []).append((source, field_name, is_list))

    relations: list[Relation] = []
    for (left, right), halves in sorted(by_pair.items()):
        left_to_many = any(is_list for source, _, is_list in halves if source == left)
        right_to_many = any(is_list for source, _, is_list in halves if source == right)
        field_name = halves[0][1] if halves else ""
        relations.append(
            Relation(
                source=left,
                target=right,
                source_to_many=left_to_many,
                target_to_many=right_to_many,
                field_name=field_name,
            )
        )
    return relations
