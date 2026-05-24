# Governova — Quick Start

> **10 steps from zero to first governed commit on a new project.**

---

## Prerequisites

- This repo cloned: `git clone https://github.com/MALULEKE-KS/governova.git`
- Your project repo initialised with `main` and `dev` branches
- Python 3.11+ (for the integrity validator)

---

## Step 1 — Identify your domain and stack

Consult `constitution/indexes/stack-assignment-matrix.md`.
Decide: which domain(s) apply? Which stack?

KSDRILL SA reference assignments:
- Content/SEO system → Next.js
- Enterprise/financial/AI system → Angular + FastAPI

---

## Step 2 — Create your CONSTITUTION-INDEX

Copy the template:
```bash
cp templates/CONSTITUTION-INDEX-template.md your-project/CONSTITUTION-INDEX.md
```

Fill in:
- `project:` your project name
- `domain:` your domain(s)
- `stack:` your stack(s)
- `mode:` personal | team | enterprise

---

## Step 3 — Read Phase 0 before writing a line of code

```bash
cat constitution/core/phase-0-foundation/C01-engineering-standards.md
```

No code until Phase 0 is read. No exceptions.

---

## Step 4 — Read Phase 1 before the first application file

Read in order:
1. `constitution/core/phase-1-core-architecture/C02-backend-constitution.md`
2. `constitution/implementation/fastapi/C02-backend-fastapi.md` (if using FastAPI)
3. `constitution/core/phase-1-core-architecture/C03-auth-constitution.md`
4. `constitution/implementation/nextauth/C03-auth-nextauth.md`
5. `constitution/core/phase-1-core-architecture/C04-frontend-constitution.md`
6. Your stack's frontend implementation guide
7. `constitution/core/phase-1-core-architecture/C05-database-constitution.md`
8. Your stack's database implementation guide(s)
9. `constitution/core/phase-1-core-architecture/C06-fullstack-architecture-constitution.md`

---

## Step 5 — Validate the integrity of your constitution index

```bash
python scripts/validate-integrity.py
```

All references must resolve before the first build session.

---

## Step 6 — Read Phase 2 before marking anything production-ready

```bash
cat constitution/core/phase-2-quality-reliability/C07-testing-constitution.md
cat constitution/core/phase-2-quality-reliability/C08-platform-reliability-constitution.md
```

---

## Step 7 — Read Phase 3 before AI sessions or roadmap decisions

```bash
cat constitution/core/phase-3-product-intelligence/C09-product-feature-constitution.md
cat constitution/core/phase-3-product-intelligence/C10-ai-collaboration-constitution.md
cat protocols/relay-protocol.md
```

---

## Step 8 — Set up your relay

Confirm which AI engineer is active. Load AI-INSTRUCTIONS.md + your CONSTITUTION-INDEX.
The relay reads `constitution/C00-constitutional-order.md` as the master reference.

---

## Step 9 — Create your first Issue and branch

```bash
# Create Issue in GitHub first (#1 — setup project architecture)
git checkout dev
git pull origin dev
git checkout -b feature/1-setup-architecture
```

---

## Step 10 — Build under the relay

Follow `protocols/relay-protocol.md` for every build session.
Every decision is documented. Every violation is caught before commit.
Every file gets its System Bible entry.

---

*You are now governed.*
