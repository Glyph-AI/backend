from .base_tool import BaseTool
from app.services import OpenaiService


class CodeGpt(BaseTool):
    def execute(self, message: str):
        openai = OpenaiService(self.db, self.chat_id)
        messages = openai.message_history()
        return openai.query_model(messages)
