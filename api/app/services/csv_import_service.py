import csv
import io

from sqlalchemy.orm import Session

from app.api.schemas.import_report import ImportReport, ImportRowError
from app.pipelines.base import run_pipeline
from app.pipelines.csv_import.context import ImportRowContext, RowValidationError
from app.pipelines.csv_import.steps import IMPORT_STEPS
from app.repositories.product_repository import ProductRepository

REQUIRED_COLUMNS = ('name', 'sku', 'price', 'stock')
FIRST_DATA_ROW = 2


class MissingColumnsError(Exception):
    def __init__(self, columns: list[str]):
        super().__init__(', '.join(columns))
        self.columns = columns


class CsvImportService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = ProductRepository(session)

    def import_products(self, text: str) -> ImportReport:
        reader = csv.DictReader(io.StringIO(text))
        self._require_columns(reader.fieldnames)

        imported = 0
        updated = 0
        skipped = 0
        errors: list[ImportRowError] = []

        for line_number, raw in enumerate(reader, start=FIRST_DATA_ROW):
            context = ImportRowContext(row_number=line_number, raw=self._normalize_keys(raw))
            try:
                result = run_pipeline(IMPORT_STEPS, context)
            except RowValidationError as error:
                errors.append(ImportRowError(row=line_number, reason=error.reason))
                continue
            if result.graceful_exit:
                skipped += 1
                continue
            _, created = self.repository.upsert_by_sku(result.normalized)
            imported += int(created)
            updated += int(not created)

        self.session.commit()
        return ImportReport(
            total=imported + updated + skipped + len(errors),
            imported=imported,
            updated=updated,
            skipped=skipped,
            errors=errors,
        )

    @staticmethod
    def _require_columns(fieldnames: list[str] | None) -> None:
        present = set(fieldnames or [])
        missing = [column for column in REQUIRED_COLUMNS if column not in present]
        if missing:
            raise MissingColumnsError(missing)

    @staticmethod
    def _normalize_keys(raw: dict) -> dict[str, str | None]:
        return {(key or '').strip(): value for key, value in raw.items() if key is not None}
