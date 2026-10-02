from app.models import MenuItem, Order
from app.schemas.menu import MenuItemOut
from app.schemas.order import OrderItemOut, OrderOut
from app.services.order_service import subtotal_of


def menu_item_out(m: MenuItem) -> MenuItemOut:
    out = MenuItemOut.model_validate(m)
    out.category_name = m.category.name if m.category else None
    return out


def order_out(o: Order, include_email: bool = False) -> OrderOut:
    items = []
    for i in o.items:
        item = OrderItemOut.model_validate(i)
        item.item_name = i.menu_item.name if i.menu_item else None
        items.append(item)
    out = OrderOut.model_validate({**{c: getattr(o, c) for c in OrderOut.model_fields if hasattr(o, c) and c not in ("items", "subtotal")}, "subtotal": subtotal_of(o), "items": items})
    if include_email and o.user:
        out.customer_email = o.user.email
    return out
