from .base_tool import BaseTool
from app.services import OpenaiService
from app.prompts import respond_to_user_prompt


class RespondToUser(BaseTool):
    respond_direct = True

    def execute(self, message: str):
        openai = OpenaiService(self.db, self.chat_id)
        messages = self.internal_message_array

        prompt = respond_to_user_prompt.format(
            user_input=self.original_message)

        message_obj = openai.query_object(prompt)
        messages.append(message_obj)

        return openai.query_model(messages)
