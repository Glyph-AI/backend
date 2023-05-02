"""empty message

Revision ID: 8c1c0c9e8bbc
Revises: aed47ca0d5c0
Create Date: 2023-04-25 02:03:43.250942

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm
from app.models import Bot, BotUser


# revision identifiers, used by Alembic.
revision = '8c1c0c9e8bbc'
down_revision = 'aed47ca0d5c0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind)
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bot_users',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=True),
                    sa.Column('bot_id', sa.Integer(), nullable=True),
                    sa.Column('creator', sa.Boolean(), nullable=True),
                    sa.Column('created_at', sa.DateTime(timezone=True),
                              server_default=sa.text('now()'), nullable=True),
                    sa.ForeignKeyConstraint(['bot_id'], ['bots.id'], ),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_bot_users_id'), 'bot_users', ['id'], unique=False)
    op.drop_constraint('bots_user_id_fkey', 'bots', type_='foreignkey')
    bots = session.query(Bot).all()
    for b in bots:
        new_bu = BotUser(bot_id=b.id, user_id=b.user_id, creator=True)
        session.add(new_bu)

    session.commit()
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key('bots_user_id_fkey', 'bots',
                          'users', ['user_id'], ['id'])
    op.drop_index(op.f('ix_bot_users_id'), table_name='bot_users')
    op.drop_table('bot_users')
    # ### end Alembic commands ###
