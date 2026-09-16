import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from app.core.db import Base, engine
from app.core.settings import Settings
from app.main import app


def _ensure_database():
    url = make_url(Settings.get_settings().DATABASE_URL)
    if 'test' not in (url.database or ''):
        pytest.exit('refusing to run against a non-test database')
    admin = create_engine(url.set(database='postgres'), isolation_level='AUTOCOMMIT')
    with admin.connect() as connection:
        exists = connection.execute(
            text('SELECT 1 FROM pg_database WHERE datname = :name'), {'name': url.database}
        ).scalar()
        if not exists:
            connection.execute(text(f'CREATE DATABASE "{url.database}"'))
    admin.dispose()


@pytest.fixture(scope='session', autouse=True)
def schema():
    _ensure_database()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture(autouse=True)
def clean_tables():
    yield
    with engine.begin() as connection:
        connection.execute(text('TRUNCATE order_items, orders, products RESTART IDENTITY CASCADE'))


@pytest.fixture
def client():
    return TestClient(app)
