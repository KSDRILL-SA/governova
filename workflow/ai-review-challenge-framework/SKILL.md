# AI Review and Challenge Framework

## Skill Description

Defines the mandatory review layers, challenge prompts, and validation criteria applied to every development stage. This skill forces critical review, assumption testing, and risk discovery before gate approval.

**Applies to:** Every stage (00–06) at all review gates.

**Status:** Operating reference | Mandatory before any Founder approval.

**Paired skills:**
- `ai-assisted-software-development-workflow/SKILL.md`
- See `.ksdrill/workflow/ai-review-challenge-framework.md` for full stage-specific questions

## When to Use This Skill

- **During internal hardening:** Apply Stage-specific questions in Step 3
- **During adversarial self-critique:** Use the adversarial prompts in Step 4
- **During independent review:** Provide GPT-5/Codex with stage-specific review prompts
- **Before stage approval:** Answer the Universal Final Challenge (11 critical questions)
- **When writing findings:** Structure all findings by severity level

## The 3 Review Layers

Every stage passes through three independent review layers with different postures.

| Layer | Reviewer | Posture | Core Question |
|-------|----------|---------|---------------|
| 1 | Claude Code Self-Review | Implementation auditor | What implementation issues exist in this phase? |
| 2 | Adversarial Critique | Design attacker | If this failed in production, why would it fail? |
| 3 | Independent Review (GPT-5/Codex) | Five-year maintainer | If another team inherited this, what becomes problematic? |

**Do not collapse these layers.** Each layer provides a different perspective and discovers different risks.

## Review Output Requirements

Every review must produce:

- ✅ **Findings ordered by severity** (Blocking → High → Medium → Low → Evidence Gap)
- ✅ **File references and evidence** (commands, tests, contract diffs, schema, docs)
- ✅ **Explicit distinction** between confirmed bugs, plausible risks, and recommendations
- ✅ **Clear severity classification** using the Severity Rubric
- ✅ **Open questions that block confident review**
- ✅ **No approvals from reviewers**—only recommendations

## Severity Rubric

| Severity | Meaning | Required Action |
|----------|---------|-----------------|
| Blocking | Gate should not be approved | Fix before approval |
| High | Serious risk, likely production or maintenance impact | Fix before approval unless Founder explicitly accepts |
| Medium | Should be fixed soon, not necessarily gate-blocking | Schedule or fix in current stage |
| Low | Improvement, cleanup, documentation polish | Track or batch |
| Evidence Gap | Claim may be true but proof is missing | Produce evidence before approval |

## Stage-Specific Review Questions

### Stage 00 – Foundation

**Self-Review Questions:**
- Is the project structure maintainable?
- Are dependencies organized correctly?
- Are environment variables managed securely?
- Are naming conventions consistent?

**Adversarial Questions:**
- What happens if the team grows from 1 to 20 developers?
- Which architectural decisions may cause technical debt?
- Which dependencies create future risk?

**Independent Review Questions:**
- Would another engineering team understand this structure?
- Does the architecture encourage coupling?
- Which standards are missing?

---

### Stage 01 – Database

**Self-Review Questions:**
- Are relationships modeled correctly?
- Are foreign keys implemented?
- Are indexes missing?
- Are constraints sufficient?
- Are queries efficient?
- Are migrations reversible?

**Adversarial Questions:**
- What happens with 1 million records?
- Which queries become bottlenecks?
- Could orphan records exist?
- Can duplicate data appear?

**Independent Review Questions:**
- Is normalization appropriate?
- Is denormalization needed anywhere?
- Are audit requirements missing?
- Which schema changes will be expensive later?

---

### Stage 02 – Authentication and Authorization

**Self-Review Questions:**
- Are passwords stored securely?
- Are tokens validated correctly?
- Are refresh tokens handled correctly?
- Are permissions enforced?
- Are rate limits implemented?

**Adversarial Questions:**
- How would an attacker bypass authorization?
- Can users access data belonging to others?
- Can privilege escalation occur?
- Can tokens be reused?
- Can sessions be hijacked?
- Can brute-force attacks succeed?

**Independent Review Questions:**
- Does authorization rely on frontend validation?
- Are trust boundaries clear?
- Are roles future-proof?
- Is MFA readiness considered?

---

### Stage 03 – Backend Modules

**Self-Review Questions:**
- Are business rules implemented correctly?
- Is validation complete?
- Are exceptions handled properly?
- Are APIs consistent?
- Are services reusable?

**Adversarial Questions:**
- Which API endpoints can fail under load?
- Which services become bottlenecks?
- Which business rules can be bypassed?
- What happens during service outages?

**Independent Review Questions:**
- Are responsibilities properly separated?
- Is the architecture modular?
- Which services are tightly coupled?
- What maintenance challenges exist?

---

### Stage 04 – Frontend

**Self-Review Questions:**
- Are components reusable?
- Is state managed correctly?
- Are forms validated?
- Are loading states handled?
- Are errors displayed properly?

**Adversarial Questions:**
- What happens with slow networks?
- What happens with failed requests?
- What happens if APIs return unexpected data?
- What breaks on mobile devices?
- What accessibility problems exist?

**Independent Review Questions:**
- Is component architecture scalable?
- Is state management becoming complex?
- Which areas will become difficult to maintain?

---

### Stage 05 – Integration

**Self-Review Questions:**
- Do frontend and backend contracts match?
- Are API responses validated?
- Are integrations tested?
- Are failures handled?

**Adversarial Questions:**
- What happens when external services fail?
- What happens during network interruptions?
- What happens during partial failures?
- Can data become inconsistent?

**Independent Review Questions:**
- Are integration boundaries clear?
- Are retries implemented appropriately?
- What hidden coupling exists?

---

### Stage 06 – Deployment and Launch

**Self-Review Questions:**
- Are deployment scripts correct?
- Are secrets secured?
- Is monitoring configured?
- Are logs useful?
- Are backups configured?

**Adversarial Questions:**
- What happens if the deployment fails?
- What happens if the database becomes unavailable?
- What happens if a service crashes?
- What happens if storage fills up?

**Independent Review Questions:**
- Is the system production ready?
- Is disaster recovery adequate?
- Is observability sufficient?
- Can incidents be diagnosed quickly?

---

## Universal Final Challenge

**Before approving ANY phase**, every reviewer must answer these 11 questions:

1. **What is most likely to fail first?**
2. **What is most expensive to fix later?**
3. **What assumption is most dangerous?**
4. **What security risk remains?**
5. **What scalability risk remains?**
6. **What maintenance problem remains?**
7. **What edge case remains uncovered?**
8. **What would break under 10x growth?**
9. **What would break under 100x growth?**
10. **Would you personally recommend this for production?**
11. **If not, why not?**

A phase cannot be approved until these questions are answered and all findings are reviewed.

## Review Findings Template

When documenting findings:

```markdown
### Finding: [Title]
- **Severity:** [Blocking | High | Medium | Low | Evidence Gap]
- **Location:** [File path, line range, or component]
- **Evidence:** [Command output, test result, or reference]
- **Description:** [What is the issue?]
- **Impact:** [Why does it matter?]
- **Recommendation:** [How to fix it?]
```

## See Also

- `ai-assisted-software-development-workflow/SKILL.md` — The 8-step phase completion workflow
- `.ksdrill/workflow/ai-review-challenge-framework.md` — Full framework with all stage questions
- `docs/process/stage-review-playbook.md` — how to conduct stage reviews in a system workspace
