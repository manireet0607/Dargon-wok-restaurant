from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.api.serializers import order_out
from app.db.session import get_db
from app.models import Order, OrderItem, User
from app.schemas.order import OrderCreate, OrderOut
from app.services import order_service
from app.services.order_service import OrderError

router = APIRouter(prefix="/orders", tags=["orders"])


def _own_order(db: Session, order_id: int, user: User) -> Order:
    order = order_service.get_order(db, order_id)
    # Same 404 for "missing" and "someone else's" so order IDs cannot be guessed.
    if not order or order.user_id != user.id:
        raise HTTPException(404, "Order not found.")
    return order


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(data: OrderCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        order = order_service.create_order(db, user, data)
    except OrderError as e:
        raise HTTPException(e.status_code, e.message)
    return order_out(order)


@router.get("", response_model=list[OrderOut])
def my_orders(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    orders = db.scalars(
        select(Order)
        .where(Order.user_id == user.id)
        .options(selectinload(Order.items).selectinload(OrderItem.menu_item))
        .order_by(Order.created_at.desc(), Order.id.desc())
    ).all()
    return [order_out(o) for o in orders]


@router.get("/{order_id}", response_model=OrderOut)
def order_detail(order_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return order_out(_own_order(db, order_id, user))


@router.post("/{order_id}/cancel", response_model=OrderOut)
def cancel_order(order_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Customers may only cancel, and only while the order is still pending."""
    order = _own_order(db, order_id, user)
    if order.order_status != "pending":
        raise HTTPException(409, "Only pending orders can be cancelled. Please call the restaurant.")
    try:
        return order_out(order_service.change_status(db, order, "cancelled"))
    except OrderError as e:
        raise HTTPException(e.status_code, e.message)
