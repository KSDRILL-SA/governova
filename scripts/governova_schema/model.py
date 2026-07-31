"""A schema, reduced to the shape that soundness questions are asked of.

Deliberately smaller than any real schema language. This model carries identity,
nullability, references, and cardinality — the properties the relational canon reasons
about — and drops types, defaults, indexes, and vendor extensions, which no check here
consults. A parser's job is to produce this; a check's job is to read only this.

The consequence worth stating: **anything the model cannot represent, a check must
report as `unknown` rather than infer.** Functional dependencies are the case that
matters — a schema does not declare them, so 2NF and 3NF are not decidable from one, and
this model does not pretend to hold them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class Confidence(StrEnum):
    """How certain a finding is, which decides whether it may block.

    The distinction exists because this analyser reports on schemas somebody else
    designed. A `certain` finding is a decidable property of the schema as written —
    a foreign key pointing at no table is wrong under every design philosophy. A
    `probable` finding is a strong signal that a legitimate design can still produce:
    a denormalised reporting table is a deliberate trade, not a defect, and saying
    otherwise destroys trust in every other finding beside it.
    """

    CERTAIN = "certain"
    PROBABLE = "probable"


@dataclass(frozen=True)
class Column:
    """One attribute of one entity."""

    name: str
    type: str = ""
    nullable: bool = True
    primary_key: bool = False
    unique: bool = False
    is_list: bool = False
    """A repeating group — an array or scalar-list column. A 1NF question."""

    references: str | None = None
    """The table this column points at, when it declares a foreign key."""

    references_column: str | None = None


@dataclass(frozen=True)
class Relation:
    """A declared association between two entities.

    `to_many` on both sides is a many-to-many. In a relational store that needs a
    bridge entity to exist at all; where the schema language synthesises one
    implicitly, the modelling decision has been made by a tool rather than a designer.
    """

    source: str
    target: str
    source_to_many: bool = False
    target_to_many: bool = False
    field_name: str = ""


@dataclass
class Table:
    """One entity."""

    name: str
    columns: list[Column] = field(default_factory=list)
    source_line: int = 0

    @property
    def primary_key(self) -> list[Column]:
        return [c for c in self.columns if c.primary_key]

    @property
    def composite_key(self) -> bool:
        return len(self.primary_key) > 1

    def column(self, name: str) -> Column | None:
        lowered = name.lower()
        return next((c for c in self.columns if c.name.lower() == lowered), None)


@dataclass
class Schema:
    """Every entity and association a parser could read from one source."""

    tables: list[Table] = field(default_factory=list)
    relations: list[Relation] = field(default_factory=list)
    dialect: str = "unknown"
    source_path: str = ""
    notes: list[str] = field(default_factory=list)
    """What the parser could **not** determine. An auditor asking why a check stayed
    silent must get an answer that points at something."""

    def table(self, name: str) -> Table | None:
        lowered = name.lower()
        return next((t for t in self.tables if t.name.lower() == lowered), None)

    @property
    def is_empty(self) -> bool:
        return not self.tables


@dataclass(frozen=True)
class Finding:
    """One soundness finding.

    `advisory` is True for everything this analyser produces today. The checks are new,
    they report on schemas this project did not design, and a check that fires wrongly
    on its first encounter with a real schema does not get a second one.
    """

    code: str
    message: str
    table: str | None = None
    column: str | None = None
    confidence: Confidence = Confidence.CERTAIN
    source_path: str = ""
    advisory: bool = True


@dataclass(frozen=True)
class Unknown:
    """A question this analyser deliberately declines to answer.

    The most important type in this module. A schema does not declare functional
    dependencies, so 2NF and 3NF cannot be decided from one — and a guess that lands
    on a deliberately denormalised table is worse than silence, because it teaches the
    reader to discount every other finding.

    Reported explicitly rather than omitted, so the gap is visible instead of looking
    like a clean result.
    """

    question: str
    reason: str
    table: str | None = None
