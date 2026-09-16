from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.api.schemas.order import CheckoutRequest, OrderRead
from app.core.db import get_session
from app.models.orm.order import OrderORM
from app.pipelines.checkout.context import InsufficientStockError, ProductNotFoundError
from app.repositories.order_repository import OrderRepository
from app.services.checkout_service import CheckoutService

router = APIRouter(prefix='/orders', tags=['orders'])


@router.post('', response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: CheckoutRequest,
    idempotency_key: str | None = Header(default=None),
    session: Session = Depends(get_session),
) -> OrderORM:
    try:
        return CheckoutService(session).checkout(payload, idempotency_key)
    except ProductNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f'product {error.product_id} not found'
        ) from None
    except InsufficientStockError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f'insufficient stock for product {error.product_id}: '
                f'requested {error.requested}, available {error.available}'
            ),
        ) from None


@router.get('/{order_id}', response_model=OrderRead)
def get_order(order_id: int, session: Session = Depends(get_session)) -> OrderORM:
    order = OrderRepository(session).get(order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='order not found')
    return order
