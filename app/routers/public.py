from fastapi import APIRouter, Depends, UploadFile
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_bot
from app.schemas import BotApiInfo, ChatBase, ChatMessageCreate, Chat, ApiChatMessageCreate
from app.services import Glyph
import app.crud.chat as chat_crud
from datetime import datetime

public_router = APIRouter(tags=["Public API"], prefix="")

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


@public_router.post("/chat", response_model=Chat)
async def api_chat(message_data: ApiChatMessageCreate, db: Session = Depends(get_db), bot_api_info: BotApiInfo = Depends(get_current_bot)):
    print("REQUEST START")
    chat_id = bot_api_info.chat_id

    chat = None
    if not chat_id:
        chat_data = ChatBase(name= f"API Chat {datetime.now().timestamp()}", bot_id=bot_api_info.bot.id, bot=bot_api_info.bot)
        chat = chat_crud.create_chat(chat_data, db, bot_api_info.user)
    else:
        chat = chat_crud.get_chat_by_id(bot_api_info.chat_id, db, current_user=bot_api_info.user)

    complete_message_data = ChatMessageCreate(
        role="user",
        content=message_data.content,
        chat_id=chat.id
    )

    handle_message_creation(
        bot_api_info.bot.id, chat_id, complete_message_data, db, bot_api_info.user
    )

    print("MESSAGE CREATED")

    glyph = Glyph(db, bot_api_info.bot.id, chat.id, bot_api_info.user.id)
    response = glyph.process_message(
        complete_message_data.content
    )

    print("GLYPH PROCESSING COMPLETE")

    responseJson = ChatMessageCreate(
        content=response, role="assistant", chat_id=chat_id
    )

    responseJson = handle_message_creation(
        bot_api_info.bot.id, chat_id, responseJson, db, bot_api_info.user
    )

    return responseJson