# Railway Deployment Runbook

**Applies To:** Angular+FastAPI systems (FundsLink, Reserve Bank) — FastAPI backend  
**Standard:** S8.2 (Railway for FastAPI), S6.29 (deploy order)

---

## Standard Production Deploy

```bash
# Triggered by GitHub Actions deploy-production.yml
# Sequence: migration → FastAPI → Angular (S6.29)

# Step 1: Run database migration FIRST (S5.59)
railway run npx prisma migrate deploy

# Step 2: Verify migration
railway run npx prisma migrate status

# Step 3: Trigger Railway deploy (via GitHub Actions or Railway CLI)
railway up

# Step 4: Wait for health check
# Railway automatically runs health check against /health endpoint
# Deploy completes only when /health returns 200

# Step 5: Only then trigger Angular deploy (GitHub Actions → Vercel)
```

---

## Rollback FastAPI (S8.69)

Via Railway dashboard:
1. Log into Railway → project → FastAPI service
2. Navigate to **Deployments** tab
3. Find last known-good deployment
4. Click **Redeploy** on that deployment

Via CLI:
```bash
railway service list  # Find service ID
railway rollback --service={service-id}
```

**Verify:**
```bash
curl https://your-fastapi.railway.app/health
# Expected: { "status": "ok", "database": "connected" }
```

---

## Zero-Downtime Deploy Configuration

Railway configuration (in `railway.toml` or dashboard):

```toml
[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 30
restartPolicyType = "on_failure"
numReplicas = 1
```

Railway's rolling restart:
- Starts new container
- Waits for `/health` to return 200
- Only then kills old container
- Result: zero downtime for compatible deployments

---

## Emergency: FastAPI Service Down

If Railway service is unresponsive:

```bash
# 1. Check service logs
railway logs --service=fastapi

# 2. Restart service
railway service restart

# 3. If restart doesn't help — redeploy last known good
railway rollback

# 4. Check database connectivity
railway run python -c "import os; from sqlalchemy import create_engine; e = create_engine(os.environ['DATABASE_URL']); e.connect(); print('DB OK')"
```

---

## Environment Variables (never commit these)

Required Railway Secrets for FastAPI:
- `DATABASE_URL` — PostgreSQL connection string
- `MONGODB_URL` — MongoDB connection string (FundsLink, Reserve Bank)
- `REDIS_URL` — Redis URL
- `RS256_PRIVATE_KEY` — JWT signing key
- `RS256_PUBLIC_KEY` — JWT verification key
- `BCRYPT_ROUNDS` — password hashing rounds
- `CORS_ALLOWED_ORIGINS` — comma-separated allowed origins
- `SENTRY_DSN` — error tracking

---

*Governed by C8 S8.2, S8.69, S6.29*
