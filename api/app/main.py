import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.controllers import health, imports, orders, products
from app.core.seed import run_startup_seed
from app.core.settings import Settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')


@asynccontextmanager
async def lifespan(_: FastAPI):
    run_startup_seed()
    yield


def create_app() -> FastAPI:
    settings = Settings.get_settings()
    application = FastAPI(
        title=settings.APPLICATION_NAME,
        docs_url='/api/docs',
        openapi_url='/api/openapi.json',
        lifespan=lifespan,
    )
    application.include_router(health.router, prefix='/api')
    application.include_router(products.router, prefix='/api')
    application.include_router(imports.router, prefix='/api')
    application.include_router(orders.router, prefix='/api')
    return application


app = create_app()
