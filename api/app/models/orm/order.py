from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class OrderORM(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(String(32))
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    payment_reference: Mapped[str] = mapped_column(String(64))
    idempotency_key: Mapped[str | None] = mapped_column(String(128), unique=True, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    items: Mapped[list['OrderItemORM']] = relationship(
        back_populates='order', cascade='all, delete-orphan'
    )


class OrderItemORM(Base):
    __tablename__ = 'order_items'
    __table_args__ = (CheckConstraint('quantity > 0', name='ck_order_items_quantity_positive'),)

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id', ondelete='CASCADE'), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), index=True)
    quantity: Mapped[int] = mapped_column()
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    order: Mapped['OrderORM'] = relationship(back_populates='items')
