from app.models import Tool
from .base import BaseFactory

class ToolFactory(BaseFactory):
    def create(self, 
               name="Test Tool", 
               class_name="TestTool", 
               internal_filename="test_tool", 
               description="Test Description", 
               user_configurable=True):

        tool = Tool(
            name=name,
            class_name=class_name,
            internal_filename=internal_filename,
            description=description,
            user_configurable=user_configurable
        )

        self.db_session.add(tool)
        self.db_session.commit()
        self.db_session.refresh(tool)

        return tool
