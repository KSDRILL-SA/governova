"""Read SQL DDL into the soundness model.

The second dialect, and the one that reaches teams with no ORM at all. It reads
`CREATE TABLE` statements — column definitions, inline and table-level constraints — and
nothing else. Views, functions, triggers, and vendor extensions are skipped rather than
half-understood.

**This is not a SQL parser and does not try to be.** It reads the declarative subset that
soundness questions are asked of, and records what it skipped as a note on the schema, so
a check that needed the skipped part reports `unknown` rather than assuming absence.
"""

from __future__ import annotations

import re

from governova_schema.model import Column, Relation, Schema, Table

_IDENT = r'(?:"[^"]{1,63}"|`[^`]{1,63}`|\[[^\]]{1,63}\]|[A-Za-z_][A-Za-z0-9_$]{0,63})'

_CREATE_TABLE = re.compile(
    rf"create\s+table\s+(?:if\s+not\s+exists\s+)?({_IDENT}(?:\.{_IDENT})?)\s*\(",
    re.I,
)

_COLUMN = re.compile(rf"^({_IDENT})\s+(.{{1,200}})$", re.S)

_PRIMARY_KEY_INLINE = re.compile(r"\bprimary\s+key\b", re.I)
_UNIQUE_INLINE = re.compile(r"\bunique\b", re.I)
_NOT_NULL = re.compile(r"\bnot\s+null\b", re.I)
_REFERENCES_INLINE = re.compile(rf"\breferences\s+({_IDENT})(?:\s*\(\s*({_IDENT})\s*\))?", re.I)
_ARRAY_TYPE = re.compile(r"\[\s*\]|\barray\b", re.I)

_TABLE_PRIMARY_KEY = re.compile(r"^\s{0,4}(?:constraint\s+\S{1,64}\s+)?primary\s+key\s*\(([^)]{1,300})\)", re.I)
_TABLE_UNIQUE = re.compile(r"^\s{0,4}(?:constraint\s+\S{1,64}\s+)?unique\s*\(([^)]{1,300})\)", re.I)
_TABLE_FOREIGN_KEY = re.compile(
    rf"^\s{{0,4}}(?:constraint\s+\S{{1,64}}\s+)?foreign\s+key\s*\(([^)]{{1,300}})\)\s*"
    rf"references\s+({_IDENT})(?:\s*\(([^)]{{1,300}})\))?",
    re.I,
)

# Constraint keywords that open a table-level clause rather than a column definition.
_CONSTRAINT_START = re.compile(
    r"^\s{0,4}(constraint|primary\s+key|unique|foreign\s+key|check|exclude)\b", re.I
)

# `re.M` matters: these appear on their own lines throughout a file, not only at its
# start. Without it the note is silently never recorded, and a skipped definition looks
# like an absent one.
_SKIPPABLE = re.compile(
    r"^\s{0,8}create\s+(?:or\s+replace\s+)?(view|function|procedure|trigger|index)\b",
    re.I | re.M,
)


def _clean(identifier: str) -> str:
    """Strip quoting and any schema qualifier — `public."User"` becomes `User`."""
    name = identifier.strip().strip('"').strip("`").strip("[]")
    return name.rsplit(".", 1)[-1].strip().strip('"').strip("`").strip("[]")


def _split_top_level(body: str) -> list[str]:
    """Split a CREATE TABLE body on commas that are not inside parentheses.

    `NUMERIC(10, 2)` must not split, which is why this is a scan rather than
    `body.split(",")`.
    """
    parts: list[str] = []
    depth = 0
    current: list[str] = []
    for char in body:
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        if char == "," and depth == 0:
            parts.append("".join(current))
            current = []
            continue
        current.append(char)
    if current:
        parts.append("".join(current))
    return [p.strip() for p in parts if p.strip()]


def _table_bodies(text: str) -> list[tuple[str, str, int]]:
    """(name, body, line) for each CREATE TABLE, matching parentheses properly."""
    results: list[tuple[str, str, int]] = []
    for match in _CREATE_TABLE.finditer(text):
        start = match.end()  # just past the opening paren
        depth = 1
        index = start
        while index < len(text) and depth:
            if text[index] == "(":
                depth += 1
            elif text[index] == ")":
                depth -= 1
            index += 1
        if depth:
            continue  # unterminated statement — skip rather than guess
        line = text.count("\n", 0, match.start()) + 1
        results.append((_clean(match.group(1)), text[start : index - 1], line))
    return results


def parse_sql(text: str, *, source_path: str = "") -> Schema:
    """Parse `CREATE TABLE` statements. Anything else is skipped and noted."""
    schema = Schema(dialect="sql", source_path=source_path)

    skipped = sorted({m.group(1).lower() for m in _SKIPPABLE.finditer(text)})
    if skipped:
        schema.notes.append(
            f"skipped {', '.join(skipped)} definitions — only CREATE TABLE is read"
        )

    for name, body, line in _table_bodies(text):
        table = Table(name=name, source_line=line)
        deferred_keys: list[str] = []
        deferred_unique: list[str] = []

        for clause in _split_top_level(body):
            pk = _TABLE_PRIMARY_KEY.match(clause)
            if pk:
                deferred_keys.extend(_clean(c) for c in pk.group(1).split(","))
                continue
            unique = _TABLE_UNIQUE.match(clause)
            if unique:
                deferred_unique.extend(_clean(c) for c in unique.group(1).split(","))
                continue
            fk = _TABLE_FOREIGN_KEY.match(clause)
            if fk:
                targets = [_clean(c) for c in (fk.group(3) or "").split(",") if c.strip()]
                for offset, column_name in enumerate(_clean(c) for c in fk.group(1).split(",")):
                    _attach_reference(
                        table,
                        column_name,
                        _clean(fk.group(2)),
                        targets[offset] if offset < len(targets) else None,
                    )
                continue
            if _CONSTRAINT_START.match(clause):
                continue  # CHECK / EXCLUDE / named constraint — not a soundness input

            column = _parse_column(clause)
            if column is not None:
                table.columns.append(column)

        for column_name in deferred_keys:
            _mark(table, column_name, primary_key=True)
        for column_name in deferred_unique:
            _mark(table, column_name, unique=True)

        schema.tables.append(table)

    schema.relations.extend(_relations_from_columns(schema))
    return schema


def _parse_column(clause: str) -> Column | None:
    match = _COLUMN.match(clause.strip())
    if not match:
        return None
    name = _clean(match.group(1))
    rest = match.group(2)
    reference = _REFERENCES_INLINE.search(rest)
    is_primary = bool(_PRIMARY_KEY_INLINE.search(rest))
    return Column(
        name=name,
        type=rest.split()[0] if rest.split() else "",
        # A primary key column is non-nullable by definition in every SQL dialect,
        # whether or not the DDL says so.
        nullable=not (_NOT_NULL.search(rest) or is_primary),
        primary_key=is_primary,
        unique=bool(_UNIQUE_INLINE.search(rest)),
        is_list=bool(_ARRAY_TYPE.search(rest)),
        references=_clean(reference.group(1)) if reference else None,
        references_column=(
            _clean(reference.group(2)) if reference and reference.group(2) else None
        ),
    )


def _attach_reference(table: Table, column_name: str, target: str, target_column: str | None) -> None:
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
                references_column=target_column,
            )
            return


def _mark(table: Table, column_name: str, *, primary_key: bool = False, unique: bool = False) -> None:
    """Apply a table-level PRIMARY KEY / UNIQUE clause to an already-parsed column."""
    for i, column in enumerate(table.columns):
        if column.name.lower() == column_name.lower():
            table.columns[i] = Column(
                name=column.name,
                type=column.type,
                # A column named in a PRIMARY KEY clause is non-nullable, whatever the
                # column definition said.
                nullable=column.nullable and not primary_key,
                primary_key=column.primary_key or primary_key,
                unique=column.unique or unique,
                is_list=column.is_list,
                references=column.references,
                references_column=column.references_column,
            )
            return


def _relations_from_columns(schema: Schema) -> list[Relation]:
    """Derive associations from foreign keys.

    SQL states cardinality only implicitly: a foreign key is many-to-one unless the
    column is unique, in which case it is one-to-one. That is all a DDL declares, and
    it is enough for the checks that consult it.
    """
    relations: list[Relation] = []
    seen: set[tuple[str, str, str]] = set()
    for table in schema.tables:
        for column in table.columns:
            if not column.references:
                continue
            key = (table.name.lower(), column.references.lower(), column.name.lower())
            if key in seen:
                continue
            seen.add(key)
            relations.append(
                Relation(
                    source=table.name,
                    target=column.references,
                    source_to_many=not (column.unique or column.primary_key),
                    target_to_many=False,
                    field_name=column.name,
                )
            )
    return relations
