"""Organisations, seats and roles — the rules the schema cannot state.

A database enforces shape. It cannot enforce "an organisation always has an
owner", or "a team's members belong to that team's organisation", and the second
of those is a soundness gap `governova schema` reported against our own model
(see `platform/cloud/prisma/README.md`).

So the invariants live here, as pure functions over plain values, and every one
of them has a test. Pure because the alternative is that they can only be tested
against a live PostgreSQL, and an invariant that is expensive to test is an
invariant that stops being tested.

Nothing here talks to a database. Stage 1's persistence layer calls into this;
the rules do not know it exists.
"""

from __future__ import annotations

import dataclasses
import datetime as dt
from enum import StrEnum


class OperatingMode(StrEnum):
    """`master.md` §16. A property of the organisation, not of a person in it."""

    PERSONAL = "PERSONAL"
    TEAM = "TEAM"
    ENTERPRISE = "ENTERPRISE"


class MemberRole(StrEnum):
    """What a member may do. Distinct from the operating mode."""

    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"


class OrgRuleError(RuntimeError):
    """An organisation invariant that would have been broken, with the reason."""


@dataclasses.dataclass(frozen=True)
class Organisation:
    id: str
    slug: str
    name: str
    mode: OperatingMode = OperatingMode.PERSONAL
    seats_purchased: int = 1
    deleted_at: dt.datetime | None = None


@dataclasses.dataclass(frozen=True)
class Membership:
    id: str
    organisation_id: str
    account_id: str
    role: MemberRole = MemberRole.MEMBER
    seat_assigned_at: dt.datetime | None = None
    deleted_at: dt.datetime | None = None

    @property
    def occupies_a_seat(self) -> bool:
        """A membership without a seat costs nothing. That is the billing unit."""
        return self.seat_assigned_at is not None and self.deleted_at is None


@dataclasses.dataclass(frozen=True)
class Team:
    id: str
    organisation_id: str
    name: str
    deleted_at: dt.datetime | None = None


def active[T: (Organisation, Membership, Team)](records: list[T]) -> list[T]:
    """Only the rows a query should see. `S5.22` — `deleted_at IS NULL`.

    A free function rather than something callers remember, because `S5.22`'s own
    anti-pattern is a query that forgot the filter: the deleted record reappears
    in whichever query forgot, and only in that one.
    """
    return [record for record in records if record.deleted_at is None]


def seats_in_use(memberships: list[Membership]) -> int:
    """How many seats an organisation is currently paying for."""
    return sum(1 for m in memberships if m.occupies_a_seat)


def assign_seat(
    organisation: Organisation,
    memberships: list[Membership],
    membership_id: str,
    *,
    now: dt.datetime | None = None,
) -> Membership:
    """Give a member a seat, or refuse with the number that stopped it.

    Refusing with the count is deliberate: "no seats available" leaves the
    administrator to go and find out how many they have and how many are used,
    which is the information the refusal already had.
    """
    target = _member(memberships, membership_id)
    if target.occupies_a_seat:
        return target

    in_use = seats_in_use(memberships)
    if in_use >= organisation.seats_purchased:
        raise OrgRuleError(
            f"{organisation.name} has {organisation.seats_purchased} seat(s) and all "
            f"{in_use} are in use. Release one, or buy another."
        )
    return dataclasses.replace(target, seat_assigned_at=now or dt.datetime.now(dt.UTC))


def release_seat(memberships: list[Membership], membership_id: str) -> Membership:
    """Take a seat back. Idempotent — releasing an empty seat is not an error."""
    return dataclasses.replace(_member(memberships, membership_id), seat_assigned_at=None)


def change_role(
    memberships: list[Membership], membership_id: str, role: MemberRole
) -> Membership:
    """Change a member's role, unless it would leave nobody in charge.

    An organisation with no owner cannot grant anyone else access, cannot change
    its own billing, and cannot be recovered without support intervening. It is
    reachable by one ordinary action — the last owner demoting themselves — which
    is why it is checked here rather than trusted to a UI.
    """
    target = _member(memberships, membership_id)
    if target.role is not MemberRole.OWNER or role is MemberRole.OWNER:
        return dataclasses.replace(target, role=role)

    other_owners = [
        m
        for m in active(memberships)
        if m.role is MemberRole.OWNER and m.id != membership_id
    ]
    if not other_owners:
        raise OrgRuleError(
            "This is the only owner. An organisation with no owner cannot grant "
            "access or change its billing, and cannot recover without support. "
            "Make somebody else an owner first."
        )
    return dataclasses.replace(target, role=role)


def remove_member(memberships: list[Membership], membership_id: str, *, now: dt.datetime | None = None) -> Membership:
    """Soft-delete a membership, subject to the same last-owner rule.

    Soft rather than hard (`S5.8`): a hard delete is irreversible and takes the
    audit trail with it.
    """
    target = _member(memberships, membership_id)
    if target.role is MemberRole.OWNER:
        other_owners = [
            m for m in active(memberships) if m.role is MemberRole.OWNER and m.id != membership_id
        ]
        if not other_owners:
            raise OrgRuleError(
                "This is the only owner. Make somebody else an owner before "
                "removing them."
            )
    return dataclasses.replace(
        target, deleted_at=now or dt.datetime.now(dt.UTC), seat_assigned_at=None
    )


def add_to_team(team: Team, membership: Membership) -> None:
    """The invariant the schema cannot express.

    `governova schema` found two paths from `TeamMembership` to an organisation —
    through its team and through its membership — and nothing in PostgreSQL stops
    them disagreeing without carrying `organisation_id` through both sides as
    part of a composite key.

    That denormalisation was declined (`S14.8` requires it to be recorded and the
    cost here is higher than this check), so the invariant is enforced here and
    the reason is written down in `platform/cloud/prisma/README.md`.

    Raises rather than returning a value: there is no sensible partial result,
    and silently dropping the request is how a member ends up not in the team
    somebody added them to.
    """
    if team.deleted_at is not None:
        raise OrgRuleError(f"team {team.name} has been deleted")
    if membership.deleted_at is not None:
        raise OrgRuleError("that member has been removed from the organisation")
    if team.organisation_id != membership.organisation_id:
        raise OrgRuleError(
            f"team {team.name} belongs to organisation {team.organisation_id} and "
            f"that member belongs to {membership.organisation_id}. A team's members "
            "must belong to the team's own organisation."
        )


def _member(memberships: list[Membership], membership_id: str) -> Membership:
    for membership in memberships:
        if membership.id == membership_id:
            return membership
    raise OrgRuleError(f"no membership {membership_id} in this organisation")
