"""Tests for the credit ledger — financial code, held to `#255`'s four criteria.

    1. `governova schema` runs clean and its findings were acted on   (Stage 1)
    2. no `float` anywhere in monetary or credit arithmetic
    3. a replayed billing webhook produces exactly one charge
    4. a balance is derivable from the ledger alone

Two, three and four are asserted here. The first landed with the schema.
"""

from __future__ import annotations

import datetime as dt
from decimal import Decimal

import pytest
from governova_ledger import (
    CREDIT_SCALE,
    HOURS_PER_MONTH,
    EntryKind,
    Ledger,
    LedgerEntry,
    LedgerError,
    Written,
    accrue,
    replay,
    to_credits,
    to_minor,
)

_NOW = dt.datetime(2026, 8, 21, 14, 30, tzinfo=dt.UTC)


def _ledger() -> Ledger:
    return Ledger("org-1")


# ─── Criterion 2 · never a float ─────────────────────────────────────────────


@pytest.mark.parametrize("bad", [0.1, 1.0, 12.5, -3.0])
def test_a_float_amount_is_refused_rather_than_converted(bad: float) -> None:
    """Converting would be worse than refusing.

    `Decimal(0.1)` is `0.1000000000000000055511151231257827…`. Accepting a float
    and converting it launders the error into the ledger, where it compounds
    silently and every later total is wrong by an amount that changes with the
    order of the additions.
    """
    with pytest.raises(LedgerError, match="never float"):
        to_minor(bad)


def test_the_refusal_names_the_rule_it_is_enforcing() -> None:
    """A developer hitting this should not have to guess why."""
    with pytest.raises(LedgerError) as caught:
        to_minor(0.1)
    assert "AP-S5.28a" in str(caught.value)


def test_a_float_budget_is_refused_too() -> None:
    """The accrual path takes an amount as well, and it is the same money."""
    with pytest.raises(LedgerError, match="never float"):
        accrue(_ledger(), monthly_budget=100.0, at=_NOW)


@pytest.mark.parametrize("good", [Decimal("0.1"), "0.1", 5, Decimal("1234.5678")])
def test_decimal_int_and_str_are_accepted(good: Decimal | str | int) -> None:
    assert isinstance(to_minor(good), int)


def test_a_value_finer_than_the_ledger_can_hold_is_refused() -> None:
    """Rounding here would either give work away or overcharge.

    Which of the two happened would depend on the value, so it is refused rather
    than resolved by a rule nobody would remember.
    """
    with pytest.raises(LedgerError, match="finer than"):
        to_minor(Decimal("0.00001"))


def test_minor_units_round_trip_exactly() -> None:
    for value in ("0.0001", "1", "9999.9999", "0.5"):
        assert to_credits(to_minor(Decimal(value))) == Decimal(value)


def test_the_ledger_source_carries_no_float_arithmetic() -> None:
    """Criterion 2, asserted by our own enforcer rather than by review.

    `AP-S5.28a` is a **blocking** rule this repository ships into other people's
    CI. Running it over our own financial code is the least we owe them.
    """
    from governova_checks import scan_paths
    from governova_compile.discovery import resolve_repo_root

    root = resolve_repo_root() / "scripts"
    files = [
        root / "governova_ledger" / "__init__.py",
        root / "governova_chain" / "__init__.py",
        root / "governova_org" / "__init__.py",
    ]
    findings = [f for f in scan_paths(files) if f.standard == "S5.28"]
    assert not findings, [f"{f.file}:{f.line} {f.match}" for f in findings]


def test_the_enforcer_would_actually_catch_a_float_here() -> None:
    """The test above is worthless if the rule cannot see Python.

    It could not, until this stage: `AP-S5.28a` matched `double price` — a
    C-family declaration — and read straight past `amount: float`. Criterion 2
    would have passed over this module without the rule reading a line of it.
    """
    from governova_checks import scan_text

    caught = scan_text("    balance: float = 0.0", file="scripts/governova_ledger/__init__.py")
    assert any(f.anti_pattern == "AP-S5.28a" for f in caught)


# ─── Criterion 3 · a replay produces exactly one charge ──────────────────────


def _webhook(ledger: Ledger, event_id: str, amount: str = "25") -> Written:
    """What a payment provider sends. They all retry; that is the point."""
    return ledger.record(
        EntryKind.GRANT, amount, idempotency_key=event_id, occurred_at=_NOW
    )


def test_a_replayed_webhook_produces_exactly_one_entry() -> None:
    """Criterion 3, with an actual replay rather than a claim about one."""
    ledger = _ledger()
    first = _webhook(ledger, "evt_abc123")
    again = _webhook(ledger, "evt_abc123")
    third = _webhook(ledger, "evt_abc123")

    assert len(ledger.entries) == 1
    assert first.entry == again.entry == third.entry
    assert ledger.balance() == Decimal(25)


def test_a_replay_returns_the_original_rather_than_raising() -> None:
    """The caller is a webhook handler whose correct behaviour is to acknowledge.

    Raising would make the provider retry again, forever, on a message that was
    already handled — turning one delivered event into an unbounded loop.
    """
    ledger = _ledger()
    original = _webhook(ledger, "evt_1")
    assert _webhook(ledger, "evt_1").entry is original.entry


def test_a_key_reused_for_different_content_is_refused() -> None:
    """That is not a retry. Two events were given the same name.

    Returning the first silently would lose the second, which is a charge that
    never happened and a balance nobody can explain.
    """
    ledger = _ledger()
    _webhook(ledger, "evt_1", amount="25")
    with pytest.raises(LedgerError, match="already used"):
        _webhook(ledger, "evt_1", amount="50")


def test_a_write_without_a_key_is_refused() -> None:
    with pytest.raises(LedgerError, match="idempotency key"):
        _ledger().record(EntryKind.GRANT, 5, idempotency_key="")


def test_an_entry_cannot_be_constructed_without_a_key() -> None:
    """`record` is not the only way in. `replay`, fixtures and importers are others."""
    with pytest.raises(LedgerError, match="idempotency key"):
        LedgerEntry(
            seq=1,
            organisation_id="org-1",
            kind=EntryKind.GRANT,
            amount_minor=10,
            idempotency_key="",
            occurred_at=_NOW.isoformat(),
        )


def test_loading_entries_with_a_duplicated_key_is_refused() -> None:
    """A duplicate in storage is a double charge that already happened.

    Loading it silently would make it permanent, and the balance would be wrong
    in a way that reconciles.
    """
    ledger = _ledger()
    _webhook(ledger, "evt_1")
    stored = ledger.entries
    with pytest.raises(LedgerError, match="double charge"):
        replay([*stored, stored[0]], "org-1")


# ─── Criterion 4 · the balance comes from the entries ────────────────────────


def test_the_balance_is_a_projection_over_the_entries() -> None:
    ledger = _ledger()
    ledger.record(EntryKind.GRANT, 100, idempotency_key="g1", occurred_at=_NOW)
    ledger.record(EntryKind.CONSUMPTION, "12.5", idempotency_key="c1", occurred_at=_NOW)
    ledger.record(EntryKind.REFUND, "2.5", idempotency_key="r1", occurred_at=_NOW)
    assert ledger.balance() == Decimal(90)


def test_there_is_no_stored_balance_to_disagree_with_the_entries() -> None:
    """Criterion 4. A projection that can disagree is a cache, and must be labelled one.

    Asserted structurally: replaying the entries into a fresh ledger reproduces
    the balance exactly, because there is nowhere else for it to come from.
    """
    ledger = _ledger()
    ledger.record(EntryKind.GRANT, 100, idempotency_key="g1", occurred_at=_NOW)
    ledger.record(EntryKind.CONSUMPTION, "37.25", idempotency_key="c1", occurred_at=_NOW)

    assert replay(ledger.entries, "org-1").balance() == ledger.balance()
    assert not any(
        "balance" in name for name in vars(ledger)
    ), "a stored balance appeared; it can now disagree with the entries"


def test_direction_comes_from_the_kind_not_from_the_sign() -> None:
    """A consumption of minus three credits is a refund wearing the wrong label.

    It would reconcile perfectly while being untrue, which is the worst kind of
    wrong a ledger can be.
    """
    with pytest.raises(LedgerError, match="unsigned"):
        _ledger().record(EntryKind.CONSUMPTION, -3, idempotency_key="c1")


def test_an_entry_cannot_be_constructed_with_a_negative_amount() -> None:
    with pytest.raises(LedgerError, match="unsigned"):
        LedgerEntry(
            seq=1,
            organisation_id="org-1",
            kind=EntryKind.CONSUMPTION,
            amount_minor=-30_000,
            idempotency_key="c1",
            occurred_at=_NOW.isoformat(),
        )


# ─── The chain, shared with the audit trail ──────────────────────────────────


def test_a_fresh_ledger_verifies() -> None:
    assert _ledger().verify().valid


def test_entries_are_linked_and_verify() -> None:
    ledger = _ledger()
    for i in range(5):
        ledger.record(EntryKind.GRANT, 10, idempotency_key=f"g{i}", occurred_at=_NOW)

    result = ledger.verify()
    assert result.valid, result.issues
    assert result.records == 5
    assert ledger.entries[0].prev_hash == "0" * 64
    assert ledger.entries[1].prev_hash == ledger.entries[0].record_hash


def test_an_edited_amount_breaks_the_chain() -> None:
    """The whole point: a balance cannot be changed quietly."""
    import dataclasses

    ledger = _ledger()
    ledger.record(EntryKind.CONSUMPTION, 10, idempotency_key="c1", occurred_at=_NOW)
    ledger.record(EntryKind.CONSUMPTION, 20, idempotency_key="c2", occurred_at=_NOW)

    tampered = list(ledger.entries)
    tampered[0] = dataclasses.replace(tampered[0], amount_minor=1)

    result = replay(tampered, "org-1").verify()
    assert not result.valid
    assert any("altered after it was written" in issue for issue in result.issues)


def test_a_removed_entry_breaks_the_chain() -> None:
    ledger = _ledger()
    for i in range(3):
        ledger.record(EntryKind.GRANT, 10, idempotency_key=f"g{i}", occurred_at=_NOW)

    without_the_middle = [ledger.entries[0], ledger.entries[2]]
    result = replay(without_the_middle, "org-1").verify()
    assert not result.valid


def test_the_ledger_and_the_audit_trail_use_one_implementation() -> None:
    """`#255`: building a second chain is `validate`-existed-twice with money attached."""
    import inspect

    import governova_audit
    import governova_ledger

    for module in (governova_audit, governova_ledger):
        source = inspect.getsource(module)
        assert "governova_chain" in source, f"{module.__name__} does not use the shared chain"
        assert "hashlib.sha256" not in source, (
            f"{module.__name__} hashes on its own rather than through the shared chain"
        )


# ─── Accrual ─────────────────────────────────────────────────────────────────


def test_credits_accrue_hourly_rather_than_resetting() -> None:
    """`ADR-010` §4 — so a subscriber who works in bursts is not punished."""
    ledger = _ledger()
    written = accrue(ledger, monthly_budget=Decimal(720), at=_NOW)
    assert written.created
    assert written.entry.kind is EntryKind.ACCRUAL
    assert written.entry.amount == Decimal(720) / HOURS_PER_MONTH


def test_an_accrual_job_that_runs_twice_credits_the_hour_once() -> None:
    """The key is the hour, which is what makes a scheduler safe.

    A retry, or two instances waking together, must not double the month's budget.
    """
    ledger = _ledger()
    accrue(ledger, monthly_budget=720, at=_NOW)
    accrue(ledger, monthly_budget=720, at=_NOW.replace(minute=59, second=59))

    assert len(ledger.entries) == 1


def test_a_month_of_accrual_does_not_exceed_the_budget() -> None:
    """Floored rather than rounded up: credit nobody sold is still a number that
    does not reconcile."""
    ledger = _ledger()
    budget = Decimal(1000)
    for hour in range(HOURS_PER_MONTH):
        accrue(ledger, monthly_budget=budget, at=_NOW + dt.timedelta(hours=hour))

    assert ledger.balance() <= budget


def test_the_hourly_rate_is_not_affected_by_the_length_of_the_month() -> None:
    """February and March accrue at the same rate.

    A subscriber whose credits arrived 10% faster in February would be right to
    ask why, and "the calendar" is not a reason.
    """
    assert HOURS_PER_MONTH == 30 * 24


def test_the_scale_is_fine_enough_for_a_small_review() -> None:
    """Two decimal places would round a Low-tier call to zero or up to a cent."""
    assert CREDIT_SCALE == 10_000
    assert to_minor(Decimal("0.0001")) == 1


# ─── What the caller is told ─────────────────────────────────────────────────


def test_a_write_says_whether_it_created_the_entry() -> None:
    """Idempotency in the ledger is not idempotency in the caller.

    `record` returned the entry alone, which left a handler that charges and then
    sends a receipt unable to tell a first delivery from a retry — so it sends
    the receipt twice. The ledger is correct and the customer is emailed twice,
    which is the same defect one layer out.
    """
    ledger = _ledger()
    first = _webhook(ledger, "evt_1")
    replayed = _webhook(ledger, "evt_1")

    assert first.created is True
    assert first.replayed is False
    assert replayed.created is False
    assert replayed.replayed is True


def test_a_handler_can_be_idempotent_because_of_it() -> None:
    """The property the return type exists to make available."""
    ledger = _ledger()
    receipts: list[str] = []

    for _ in range(4):  # the provider delivers the same event four times
        written = _webhook(ledger, "evt_1")
        if written.created:
            receipts.append(written.entry.idempotency_key)

    assert len(ledger.entries) == 1
    assert receipts == ["evt_1"]


def test_an_accrual_that_was_already_credited_says_so() -> None:
    ledger = _ledger()
    assert accrue(ledger, monthly_budget=720, at=_NOW).created is True
    assert accrue(ledger, monthly_budget=720, at=_NOW).created is False


# ─── What actually prevents a double charge ──────────────────────────────────


def test_the_database_carries_the_idempotency_constraint() -> None:
    """`S5.30` — uniqueness belongs in the database, not in application code.

    The in-memory index is the fast path and the readable error. It cannot be the
    guarantee: two deliveries of one webhook arriving at two processes both find
    no key and both write, and neither sees the other. Only the database does.

    Read from the schema so the constraint cannot be removed while this passes.
    """
    from governova_compile.discovery import resolve_repo_root

    schema = (
        resolve_repo_root() / "platform" / "cloud" / "prisma" / "schema.prisma"
    ).read_text(encoding="utf-8")
    block = schema.split("model LedgerEntry {")[1].split("\n}")[0]

    assert "@@unique([organisation_id, idempotency_key])" in block
    assert "@@unique([organisation_id, seq])" in block


def test_the_ledger_table_is_append_only() -> None:
    """The one model with no `deleted_at` and no `updated_at`, deliberately.

    `S5.34` asks every table for those. A ledger entry that can be soft-deleted
    is not append-only, and a balance derived from entries that can disappear is
    not derivable from anything. A movement is reversed by a REFUND entry — which
    is a fact — rather than by hiding the entry being reversed.
    """
    from governova_compile.discovery import resolve_repo_root

    schema = (
        resolve_repo_root() / "platform" / "cloud" / "prisma" / "schema.prisma"
    ).read_text(encoding="utf-8")
    block = schema.split("model LedgerEntry {")[1].split("\n}")[0]

    assert "deleted_at" not in block
    assert "updated_at" not in block
    assert "REFUND" in schema, "reversal must remain expressible as an entry"


def test_the_amount_column_is_an_integer_not_a_decimal_or_a_float() -> None:
    """The value hashed and the value stored must be the same bytes.

    A `Decimal` column serialises to a textual form that depends on how it was
    constructed — `1.0` and `1.00` are equal and do not encode identically, which
    would give two hashes for one amount and break the chain on a round trip.
    """
    from governova_compile.discovery import resolve_repo_root

    schema = (
        resolve_repo_root() / "platform" / "cloud" / "prisma" / "schema.prisma"
    ).read_text(encoding="utf-8")
    block = schema.split("model LedgerEntry {")[1].split("\n}")[0]

    # Declarations only. The doc comments above the column discuss `Decimal` and
    # `Float` by name, which is the point of them — reading those as column types
    # would make this test fail for saying the right thing.
    declarations = "\n".join(
        line for line in block.splitlines() if not line.strip().startswith("///")
    )
    assert "amount_minor    BigInt" in declarations
    assert "Float" not in declarations
    assert "Decimal" not in declarations
