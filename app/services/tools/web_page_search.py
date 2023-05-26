from .base_tool import BaseTool
from app.services import SentenceTransformerService
from urlextract import URLExtract
from bs4 import BeautifulSoup
from bs4.element import Comment
import requests
import numpy as np
from numpy.linalg import norm


class WebPageSearch(BaseTool):

    def __extract_url_from_message(self, message):
        ext = URLExtract()
        url = ext.find_urls(message)[0]

        return url

    def __tag_visible(self, element):
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        if isinstance(element, Comment):
            return False
        return True

    def __extract_text_from_url(self, url):
        content = requests.get(url).text
        soup = BeautifulSoup(content, 'html.parser')
        texts = soup.findAll(text=True)
        visible = filter(self.__tag_visible, texts)

        return " ".join(t.strip() for t in visible)

    def __binary_search(self, query_embedding, text):
        text_copy = text
        found_texts = []
        for i in range(3):
            operating_text = text_copy
            while len(operating_text) > 3000:
                half_length = len(operating_text) // 2
                left = operating_text[:half_length]
                right = operating_text[half_length:]

                l_e = np.array(self.__embed(left))
                r_e = np.array(self.__embed(right))

                l_sim = np.dot(query_embedding, l_e.T)
                r_sim = np.dot(query_embedding, r_e.T)

                if l_sim > r_sim:
                    operating_text = left

                else:
                    operating_text = right

            found_texts.append(operating_text)
            text_copy = text_copy.replace(operating_text, "")

        return found_texts

    async def __embed(self, message):
        sts = SentenceTransformerService()
        query = sts.get_embedding(message)

        return query

    def __filter_page_by_query(self, q_vector, page_vectors):
        sim = np.dot(q_vector, page_vectors.T)
        top_3 = np.argpartition(sim, -3)[-3:]

        return top_3

    def execute(self, message):
        url = self.__extract_url_from_message(self.original_message)

        text = self.__extract_text_from_url(url)

        query = self.__embed(message)
        found_texts = self.__binary_search(query, text)

        return found_texts
