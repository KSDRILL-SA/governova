"""The tamper-evident chain, once.

`governova_audit` has walked a hash-linked chain since the runtime's first live
cycle. `#255` asks the credit ledger to reuse it rather than grow a second one —
*"building a second one is the `validate`-existed-twice failure with money
attached"* — so the walk lives here and both callers use it.

What a chain detects is not "somebody changed a record". It is the four distinct
ways a trail is falsified, which are different failures that a single check has
to separate if its report is going to be actionable:

- a record **edited** after the fact — its own hash no longer matches its content
- a link **rewritten** to point somewhere else
- a record **removed** — a sequence gap, a broken link, or both
- a record **inserted or reordered** — both surface as a link mismatch

None of that requires knowing what a record *means*, which is why it generalises:
governance entries and ledger entries are the same shape to a verifier and
entirely different to everyone else.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

GENESIS_HASH = "0" * 64


def canonical_hash(payload: dict[str, Any]) -> str:
    """SHA-256 over a canonical encoding.

    `sort_keys` and tight separators are what make it canonical: the same content
    hashes identically on any platform, any Python version, and in any order the
    fields happen to be written. Without that a chain verifies on the machine
    that wrote it and fails everywhere else, which reads exactly like tampering.
    """
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


@runtime_checkable
class ChainLink(Protocol):
    """What the verifier needs. Deliberately the least it could be.

    A record is free to carry anything else — an actor and a permission level, or
    an amount and an idempotency key. The chain does not read them, so neither
    caller has to shape its records around the other's.

    Every member is declared read-only. A plain attribute annotation describes a
    *mutable* one, which a frozen dataclass does not structurally satisfy — and
    both callers are frozen, necessarily: a record in a tamper-evident chain that
    can be edited in place is the thing the chain exists to detect.
    """

    @property
    def seq(self) -> int: ...

    @property
    def prev_hash(self) -> str: ...

    @property
    def record_hash(self) -> str: ...

    def compute_hash(self) -> str: ...


@dataclass(frozen=True)
class Verification:
    """The result of walking a chain end to end."""

    valid: bool
    records: int
    issues: list[str]

    @property
    def summary(self) -> str:
        if self.valid:
            return f"chain intact, {self.records} record(s)"
        return f"chain BROKEN — {len(self.issues)} issue(s) across {self.records} record(s)"


def verify_chain(records: Sequence[ChainLink], *, label: str = "seq") -> Verification:
    """Walk the chain and report every integrity failure found.

    Every failure, not the first: a trail with three problems and one reported is
    a trail somebody fixes once and re-runs, and the second run is the one that
    tells them the truth. Reporting all of them makes a falsified chain expensive
    to repair convincingly, which is most of what a chain is for.
    """
    issues: list[str] = []
    expected_prev = GENESIS_HASH
    expected_seq = 1

    for record in records:
        if record.record_hash != record.compute_hash():
            issues.append(
                f"{label} {record.seq}: record content was altered after it was "
                "written (hash mismatch)"
            )
        if record.prev_hash != expected_prev:
            issues.append(
                f"{label} {record.seq}: chain link broken — expected predecessor "
                f"{expected_prev[:12]}…, found {record.prev_hash[:12]}…"
            )
        if record.seq != expected_seq:
            issues.append(
                f"sequence gap — expected {label} {expected_seq}, found {record.seq}"
            )
            expected_seq = record.seq
        expected_prev = record.record_hash
        expected_seq += 1

    return Verification(valid=not issues, records=len(records), issues=issues)


def next_link(records: Sequence[ChainLink]) -> tuple[int, str]:
    """The `(seq, prev_hash)` a new record must carry to extend the chain."""
    if not records:
        return 1, GENESIS_HASH
    last = records[-1]
    return last.seq + 1, last.record_hash
