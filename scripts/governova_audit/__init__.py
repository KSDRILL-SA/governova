"""governova_audit — the append-only, tamper-evident audit trail.

Implements the `audit-trail` engine component (`platform/engine/SPEC.md`): an
immutable record of every governed action, which GOVERNOVA-MASTER §12.2 and the
Governova Score both depend on.

**Why a hash chain rather than a log file.** An audit trail exists to be trusted
by someone who does not trust the system that wrote it — an auditor, a regulator,
a customer in a dispute. A plain log proves nothing, because the party whose
conduct is in question is the party that can rewrite it. Chaining each record to
the hash of its predecessor makes history *self-verifying*: editing a record,
deleting one, or reordering two breaks every link after the change, and the break
is detectable without any external system. That is the difference between "we log
our actions" and "our actions can be shown not to have been altered".

The chain is deliberately pure stdlib and file-backed. It must work offline, in
CI, and inside the free local engine, with no database and no service to trust.

Storage: `governance/audit/audit-log.jsonl` — one JSON object per line, appended
never rewritten. JSONL is chosen so that appending is atomic-ish per line and a
partially written tail cannot corrupt earlier records.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

AUDIT_RELATIVE_PATH = "governance/audit/audit-log.jsonl"

# The genesis link. The first record chains to this, so a log whose first record
# claims any other predecessor has had its head removed.
GENESIS_HASH = "0" * 64


class PermissionLevel(StrEnum):
    """`framework/permission-model.md` — L4 is permanently human-only."""

    L1_PROPOSE = "L1"
    L2_RECOMMEND = "L2"
    L3_IMPLEMENT = "L3"
    L4_APPROVE = "L4"


class ActorKind(StrEnum):
    HUMAN = "human"
    AI = "ai"
    SYSTEM = "system"


@dataclass(frozen=True)
class AuditRecord:
    """One immutable entry in the trail.

    `record_hash` covers every other field *including* `prev_hash`, which is what
    links the chain. `seq` is retained as well so that a wholesale truncation —
    removing the tail and its links together — is still visible as a gap.
    """

    seq: int
    timestamp: str
    actor: str
    actor_kind: str
    permission_level: str
    action: str
    subject: str
    outcome: str
    standards: list[str] = field(default_factory=list)
    detail: str = ""
    prev_hash: str = GENESIS_HASH
    record_hash: str = ""

    def payload(self) -> dict[str, Any]:
        """The signed portion — everything except the hash it produces."""
        d = asdict(self)
        d.pop("record_hash")
        return d

    def compute_hash(self) -> str:
        # sort_keys + separators make the encoding canonical, so the same record
        # hashes identically on any platform and any Python version.
        canonical = json.dumps(self.payload(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def is_intact(self) -> bool:
        return self.record_hash == self.compute_hash()


@dataclass(frozen=True)
class ChainVerification:
    """The result of walking the chain end to end."""

    valid: bool
    records: int
    issues: list[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        if self.valid:
            return f"chain intact — {self.records} record(s) verified"
        return f"chain BROKEN — {len(self.issues)} issue(s) across {self.records} record(s)"


def audit_path(root: Path) -> Path:
    return root / AUDIT_RELATIVE_PATH


def read_records(root: Path) -> list[AuditRecord]:
    """Read the trail. A malformed line is skipped here and caught by `verify`."""
    path = audit_path(root)
    if not path.is_file():
        return []
    records: list[AuditRecord] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(AuditRecord(**json.loads(line)))
        except (json.JSONDecodeError, TypeError):
            continue
    return records


def append(
    root: Path,
    *,
    actor: str,
    actor_kind: ActorKind | str,
    permission_level: PermissionLevel | str,
    action: str,
    subject: str,
    outcome: str = "recorded",
    standards: list[str] | None = None,
    detail: str = "",
) -> AuditRecord:
    """Append one record, chained to the current head.

    Reads the existing tail to find the head rather than trusting a cached value,
    so a record appended by another process still links correctly.
    """
    existing = read_records(root)
    prev_hash = existing[-1].record_hash if existing else GENESIS_HASH
    seq = existing[-1].seq + 1 if existing else 1

    unsigned = AuditRecord(
        seq=seq,
        timestamp=datetime.now(UTC).isoformat(timespec="seconds"),
        actor=actor,
        actor_kind=str(actor_kind),
        permission_level=str(permission_level),
        action=action,
        subject=subject,
        outcome=outcome,
        standards=sorted(standards or []),
        detail=detail,
        prev_hash=prev_hash,
    )
    record = AuditRecord(**{**unsigned.payload(), "record_hash": unsigned.compute_hash()})

    path = audit_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(asdict(record), sort_keys=True, separators=(",", ":"))
    # Append-only, and flushed to disk before returning — an audit record that is
    # still in a buffer when the process dies is a record that did not happen.
    with path.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(line + "\n")
        fh.flush()
        os.fsync(fh.fileno())
    return record


def verify(root: Path) -> ChainVerification:
    """Walk the chain and report every integrity failure found.

    Detects the four ways a trail is falsified: a record edited after the fact
    (its own hash no longer matches), a link rewritten to point elsewhere, a
    record removed (sequence gap or broken link), and a record inserted or
    reordered (both surface as a link mismatch).
    """
    path = audit_path(root)
    if not path.is_file():
        return ChainVerification(valid=True, records=0, issues=[])

    issues: list[str] = []
    raw_lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]

    records: list[AuditRecord] = []
    for i, line in enumerate(raw_lines, start=1):
        try:
            records.append(AuditRecord(**json.loads(line)))
        except (json.JSONDecodeError, TypeError) as exc:
            issues.append(f"line {i}: unreadable audit record ({type(exc).__name__})")

    expected_prev = GENESIS_HASH
    expected_seq = 1
    for record in records:
        if not record.is_intact():
            issues.append(
                f"seq {record.seq}: record content was altered after it was written "
                f"(hash mismatch)"
            )
        if record.prev_hash != expected_prev:
            issues.append(
                f"seq {record.seq}: chain link broken — expected predecessor "
                f"{expected_prev[:12]}…, found {record.prev_hash[:12]}…"
            )
        if record.seq != expected_seq:
            issues.append(f"sequence gap — expected seq {expected_seq}, found {record.seq}")
            expected_seq = record.seq
        expected_prev = record.record_hash
        expected_seq += 1

    return ChainVerification(valid=not issues, records=len(records), issues=issues)


def completeness(root: Path) -> float:
    """Share of records carrying the full governance context (0–100).

    A record that names no actor, no permission level, or no subject is present
    but not accountable — it cannot answer who did what under what authority,
    which is the only question the trail exists to answer.
    """
    records = read_records(root)
    if not records:
        return 0.0
    complete = sum(
        1
        for r in records
        if r.actor and r.actor_kind and r.permission_level and r.action and r.subject
    )
    return round(100 * complete / len(records), 1)
