from app.models import User
from .base import BaseFactory

class UserFactory(BaseFactory):
    def create(self, email="test@test.com",
               first_name="test",
               last_name="test",
               role="user",
               is_current=True):
        
        new_user = User(
            email="test@test.com",
            first_name="test",
            last_name="test",
            role="user",
            is_current=True
        )

        self.db_session.add(new_user)
        self.db_session.commit()
        self.db_session.refresh(new_user)

        return new_user