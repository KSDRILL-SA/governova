# SEV0 Response Runbook

**Severity:** SEV0 — Complete platform outage, data loss, auth down, or financial failure  
**Response SLA:** 15 minutes  
**Resolution SLA:** 2 hours

---

> **RESTORE SERVICE FIRST. INVESTIGATE SECOND. (S8.49)**

---

## Step 1 — Classify (within 5 minutes)

- [ ] Confirm this is SEV0: complete outage, data loss, auth down, or financial integrity failure
- [ ] Open GitHub Issue: `[SEV0] {title}` — tag `incident`, `sev0`
- [ ] Assign Incident Commander: Maluleke Kurhula Success

**Reserve Bank financial incident?** → Execute `runbooks/financial-freeze-runbook.md` IMMEDIATELY as Step 1a before anything else.

---

## Step 2 — Communicate (within 15 minutes)

- [ ] Update Better Stack status page: "We are experiencing a platform outage. Our team is actively investigating. Next update in 30 minutes."
- [ ] Set status update reminder: every 30 minutes (S8.54)

---

## Step 3 — Triage (immediate)

Check in this order:

1. **Recent deployment?**
   - YES → Rollback immediately (S8.67)
   - Next.js: Vercel dashboard → one-click rollback
   - FastAPI: Railway dashboard → redeploy previous build
   - Rollback takes 2-5 minutes; do not wait to investigate first

2. **Database connectivity?**
   - Check `/health` endpoint: `curl https://your-app/api/health`
   - If database is down → Railway dashboard → restart PostgreSQL service

3. **Auth service down?**
   - Check Sentry for auth-related errors
   - Check NextAuth session table or JWT deny-list for corruption

---

## Step 4 — Contain

- [ ] If data integrity risk: stop writes to affected tables immediately
- [ ] If auth is compromised: force-logout all users via session table truncation (Next.js) or mass token revocation (Angular)
- [ ] Enable maintenance mode if available

---

## Step 5 — Fix

- [ ] Apply fix to staging first
- [ ] Verify fix resolves the issue in staging
- [ ] Deploy to production via standard deployment pipeline
- [ ] Monitor for 15 minutes after deploy

---

## Step 6 — Resolve

- [ ] Service functioning correctly for 15 minutes: ✓
- [ ] Monitoring shows no anomalies: ✓
- [ ] Incident Commander declares resolution in GitHub Issue
- [ ] Update Better Stack status page: "Resolved. Post-mortem within 5 business days."

---

## Step 7 — Post-Mortem

- [ ] Schedule post-mortem within 5 business days (S8.77)
- [ ] Use `templates/post-mortem-template.md`
- [ ] All action items become GitHub Issues with `post-mortem-action` label

---

## Related Runbooks

- `financial-freeze-runbook.md` — Reserve Bank financial incidents
- `vercel-rollback-runbook.md` — Next.js rollback procedure
- `railway-deployment-runbook.md` — FastAPI rollback procedure
- `database-migration-runbook.md` — If schema migration caused the incident

---

*Governed by C8 S8.47–S8.54, S8.67–S8.82*
