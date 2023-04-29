from googlesearch import search
from .base_tool import BaseTool

RESULT_FORMAT = """
SOURCE_URL: {url}
TITLIE: {title}
SHORT_DESCRIPTION: {description}
"""


class GoogleSearch(BaseTool):
    def __format_results(self, results):
        formatted_strings = [RESULT_FORMAT.format(
            url=i.url, title=i.title, description=i.description) for i in results]
        return "\n\n".join(formatted_strings)

    def execute(self, message):
        try:
            results = search(message, advanced=True, num_results=5)
            formatted = self.__format_results(results)
        except Exception as e:
            print(e)

            return "NOTHING"

        return formatted
