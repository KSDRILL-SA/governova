# AI Degradation Runbook

**Severity:** SEV2  
**Applies To:** FundsLink Academy (LangChain + ChromaDB AI matching service)  
**Governed by:** S8.51 (C8), S2.47 (circuit breaker — C2)

---

> When the AI matching service fails, FundsLink degrades gracefully — students can still apply manually. This is SEV2, not SEV0. (S8.51)

---

## Symptoms

- Sentry: LangChain or ChromaDB errors appearing
- AI matching endpoint returning 503 or timeout
- Circuit breaker (S2.47) has tripped — `AI_MATCHING_CIRCUIT` is open
- Students seeing "AI matching temporarily unavailable" screen

---

## Immediate Response

### Step 1 — Confirm AI degradation (not full outage)

```bash
# Check if manual application flow still works
curl -X POST https://fundslink.railway.app/api/v1/applications/submit \
  -H "Authorization: Bearer {test_token}" \
  -d '{"student_id": "...", "scholarship_id": "..."}'

# Expected: 200 (manual flow bypasses AI)
# If 500: This is a different incident — escalate to SEV1
```

### Step 2 — Check ChromaDB health

```bash
# ChromaDB internal health check (via Railway internal URL)
railway run curl http://chromadb-internal:8000/api/v1/heartbeat
```

### Step 3 — Check LangChain pipeline logs

```bash
railway logs --service=fastapi --filter="langchain"
```

---

## Common Causes and Fixes

**ChromaDB container restarted (volume detached):**
```bash
railway service restart --service=chromadb
# Wait 30 seconds for ChromaDB to load embeddings from volume
# Verify: curl http://chromadb-internal:8000/api/v1/heartbeat
```

**Embedding model API rate limit:**
- Check OpenAI/embedding API usage in provider dashboard
- If rate-limited: reduce batch size in LangChain pipeline
- Circuit breaker will auto-reset after 60 seconds of successful calls

**ChromaDB similarity threshold returning no results (S5.48):**
- Check if embeddings are stale — may need re-embedding
- Verify: `railway run python scripts/check_embedding_freshness.py`

---

## Reset Circuit Breaker (if needed)

```python
# Railway console — reset circuit breaker manually
import redis
r = redis.from_url(os.environ["REDIS_URL"])
r.delete("circuit_breaker:ai_matching")
```

The circuit breaker will reset automatically after the configured timeout (default: 60 seconds with 3 successful calls).

---

## Communication

SEV2 — internal communication only:
- GitHub Issue: `[SEV2] FundsLink AI matching degraded — {description}`
- Students are already seeing the graceful degradation message
- No public status page update required for SEV2

---

## Re-Enable Full AI Matching

After root cause is resolved:
1. Verify ChromaDB heartbeat returns healthy
2. Run a test embedding query: `railway run python scripts/test_rag_pipeline.py`
3. If successful — circuit breaker auto-resets on next request
4. Monitor Sentry for 15 minutes to confirm no new errors

---

*Governed by C8 S8.51, C2 S2.47, C5 S5.48*
