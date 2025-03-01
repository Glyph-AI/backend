"""empty message

Revision ID: adab9db1738e
Revises: f6994ade93af
Create Date: 2023-03-17 12:35:14.075463

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'adab9db1738e'
down_revision = 'f6994ade93af'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('chat_messages', sa.Column('hidden', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('chat_messages', 'hidden')
    # ### end Alembic commands ###
