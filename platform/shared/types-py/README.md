# governova-types

Typed models for the Governova compiled constitutional index
(`compiled/constitution.json`).

**Generated — do not edit.** Emitted from
`scripts/governova_compile/schema.py` by `governova-codegen`. Edit the schema,
re-run codegen.

The version tracks the index schema version (currently `1.1.0`): pinning
this package pins the index shape your code can read.

```python
from governova_types import CompiledIndex

index = CompiledIndex.model_validate_json(Path("compiled/constitution.json").read_text())
```

Depends only on `pydantic` — never on the Governova engine.
