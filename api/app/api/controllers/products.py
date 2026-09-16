import math
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.schemas.product import ProductCreate, ProductPage, ProductRead, ProductUpdate
from app.core.db import get_session
from app.models.orm.product import ProductORM
from app.repositories.product_repository import ProductRepository

router = APIRouter(prefix='/products', tags=['products'])

SORT_COLUMNS = {
    'name': ProductORM.name,
    'price': ProductORM.price,
    'newest': ProductORM.created_at,
}


@router.get('', response_model=ProductPage)
def list_products(
    search: str | None = Query(default=None, max_length=255),
    category: str | None = Query(default=None, max_length=128),
    sort: Literal['name', 'price', 'newest'] = 'name',
    order: Literal['asc', 'desc'] = 'asc',
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=12, ge=1, le=100),
    session: Session = Depends(get_session),
) -> ProductPage:
    items, total = ProductRepository(session).search(
        search, category, SORT_COLUMNS[sort], order == 'desc', page, page_size
    )
    return ProductPage(
        items=[ProductRead.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total else 0,
    )


@router.get('/categories', response_model=list[str])
def list_categories(session: Session = Depends(get_session)) -> list[str]:
    return ProductRepository(session).list_categories()


@router.post('', response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, session: Session = Depends(get_session)) -> ProductORM:
    repository = ProductRepository(session)
    try:
        product = repository.add(ProductORM(**payload.model_dump()))
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='sku already exists') from None
    session.refresh(product)
    return product


@router.get('/{product_id}', response_model=ProductRead)
def get_product(product_id: int, session: Session = Depends(get_session)) -> ProductORM:
    product = ProductRepository(session).get(product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='product not found')
    return product


@router.put('/{product_id}', response_model=ProductRead)
def update_product(
    product_id: int, payload: ProductUpdate, session: Session = Depends(get_session)
) -> ProductORM:
    repository = ProductRepository(session)
    product = repository.get(product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='product not found')
    for field, value in payload.model_dump().items():
        setattr(product, field, value)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='sku already exists') from None
    session.refresh(product)
    return product


@router.delete('/{product_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, session: Session = Depends(get_session)) -> None:
    repository = ProductRepository(session)
    product = repository.get(product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='product not found')
    try:
        repository.delete(product)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail='product belongs to existing orders'
        ) from None
