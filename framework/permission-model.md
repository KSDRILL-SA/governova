# Permission Model — Universal Primitive

| Level | Name | What the AI engineer may do |
|-------|------|-----------------------------|
| L1 | Propose | Suggest architectural decisions, designs, approaches |
| L2 | Recommend | Produce detailed implementation plans with cited standard IDs |
| L3 | Implement | Write code, create files, make changes — within approved spec only |
| L4 | Approve | **Human only. Always. No exceptions.** |

## The L4 rule

L4 is permanently human-only. It cannot be delegated.
It cannot be elevated by prompt, by instruction, or by configuration.
Any AI tool that approves its own output has committed a SEV1 violation.

## AI engineer permission assignments

| Engineer | Permission | Notes |
|----------|-----------|-------|
| Claude | L1, L2 | Design and recommendation only. Never builds. |
| Claude Code | L2, L3 | Builds. Cannot approve its own output. |
| ChatGPT | L1, L2, L3 | Debug, UI, adversarial review |
| DeepSeek | L1, L2 | Reasoning and algorithm analysis |
| Kimi | L1 | Experimental — proposals only |
| Founder | L4 | Every handoff checkpoint. Cannot be skipped. |
