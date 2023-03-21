from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests
import os

from app.dependencies import get_db, get_current_user, create_access_token
from app.schemas import UserCreateSSO, User, GoogleAuth
import app.crud.user as user_crud
from app.errors import Errors

users_router = APIRouter(tags=["User API"])


@users_router.get("/users/{id}", response_model=User)
async def get_user(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.id != id:
        raise Errors.not_authorized_error

    return current_user


@users_router.post("/auth/google")
async def auth_google(google_token: GoogleAuth, db: Session = Depends(get_db)):
    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        google_user = id_token.verify_oauth2_token(
            google_token.token,
            requests.Request(),
            os.getenv("GOOGLE_CLIENT_ID"),
            clock_skew_in_seconds=10
        )

        print(google_user)
        # check the aud claim for our client
        if not os.getenv("GOOGLE_CLIENT_ID") in google_user["aud"]:
            raise Errors.credentials_error

        userid = google_user['sub']
        # check if the user exists
        db_user = user_crud.get_user_by_email(db, google_user["email"])
        if not db_user:
            # new sso user, create an account

            user_data = {
                "first_name": google_user["given_name"],
                "last_name": google_user["family_name"],
                "email": google_user["email"],
                "google_user_id": userid,
                "role": "user",
            }

            user_create_data = UserCreateSSO(**user_data)
            db_user = user_crud.create_user(db, user_create_data)

        # generate access_token
        access_token = create_access_token(data={"sub": db_user.email})
        response = JSONResponse(
            content={"access_token": access_token, "token_type": "bearer"})
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            max_age=1800,
            expires=1800
        )

        return response
    except ValueError as e:
        print(e)
        raise Errors.credentials_error
