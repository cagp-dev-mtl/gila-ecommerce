from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductBase(BaseModel):
    sku: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    category: str | None = Field(default=None, max_length=128)
    price: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    stock: int = Field(default=0, ge=0)
    weight_kg: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=3)
    image_url: str | None = Field(default=None, max_length=1024)

    @field_validator('sku', 'name')
    @classmethod
    def reject_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError('must not be blank')
        return stripped


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    pass


class ProductRead(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class ProductPage(BaseModel):
    items: list[ProductRead]
    total: int
    page: int
    page_size: int
    pages: int
