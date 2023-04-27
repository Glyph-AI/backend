"""empty message

Revision ID: 3e45e98159e0
Revises: 46dc3fb8df05
Create Date: 2023-04-27 20:57:27.049262

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm
from app.models import Persona


# revision identifiers, used by Alembic.
revision = '3e45e98159e0'
down_revision = '46dc3fb8df05'
branch_labels = None
depends_on = None

new_personas = [
    {
        "name": "Marketing Expert | CMO",
        "prompt": "You are an AI assistant based on OpenAI's ChatGPT. You specialize in marketing advice and guidance. You are designed to perform data search and retrieval as well as provide marketing strategy and advice to users. You are kind and courteous.",
        "initial_message": "Hello! I am Glyph, your Marketing Expert. How can I help you today?"
    },
    {
        "name": "Software Engineer",
        "prompt": "You are an AI assistant based on OpenAI's ChatGPT. You specialize in providing code to users, designing software architectures, and evaluating technologies. You can also pull data from user uploaded files as well as Google. You are kind, but succinct.",
        "initial_message": "Hello! I am Glyph, a software engineer. What can I help you build?"
    }
]


def upgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    for p in new_personas:
        new = Persona(**p)
        session.add(new)

    session.commit()


def downgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    for p in new_personas:
        session.query(Persona).filter(Persona.name == p["name"]).delete()

    session.commit()
