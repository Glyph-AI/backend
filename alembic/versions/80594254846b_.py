"""empty message

Revision ID: 80594254846b
Revises: 2064e145e5d4
Create Date: 2023-05-24 15:50:15.000033

"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision = '80594254846b'
down_revision = '2064e145e5d4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('embeddings', 'vector')
    op.alter_column("embeddings", "vector_new", new_column_name="vector")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("embeddings", "vector", new_column_name="vector_new")
    op.add_column('embeddings', sa.Column(
        'vector', Vector(dim=1536), nullable=True))
    # ### end Alembic commands ###
