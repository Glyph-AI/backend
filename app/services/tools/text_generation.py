from .base_tool import BaseTool
from app.services import OpenaiService
from app.prompts import text_generation_prompt


class TextGeneration(BaseTool):
    respond_direct = True

    def execute(self, message: str):
        openai = OpenaiService(self.db, self.chat_id)
        messages = self.internal_message_array

        prompt = text_generation_prompt.format(prompt=message)

        message_obj = openai.query_object(prompt)
        messages.append(message_obj)

        return openai.query_model(messages)
