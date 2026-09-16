from pydantic import BaseModel


class ImportRowError(BaseModel):
    row: int
    reason: str


class ImportReport(BaseModel):
    total: int
    imported: int
    updated: int
    skipped: int
    errors: list[ImportRowError]
