# Vercel Rollback Runbook

**Applies To:** Next.js systems (Maphophe, SyncUp) and Angular frontend (FundsLink, Reserve Bank)  
**SLA:** Under 5 minutes (S8.7)

---

## When to Roll Back

- Sentry error rate spike >5% within 5 minutes of deploy (S8.71)
- p95 latency >3x baseline within 5 minutes of deploy (S8.71)
- SEV0 or SEV1 detected within 15 minutes of deploy (S8.71)
- Health check failures after deploy

---

## Step 1 — Instant Rollback via Vercel Dashboard

1. Log into Vercel dashboard → select the project
2. Navigate to **Deployments** tab
3. Find the last known-good deployment (the one before the problematic deploy)
4. Click the three-dot menu → **Redeploy**
5. Confirm "Use existing build" (not a new build)

**Time to live: approximately 30–60 seconds**

---

## Step 2 — Verify Rollback Succeeded

```bash
# Check which deployment is live
curl -I https://your-app.vercel.app/api/health
# Look for x-vercel-deployment-url header to confirm correct build is live

# Check Sentry error rate is returning to baseline
# Check Better Stack health check is passing
```

---

## Step 3 — Communicate

- Update GitHub incident issue with: "Rolled back to previous deployment at {HH:MM UTC}. Monitoring stability."
- 15-minute stability window: confirm no errors before declaring stable

---

## After Rollback — Before Re-Deploying

- [ ] Root cause identified
- [ ] Fix applied and tested in staging
- [ ] Staging preview deployment reviewed
- [ ] CI fully green
- [ ] Re-deploy via standard pipeline (not manual push)

---

## Angular Stack Note

For Angular+FastAPI systems where the FastAPI deploy caused the issue:
→ See `railway-deployment-runbook.md` for FastAPI rollback.

If only the Angular frontend caused the issue (static build regression):
→ Use this runbook for the Angular Vercel project.

If the FastAPI API changed and Angular calls a missing endpoint:
→ Roll back BOTH: FastAPI (Railway) first, then Angular (Vercel). Reverse of S6.29.

---

*Governed by C8 S8.67–S8.68, S8.7*
