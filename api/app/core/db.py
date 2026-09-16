from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.settings import Settings


class Base(DeclarativeBase):
    pass


engine = create_engine(Settings.get_settings().DATABASE_URL, pool_pre_ping=True)
SessionFactory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_session() -> Iterator[Session]:
    session = SessionFactory()
    try:
        yield session
    finally:
        session.close()
