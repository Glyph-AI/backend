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
from app.models import UserUpload, Text, Embedding, ChatMessage, ChatgptLog, Bot
from .openai_service import OpenaiService

openai.api_key = os.environ.get(
    "OPENAI_API_KEY", "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")


class Glyph:
    def __init__(self, db: Session, bot_id: int, chat_id: int, user_id: int):
        self.db = db
        self.bot_id = bot_id
        self.chat_id = chat_id
        self.user_id = user_id
        self.message_history_to_include = 8
        self.history_threshold = 2000
        self.max_iter = 5
        self.bot = self.db.query(Bot).get(bot_id)
        self.tools = self.bot.enabled_tools
        self.openai = OpenaiService(self.db, self.chat_id)

    def process_message(self, user_message: str):
        try:
            self.archive()
            scratchpad = "PREVIOUS ACTIONS:"
            prompt = self.format_prompt(
                user_message, "", [i.format() for i in self.tools])
            initial_obj = self.openai.query_object(prompt)
            internal_message_array = [initial_obj]
            chatgpt_response = self.openai.query_model(internal_message_array)

            iter = 0
            while True:

                action_taken, glyph_response, respond_direct = self.handle_response(
                    chatgpt_response)
                if respond_direct:
                    return glyph_response

                iter += 1
                if iter >= self.max_iter:
                    return "Max Internal Iterations Reached"

                scratchpad += f"\n\n{chatgpt_response}"
                user_input = f"""What is your next action based on the response from the tool? If you have the answer, use the Respond to User tool. If the last tool used was Text Generation, return the exact results from the Text Generation to the user via Respond to User. DO NOT MODIFY THEM."""
                prompt = self.format_conversation_prompt(
                    tool_response=glyph_response, user_message=user_input, scratchpad=scratchpad, allowed_tools=[
                        i.format() for i in self.tools]
                )
                obj = self.openai.query_object(prompt)
                internal_message_array.append(obj)

                chatgpt_response = self.openai.query_model(
                    internal_message_array)
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
        ).offset(
            self.message_history_to_include
        ).all()

        unarchived_chars = sum([len(i.content) for i in unarchived])

        if unarchived_chars > self.history_threshold:
            self.embed_message_history(unarchived)

    def embed_message_history(self, message_list):

        message_texts = [i.format_archive() for i in message_list]

        combined_text = "\n".join(message_texts)

        new_text = Text(
            user_id=self.user_id,
            content=combined_text,
            text_type="chat_history",
            history_chat_id=self.chat_id
        )

        self.db.add(new_text)

        for m in message_list:
            m.archived = True

        self.db.commit()
        self.db.refresh(new_text)

        new_text.generate_embeddings()

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

    def search_for_tool(self, tool_name):
        for tool in self.tools:
            if tool.name == tool_name:
                return tool

    def handle_response(self, response):
        action, action_input = self.parse_response(response)

        # get tool
        print(f"{action} | {action_input}")
        tool = self.search_for_tool(action)
        tool_class = tool.import_tool()
        tool_obj = tool_class(self.db, self.bot_id, self.chat_id)
        response = tool_obj.execute(action_input)

        return action, response, tool_class.respond_direct

    def parse_response(self, response):
        try:
            json_response = json.loads(response)
        except Exception as e:
            print(e, response)
            json_response = {"action": "Respond to User",
                             "action_input": "I'm sorry, an unknown exception as occurred. Please try again!"}

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

    def format_prompt(self, user_message: str, scratchpad: str, allowed_tools: list[dict]):
        chat_history = self.get_last_n_messages(
            self.message_history_to_include)
        print(allowed_tools)
        prompt = base_prompt.format(
            tools=allowed_tools,
            persona_prompt=self.bot.persona.prompt,
            user_input=user_message,
            chat_history=chat_history,
            scratchpad=scratchpad,
            current_date=datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        )

        return prompt

    def format_conversation_prompt(self, tool_response: str, user_message: str, scratchpad: str, allowed_tools: list[dict]):
        chat_history = self.get_last_n_messages(
            self.message_history_to_include)
       
        prompt = conversation_prompt.format(
            tools=allowed_tools,
            persona_prompt=self.bot.persona.prompt,
            tool_response=tool_response,
            chat_history=chat_history,
            user_input=user_message,
            scratchpad=scratchpad,
            current_date=datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        )

        return prompt
