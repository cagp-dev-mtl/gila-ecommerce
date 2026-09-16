from sqlalchemy import select

from app.models.orm.order import OrderORM
from app.repositories.base_repository import BaseRepository


class OrderRepository(BaseRepository[OrderORM]):
    model = OrderORM

    def get_by_idempotency_key(self, key: str) -> OrderORM | None:
        return self.session.scalar(select(OrderORM).where(OrderORM.idempotency_key == key))
