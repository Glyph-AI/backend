from app.models import Persona
from .base import BaseFactory

class PersonaFactory(BaseFactory):
    def create(self, name="Test Persona", prompt="Test Prompt", initial_message="Test Message"):
        persona = Persona(
            name=name,
            prompt=prompt,
            initial_message=initial_message
        )

        self.db_session.add(persona)
        self.db_session.commit()
        self.db_session.refresh(persona)

        return persona