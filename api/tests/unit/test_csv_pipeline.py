from decimal import Decimal

import pytest

from app.pipelines.base import BaseStep, run_pipeline
from app.pipelines.csv_import.context import ImportRowContext, RowValidationError
from app.pipelines.csv_import.steps import IMPORT_STEPS, DetectEmptyRow


def make_context(raw):
    return ImportRowContext(row_number=2, raw=raw)


def test_detect_empty_row_sets_graceful_exit():
    result = DetectEmptyRow().execute(make_context({'name': ' ', 'sku': '', 'price': None}))
    assert result.graceful_exit is True


def test_detect_non_empty_row_passes():
    result = DetectEmptyRow().execute(make_context({'name': 'X', 'sku': 'S', 'price': '1'}))
    assert result.graceful_exit is False


def test_full_pipeline_normalizes_valid_row():
    raw = {
        'name': ' Shoe ',
        'sku': 'S-1',
        'description': '',
        'category': 'Foot',
        'price': '$10.5',
        'stock': '3',
        'weight_kg': '0.2',
    }
    result = run_pipeline(IMPORT_STEPS, make_context(raw))
    assert result.normalized['name'] == 'Shoe'
    assert result.normalized['description'] is None
    assert result.normalized['price'] == Decimal('10.50')
    assert result.normalized['stock'] == 3
    assert result.normalized['weight_kg'] == Decimal('0.200')


def test_pipeline_stops_on_empty_row():
    raw = {'name': '', 'sku': '', 'price': '', 'stock': '', 'weight_kg': ''}
    result = run_pipeline(IMPORT_STEPS, make_context(raw))
    assert result.graceful_exit is True
    assert result.normalized == {}


def test_pipeline_raises_on_invalid_row():
    raw = {'name': '', 'sku': 'S', 'price': '1', 'stock': '1', 'weight_kg': ''}
    with pytest.raises(RowValidationError):
        run_pipeline(IMPORT_STEPS, make_context(raw))


def test_base_step_is_abstract():
    with pytest.raises(NotImplementedError):
        BaseStep().execute(make_context({}))
