# Database Migration Runbook

**Applies To:** All systems with PostgreSQL  
**Standard:** S5.59 — Migrations run before service starts

---

## Pre-Migration Checklist

Before any production migration:

- [ ] Migration tested on staging and confirmed successful
- [ ] Migration is backward-compatible with the previous service version (S5.60)
- [ ] Rollback plan documented (what happens if migration fails)
- [ ] Not deleting a column that the current service version reads (S5.61)
- [ ] `prisma migrate diff` confirmed in CI with no unexpected changes (S8.14)

---

## Standard Migration (new columns, indexes, new tables)

```bash
# 1. Deploy migration BEFORE deploying new service version (S5.59)
npx prisma migrate deploy

# 2. Verify migration applied successfully
npx prisma migrate status

# 3. Only if migrate status shows all migrations applied — deploy new service
```

**In CI/CD (`deploy-production.yml`):**
```yaml
steps:
  - name: Run database migration
    run: npx prisma migrate deploy
    
  - name: Verify migration status
    run: npx prisma migrate status | grep -c "applied"
    
  - name: Deploy service
    if: success()  # Only if migration succeeded
    run: railway up
```

---

## Column Removal (two-phase)

Removing a column requires two separate deployments:

**Phase 1 — Remove from code, keep in schema:**
```prisma
// schema.prisma — remove from code but keep column (deprecated)
// model User {
//   old_field  String?  @deprecated  ← still in schema, not in queries
// }
```
Deploy Phase 1. Let it run in production for one sprint minimum.

**Phase 2 — Remove from schema:**
```bash
# Remove the column definition from schema.prisma
# Generate migration
npx prisma migrate dev --name remove_old_field
npx prisma migrate deploy  # Deploy to production
```

---

## Migration Rollback

If a migration fails in production:

```bash
# Mark the failed migration as rolled back
npx prisma migrate resolve --rolled-back {migration_name}

# Verify
npx prisma migrate status

# Redeploy previous service version (that works with old schema)
railway redeploy  # Previous Railway build
```

**Do NOT use `prisma migrate reset` in production — this drops all tables.**

---

## Emergency: Schema Drift Detected

If `prisma migrate status` shows "Database schema is not in sync":

```bash
# Diagnose the drift
npx prisma migrate diff --from-schema-datamodel prisma/schema.prisma --to-schema-datasource

# DO NOT fix with prisma db push in production
# Create a migration that reconciles the drift
npx prisma migrate dev --name fix_schema_drift

# Review the generated migration carefully before deploying
```

---

*Governed by C5 S5.59–S5.64, C8 S8.70*
