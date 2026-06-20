# AI-Assisted Software Development Workflow

## Skill Description

Defines the standard process for designing, implementing, reviewing, hardening, and validating software systems across all KSDRILL SA builds. This skill ensures that AI tools are assigned specialist roles across the engineering lifecycle—architect, planner, implementer, critic, reviewer—with independent quality gates preventing any single tool from being the sole authority.

**Applies to:** All KSDRILL SA systems — every stage-gated build (00–06).

**Status:** Operating reference | Mandatory for all implementations.

**Paired skills:**
- `ai-review-challenge-framework/SKILL.md`
- See `.ksdrill/workflow/ai-assisted-software-development-workflow.md` for full details

## When to Use This Skill

- **During design phase:** Understand which AI tool owns architecture vs. planning vs. implementation
- **During implementation:** Confirm that the development workflow follows the 8-step phase completion process
- **Before seeking approval:** Verify that hardening, adversarial review, and independent review have been executed
- **During handoff:** Ensure the next engineer understands the workflow and review expectations
- **Before stage gate:** Confirm all 8 steps completed before the Founder approves progression

## Key Concepts

### Tool Responsibilities

| Tool | Role | Owns |
|------|------|------|
| Claude Chat | Architect / Strategist | Requirements, design, architecture, API design, independent architecture review, adversarial analysis |
| Claude Code | Implementer / Builder | Feature implementation, refactoring, code generation, repo analysis, tests, bugs, self-review, hardening |
| GPT-5/Codex | Independent Reviewer | Code review, security review, scalability review, maintainability, architectural gaps, edge cases |
| Gemini | Secondary Reviewer | Alternative architecture recommendations, assumption validation, risk identification (optional, high-impact decisions) |

**Critical rule:** No single AI is trusted as sole authority for design, implementation, AND review. Independent review before Founder approval is mandatory.

### Phase Completion Workflow (8 Steps)

Every stage must pass through all steps before Founder approval:

1. **Design** → Architecture decisions, requirements, specifications, plan
2. **Implementation** → Working code, tests, documentation
3. **Internal Hardening Review** → Self-review for edge cases, error handling, security
4. **Adversarial Self-Critique** → Challenge own assumptions, identify risks
5. **Independent Review** → GPT-5/Codex reviews from external perspective
6. **Secondary Review** → Gemini when high-risk or decisions disagree
7. **Findings Resolution** → Fix or risk-accept all findings
8. **Phase Approval** → Founder approves only after steps 1–7 complete

**Nothing ships until all 8 steps are done.**

## Implementation Checklist

When executing a stage:

- [ ] Stage brief read and understood
- [ ] Design phase completed and documented
- [ ] Implementation code written and tested
- [ ] Internal hardening findings addressed
- [ ] Adversarial self-critique completed
- [ ] Independent review (GPT-5/Codex) completed
- [ ] All findings resolved or risk-accepted
- [ ] Handoff document captures evidence
- [ ] Ready for Founder review

## Review Postures

### Step 3 – Internal Hardening Review
**Posture:** Find implementation mistakes, missed requirements, bugs, edge cases.
**Ask:** What implementation issues exist in this phase?

### Step 4 – Adversarial Self-Critique
**Posture:** Assume the implementation is flawed. Attack it.
**Ask:** If this failed in production, why would it fail?

### Step 5 – Independent Review (GPT-5/Codex)
**Posture:** I am inheriting this system for the next five years.
**Ask:** What becomes problematic? What hidden assumptions exist?

## Success Criteria

This workflow succeeds when:

- Defects are discovered early
- Architecture remains consistent
- Technical debt is minimized
- Security concerns are identified proactively
- Scalability risks are addressed before launch
- Each phase is production-ready before progression
- Handoffs contain verifiable evidence, not just claims

Speed is a benefit. **Reliability, maintainability, and correctness are the objective.**

## Reference the Full Workflow

For complete details including all 6 stage definitions and full review principles:

📖 **See:** `.ksdrill/workflow/ai-assisted-software-development-workflow.md`

## See Also

- `ai-review-challenge-framework/SKILL.md` — Stage-specific challenge questions and Universal Final Challenge
- `docs/process/stage-review-playbook.md` — how to conduct stage reviews in a system workspace
- `docs/process/session-playbook.md` — how to structure each stage session
