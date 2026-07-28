"""Tests for the governance runtime — audit trail and relay state machine.

The audit tests concentrate on **tampering**, because an audit trail's only claim
is that it has not been altered. A test that appends a record and reads it back
proves nothing an ordinary log file could not also pass; the tests that matter are
the ones that edit, delete, reorder, and forge, and require the chain to notice.

The relay tests concentrate on **refusals**, for the same reason: the protocol's
value is entirely in what it prevents.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from governova_audit import (
    GENESIS_HASH,
    ActorKind,
    PermissionLevel,
    append,
    audit_path,
    completeness,
    read_records,
    verify,
)
from governova_relay import (
    RelayState,
    RelayViolationError,
    approve,
    assign,
    close_task,
    compliance,
    load,
    open_task,
    relay_path,
    submit,
)
from governova_score.compute import compute_score


def _seed(root: Path, n: int = 3) -> None:
    for i in range(n):
        append(
            root,
            actor="Maluleke Kurhula Success",
            actor_kind=ActorKind.HUMAN,
            permission_level=PermissionLevel.L4_APPROVE,
            action=f"action.{i}",
            subject=f"subject-{i}",
        )


def _rewrite(root: Path, lines: list[str]) -> None:
    audit_path(root).write_text("\n".join(lines) + "\n", encoding="utf-8")


def _lines(root: Path) -> list[str]:
    return [ln for ln in audit_path(root).read_text(encoding="utf-8").splitlines() if ln.strip()]


# ─── Audit trail — the happy path (necessary, not sufficient) ────────────────


def test_records_chain_to_their_predecessor(tmp_path: Path) -> None:
    _seed(tmp_path, 3)
    records = read_records(tmp_path)
    assert [r.seq for r in records] == [1, 2, 3]
    assert records[0].prev_hash == GENESIS_HASH
    assert records[1].prev_hash == records[0].record_hash
    assert records[2].prev_hash == records[1].record_hash
    assert verify(tmp_path).valid


def test_an_empty_or_missing_trail_is_valid_not_broken(tmp_path: Path) -> None:
    """No trail is an absence of evidence, not evidence of tampering."""
    result = verify(tmp_path)
    assert result.valid and result.records == 0


def test_hashing_is_canonical_and_platform_independent(tmp_path: Path) -> None:
    rec = append(
        tmp_path,
        actor="a",
        actor_kind=ActorKind.AI,
        permission_level=PermissionLevel.L3_IMPLEMENT,
        action="x",
        subject="y",
    )
    assert rec.record_hash == rec.compute_hash()
    assert len(rec.record_hash) == 64


# ─── Audit trail — tampering. This is the point. ─────────────────────────────


def test_editing_a_record_is_detected(tmp_path: Path) -> None:
    _seed(tmp_path, 3)
    lines = _lines(tmp_path)
    doctored = json.loads(lines[1])
    doctored["actor"] = "Someone Else"
    lines[1] = json.dumps(doctored, sort_keys=True, separators=(",", ":"))
    _rewrite(tmp_path, lines)

    result = verify(tmp_path)
    assert not result.valid
    assert any("altered after it was written" in i for i in result.issues)


def test_deleting_a_record_is_detected(tmp_path: Path) -> None:
    _seed(tmp_path, 4)
    lines = _lines(tmp_path)
    del lines[1]
    _rewrite(tmp_path, lines)

    result = verify(tmp_path)
    assert not result.valid
    assert any("chain link broken" in i for i in result.issues)
    assert any("sequence gap" in i for i in result.issues)


def test_reordering_records_is_detected(tmp_path: Path) -> None:
    _seed(tmp_path, 3)
    lines = _lines(tmp_path)
    lines[1], lines[2] = lines[2], lines[1]
    _rewrite(tmp_path, lines)
    assert not verify(tmp_path).valid


def test_truncating_the_head_is_detected(tmp_path: Path) -> None:
    """Removing the beginning leaves a record whose predecessor no longer exists."""
    _seed(tmp_path, 3)
    _rewrite(tmp_path, _lines(tmp_path)[1:])
    result = verify(tmp_path)
    assert not result.valid
    assert any("chain link broken" in i for i in result.issues)


def test_a_forged_record_with_a_recomputed_hash_still_breaks_the_chain(
    tmp_path: Path,
) -> None:
    """The hardest case: an attacker who understands the format.

    They edit a record and recompute *its* hash so it is self-consistent. The
    edit still breaks every following link, because those records committed to
    the original hash. This is what chaining buys over per-record checksums.
    """
    _seed(tmp_path, 3)
    lines = _lines(tmp_path)
    doctored = json.loads(lines[0])
    doctored["outcome"] = "approved"
    doctored.pop("record_hash")
    from governova_audit import AuditRecord

    forged = AuditRecord(**doctored)
    lines[0] = json.dumps(
        {**doctored, "record_hash": forged.compute_hash()},
        sort_keys=True,
        separators=(",", ":"),
    )
    _rewrite(tmp_path, lines)

    result = verify(tmp_path)
    assert not result.valid, "a self-consistent forgery must still break the chain"
    assert any("chain link broken" in i for i in result.issues)


def test_an_unreadable_line_is_reported_not_silently_skipped(tmp_path: Path) -> None:
    _seed(tmp_path, 2)
    _rewrite(tmp_path, [*_lines(tmp_path), "{ this is not json"])
    result = verify(tmp_path)
    assert not result.valid
    assert any("unreadable audit record" in i for i in result.issues)


def test_appending_after_tampering_does_not_repair_the_chain(tmp_path: Path) -> None:
    """A tampered trail stays broken — later good records cannot launder it."""
    _seed(tmp_path, 2)
    lines = _lines(tmp_path)
    doctored = json.loads(lines[0])
    doctored["subject"] = "changed"
    lines[0] = json.dumps(doctored, sort_keys=True, separators=(",", ":"))
    _rewrite(tmp_path, lines)
    _seed(tmp_path, 1)
    assert not verify(tmp_path).valid


def test_completeness_measures_attribution(tmp_path: Path) -> None:
    _seed(tmp_path, 2)
    assert completeness(tmp_path) == 100.0
    lines = _lines(tmp_path)
    stripped = json.loads(lines[0])
    stripped["actor"] = ""
    lines[0] = json.dumps(stripped, sort_keys=True, separators=(",", ":"))
    _rewrite(tmp_path, lines)
    assert completeness(tmp_path) == 50.0


# ─── Relay — the L4 boundary ─────────────────────────────────────────────────


def _run_to_submission(root: Path) -> None:
    open_task(root, task="Build auth", opened_by="Maluleke Kurhula Success")
    assign(root, engineer="engineer-02", permission_level=PermissionLevel.L3_IMPLEMENT)
    submit(root, engineer="engineer-02")


def test_an_ai_actor_cannot_approve(tmp_path: Path) -> None:
    """The load-bearing rule. L4 is permanently human-only."""
    _run_to_submission(tmp_path)
    with pytest.raises(RelayViolationError) as exc:
        approve(tmp_path, approver="engineer-02", actor_kind=ActorKind.AI)
    assert "human-only" in str(exc.value)
    assert exc.value.severity == "SEV1"


def test_a_refused_approval_does_not_change_state(tmp_path: Path) -> None:
    """A blocked breach must not half-apply."""
    _run_to_submission(tmp_path)
    with pytest.raises(RelayViolationError):
        approve(tmp_path, approver="engineer-02", actor_kind=ActorKind.AI)
    relay = load(tmp_path)
    assert relay.state == RelayState.AWAITING_APPROVAL
    assert relay.approvals == 0


def test_a_refused_approval_is_recorded_as_sev1(tmp_path: Path) -> None:
    """Refusing silently would lose the evidence that a tool tried."""
    _run_to_submission(tmp_path)
    with pytest.raises(RelayViolationError):
        approve(tmp_path, approver="engineer-02", actor_kind=ActorKind.AI)
    refusals = [r for r in read_records(tmp_path) if r.outcome == "REFUSED"]
    assert len(refusals) == 1
    assert refusals[0].permission_level == "L4"
    assert "SEV1" in refusals[0].detail
    assert load(tmp_path).violations


def test_a_system_actor_cannot_approve_either(tmp_path: Path) -> None:
    """'system' is not a loophole around 'human'."""
    _run_to_submission(tmp_path)
    with pytest.raises(RelayViolationError):
        approve(tmp_path, approver="ci-bot", actor_kind=ActorKind.SYSTEM)


def test_a_human_can_approve(tmp_path: Path) -> None:
    _run_to_submission(tmp_path)
    relay = approve(tmp_path, approver="Maluleke Kurhula Success", actor_kind=ActorKind.HUMAN)
    assert relay.approvals == 1 and relay.handoffs == 1
    assert relay.state == RelayState.IDLE
    assert relay.engineer is None


def test_no_engineer_may_be_assigned_at_l4(tmp_path: Path) -> None:
    open_task(tmp_path, task="t", opened_by="Founder")
    with pytest.raises(RelayViolationError, match="human-only"):
        assign(tmp_path, engineer="engineer-02", permission_level=PermissionLevel.L4_APPROVE)


def test_an_ai_actor_cannot_open_or_close_a_task(tmp_path: Path) -> None:
    with pytest.raises(RelayViolationError, match="human-only"):
        open_task(tmp_path, task="t", opened_by="engineer-02", actor_kind=ActorKind.AI)
    open_task(tmp_path, task="t", opened_by="Founder")
    with pytest.raises(RelayViolationError, match="human-only"):
        close_task(tmp_path, closed_by="engineer-02", actor_kind=ActorKind.AI)


# ─── Relay — linearity and the unskippable gate ──────────────────────────────


def test_two_engineers_cannot_hold_the_task(tmp_path: Path) -> None:
    open_task(tmp_path, task="t", opened_by="Founder")
    assign(tmp_path, engineer="engineer-02", permission_level=PermissionLevel.L3_IMPLEMENT)
    with pytest.raises(RelayViolationError, match="one engineer at a time"):
        assign(tmp_path, engineer="engineer-03", permission_level=PermissionLevel.L3_IMPLEMENT)


def test_the_next_engineer_cannot_start_before_l4_approval(tmp_path: Path) -> None:
    """The gate is unskippable — this is the whole point of the relay."""
    _run_to_submission(tmp_path)
    with pytest.raises(RelayViolationError, match="cannot be skipped"):
        assign(tmp_path, engineer="engineer-03", permission_level=PermissionLevel.L3_IMPLEMENT)


def test_an_engineer_cannot_submit_another_engineers_work(tmp_path: Path) -> None:
    open_task(tmp_path, task="t", opened_by="Founder")
    assign(tmp_path, engineer="engineer-02", permission_level=PermissionLevel.L3_IMPLEMENT)
    with pytest.raises(RelayViolationError):
        submit(tmp_path, engineer="engineer-03")


def test_an_engineer_cannot_be_assigned_before_a_task_is_opened(tmp_path: Path) -> None:
    with pytest.raises(RelayViolationError, match="before the task is opened"):
        assign(tmp_path, engineer="engineer-02", permission_level=PermissionLevel.L3_IMPLEMENT)


def test_a_task_with_work_awaiting_approval_cannot_be_closed(tmp_path: Path) -> None:
    _run_to_submission(tmp_path)
    with pytest.raises(RelayViolationError, match="awaiting approval"):
        close_task(tmp_path, closed_by="Founder", actor_kind=ActorKind.HUMAN)


def test_a_second_task_cannot_open_while_one_is_live(tmp_path: Path) -> None:
    open_task(tmp_path, task="one", opened_by="Founder")
    assign(tmp_path, engineer="engineer-02", permission_level=PermissionLevel.L3_IMPLEMENT)
    with pytest.raises(RelayViolationError, match="linear"):
        open_task(tmp_path, task="two", opened_by="Founder")


def test_a_full_relay_cycle_writes_a_verifiable_trail(tmp_path: Path) -> None:
    open_task(tmp_path, task="Build auth", opened_by="Founder")
    assign(tmp_path, engineer="engineer-02", permission_level=PermissionLevel.L3_IMPLEMENT)
    submit(tmp_path, engineer="engineer-02")
    approve(tmp_path, approver="Founder", actor_kind=ActorKind.HUMAN)
    assign(tmp_path, engineer="engineer-03", permission_level=PermissionLevel.L2_RECOMMEND)
    submit(tmp_path, engineer="engineer-03")
    approve(tmp_path, approver="Founder", actor_kind=ActorKind.HUMAN)
    close_task(tmp_path, closed_by="Founder", actor_kind=ActorKind.HUMAN)

    assert verify(tmp_path).valid
    actions = [r.action for r in read_records(tmp_path)]
    assert actions.count("relay.approve") == 2
    assert actions[-1] == "relay.close_task"
    assert load(tmp_path).handoffs == 2


# ─── Relay compliance scoring ────────────────────────────────────────────────


def test_compliance_is_unassessed_without_instrumentation(tmp_path: Path) -> None:
    score, detail = compliance(tmp_path)
    assert score is None and "requires runtime" in detail


def test_compliance_is_unassessed_before_the_first_handoff(tmp_path: Path) -> None:
    """An opened task is not yet evidence of compliance."""
    open_task(tmp_path, task="t", opened_by="Founder")
    score, _ = compliance(tmp_path)
    assert score is None


def test_full_compliance_when_every_handoff_was_approved(tmp_path: Path) -> None:
    _run_to_submission(tmp_path)
    approve(tmp_path, approver="Founder", actor_kind=ActorKind.HUMAN)
    score, _ = compliance(tmp_path)
    assert score == 100.0


def test_an_unapproved_submission_lowers_compliance(tmp_path: Path) -> None:
    _run_to_submission(tmp_path)
    approve(tmp_path, approver="Founder", actor_kind=ActorKind.HUMAN)
    assign(tmp_path, engineer="engineer-03", permission_level=PermissionLevel.L3_IMPLEMENT)
    submit(tmp_path, engineer="engineer-03")  # never approved
    score, _ = compliance(tmp_path)
    assert score == 50.0


def test_a_refused_l4_attempt_is_penalised(tmp_path: Path) -> None:
    """Correctly blocked, but the score must not read as clean."""
    _run_to_submission(tmp_path)
    with pytest.raises(RelayViolationError):
        approve(tmp_path, approver="engineer-02", actor_kind=ActorKind.AI)
    approve(tmp_path, approver="Founder", actor_kind=ActorKind.HUMAN)
    score, detail = compliance(tmp_path)
    assert score == 85.0
    assert "refused" in detail


# ─── Score integration ───────────────────────────────────────────────────────


def test_an_empty_audit_dir_no_longer_scores_full_marks(tmp_path: Path) -> None:
    """The regression this runtime exists to fix.

    Previously any file under governance/audit/ scored 100 on the factor whose
    purpose is proving records were not fabricated.
    """
    (tmp_path / "governance" / "audit").mkdir(parents=True)
    (tmp_path / "governance" / "audit" / "x").write_text("", encoding="utf-8")
    factor = next(f for f in compute_score(tmp_path).factors if f.key == "audit_trail")
    assert factor.score != 100.0


def test_a_tampered_trail_scores_zero_not_partial_credit(tmp_path: Path) -> None:
    _seed(tmp_path, 3)
    lines = _lines(tmp_path)
    doctored = json.loads(lines[1])
    doctored["outcome"] = "approved"
    lines[1] = json.dumps(doctored, sort_keys=True, separators=(",", ":"))
    _rewrite(tmp_path, lines)

    factor = next(f for f in compute_score(tmp_path).factors if f.key == "audit_trail")
    assert factor.score == 0.0
    assert "TAMPERED" in factor.detail


def test_an_intact_trail_and_relay_light_up_both_factors(tmp_path: Path) -> None:
    open_task(tmp_path, task="t", opened_by="Founder")
    assign(tmp_path, engineer="engineer-02", permission_level=PermissionLevel.L3_IMPLEMENT)
    submit(tmp_path, engineer="engineer-02")
    approve(tmp_path, approver="Founder", actor_kind=ActorKind.HUMAN)

    factors = {f.key: f for f in compute_score(tmp_path).factors}
    assert factors["audit_trail"].score == 100.0
    assert factors["relay_compliance"].score == 100.0
    assert relay_path(tmp_path).is_file()


def test_assessed_weight_rises_once_the_runtime_is_instrumented(tmp_path: Path) -> None:
    before = {f.key for f in compute_score(tmp_path).factors if f.score is not None}
    open_task(tmp_path, task="t", opened_by="Founder")
    assign(tmp_path, engineer="e2", permission_level=PermissionLevel.L3_IMPLEMENT)
    submit(tmp_path, engineer="e2")
    approve(tmp_path, approver="Founder", actor_kind=ActorKind.HUMAN)
    after = {f.key for f in compute_score(tmp_path).factors if f.score is not None}

    assert "relay_compliance" not in before and "audit_trail" not in before
    assert {"relay_compliance", "audit_trail"} <= after
