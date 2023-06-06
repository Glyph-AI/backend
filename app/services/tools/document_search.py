from app.models import Embedding, Text, UserUpload, BotText
from app.services import SentenceTransformerService
from .base_tool import BaseTool


class DocumentSearch(BaseTool):
    def execute(self, message):
        sts = SentenceTransformerService()
        embed = sts.get_embedding(message)
        top = self.db.query(Embedding).join(Text).join(BotText).filter(
            BotText.include_in_context == True, BotText.bot_id == self.bot_id
        ).order_by(Embedding.vector.l2_distance(embed).asc()).limit(6).all()
        context = [i.content for i in top]
        if len(context) == 0:
            return ["NO INFORMATION FOUND"]
        return context
