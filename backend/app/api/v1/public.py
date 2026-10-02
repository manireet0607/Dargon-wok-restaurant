from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.serializers import menu_item_out
from app.core.config import get_settings
from app.db.session import get_db
from app.models import Category, MenuItem
from app.schemas.menu import CategoryOut, MenuItemOut
from app.schemas.order import PublicConfig
from app.services.order_service import money

router = APIRouter(tags=["menu"])


@router.get("/config", response_model=PublicConfig)
def public_config():
    """Fees the frontend uses for its cart estimate. The server recalculates at checkout."""
    s = get_settings()
    return PublicConfig(
        delivery_fee=money(s.delivery_fee), tax_rate=str(s.tax_rate), free_delivery_above=money(s.free_delivery_above)
    )


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.scalars(select(Category).order_by(Category.id)).all()


@router.get("/menu", response_model=list[MenuItemOut])
def list_menu(
    category_id: int | None = None,
    food_type: str | None = Query(default=None, pattern="^(veg|non_veg)$"),
    search: str | None = Query(default=None, max_length=100),
    db: Session = Depends(get_db),
):
    q = select(MenuItem).options(selectinload(MenuItem.category)).order_by(MenuItem.category_id, MenuItem.id)
    if category_id:
        q = q.where(MenuItem.category_id == category_id)
    if food_type:
        q = q.where(MenuItem.food_type == food_type)
    if search:
        q = q.where(MenuItem.name.ilike(f"%{search}%"))
    return [menu_item_out(m) for m in db.scalars(q).all()]


@router.get("/menu/{item_id}", response_model=MenuItemOut)
def get_menu_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(MenuItem, item_id)
    if not item:
        raise HTTPException(404, "Menu item not found.")
    return menu_item_out(item)
