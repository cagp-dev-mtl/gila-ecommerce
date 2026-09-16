from fastapi import FastAPI

from app.api.controllers import health, imports, products
from app.core.settings import Settings


def create_app() -> FastAPI:
    settings = Settings.get_settings()
    application = FastAPI(title=settings.APPLICATION_NAME, docs_url='/api/docs', openapi_url='/api/openapi.json')
    application.include_router(health.router, prefix='/api')
    application.include_router(products.router, prefix='/api')
    application.include_router(imports.router, prefix='/api')
    return application


app = create_app()
