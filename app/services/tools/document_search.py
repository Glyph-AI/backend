from app.models import Embedding, Text, UserUpload, BotText
from app.services import SentenceTransformerService
from app.services import OpenaiService
from app.prompts import document_search
import json
from .base_tool import BaseTool


class DocumentSearch(BaseTool):
    def __format_prompt(self, message):
        return document_search.format(input=message)

    def __parse_response(self, response):
        try:
            cleaned_response = response
            if "`" in response:
                cleaned_response = response.strip("`")

            json_response = json.loads(cleaned_response)

            return json_response["search_terms"]
        except Exception as e:
            raise e

    def execute(self, message):
        sts = SentenceTransformerService()
        openai = OpenaiService(db=self.db, chat_id=self.chat_id)

        prompt = self.__format_prompt(message)
        query_object = openai.query_object(prompt)
        response = openai.query_model([query_object])
        search_terms = self.__parse_response(response)

        print("-" * 80)
        print(search_terms)

        embed = sts.get_embedding(search_terms)
        top = self.db.query(Embedding).join(Text).join(BotText).filter(
            BotText.include_in_context == True, BotText.bot_id == self.bot_id
        ).order_by(Embedding.vector.l2_distance(embed).desc()).limit(3).all()
        context = [i.content for i in top]
        if len(context) == 0:
            return ["NO INFORMATION FOUND"]
        return context
