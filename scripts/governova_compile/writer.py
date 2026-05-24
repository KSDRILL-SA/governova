"""Deterministic serialisation of the compiled index, with content checksum."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from governova_compile.schema import CompiledIndex, export_json_schema

# Fields excluded from the checksum: the checksum itself plus volatile build
# metadata. This makes the checksum a pure content fingerprint — identical
# constitutional content always yields the same checksum regardless of when or
# at which commit it was compiled. CI compares fingerprints, not wall-clock.
_VOLATILE_FIELDS = {"checksum", "compiled_at", "source_commit_sha"}


def _index_body_for_checksum(index: CompiledIndex) -> str:
    """Serialise the constitutional content (excluding volatile metadata),
    deterministically, so the checksum is a stable content fingerprint."""
    payload = index.model_dump(mode="json", exclude=_VOLATILE_FIELDS)
    return json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def compute_checksum(index: CompiledIndex) -> str:
    body = _index_body_for_checksum(index)
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def write_index(index: CompiledIndex, out_dir: Path) -> dict[str, Path]:
    """Write constitution.json, constitution.schema.json, and checksum.txt.

    Returns a mapping of artifact name → written path.
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    index.checksum = compute_checksum(index)

    index_path = out_dir / "constitution.json"
    schema_path = out_dir / "constitution.schema.json"
    checksum_path = out_dir / "checksum.txt"

    index_path.write_text(
        json.dumps(index.model_dump(mode="json"), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    schema_path.write_text(
        json.dumps(export_json_schema(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    checksum_path.write_text(index.checksum + "\n", encoding="utf-8")

    return {
        "index": index_path,
        "schema": schema_path,
        "checksum": checksum_path,
    }


def load_index(index_path: Path) -> CompiledIndex:
    """Load and validate a compiled index from disk."""
    data = json.loads(index_path.read_text(encoding="utf-8"))
    return CompiledIndex.model_validate(data)


def verify_checksum(index: CompiledIndex) -> bool:
    """Return True if the stored checksum matches a freshly computed one."""
    stored: str = index.checksum
    recomputed = compute_checksum(index)
    return stored == recomputed
