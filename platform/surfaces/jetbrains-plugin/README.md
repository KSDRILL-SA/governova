# Governova — JetBrains Plugin

**Status:** Planned (specified) — the 8th surface

The JetBrains/IntelliJ-platform counterpart to the VS Code / Cursor extension: live,
in-editor constitutional governance for IntelliJ IDEA, PyCharm, WebStorm, and the rest
of the JetBrains family.

> Specified rather than shipped here because it requires a JVM/Gradle toolchain to build
> and verify, which is out of scope for this Python engine repository. The contract below
> is stable; implementation is tracked in the [strengthening roadmap](../../../planning/strengthening-roadmap.md).

## Contract (mirrors the VS Code extension)

- **Source of truth:** read `compiled/constitution.json` (never re-parse markdown), exactly
  like `platform/surfaces/ide-extension`.
- **Diagnostics:** run the reliable-tier checks (the same rule set as `governova_checks`)
  over the open file and surface them as IntelliJ inspections — advisory, never blocking,
  consistent with GOVERNOVA-STRATEGY §11.2.
- **Hover:** show the standard (`S{C}.{N}`) and anti-pattern (`AP-S{C}.{N}{x}`) behind a finding.
- **Tooling:** a tool window listing constitutions and standards, mirroring the VS Code tree.

## Implementation outline

- Gradle + the IntelliJ Platform Plugin SDK (Kotlin).
- `plugin.xml` registering a `LocalInspectionTool` and a `DocumentationProvider`.
- A thin index loader (parse the compiled JSON) and a port of the deterministic rule set,
  or a call out to `governova-enforce --format json` for parity with the CI gate.

The detection logic already lives in `governova_checks`; the plugin is a presentation
layer over the same compiled index and rules.
