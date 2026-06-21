# KSDRILL SA - AI-Assisted Software Development Workflow

| Attribute | Value |
|-----------|-------|
| Document | AI-assisted software development workflow |
| Status | Operating reference |
| Applies to | All KSDRILL SA software systems and stage-gated builds |
| Primary use | Guide design, implementation, hardening, review, and phase approval |
| Paired with | `ai-review-challenge-framework.md`, `ksdrill-sa-ai-workflow.md`, `AI-INSTRUCTIONS.md` |

## 1. Purpose

This workflow defines the standard process for designing, implementing, reviewing, hardening, and validating software systems with multiple AI tools while preserving engineering quality.

The goal is not simply to move faster. The goal is to improve architectural quality, expose hidden risks, reduce defects, and make every completed stage production-ready before the next stage begins.

## 2. Core Philosophy

AI is not treated as a single code generator. AI is assigned specialist roles across the engineering lifecycle:

| Role | Function |
|------|----------|
| Architect | Designs the system, validates requirements, and defines constraints |
| Planner | Breaks the work into staged, testable implementation steps |
| Implementer | Builds the approved design inside the repository |
| Critic | Challenges assumptions and searches for failure modes |
| Reviewer | Performs independent review before stage approval |

No single AI system is trusted as the sole authority for design, implementation, review, and approval. Independent review and adversarial analysis are mandatory before phase approval. Founder approval remains the only L4 approval gate.

## 3. Tool Responsibilities

### Claude Chat

Primary responsibilities:

- Requirements analysis
- System design
- Architecture design
- Database design
- API design
- Implementation planning
- Independent architecture review
- Adversarial design review

Claude Chat serves as the strategic and architectural advisor.

### Claude Code

Primary responsibilities:

- Feature implementation
- Refactoring
- Code generation
- Repository analysis
- Test execution
- Bug fixing
- Initial self-review
- Hardening passes

Claude Code serves as the implementation engine.

### GPT-5 / Codex

Primary responsibilities:

- Independent code review
- Security review
- Scalability review
- Maintainability review
- Architectural gap analysis
- Edge-case identification

GPT-5/Codex serves as the primary independent reviewer. Its job is to challenge the work as if another engineering team will inherit it.

### Gemini

Primary responsibilities:

- Alternative architectural recommendations
- Secondary independent review
- Assumption validation
- Additional risk identification

Gemini is optional and should be used for major phases, high-impact decisions, or unresolved disagreement between earlier reviewers.

## 4. Development Lifecycle

Every system is reviewed stage by stage. Do not review all stages at once unless the Founder explicitly requests a full-system audit.

| Stage | Name | Scope | Primary Review Focus |
|-------|------|-------|----------------------|
| 00 | Foundation | Project initialization, repository setup, folder structure, environment configuration, CI/CD preparation, coding standards, dependency management | Maintainability, scalability, environment consistency, architectural alignment |
| 01 | Database layer | Entity design, schema creation, constraints, relationships, migrations, indexing strategy | Normalization, query efficiency, data integrity, backup strategy, future scalability |
| 02 | Authentication and authorization | Registration, login flows, session management, JWT implementation, role-based access control | Privilege escalation, token security, session handling, password recovery, account protection, authorization boundaries |
| 03 | Core backend services | Business logic, service layer, APIs, data processing, validation | Performance, reliability, error handling, API consistency, domain correctness |
| 04 | Frontend | User interface, state management, user experience, client-side validation | Accessibility, maintainability, performance, UX consistency, error handling |
| 05 | Integration | Backend/frontend integration, third-party services, end-to-end workflows | Contract compliance, failure handling, resilience, workflow correctness |
| 06 | Deployment and launch | Infrastructure, monitoring, logging, security hardening, release preparation | Production readiness, disaster recovery, observability, operational reliability |

## 5. Phase Completion Workflow

Each phase must complete this sequence before approval.

### Step 1 - Design

Performed by Claude Chat.

Required deliverables:

- Architecture decisions
- Requirements validation
- Technical specifications
- Implementation plan

### Step 2 - Implementation

Performed by Claude Code.

Required deliverables:

- Working implementation
- Tests
- Documentation updates

### Step 3 - Internal Hardening Review

Performed by Claude Code after implementation.

Review areas:

- Edge cases
- Error handling
- Security issues
- Missing requirements
- Performance concerns

Findings must be addressed before progressing to external review.

### Step 4 - Adversarial Self-Critique

Performed by Claude Code or Claude Chat in a challenge posture.

Prompt strategy:

```text
Assume this implementation is flawed.
Identify design weaknesses, hidden assumptions, production risks,
scalability bottlenecks, security vulnerabilities, and missing tests.
```

All findings are evaluated and either fixed or explicitly risk-accepted by the Founder.

### Step 5 - Independent Review

Performed by GPT-5/Codex.

Review areas:

- Architecture flaws
- Security concerns
- Scalability risks
- Maintainability issues
- Testing gaps
- Hidden assumptions

The reviewer must be instructed to challenge all major decisions and must not simply validate that the implementation appears to work.

### Step 6 - Secondary Review

Performed by Gemini when needed.

Recommended for:

- Major architectural decisions
- Security-sensitive flows
- Money-adjacent systems
- High-risk customer-facing functionality
- Disagreement between implementation and independent review

Review areas:

- Alternative solutions
- Architectural trade-offs
- Additional risk analysis

### Step 7 - Findings Resolution

The development team and Founder evaluate:

- Valid findings
- Recommended improvements
- Risk acceptance decisions
- Required fixes before sign-off

Approved fixes are implemented before phase sign-off.

### Step 8 - Phase Approval

A phase is complete only after:

- Implementation is complete
- Hardening is complete
- Independent review is complete
- Findings are addressed or explicitly accepted
- Documentation is updated
- Founder approves the phase gate

Only then may development proceed to the next phase.

## 6. Review Principles

Reviewers must not focus on confirming that the implementation is acceptable. Reviewers must actively search for:

- Failure scenarios
- Security weaknesses
- Hidden assumptions
- Architectural debt
- Long-term maintenance risks
- Missing tests
- Operational gaps

The purpose of review is to discover what could fail before production discovers it.

## 7. Success Criteria

This workflow succeeds when:

- Defects are discovered early
- Architecture remains consistent
- Technical debt is minimized
- Security concerns are identified proactively
- Scalability risks are addressed before launch
- Each phase is production-ready before progression
- Handoffs contain enough evidence for the next engineer to verify reality, not trust claims

Speed is a benefit. Reliability, maintainability, and correctness are the objective.

