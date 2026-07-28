# Fintech Domain Constitution

| Attribute | Value |
|-----------|-------|
| **Document** | Fintech Domain Constitution |
| **Layer** | 4 — Domain Extension |
| **Extends** | Universal Core (C00–C10) |
| **Regulatory basis** | PCI-DSS · FICA · FATF |
| **Contributed by** | Maluleke Kurhula Success |
| **Version** | v1.0 |
| **Status** | ACTIVE |
| **Applies To** | Any system that holds, moves, or reconciles money |
| **Paired With** | `governance/runbooks/RB-03-financial-freeze.md` |

---

> *Money is the one domain where a rounding error is a breach, a retry is a theft, and
> a missing log is a regulatory finding. The universal core makes a system correct;
> this domain makes it accountable for value it does not own.*

---

## Domain overview

A fintech system is judged by a standard no general software carries: every cent it
reports must be reconstructible from an immutable record, and every movement of value
must be attributable to an identity, an authorisation, and a moment in time.

The universal core already governs precision (`S5.28`), transactional writes (`S5.15`),
immutable ledgers (`S5.65`), structured logging (`S8.31`), and incident severity
(`S8.47`). Those are necessary and not sufficient. This domain adds the requirements a
financial regulator imposes on top of them: idempotent value movement, dual-entry
reconciliation, retention that outlives the product, and a hard separation between the
party that initiates a payment and the party that approves it.

Seeded from two reference systems — **FundsLink Academy** (disbursement of student
funding) and **KSDRILL Reserve Bank** (core banking) — where these standards were
established under production conditions before being generalised here.

---

## Standards

### D-FINTECH.1 — Monetary Amounts Are Exact and Carry Their Currency

| Attribute       | Value |
|-----------------|-------|
| **ID**          | D-FINTECH.1 |
| **Priority**    | Critical |
| **Applies To**  | All Stacks · every system holding monetary values |
| **Enforced By** | schema review · reliable-tier rules · code review |

**Extends:**
`S5.28` (Decimal columns for monetary values), `S1.67` (constants are named and centralised)

**Standard:**
Every monetary amount is stored and computed as an exact decimal type — `NUMERIC`/`DECIMAL` in the database, `Decimal`/`BigDecimal` in application code — never a binary floating-point type. Every stored amount is accompanied by an explicit ISO 4217 currency code; a bare number is not an amount. Amounts are never converted to floating point at any point in their lifecycle, including serialisation, and are transported as strings rather than JSON numbers. Rounding is applied only at explicit, documented boundaries using a declared rounding mode, never implicitly.

**Rationale:**
Binary floating point cannot represent most decimal fractions exactly, so `0.1 + 0.2` is not `0.3`. In a ledger, that discrepancy accumulates silently across millions of rows until a reconciliation fails and no one can say which transaction was wrong. A currency-less amount is worse: it reconciles perfectly and is still fraudulent, because 100 of one currency was treated as 100 of another. JSON serialisation is the most common leak — a `Decimal` correct in the database becomes a float the moment it crosses an API boundary as a JSON number.

**Anti-Patterns:**
- `AP-D-FINTECH.1a` — A monetary value stored or computed as `float`, `double`, or `REAL`, or serialised as a JSON number.
- `AP-D-FINTECH.1b` — An amount persisted without an accompanying currency code, or a calculation that adds two amounts without asserting their currencies match.

---

### D-FINTECH.2 — Value Movement Is Idempotent

| Attribute       | Value |
|-----------------|-------|
| **ID**          | D-FINTECH.2 |
| **Priority**    | Critical |
| **Applies To**  | All Stacks · every endpoint or job that moves money |
| **Enforced By** | architecture review · semantic tier · integration tests |

**Extends:**
`S5.15` (transactions for multi-step writes), `S2.81` (external-call resilience)

**Standard:**
Every operation that moves value accepts a caller-supplied idempotency key, persists that key with the result of the operation in the same transaction as the movement itself, and returns the original result on any repeat of the same key. A retry — whether from a client, a network timeout, a queue redelivery, or an operator — never produces a second movement of value. Idempotency keys are retained at least as long as any upstream party may retry, and never less than 24 hours.

**Rationale:**
Every layer between a user and a ledger retries: browsers, mobile clients, load balancers, HTTP clients, message queues, and payment providers. A payment endpoint without idempotency is not a payment endpoint that occasionally double-charges — it is one that will double-charge, because a timeout on a *successful* write is indistinguishable from a failure at the caller. Storing the key outside the movement's transaction reintroduces the same race it was meant to close.

**Anti-Patterns:**
- `AP-D-FINTECH.2a` — A money-moving endpoint or job with no idempotency key, or one that derives the key from a server-side value (timestamp, UUID generated per request) rather than the caller.
- `AP-D-FINTECH.2b` — An idempotency record written in a separate transaction from the value movement it guards.

---

### D-FINTECH.3 — Every Movement Is Double-Entry and Reconciled

| Attribute       | Value |
|-----------------|-------|
| **ID**          | D-FINTECH.3 |
| **Priority**    | Critical |
| **Applies To**  | All Stacks · every system maintaining balances |
| **Enforced By** | schema review · scheduled reconciliation job · SEV0 alert |

**Extends:**
`S5.65` (ledger tables are immutable), `S5.15` (transactions for multi-step writes)

**Standard:**
Value movement is recorded as balanced double-entry: every transaction writes matching debit and credit entries that sum to zero, within one database transaction. Account balances are derived from ledger entries, never stored as an independently mutable field; where a cached balance exists for performance it is reconciled against the derived balance on a defined schedule. A reconciliation discrepancy of any magnitude is a SEV0 incident and triggers the financial freeze runbook.

**Rationale:**
A single-entry system cannot detect its own corruption — a lost write produces a wrong balance that looks exactly like a right one. Double-entry makes corruption arithmetically visible: the books stop balancing. A separately stored mutable balance is the most common way this guarantee is lost, because it can drift from the entries that justify it, and once drifted there is no record of which figure was ever correct. Treating a small discrepancy as a minor bug is how a reconciliation gap becomes a regulatory finding.

**Anti-Patterns:**
- `AP-D-FINTECH.3a` — A balance column updated directly (`balance = balance + amount`) rather than derived from immutable ledger entries.
- `AP-D-FINTECH.3b` — Debit and credit entries written in separate transactions, or a movement recorded as a single entry.

---

### D-FINTECH.4 — Financial Actions Carry an Immutable, Attributable Audit Record

| Attribute       | Value |
|-----------------|-------|
| **ID**          | D-FINTECH.4 |
| **Priority**    | Critical |
| **Applies To**  | All Stacks · every financial system |
| **Enforced By** | audit-log review · retention policy · code review |

**Extends:**
`S8.31` (structured JSON logging), `S5.65` (ledger tables are immutable), `S5.8` (soft delete, never hard delete)

**Standard:**
Every financial action — movement, authorisation, rate or fee change, manual adjustment, account state change, and every read of another party's financial data — is written to an append-only audit record carrying: actor identity, authorisation basis, timestamp with timezone, before and after values, and the correlation ID of the originating request. Audit records are retained for the longer of the applicable regulatory period or seven years, are written to storage that denies update and delete to the application's own credentials, and are never anonymised or purged by a data-deletion request without a recorded legal basis.

**Rationale:**
In a financial dispute, the record is the defence. A log that the application can rewrite proves nothing, because the party accused of the error is the party that controls the evidence — which is why write-once storage and credential separation matter more than log volume. Reads are included because unauthorised *access* to financial data is itself a reportable event, and a system that logs only writes cannot answer the question a regulator actually asks: who saw this account.

**Anti-Patterns:**
- `AP-D-FINTECH.4a` — An audit table the application can `UPDATE` or `DELETE`, or audit records held only in application logs subject to rotation.
- `AP-D-FINTECH.4b` — A financial action recorded without actor identity, or with a service account as the actor where a human initiated it.

---

### D-FINTECH.5 — Initiation and Approval Are Separated

| Attribute       | Value |
|-----------------|-------|
| **ID**          | D-FINTECH.5 |
| **Priority**    | Critical |
| **Applies To**  | All Stacks · privileged financial operations |
| **Enforced By** | authorisation review · access-control tests · semantic tier |

**Extends:**
`S3.4` (rate limiting on auth endpoints), `S1.103` (logic lives in its layer)

**Standard:**
No single identity may both initiate and approve a privileged financial operation. Privileged operations — outbound payments above a documented threshold, manual ledger adjustments, fee and rate changes, and counterparty detail changes — require approval by a distinct authenticated identity with a distinct role, recorded per `D-FINTECH.4`. The threshold, the roles, and the escalation path are declared in the system's CONSTITUTION-INDEX, and the separation is enforced server-side; a UI that merely hides the approve action does not satisfy this standard.

**Rationale:**
The dominant fraud pattern in financial systems is not an external breach but an internal actor with sufficient privilege to complete a movement alone. Separation of duties is the control that makes single-actor fraud impossible rather than merely detectable after the fact. Enforcing it in the interface only is the classic failure: the endpoint remains reachable, and the control evaporates for anyone who can issue an HTTP request. Changing a counterparty's bank details is included deliberately — it is the highest-yield fraud in practice, and it is often left unguarded because it moves no money by itself.

**Anti-Patterns:**
- `AP-D-FINTECH.5a` — A privileged financial operation completable by one identity, or an approval step enforced only in the client.
- `AP-D-FINTECH.5b` — An approval role that the initiating identity can grant to itself.

---

### D-FINTECH.6 — Financial Calculation Code Is Exhaustively Tested

| Attribute       | Value |
|-----------------|-------|
| **ID**          | D-FINTECH.6 |
| **Priority**    | Critical |
| **Applies To**  | All Stacks · interest, fees, tax, rounding, currency conversion, settlement |
| **Enforced By** | CI coverage gate · code review |

**Extends:**
`S7.25` (coverage gates — locked thresholds by stack), `S7.18` (E2E covers every critical path)

**Standard:**
Code that computes monetary results carries 100% branch coverage, enforced as a CI gate that blocks merge. Its tests assert exact decimal values — never approximate or tolerance-based comparison — and explicitly cover the boundary cases: zero, negative amounts, the maximum representable amount, rounding at the half, currency-precision limits, and the reversal path for every operation. Test fixtures express amounts as decimals or strings, never as floating-point literals.

**Rationale:**
Financial defects are not caught in production by users, because a user cannot tell that interest was computed with the wrong rounding mode — they can only tell years later, across a whole book, when an auditor can. Branch coverage matters more here than elsewhere because financial logic is dense with conditionals (tiers, thresholds, proration) and an untested branch is an untested money path. A tolerance-based assertion (`assertAlmostEqual`) defeats the purpose entirely: it is precisely the small discrepancy the domain exists to prevent.

**Anti-Patterns:**
- `AP-D-FINTECH.6a` — Financial calculation code below 100% branch coverage, or a coverage exclusion applied to it.
- `AP-D-FINTECH.6b` — A monetary assertion using approximate comparison or a floating-point literal in a test fixture.

---

## Conflict analysis

Every core standard this domain interacts with, and the resolution.

| Core standard | Interaction | Resolved? |
|---------------|-------------|-----------|
| `S5.28` — Decimal columns for monetary values | `D-FINTECH.1` extends it beyond storage to computation, serialisation, and transport, and adds the currency-code requirement | Yes — strictly additive; a system satisfying `D-FINTECH.1` satisfies `S5.28` |
| `S5.8` — Soft delete, never hard delete | `D-FINTECH.4` requires audit records to survive data-deletion requests absent a recorded legal basis | Yes — `S5.65` already establishes that ledgers permit no mutation; `D-FINTECH.4` applies the same reasoning to the audit trail |
| `S5.15` — Transactions for multi-step writes | `D-FINTECH.2` and `D-FINTECH.3` require specific writes to share one transaction | Yes — narrows `S5.15` to named cases; no conflict |
| `S5.65` — Ledger tables are immutable | `D-FINTECH.3` requires balances be derived from those immutable entries | Yes — `D-FINTECH.3` is the read-side consequence of `S5.65` |
| `S8.31` — Structured JSON logging | `D-FINTECH.4` adds mandatory fields and write-once storage for financial events specifically | Yes — additive; application logging remains governed by `S8.31` |
| `S8.47` — Severity classification | `D-FINTECH.3` fixes reconciliation discrepancy at SEV0 rather than leaving it to classification | Yes — a domain may raise a floor, never lower one |
| `S7.25` — Coverage gates by stack | `D-FINTECH.6` raises the threshold to 100% branch for financial calculation code only | Yes — raises, never lowers; the stack threshold continues to govern all other code |
| `S3.4` — Rate limiting on auth endpoints | `D-FINTECH.5` adds separation of duties above authentication | Yes — orthogonal controls at different layers |
| `S1.103` — Logic lives in its layer | `D-FINTECH.5` requires server-side enforcement, which is `S1.103` applied to authorisation | Yes — `D-FINTECH.5` is a domain-specific instance of `S1.103` |
| `S2.81` — External-call resilience | `D-FINTECH.2` makes idempotency mandatory where `S2.81` makes retries mandatory | Yes — complementary; retries are only safe because movement is idempotent |

No core standard is weakened, narrowed, or overridden by this domain. Every standard above
either extends a core standard to a financial context or raises a floor the core sets.

---

| Version | Date | Change | Rationale |
|---------|------|--------|-----------|
| v1.0 | 2026-07-28 | Initial fintech domain extension — `D-FINTECH.1`–`D-FINTECH.6`. Seeded from FundsLink Academy and KSDRILL Reserve Bank. | ADR-005 workstream A — Layer 4 established with its first domain. |
