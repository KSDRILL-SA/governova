# Severity Model — Universal Primitive

| Level | Name | Meaning | Response |
|-------|------|---------|----------|
| SEV0 | Critical | Production down or data at risk | Immediate stop · runbook activation · all hands |
| SEV1 | High | Functional breakage or security gap | Relay pause · Founder approval required |
| SEV2 | Medium | Standard violation, non-critical | Flag in PR review · amendment or documented exception |
| SEV3 | Low | Style, convention, minor deviation | Lint warning · document in commit message |

## Violation weighting in Governova Score

| Severity | Score weight |
|----------|-------------|
| SEV0 | 5× |
| SEV1 | 5× |
| SEV2 | 2× |
| SEV3 | 1× |

## SEV0 trigger conditions (non-exhaustive)

- Production database unreachable
- Balance discrepancy detected in financial system
- Authentication bypass detected
- Data exfiltration pattern detected
- Deployment has corrupted production state
