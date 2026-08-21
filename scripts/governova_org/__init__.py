"""Organisations, seats and roles — the rules the schema cannot state.

A database enforces shape, and where it can enforce a rule it should: the
cross-organisation invariant `governova schema` surfaced is held by a composite
foreign key, not by anything here (see `platform/cloud/prisma/README.md`).

What is left are the rules a schema genuinely cannot state — "an organisation
always has an owner", "a seat is counted from assignment rather than headcount" —
and the query paths that keep the fan trap at `Organisation` unreachable.

Pure functions over plain values, because the alternative is that they can only
be tested against a live PostgreSQL, and an invariant that is expensive to test
is an invariant that stops being tested.

Nothing here talks to a database. Stage 1's persistence layer calls into this;
the rules do not know it exists.
"""

from __future__ import annotations

import dataclasses
import datetime as dt
from collections.abc import Iterable, Iterator
from enum import StrEnum
from typing import Protocol, runtime_checkable


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


@dataclasses.dataclass(frozen=True)
class TeamMembership:
    """A person's place on a team.

    `organisation_id` is carried here because the database carries it: both
    foreign keys are composite on `(organisation_id, id)`, which is what makes a
    team in one organisation and a membership in another unable to satisfy them
    at the same time. The column is a denormalisation and is recorded as one in
    `platform/cloud/prisma/schema.prisma` (`S14.8`).
    """

    id: str
    organisation_id: str
    team_id: str
    membership_id: str
    deleted_at: dt.datetime | None = None


@runtime_checkable
class SoftDeletable(Protocol):
    """Anything carrying `deleted_at`. Every model here does (`S5.34`).

    Declared read-only. A plain attribute annotation describes a *mutable* one,
    which a frozen dataclass does not structurally satisfy — and every model here
    is frozen, because a record that can be edited in place is a record whose
    history is a guess.
    """

    @property
    def deleted_at(self) -> dt.datetime | None: ...


@dataclasses.dataclass(frozen=True)
class Active[T: SoftDeletable]:
    """Records that have been filtered, in a type that cannot hold a deleted one.

    `S5.22`'s own anti-pattern is a query that forgot `deleted_at IS NULL` — the
    deleted record reappears in whichever query forgot, and only in that one. A
    free `active()` helper does not prevent that: it relies on every caller
    remembering to call it, and the first version of this module proved the point.
    `assign_seat` and `change_role` both took a raw list, and both would happily
    give a seat to a removed member or promote them to admin, because the only
    thing standing between them and a deleted row was that somebody had thought
    to filter.

    So the filter is carried by the **type**. A function that must not see
    deleted rows asks for `Active[Membership]`, and a raw list will not type-check
    where one is wanted. `__post_init__` then makes it true rather than merely
    conventional: an `Active` containing a deleted record cannot be constructed
    at all, including by a caller who bypasses `active()` and builds one directly.

    This is the same choice as the composite foreign key one layer down. A rule
    the system cannot break beats a rule everybody is asked to remember.
    """

    records: tuple[T, ...]

    def __post_init__(self) -> None:
        deleted = [r for r in self.records if r.deleted_at is not None]
        if deleted:
            raise OrgRuleError(
                f"{len(deleted)} deleted record(s) were put into an Active set. "
                "Build one with `active()`, which filters; constructing it "
                "directly is only for records already known to be live."
            )

    def __iter__(self) -> Iterator[T]:
        return iter(self.records)

    def __len__(self) -> int:
        return len(self.records)

    def __contains__(self, record: object) -> bool:
        return record in self.records


def active[T: SoftDeletable](records: Iterable[T]) -> Active[T]:
    """The only way to get an `Active` from records of unknown state.

    `S5.22` — `deleted_at IS NULL`, applied once, in the one place that is easy
    to find and impossible to skip on the way to a function that needs it.
    """
    return Active(tuple(record for record in records if record.deleted_at is None))


def seats_in_use(memberships: Active[Membership]) -> int:
    """How many seats an organisation is currently paying for."""
    return sum(1 for m in memberships if m.occupies_a_seat)


def assign_seat(
    organisation: Organisation,
    memberships: Active[Membership],
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


def release_seat(memberships: Active[Membership], membership_id: str) -> Membership:
    """Take a seat back. Idempotent — releasing an empty seat is not an error."""
    return dataclasses.replace(_member(memberships, membership_id), seat_assigned_at=None)


def change_role(
    memberships: Active[Membership], membership_id: str, role: MemberRole
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
        m for m in memberships if m.role is MemberRole.OWNER and m.id != membership_id
    ]
    if not other_owners:
        raise OrgRuleError(
            "This is the only owner. An organisation with no owner cannot grant "
            "access or change its billing, and cannot recover without support. "
            "Make somebody else an owner first."
        )
    return dataclasses.replace(target, role=role)


def remove_member(
    memberships: Active[Membership], membership_id: str, *, now: dt.datetime | None = None
) -> Membership:
    """Soft-delete a membership, subject to the same last-owner rule.

    Soft rather than hard (`S5.8`): a hard delete is irreversible and takes the
    audit trail with it.
    """
    target = _member(memberships, membership_id)
    if target.role is MemberRole.OWNER:
        other_owners = [
            m for m in memberships if m.role is MemberRole.OWNER and m.id != membership_id
        ]
        if not other_owners:
            raise OrgRuleError(
                "This is the only owner. Make somebody else an owner before "
                "removing them."
            )
    return dataclasses.replace(
        target, deleted_at=now or dt.datetime.now(dt.UTC), seat_assigned_at=None
    )


def add_to_team(team: Team, membership: Membership, *, identifier: str = "") -> TeamMembership:
    """Put a member on a team, refusing what the database would refuse.

    **The cross-organisation case is prevented by the schema, not by this.** Both
    of `TeamMembership`'s foreign keys are composite on `(organisation_id, id)`
    and share the one column, so a team in organisation A and a membership in
    organisation B cannot both satisfy them. An application check is not what
    holds that invariant — a migration, a bulk import, a support script or a
    direct `INSERT` all bypass application code, and every one of those is an
    ordinary thing to do to a production database.

    This check remains so the refusal arrives as a sentence rather than as a
    foreign-key violation from the driver, and so it is testable without a live
    PostgreSQL. It agrees with the constraint; it does not substitute for it.
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
    return TeamMembership(
        id=identifier or f"{team.id}:{membership.id}",
        organisation_id=team.organisation_id,
        team_id=team.id,
        membership_id=membership.id,
    )


# ── The fan trap, resolved rather than described ─────────────────────────────
#
# `governova schema` reports `Organisation` as the one side of both `Membership`
# and `Team`. A query that joins those two through the organisation multiplies
# them: ten members and four teams return forty rows, and any COUNT or SUM over
# that is wrong.
#
# The shape cannot be removed — an organisation genuinely has both — so the trap
# is resolved where it can be: **nothing has to write that join.** Every question
# somebody would reach for it to answer is answered below, by a path that does
# not fan. `test_org.py` builds the ten-by-four case and shows the naive join
# returning 40 beside these returning 10 and 4.


def members_of(
    organisation: Organisation, memberships: Iterable[Membership]
) -> Active[Membership]:
    """Active memberships of one organisation. Never joined through teams.

    Takes raw records and returns an `Active` — this is one of the boundaries
    where unfiltered rows arrive from storage and stop being unfiltered.
    """
    return active(m for m in memberships if m.organisation_id == organisation.id)


def teams_of(organisation: Organisation, teams: Iterable[Team]) -> Active[Team]:
    """Active teams of one organisation. Never joined through memberships."""
    return active(t for t in teams if t.organisation_id == organisation.id)


def members_of_team(
    team: Team, links: Iterable[TeamMembership], memberships: Iterable[Membership]
) -> Active[Membership]:
    """Members on one team, by the path that does not fan.

    `Team → TeamMembership → Membership` is the real relationship. Reaching the
    same set through `Organisation` is what multiplies rows, and it is also
    wrong: it would return every member of the organisation rather than every
    member of the team.
    """
    on_team = {link.membership_id for link in active(links) if link.team_id == team.id}
    return active(m for m in memberships if m.id in on_team)


def _member(memberships: Active[Membership], membership_id: str) -> Membership:
    for membership in memberships:
        if membership.id == membership_id:
            return membership
    raise OrgRuleError(f"no membership {membership_id} in this organisation")
