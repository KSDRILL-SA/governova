# Fintech — `D-FINTECH`

**Status:** Ratified — 6 standards (`D-FINTECH.1`–`D-FINTECH.6`)
**Regulatory basis:** PCI-DSS · FICA · FATF
**Seeded from:** FundsLink Academy · KSDRILL Reserve Bank

The domain constitution is [`D-FINTECH-domain-constitution.md`](./D-FINTECH-domain-constitution.md).

| ID | Standard |
|----|----------|
| `D-FINTECH.1` | Monetary amounts are exact and carry their currency |
| `D-FINTECH.2` | Value movement is idempotent |
| `D-FINTECH.3` | Every movement is double-entry and reconciled |
| `D-FINTECH.4` | Financial actions carry an immutable, attributable audit record |
| `D-FINTECH.5` | Initiation and approval are separated |
| `D-FINTECH.6` | Financial calculation code is exhaustively tested |

Applies to any system that holds, moves, or reconciles money — not only to the
reference systems it was seeded from. See `constitution/domains/README.md` for the
full registry and `framework/format-specification.md` for the format.
