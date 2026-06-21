# Platform — The Product

The software that operates on Governova's constitutional database.
Organised into the engine (the runtime) and the surfaces (where developers interact).

## Engine
The central runtime. Every product surface connects to it.
See `engine/SPEC.md` for the full architecture specification.

## Surfaces
Seven surfaces. One engine. Every touchpoint in the development workflow.

| Surface | Description |
|---------|-------------|
| `ide-extension/` | VS Code + Cursor — primary developer interface |
| `jetbrains-plugin/` | IntelliJ + WebStorm — enterprise unlock |
| `cicd-enforcer/` | GitHub Actions + GitLab CI — makes governance non-optional |
| `pr-guardian-bot/` | GitHub + GitLab bot — constitutional PR review |
| `web-dashboard/` | Team and management interface |
| `cli/` | Terminal interface and automation |
| `slack-teams-bot/` | Organisational communication layer |
| `mcp-server/` | Live constitutional database API for AI tools |

## Status
All folders are spec-phase. `SPEC.md` files define what gets built.
Code is added into these folders as each surface is built. Per
GOVERNOVA-STRATEGY.md §13, the IDE extension is the wedge and is built first.
