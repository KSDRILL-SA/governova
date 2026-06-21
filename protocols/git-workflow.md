# KSDRILL SA — Git & Branch Workflow

---

| Attribute        | Value                                                                 |
|------------------|-----------------------------------------------------------------------|
| **Document**     | Git & Branch Workflow — Studio Version Control Standard               |
| **Organisation** | KSDRILL SA                                                            |
| **Version**      | v1.0                                                                  |
| **Status**       | LOCKED                                                                |
| **Locked**       | 2026-05-20                                                            |
| **Next Review**  | 2026-08-20                                                            |
| **Applies To**   | All Systems · Both Stacks · All Projects                              |
| **Governed By**  | C1 — Engineering Standards                                            |
| **Paired With**  | `workflow/ksdrill-sa-ai-workflow.md` · `constitutions/C01-engineering-standards.md` |

---

> *"Every line of code committed under KSDRILL SA follows this workflow. No exceptions. No shortcuts."*

---

> **⚠️ Order & authority update.** The authoritative workflow order is **branch → issue → PR → merge**, the no-AI-references rule, full issue/PR metadata, and mode-based merge authority are defined in **`protocols/github-workflow.md`** — read it first. Where the step ordering below (issue-first) differs, `github-workflow.md` governs. This document remains authoritative for branch/commit *mechanics* (naming, conventional commits, protection rules).

---

## Table of Contents

| Section | Title |
|---------|-------|
| §1 | Repository Structure |
| §2 | Branch Definitions |
| §3 | Full Development Lifecycle |
| §4 | Branch Protection Rules |
| §5 | Naming Conventions |
| §6 | Commit Convention |
| §7 | Labels |
| §8 | Repository Settings |
| §9 | Daily Workflow Reference |
| §10 | Golden Rules |

---

## §1 — Repository Structure

Every KSDRILL SA repository follows this branch hierarchy:

```
main
└── dev
    ├── feature/*
    ├── fix/*
    ├── refactor/*
    ├── docs/*
    └── hotfix/*
```

This structure is non-negotiable across all four flagship systems and any future project under the studio.

---

## §2 — Branch Definitions

### `main` — Production Branch

The single source of truth for deployed, production-ready code.

| Rule | Detail |
|------|--------|
| Stability | Always stable. Never broken. |
| Direct commits | ❌ Prohibited |
| Receives from | `Dev` only, via PR |
| Protection | ✅ Protected branch |

---

### `Dev` — Integration Branch

The staging layer between feature work and production.

| Rule | Detail |
|------|--------|
| Purpose | Combine completed features · Integration testing |
| Direct commits | ❌ Prohibited |
| Base for | All feature branches |
| Protection | ✅ Protected branch |

---

### Feature Branches — Isolated Development

All active development happens in feature branches, isolated from each other.

**Examples:**
```
feature/auth-system
feature/patient-module
feature/dashboard-ui
```

Each feature branch:
- Handles one task or feature only
- Is linked to exactly one GitHub Issue
- Is merged into `Dev` through a PR
- Is deleted after merge

---

## §3 — Full Development Lifecycle

### STEP 1 — Create Issues First

Before writing a single line of code, the full system is planned in GitHub Issues.

**Process:**
1. Plan the whole system scope
2. Break work into discrete Issues
3. Assign labels (phase, type, status)
4. Define scope per Issue before branching

**Example Issue set:**
```
#1  Setup backend architecture
#2  Implement JWT authentication
#3  Create patient CRUD API
#4  Build dashboard UI
#5  Configure CI/CD
```

> Issues are the single source of task truth. No Issue = no branch.

---

### STEP 2 — Create Feature Branch From `Dev`

Always branch from the latest `Dev`. Never from `main`.

```bash
git checkout dev
git pull origin dev

git checkout -b feature/auth-system
git push -u origin feature/auth-system
```

---

### STEP 3 — Work Only In Your Feature Branch

| Rule | Enforcement |
|------|-------------|
| Never work in `main` | Hard rule |
| Never work in `Dev` | Hard rule |
| One branch = one responsibility | Hard rule |

Commit regularly throughout development. Small, meaningful commits — not one large dump at the end.

**Example commit sequence:**
```
feat: add login endpoint
feat: add JWT middleware
fix: validate empty password field
```

---

### STEP 4 — Link Work To Issues

Every branch must map to an Issue. Every PR must close that Issue on merge.

| Component | Example |
|-----------|---------|
| Issue | `#12 Implement authentication` |
| Branch | `feature/12-authentication` |
| PR body | `Closes #12` |
| On merge | GitHub auto-closes Issue `#12` |

This keeps the Issues board accurate without manual closing.

---

### STEP 5 — Open Pull Request To `Dev`

Flow:
```
feature/auth-system → dev
```

**PR Checklist before opening:**

- [ ] Code works as expected
- [ ] Tests pass
- [ ] No merge conflicts
- [ ] Issue linked in PR body (`Closes #N`)
- [ ] Branch is updated with latest `Dev`

---

### STEP 6 — Review + Merge (Squash Strategy)

Preferred merge strategy across all repos: **Squash Merge**.

| Benefit | Detail |
|---------|--------|
| Clean history | One PR = one commit in `Dev` |
| Easier rollback | Single commit to revert |
| Readable log | `git log` tells the story, not noise |

**Example squash commit message:**
```
feat: implement JWT authentication (#12)
```

Delete the feature branch after merge.

---

### STEP 7 — Repeat For Every Task

```
Issue
  ↓
Feature Branch
  ↓
Commits
  ↓
PR → dev
  ↓
Review
  ↓
Squash Merge
  ↓
Delete Branch
  ↓
Repeat
```

---

### STEP 8 — Integration Testing In `Dev`

Once features are merged into `Dev`:

1. Test all features together — APIs, UI, database
2. Identify and fix integration bugs
3. Open fix branches off `Dev` if needed:

```
fix/integration-auth-error → dev
```

Do not release to `main` until `Dev` is stable and fully integrated.

---

### STEP 9 — Release To `main`

When a sprint or system phase is complete and `Dev` is stable:

```
dev → main
```

**Release Requirements:**

- [ ] All tests pass
- [ ] Integration complete
- [ ] No major open bugs
- [ ] Deployment configuration verified

Merge into `main` = production is updated.

---

## §4 — Branch Protection Rules

### Protecting `main`

Navigate to: `Repo → Settings → Branches → Add rule for main`

| Rule | Enabled |
|------|---------|
| Require PR before merging | ✅ |
| Require approvals | ✅ |
| Require status checks to pass | ✅ |
| Prevent force pushes | ✅ |
| Prevent branch deletion | ✅ |
| Restrict direct pushes | ✅ |

---

### Protecting `Dev`

Navigate to: `Repo → Settings → Branches → Add rule for dev`

| Rule | Enabled |
|------|---------|
| Require PR before merging | ✅ |
| Restrict direct pushes | ✅ |
| Prevent branch deletion | ✅ |

---

## §5 — Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feature/{description}` | `feature/auth-system` |
| Feature + Issue | `feature/{issue-number}-{description}` | `feature/12-authentication` |
| Fix | `fix/{description}` | `fix/login-validation` |
| Refactor | `refactor/{description}` | `refactor/user-service` |
| Documentation | `docs/{description}` | `docs/setup-guide` |
| Hotfix | `hotfix/{description}` | `hotfix/security-patch` |

Rules:
- All lowercase
- Hyphens only — no underscores, no spaces
- Descriptive but concise

---

## §6 — Commit Convention

Follows the [Conventional Commits](https://www.conventionalcommits.org) standard.

| Type | Usage | Example |
|------|-------|---------|
| `feat` | New feature | `feat: implement JWT authentication` |
| `fix` | Bug fix | `fix: resolve login validation bug` |
| `docs` | Documentation only | `docs: update backend setup guide` |
| `refactor` | Code restructure, no behaviour change | `refactor: simplify auth middleware` |
| `test` | Adding or fixing tests | `test: add authentication unit tests` |
| `chore` | Build/config/tooling changes | `chore: update ESLint config` |
| `perf` | Performance improvement | `perf: optimise token refresh logic` |

**Format:**
```
type: short imperative description (#issue-number)
```

> Commits are permanent records. Write them as if the next engineer reading them has no context.

---

## §7 — Labels

### Technical Labels

| Label | Usage |
|-------|-------|
| `backend` | Server-side, API, database work |
| `frontend` | UI, components, styling |
| `database` | Schema, migrations, queries |
| `devops` | CI/CD, infrastructure, deployment |
| `documentation` | Docs, READMEs, changelogs |
| `testing` | Unit, integration, E2E tests |
| `security` | Auth, permissions, vulnerability fixes |

### Status Labels

| Label | Usage |
|-------|-------|
| `blocked` | Cannot proceed — dependency or decision needed |
| `in-progress` | Actively being worked on |
| `ready-for-review` | PR opened, awaiting review |
| `urgent` | Time-sensitive — escalate |

### Phase Labels

| Label | Usage |
|-------|-------|
| `phase-1` | Foundation and core architecture |
| `phase-2` | Feature development |
| `phase-3` | Integration and testing |
| `phase-4` | Release and post-launch |

---

## §8 — Repository Settings

### Enable

| Setting | Reason |
|---------|--------|
| Issues | Task tracking backbone |
| Pull Requests | Code review and merge gate |
| Branch Protection | Enforce workflow compliance |
| Squash Merging | Clean commit history |
| Discussions | Optional — async team communication |

### Disable

| Setting | Reason |
|---------|--------|
| Merge commits | Produces noisy history |
| Rebase merging | Risk of rewriting public history |

---

## §9 — Daily Workflow Reference

### Start of Session

```bash
git checkout dev
git pull origin dev
git checkout -b feature/patient-module
```

### During Development

```bash
git add .
git commit -m "feat: create patient entity"
git push
```

### Before Opening PR

```bash
# Sync with latest dev first
git checkout dev
git pull origin dev

git checkout feature/patient-module
git merge dev

# Resolve any conflicts, then push
git push
```

### Open PR

```
feature/patient-module → dev
PR body: Closes #14
```

---

## §10 — Golden Rules

### Never

| Rule |
|------|
| ❌ Commit directly to `main` |
| ❌ Develop directly in `Dev` |
| ❌ Mix unrelated features in one branch |
| ❌ Merge untested code |
| ❌ Leave stale branches undeleted |
| ❌ Open a PR without linking an Issue |
| ❌ Force-push to protected branches |

### Always

| Rule |
|------|
| ✅ Create Issues before branching |
| ✅ Branch from latest `Dev` |
| ✅ Use PRs for all merges |
| ✅ Link every PR to an Issue |
| ✅ Squash merge into `Dev` |
| ✅ Delete branches after merge |
| ✅ Write meaningful commit messages |
| ✅ Test integration in `Dev` before releasing to `main` |
| ✅ Protect `main` and `Dev` at repo creation |

---

## Final Flow Diagram

```
Issue
  ↓
Create feature branch from dev
  ↓
Commits (conventional format)
  ↓
Sync with latest dev
  ↓
PR → dev (Closes #N)
  ↓
Review + Status checks
  ↓
Squash Merge
  ↓
Delete branch · Issue auto-closes
  ↓
Repeat for next Issue
  ↓
Integration testing in dev
  ↓
PR dev → main
  ↓
Production Release
```

---

*This document is a permanent standard under KSDRILL SA. All engineers — human and AI — follow this workflow on every project without exception.*
