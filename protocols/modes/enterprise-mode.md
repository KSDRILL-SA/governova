# Enterprise Mode — Operating Mode

| Attribute | Value |
|-----------|-------|
| **Mode** | Enterprise |
| **Activates** | Mapping Engine · Certification tracking · Board reporting · Exception recording |
| **Tier** | Max · Enterprise contracts |
| **Adds to** | Team mode (enterprise mode is a superset) |

---

## What enterprise mode activates

**Constitutional Mapping Engine.** The enterprise's existing standards are ingested,
mapped to Governova's constitutional database, and a CONSTITUTION-INDEX is produced
in the enterprise's own language and format. See GOVERNOVA-MASTER.md §14.

**Certification tracking.** The Governova Score is monitored against certification
thresholds (≥85 for Standard, ≥92 for Advanced, ≥95 for Enterprise).
Certification readiness is surfaced in the web dashboard.

**Board-level governance report.** Auto-generated monthly. One page. Plain English.
Red/amber/green per constitutional area. AI action volume. Governance events.

**Constitutional exception recording.** When the enterprise overrides a Governova
standard, the exception is formally recorded with date, approver, rationale, and
scheduled review date. No exception is invisible.

**Multi-approver relay.** The L4 approval checkpoint can be distributed across
multiple named approvers with defined authority domains. Requires a documented
approval matrix in the CONSTITUTION-INDEX.

---

## CONSTITUTION-INDEX additions for enterprise mode

```yaml
mode: enterprise
approval_matrix:
  security_decisions: [CISO name]
  architecture_decisions: [CTO name]
  production_releases: [Engineering Lead name]
certification_target: advanced
constitutional_exceptions: []  # populated as exceptions are recorded
board_report: monthly
```
