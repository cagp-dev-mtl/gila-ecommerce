from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APPLICATION_NAME: str = 'gila-ecommerce'
    DATABASE_URL: str = 'postgresql+psycopg://ecommerce:ecommerce@localhost:5432/ecommerce'

    @staticmethod
    @lru_cache
    def get_settings() -> 'Settings':
        return Settings()
