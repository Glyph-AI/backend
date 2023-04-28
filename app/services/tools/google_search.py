from langchain.utilities import GoogleSearchAPIWrapper
from .base_tool import BaseTool


class GoogleSearch(BaseTool):
    def execute(self, message):
        search = GoogleSearchAPIWrapper()

        return search.run(message)
