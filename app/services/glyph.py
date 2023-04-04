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
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent
import os
import json
from typing import Optional, Tuple
from datetime import datetime

from app.models import Embedding, ChatMessage, Text, UserUpload
import app.schemas as schemas
from app.crud import chat_message as chat_message_crud

openai.api_key = os.environ.get(
    "OPENAI_API_KEY", "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")


class Glyph:
    def __init__(self, db: Session, bot_id: int, chat_id: int, user_id: int):
        self.db = db
        self.bot_id = bot_id
        self.chat_id = chat_id
        self.user_id = user_id
        self.message_history_to_include = 15
        self.history_threshold = 2000
        search = GoogleSearchAPIWrapper()

        self.tools = [
            Tool(
                name="Document Search",
                func=self.build_context,
                description="Use this tool first before using Google Search. Useful for finding answers to user questions."
            )
            # Tool(
            #     name="Google Search",
            #     func=search.run,
            #     description="Useful for when you need to answer questions and the information is not included in the context for the question. Try this tool if Document Search does not return a useful answer."
            # )
        ]

    def embed_message(self, message: str):
        query_embed = openai.Embedding.create(
            input=message, model="text-embedding-ada-002")['data'][0]['embedding']
        return query_embed

    def chatgpt_request(self, query_object):
        return openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[query_object]
        )["choices"][0]["message"]["content"]

    def boolean_chatgpt(self, response: str):
        try:
            json_response = json.loads(response)
        except Exception as e:
            json_response = {"response": "NO"}

        if json_response["response"] == "NO":
            return False

        return True

    def ask_model_about_information(self, message: str, context: str):
        query_object = {
            "role": "user",
            "content": f"""Context: {context}.\n\nQuestion: {message}\n\nGiven the preceeding context, determine whether or not the answer to the question is contained within the context. Your response should be in the form of a JSON Object like the following example where $ANSWER is either "YES" or "NO"\n\n```\n    {{\n        "response": "$ANSWER"\n    }}\n```\n\nProvide only the object, do not provide any additional explanation."""
        }

        return self.boolean_chatgpt(self.chatgpt_request(query_object))

    def query_references_uploaded_file(self, message: str):
        user_files = self.db.query(UserUpload).filter(
            UserUpload.bot_id == self.bot_id).all()
        file_names = [i.filename for i in user_files]
        joined_filenames = ", ".join(file_names)

        query_object = {
            "role": "user",
            "content": f"""File List: {joined_filenames}.\n\nQuestion: {message}\n\nGiven the preceeding list of files, determine whether or not the question contains a reference to one of the files listed.\nYour response should be in the form of a JSON Object like the following example where $ANSWER is either "YES" or "NO", and $FILENAME is a file from the list given or an empty string if no file is given.\n\n```\n\n    {{\n        "response": "$ANSWER",\n        "filename": "$FILENAME"\n    }}\n```\n\nProvide only the object, do not provide any additional explanation."""
        }

        response = self.chatgpt_request(query_object)
        try:
            json_response = json.loads(response)
        except:
            json_response = {"response": "NO", "filename": ""}

        if json_response["response"] == "NO":
            return False, ""

        return True, json_response["filename"]

    def build_context(self, message: str):
        vector = self.embed_message(message)
        ref, referenced_file = self.query_references_uploaded_file(message)
        print(ref, referenced_file)
        top = None
        if ref:
            top = self.db.query(Embedding).join(Text).join(UserUpload).filter(
                UserUpload.include_in_context == True, UserUpload.filename == referenced_file, Embedding.bot_id == self.bot_id).order_by(Embedding.vector.l2_distance(vector)).limit(3).all()
        else:
            top = self.db.query(Embedding).join(Text).join(UserUpload).filter(
                UserUpload.include_in_context == True, Embedding.bot_id == self.bot_id).order_by(Embedding.vector.l2_distance(vector)).limit(3).all()

        context_array = [i.content for i in top]
        final_contexts = []
        for c in context_array:
            relevant = self.ask_model_about_information(
                message, c)

            print(f"RELEVANT: {relevant}")

            if relevant:
                final_contexts.append(c)

        if len(final_contexts) == 0:
            return "No relevant information found in user's documents."
        else:
            return " | ".join(final_contexts)

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
            content=f"You are Glyph, a helpful AI assistant. Current date and time are: {datetime.today().strftime('%Y-%m-%d %H:%M:%S')}")] + last_n
        memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True)
        memory.chat_memory.messages = last_n
        llm = ChatOpenAI(temperature=0)
        agent_chain = initialize_agent(
            self.tools, llm, agent="chat-conversational-react-description", verbose=False, memory=memory)

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

        # embedding = self.embed_message(incoming_message)

        # context = self.build_context(embedding)
        # if context:
        #     self.save_context(context)

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
