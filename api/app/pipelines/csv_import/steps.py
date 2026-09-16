from app.pipelines.base import BaseStep
from app.pipelines.csv_import.context import ImportRowContext
from app.pipelines.csv_import.normalizers import (
    clean_text,
    normalize_price,
    normalize_stock,
    normalize_weight,
    optional_text,
    require_text,
)


class DetectEmptyRow(BaseStep):
    def execute(self, context: ImportRowContext) -> ImportRowContext:
        if all(clean_text(value) is None for value in context.raw.values()):
            return context.model_copy(update={'graceful_exit': True})
        return context


class NormalizeText(BaseStep):
    def execute(self, context: ImportRowContext) -> ImportRowContext:
        normalized = {
            **context.normalized,
            'name': require_text('name', context.raw.get('name'), 255),
            'sku': require_text('sku', context.raw.get('sku'), 64),
            'description': optional_text('description', context.raw.get('description'), 2000),
            'category': optional_text('category', context.raw.get('category'), 128),
            'image_url': optional_text('image_url', context.raw.get('image_url'), 1024),
        }
        return context.model_copy(update={'normalized': normalized})


class NormalizePricing(BaseStep):
    def execute(self, context: ImportRowContext) -> ImportRowContext:
        normalized = {**context.normalized, 'price': normalize_price(context.raw.get('price'))}
        return context.model_copy(update={'normalized': normalized})


class NormalizeInventory(BaseStep):
    def execute(self, context: ImportRowContext) -> ImportRowContext:
        normalized = {
            **context.normalized,
            'stock': normalize_stock(context.raw.get('stock')),
            'weight_kg': normalize_weight(context.raw.get('weight_kg')),
        }
        return context.model_copy(update={'normalized': normalized})


IMPORT_STEPS = (DetectEmptyRow(), NormalizeText(), NormalizePricing(), NormalizeInventory())
