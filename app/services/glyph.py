import openai
import os
from sqlalchemy.orm import Session
from sqlalchemy import or_
from langchain.utilities import GoogleSearchAPIWrapper
import json
from typing import Callable

from app.prompts import *
from app.models import UserUpload, Text, Embedding, ChatMessage, ChatgptLog

openai.api_key = os.environ.get(
    "OPENAI_API_KEY", "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")


class Tool:
    def __init__(self, name: str, description: str, func: Callable):
        self.name = name
        self.description = description
        self.func = func

    def format(self):
        return {
            "name": self.name,
            "description": self.description
        }


class Glyph:
    def __init__(self, db: Session, bot_id: int, chat_id: int, user_id: int):
        self.db = db
        self.bot_id = bot_id
        self.chat_id = chat_id
        self.user_id = user_id
        self.message_history_to_include = 8
        self.history_threshold = 2000
        self.search = GoogleSearchAPIWrapper()
        self.max_iter = 5
        self.initial_tools = [
            Tool(
                name="Document Search",
                description="Searches Documents the user has uploaded to the database.",
                func=self.document_search
            ),
            Tool(
                name="CodeGPT",
                description="Handles computer code related requests.",
                func=self.ask_chat
            ),
            Tool(
                name="Respond to User",
                description="If you have the answer to the question, this tool provides it to the user.",
                func=None
            )
        ]
        self.tools = [
            Tool(
                name="Document Search",
                description="Searches Documents the user has uploaded to the database.",
                func=self.document_search
            ),
            Tool(
                name="Google Search",
                description="Searches Google for relevant information.",
                func=self.search.run
            ),
            Tool(
                name="CodeGPT",
                description="Handles computer code related requests.",
                func=self.ask_chat
            ),
            Tool(
                name="Respond to User",
                description="If you have the answer to the question, this tool provides it to the user.",
                func=None
            )
        ]

    def process_message(self, user_message: str):
        self.archive()
        scratchpad = "PREVIOUS ACTIONS:"
        prompt = self.format_prompt(
            user_message, "", [i.format() for i in self.initial_tools])
        initial_obj = self.build_chatgpt_query_object(prompt)
        internal_message_array = [initial_obj]
        chatgpt_response = self.chatgpt_request(internal_message_array)

        iter = 0
        while True:

            action_taken, glyph_response = self.handle_response(
                chatgpt_response)

            if action_taken == "Respond to User":
                return glyph_response

            iter += 1
            if iter >= self.max_iter:
                return "Max Internal Iterations Reached"

            scratchpad += f"\n\n{chatgpt_response}"
            user_input = f"What is your next action based on the response from the tool? If you have the answer, use the Respond to User tool."
            prompt = self.format_conversation_prompt(
                tool_response=glyph_response, user_message=user_input, scratchpad=scratchpad, allowed_tools=[
                    i.format() for i in self.tools]
            )
            obj = self.build_chatgpt_query_object(prompt)
            internal_message_array.append(obj)

            chatgpt_response = self.chatgpt_request(internal_message_array)

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

        # chunk if necessar
        chunk_size = 2000
        overlap = 500
        chunks = [combined_text[i:i + chunk_size]
                  for i in range(0, len(combined_text), chunk_size-overlap)]

        for chunk in chunks:
            embedding = self.embed_message(chunk)

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

    def ask_chat(self, message):
        messages = self.db.query(ChatMessage).filter(
            ChatMessage.chat_id == self.chat_id
        ).order_by(
            ChatMessage.created_at.desc()
        ).limit(16).offset(1)

        formatted = [i.format_gpt() for i in messages]
        formatted.reverse()

        response = self.chatgpt_request(formatted)
        return response

    def relevancy_checker(self, query, context_pieces):
        context = []
        for c in context_pieces:
            prompt = relevancy_prompt.format(context=c, query=query)
            query_obj = self.build_chatgpt_query_object(prompt)
            response = self.chatgpt_request([query_obj])
            if response == "YES":
                context.append(c)

        return context

    def document_search(self, message):
        embed = self.embed_message(message)
        top = self.db.query(Embedding).join(Text).join(UserUpload).filter(
            UserUpload.include_in_context == True, Embedding.bot_id == self.bot_id).order_by(Embedding.vector.l2_distance(embed)).limit(3).all()

        context = [i.content for i in top]
        relevant_pieces = self.relevancy_checker(message, context)

        if len(relevant_pieces) > 0:
            return "\n".join(relevant_pieces)

        # if len(relevant_pieces) > 0:
        #     context = "\n".join(relevant_pieces)
        #     prompt = document_search.format(context=context, query=message)

        #     chat_message = {"role": "user", "content": prompt}
        #     search_answer = self.chatgpt_request([chat_message])
        #     return search_answer

        return "No Relevant Document Information Found"

    def search_for_tool_func(self, tool_name):
        for tool in self.tools:
            if tool.name == tool_name:
                return tool.func

    def handle_response(self, response):
        action, action_input = self.parse_response(response)
        if action == "Respond to User":
            return action, action_input

        tool_func = self.search_for_tool_func(action)
        response = tool_func(action_input)

        return action, response

    def parse_response(self, response):
        try:
            json_response = json.loads(response)
        except Exception as e:
            json_response = {"action": "Respond to User",
                             "action_input": "I'm sorry, an unknown exception as occurred"}

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

    def chatgpt_request(self, messages: list[dict]):
        # log prompt and response
        self.chatgpt_log(f"{messages}")

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.0,
            messages=messages
        )["choices"][0]["message"]["content"]

        self.chatgpt_log(response)

        return response

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
        prompt = base_prompt.format(
            tools=allowed_tools, user_input=user_message, chat_history=chat_history, scratchpad=scratchpad)

        return prompt

    def format_conversation_prompt(self, tool_response: str, user_message: str, scratchpad: str, allowed_tools: list[dict]):
        prompt = conversation_prompt.format(
            tools=allowed_tools, tool_response=tool_response, user_input=user_message, scratchpad=scratchpad,
        )

        return prompt

    def embed_message(self, user_message: str):
        query_embed = openai.Embedding.create(
            input=user_message, model="text-embedding-ada-002")['data'][0]['embedding']
        return query_embed
