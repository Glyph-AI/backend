from fastapi import Depends, WebSocket, WebSocketDisconnect, status, HTTPException, Request
from app.db.session import SessionLocal
from fastapi.security import OAuth2, HTTPBearer
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security.utils import get_authorization_scheme_param
from sqlalchemy.orm import Session
import app.models as models
from app.schemas import User, Token, TokenData, BotTokenData, BotApiInfo
import app.crud.user as user_crud
import app.crud.bot as bot_crud
import app.crud.chat as chat_crud
from app.errors import Errors
from jose import JWTError, jwt
from typing import Optional, Dict
import os
from datetime import timedelta, datetime

SECRET_KEY = os.getenv("AUTH_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(
            password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.cookies.get("access_token")
        if not authorization:
            authorization: str = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param


oauth2_scheme = OAuth2PasswordBearerWithCookie(
    tokenUrl="/token", scheme_name="oauth2_scheme")

bot_bearer_scheme = HTTPBearer(scheme_name="public_oauth2_scheme")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(db: Session = Depends(get_db), token: Token = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise Errors.credentials_error
        token_data = TokenData(email=email)
    except JWTError:
        raise Errors.credentials_error
    user = user_crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise Errors.credentials_error

    return user

# handles permissioning for bot keys
# requires token in the format {email}|{bot_id}|{chat_id}


async def get_current_bot(db: Session = Depends(get_db), token: Token = Depends(bot_bearer_scheme)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY,
                             algorithms=[ALGORITHM])
        data = payload.get("sub").split("|")
        email = data[0]
        id = int(data[1])
        chat_id = int(data[2])
        if id is None:
            raise Errors.credentials_error
        token_data = BotTokenData(id=id, chat_id=chat_id, email=email)
    except JWTError:
        raise Errors.credentials_error
    user = user_crud.get_user_by_email(db, email=token_data.email)
    bot = bot_crud.get_bot_by_id(token_data.id, db, user)

    # make sure the user calling the API is a user of this bot
    bot_user = db.query(models.BotUser).filter(
        models.BotUser.user_id == user.id, models.BotUser.bot_id == bot.id).first()
    if not bot_user:
        raise Errors.credentials_error

    info = BotApiInfo(user=user, bot=bot, chat_id=chat_id)

    return info


async def current_user_is_admin(current_user: User = Depends(get_current_user)):
    if not current_user.admin:
        raise Errors.credentials_error
    return current_user


def create_access_token(data: dict):
    to_encode = data.copy()
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_bot_access_token(data: dict):
    to_encode = data.copy()
    expires_delta = timedelta(minutes=100000000)
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
