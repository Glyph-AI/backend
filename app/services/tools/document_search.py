from app.models import Embedding, Text, UserUpload
from app.services import OpenaiService
from .base_tool import BaseTool


class DocumentSearch(BaseTool):
    def execute(self, message):
        openai = OpenaiService(self.db, self.chat_id)
        embed = openai.get_embedding(message)
        top = self.db.query(Embedding).join(Text).join(UserUpload).filter(
            UserUpload.include_in_context == True, Embedding.bot_id == self.bot_id).order_by(Embedding.vector.l2_distance(embed)).limit(3).all()
        context = [i.content for i in top]
        return context
