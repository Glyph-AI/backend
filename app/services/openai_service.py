import openai
import os
from app.models import ChatgptLog, ChatMessage
from sqlalchemy.orm import Session
from tenacity import retry, stop_after_attempt, wait_random_exponential


openai.api_key = os.environ.get(
    "OPENAI_API_KEY", "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")

MODEL = "gpt-3.5-turbo-16k"


class OpenaiService:
    def __init__(self, db: Session | None = None, chat_id: int | None = None, temperature=0.0):
        self.chat_id = chat_id
        self.db = db
        self.temperature = temperature

    def __chatgpt_log(self, message_to_log: str):
        log = ChatgptLog(
            chat_id=self.chat_id,
            message=message_to_log
        )

        self.db.add(log)
        self.db.commit()
        return True

    def message_history(self):
        messages = self.db.query(ChatMessage).filter(
            ChatMessage.chat_id == self.chat_id
        ).order_by(
            ChatMessage.created_at.desc()
        ).limit(16)

        formatted = [i.format_gpt() for i in messages]
        formatted.reverse()

        return formatted

    def query_object(self, content: str, role="user"):
        return {
            "role": role,
            "content": content
        }

    def get_embedding(self, text: str):
        return openai.Embedding.create(
            input=text, model="text-embedding-ada-002")['data'][0]['embedding']

    @retry(wait=wait_random_exponential(min=1, max=30), stop=stop_after_attempt(6))
    def query_model(self, messages: list[dict]):
        self.__chatgpt_log(f"{messages}")

        response = openai.ChatCompletion.create(
            model=MODEL,
            temperature=self.temperature,
            messages=messages
        )["choices"][0]["message"]["content"]

        self.__chatgpt_log(response)
        return response
