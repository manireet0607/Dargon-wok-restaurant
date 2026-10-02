from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.api.deps import require_admin
from app.api.serializers import menu_item_out, order_out
from app.db.session import get_db
from app.models import Category, MenuItem, Order, OrderItem, User
from app.schemas.menu import (
    AvailabilityUpdate, CategoryCreate, CategoryOut, CategoryUpdate, MenuItemCreate, MenuItemOut, MenuItemUpdate,
)
from app.schemas.order import OrderOut, OrderStatusUpdate
from app.schemas.user import UserOut
from app.services import order_service
from app.services.order_service import OrderError

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


# ---------- Dashboard ----------
@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    total_orders = db.scalar(select(func.count(Order.id))) or 0
    revenue = db.scalar(select(func.coalesce(func.sum(Order.total_amount), 0)).where(Order.order_status == "delivered")) or 0
    by_status = dict(db.execute(select(Order.order_status, func.count(Order.id)).group_by(Order.order_status)).all())
    return {
        "total_orders": total_orders,
        "revenue": f"{Decimal(revenue):.2f}",  # delivered orders only
        "customers": db.scalar(select(func.count(User.id)).where(User.role == "customer")) or 0,
        "menu_items": db.scalar(select(func.count(MenuItem.id))) or 0,
        "orders_by_status": by_status,
    }


# ---------- Categories ----------
@router.get("/categories", response_model=list[CategoryOut])
def admin_categories(db: Session = Depends(get_db)):
    return db.scalars(select(Category).order_by(Category.id)).all()


@router.post("/categories", response_model=CategoryOut, status_code=201)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    if db.scalar(select(Category.id).where(Category.name == data.name.strip())):
        raise HTTPException(409, "A category with this name already exists.")
    cat = Category(name=data.name.strip(), description=data.description)
    db.add(cat)
    db.commit()
    return cat


@router.put("/categories/{cat_id}", response_model=CategoryOut)
def update_category(cat_id: int, data: CategoryUpdate, db: Session = Depends(get_db)):
    cat = db.get(Category, cat_id)
    if not cat:
        raise HTTPException(404, "Category not found.")
    clash = db.scalar(select(Category.id).where(Category.name == data.name.strip(), Category.id != cat_id))
    if clash:
        raise HTTPException(409, "A category with this name already exists.")
    cat.name, cat.description = data.name.strip(), data.description
    db.commit()
    return cat


@router.delete("/categories/{cat_id}", status_code=204)
def delete_category(cat_id: int, db: Session = Depends(get_db)):
    cat = db.get(Category, cat_id)
    if not cat:
        raise HTTPException(404, "Category not found.")
    if db.scalar(select(func.count(MenuItem.id)).where(MenuItem.category_id == cat_id)):
        raise HTTPException(409, "This category still has food items. Move or delete them first.")
    db.delete(cat)
    db.commit()


# ---------- Menu ----------
def _check_category(db: Session, category_id: int) -> None:
    if not db.get(Category, category_id):
        raise HTTPException(422, "Category does not exist.")


@router.get("/menu", response_model=list[MenuItemOut])
def admin_menu(db: Session = Depends(get_db)):
    rows = db.scalars(select(MenuItem).options(selectinload(MenuItem.category)).order_by(MenuItem.category_id, MenuItem.id)).all()
    return [menu_item_out(m) for m in rows]


@router.post("/menu", response_model=MenuItemOut, status_code=201)
def create_menu_item(data: MenuItemCreate, db: Session = Depends(get_db)):
    _check_category(db, data.category_id)
    item = MenuItem(**data.model_dump())
    db.add(item)
    db.commit()
    return menu_item_out(db.get(MenuItem, item.id))


@router.put("/menu/{item_id}", response_model=MenuItemOut)
def update_menu_item(item_id: int, data: MenuItemUpdate, db: Session = Depends(get_db)):
    item = db.get(MenuItem, item_id)
    if not item:
        raise HTTPException(404, "Menu item not found.")
    _check_category(db, data.category_id)
    for k, v in data.model_dump().items():
        setattr(item, k, v)
    db.commit()
    return menu_item_out(db.get(MenuItem, item_id))


@router.patch("/menu/{item_id}/availability", response_model=MenuItemOut)
def set_availability(item_id: int, data: AvailabilityUpdate, db: Session = Depends(get_db)):
    item = db.get(MenuItem, item_id)
    if not item:
        raise HTTPException(404, "Menu item not found.")
    item.is_available = data.is_available
    db.commit()
    return menu_item_out(db.get(MenuItem, item_id))


@router.delete("/menu/{item_id}", status_code=204)
def delete_menu_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(MenuItem, item_id)
    if not item:
        raise HTTPException(404, "Menu item not found.")
    if db.scalar(select(func.count(OrderItem.id)).where(OrderItem.menu_item_id == item_id)):
        raise HTTPException(409, "This item is part of past orders, so it cannot be deleted. Turn off availability instead.")
    try:
        db.delete(item)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "This item is in use and cannot be deleted.")


# ---------- Orders ----------
@router.get("/orders", response_model=list[OrderOut])
def admin_orders(status_filter: str | None = Query(default=None, alias="status"), db: Session = Depends(get_db)):
    q = select(Order).options(selectinload(Order.items).selectinload(OrderItem.menu_item), selectinload(Order.user)).order_by(Order.created_at.desc(), Order.id.desc())
    if status_filter:
        q = q.where(Order.order_status == status_filter)
    return [order_out(o, include_email=True) for o in db.scalars(q).all()]


@router.get("/orders/{order_id}", response_model=OrderOut)
def admin_order(order_id: int, db: Session = Depends(get_db)):
    order = order_service.get_order(db, order_id)
    if not order:
        raise HTTPException(404, "Order not found.")
    return order_out(order, include_email=True)


@router.patch("/orders/{order_id}/status", response_model=OrderOut)
def update_status(order_id: int, data: OrderStatusUpdate, db: Session = Depends(get_db)):
    order = order_service.get_order(db, order_id)
    if not order:
        raise HTTPException(404, "Order not found.")
    try:
        return order_out(order_service.change_status(db, order, data.status), include_email=True)
    except OrderError as e:
        raise HTTPException(e.status_code, e.message)


# ---------- Customers ----------
@router.get("/customers", response_model=list[UserOut])
def customers(db: Session = Depends(get_db)):
    return db.scalars(select(User).where(User.role == "customer").order_by(User.created_at.desc())).all()
