from sqlalchemy import select

from app.models.orm.product import ProductORM
from app.repositories.base_repository import BaseRepository


class ProductRepository(BaseRepository[ProductORM]):
    model = ProductORM

    def get_by_sku(self, sku: str) -> ProductORM | None:
        return self.session.scalar(select(ProductORM).where(ProductORM.sku == sku))
