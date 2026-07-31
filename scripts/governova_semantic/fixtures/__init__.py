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
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Fixture:
    """One evaluation case.

    `expected` is the set of standards a competent reviewer would cite. Anything else the
    backend reports is a false positive — including a finding that is arguably true but
    not the one this fixture is about, because a tier that reports adjacent concerns on
    every file is a tier whose output nobody reads.
    """

    id: str
    language: str
    code: str
    expected: frozenset[str] = field(default_factory=frozenset)
    note: str = ""

    @property
    def is_clean(self) -> bool:
        return not self.expected


# ─── Violating fixtures ──────────────────────────────────────────────────────

_LAYER_VIOLATION = Fixture(
    id="layer-logic-in-route",
    language="python",
    expected=frozenset({"S1.103"}),
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

# ─── Clean fixtures — where precision is measured ────────────────────────────

_CLEAN_SERVICE = Fixture(
    id="clean-layered-service",
    language="python",
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


FIXTURES: tuple[Fixture, ...] = (
    _LAYER_VIOLATION,
    _REPOSITORY_VIOLATION,
    _DUPLICATION_VIOLATION,
    _SPECULATIVE_VIOLATION,
    _CLEAN_SERVICE,
    _CLEAN_SIMILAR_NOT_DUPLICATE,
    _CLEAN_JUSTIFIED_ABSTRACTION,
    _CLEAN_PLAIN_UTILITY,
)


def expected_standards() -> frozenset[str]:
    """Every standard the fixture set expects to be found. Validated against the index."""
    return frozenset(sid for fixture in FIXTURES for sid in fixture.expected)
