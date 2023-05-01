from googlesearch import search
from .base_tool import BaseTool
import os
import requests

RESULT_FORMAT = """
SOURCE_URL: {url}
TITLE: {title}
SHORT_DESCRIPTION: {description}
"""

CSE_ID = os.getenv("GOOGLE_CSE_ID")
API_KEY = os.getenv("GOOGLE_API_KEY")


class GoogleSearch(BaseTool):
    def __url(self, search_term):
        return f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={CSE_ID}&q={search_term}"

    def __format_results(self, results):
        formatted_strings = [RESULT_FORMAT.format(
            url=i["url"], title=i["title"], description=i["description"]) for i in results]
        return "\n\n".join(formatted_strings)
    
    def __get_results(self, search_query):
        raw = requests.get(self.__url(search_query)).json()["items"]
        array_results = [{"url": i['link'], "description": i["snippet"], "title": i['title']} for i in raw][:5]
        return array_results

    def execute(self, message):
        try:
            results = self.__get_results(message)
            formatted = self.__format_results(results)
        except Exception as e:
            print(e)

            return "NOTHING"

        return formatted
