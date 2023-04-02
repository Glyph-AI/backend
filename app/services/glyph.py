import time
import openai
from sqlalchemy.orm import Session
from sqlalchemy import or_
from langchain import LLMChain
from langchain.llms.fake import FakeListLLM
from langchain.agents import load_tools, Tool, AgentExecutor
from langchain.agents.chat.base import ChatAgent
from langchain.utilities import GoogleSearchAPIWrapper
from langchain.chat_models import ChatOpenAI
from langchain.agents import Tool
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage
from langchain.chat_models import ChatOpenAI
from langchain.utilities import SerpAPIWrapper
from langchain.agents import initialize_agent
import os
import json
from typing import Optional, Tuple
from datetime import datetime

from app.models import Embedding, ChatMessage, Text
import app.schemas as schemas
from app.crud import chat_message as chat_message_crud

openai.api_key = os.environ.get(
    "OPENAI_API_KEY", "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")

search = GoogleSearchAPIWrapper()

tools = [
    Tool(
        name="Google Search",
        func=search.run,
        description="Useful for when you need to answer questions and the information is not included in the context for the question."
    )
]


class Glyph:
    def __init__(self, db: Session, bot_id: int, chat_id: int, user_id: int):
        self.db = db
        self.bot_id = bot_id
        self.chat_id = chat_id
        self.user_id = user_id
        self.message_history_to_include = 5
        self.history_threshold = 2000

    def embed_message(self, message: str):
        query_embed = openai.Embedding.create(
            input=message, model="text-embedding-ada-002")['data'][0]['embedding']
        return query_embed

    def build_context(self, vector: list):
        top = self.db.query(Embedding).filter(
            Embedding.bot_id == self.bot_id).order_by(Embedding.vector.l2_distance(vector)).limit(3).all()
        context_array = [i.content for i in top]

        if len(context_array) == 0:
            return None
        else:
            return " | ".join(context_array)

    def get_last_n_messages(self, n: int):
        messages = self.db.query(ChatMessage).filter(
            ChatMessage.chat_id == self.chat_id
        ).order_by(
            ChatMessage.created_at.desc()
        ).limit(n)

        formatted_messages = [i.format_langchain() for i in messages]

        return formatted_messages[:-1]

    def save_context(self, context: str):
        new_message = schemas.ChatMessageCreateHidden(
            role="user",
            content=context,
            chat_id=self.chat_id,
            hidden=True
        )

        saved_message = chat_message_crud.create_chat_message(
            self.db, new_message)

        return saved_message

    def query_gpt(self, message: str):
        last_n = self.get_last_n_messages(self.message_history_to_include)
        last_n = [SystemMessage(
            content=f"You are Glyph, a helpful AI assistant. Todays date is: {datetime.today().strftime('%Y-%m-%d')}")] + last_n
        memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True)
        memory.chat_memory.messages = last_n
        llm = ChatOpenAI(temperature=0)
        agent_chain = initialize_agent(
            tools, llm, agent="chat-conversational-react-description", verbose=True, memory=memory)
        resp = agent_chain.run(message)

        return resp

    def process_message(self, incoming_message: str):
        # does the new message push our non-hidden messages over the character threshold?
        unarchived = self.db.query(ChatMessage).filter(
            or_(ChatMessage.archived == False, ChatMessage.archived == None),
            ChatMessage.hidden == False,
            ChatMessage.chat_id == self.chat_id
        ).order_by(
            ChatMessage.created_at.desc()
        ).offset(
            self.message_history_to_include
        ).all()

        unarchived_chars = sum([len(i.content) for i in unarchived])

        if unarchived_chars > self.history_threshold:
            self.embed_message_history(unarchived)

        embedding = self.embed_message(incoming_message)

        context = self.build_context(embedding)
        if context:
            self.save_context(context)

        answer = self.query_gpt(incoming_message)

        return answer

    def embed_message_history(self, message_list):
        print("Embedding Chat History")

        message_texts = [i.format_archive() for i in message_list]

        combined_text = "\n".join(message_texts)

        embedding = self.embed_message(combined_text)

        new_e = Embedding(
            bot_id=self.bot_id,
            user_id=self.user_id,
            vector=embedding,
            content=combined_text
        )

        self.db.add(new_e)

        for m in message_list:
            m.archived = True

        self.db.commit()

        return True
