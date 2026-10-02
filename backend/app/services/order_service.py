import secrets
from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.models import MenuItem, Order, OrderItem, User
from app.schemas.order import OrderCreate
from app.services.payment import get_payment_provider

CENT = Decimal("0.01")

# Allowed status changes. Anything not listed here is rejected.
TRANSITIONS: dict[str, set[str]] = {
    "pending": {"confirmed", "cancelled"},
    "confirmed": {"preparing", "cancelled"},
    "preparing": {"out_for_delivery", "cancelled"},
    "out_for_delivery": {"delivered"},
    "delivered": set(),
    "cancelled": set(),
}


class OrderError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def money(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def calculate_totals(subtotal: Decimal) -> tuple[Decimal, Decimal, Decimal]:
    """Returns (delivery_fee, tax_amount, total). Uses server settings only."""
    s = get_settings()
    fee = money(s.delivery_fee)
    if s.free_delivery_above > 0 and subtotal >= s.free_delivery_above:
        fee = Decimal("0.00")
    tax = money(subtotal * s.tax_rate)
    return fee, tax, money(subtotal + fee + tax)


def generate_order_number() -> str:
    stamp = datetime.now(timezone.utc).strftime("%y%m%d")
    return f"DW-{stamp}-{secrets.token_hex(3).upper()}"


def subtotal_of(order: Order) -> Decimal:
    return money(order.total_amount - order.delivery_fee - order.tax_amount)


def create_order(db: Session, user: User, data: OrderCreate) -> Order:
    # Merge repeated items, then load current menu rows from the database.
    wanted: dict[int, int] = {}
    for line in data.items:
        wanted[line.menu_item_id] = wanted.get(line.menu_item_id, 0) + line.quantity
    if any(q > 50 for q in wanted.values()):
        raise OrderError("You can order at most 50 of one item.", 422)

    rows = db.scalars(select(MenuItem).where(MenuItem.id.in_(wanted.keys()))).all()
    found = {m.id: m for m in rows}
    missing = [i for i in wanted if i not in found]
    if missing:
        raise OrderError(f"Menu item(s) not found: {sorted(missing)}", 422)
    unavailable = [found[i].name for i in wanted if not found[i].is_available]
    if unavailable:
        raise OrderError("These items are not available right now: " + ", ".join(unavailable), 409)

    provider = get_payment_provider(data.payment_method)
    order = Order(
        user_id=user.id,
        order_number=generate_order_number(),
        payment_method=provider.method,
        payment_status=provider.initial_status(),
        order_status="pending",
        customer_name=data.customer_name.strip(),
        customer_phone=data.customer_phone,
        delivery_address=data.delivery_address.strip(),
        special_instructions=(data.special_instructions or "").strip() or None,
        total_amount=Decimal("0.00"),
        delivery_fee=Decimal("0.00"),
        tax_amount=Decimal("0.00"),
    )
    subtotal = Decimal("0.00")
    for item_id, qty in wanted.items():
        menu_item = found[item_id]
        line_total = money(menu_item.price * qty)
        subtotal += line_total
        order.items.append(
            OrderItem(menu_item_id=item_id, quantity=qty, unit_price=money(menu_item.price), subtotal=line_total)
        )
    order.delivery_fee, order.tax_amount, order.total_amount = calculate_totals(subtotal)
    db.add(order)
    db.commit()
    return get_order(db, order.id)


def get_order(db: Session, order_id: int) -> Order | None:
    return db.scalars(
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.items).selectinload(OrderItem.menu_item), selectinload(Order.user))
    ).first()


def change_status(db: Session, order: Order, new_status: str) -> Order:
    if new_status == order.order_status:
        raise OrderError(f"Order is already {new_status}.", 409)
    if new_status not in TRANSITIONS.get(order.order_status, set()):
        raise OrderError(f"Cannot change an order from '{order.order_status}' to '{new_status}'.", 409)
    order.order_status = new_status
    provider = get_payment_provider(order.payment_method)
    if new_status == "delivered":
        paid = provider.on_delivered()
        if paid:
            order.payment_status = paid
    db.commit()
    return get_order(db, order.id)
