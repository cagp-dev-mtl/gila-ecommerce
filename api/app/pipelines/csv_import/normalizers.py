from decimal import Decimal, InvalidOperation

from app.pipelines.csv_import.context import RowValidationError


def clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def optional_text(field: str, value: str | None, max_length: int) -> str | None:
    cleaned = clean_text(value)
    if cleaned is not None and len(cleaned) > max_length:
        raise RowValidationError(f'{field} exceeds {max_length} characters')
    return cleaned


def require_text(field: str, value: str | None, max_length: int) -> str:
    cleaned = optional_text(field, value, max_length)
    if cleaned is None:
        raise RowValidationError(f'{field} is required')
    return cleaned


def normalize_price(value: str | None) -> Decimal:
    cleaned = clean_text(value)
    if cleaned is None:
        raise RowValidationError('price is required')
    candidate = cleaned.lstrip('$').replace(',', '').strip()
    try:
        price = Decimal(candidate)
    except InvalidOperation:
        raise RowValidationError(f'price is not a valid number: {cleaned}') from None
    if price < 0:
        raise RowValidationError('price must not be negative')
    return price.quantize(Decimal('0.01'))


def normalize_stock(value: str | None) -> int:
    cleaned = clean_text(value)
    if cleaned is None:
        raise RowValidationError('stock is required')
    try:
        stock = int(cleaned)
    except ValueError:
        raise RowValidationError(f'stock is not a valid integer: {cleaned}') from None
    if stock < 0:
        raise RowValidationError('stock must not be negative')
    return stock


def normalize_weight(value: str | None) -> Decimal | None:
    cleaned = clean_text(value)
    if cleaned is None:
        return None
    try:
        weight = Decimal(cleaned)
    except InvalidOperation:
        raise RowValidationError(f'weight_kg is not a valid number: {cleaned}') from None
    if weight < 0:
        raise RowValidationError('weight_kg must not be negative')
    return weight.quantize(Decimal('0.001'))
