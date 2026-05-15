# Post-Mortem — {Incident Title}

---

| Attribute            | Value |
|----------------------|-------|
| **Incident ID**      | INC-{NNN} |
| **Severity**         | SEV0 / SEV1 |
| **System Affected**  | {System name(s)} |
| **Detection Time**   | {YYYY-MM-DD HH:MM UTC} |
| **Resolution Time**  | {YYYY-MM-DD HH:MM UTC} |
| **Total Duration**   | {N hours N minutes} |
| **Incident Commander** | {Name} |
| **Post-Mortem Author** | {Name} |
| **Review Date**      | {YYYY-MM-DD} (within 5 business days) |
| **Status**           | Draft / Final |

---

> **This post-mortem is blameless.** The goal is system improvement, not individual fault.

---

## Impact Summary

*Describe the user-facing impact of the incident. How many users were affected? What could they not do? Was any data affected?*

---

## Timeline

*Minute-by-minute from first detection to resolution. Be specific with timestamps.*

| Time (UTC) | Event |
|-----------|-------|
| {HH:MM} | {First detection — what was observed, how} |
| {HH:MM} | {Severity classified — SEV{N}} |
| {HH:MM} | {Incident declared — GitHub Issue #{N} opened} |
| {HH:MM} | {Incident Commander assigned} |
| {HH:MM} | {First hypothesis formed} |
| {HH:MM} | {Action taken — describe what was done} |
| {HH:MM} | {Result of action} |
| {HH:MM} | {Resolution action — rollback / fix deployed} |
| {HH:MM} | {Service restored — stability window started} |
| {HH:MM} | {15-minute stability window completed} |
| {HH:MM} | {Incident declared resolved by Incident Commander} |

---

## Root Cause Analysis

### The 5 Whys

**Why did the incident occur?**
{Answer}

**Why did that happen?**
{Answer}

**Why did that happen?**
{Answer}

**Why did that happen?**
{Answer}

**Why did that happen?**
{Root cause — the systemic reason, not the surface symptom}

### Contributing Factors

*What other factors made this incident worse, harder to detect, or slower to resolve?*

---

## What Went Well

*Acknowledge what worked — fast detection, correct runbook execution, good communication, etc.*

---

## What Went Poorly

*Acknowledge what didn't work — slow detection, missing runbook, communication gaps, incorrect initial diagnosis, etc.*

---

## Action Items

*Every action item must have an owner and a due date. Vague action items produce no improvement.*

| # | Action Item | Owner | Due Date | GitHub Issue |
|---|-------------|-------|----------|-------------|
| 1 | {Specific, actionable improvement} | {Name} | {YYYY-MM-DD} | # |
| 2 | | | | |

---

## Common Failure Register Update

*Does this incident add a new entry to C0 §13? If yes, propose the entry:*

| ID | Failure | Violated Standard | Consequence | Severity | Recovery |
|----|---------|-------------------|-------------|----------|----------|
| CF-{N} | {Failure description} | `S{C}.{N}` | {Production impact} | SEV{N} | {Recovery path} |

---

## Constitutional Amendment Required?

*Did this incident reveal a gap in the constitutional system? If yes, open a GitHub Issue in `system-design-template` with the amendment proposal following C0 §8.*

**Amendment required:** Yes / No

**If yes — proposed amendment:** {Constitution}, {Standard ID}, {Change description}

---

> *Post-mortem complete. Action items are tracked in GitHub Issues with the `post-mortem-action` label.*
