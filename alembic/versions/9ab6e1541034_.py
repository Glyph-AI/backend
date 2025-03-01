"""empty message

Revision ID: 9ab6e1541034
Revises: 3e45e98159e0
Create Date: 2023-04-28 18:10:12.462859

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm
from app.models import Tool, BotTool, Bot


# revision identifiers, used by Alembic.
revision = '9ab6e1541034'
down_revision = '3e45e98159e0'
branch_labels = None
depends_on = None

tools = [
    {
        "name": "Document Search",
        "description": "Searches Documents the user has uploaded to the database.",
        "internal_filename": "document_search",
        "class_name": "DocumentSearch"
    },
    {
        "name": "Google Search",
        "description": "Searches Google for relevant information.",
        "internal_filename": "google_search",
        "class_name": "GoogleSearch"
    },
    {
        "name": "CodeGPT",
        "description": "Handles computer code related requests.",
        "internal_filename": "code_gpt",
        "class_name": "CodeGpt"
    },
    {
        "name": "Respond to User",
        "description": "If you have the answer to the question, this tool provides it to the user.",
        "internal_filename": "respond_to_user",
        "class_name": "RespondToUser"
    }
]


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tools',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(), nullable=False),
                    sa.Column('class_name', sa.String(), nullable=False),
                    sa.Column('internal_filename',
                              sa.String(), nullable=False),
                    sa.Column('description', sa.String(), nullable=False),
                    sa.Column('created_at', sa.DateTime(timezone=True),
                              server_default=sa.text('now()'), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_tools_id'), 'tools', ['id'], unique=False)
    op.create_table('bot_tools',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('bot_id', sa.Integer(), nullable=False),
                    sa.Column('tool_id', sa.Integer(), nullable=False),
                    sa.Column('enabled', sa.Boolean(), nullable=False),
                    sa.Column('created_at', sa.DateTime(timezone=True),
                              server_default=sa.text('now()'), nullable=True),
                    sa.ForeignKeyConstraint(['bot_id'], ['bots.id'], ),
                    sa.ForeignKeyConstraint(['tool_id'], ['tools.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_bot_tools_bot_id'),
                    'bot_tools', ['bot_id'], unique=False)
    op.create_index(op.f('ix_bot_tools_id'), 'bot_tools', ['id'], unique=False)
    op.create_index(op.f('ix_bot_tools_tool_id'),
                    'bot_tools', ['tool_id'], unique=False)
    # ### end Alembic commands ###

    # Create tools and assign tools to bots
    bind = op.get_bind()
    session = orm.Session(bind=bind)
    for t in tools:
        new_tool = Tool(**t)
        session.add(new_tool)
        session.commit()

        # create bot tools
        bots = session.query(Bot).all()
        for b in bots:
            new_bot_tool = BotTool(tool_id=new_tool.id,
                                   bot_id=b.id, enabled=True)
            session.add(new_bot_tool)
            session.commit()


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_bot_tools_tool_id'), table_name='bot_tools')
    op.drop_index(op.f('ix_bot_tools_id'), table_name='bot_tools')
    op.drop_index(op.f('ix_bot_tools_bot_id'), table_name='bot_tools')
    op.drop_table('bot_tools')
    op.drop_index(op.f('ix_tools_id'), table_name='tools')
    op.drop_table('tools')
    # ### end Alembic commands ###
