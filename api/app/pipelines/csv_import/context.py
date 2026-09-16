from typing import Any

from app.pipelines.base import BaseContext


class RowValidationError(Exception):
    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


class ImportRowContext(BaseContext):
    row_number: int
    raw: dict[str, str | None]
    normalized: dict[str, Any] = {}
