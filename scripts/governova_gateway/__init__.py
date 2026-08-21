"""The Intelligence Gateway — the metered path to the semantic tier.

The first paid capability that touches user code, which is why `ADR-010` §4
states its contract before it is built. Three of those clauses are guarantees
about what the Gateway *cannot* do, and each is expressed here as something the
type system refuses rather than something the code remembers.

**It never terminates a review mid-task.** *"A governance verdict truncated
halfway is worse than one not attempted — it looks like a result."* So the budget
decision happens once, before any work starts, and produces a value. There is no
call to check a balance during a review, and `Decision` has exactly two members:
proceed, or wait. **There is no way to spell "abort".**

**It never changes a build result.** `REQ-008`. Nothing here produces a verdict
of its own — a review returns `governova_semantic.ReviewResult`, which carries
findings and an outcome and has no field a build could fail on. Building a second
result type is how that guarantee would quietly acquire a `blocking` flag.

**It degrades rather than cutting.** Approaching the cap the requested tier
downshifts, and only when the cheapest tier is unaffordable does the work queue.
Queued means *retry later*, not *your task died*.

And one about honesty in billing: **a review that did not happen is not charged.**
`ADR-010` §4 says a Gateway outage degrades a build to the deterministic tier and
says so. Charging for the attempt would make an outage a revenue event.
"""

from __future__ import annotations

import dataclasses
import datetime as dt
from decimal import Decimal
from enum import StrEnum

from governova_ledger import EntryKind, Ledger, Written
from governova_semantic import ReviewResult


class EffortTier(StrEnum):
    """*Model size × reasoning depth × review passes* (`ADR-010` §4).

    A tier is a **declared intent**. Which model serves it is ours to change as
    models change; the price of a tier is not. That separation is what lets the
    fleet move without repricing anybody's subscription.
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAX = "max"


# Cheapest first. Downshifting walks this backwards from the requested tier, so
# the order is the policy and not an implementation detail.
TIER_ORDER: tuple[EffortTier, ...] = (
    EffortTier.LOW,
    EffortTier.MEDIUM,
    EffortTier.HIGH,
    EffortTier.MAX,
)

# Credits per review. `Decimal` throughout — `AP-S5.28a`, which this repository
# blocks builds for, and the ledger refuses a float at its boundary anyway.
TIER_COST: dict[EffortTier, Decimal] = {
    EffortTier.LOW: Decimal("0.25"),
    EffortTier.MEDIUM: Decimal("1"),
    EffortTier.HIGH: Decimal("4"),
    EffortTier.MAX: Decimal("16"),
}

# How long a queued caller is asked to wait. One hour, because that is the
# accrual period (`ADR-010` §4) — telling somebody to retry sooner than any
# credit can possibly arrive is telling them to retry for nothing.
RETRY_AFTER = dt.timedelta(hours=1)


@dataclasses.dataclass(frozen=True)
class Authorisation:
    """Permission to run one review, at a tier that is already affordable.

    Holding one of these means the decision is made. Nothing re-checks the
    balance while the review runs, which is what makes "never terminate
    mid-task" a property of the design rather than a rule somebody follows.
    """

    tier: EffortTier
    cost: Decimal
    requested: EffortTier
    idempotency_key: str

    @property
    def degraded(self) -> bool:
        """Whether the caller is getting less than they asked for.

        Reported rather than hidden. A verdict produced at Low when the caller
        asked for Max is a weaker verdict, and presenting it as though it were
        what they requested is the same class of dishonesty as a truncated one.
        """
        return self.tier is not self.requested


@dataclasses.dataclass(frozen=True)
class Queued:
    """Not enough credit for even the cheapest tier. Retry later.

    Deliberately not named `Denied` or `Rejected`. The caller's work is not
    finished or failed — it has not started, and it will run when credit
    accrues. A name that implied otherwise would invite a caller to treat this
    as an error and surface it as one.
    """

    shortfall: Decimal
    cheapest: EffortTier
    retry_after: dt.timedelta = RETRY_AFTER

    @property
    def sentence(self) -> str:
        return (
            f"not enough credit for a {self.cheapest} review — {self.shortfall} short. "
            f"Credits accrue hourly; this will run on its own. The deterministic "
            f"tier is unaffected and has already reported."
        )


# Exactly two outcomes. There is no third member and there must never be one:
# `ADR-010` §4 forbids terminating a review mid-task, and the way that guarantee
# survives contact with future changes is that there is no way to express it.
type Decision = Authorisation | Queued


def authorise(
    balance: Decimal,
    requested: EffortTier,
    *,
    idempotency_key: str,
) -> Decision:
    """Decide once, before any work begins.

    Walks down from the requested tier to the cheapest one the balance covers.
    Only when nothing is affordable does the work queue.

    The balance is a value, not a source consulted later. That is the whole
    mechanism behind "never terminate mid-task": there is no point in the review
    at which this is asked again, so there is no point at which the answer can
    change underneath it.
    """
    if not idempotency_key:
        raise ValueError(
            "a Gateway authorisation carries the key its consumption will be "
            "recorded under (S2.34). Without it a retried review charges twice."
        )

    ceiling = TIER_ORDER.index(requested)
    for tier in reversed(TIER_ORDER[: ceiling + 1]):
        cost = TIER_COST[tier]
        if balance >= cost:
            return Authorisation(
                tier=tier, cost=cost, requested=requested, idempotency_key=idempotency_key
            )

    cheapest = TIER_ORDER[0]
    return Queued(shortfall=TIER_COST[cheapest] - balance, cheapest=cheapest)


def settle(
    ledger: Ledger,
    authorisation: Authorisation,
    result: ReviewResult,
) -> Written | None:
    """Charge for a review that produced a verdict. Charge nothing otherwise.

    `ADR-010` §4: a Gateway outage degrades a build to the deterministic tier and
    says so. Charging for the attempt would make an outage a revenue event, and
    the customer would be paying for the absence of the thing they bought.

    `ReviewResult.ran` is the existing distinction between "reviewed and found
    nothing" and "did not review", which the semantic tier already had to draw
    for exactly this kind of reason. Returns None when nothing was charged, so a
    caller cannot mistake a free outage for a completed billing.
    """
    if not result.ran:
        return None
    return ledger.record(
        EntryKind.CONSUMPTION,
        authorisation.cost,
        idempotency_key=authorisation.idempotency_key,
        detail=(
            f"{authorisation.tier} review"
            + (f" (requested {authorisation.requested})" if authorisation.degraded else "")
        ),
    )


def affordable_tiers(balance: Decimal) -> tuple[EffortTier, ...]:
    """Which tiers this balance covers, cheapest first. For showing a caller."""
    return tuple(tier for tier in TIER_ORDER if balance >= TIER_COST[tier])
