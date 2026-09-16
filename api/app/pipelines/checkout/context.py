from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.pipelines.base import BaseContext


class CheckoutError(Exception):
    pass


class ProductNotFoundError(CheckoutError):
    def __init__(self, product_id: int):
        super().__init__(str(product_id))
        self.product_id = product_id


class InsufficientStockError(CheckoutError):
    def __init__(self, product_id: int, requested: int, available: int):
        super().__init__(str(product_id))
        self.product_id = product_id
        self.requested = requested
        self.available = available


class RequestedItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    product_id: int
    quantity: int


class ProductSnapshot(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int
    price: Decimal
    stock: int


class OrderLine(BaseModel):
    model_config = ConfigDict(frozen=True)

    product_id: int
    quantity: int
    unit_price: Decimal


class OrderPlan(BaseModel):
    model_config = ConfigDict(frozen=True)

    lines: tuple[OrderLine, ...]
    total: Decimal


class CheckoutContext(BaseContext):
    items: tuple[RequestedItem, ...]
    products: dict[int, ProductSnapshot]
    plan: OrderPlan | None = None
