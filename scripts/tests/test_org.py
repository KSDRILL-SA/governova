"""Tests for the organisation rules — the invariants the schema cannot state.

Every rule here exists because a database cannot enforce it. One of them exists
because `governova schema`, run on our own model, said so.
"""

from __future__ import annotations

import dataclasses
import datetime as dt

import pytest
from governova_org import (
    MemberRole,
    Membership,
    OperatingMode,
    Organisation,
    OrgRuleError,
    Team,
    active,
    add_to_team,
    assign_seat,
    change_role,
    members_of,
    members_of_team,
    release_seat,
    remove_member,
    seats_in_use,
    teams_of,
)

_NOW = dt.datetime(2026, 8, 21, tzinfo=dt.UTC)


def _org(seats: int = 3) -> Organisation:
    return Organisation(
        id="org-1", slug="ksdrill", name="KSDRILL SA", mode=OperatingMode.TEAM, seats_purchased=seats
    )


def _member(
    identifier: str,
    role: MemberRole = MemberRole.MEMBER,
    *,
    seated: bool = False,
    deleted: bool = False,
    organisation_id: str = "org-1",
) -> Membership:
    return Membership(
        id=identifier,
        organisation_id=organisation_id,
        account_id=f"account-{identifier}",
        role=role,
        seat_assigned_at=_NOW if seated else None,
        deleted_at=_NOW if deleted else None,
    )


# ─── Soft delete ─────────────────────────────────────────────────────────────


def test_deleted_rows_are_not_returned() -> None:
    """`S5.22`. Its own anti-pattern is the query that forgot the filter."""
    rows = [_member("a"), _member("b", deleted=True), _member("c")]
    assert [m.id for m in active(rows)] == ["a", "c"]


def test_a_deleted_membership_occupies_no_seat() -> None:
    """Otherwise removing somebody keeps charging for them."""
    assert not _member("a", seated=True, deleted=True).occupies_a_seat


# ─── Seats ───────────────────────────────────────────────────────────────────


def test_seats_are_counted_from_assignment_not_from_headcount() -> None:
    """A membership without a seat costs nothing — that is the billing unit."""
    rows = [_member("a", seated=True), _member("b"), _member("c", seated=True)]
    assert seats_in_use(rows) == 2


def test_a_seat_is_assigned_when_one_is_free() -> None:
    rows = [_member("a", seated=True), _member("b")]
    assert assign_seat(_org(seats=2), rows, "b", now=_NOW).occupies_a_seat


def test_assigning_a_seat_that_is_already_held_changes_nothing() -> None:
    """Idempotent. A double-click must not consume two seats."""
    rows = [_member("a", seated=True)]
    assert assign_seat(_org(seats=1), rows, "a").seat_assigned_at == _NOW


def test_running_out_of_seats_refuses_with_the_numbers() -> None:
    """"No seats available" makes the administrator go and find out what this knew."""
    rows = [_member("a", seated=True), _member("b", seated=True), _member("c")]
    with pytest.raises(OrgRuleError) as caught:
        assign_seat(_org(seats=2), rows, "c")
    message = str(caught.value)
    assert "2 seat(s)" in message
    assert "all 2 are in use" in message


def test_releasing_a_seat_frees_it_for_somebody_else() -> None:
    rows = [_member("a", seated=True), _member("b")]
    released = release_seat(rows, "a")
    rows = [released, rows[1]]
    assert seats_in_use(rows) == 0
    assert assign_seat(_org(seats=1), rows, "b").occupies_a_seat


def test_releasing_a_seat_nobody_holds_is_not_an_error() -> None:
    assert release_seat([_member("a")], "a").seat_assigned_at is None


def test_an_unknown_membership_is_refused_by_name() -> None:
    with pytest.raises(OrgRuleError, match="ghost"):
        assign_seat(_org(), [_member("a")], "ghost")


# ─── The last owner ──────────────────────────────────────────────────────────


def test_the_last_owner_cannot_demote_themselves() -> None:
    """Reachable by one ordinary action, and unrecoverable without support.

    An organisation with no owner cannot grant anyone access and cannot change
    its own billing.
    """
    rows = [_member("a", MemberRole.OWNER), _member("b", MemberRole.ADMIN)]
    with pytest.raises(OrgRuleError, match="only owner"):
        change_role(rows, "a", MemberRole.ADMIN)


def test_an_owner_can_step_down_once_somebody_else_is_an_owner() -> None:
    rows = [_member("a", MemberRole.OWNER), _member("b", MemberRole.OWNER)]
    assert change_role(rows, "a", MemberRole.MEMBER).role is MemberRole.MEMBER


def test_a_deleted_owner_does_not_count_as_cover() -> None:
    """The check reads active memberships, or a removed owner keeps the seat warm."""
    rows = [
        _member("a", MemberRole.OWNER),
        _member("b", MemberRole.OWNER, deleted=True),
    ]
    with pytest.raises(OrgRuleError, match="only owner"):
        change_role(rows, "a", MemberRole.MEMBER)


def test_promoting_somebody_to_owner_is_never_blocked() -> None:
    rows = [_member("a", MemberRole.OWNER), _member("b")]
    assert change_role(rows, "b", MemberRole.OWNER).role is MemberRole.OWNER


def test_the_last_owner_cannot_be_removed() -> None:
    rows = [_member("a", MemberRole.OWNER), _member("b")]
    with pytest.raises(OrgRuleError, match="only owner"):
        remove_member(rows, "a")


def test_removing_a_member_is_a_soft_delete_that_frees_their_seat() -> None:
    """`S5.8` — a hard delete is irreversible and takes the audit trail with it."""
    rows = [_member("a", MemberRole.OWNER), _member("b", seated=True)]
    removed = remove_member(rows, "b", now=_NOW)
    assert removed.deleted_at == _NOW
    assert removed.seat_assigned_at is None
    assert not removed.occupies_a_seat


# ─── The invariant `governova schema` found ──────────────────────────────────


def test_a_team_cannot_take_a_member_from_another_organisation() -> None:
    """The soundness gap the analyser reported against our own model.

    `TeamMembership` reaches an organisation by two paths — through its team and
    through its membership — and PostgreSQL cannot require them to agree without
    carrying `organisation_id` through both sides as part of a composite key.
    That denormalisation was declined, so this is where the invariant lives.
    """
    team = Team(id="team-1", organisation_id="org-1", name="Platform")
    outsider = _member("x", organisation_id="org-2")

    with pytest.raises(OrgRuleError) as caught:
        add_to_team(team, outsider)
    assert "org-1" in str(caught.value)
    assert "org-2" in str(caught.value)


def test_a_team_takes_a_member_of_its_own_organisation() -> None:
    add_to_team(Team(id="team-1", organisation_id="org-1", name="Platform"), _member("a"))


def test_a_deleted_team_takes_nobody() -> None:
    team = Team(id="team-1", organisation_id="org-1", name="Platform", deleted_at=_NOW)
    with pytest.raises(OrgRuleError, match="deleted"):
        add_to_team(team, _member("a"))


def test_a_removed_member_joins_nothing() -> None:
    team = Team(id="team-1", organisation_id="org-1", name="Platform")
    with pytest.raises(OrgRuleError, match="removed"):
        add_to_team(team, _member("a", deleted=True))


# ─── Vocabulary ──────────────────────────────────────────────────────────────


def test_the_operating_modes_are_the_ones_the_vision_names() -> None:
    """`master.md` §16 — Personal, Team, Enterprise. Not a parallel vocabulary."""
    assert {m.value for m in OperatingMode} == {"PERSONAL", "TEAM", "ENTERPRISE"}


def test_a_role_is_not_an_operating_mode() -> None:
    """The mode belongs to the organisation; the role belongs to a person in it.

    Collapsing them is the mistake `#255` warns about — it would make "Enterprise"
    both a billing tier and a permission level.
    """
    assert {r.value for r in MemberRole}.isdisjoint({m.value for m in OperatingMode})


# ─── The fan trap, resolved rather than described ────────────────────────────


def _ten_by_four() -> tuple[Organisation, list[Membership], list[Team]]:
    """The shape the analyser warns about: 10 members and 4 teams in one org."""
    org = _org(seats=10)
    members = [_member(f"m{i}") for i in range(10)]
    teams = [Team(id=f"t{i}", organisation_id="org-1", name=f"Team {i}") for i in range(4)]
    return org, members, teams


def test_the_fanning_join_really_does_fan() -> None:
    """The finding is real, and this is the arithmetic behind it.

    Ten members and four teams joined through their shared organisation produce
    forty rows. Any COUNT or SUM over that is wrong, and it is wrong quietly —
    the query succeeds and returns a number.
    """
    org, members, teams = _ten_by_four()
    fanned = [
        (m, t)
        for m in members
        if m.organisation_id == org.id
        for t in teams
        if t.organisation_id == org.id
    ]
    assert len(fanned) == 40
    assert len(fanned) != len(members)


def test_the_supported_paths_do_not_fan() -> None:
    """Which is why nothing has to write that join.

    `S14.10` allows a fan trap to be resolved *or* documented. Documenting it
    leaves the next person to read the note; this makes the trap unreachable
    through the API they will actually use.
    """
    org, members, teams = _ten_by_four()
    assert len(members_of(org, members)) == 10
    assert len(teams_of(org, teams)) == 4


def test_team_members_are_reached_through_the_bridge_not_the_organisation() -> None:
    """`Team → TeamMembership → Membership` is the real relationship.

    Reaching the same set through the organisation does not merely fan — it
    returns every member of the organisation rather than every member of the
    team, which is a different and wrong answer.
    """
    org, members, teams = _ten_by_four()
    platform = teams[0]
    links = [add_to_team(platform, members[i]) for i in range(3)]

    on_team = members_of_team(platform, links, members)
    assert [m.id for m in on_team] == ["m0", "m1", "m2"]
    assert len(on_team) < len(members_of(org, members))


def test_a_removed_team_membership_is_not_counted() -> None:
    """`S5.22` again — the filter has to be on every path, including this one."""
    _, members, teams = _ten_by_four()
    platform = teams[0]
    links = [
        add_to_team(platform, members[0]),
        dataclasses.replace(add_to_team(platform, members[1]), deleted_at=_NOW),
    ]
    assert [m.id for m in members_of_team(platform, links, members)] == ["m0"]


# ─── The invariant, now held by the database ─────────────────────────────────


def test_a_team_membership_carries_the_organisation_the_composite_key_needs() -> None:
    """The column that makes the two foreign keys composite.

    Both of `TeamMembership`'s references are keyed on `(organisation_id, id)`
    and share the one column, so a team in organisation A and a membership in
    organisation B cannot both satisfy them. The invariant is impossible rather
    than merely checked — a migration, a bulk import or a direct INSERT cannot
    bypass a foreign key the way they bypass application code.
    """
    link = add_to_team(Team(id="t1", organisation_id="org-1", name="Platform"), _member("a"))
    assert link.organisation_id == "org-1"
    assert link.team_id == "t1"
    assert link.membership_id == "a"


def test_the_schema_keys_team_membership_on_the_organisation() -> None:
    """Read from the schema itself, so the code and the database cannot drift.

    If somebody simplifies these back to single-column references, the invariant
    silently stops being enforced and only this fails.
    """
    from governova_compile.discovery import resolve_repo_root

    schema = (
        resolve_repo_root() / "platform" / "cloud" / "prisma" / "schema.prisma"
    ).read_text(encoding="utf-8")
    block = schema.split("model TeamMembership {")[1].split("}")[0]

    assert "fields: [organisation_id, team_id]" in block
    assert "references: [organisation_id, id]" in block
    assert "fields: [organisation_id, membership_id]" in block
