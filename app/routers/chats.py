from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
import asyncio
from sqlalchemy.orm import Session
from jose import JWTError, jwt
import os
import json


from app.dependencies import get_db, get_current_user, ConnectionManager
from app.schemas import ChatBase, Chat, User, ChatMessageCreate, ChatCreate
from app.crud import chat as chat_crud
from app.crud import user as user_crud
from app.errors import Errors
from app.services import Glyph
import app.models as models


SECRET_KEY = os.getenv("AUTH_SECRET_KEY")
ALGORITHM = "HS256"

chats_router = APIRouter(tags=["Chats API"], prefix="/chats")

manager = ConnectionManager()


def decode_chat_token(db, token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        info = payload.get("sub")
        email, chat_id = info.split("|")
        if email is None:
            raise Errors.credentials_error
        if chat_id is None:
            raise Errors.credentials_error

    except JWTError:
        raise Errors.credentials_error
    user = user_crud.get_user_by_email(db, email=email)

    return user


def handle_message_creation(bot_id, chat_id, messageJson, db, current_user):
    chat_crud.create_message(
        chat_id, messageJson, db, current_user)

    newChatData = chat_crud.get_chat_by_id(
        chat_id, db, current_user)

    newChatJson = newChatData.__dict__

    newChatJson["chat_messages"] = newChatData.chat_messages
    newChatJson["bot"] = newChatData.bot

    chatJson = jsonable_encoder(Chat(**newChatJson))

    return chatJson


@chats_router.get("", response_model=list[Chat])
def get_chats_by_user_id(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return chat_crud.get_chats(db, current_user)


@chats_router.post("", response_model=Chat)
def create_chat(chat_data: ChatCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return chat_crud.create_chat(chat_data, db, current_user)

@chats_router.delete("/{chat_id}")
def delete_chats(chat_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return chat_crud.delete_chat_by_id(chat_id, db, current_user)


@chats_router.post("/{chat_id}/message", response_model=Chat)
def send_message(message_data: ChatMessageCreate, chat_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    print("REQUEST START")
    bot_id = db.query(models.Chat).get(chat_id).bot_id
    chatJson = handle_message_creation(
        bot_id, chat_id, message_data, db, current_user)

    print("MESSAGE CREATED")

    glyph = Glyph(db, bot_id, chat_id, current_user.id)
    response = glyph.process_message(
        message_data.content
    )

    print("GLYPH PROCESSING COMPLETE")

    responseJson = ChatMessageCreate(
        **{"content": response, "role": "assistant", "chat_id": chat_id}
    )

    responseJson = handle_message_creation(
        bot_id, chat_id, responseJson, db, current_user
    )

    return responseJson

@chats_router.get("/{chat_id}", response_model=Chat)
def get_all_messages_for_chat(chat_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    output = chat_crud.get_chat_by_id(chat_id, db, current_user)
    return output
