"""empty message

Revision ID: 8534aa075072
Revises: a04fb0decea3
Create Date: 2023-03-29 16:00:46.072803

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8534aa075072'
down_revision = 'a04fb0decea3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('chat_messages', sa.Column('archived', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('chat_messages', 'archived')
    # ### end Alembic commands ###
