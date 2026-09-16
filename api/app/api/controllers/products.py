from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.schemas.product import ProductCreate, ProductRead, ProductUpdate
from app.core.db import get_session
from app.models.orm.product import ProductORM
from app.repositories.product_repository import ProductRepository

router = APIRouter(prefix='/products', tags=['products'])


@router.get('', response_model=list[ProductRead])
def list_products(session: Session = Depends(get_session)) -> list[ProductORM]:
    return ProductRepository(session).list()


@router.post('', response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, session: Session = Depends(get_session)) -> ProductORM:
    repository = ProductRepository(session)
    if repository.get_by_sku(payload.sku):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='sku already exists')
    product = repository.add(ProductORM(**payload.model_dump()))
    session.commit()
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
    conflict = repository.get_by_sku(payload.sku)
    if conflict is not None and conflict.id != product_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='sku already exists')
    for field, value in payload.model_dump().items():
        setattr(product, field, value)
    session.commit()
    session.refresh(product)
    return product


@router.delete('/{product_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, session: Session = Depends(get_session)) -> None:
    repository = ProductRepository(session)
    product = repository.get(product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='product not found')
    repository.delete(product)
    session.commit()
