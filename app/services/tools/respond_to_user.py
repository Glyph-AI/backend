from .base_tool import BaseTool


class RespondToUser(BaseTool):
    respond_direct = True

    def execute(self, message):
        return message
