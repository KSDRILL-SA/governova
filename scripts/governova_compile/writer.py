"""Deterministic serialisation of the compiled index, with content checksum.

Also resolves *which* index a command should govern with — see
`load_active_index`. The engine ships its own constitution as package data, so
an installed `governova` governs any repository without needing the Governova
source tree on disk.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from governova_compile.schema import CompiledIndex, export_json_schema

INDEX_FILENAME = "constitution.json"
CONSTITUTION_ENV_VAR = "GOVERNOVA_CONSTITUTION"

# The index bundled into the wheel, alongside this module. Present in an
# installed package; absent when running from a source checkout, where the
# working-tree index is found by the search below instead.
BUNDLED_INDEX = Path(__file__).resolve().parent / "data" / INDEX_FILENAME

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


def compute_checksum(index: CompiledIndex) -> str:  # implements REQ-004
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


def find_index(start: Path | None = None) -> Path | None:
    """Search upward from `start` for a working-tree `compiled/constitution.json`.

    Returns None when there is none — which is the normal case for a repository
    that Governova governs but does not contain.
    """
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        index_file = candidate / "compiled" / INDEX_FILENAME
        if index_file.is_file():
            return index_file
    return None


def resolve_index_path(explicit: Path | None = None, *, start: Path | None = None) -> Path:
    """Resolve which constitution to govern with, most specific source first.

    1. An explicit path passed by the caller.
    2. ``GOVERNOVA_CONSTITUTION`` — lets an organisation point every surface at
       its own amended corpus without editing any command.
    3. A working-tree ``compiled/constitution.json`` found by walking upward.
       This is what keeps Governova's own CI governed by the constitution in the
       branch under review rather than by whichever copy happens to be installed.
    4. The index bundled with the package.

    Raises FileNotFoundError only when every source is exhausted, which for an
    installed package means the wheel was built without its data.
    """
    if explicit is not None:
        if not explicit.is_file():
            raise FileNotFoundError(f"No constitution index at {explicit}")
        return explicit

    from_env = os.environ.get(CONSTITUTION_ENV_VAR)
    if from_env:
        candidate = Path(from_env).expanduser()
        if not candidate.is_file():
            raise FileNotFoundError(
                f"{CONSTITUTION_ENV_VAR} points at {candidate}, which is not a file"
            )
        return candidate

    local = find_index(start)
    if local is not None:
        return local

    if BUNDLED_INDEX.is_file():
        return BUNDLED_INDEX

    raise FileNotFoundError(
        "No constitution index found. Pass one explicitly, set "
        f"{CONSTITUTION_ENV_VAR}, or run `governova compile` in a Governova source tree."
    )


def load_active_index(
    explicit: Path | None = None, *, start: Path | None = None
) -> CompiledIndex:
    """Load the constitution this command should govern with."""
    return load_index(resolve_index_path(explicit, start=start))
