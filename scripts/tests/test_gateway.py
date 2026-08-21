"""Tests for the Intelligence Gateway — Stage 3.

`ADR-010` §4 states three things the Gateway must never do. Each is asserted here
as a property of the design rather than of the code's current behaviour, because
a guarantee that only holds while nobody edits the file is not a guarantee.
"""

from __future__ import annotations

import datetime as dt
from decimal import Decimal

import pytest
from governova_gateway import (
    RETRY_AFTER,
    TIER_COST,
    TIER_ORDER,
    Authorisation,
    EffortTier,
    Queued,
    affordable_tiers,
    authorise,
    settle,
)
from governova_ledger import EntryKind, Ledger
from governova_semantic import Outcome, ReviewResult

_KEY = "review:pr-42:abc123"


def _ledger(credits: str = "100") -> Ledger:
    ledger = Ledger("org-1")
    ledger.record(EntryKind.GRANT, credits, idempotency_key="seed")
    return ledger


def _reviewed() -> ReviewResult:
    """A review that actually happened and found nothing."""
    return ReviewResult(outcome=Outcome.REVIEWED)


def _outage() -> ReviewResult:
    return ReviewResult(outcome=Outcome.UNAVAILABLE, detail="endpoint unreachable")


# ─── "Never terminate a review mid-task" ─────────────────────────────────────


def test_there_is_no_way_to_express_aborting_a_review() -> None:
    """The guarantee, asserted as the absence of a spelling for its opposite.

    `ADR-010` §4: *"a governance verdict truncated halfway is worse than one not
    attempted — it looks like a result."* A `Decision` has exactly two members,
    and the way that survives future edits is that there is nowhere to put a
    third without this failing.
    """
    import typing

    import governova_gateway

    members = typing.get_args(governova_gateway.Decision.__value__)
    assert set(members) == {Authorisation, Queued}, members


def test_the_balance_is_decided_once_and_not_consulted_again() -> None:
    """An authorisation is a value, so nothing can change underneath a review.

    This is the mechanism behind the guarantee above: there is no point during a
    review at which the budget is asked again, so there is no point at which the
    answer can change.
    """
    ledger = _ledger("100")
    granted = authorise(ledger.balance(), EffortTier.HIGH, idempotency_key=_KEY)
    assert isinstance(granted, Authorisation)

    # The organisation spends everything else while the review is in flight.
    ledger.record(EntryKind.CONSUMPTION, "100", idempotency_key="something-else")
    assert ledger.balance() == Decimal(0)

    # The authorisation is unchanged, and settling it still works.
    assert granted.tier is EffortTier.HIGH
    assert settle(ledger, granted, _reviewed()) is not None


def test_running_out_queues_rather_than_denying() -> None:
    """Queued means retry later, not "your task died".

    The name matters: a caller who reads `Denied` surfaces an error, and the
    work was never started rather than failed.
    """
    decision = authorise(Decimal("0.1"), EffortTier.MAX, idempotency_key=_KEY)
    assert isinstance(decision, Queued)
    assert decision.retry_after == RETRY_AFTER
    assert "will run on its own" in decision.sentence


def test_the_queued_message_says_the_build_already_had_an_answer() -> None:
    """`REQ-008` in the wording, not only in the types.

    Somebody reading this needs to know their build was not held up, or they
    will treat a queue as an outage.
    """
    decision = authorise(Decimal(0), EffortTier.LOW, idempotency_key=_KEY)
    assert isinstance(decision, Queued)
    assert "deterministic tier is unaffected" in decision.sentence


def test_the_retry_window_is_not_shorter_than_credit_can_arrive() -> None:
    """Credits accrue hourly. Asking somebody to retry sooner is asking for nothing."""
    assert dt.timedelta(hours=1) <= RETRY_AFTER


# ─── "Degrade, never hard-cut" ───────────────────────────────────────────────


def test_an_affordable_request_is_granted_as_asked() -> None:
    granted = authorise(Decimal(100), EffortTier.MAX, idempotency_key=_KEY)
    assert isinstance(granted, Authorisation)
    assert granted.tier is EffortTier.MAX
    assert not granted.degraded


def test_an_unaffordable_request_downshifts_to_the_best_that_fits() -> None:
    """4 credits buys High, not Max."""
    granted = authorise(Decimal(4), EffortTier.MAX, idempotency_key=_KEY)
    assert isinstance(granted, Authorisation)
    assert granted.tier is EffortTier.HIGH
    assert granted.degraded


@pytest.mark.parametrize(
    ("balance", "expected"),
    [
        ("16", EffortTier.MAX),
        ("15.9999", EffortTier.HIGH),
        ("4", EffortTier.HIGH),
        ("3.9999", EffortTier.MEDIUM),
        ("1", EffortTier.MEDIUM),
        ("0.9999", EffortTier.LOW),
        ("0.25", EffortTier.LOW),
    ],
)
def test_the_downshift_walks_the_tiers_in_order(balance: str, expected: EffortTier) -> None:
    granted = authorise(Decimal(balance), EffortTier.MAX, idempotency_key=_KEY)
    assert isinstance(granted, Authorisation)
    assert granted.tier is expected


def test_a_downshift_never_upgrades_beyond_what_was_asked() -> None:
    """A rich balance does not buy a caller a tier they did not request.

    Effort is *model size × reasoning depth × review passes*, so a silent upgrade
    spends somebody's credit on work they did not ask for.
    """
    granted = authorise(Decimal(1000), EffortTier.LOW, idempotency_key=_KEY)
    assert isinstance(granted, Authorisation)
    assert granted.tier is EffortTier.LOW
    assert granted.cost == TIER_COST[EffortTier.LOW]


def test_a_degraded_authorisation_says_so() -> None:
    """A Low verdict presented as a Max verdict is the same dishonesty as a truncated one."""
    granted = authorise(Decimal("0.5"), EffortTier.MAX, idempotency_key=_KEY)
    assert isinstance(granted, Authorisation)
    assert granted.degraded
    assert granted.requested is EffortTier.MAX
    assert granted.tier is EffortTier.LOW


def test_the_tier_order_is_cheapest_first_and_strictly_increasing() -> None:
    """The order is the downshift policy, so it is asserted rather than assumed."""
    costs = [TIER_COST[tier] for tier in TIER_ORDER]
    assert costs == sorted(costs)
    assert len(set(costs)) == len(costs)


def test_affordable_tiers_reports_what_a_balance_covers() -> None:
    assert affordable_tiers(Decimal(0)) == ()
    assert affordable_tiers(Decimal(1)) == (EffortTier.LOW, EffortTier.MEDIUM)
    assert affordable_tiers(Decimal(1000)) == TIER_ORDER


# ─── "Never changes a build result" ──────────────────────────────────────────


def test_the_gateway_produces_no_verdict_of_its_own() -> None:
    """`REQ-008`, asserted as the absence of a second result type.

    Nothing here returns findings. A review returns the semantic tier's existing
    `ReviewResult`, which has no field a build could fail on — and building a
    parallel type is exactly how that guarantee would quietly acquire a
    `blocking` flag.
    """
    import dataclasses

    import governova_gateway

    # Checked against the module's actual types rather than its text. The first
    # version searched the source for "blocking" and failed on the docstring
    # explaining why there is no such field — a test that fails for saying the
    # right thing is a test people delete.
    own_types = [
        value
        for value in vars(governova_gateway).values()
        if dataclasses.is_dataclass(value)
        and getattr(value, "__module__", "") == "governova_gateway"
    ]
    assert own_types, "this test is meaningless if it inspects nothing"

    for declared in own_types:
        fields = {f.name for f in dataclasses.fields(declared)}
        assert not fields & {"findings", "blocking", "fatal", "exit_code", "severity"}, (
            f"{declared.__name__} carries a verdict; the Gateway must not produce one"
        )

    assert governova_gateway.ReviewResult is ReviewResult, (
        "the Gateway must reuse the semantic tier's result rather than define one"
    )


def test_the_semantic_result_has_nothing_a_build_could_fail_on() -> None:
    """The property the reuse inherits, checked rather than assumed."""
    import dataclasses

    fields = {f.name for f in dataclasses.fields(ReviewResult)}
    assert not fields & {"blocking", "fatal", "exit_code", "fails_build", "severity"}


# ─── Billing honesty ─────────────────────────────────────────────────────────


def test_a_completed_review_is_charged_once() -> None:
    ledger = _ledger("100")
    granted = authorise(ledger.balance(), EffortTier.HIGH, idempotency_key=_KEY)
    assert isinstance(granted, Authorisation)

    written = settle(ledger, granted, _reviewed())
    assert written is not None and written.created
    assert ledger.balance() == Decimal(96)


def test_an_outage_is_not_charged() -> None:
    """`ADR-010` §4 — a Gateway outage degrades the build and says so.

    Charging for the attempt would make an outage a revenue event, and the
    customer would pay for the absence of the thing they bought.
    """
    ledger = _ledger("100")
    granted = authorise(ledger.balance(), EffortTier.MAX, idempotency_key=_KEY)
    assert isinstance(granted, Authorisation)

    assert settle(ledger, granted, _outage()) is None
    assert ledger.balance() == Decimal(100)
    assert ledger.entries[-1].kind is EntryKind.GRANT


@pytest.mark.parametrize(
    "outcome",
    [Outcome.UNAVAILABLE, Outcome.UNPARSEABLE, Outcome.INACTIVE, Outcome.NOT_GROUNDED],
)
def test_nothing_that_failed_to_review_is_charged(outcome: Outcome) -> None:
    """A 200 with no readable verdict is as unreviewed as an unreachable endpoint.

    `NOT_GROUNDED` is here too: no standard was relevant, so nothing was asked.
    Billing for a question nobody put is the same as billing for an outage.
    """
    ledger = _ledger("100")
    granted = authorise(ledger.balance(), EffortTier.LOW, idempotency_key=_KEY)
    assert isinstance(granted, Authorisation)

    assert settle(ledger, granted, ReviewResult(outcome=outcome)) is None
    assert ledger.balance() == Decimal(100)


def test_a_retried_review_charges_once() -> None:
    """`S2.34`. The authorisation carries the key, so a retry cannot double-charge."""
    ledger = _ledger("100")
    granted = authorise(ledger.balance(), EffortTier.HIGH, idempotency_key=_KEY)
    assert isinstance(granted, Authorisation)

    first = settle(ledger, granted, _reviewed())
    again = settle(ledger, granted, _reviewed())

    assert first is not None and first.created
    assert again is not None and again.replayed
    assert ledger.balance() == Decimal(96)


def test_an_authorisation_without_a_key_is_refused() -> None:
    """Without one a retried review charges twice, which is the defect that matters."""
    with pytest.raises(ValueError, match=r"idempotency|S2.34"):
        authorise(Decimal(100), EffortTier.LOW, idempotency_key="")


def test_the_charge_records_the_degradation() -> None:
    """An invoice line that says Max for a Low review is a bill nobody can check."""
    ledger = _ledger("1")
    granted = authorise(ledger.balance(), EffortTier.MAX, idempotency_key=_KEY)
    assert isinstance(granted, Authorisation)

    written = settle(ledger, granted, _reviewed())
    assert written is not None
    assert "requested max" in written.entry.detail


def test_every_tier_price_is_decimal() -> None:
    """`AP-S5.28a`. A float here would be the product violating what it sells."""
    assert all(isinstance(cost, Decimal) for cost in TIER_COST.values())
    assert set(TIER_COST) == set(TIER_ORDER)
