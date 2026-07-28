"""governova_relay — the relay state machine.

Implements the `relay-state-machine` engine component (`platform/engine/SPEC.md`)
and enforces `protocols/relay-protocol.md` §4 together with
`framework/permission-model.md`.

The protocol declares three things non-negotiable. This module makes them
mechanical rather than aspirational:

1. **One engineer at a time.** No parallel work — a second engineer cannot start
   while another holds the task.
2. **L4 approval between every handoff.** It cannot be skipped; the next engineer
   cannot start from an unapproved state.
3. **L4 is human-only, permanently.** An AI actor approving its own output is a
   SEV1 violation. This is refused *at the API boundary* rather than recorded
   afterwards — a control that only reports the breach it could have prevented is
   not a control. It cannot be elevated by argument, configuration, or flag,
   because there is no parameter that permits it.

Every transition writes to the audit trail, so relay history and audit history
cannot diverge: the relay's claim about what happened is the audit record.

State: `governance/relay/state.json` — the current position only. The history
lives in the audit trail, which is the tamper-evident record.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

from governova_audit import ActorKind, PermissionLevel, append, read_records

RELAY_RELATIVE_PATH = "governance/relay/state.json"


class RelayState(StrEnum):
    IDLE = "idle"  # no open task
    ASSIGNED = "assigned"  # an engineer holds the task
    AWAITING_APPROVAL = "awaiting_approval"  # work submitted, L4 review pending
    CLOSED = "closed"  # task closed by L4


class RelayViolationError(Exception):
    """A refused transition. Carries the severity the protocol assigns it."""

    def __init__(self, message: str, *, severity: str = "SEV1", standard: str = "S10.8") -> None:
        super().__init__(message)
        self.severity = severity
        self.standard = standard


@dataclass
class Relay:
    """The current relay position for one repository."""

    state: str = RelayState.IDLE
    task: str | None = None
    engineer: str | None = None
    permission_level: str | None = None
    opened_by: str | None = None
    opened_at: str | None = None
    handoffs: int = 0
    approvals: int = 0
    violations: list[str] = field(default_factory=list)


def relay_path(root: Path) -> Path:
    return root / RELAY_RELATIVE_PATH


def load(root: Path) -> Relay:
    path = relay_path(root)
    if not path.is_file():
        return Relay()
    try:
        return Relay(**json.loads(path.read_text(encoding="utf-8")))
    except (json.JSONDecodeError, TypeError):
        return Relay()


def save(root: Path, relay: Relay) -> None:
    path = relay_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(asdict(relay), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _record(
    root: Path,
    relay: Relay,
    *,
    actor: str,
    actor_kind: ActorKind,
    level: PermissionLevel,
    action: str,
    outcome: str,
    detail: str = "",
    standards: list[str] | None = None,
) -> None:
    append(
        root,
        actor=actor,
        actor_kind=actor_kind,
        permission_level=level,
        action=action,
        subject=relay.task or "—",
        outcome=outcome,
        standards=standards or ["S10.8"],
        detail=detail,
    )


def open_task(
    root: Path, *, task: str, opened_by: str, actor_kind: ActorKind | str = ActorKind.HUMAN
) -> Relay:
    """Open a task. L4 only — the Founder defines goal and done criteria (§4)."""
    if str(actor_kind) != ActorKind.HUMAN:
        raise RelayViolationError(
            f"'{opened_by}' is a {actor_kind} actor and cannot open a task — "
            f"task definition is an L4 act, and L4 is permanently human-only."
        )
    relay = load(root)
    if relay.state not in (RelayState.IDLE, RelayState.CLOSED):
        raise RelayViolationError(
            f"task '{relay.task}' is still open in state '{relay.state}'. "
            f"The relay is linear — close it before opening another.",
            severity="SEV2",
            standard="S10.9",
        )
    relay = Relay(
        state=RelayState.IDLE.value,  # open, but no engineer holds it yet
        task=task,
        opened_by=opened_by,
        opened_at=datetime.now(UTC).isoformat(timespec="seconds"),
    )
    save(root, relay)
    _record(
        root,
        relay,
        actor=opened_by,
        actor_kind=ActorKind.HUMAN,
        level=PermissionLevel.L4_APPROVE,
        action="relay.open_task",
        outcome="opened",
        detail=f"task opened: {task}",
    )
    return relay


def assign(
    root: Path,
    *,
    engineer: str,
    permission_level: PermissionLevel | str,
    actor_kind: ActorKind | str = ActorKind.AI,
) -> Relay:
    """Hand the task to an engineer. Refused if another engineer already holds it."""
    relay = load(root)
    if relay.state == RelayState.CLOSED or relay.task is None:
        raise RelayViolationError(
            "no open task — an engineer cannot be assigned before the task is opened by L4.",
            severity="SEV2",
            standard="S10.9",
        )
    if relay.state == RelayState.ASSIGNED:
        raise RelayViolationError(
            f"'{relay.engineer}' already holds this task. The relay is linear — "
            f"one engineer at a time, no parallel work (relay-protocol §4).",
            severity="SEV1",
            standard="S10.9",
        )
    if relay.state == RelayState.AWAITING_APPROVAL:
        raise RelayViolationError(
            f"'{relay.engineer}' submitted work that has not been approved. "
            f"L4 approval sits between every handoff and cannot be skipped.",
            severity="SEV1",
            standard="S10.8",
        )
    if str(permission_level) == PermissionLevel.L4_APPROVE:
        raise RelayViolationError(
            f"'{engineer}' cannot be assigned at L4 — L4 is approval authority, "
            f"not a working level, and is permanently human-only."
        )

    relay.state = RelayState.ASSIGNED.value
    relay.engineer = engineer
    relay.permission_level = str(permission_level)
    save(root, relay)
    _record(
        root,
        relay,
        actor=engineer,
        actor_kind=ActorKind(str(actor_kind)),
        level=PermissionLevel(str(permission_level)),
        action="relay.assign",
        outcome="assigned",
        detail=f"{engineer} holds the task at {permission_level}",
    )
    return relay


def submit(root: Path, *, engineer: str, detail: str = "") -> Relay:
    """Engineer submits work for L4 review."""
    relay = load(root)
    if relay.state != RelayState.ASSIGNED:
        raise RelayViolationError(
            f"cannot submit from state '{relay.state}' — no engineer holds the task.",
            severity="SEV2",
            standard="S10.9",
        )
    if relay.engineer != engineer:
        raise RelayViolationError(
            f"'{engineer}' cannot submit work held by '{relay.engineer}'.",
            severity="SEV1",
            standard="S10.9",
        )
    relay.state = RelayState.AWAITING_APPROVAL.value
    save(root, relay)
    _record(
        root,
        relay,
        actor=engineer,
        actor_kind=ActorKind.AI,
        level=PermissionLevel(relay.permission_level or PermissionLevel.L3_IMPLEMENT),
        action="relay.submit",
        outcome="awaiting_approval",
        detail=detail or f"{engineer} submitted work for L4 review",
    )
    return relay


def approve(
    root: Path, *, approver: str, actor_kind: ActorKind | str, detail: str = ""
) -> Relay:
    """L4 approval of the submitted work. **Human actors only, always.**

    The AI refusal below is the load-bearing line of this module. It is checked
    before any state is read or written, so a non-human approval cannot take
    effect even partially, and it is recorded as a SEV1 attempt.
    """
    if str(actor_kind) != ActorKind.HUMAN:
        relay = load(root)
        relay.violations.append(
            f"SEV1: {actor_kind} actor '{approver}' attempted L4 approval"
        )
        save(root, relay)
        _record(
            root,
            relay,
            actor=approver,
            actor_kind=ActorKind(str(actor_kind)),
            level=PermissionLevel.L4_APPROVE,
            action="relay.approve",
            outcome="REFUSED",
            detail=(
                "SEV1 — L4 is permanently human-only and cannot be delegated, "
                "elevated by prompt, or granted by configuration "
                "(framework/permission-model.md)."
            ),
        )
        raise RelayViolationError(
            f"'{approver}' is a {actor_kind} actor and cannot approve. L4 is "
            f"permanently human-only — an AI tool approving its own output is a "
            f"SEV1 violation."
        )

    relay = load(root)
    if relay.state != RelayState.AWAITING_APPROVAL:
        raise RelayViolationError(
            f"nothing is awaiting approval (state '{relay.state}').",
            severity="SEV2",
            standard="S10.9",
        )
    relay.state = RelayState.IDLE.value
    relay.approvals += 1
    relay.handoffs += 1
    relay.engineer = None
    relay.permission_level = None
    save(root, relay)
    _record(
        root,
        relay,
        actor=approver,
        actor_kind=ActorKind.HUMAN,
        level=PermissionLevel.L4_APPROVE,
        action="relay.approve",
        outcome="approved",
        detail=detail or "L4 approved the handoff",
    )
    return relay


def close_task(root: Path, *, closed_by: str, actor_kind: ActorKind | str) -> Relay:
    """Close the task. L4 only."""
    if str(actor_kind) != ActorKind.HUMAN:
        raise RelayViolationError(
            f"'{closed_by}' is a {actor_kind} actor and cannot close a task — "
            f"closing is an L4 act, and L4 is permanently human-only."
        )
    relay = load(root)
    if relay.task is None or relay.state == RelayState.CLOSED:
        raise RelayViolationError(
            "no open task to close.", severity="SEV3", standard="S10.9"
        )
    if relay.state == RelayState.AWAITING_APPROVAL:
        raise RelayViolationError(
            f"'{relay.engineer}' has work awaiting approval — approve or reject it "
            f"before closing the task.",
            severity="SEV2",
            standard="S10.8",
        )
    relay.state = RelayState.CLOSED.value
    relay.engineer = None
    relay.permission_level = None
    save(root, relay)
    _record(
        root,
        relay,
        actor=closed_by,
        actor_kind=ActorKind.HUMAN,
        level=PermissionLevel.L4_APPROVE,
        action="relay.close_task",
        outcome="closed",
        detail=f"task closed after {relay.handoffs} approved handoff(s)",
    )
    return relay


def compliance(root: Path) -> tuple[float | None, str]:
    """Relay compliance as a 0–100 score, or None when the relay is uninstrumented.

    Compliance is measured against what the protocol forbids: unapproved
    handoffs, and attempts on the human-only L4 boundary. A repository that has
    never run the relay is *unassessed*, not compliant — absence of evidence is
    never scored as evidence.
    """
    if not relay_path(root).is_file():
        return None, "requires runtime relay instrumentation"

    relay = load(root)
    records = read_records(root)
    submissions = sum(1 for r in records if r.action == "relay.submit")
    approvals = sum(1 for r in records if r.action == "relay.approve" and r.outcome == "approved")
    refused = sum(1 for r in records if r.action == "relay.approve" and r.outcome == "REFUSED")

    if submissions == 0 and approvals == 0:
        return None, "relay initialised but no handoff recorded yet"

    # Every submission must reach an L4 approval. An unapproved submission is a
    # skipped gate — the failure the protocol exists to prevent.
    score = 100.0 * min(1.0, approvals / submissions) if submissions else 100.0

    # Each refused L4 attempt is a SEV1 event. It was correctly blocked, so it is
    # not a breach — but it is evidence of a tool trying to self-approve, and the
    # score must not read as clean.
    score = max(0.0, score - 15.0 * refused)

    bits = [f"{approvals}/{submissions} handoff(s) approved"]
    if refused:
        bits.append(f"{refused} SEV1 L4 attempt(s) refused")
    if relay.violations:
        bits.append(f"{len(relay.violations)} recorded violation(s)")
    return round(score, 1), ", ".join(bits)
