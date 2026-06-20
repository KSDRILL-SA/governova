# Relay Abort Protocol — RB-08

| Attribute | Value |
|-----------|-------|
| **Severity** | SEV1 |
| **Trigger** | AI output diverges significantly from Claude's approved design |
| **Governed by** | C10 — AI Collaboration Constitution |

---

## Trigger conditions

Activate this protocol when any of the following are true:

- Claude Code has built files or structure not present in Claude's design spec
- Claude Code has made an ARCHITECTURAL decision without Founder approval
- The output contradicts a constitutional standard (any severity)
- The relay position is ambiguous and cannot be recovered without redesign
- A SEV0 violation is detected in Claude Code's output

## Protocol steps

**Step 1 — Stop immediately.**
Claude Code stops all build activity. No further files are created or modified.

**Step 2 — Commit current state to abort branch.**
```bash
git add -A
git commit -m "relay-abort: state at point of divergence — [brief description]"
git checkout -b relay-abort/[session-date]-[brief-description]
git push origin relay-abort/[session-date]-[brief-description]
```

**Step 3 — Document the divergence.**
Open a GitHub Issue in the Governova repo:
- Title: `[RELAY ABORT] [brief description]`
- Tag: `relay-abort`, `constitutional-review`
- Body: Which design spec was being followed, what divergence occurred,
  which standard was violated or which decision was made without authority,
  the commit hash of the abort state.

**Step 4 — Founder reviews.**
Founder reviews the abort branch and the GitHub Issue.
Two outcomes: (A) Divergence is acceptable — create amendment and continue.
(B) Divergence is not acceptable — relay re-enters at Claude (Design) for redesign.

**Step 5 — Re-enter relay at Claude (Design).**
Before resuming, Claude reads the abort Issue and the original design spec.
Claude produces a revised design spec that resolves the divergence.
Founder approves. Relay resumes at Step 1 from the relay protocol.
