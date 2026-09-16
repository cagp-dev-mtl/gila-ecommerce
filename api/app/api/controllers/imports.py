from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.schemas.import_report import ImportReport
from app.core.db import get_session
from app.services.csv_import_service import CsvImportService, MissingColumnsError

router = APIRouter(prefix='/products', tags=['products'])


@router.post('/import', response_model=ImportReport)
async def import_products(
    file: UploadFile = File(...), session: Session = Depends(get_session)
) -> ImportReport:
    filename = file.filename or ''
    if not filename.lower().endswith('.csv') and file.content_type not in {'text/csv', 'application/csv'}:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail='a CSV file is required'
        )
    content = await file.read()
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
