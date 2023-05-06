from app.models import UserUpload
from .bot import BotFactory
from .user import UserFactory
from .base import BaseFactory

class UserUploadFactory(BaseFactory):
    def create(self, 
               user=None, 
               s3_link="test_link", 
               filename="testfile", 
               bot=None, 
               processed=True, 
               include_in_context=True, 
               deleted=False):
        
        if user is None:
            user = UserFactory(self.db_session).create()

        if bot is None:
            bot = BotFactory(self.db_session).create()

        
        uu = UserUpload(
            user=user,
            s3_link=s3_link,
            filename=filename,
            bot=bot,
            processed=processed,
            include_in_context=include_in_context,
            deleted=deleted
        )

        self.db_session.add(uu)
        self.db_session.commit()
        self.db_session.refresh(uu)

        return uu
