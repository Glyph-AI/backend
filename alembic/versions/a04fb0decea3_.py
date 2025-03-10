"""empty message

Revision ID: a04fb0decea3
Revises: ab1600dfe724
Create Date: 2023-03-28 15:03:43.934088

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a04fb0decea3'
down_revision = 'ab1600dfe724'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('subscriptions', sa.Column('stripe_subscription_id', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('subscriptions', 'stripe_subscription_id')
    # ### end Alembic commands ###
