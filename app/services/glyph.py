import openai
import os
from sqlalchemy.orm import Session
from sqlalchemy import or_
import json
from typing import Callable
from datetime import datetime
from difflib import SequenceMatcher
import numpy as np

from app.prompts import *
from app.models import UserUpload, Text, Embedding, ChatMessage, ChatgptLog, Bot, Chat
from .openai_service import OpenaiService
from .sentence_transformer_service import SentenceTransformerService

openai.api_key = os.environ.get(
    "OPENAI_API_KEY", "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")


class Glyph:
    def __init__(self, db: Session, bot_id: int, chat_id: int, user_id: int):
        self.db = db
        self.bot_id = bot_id
        self.chat_id = chat_id
        self.user_id = user_id
        self.message_history_to_include = 16
        self.history_threshold = 2000
        self.max_iter = 5
        self.bot = self.db.query(Bot).get(bot_id)
        self.tools = self.bot.enabled_tools
        self.openai = OpenaiService(self.db, self.chat_id)
        self.transformer_service = SentenceTransformerService()
        self.user_message = ""

    def __initial_tools(self):
        # for now force it to do something if Document Search is actually present in the tool list
        if "Document Search" in [i.name for i in self.tools]:
            return [i.format() for i in self.tools if i.name != "Respond to User"]

        return [[i.format() for i in self.tools]]

    def process_message(self, user_message: str):
        try:
            self.archive()
            self.user_message = user_message
            prompt = self.format_base_prompt(
                user_message, self.__initial_tools())
            initial_obj = self.openai.query_object(prompt)
            internal_message_array = [initial_obj]
            list_response = self.openai.query_model(internal_message_array)
            print("-" * 80)
            print(list_response)
            print("-" * 80)
            list_response = self.openai.query_object(
                list_response, role="assistant")
            internal_message_array.append(list_response)
            followup = self.openai.query_object(followup_prompt)
            internal_message_array.append(followup)
            chatgpt_response = self.openai.query_model(internal_message_array)
            chatgpt_response_obj = self.openai.query_object(
                chatgpt_response, role="assistant")
            internal_message_array.append(chatgpt_response_obj)

            iter = 0
            while True:
                print("-" * 80)
                print(chatgpt_response)
                print("-" * 80)
                action_taken, glyph_response, respond_direct = self.handle_response(
                    chatgpt_response, internal_message_array)

                print("-" * 80)
                print(glyph_response)
                print("-" * 80)
                if respond_direct:
                    return glyph_response

                iter += 1
                if iter >= self.max_iter:
                    return "Max Internal Iterations Reached"

                prompt = self.format_conversation_prompt(
                    tool_response=glyph_response, action=action_taken, tools=[i.format() for i in self.tools])

                obj = self.openai.query_object(prompt)
                internal_message_array.append(obj)

                chatgpt_response = self.openai.query_model(
                    internal_message_array)

                # make chatgpt aware of itself
                chatgpt_response_object = self.openai.query_object(
                    chatgpt_response, role="assistant")
                internal_message_array.append(chatgpt_response_object)

        except Exception as e:
            print(e)
            return "I'm sorry, an internal error occurred, please try again!"

        return glyph_response

    def archive(self):
        unarchived = self.db.query(ChatMessage).filter(
            or_(ChatMessage.archived == False, ChatMessage.archived == None),
            ChatMessage.hidden == False,
            ChatMessage.chat_id == self.chat_id
        ).order_by(
            ChatMessage.created_at.desc()
        ).all()

        unarchived_chars = sum([len(i.content) for i in unarchived])

        print("-" * 80)
        print(unarchived_chars)
        print("-" * 80)

        if unarchived_chars > self.history_threshold:
            self.embed_message_history(unarchived)

    def tag_conversation(self, messages):
        chat = self.db.query(Chat).filter(Chat.id == self.chat_id).first()
        print("TAGGING CONVERSATION")
        prompt = tagging_prompt.format(
            message_history=messages,
            current_tags=chat.tags
        )

        query_object = self.openai.query_object(content=prompt, role="user")
        resp = self.openai.query_model([query_object])

        if chat.tags:
            chat.tags += resp
        else:
            chat.tags = resp
        self.db.commit()

        return True

    def embed_message_history(self, message_list):
        message_texts = [i.format_archive() for i in message_list]

        combined_text = "\n".join(message_texts)

        # tag the chat
        self.tag_conversation(combined_text)

        # chunk if necessary
        chunk_size = 1000
        overlap = 250
        chunks = [combined_text[i:i + chunk_size]
                  for i in range(0, len(combined_text), chunk_size-overlap)]

        for chunk in chunks:
            embedding = self.transformer_service.get_embedding(chunk)

            new_e = Embedding(
                bot_id=self.bot_id,
                user_id=self.user_id,
                vector=embedding,
                content=chunk
            )

            self.db.add(new_e)

        for m in message_list:
            m.archived = True

        self.db.commit()

        return True

    def relevancy_checker(self, query, context_pieces):
        context = []
        for c in context_pieces:
            prompt = relevancy_prompt.format(context=c, query=query)
            query_obj = self.build_chatgpt_query_object(prompt)
            response = self.openai.query_model([query_obj])
            if response == "YES":
                context.append(c)

        return context

    def search_for_tool(self, raw_name):
        # catch weird Document search thing
        tool_name = raw_name
        if raw_name == "DOCUMENT SEARCH":
            tool_name = "Document Search"

        if raw_name == "TEXT GENERATION":
            tool_name = "Text Generation"

        for tool in self.tools:
            if tool.name == tool_name:
                return tool

    def handle_response(self, response, internal_message_array):
        action, action_input = self.parse_response(response)

        # get tool
        tool = self.search_for_tool(action)
        tool_class = tool.import_tool()
        tool_obj = tool_class(self.db,
                              self.bot_id,
                              self.chat_id,
                              internal_message_array=internal_message_array,
                              original_message=self.user_message)
        response = tool_obj.execute(action_input)

        return action, response, tool_class.respond_direct

    def parse_response(self, response):
        try:
            cleaned_response = response
            if "`" in response:
                cleaned_response = response.strip("`")

            json_response = json.loads(cleaned_response)
        except Exception as e:
            print(e)
            json_response = {"action": "Respond to User",
                             "action_input": "I'm sorry, an internal error occurred, please try again!"}

        return json_response["action"], json_response["action_input"]

    def build_chatgpt_query_object(self, content: str):
        return {
            "role": "user",
            "content": content
        }

    def chatgpt_log(self, message_to_log):
        log = ChatgptLog(
            chat_id=self.chat_id,
            message=message_to_log,
        )

        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)

        return log

    def get_last_n_messages(self, n: int):
        messages = self.db.query(ChatMessage).filter(
            ChatMessage.chat_id == self.chat_id
        ).order_by(
            ChatMessage.created_at.desc()
        ).limit(n)

        formatted_messages = [i.format_for_prompt() for i in messages]
        formatted_messages.reverse()
        history_length = 0
        history = []
        for m in formatted_messages[:-1]:
            history_length += len(m)

            history.append(m)

            if history_length > 1500:
                break

        joined_messages = "\n".join(history)

        return joined_messages

    def format_base_prompt(self, user_message: str, allowed_tools: list[dict]):
        chat_history = self.get_last_n_messages(
            self.message_history_to_include)
        prompt = base_prompt.format(
            tools=allowed_tools,
            persona_prompt=self.bot.persona.prompt,
            user_input=user_message,
            chat_history=chat_history,
            current_date=datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        )

        return prompt

    def format_conversation_prompt(self, tool_response: str, action: str, tools: list[dict]):
        chat_history = self.get_last_n_messages(
            self.message_history_to_include)

        prompt = conversation_prompt.format(
            persona_prompt=self.bot.persona.prompt,
            tool_response=tool_response,
            action=action,
            tools=tools,
            current_date=datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        )

        return prompt
