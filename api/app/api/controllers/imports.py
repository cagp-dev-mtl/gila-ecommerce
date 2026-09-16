from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.schemas.import_report import ImportReport
from app.core.db import get_session
from app.services.csv_import_service import CsvImportService, MissingColumnsError

router = APIRouter(prefix='/products', tags=['products'])

MAX_UPLOAD_BYTES = 5 * 1024 * 1024


@router.post('/import', response_model=ImportReport)
async def import_products(
    file: UploadFile = File(...), session: Session = Depends(get_session)
) -> ImportReport:
    filename = file.filename or ''
    if not filename.lower().endswith('.csv') and file.content_type not in {'text/csv', 'application/csv'}:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail='a CSV file is required'
        )
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail='file exceeds the 5 MB limit'
        )
    try:
        text = content.decode('utf-8-sig')
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='file must be UTF-8 encoded'
        ) from None
    try:
        return CsvImportService(session).import_products(text)
    except MissingColumnsError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'missing required columns: {", ".join(error.columns)}',
        ) from None
