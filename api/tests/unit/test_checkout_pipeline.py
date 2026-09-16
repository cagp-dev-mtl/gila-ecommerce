from decimal import Decimal

import pytest

from app.pipelines.base import run_pipeline
from app.pipelines.checkout.context import (
    CheckoutContext,
    InsufficientStockError,
    ProductNotFoundError,
    ProductSnapshot,
    RequestedItem,
)
from app.pipelines.checkout.steps import CHECKOUT_STEPS, ValidateAvailability


def make_context(items, products):
    return CheckoutContext(items=items, products=products)


def test_validate_availability_missing_product():
    context = make_context((RequestedItem(product_id=1, quantity=1),), {})
    with pytest.raises(ProductNotFoundError):
        ValidateAvailability().execute(context)


def test_validate_availability_insufficient_stock():
    context = make_context(
        (RequestedItem(product_id=1, quantity=5),),
        {1: ProductSnapshot(id=1, price=Decimal('2'), stock=3)},
    )
    with pytest.raises(InsufficientStockError) as error:
        ValidateAvailability().execute(context)
    assert error.value.available == 3


def test_build_order_plan_totals_with_snapshot_price():
    products = {
        1: ProductSnapshot(id=1, price=Decimal('2.50'), stock=10),
        2: ProductSnapshot(id=2, price=Decimal('4.00'), stock=10),
    }
    items = (RequestedItem(product_id=1, quantity=2), RequestedItem(product_id=2, quantity=1))
    result = run_pipeline(CHECKOUT_STEPS, make_context(items, products))
    assert result.plan.total == Decimal('9.00')
    assert len(result.plan.lines) == 2
