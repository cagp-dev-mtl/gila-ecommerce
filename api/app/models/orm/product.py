from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class ProductORM(Base):
    __tablename__ = 'products'
    __table_args__ = (
        CheckConstraint('price >= 0', name='ck_products_price_non_negative'),
        CheckConstraint('stock >= 0', name='ck_products_stock_non_negative'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str | None] = mapped_column(String(2000), default=None)
    category: Mapped[str | None] = mapped_column(String(128), index=True, default=None)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    stock: Mapped[int] = mapped_column(default=0)
    weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(10, 3), default=None)
    image_url: Mapped[str | None] = mapped_column(String(1024), default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
