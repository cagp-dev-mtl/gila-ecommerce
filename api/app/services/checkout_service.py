from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.schemas.order import CheckoutRequest
from app.models.orm.order import OrderItemORM, OrderORM
from app.pipelines.base import run_pipeline
from app.pipelines.checkout.context import CheckoutContext, OrderPlan, ProductSnapshot, RequestedItem
from app.pipelines.checkout.steps import CHECKOUT_STEPS
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository


class CheckoutService:
    def __init__(self, session: Session):
        self.session = session
        self.products = ProductRepository(session)
        self.orders = OrderRepository(session)

    def checkout(self, request: CheckoutRequest, idempotency_key: str | None) -> OrderORM:
        if idempotency_key:
            existing = self.orders.get_by_idempotency_key(idempotency_key)
            if existing is not None:
                return existing

        items = self._aggregate(request)
        locked = self.products.get_many_for_update([item.product_id for item in items])
        context = CheckoutContext(
            items=items,
            products={
                product_id: ProductSnapshot(id=product.id, price=product.price, stock=product.stock)
                for product_id, product in locked.items()
            },
        )
        result = run_pipeline(CHECKOUT_STEPS, context)
        try:
            order = self._persist(result.plan, locked, idempotency_key)
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            if idempotency_key:
                existing = self.orders.get_by_idempotency_key(idempotency_key)
                if existing is not None:
                    return existing
            raise
        self.session.refresh(order)
        return order

    def _persist(self, plan: OrderPlan, locked: dict, idempotency_key: str | None) -> OrderORM:
        order = OrderORM(
            status='paid',
            total=plan.total,
            payment_reference=f'FAKE-{uuid4().hex[:12].upper()}',
            idempotency_key=idempotency_key,
        )
        for line in plan.lines:
            order.items.append(
                OrderItemORM(
                    product_id=line.product_id, quantity=line.quantity, unit_price=line.unit_price
                )
            )
            locked[line.product_id].stock -= line.quantity
        return self.orders.add(order)

    @staticmethod
    def _aggregate(request: CheckoutRequest) -> tuple[RequestedItem, ...]:
        totals: dict[int, int] = {}
        for item in request.items:
            totals[item.product_id] = totals.get(item.product_id, 0) + item.quantity
        return tuple(
            RequestedItem(product_id=product_id, quantity=quantity)
            for product_id, quantity in totals.items()
        )
