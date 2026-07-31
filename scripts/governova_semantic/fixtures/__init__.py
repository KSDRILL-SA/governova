"""The evaluation fixture set — code with known expected findings.

Every fixture cites **real standard IDs from the compiled index**. A fixture naming a
standard that does not exist is testing fiction, and `test_semantic_eval.py` asserts
against the index exactly as `validate_rules()` does for the reliable tier.

Two kinds of fixture, and **the clean ones are the deliverable**:

- **Violating** — code that genuinely breaks the named standards. Measures recall.
- **Clean** — idiomatic code that breaks nothing. Measures **precision**, which is the
  number that decides whether a backend is usable at all.

The set deliberately favours standards the reliable tier **cannot** reach. `S1.106` and
`S1.107` are left to the semantic tier precisely because they have no deterministic
signature, so they are the honest test of whether a backend adds anything a regex could
not. A backend that only re-finds what the reliable tier already catches is not worth its
latency.

**Size is a correctness property, not a matter of thoroughness.** Precision is a ratio
whose denominator is the number of findings, so a small set can only produce a few
distinct scores. The first version of this set held four required findings, which made
the only reachable precisions 100%, 80%, 67%, 57% and 50% — nothing between 80 and 100.
Against a 90% bar that is not a threshold at all: it silently means *zero false positives
in every run*, a pass/fail gate wearing a percentage costume, and no backend was ever
going to clear it. The set now carries enough required findings that 90% means what it
says — roughly one mistake tolerated — and `test_semantic_eval.py` asserts the property
so the set cannot shrink back below the bar it is measured against.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Fixture:
    """One evaluation case.

    Three classes, not two, because real code violates several standards at once and a
    two-class scheme punishes a backend for being right about something the fixture
    author did not think to list:

    - **`expected`** — what a competent reviewer would cite. Finding these is recall.
    - **`acceptable`** — defensible but not required. Scored as **neither** a hit nor an
      invention.
    - **everything else** — a false positive, and precision is measured on these.

    The neutral class was added after the first real measurement. A 120b model was
    scored well below its real accuracy, because most of its "inventions" were correct:
    `S1.50` and
    `S2.5` (explicit return types) are genuinely violated by these Python snippets, and
    `S2.1` is the backend-scoped statement of the same concern as `S1.103`. Scoring a
    correct finding as an invention makes the harness measure fixture completeness
    rather than backend quality.
    """

    id: str
    language: str
    code: str
    expected: frozenset[str] = field(default_factory=frozenset)
    acceptable: frozenset[str] = field(default_factory=frozenset)
    note: str = ""

    @property
    def is_clean(self) -> bool:
        """No *required* finding. A clean fixture may still have acceptable ones."""
        return not self.expected

    @property
    def tolerated(self) -> frozenset[str]:
        """Everything that is not counted against the backend."""
        return self.expected | self.acceptable


# ─── Violating fixtures ──────────────────────────────────────────────────────

_LAYER_VIOLATION = Fixture(
    id="layer-logic-in-route",
    language="python",
    expected=frozenset({"S1.103"}),
    # S2.1 is C2's backend-scoped statement of the same concern; citing it on a route
    # handler is defensible. S1.50/S2.5: this snippet declares no return type.
    acceptable=frozenset({"S2.1", "S1.50", "S2.5"}),
    note="Business logic — a discount calculation — implemented inside a transport handler.",
    code='''\
@router.post("/orders")
async def create_order(request: OrderRequest):
    # Pricing logic living in the transport layer rather than a service.
    subtotal = sum(line.price * line.quantity for line in request.lines)
    if request.customer_tier == "gold":
        discount = subtotal * 0.15
    elif subtotal > 1000:
        discount = subtotal * 0.05
    else:
        discount = 0
    total = subtotal - discount
    return {"total": total}
''',
)

_REPOSITORY_VIOLATION = Fixture(
    id="data-access-outside-repository",
    language="python",
    expected=frozenset({"S1.104"}),
    acceptable=frozenset({"S1.50", "S2.5", "S2.28"}),
    note="Direct ORM data access issued from a service instead of through a repository.",
    code='''\
class InvoiceService:
    async def mark_paid(self, invoice_id: str) -> None:
        # Direct database access from the service layer — no repository boundary.
        async with db.session() as session:
            invoice_data = await session.execute(
                select(Invoice).where(Invoice.id == invoice_id)
            )
            record = invoice_data.scalar_one()
            record.status = "paid"
            await session.commit()
''',
)

_DUPLICATION_VIOLATION = Fixture(
    id="duplicated-shared-logic",
    language="python",
    expected=frozenset({"S1.106"}),
    acceptable=frozenset({"S1.50", "S2.5"}),
    note=(
        "The same normalisation logic repeated verbatim in two places. No deterministic "
        "signature exists for this, which is why it is left to the semantic tier."
    ),
    code='''\
def register_user(payload):
    email = payload["email"].strip().lower()
    if "+" in email.split("@")[0]:
        email = email.split("+")[0] + "@" + email.split("@")[1]
    return create_account(email)


def invite_user(payload):
    email = payload["email"].strip().lower()
    if "+" in email.split("@")[0]:
        email = email.split("+")[0] + "@" + email.split("@")[1]
    return send_invite(email)
''',
)

_SPECULATIVE_VIOLATION = Fixture(
    id="speculative-generality",
    language="python",
    expected=frozenset({"S1.107"}),
    acceptable=frozenset({"S1.50", "S2.5"}),
    note=(
        "An abstraction layer with exactly one implementation and no current requirement "
        "for a second — the simplest correct solution was not chosen."
    ),
    code='''\
class NotificationStrategy(ABC):
    @abstractmethod
    def send(self, message: str) -> None: ...


class EmailNotificationStrategy(NotificationStrategy):
    def send(self, message: str) -> None:
        smtp.send(message)


class NotificationStrategyFactory:
    _registry: dict[str, type[NotificationStrategy]] = {"email": EmailNotificationStrategy}

    @classmethod
    def create(cls, kind: str = "email") -> NotificationStrategy:
        return cls._registry[kind]()


def notify(message: str) -> None:
    NotificationStrategyFactory.create().send(message)
''',
)

_MULTI_CONCERN_VIOLATION = Fixture(
    id="multiple-concerns-in-one-function",
    language="python",
    expected=frozenset({"S1.3"}),
    acceptable=frozenset({"S1.107", "S1.50", "S2.5", "S1.103"}),
    note=(
        "One function that parses a file, validates rows, writes them, and sends mail. "
        "Four concerns, one unit."
    ),
    code='''\
def process_upload(raw_csv, connection, mailer):
    rows = []
    for line in raw_csv.splitlines()[1:]:
        name, email, amount = line.split(",")
        if "@" not in email:
            raise ValueError("bad email")
        if float(amount) <= 0:
            raise ValueError("bad amount")
        rows.append((name, email, float(amount)))
    for name, email, amount in rows:
        connection.execute(
            "INSERT INTO donations (name, email, amount) VALUES (?, ?, ?)",
            (name, email, amount),
        )
    connection.commit()
    for name, email, amount in rows:
        mailer.send(email, "Thank you", f"Dear {name}, we received {amount}.")
    return len(rows)
''',
)

_LEAKED_INTERNALS_VIOLATION = Fixture(
    id="internal-details-in-error-response",
    language="python",
    expected=frozenset({"S2.18"}),
    # S2.22 (uniform error shape) and S2.43 (translate database errors) are both
    # genuinely broken here too; either is a defensible citation.
    acceptable=frozenset({"S2.22", "S2.43", "S1.50", "S2.5"}),
    note=(
        "The driver's own message — carrying the table name and the SQL — is handed "
        "straight back to the caller."
    ),
    code='''\
@router.get("/accounts/{account_id}")
async def read_account(account_id: str):
    try:
        return await accounts.fetch(account_id)
    except DatabaseError as exc:
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc), "query": exc.statement, "trace": traceback.format_exc()},
        )
''',
)

_MISSING_OWNERSHIP_VIOLATION = Fixture(
    id="user-scoped-read-without-ownership-check",
    language="python",
    expected=frozenset({"S2.53"}),
    acceptable=frozenset({"S2.31", "S1.50", "S2.5"}),
    note=(
        "The caller is authenticated, so the handler assumes the document is theirs. Any "
        "signed-in user can read any document by guessing an id."
    ),
    code='''\
@router.get("/documents/{document_id}")
async def read_document(document_id: str, user: User = Depends(current_user)):
    # `user` is authenticated but never compared against the document's owner.
    document = await documents.get(document_id)
    if document is None:
        raise HTTPException(status_code=404)
    return document
''',
)

_MAGIC_VALUES_VIOLATION = Fixture(
    id="inlined-configuration-and-magic-numbers",
    language="python",
    expected=frozenset({"S1.105"}),
    acceptable=frozenset({"S1.67", "S1.50", "S2.5"}),
    note=(
        "An environment-specific host and three unexplained numbers, all inlined at the "
        "point of use."
    ),
    code='''\
async def sync_ledger(client):
    response = await client.post(
        "https://api.eu-west-1.internal.acme.com/v2/ledger/sync",
        timeout=30,
    )
    attempts = 0
    while response.status_code >= 500 and attempts < 5:
        await asyncio.sleep(2 ** attempts)
        response = await client.post(
            "https://api.eu-west-1.internal.acme.com/v2/ledger/sync",
            timeout=30,
        )
        attempts += 1
    return response
''',
)

_ROUTE_LOGIC_AND_MAGIC_VIOLATION = Fixture(
    id="route-with-inlined-rule-and-magic-threshold",
    language="python",
    # Both are unmistakable and independent: the rule is in the wrong layer, and the
    # numbers that define it are unnamed. A reviewer would cite both.
    expected=frozenset({"S1.103", "S1.105"}),
    acceptable=frozenset({"S2.1", "S1.67", "S1.50", "S2.5"}),
    note="Eligibility policy written into the handler, with its thresholds inlined.",
    code='''\
@router.post("/loans/assess")
async def assess(application: LoanApplication):
    if application.credit_score < 640:
        return {"eligible": False, "reason": "score"}
    if application.monthly_debt / application.monthly_income > 0.43:
        return {"eligible": False, "reason": "dti"}
    if application.months_employed < 24:
        return {"eligible": False, "reason": "tenure"}
    return {"eligible": True, "limit": application.monthly_income * 4.5}
''',
)

# ─── Clean fixtures — where precision is measured ────────────────────────────

_CLEAN_SERVICE = Fixture(
    id="clean-layered-service",
    language="python",
    acceptable=frozenset({"S1.50", "S2.5"}),
    note=(
        "Correct layering: the handler delegates, the service holds the rule, data access "
        "goes through a repository. A backend reporting anything here is unusable."
    ),
    code='''\
@router.post("/orders")
async def create_order(request: OrderRequest, service: OrderService = Depends()):
    order = await service.place(request.customer_id, request.lines)
    return OrderResponse.from_domain(order)


class OrderService:
    def __init__(self, orders: OrderRepository) -> None:
        self._orders = orders

    async def place(self, customer_id: str, lines: list[OrderLine]) -> Order:
        order = Order.draft(customer_id, lines)
        return await self._orders.add(order)
''',
)

_CLEAN_SIMILAR_NOT_DUPLICATE = Fixture(
    id="clean-similar-but-not-duplicate",
    language="python",
    acceptable=frozenset({"S1.50", "S2.5"}),
    note=(
        "Two functions of similar shape doing genuinely different things. The negative "
        "case for S1.106 — a backend that calls structural similarity duplication will "
        "report it on every well-factored codebase."
    ),
    code='''\
def total_incl_tax(lines: list[Line], rate: Decimal) -> Decimal:
    subtotal = sum((line.amount for line in lines), Decimal("0"))
    return subtotal + (subtotal * rate)


def total_after_refunds(lines: list[Line], refunds: list[Refund]) -> Decimal:
    subtotal = sum((line.amount for line in lines), Decimal("0"))
    return subtotal - sum((refund.amount for refund in refunds), Decimal("0"))
''',
)

_CLEAN_JUSTIFIED_ABSTRACTION = Fixture(
    id="clean-abstraction-with-two-implementations",
    language="python",
    acceptable=frozenset({"S1.50", "S2.5"}),
    note=(
        "An abstraction with two real implementations serving a present requirement. The "
        "negative case for S1.107 — a backend that flags every interface will be ignored."
    ),
    code='''\
class PaymentGateway(Protocol):
    def charge(self, amount: Decimal, token: str) -> ChargeResult: ...


class StripeGateway:
    def charge(self, amount: Decimal, token: str) -> ChargeResult:
        return _to_result(stripe.Charge.create(amount=int(amount * 100), source=token))


class PayfastGateway:
    def charge(self, amount: Decimal, token: str) -> ChargeResult:
        return _to_result(payfast.submit(amount=amount, token=token))
''',
)

_CLEAN_PLAIN_UTILITY = Fixture(
    id="clean-plain-utility",
    language="python",
    note=(
        "Ordinary, unremarkable code. If a backend finds a violation here it is inventing "
        "them, and every other finding it makes has to be discounted."
    ),
    code='''\
def slugify(title: str, max_length: int = 80) -> str:
    """Lower-case, hyphenate, and trim a title for use in a URL path."""
    cleaned = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return cleaned[:max_length].rstrip("-")
''',
)


_CLEAN_COHESIVE_STEPS = Fixture(
    id="clean-many-steps-one-concern",
    language="python",
    acceptable=frozenset({"S1.50", "S2.5"}),
    note=(
        "Six statements, one concern: formatting an address. The negative case for S1.3 — "
        "a backend that equates step count with concern count will fire on every function "
        "longer than three lines."
    ),
    code='''\
def format_postal_address(address: Address) -> str:
    """Render an address as the lines a postal service expects."""
    lines = [address.recipient, address.street]
    if address.unit:
        lines.append(f"Unit {address.unit}")
    lines.append(f"{address.city} {address.postal_code}")
    lines.append(address.country.upper())
    return "\\n".join(line.strip() for line in lines if line)
''',
)

_CLEAN_TRANSLATED_ERROR = Fixture(
    id="clean-translated-error-response",
    language="python",
    acceptable=frozenset({"S1.50", "S2.5"}),
    note=(
        "The driver error is logged and translated; the response carries the uniform "
        "shape and nothing internal. The negative case for S2.18 and S2.43."
    ),
    code='''\
@router.get("/accounts/{account_id}")
async def read_account(account_id: str) -> AccountResponse:
    try:
        return AccountResponse.from_domain(await accounts.fetch(account_id))
    except DatabaseError:
        logger.exception("account lookup failed", extra={"account_id": account_id})
        raise HTTPException(
            status_code=503,
            detail={"error": "Account lookup is unavailable.", "code": "ACCOUNT_UNAVAILABLE"},
        ) from None
''',
)

_CLEAN_OWNERSHIP_ENFORCED = Fixture(
    id="clean-ownership-checked-before-read",
    language="python",
    acceptable=frozenset({"S1.50", "S2.5"}),
    note=(
        "Ownership is part of the query, so a guessed id returns 404 rather than another "
        "tenant's row. The negative case for S2.53."
    ),
    code='''\
@router.get("/documents/{document_id}")
async def read_document(
    document_id: str, user: User = Depends(current_user)
) -> DocumentResponse:
    document = await documents.get_for_owner(document_id, owner_id=user.id)
    if document is None:
        raise HTTPException(status_code=404)
    return DocumentResponse.from_domain(document)
''',
)

_CLEAN_NAMED_CONSTANTS = Fixture(
    id="clean-named-constants-and-configuration",
    language="python",
    acceptable=frozenset({"S1.50", "S2.5"}),
    note=(
        "Every number is named for what it means and the host comes from configuration. "
        "The negative case for S1.105 and S1.67 — a backend that flags any numeric "
        "literal will flag `0`, `1` and every index in the codebase."
    ),
    code='''\
LEDGER_SYNC_TIMEOUT_SECONDS = 30
LEDGER_SYNC_MAX_ATTEMPTS = 5
BACKOFF_BASE_SECONDS = 2


async def sync_ledger(client: AsyncClient, settings: Settings) -> Response:
    for attempt in range(LEDGER_SYNC_MAX_ATTEMPTS):
        response = await client.post(
            settings.ledger_sync_url, timeout=LEDGER_SYNC_TIMEOUT_SECONDS
        )
        if response.status_code < HTTPStatus.INTERNAL_SERVER_ERROR:
            return response
        await asyncio.sleep(BACKOFF_BASE_SECONDS**attempt)
    return response
''',
)


FIXTURES: tuple[Fixture, ...] = (
    _LAYER_VIOLATION,
    _REPOSITORY_VIOLATION,
    _DUPLICATION_VIOLATION,
    _SPECULATIVE_VIOLATION,
    _MULTI_CONCERN_VIOLATION,
    _LEAKED_INTERNALS_VIOLATION,
    _MISSING_OWNERSHIP_VIOLATION,
    _MAGIC_VALUES_VIOLATION,
    _ROUTE_LOGIC_AND_MAGIC_VIOLATION,
    _CLEAN_SERVICE,
    _CLEAN_SIMILAR_NOT_DUPLICATE,
    _CLEAN_JUSTIFIED_ABSTRACTION,
    _CLEAN_PLAIN_UTILITY,
    _CLEAN_COHESIVE_STEPS,
    _CLEAN_TRANSLATED_ERROR,
    _CLEAN_OWNERSHIP_ENFORCED,
    _CLEAN_NAMED_CONSTANTS,
)


def required_findings() -> int:
    """How many findings a perfect backend must make — precision's denominator floor.

    Exposed because the evaluation bar depends on it: a bar of 90% is only a threshold
    if the set is large enough for 90% to sit between two reachable scores.
    """
    return sum(len(fixture.expected) for fixture in FIXTURES)


def expected_standards() -> frozenset[str]:
    """Every standard the fixture set names, required or tolerated.

    Both classes are validated against the compiled index: an `acceptable` entry naming
    a standard that does not exist would silently excuse a real invention.
    """
    return frozenset(sid for fixture in FIXTURES for sid in fixture.tolerated)
