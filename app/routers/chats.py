from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
import asyncio
from sqlalchemy.orm import Session
from jose import JWTError, jwt
import os
import json


from app.dependencies import get_db, get_current_user, ConnectionManager
from app.schemas import ChatBase, Chat, User, ChatMessageCreate
from app.crud import chat as chat_crud
from app.crud import user as user_crud
from app.errors import Errors
from app.services import Glyph


SECRET_KEY = os.getenv("AUTH_SECRET_KEY")
ALGORITHM = "HS256"

chats_router = APIRouter(tags=["Chats API"], prefix="/bots/{bot_id}/chats")

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
        bot_id, chat_id, messageJson, db, current_user)

    newChatData = chat_crud.get_chat_by_id(
        bot_id, chat_id, db, current_user)

    newChatJson = newChatData.__dict__

    newChatJson["chat_messages"] = newChatData.chat_messages

    chatJson = jsonable_encoder(Chat(**newChatJson))

    return chatJson


@chats_router.get("/", response_model=list[Chat])
def get_chats_by_user_id(bot_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return chat_crud.get_chats(bot_id, db, current_user)


@chats_router.post("/", response_model=Chat)
def create_chat(chat_data: ChatBase, bot_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return chat_crud.create_chat(chat_data, bot_id, db, current_user)


@chats_router.websocket("/{chat_id}/{chat_token}")
async def chat_endpoint(bot_id: int, chat_id: int, chat_token: str, websocket: WebSocket, db: Session = Depends(get_db)):
    current_user = decode_chat_token(db, chat_token)
    await manager.connect(websocket)
    try:
        while True:
            newMessage = await websocket.receive_text()
            # process_data
            if newMessage != "Connect":
                messageJson = ChatMessageCreate(**json.loads(newMessage))
                chatJson = handle_message_creation(
                    bot_id, chat_id, messageJson, db, current_user)

                # create instance of Glyph
                glyph = Glyph(db, bot_id, chat_id, current_user.id)
                message = glyph.process_message(
                    messageJson.content)
                # process and respond
                messageJson = ChatMessageCreate(
                    **{"content": message, "role": "assistant", "chat_id": chat_id})

                chatJson = handle_message_creation(
                    bot_id, chat_id, messageJson, db, current_user)

                await manager.send_personal_message(json.dumps(chatJson), websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@chats_router.get("/{chat_id}/", response_model=Chat)
def get_all_messages_for_chat(bot_id: int, chat_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    output = chat_crud.get_chat_by_id(bot_id, chat_id, db, current_user)
    return output
