from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = '0002_create_orders'
down_revision: Union[str, None] = '0001_create_products'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('total', sa.Numeric(12, 2), nullable=False),
        sa.Column('payment_reference', sa.String(length=64), nullable=False),
        sa.Column('idempotency_key', sa.String(length=128), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_orders_idempotency_key', 'orders', ['idempotency_key'], unique=True)
    op.create_table(
        'order_items',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('order_id', sa.Integer(), sa.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Numeric(10, 2), nullable=False),
        sa.CheckConstraint('quantity > 0', name='ck_order_items_quantity_positive'),
    )
    op.create_index('ix_order_items_order_id', 'order_items', ['order_id'])
    op.create_index('ix_order_items_product_id', 'order_items', ['product_id'])


def downgrade() -> None:
    op.drop_index('ix_order_items_product_id', table_name='order_items')
    op.drop_index('ix_order_items_order_id', table_name='order_items')
    op.drop_table('order_items')
    op.drop_index('ix_orders_idempotency_key', table_name='orders')
    op.drop_table('orders')
