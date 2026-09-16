from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CheckoutItem(BaseModel):
    product_id: int
    quantity: int = Field(ge=1)


class CheckoutRequest(BaseModel):
    items: list[CheckoutItem] = Field(min_length=1)


class OrderItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    quantity: int
    unit_price: Decimal


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    total: Decimal
    payment_reference: str
    idempotency_key: str | None
    created_at: datetime
    items: list[OrderItemRead]
