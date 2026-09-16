from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings

DEFAULT_SEED_FILE = str(Path(__file__).resolve().parents[1] / 'data' / 'products.csv')


class Settings(BaseSettings):
    APPLICATION_NAME: str = 'gila-ecommerce'
    DATABASE_URL: str = 'postgresql+psycopg://ecommerce:ecommerce@localhost:5432/ecommerce'
    SEED_ON_STARTUP: bool = False
    SEED_FILE: str = DEFAULT_SEED_FILE

    @staticmethod
    @lru_cache
    def get_settings() -> 'Settings':
        return Settings()
