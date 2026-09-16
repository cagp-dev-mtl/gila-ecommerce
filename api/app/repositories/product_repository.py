from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import InstrumentedAttribute

from app.models.orm.product import ProductORM
from app.repositories.base_repository import BaseRepository


class ProductRepository(BaseRepository[ProductORM]):
    model = ProductORM

    def get_by_sku(self, sku: str) -> ProductORM | None:
        return self.session.scalar(select(ProductORM).where(ProductORM.sku == sku))

    def upsert_by_sku(self, data: dict) -> tuple[ProductORM, bool]:
        existing = self.get_by_sku(data['sku'])
        if existing is None:
            product = ProductORM(**data)
            self.session.add(product)
            self.session.flush()
            return product, True
        for field, value in data.items():
            setattr(existing, field, value)
        self.session.flush()
        return existing, False

    def get_many_for_update(self, ids: list[int]) -> dict[int, ProductORM]:
        rows = self.session.scalars(
            select(ProductORM).where(ProductORM.id.in_(ids)).order_by(ProductORM.id).with_for_update()
        )
        return {product.id: product for product in rows}

    def search(
        self,
        search: str | None,
        category: str | None,
        sort_column: InstrumentedAttribute,
        descending: bool,
        page: int,
        page_size: int,
    ) -> tuple[list[ProductORM], int]:
        query = self._apply_filters(select(ProductORM), search, category)
        total = self.session.scalar(select(func.count()).select_from(query.subquery())) or 0
        ordering = sort_column.desc() if descending else sort_column.asc()
        items = self.session.scalars(
            query.order_by(ordering, ProductORM.id).limit(page_size).offset((page - 1) * page_size)
        )
        return list(items), total

    def list_categories(self) -> list[str]:
        rows = self.session.scalars(
            select(ProductORM.category)
            .where(ProductORM.category.is_not(None))
            .distinct()
            .order_by(ProductORM.category)
        )
        return list(rows)

    @staticmethod
    def _apply_filters(query: Select, search: str | None, category: str | None) -> Select:
        if search:
            pattern = f'%{search}%'
            query = query.where(
                or_(
                    ProductORM.name.ilike(pattern),
                    ProductORM.sku.ilike(pattern),
                    ProductORM.description.ilike(pattern),
                )
            )
        if category:
            query = query.where(ProductORM.category == category)
        return query
