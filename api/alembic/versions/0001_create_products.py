from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = '0001_create_products'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('sku', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=2000), nullable=True),
        sa.Column('category', sa.String(length=128), nullable=True),
        sa.Column('price', sa.Numeric(10, 2), nullable=False),
        sa.Column('stock', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('weight_kg', sa.Numeric(10, 3), nullable=True),
        sa.Column('image_url', sa.String(length=1024), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint('price >= 0', name='ck_products_price_non_negative'),
        sa.CheckConstraint('stock >= 0', name='ck_products_stock_non_negative'),
    )
    op.create_index('ix_products_sku', 'products', ['sku'], unique=True)
    op.create_index('ix_products_name', 'products', ['name'])
    op.create_index('ix_products_category', 'products', ['category'])


def downgrade() -> None:
    op.drop_index('ix_products_category', table_name='products')
    op.drop_index('ix_products_name', table_name='products')
    op.drop_index('ix_products_sku', table_name='products')
    op.drop_table('products')
