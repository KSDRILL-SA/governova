# Contributing to Governova

Governova's constitutional database grows through governed contributions.
Domain and stack constitutions can be contributed by domain experts.

## What can be contributed

- **Domain constitutions** — industry-specific extensions (e.g., healthtech, e-commerce)
- **Stack implementation bindings** — how universal standards are satisfied in a specific technology

## What cannot be contributed

- Changes to the universal core (C00–C10)
- Changes to the framework primitives
- Changes to the permission model or relay protocol

These are maintained exclusively by KSDRILL SA.

## Contribution process

1. Fork the Governova repository
2. Create a branch: `contribution/{domain-or-stack}-constitution`
3. Write your constitution following `framework/format-specification.md` exactly
4. Include for each standard: ID, severity, phase, applies-to, rule, rationale, anti-pattern
5. Write a conflict analysis against the universal core (which standards does your
   domain extension interact with? Do any conflict?)
6. Open a pull request with the tag `domain-contribution` or `stack-contribution`
7. The Governova review process runs adversarial AI review + conflict check
8. Approved contributions are merged and the contributor is enrolled in revenue share

## Quality bar

A contribution that fails adversarial AI review is returned for revision.
A contribution with unresolved conflicts against the universal core is not merged.
A contribution without evidence (regulatory basis, production experience, case study)
is not considered.

Evidence is required. Personal preference is not evidence.
