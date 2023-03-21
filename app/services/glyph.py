import time
import openai
from sqlalchemy.orm import Session
import os

from app.models import Embedding, ChatMessage
import app.schemas as schemas
from app.crud import chat_message as chat_message_crud

openai.api_key = os.environ.get(
    "OPENAI_KEY", "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")


class Glyph:
    def __init__(self):
        self.sleep_time = 1

    def embed_message(self, message: str):
        query_embed = openai.Embedding.create(
            input=message, model="text-embedding-ada-002")['data'][0]['embedding']
        return query_embed

    def build_context(self, vector: list, bot_id: int, db: Session):
        top_3 = db.query(Embedding).filter(
            Embedding.bot_id == bot_id).order_by(Embedding.vector.l2_distance(vector)).limit(3).all()
        context_array = [i.content for i in top_3]
        context = " | ".join(context_array)
        print("-" * 80)
        print(len(context))
        return context

    def get_last_n_messages(self, n: int, bot_id: int, chat_id: int, db: Session):
        embeddings = db.query(ChatMessage).filter(
            ChatMessage.chat_id == chat_id
        ).order_by(
            ChatMessage.created_at.desc()
        ).limit(n)

        messages = [i.format_gpt() for i in embeddings]

        return messages

    def save_context(self, context: str, chat_id: int, db: Session):
        new_message = schemas.ChatMessageCreateHidden(
            role="user",
            content=context,
            chat_id=chat_id,
            hidden=True
        )

        saved_message = chat_message_crud.create_chat_message(db, new_message)

        return saved_message

    def query_gpt(self, message: str, bot_id: int, chat_id: int, db: Session):
        last_n = self.get_last_n_messages(5, bot_id, chat_id, db)
        # add context to chat_messages as hidden

        chatdata = [
            {"role": "system",
                "content": "You are a helpful Virtual Intelligence named Glyph."},
            *last_n,
            {"role": "system", "content": f"Based on the above context and your existing knowledge, answer the following question: {message}"},
        ]

        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=chatdata
        )["choices"][0]["message"]["content"]

        return resp

    def process_message(self, incoming_message: str, bot_id: int, chat_id: int, db: Session):
        embedding = self.embed_message(incoming_message)
        context = self.build_context(embedding, bot_id, db)
        self.save_context(context, chat_id, db)
        answer = self.query_gpt(incoming_message, bot_id, chat_id, db)

        return answer
