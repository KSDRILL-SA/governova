# SEV1 Response Runbook

**Severity:** SEV1 — Major feature failure >50% users, or critical service degraded  
**Response SLA:** 30 minutes  
**Resolution SLA:** 4 hours

---

## Step 1 — Classify and Declare (within 30 minutes)

- [ ] Confirm this is SEV1 (not SEV0): major feature broken, not complete outage
- [ ] Open GitHub Issue: `[SEV1] {title}` — tag `incident`, `sev1`
- [ ] Assign Incident Commander

Common SEV1 triggers:
- AI matching service down (FundsLink) → use `ai-degradation-runbook.md` in parallel
- Payment/deposit endpoint failing (Reserve Bank) → use `financial-freeze-runbook.md` if financial integrity is at risk
- Database error rate elevated (>1% on critical endpoints)
- Auth endpoint returning errors (>1% failure rate on login)
- Memory >90% sustained for 5 minutes (Railway alert)
- Service restart detected (Railway alert)

---

## Step 2 — Recent Deployment?

- [ ] Check deployment history: Vercel dashboard or Railway dashboard
- [ ] If deployed in last 30 minutes and correlated with issue onset → rollback immediately
  - Next.js: `vercel-rollback-runbook.md`
  - FastAPI: `railway-deployment-runbook.md`

---

## Step 3 — Diagnose

**Check in order:**
1. Sentry — what errors are appearing and on which endpoints?
2. Better Stack — which services are healthy/degraded?
3. Railway Metrics — CPU, memory, database connection pool
4. Recent code changes — last 3 commits

---

## Step 4 — Contain

Options (choose appropriate):
- Disable the affected feature via feature flag
- Rollback the affected service
- Scale up Railway service if resource-constrained
- Clear Redis if deny-list or cache corruption suspected

---

## Step 5 — Fix and Verify in Staging

- Apply fix to staging
- Verify fix resolves the issue
- Confirm CI is green
- Deploy to production

---

## Step 6 — Resolve

- [ ] Service functioning correctly for 15 minutes: ✓
- [ ] Monitoring shows no anomalies: ✓
- [ ] Incident Commander declares resolution

**Communication:** Update GitHub Issue and status page.

---

## Step 7 — Post-Mortem

SEV1 requires a post-mortem. Schedule within 5 business days.

---

*Governed by C8 S8.47–S8.54, S8.77*
