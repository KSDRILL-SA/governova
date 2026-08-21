"""The credit ledger — append-only, hash-linked, and never a float.

This is financial code and it inherits C05 entirely. Four properties are not
negotiable, and each is here because getting it wrong is expensive in a way that
is invisible until somebody is charged incorrectly.

**`Decimal`, never `float`.** `S5.28` / `AP-S5.28a` is a rule this repository
ships as *blocking* into other people's CI. A float here would be the product
violating the standard it sells, in the code that charges people. Amounts are
carried as integer **minor units** in string form on the wire (`ADR-011`), so
nothing between the ledger and the database can widen them to binary floating
point on the way past.

**Append-only.** Every balance change is an entry. A balance is a *projection*
over entries and never a stored column, because a stored balance and its entries
can disagree — and when they do, there is no way to tell which one is wrong.

**Idempotent.** Every write carries a key. A payment webhook that is retried —
and they are all retried — must produce exactly one charge. `S2.34`.

**Hash-linked, using the chain that already exists.** `governova_chain`, shared
with the governance audit trail. Building a second one would be the
`validate`-existed-twice failure with money attached.
"""

from __future__ import annotations

import dataclasses
import datetime as dt
from collections.abc import Sequence
from decimal import Decimal
from enum import StrEnum
from typing import Any

from governova_chain import (
    GENESIS_HASH,
    Verification,
    canonical_hash,
    next_link,
    verify_chain,
)

# Credits are counted in whole units with four decimal places of precision, held
# as an integer number of ten-thousandths. Four because a Low-tier review can
# cost a small fraction of a credit and rounding it to two would either round
# many of them to zero — free work — or round them up, which is a charge nobody
# agreed to.
CREDIT_SCALE = 10_000
_QUANTUM = Decimal(1) / CREDIT_SCALE


class EntryKind(StrEnum):
    """Why the balance moved. The vocabulary is closed on purpose.

    A free-text reason cannot be summed, cannot be reconciled, and cannot be
    checked — and a ledger nobody can reconcile is a list.
    """

    ACCRUAL = "accrual"
    """Hourly accrual against a tier budget (`ADR-010` §4)."""
    CONSUMPTION = "consumption"
    """A metered Gateway call."""
    GRANT = "grant"
    """Credits added by hand — a trial, a goodwill adjustment, a correction."""
    REFUND = "refund"
    """A reversal of a consumption, recorded rather than deleted."""
    EXPIRY = "expiry"
    """Accrued credit that lapsed at the end of a budget window."""


class LedgerError(RuntimeError):
    """A write the ledger refused, with the reason."""


def to_minor(amount: Decimal | int | str) -> int:
    """A credit amount as an integer number of ten-thousandths.

    Accepts `Decimal`, `int` or `str` and **never `float`.** A float argument is
    refused rather than converted: `0.1` is not one tenth, and the moment it
    enters the arithmetic every later total is quietly wrong by an amount nobody
    can predict or reproduce.
    """
    if isinstance(amount, float):
        raise LedgerError(
            "credit amounts are never float. 0.1 is not one tenth in binary "
            "floating point, and a total built from floats is wrong by an amount "
            "that changes with the order of the additions. Pass Decimal, int or str "
            "(AP-S5.28a — this repository blocks builds for it)."
        )
    value = Decimal(amount) if not isinstance(amount, Decimal) else amount
    scaled = value * CREDIT_SCALE
    if scaled != scaled.to_integral_value():
        raise LedgerError(
            f"{value} is finer than the ledger's precision of {_QUANTUM}. Rounding it "
            "here would either give work away or charge for more than was used, and "
            "which of those happened would depend on the value."
        )
    return int(scaled)


def to_credits(minor: int) -> Decimal:
    """A stored minor-unit integer back as a `Decimal` credit amount."""
    return Decimal(minor) / CREDIT_SCALE


@dataclasses.dataclass(frozen=True)
class LedgerEntry:
    """One immutable movement.

    `amount_minor` is an integer, not a `Decimal` field, so that the value that
    is hashed and the value that is stored are the same bytes. A `Decimal`
    serialised to JSON becomes a string whose form depends on how it was
    constructed — `Decimal("1.0")` and `Decimal("1.00")` are equal and do not
    encode identically, which would give two hashes for one amount.
    """

    seq: int
    organisation_id: str
    kind: EntryKind
    amount_minor: int
    idempotency_key: str
    occurred_at: str
    detail: str = ""
    prev_hash: str = GENESIS_HASH
    record_hash: str = ""

    def __post_init__(self) -> None:
        """The shape rules, enforced by the type rather than by the writer.

        `Ledger.record` checks these on the way in, and an entry constructed
        directly would bypass every one of them. Direct construction is not
        exotic — `replay` does it on every row read back from the database, and
        so will any importer, fixture or migration.
        """
        if self.amount_minor < 0:
            raise LedgerError(
                "amounts are unsigned; the direction comes from the kind. A "
                "consumption of a negative amount is a refund wearing the wrong "
                "label, and it would reconcile perfectly while being untrue."
            )
        if not self.idempotency_key:
            raise LedgerError(
                "every entry carries an idempotency key (S2.34). A retried webhook "
                "that double-charges is the defect this ledger most deserves to be "
                "judged on."
            )
        if self.seq < 1:
            raise LedgerError(f"sequence numbers start at 1, not {self.seq}")

    @property
    def amount(self) -> Decimal:
        return to_credits(self.amount_minor)

    def payload(self) -> dict[str, Any]:
        """The signed portion — everything except the hash it produces."""
        content = dataclasses.asdict(self)
        content.pop("record_hash")
        content["kind"] = str(self.kind)
        return content

    def compute_hash(self) -> str:
        return canonical_hash(self.payload())


# Which direction each kind moves the balance. Held as data rather than as a sign
# on the amount so that an entry cannot be written with a nonsensical one — a
# consumption of *negative* three credits is a refund wearing the wrong label,
# and it would reconcile perfectly while being untrue.
_DIRECTION: dict[EntryKind, int] = {
    EntryKind.ACCRUAL: +1,
    EntryKind.GRANT: +1,
    EntryKind.REFUND: +1,
    EntryKind.CONSUMPTION: -1,
    EntryKind.EXPIRY: -1,
}


class Ledger:
    """An organisation's entries, in order.

    In memory for now. Stage 1's PostgreSQL is where these rows live; the rules
    are here so they can be tested without one, and so that the storage layer
    cannot quietly acquire a second opinion about what a balance is.
    """

    def __init__(self, organisation_id: str, entries: Sequence[LedgerEntry] = ()) -> None:
        """A ledger, optionally rebuilt from stored entries.

        Reconstruction is a constructor rather than a function reaching into the
        instance afterwards. The index below is *derived* from the entries in one
        place, so the two cannot drift — a separate dict maintained alongside
        appends is one missed update away from a duplicate charge, which is the
        one defect this whole module exists to prevent.

        It does **not** re-hash. An entry whose stored hash disagrees with its
        content is exactly what `verify` exists to report, and silently repairing
        it here would destroy the only evidence.
        """
        self.organisation_id = organisation_id
        self._entries: list[LedgerEntry] = list(entries)
        self._keys: dict[str, LedgerEntry] = {e.idempotency_key: e for e in self._entries}
        if len(self._keys) != len(self._entries):
            raise LedgerError(
                "the stored entries contain a duplicated idempotency key, which "
                "means a retry was recorded twice. That is a double charge, and "
                "loading it silently would make it permanent."
            )

    @property
    def entries(self) -> list[LedgerEntry]:
        return list(self._entries)

    def record(
        self,
        kind: EntryKind,
        amount: Decimal | int | str,
        *,
        idempotency_key: str,
        occurred_at: dt.datetime | None = None,
        detail: str = "",
    ) -> LedgerEntry:
        """Append one movement, or return the one this key already wrote.

        **A replay returns the original entry rather than raising.** The caller
        is a webhook handler that has been retried, and its correct behaviour is
        to acknowledge — raising would make it retry again, forever, on a message
        that was already handled.

        A key reused with *different* content is a different matter and does
        raise: that is not a retry, it is two events that were given the same
        name, and silently returning the first would lose the second.
        """
        if not idempotency_key:
            raise LedgerError(
                "every ledger write carries an idempotency key (S2.34). A retried "
                "webhook that double-charges is the defect this ledger most "
                "deserves to be judged on."
            )

        minor = to_minor(amount)
        if minor < 0:
            raise LedgerError(
                "amounts are unsigned; the direction comes from the kind. A "
                "consumption of a negative amount is a refund wearing the wrong "
                "label, and it would reconcile perfectly while being untrue."
            )

        existing = self._keys.get(idempotency_key)
        if existing is not None:
            if existing.kind is not kind or existing.amount_minor != minor:
                raise LedgerError(
                    f"idempotency key {idempotency_key!r} was already used for "
                    f"{existing.kind} of {existing.amount}, and is now presented for "
                    f"{kind} of {to_credits(minor)}. Two different events cannot share "
                    "a key — one of them would be lost."
                )
            return existing

        seq, prev_hash = next_link(self._entries)
        entry = LedgerEntry(
            seq=seq,
            organisation_id=self.organisation_id,
            kind=kind,
            amount_minor=minor,
            idempotency_key=idempotency_key,
            occurred_at=(occurred_at or dt.datetime.now(dt.UTC)).isoformat(),
            detail=detail,
            prev_hash=prev_hash,
        )
        entry = dataclasses.replace(entry, record_hash=entry.compute_hash())
        self._entries.append(entry)
        self._keys[idempotency_key] = entry
        return entry

    def balance(self) -> Decimal:
        """The balance, derived from the entries and nowhere else.

        There is no stored column to disagree with this. `#255`'s fourth
        criterion says a balance must be derivable from the ledger alone, and
        that if the two can disagree the projection is a cache and must be
        labelled one. Nothing here is a cache.
        """
        total = sum(_DIRECTION[e.kind] * e.amount_minor for e in self._entries)
        return to_credits(total)

    def verify(self) -> Verification:
        """Walk the chain. Shared with the governance trail — one implementation."""
        return verify_chain(self._entries, label="entry")


def accrue(
    ledger: Ledger,
    *,
    monthly_budget: Decimal | int | str,
    hours: int = 1,
    at: dt.datetime | None = None,
) -> LedgerEntry:
    """Hourly accrual against a tier budget (`ADR-010` §4).

    Credits accrue rather than resetting monthly, *"so a subscriber who works in
    bursts is not punished for the shape of their week"*. The hourly rate is the
    monthly budget divided across a 30-day month.

    The idempotency key is the hour itself, which is what makes a scheduler safe:
    an accrual job that runs twice for the same hour — because it was retried, or
    because two instances woke together — credits that hour once.
    """
    moment = at or dt.datetime.now(dt.UTC)
    hour = moment.replace(minute=0, second=0, microsecond=0)
    per_hour = _hourly_rate(monthly_budget)
    return ledger.record(
        EntryKind.ACCRUAL,
        per_hour * hours,
        idempotency_key=f"accrual:{ledger.organisation_id}:{hour.isoformat()}",
        occurred_at=hour,
        detail=f"{hours}h at {per_hour}/h",
    )


# A month for accrual purposes. Fixed at 30 days rather than the calendar's
# length so that the hourly rate does not change between February and March —
# a subscriber whose credits accrue 10% faster in February would be right to ask
# why, and the answer would be "the calendar", which is not a reason.
HOURS_PER_MONTH = 30 * 24


def _hourly_rate(monthly_budget: Decimal | int | str) -> Decimal:
    """The per-hour share of a monthly budget, floored to the ledger's precision.

    Floored, never rounded up. Rounding up would accrue more than the budget over
    a month — the subscriber would be given credit nobody sold them, which is a
    smaller problem than overcharging and still a number that does not reconcile.
    """
    if isinstance(monthly_budget, float):
        raise LedgerError("a tier budget is never float — see `to_minor`.")
    budget = Decimal(monthly_budget) if not isinstance(monthly_budget, Decimal) else monthly_budget
    minor = int((budget * CREDIT_SCALE) / HOURS_PER_MONTH)
    return to_credits(minor)


def replay(entries: Sequence[LedgerEntry], organisation_id: str) -> Ledger:
    """Rebuild a ledger from stored entries. A thin name over the constructor."""
    return Ledger(organisation_id, entries)
