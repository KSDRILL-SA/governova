# RB-08 — Relay Abort Runbook

| Attribute | Value |
|-----------|-------|
| **ID** | RB-08 |
| **Trigger** | AI output diverges significantly from approved design |
| **Severity** | SEV1 |
| **Governed by** | C10 · protocols/relay-abort.md |

---

## When to activate

- Claude Code has built files not present in Claude's design spec
- Claude Code has made an ARCHITECTURAL decision without Founder approval
- The output contradicts a constitutional standard
- The relay position is ambiguous and unrecoverable
- A SEV0 violation is detected in Claude Code's output

## Response steps

**Step 1 — Stop.** No further files created or modified.

**Step 2 — Commit abort state.**
```bash
git add -A
git commit -m "relay-abort: [brief description of divergence]"
git checkout -b relay-abort/$(date +%Y-%m-%d)-[description]
git push origin relay-abort/$(date +%Y-%m-%d)-[description]
```

**Step 3 — Open GitHub Issue.**
Title: `[RELAY ABORT] [brief description]`
Tags: `relay-abort` `constitutional-review`
Body: Original design spec reference · divergence description · standard violated ·
abort commit hash.

**Step 4 — Founder review.**

**Step 5 — Re-enter relay at Claude (Design).**
Claude reads abort Issue + original spec.
Claude produces revised spec.
Founder approves.
Relay resumes from Step 1.

## Recovery time target
SEV1 — resolve within the same build session where possible.
