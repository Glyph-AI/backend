from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.sql import text
from app.db.base_class import Base
from sqlalchemy.ext.associationproxy import association_proxy
import importlib


class Tool(Base):
    __tablename__ = "tools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    class_name = Column(String, nullable=False)
    internal_filename = Column(String, nullable=False)
    description = Column(String, nullable=False)
    user_configurable = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())

    bots = association_proxy("bot_tools", "bots")

    def import_tool(self):
        module_name = f"app.services.tools.{self.internal_filename}"
        module = importlib.import_module(module_name)
        tool_class = getattr(module, self.class_name)
        return tool_class

    def format(self):
        return {
            "name": self.name,
            "description": self.description
        }
