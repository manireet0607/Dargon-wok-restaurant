from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

ORDER_STATUSES = ("pending", "confirmed", "preparing", "out_for_delivery", "delivered", "cancelled")
PAYMENT_STATUSES = ("pending", "paid", "failed", "refunded")


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        CheckConstraint("order_status IN ('pending','confirmed','preparing','out_for_delivery','delivered','cancelled')", name="ck_orders_status"),
        CheckConstraint("payment_status IN ('pending','paid','failed','refunded')", name="ck_orders_payment_status"),
        CheckConstraint("total_amount >= 0", name="ck_orders_total_nonneg"),
        Index("ix_orders_user_created", "user_id", "created_at"),
        Index("ix_orders_status", "order_status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    order_number: Mapped[str] = mapped_column(String(32), unique=True)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    delivery_fee: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"))
    payment_method: Mapped[str] = mapped_column(String(20), default="cod", server_default="cod")
    payment_status: Mapped[str] = mapped_column(String(20), default="pending", server_default="pending")
    order_status: Mapped[str] = mapped_column(String(20), default="pending", server_default="pending")
    customer_name: Mapped[str] = mapped_column(String(100))
    customer_phone: Mapped[str] = mapped_column(String(20))
    delivery_address: Mapped[str] = mapped_column(Text)
    special_instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"
    __table_args__ = (CheckConstraint("quantity > 0", name="ck_order_items_qty_positive"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), index=True)
    menu_item_id: Mapped[int] = mapped_column(ForeignKey("menu_items.id", ondelete="RESTRICT"), index=True)
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))  # price when the order was placed
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem")
