from decimal import Decimal

import pytest

from app.pipelines.csv_import.context import RowValidationError
from app.pipelines.csv_import.normalizers import (
    clean_text,
    normalize_price,
    normalize_stock,
    normalize_weight,
    optional_text,
    require_text,
)


def test_clean_text_strips_and_nullifies():
    assert clean_text('  hi  ') == 'hi'
    assert clean_text('   ') is None
    assert clean_text(None) is None


def test_optional_text_respects_length():
    assert optional_text('name', 'abc', 10) == 'abc'
    assert optional_text('name', None, 10) is None
    with pytest.raises(RowValidationError):
        optional_text('name', 'abcdef', 3)


def test_require_text_rejects_blank():
    assert require_text('name', ' x ', 10) == 'x'
    with pytest.raises(RowValidationError):
        require_text('name', '   ', 10)


def test_normalize_price_variants():
    assert normalize_price('$29.99') == Decimal('29.99')
    assert normalize_price('1,299.50') == Decimal('1299.50')
    assert normalize_price('0.00') == Decimal('0.00')
    with pytest.raises(RowValidationError):
        normalize_price('free')
    with pytest.raises(RowValidationError):
        normalize_price('-5')
    with pytest.raises(RowValidationError):
        normalize_price('   ')


def test_normalize_stock_variants():
    assert normalize_stock('10') == 10
    with pytest.raises(RowValidationError):
        normalize_stock('-1')
    with pytest.raises(RowValidationError):
        normalize_stock('abc')
    with pytest.raises(RowValidationError):
        normalize_stock('')


def test_normalize_weight_variants():
    assert normalize_weight('0.35') == Decimal('0.350')
    assert normalize_weight('') is None
    with pytest.raises(RowValidationError):
        normalize_weight('-0.1')
    with pytest.raises(RowValidationError):
        normalize_weight('heavy')
