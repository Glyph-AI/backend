"""empty message

Revision ID: ee130f24a9b5
Revises: 1dbb561a018d
Create Date: 2023-07-10 20:58:50.154987

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ee130f24a9b5'
down_revision = '1dbb561a018d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('products',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('message_limit', sa.Integer(), nullable=False),
    sa.Column('bot_limit', sa.Integer(), nullable=False),
    sa.Column('text_limit', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_products_id'), 'products', ['id'], unique=False)
    op.create_index(op.f('ix_products_name'), 'products', ['name'], unique=False)
    op.add_column('price_tiers', sa.Column('product_id', sa.String(), nullable=True))
    op.create_foreign_key(None, 'price_tiers', 'products', ['product_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'price_tiers', type_='foreignkey')
    op.drop_column('price_tiers', 'product_id')
    op.drop_index(op.f('ix_products_name'), table_name='products')
    op.drop_index(op.f('ix_products_id'), table_name='products')
    op.drop_table('products')
    # ### end Alembic commands ###
