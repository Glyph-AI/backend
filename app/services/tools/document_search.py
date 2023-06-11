from app.models import Embedding, Text, UserUpload, BotText
from app.services import SentenceTransformerService
from .base_tool import BaseTool


class DocumentSearch(BaseTool):
    def __cleanse_content(self, content):
        return content.replace("\n", "").replace("\t", "")

    def execute(self, message):
        sts = SentenceTransformerService()
        embed = sts.get_embedding(message)
        top = self.db.query(Embedding).join(Text).join(BotText).filter(
            BotText.include_in_context == True, BotText.bot_id == self.bot_id
        ).order_by(Embedding.vector.l2_distance(embed).asc()).limit(4).all()
        context = {}
        for t in top:
            cleansed_content = self.__cleanse_content(t.content)
            if t.text.name in context:
                context[t.text.name] += f" | {cleansed_content}"
            else:
                context[t.text.name] = cleansed_content

        if len(context) == 0:
            return "NO INFORMATION FOUND"
        return context
