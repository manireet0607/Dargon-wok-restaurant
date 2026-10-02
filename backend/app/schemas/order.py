from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.common import Money
from app.schemas.user import clean_phone


class OrderItemIn(BaseModel):
    menu_item_id: int
    quantity: int = Field(ge=1, le=50)


class OrderCreate(BaseModel):
    """Note: there is no price or total here on purpose. The server calculates them."""
    items: list[OrderItemIn] = Field(min_length=1, max_length=50)
    customer_name: str = Field(min_length=2, max_length=100)
    customer_phone: str
    delivery_address: str = Field(min_length=10, max_length=500)
    special_instructions: str | None = Field(default=None, max_length=500)
    payment_method: Literal["cod"] = "cod"

    _phone = field_validator("customer_phone")(clean_phone)


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    menu_item_id: int
    item_name: str | None = None
    quantity: int
    unit_price: Money
    subtotal: Money


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    order_number: str
    subtotal: Money
    delivery_fee: Money
    tax_amount: Money
    total_amount: Money
    payment_method: str
    payment_status: str
    order_status: str
    customer_name: str
    customer_phone: str
    delivery_address: str
    special_instructions: str | None
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemOut]
    customer_email: str | None = None


class OrderStatusUpdate(BaseModel):
    status: Literal["pending", "confirmed", "preparing", "out_for_delivery", "delivered", "cancelled"]


class PublicConfig(BaseModel):
    currency: str = "INR"
    delivery_fee: Money
    tax_rate: str
    free_delivery_above: Money
