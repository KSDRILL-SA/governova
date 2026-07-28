# Domains — Layer 4: Domain Extensions

Domain extensions add industry-specific standards on top of the universal core
and implementation bindings. They encode the additional requirements a specific
industry imposes — and only those. A domain never restates the core, and never
weakens it.

## Registry

Each domain's **ID** is its constitutional namespace: every standard it declares is
`D-{DOMAIN}.{N}`, and every anti-pattern `AP-D-{DOMAIN}.{N}{letter}`. The ID comes
from `DOMAIN_REGISTRY` in `scripts/governova_compile/discovery.py`, never from a
filename — a domain cannot mint an identity by dropping a file into a folder.

| Folder | ID | Domain | Standards | Status | Regulatory basis | Seeded from |
|--------|----|--------|-----------|--------|------------------|-------------|
| `fintech/` | `D-FINTECH` | Financial technology | 6 | **Ratified** | PCI-DSS · FICA · FATF | FundsLink Academy, Reserve Bank |
| `govtech/` | `D-GOVTECH` | Government technology | — | Registered — unwritten | POPIA · GDPR-adjacent | Maphophe |
| `edtech/` | `D-EDTECH` | Education technology | — | Registered — unwritten | FERPA · COPPA | FundsLink Academy |
| `saas/` | `D-SAAS` | SaaS / B2B | — | Registered — unwritten | — | SyncUp |
| `healthtech/` | `D-HEALTHTECH` | Health technology | — | Registered — unwritten | HIPAA-equivalent · NHI Act | — |
| `ecommerce/` | `D-ECOMMERCE` | E-commerce | — | Registered — unwritten | PCI-DSS · Consumer protection | — |
| `iot/` | `D-IOT` | IoT / Embedded | — | Registered — unwritten | IEC 62443 · ETSI EN 303 645 | — |
| `ai-ml/` | `D-AIML` | AI / ML Systems | — | Registered — unwritten | EU AI Act · NIST AI RMF | — |

*Registered — unwritten* means the identity is reserved and the folder compiles to
nothing. A domain folder holding only its README is skipped by the compiler, so an
unwritten domain never inflates a count or a score.

Run `governova domains` to list what is actually compiled.

## Writing a domain extension

1. Confirm the domain has an entry in `DOMAIN_REGISTRY`; add one if it does not.
2. Copy `templates/domain-constitution-template.md` into the domain folder.
3. Write each standard with a mandatory `**Extends:**` block naming the core
   standard(s) it builds on — this is what makes conflict review possible.
4. Complete the conflict-analysis table. A domain may **raise** a floor the core
   sets; it may never lower, narrow, or override one.
5. Run `governova compile` then `governova validate`. The validator enforces
   namespace ownership, the extends-the-core requirement, rationale, and
   anti-pattern presence.

Format is specified in `framework/format-specification.md`.

## How domain extensions grow

Domain extensions are the primary growth vector of the constitutional database.
They can be contributed by domain experts via the process in `CONTRIBUTING.md`.
Every extension follows the same format specification as the core and undergoes
conflict review before publication.
