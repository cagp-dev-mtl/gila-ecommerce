from decimal import Decimal

from app.pipelines.base import BaseStep
from app.pipelines.checkout.context import (
    CheckoutContext,
    InsufficientStockError,
    OrderLine,
    OrderPlan,
    ProductNotFoundError,
)


class ValidateAvailability(BaseStep):
    def execute(self, context: CheckoutContext) -> CheckoutContext:
        for item in context.items:
            snapshot = context.products.get(item.product_id)
            if snapshot is None:
                raise ProductNotFoundError(item.product_id)
            if snapshot.stock < item.quantity:
                raise InsufficientStockError(item.product_id, item.quantity, snapshot.stock)
        return context


class BuildOrderPlan(BaseStep):
    def execute(self, context: CheckoutContext) -> CheckoutContext:
        lines = tuple(
            OrderLine(
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=context.products[item.product_id].price,
            )
            for item in context.items
        )
        total = sum((line.unit_price * line.quantity for line in lines), Decimal('0'))
        return context.model_copy(update={'plan': OrderPlan(lines=lines, total=total)})


CHECKOUT_STEPS = (ValidateAvailability(), BuildOrderPlan())
