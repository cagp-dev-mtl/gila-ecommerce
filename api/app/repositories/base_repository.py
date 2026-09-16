from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import Base

ModelType = TypeVar('ModelType', bound=Base)


class BaseRepository(Generic[ModelType]):
    model: type[ModelType]

    def __init__(self, session: Session):
        self.session = session

    def get(self, entity_id: int) -> ModelType | None:
        return self.session.get(self.model, entity_id)

    def list(self) -> list[ModelType]:
        return list(self.session.scalars(select(self.model).order_by(self.model.id)))

    def add(self, entity: ModelType) -> ModelType:
        self.session.add(entity)
        self.session.flush()
        return entity

    def delete(self, entity: ModelType) -> None:
        self.session.delete(entity)
        self.session.flush()
