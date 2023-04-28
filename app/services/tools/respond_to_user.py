from .base_tool import BaseTool


class RespondToUser(BaseTool):
    def execute(self, message):
        return message
