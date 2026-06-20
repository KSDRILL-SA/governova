# KSDRILL SA - AI Review and Challenge Framework

| Attribute | Value |
|-----------|-------|
| Document | AI review and challenge framework |
| Status | Operating reference |
| Applies to | Every stage-gated implementation review |
| Primary use | Force critical review, assumption testing, and risk discovery before gate approval |
| Paired with | `ai-assisted-software-development-workflow.md`, `ksdrill-sa-ai-workflow.md`, `AI-INSTRUCTIONS.md` |

## 1. Purpose

This framework defines the mandatory review layers, challenge prompts, and validation criteria applied to every development stage.

The objective is to force AI reviewers to think critically, identify hidden assumptions, challenge implementation decisions, and discover risks before the Founder approves progression to the next stage.

## 2. Review Layers

Each phase must pass through three review layers.

| Layer | Reviewer | Goal | Core Question |
|-------|----------|------|---------------|
| 1 | Claude Code self-review | Find implementation mistakes, missed requirements, bugs, and edge cases | What implementation issues exist in this phase? |
| 2 | Claude adversarial review | Attack the design, challenge assumptions, and simulate production failures | If this phase failed in production, why would it fail? |
| 3 | GPT-5/Codex independent review | Provide an independent engineering perspective and challenge maintainability, scalability, security, and architecture | If another engineering team inherited this system for the next five years, what would become problematic? |

Do not collapse these layers into one review. The value comes from changing the reviewer posture at each layer.

## 3. Review Output Rules

Every review must produce:

- Findings ordered by severity
- File or document references when applicable
- Evidence from commands, tests, contracts, schema, or docs
- Explicit distinction between confirmed bugs, plausible risks, and recommendations
- Required fixes before approval
- Risk acceptances that require Founder approval
- Open questions that block confident review

Reviewers must not approve phases. Reviewers recommend. The Founder approves.

## 4. Stage 00 - Foundation Review

### Claude Code Self-Review

Ask:

- Is the project structure maintainable?
- Are dependencies organized correctly?
- Are environment variables managed securely?
- Are naming conventions consistent?
- Are configuration files separated correctly?
- Are development and production settings isolated?
- Are secrets exposed anywhere?

### Claude Adversarial Review

Ask:

- What happens if the team grows from 1 developer to 20?
- What becomes difficult to maintain?
- Which folders will become overloaded?
- Which architectural decisions may cause technical debt?
- Which dependencies create future risk?
- Which assumptions may fail after six months?

### GPT-5/Codex Independent Review

Ask:

- Would another engineering team understand this structure?
- Does the architecture encourage coupling?
- Does the structure scale for future features?
- Which standards are missing?
- What future refactoring appears inevitable?

## 5. Stage 01 - Database Review

### Claude Code Self-Review

Ask:

- Are relationships modeled correctly?
- Are foreign keys implemented?
- Are indexes missing?
- Are constraints sufficient?
- Are queries efficient?
- Are migrations reversible?
- Is data integrity protected?

### Claude Adversarial Review

Ask:

- What happens with 1 million records?
- What happens with 100 million records?
- Which queries become bottlenecks?
- Could orphan records exist?
- Can duplicate data appear?
- What data corruption scenarios exist?
- What happens during migration failure?

### GPT-5/Codex Independent Review

Ask:

- Is normalization appropriate?
- Is denormalization needed anywhere?
- Are audit requirements missing?
- Are backup and recovery considerations present?
- Is future reporting supported?
- Which schema changes will be expensive later?

## 6. Stage 02 - Authentication and Authorization Review

### Claude Code Self-Review

Ask:

- Are passwords stored securely?
- Are tokens validated correctly?
- Are refresh tokens handled correctly?
- Are permissions enforced?
- Are authentication failures handled safely?
- Are rate limits implemented?

### Claude Adversarial Review

Ask:

- How would an attacker bypass authorization?
- Can users access data belonging to others?
- Can privilege escalation occur?
- Can tokens be reused?
- Can sessions be hijacked?
- Can brute-force attacks succeed?
- Can reset flows be abused?

### GPT-5/Codex Independent Review

Ask:

- Does authorization rely on frontend validation?
- Are trust boundaries clear?
- Are roles future-proof?
- Is MFA readiness considered?
- Are audit logs needed?
- What security assumptions are dangerous?

## 7. Stage 03 - Backend Review

### Claude Code Self-Review

Ask:

- Are business rules implemented correctly?
- Is validation complete?
- Are exceptions handled properly?
- Are APIs consistent?
- Are services reusable?

### Claude Adversarial Review

Ask:

- Which API endpoints can fail under load?
- Which services become bottlenecks?
- Which assumptions are undocumented?
- Which business rules can be bypassed?
- What happens during service outages?

### GPT-5/Codex Independent Review

Ask:

- Are responsibilities properly separated?
- Is the architecture modular?
- Which services are tightly coupled?
- What maintenance challenges exist?
- Which future features will be difficult to add?

## 8. Stage 04 - Frontend Review

### Claude Code Self-Review

Ask:

- Are components reusable?
- Is state managed correctly?
- Are forms validated?
- Are loading states handled?
- Are errors displayed properly?

### Claude Adversarial Review

Ask:

- What happens with slow networks?
- What happens with failed requests?
- What happens if APIs return unexpected data?
- What breaks on mobile devices?
- What accessibility problems exist?

### GPT-5/Codex Independent Review

Ask:

- Is component architecture scalable?
- Is state management becoming complex?
- Which components violate separation of concerns?
- Which areas will become difficult to maintain?

## 9. Stage 05 - Integration Review

### Claude Code Self-Review

Ask:

- Do frontend and backend contracts match?
- Are API responses validated?
- Are integrations tested?
- Are failures handled?

### Claude Adversarial Review

Ask:

- What happens when external services fail?
- What happens during network interruptions?
- What happens during partial failures?
- Can data become inconsistent?

### GPT-5/Codex Independent Review

Ask:

- Are integration boundaries clear?
- Are retries implemented appropriately?
- Is eventual consistency required?
- What hidden coupling exists?

## 10. Stage 06 - Deployment and Launch Review

### Claude Code Self-Review

Ask:

- Are deployment scripts correct?
- Are secrets secured?
- Is monitoring configured?
- Are logs useful?
- Are backups configured?

### Claude Adversarial Review

Ask:

- What happens if the deployment fails?
- What happens if the database becomes unavailable?
- What happens if a service crashes?
- What happens if storage fills up?
- What happens during traffic spikes?

### GPT-5/Codex Independent Review

Ask:

- Is the system production ready?
- Is disaster recovery adequate?
- Is observability sufficient?
- Can incidents be diagnosed quickly?
- What operational risks remain?

## 11. Universal Final Challenge

Before approving any phase, every reviewer must answer:

1. What is most likely to fail first?
2. What is most expensive to fix later?
3. What assumption is most dangerous?
4. What security risk remains?
5. What scalability risk remains?
6. What maintenance problem remains?
7. What edge case remains uncovered?
8. What would break under 10x growth?
9. What would break under 100x growth?
10. Would you personally recommend this for production?
11. If not, why not?

A phase cannot be considered complete until these questions have been answered and all findings have been reviewed.

## 12. Recommended Review Prompt

Use this prompt when assigning an independent phase review:

```text
You are the independent reviewer for Stage NN of this project.

Read the stage handoff, the relevant stage brief, the governing docs, and the actual repository state.
Do not assume the implementation is correct because a prior AI said it is correct.
Verify claims against files, contracts, schema, tests, and command output.

Review using .ksdrill/workflow/ai-review-challenge-framework.md.
Focus on Stage NN only. Do not review later stages.

Return:
1. Blocking findings
2. High-risk findings
3. Medium/low recommendations
4. Missing evidence or tests
5. Risk acceptances requiring Founder approval
6. Universal Final Challenge answers
7. A clear recommendation: approve, approve after fixes, or do not approve
```

