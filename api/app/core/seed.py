import logging
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.db import SessionFactory
from app.core.settings import Settings
from app.models.orm.product import ProductORM
from app.services.csv_import_service import CsvImportService

logger = logging.getLogger('app.seed')


def seed_catalog(session: Session, path: Path) -> None:
    existing = session.scalar(select(func.count()).select_from(ProductORM))
    if existing:
        logger.info('seed skipped: catalog already has %s products', existing)
        return
    report = CsvImportService(session).import_products(path.read_text(encoding='utf-8-sig'))
    logger.info(
        'seed complete: imported=%s updated=%s skipped=%s errors=%s',
        report.imported,
        report.updated,
        report.skipped,
        len(report.errors),
    )


def run_startup_seed() -> None:
    settings = Settings.get_settings()
    if not settings.SEED_ON_STARTUP:
        return
    with SessionFactory() as session:
        seed_catalog(session, Path(settings.SEED_FILE))
