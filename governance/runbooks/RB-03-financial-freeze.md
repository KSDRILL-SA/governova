# Financial Freeze Runbook

**Severity:** SEV0 (automatic — S8.50)  
**Applies To:** KSDRILL Reserve Bank  
**Trigger:** Any incident involving incorrect balances, failed deposits, interest miscalculation, or transaction duplication

---

> **FREEZE FIRST. VERIFY SECOND. RESUME ONLY WHEN INTEGRITY IS CONFIRMED.**

---

## Immediate Actions (within 2 minutes)

### Step 1 — Freeze All Financial Operations

Set feature flags to `false` via direct database update:

```sql
-- Run against production PostgreSQL
UPDATE "FeatureFlag" SET enabled = false 
WHERE key IN ('DEPOSITS_ENABLED', 'WITHDRAWALS_ENABLED', 'INTEREST_CALCULATION_ENABLED');
```

Or via Railway console if database is inaccessible:
```bash
railway run psql $DATABASE_URL -c "UPDATE \"FeatureFlag\" SET enabled = false WHERE key LIKE '%ENABLED%';"
```

- [ ] `DEPOSITS_ENABLED` = false
- [ ] `WITHDRAWALS_ENABLED` = false
- [ ] `INTEREST_CALCULATION_ENABLED` = false

**Verify:** Try to make a deposit via the UI — it should be blocked.

### Step 2 — Declare SEV0 Incident

- [ ] Open GitHub Issue: `[SEV0] Financial integrity incident — {description}`
- [ ] Tag: `incident`, `sev0`, `financial`
- [ ] Assign Incident Commander: Maluleke Kurhula Success

### Step 3 — Communicate (within 15 minutes)

Update status page: "We have temporarily suspended deposit and withdrawal operations as a precautionary measure while we investigate a reported issue. Account balances are not affected. We will update within 30 minutes."

---

## Diagnosis (complete before any data changes)

### Check balance consistency

```sql
-- Check for any accounts where transaction sum != recorded balance
SELECT 
  a.id,
  a.balance AS recorded_balance,
  COALESCE(SUM(t.amount), 0) AS calculated_balance,
  a.balance - COALESCE(SUM(t.amount), 0) AS discrepancy
FROM "Account" a
LEFT JOIN "Transaction" t ON t.account_id = a.id AND t.deleted_at IS NULL
WHERE a.deleted_at IS NULL
GROUP BY a.id, a.balance
HAVING a.balance != COALESCE(SUM(t.amount), 0);
```

### Check for duplicate transactions

```sql
-- Find potential duplicate deposits within 5 minutes
SELECT 
  user_id, amount, COUNT(*) as count,
  array_agg(id) as transaction_ids
FROM "Transaction"
WHERE created_at > NOW() - INTERVAL '2 hours'
  AND deleted_at IS NULL
GROUP BY user_id, amount, date_trunc('minute', created_at / 5 * 5)
HAVING COUNT(*) > 1;
```

---

## Recovery

1. **Identify all affected accounts**
2. **Calculate correct balances** using transaction history as ground truth
3. **Apply corrections** via Prisma transaction (not raw SQL):
   ```typescript
   await prisma.$transaction([
     prisma.account.update({ where: { id }, data: { balance: correctBalance } }),
     prisma.auditLog.create({ data: { event: 'balance_correction', metadata: { before, after, reason } } })
   ])
   ```
4. **Verify corrections** with the diagnostic query above
5. **Get owner sign-off** on all corrections before re-enabling

---

## Resume Operations

Only resume after:
- [ ] All balance discrepancies resolved
- [ ] Diagnostic query returns zero rows
- [ ] Owner (Maluleke Kurhula Success) explicitly approves resume
- [ ] Re-enable feature flags:
  ```sql
  UPDATE "FeatureFlag" SET enabled = true 
  WHERE key IN ('DEPOSITS_ENABLED', 'WITHDRAWALS_ENABLED');
  ```
  Note: `INTEREST_CALCULATION_ENABLED` — re-enable only after verifying the interest calculation bug is fixed.

---

## Post-Mortem

This incident always produces a post-mortem regardless of duration. Financial integrity incidents are the highest-stakes failures in the system.

---

*Governed by C8 S8.50, C5 S5.3, C0 CF-03*
