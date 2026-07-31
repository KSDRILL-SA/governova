"""Tests for the schema-soundness analyser.

The exit criterion ADR-007 sets for this stage is **zero findings on a correct schema**.
That is the first test here and the one that matters most: an analyser that fires on
well-designed work is worse than no analyser, because every finding it makes afterwards
gets discounted.

The second-most-important behaviour is the refusal. 2NF and 3NF must come back as
`Unknown` and never as findings, because a schema does not declare functional
dependencies and a false normalisation verdict on a deliberately denormalised table
destroys trust in everything else.
"""

from __future__ import annotations

from governova_schema import (
    Confidence,
    analyse,
    analyse_repository,
    find_schema_files,
    normalisation_unknowns,
    parse_prisma,
    parse_sql,
)

# ─── Fixtures: a correct schema in each dialect ──────────────────────────────

SOUND_PRISMA = """
datasource db {
  provider = "postgresql"
}

enum Role {
  ADMIN
  MEMBER
}

model User {
  id    String @id @default(cuid())
  email String @unique
  role  Role   @default(MEMBER)
  posts Post[]
}

model Post {
  id       String    @id @default(cuid())
  title    String
  authorId String
  author   User      @relation(fields: [authorId], references: [id])
  tags     PostTag[]
}

model Tag {
  id    String    @id @default(cuid())
  label String    @unique
  posts PostTag[]
}

model PostTag {
  postId String
  tagId  String
  post   Post @relation(fields: [postId], references: [id])
  tag    Tag  @relation(fields: [tagId], references: [id])

  @@id([postId, tagId])
}
"""

SOUND_SQL = """
CREATE TABLE customer (
    customer_id INTEGER PRIMARY KEY,
    email       VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE invoice (
    invoice_id  INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customer(customer_id),
    total       NUMERIC(10, 2) NOT NULL
);
"""


def _codes(text: str, *, sql: bool = False) -> list[str]:
    schema = parse_sql(text) if sql else parse_prisma(text)
    findings, _ = analyse(schema)
    return [f.code for f in findings]


# ─── The exit criterion ──────────────────────────────────────────────────────


def test_a_correct_prisma_schema_produces_no_findings():
    """ADR-007 Stage 2 exit criterion. An analyser that fires on good work is worse
    than none, because every later finding gets discounted."""
    schema = parse_prisma(SOUND_PRISMA)
    assert [t.name for t in schema.tables] == ["User", "Post", "Tag", "PostTag"]
    findings, _ = analyse(schema)
    assert findings == [], [f.code for f in findings]


def test_a_correct_sql_schema_produces_no_findings():
    findings, _ = analyse(parse_sql(SOUND_SQL))
    assert findings == [], [f.code for f in findings]


# ─── The refusal — the behaviour that keeps the rest credible ────────────────


def test_normalisation_is_unknown_never_a_finding():
    """2NF and 3NF need functional dependencies, which a schema does not declare."""
    schema = parse_prisma(SOUND_PRISMA)
    findings, unknowns = analyse(schema)
    assert not any("normal" in f.code or f.code == "nf" for f in findings)
    questions = {u.question for u in unknowns}
    assert "third normal form" in questions
    # PostTag has a composite key, so the 2NF question is raised for it specifically.
    assert "second normal form" in questions
    assert any(u.table == "PostTag" for u in unknowns if u.question == "second normal form")


def test_every_unknown_explains_why_it_was_not_answered():
    # A bare "unknown" is not much better than silence. An auditor asking why must get
    # an answer that points at something.
    for unknown in normalisation_unknowns(parse_prisma(SOUND_PRISMA)):
        assert "functional dependencies" in unknown.reason


def test_a_schema_with_no_composite_key_raises_no_2nf_question():
    # The negative half: 2NF is a question about partial dependency on part of a
    # composite key. With no composite key there is no question to decline.
    unknowns = normalisation_unknowns(parse_sql(SOUND_SQL))
    assert not any(u.question == "second normal form" for u in unknowns)


# ─── Entity integrity ────────────────────────────────────────────────────────


def test_missing_primary_key_is_certain():
    codes = _codes("CREATE TABLE audit (happened_at TIMESTAMP, detail TEXT);", sql=True)
    assert "no-primary-key" in codes


def test_a_table_with_a_key_is_not_flagged():
    assert "no-primary-key" not in _codes(SOUND_SQL, sql=True)


def test_a_composite_key_declared_at_table_level_is_recognised():
    # The negative case that matters for the parser: PRIMARY KEY (a, b) appears *after*
    # the columns it constrains, so a single-pass reader would report no key at all.
    text = """
    CREATE TABLE post_tag (
        post_id INTEGER NOT NULL,
        tag_id  INTEGER NOT NULL,
        PRIMARY KEY (post_id, tag_id)
    );
    """
    schema = parse_sql(text)
    assert schema.table("post_tag").composite_key
    assert "no-primary-key" not in [f.code for f in analyse(schema)[0]]


def test_a_nullable_primary_key_is_reported():
    schema = parse_sql("CREATE TABLE t (id INTEGER, PRIMARY KEY (id));")
    # A column named in a PRIMARY KEY clause is non-nullable by definition, so this
    # must NOT fire — the dialect guarantees it even when the DDL is silent.
    assert "nullable-primary-key" not in [f.code for f in analyse(schema)[0]]


# ─── Referential integrity ───────────────────────────────────────────────────


def test_a_foreign_key_to_a_missing_table_is_certain():
    text = "CREATE TABLE s (id INTEGER PRIMARY KEY, o INTEGER REFERENCES purchase_order(id));"
    findings, _ = analyse(parse_sql(text))
    match = next(f for f in findings if f.code == "dangling-foreign-key")
    assert match.confidence is Confidence.CERTAIN


def test_a_foreign_key_to_a_non_key_column_is_reported():
    text = """
    CREATE TABLE customer (customer_id INTEGER PRIMARY KEY, nickname VARCHAR(50));
    CREATE TABLE note (
        note_id INTEGER PRIMARY KEY,
        who     VARCHAR(50) NOT NULL,
        CONSTRAINT fk FOREIGN KEY (who) REFERENCES customer(nickname)
    );
    """
    assert "foreign-key-to-non-key" in _codes(text, sql=True)


def test_a_foreign_key_to_a_unique_column_is_legitimate():
    # The negative half. A unique column is a candidate key; referencing it is correct,
    # and flagging it would make the check unusable on real schemas.
    text = """
    CREATE TABLE customer (customer_id INTEGER PRIMARY KEY, email VARCHAR(255) UNIQUE);
    CREATE TABLE note (
        note_id INTEGER PRIMARY KEY,
        mail    VARCHAR(255) NOT NULL,
        CONSTRAINT fk FOREIGN KEY (mail) REFERENCES customer(email)
    );
    """
    assert "foreign-key-to-non-key" not in _codes(text, sql=True)


def test_prisma_relations_resolve_without_a_dangling_report():
    assert "dangling-foreign-key" not in _codes(SOUND_PRISMA)


# ─── 1NF, M:N, and the graph-shape checks ────────────────────────────────────


def test_an_array_column_is_a_probable_repeating_group():
    findings, _ = analyse(parse_sql("CREATE TABLE c (id INTEGER PRIMARY KEY, phones TEXT[]);"))
    match = next(f for f in findings if f.code == "repeating-group")
    # Probable, never certain: an array is a deliberate, correct choice in plenty of
    # real schemas, and saying otherwise discredits every other finding.
    assert match.confidence is Confidence.PROBABLE


def test_scalar_columns_are_not_repeating_groups():
    assert "repeating-group" not in _codes(SOUND_SQL, sql=True)


def test_an_implicit_many_to_many_is_reported():
    text = """
    model Post { id String @id
      tags Tag[] }
    model Tag { id String @id
      posts Post[] }
    """
    assert "unresolved-many-to-many" in _codes(text)


def test_a_many_to_many_with_a_bridge_entity_is_not_reported():
    # The negative half, and the reason the sound fixture models PostTag explicitly.
    assert "unresolved-many-to-many" not in _codes(SOUND_PRISMA)


def test_a_fan_trap_needs_two_children():
    two = """
    CREATE TABLE c (id INTEGER PRIMARY KEY);
    CREATE TABLE invoice (id INTEGER PRIMARY KEY, cid INTEGER REFERENCES c(id));
    CREATE TABLE payment (id INTEGER PRIMARY KEY, cid INTEGER REFERENCES c(id));
    """
    assert "fan-trap" in _codes(two, sql=True)


def test_a_single_child_is_not_a_fan_trap():
    assert "fan-trap" not in _codes(SOUND_SQL, sql=True)


def test_a_relationship_cycle_is_reported():
    text = """
    CREATE TABLE a (id INTEGER PRIMARY KEY, cid INTEGER REFERENCES c(id));
    CREATE TABLE b (id INTEGER PRIMARY KEY, aid INTEGER REFERENCES a(id));
    CREATE TABLE c (id INTEGER PRIMARY KEY, bid INTEGER REFERENCES b(id));
    """
    assert "redundant-relationship" in _codes(text, sql=True)


def test_a_tree_shaped_schema_has_no_redundant_relationship():
    assert "redundant-relationship" not in _codes(SOUND_SQL, sql=True)


def test_history_without_a_temporal_key_is_reported():
    text = """
    CREATE TABLE price_history (
        product_id INTEGER PRIMARY KEY,
        valid_from DATE NOT NULL,
        price      NUMERIC(10, 2) NOT NULL
    );
    """
    assert "time-variant-without-temporal-key" in _codes(text, sql=True)


def test_history_with_a_temporal_key_is_correct():
    text = """
    CREATE TABLE price_history (
        product_id INTEGER NOT NULL,
        valid_from DATE NOT NULL,
        price      NUMERIC(10, 2) NOT NULL,
        PRIMARY KEY (product_id, valid_from)
    );
    """
    assert "time-variant-without-temporal-key" not in _codes(text, sql=True)


# ─── Parser behaviour and discovery ──────────────────────────────────────────


def test_non_table_definitions_are_skipped_and_recorded():
    schema = parse_sql("CREATE TABLE t (id INTEGER PRIMARY KEY);\nCREATE VIEW v AS SELECT 1;")
    assert [t.name for t in schema.tables] == ["t"]
    assert any("view" in note for note in schema.notes)


def test_numeric_precision_does_not_split_a_column_definition():
    # `NUMERIC(10, 2)` contains a comma. A naive split on commas loses the column.
    schema = parse_sql("CREATE TABLE t (id INTEGER PRIMARY KEY, total NUMERIC(10, 2) NOT NULL);")
    assert [c.name for c in schema.table("t").columns] == ["id", "total"]


def test_quoted_and_schema_qualified_names_are_normalised():
    schema = parse_sql('CREATE TABLE public."User" ("id" INTEGER PRIMARY KEY);')
    assert schema.table("User") is not None


def test_an_unterminated_statement_is_skipped_not_guessed():
    schema = parse_sql("CREATE TABLE broken (id INTEGER PRIMARY KEY")
    assert schema.tables == []


def test_prisma_enums_are_not_mistaken_for_relations():
    # `role Role` is an enum-typed scalar, not an association. Treating it as a relation
    # would invent an edge and could manufacture a fan trap out of nothing.
    schema = parse_prisma(SOUND_PRISMA)
    assert not any(r.target == "Role" for r in schema.relations)


def test_discovery_skips_migrations_and_vendored_trees(tmp_path):
    (tmp_path / "schema.prisma").write_text(SOUND_PRISMA, encoding="utf-8")
    migrations = tmp_path / "migrations"
    migrations.mkdir()
    (migrations / "001_init.sql").write_text(SOUND_SQL, encoding="utf-8")
    vendored = tmp_path / "node_modules" / "pkg"
    vendored.mkdir(parents=True)
    (vendored / "schema.prisma").write_text(SOUND_PRISMA, encoding="utf-8")
    assert [p.name for p in find_schema_files(tmp_path)] == ["schema.prisma"]


def test_the_parsers_stay_fast_on_hostile_input():
    """Every quantifier in this repository is bounded, and this is where that is proved.

    `AP-D-FINTECH.3a` once took 8.7 seconds on one 20k-character line. A schema file is
    exactly the kind of input that arrives generated, minified, or malformed, and these
    parsers run over whatever a consumer's repository contains — so the budget is
    measured rather than trusted to inspection.
    """
    import time

    hostile = {
        "unterminated": "CREATE TABLE t (" + "a" * 40_000,
        "nested-parens": "CREATE TABLE t (" + "(" * 8_000,
        "comma-storm": "CREATE TABLE t (" + "a," * 8_000 + ");",
        "long-identifier": "CREATE TABLE " + "a" * 30_000 + " (id INTEGER PRIMARY KEY);",
        "quote-storm": 'CREATE TABLE t (' + '"' * 8_000 + ");",
        "prisma-model-storm": "model M {\n" + ("  f String @id\n" * 4_000) + "}\n",
        "prisma-long-attr": "model M {\n  f String " + "@x" * 20_000 + "\n}\n",
        "prisma-unclosed": "model M {\n" + "a" * 40_000,
    }
    for name, payload in hostile.items():
        for parser in (parse_sql, parse_prisma):
            start = time.perf_counter()
            schema = parser(payload)
            analyse(schema)
            elapsed = time.perf_counter() - start
            assert elapsed < 2.0, f"{parser.__name__} took {elapsed:.2f}s on {name}"


def test_a_repository_with_no_schema_reports_nothing(tmp_path):
    # No schema is not a sound schema. It is unknown, exactly as requirements tier 0 is.
    schemas, findings, unknowns = analyse_repository(tmp_path)
    assert schemas == [] and findings == [] and unknowns == []
