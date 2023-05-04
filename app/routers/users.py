from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests
import os
from datetime import datetime, timedelta, timezone

from app.dependencies import get_db, get_current_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.schemas import UserCreateSSO, User, GoogleAuth
import app.crud.user as user_crud
from app.errors import Errors
from app.services import StripeService

COOKIE_DOMAIN = os.environ.get("COOKIE_DOMAIN", "localhost")

users_router = APIRouter(tags=["User API"])


@users_router.get("/users/{id}", response_model=User)
async def get_user(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.id != id:
        raise Errors.not_authorized_error

    return current_user


@users_router.get("/profile", response_model=User)
async def profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = user_crud.get_user_by_id(db, current_user, current_user.id)
    return user


@users_router.post("/logout")
async def logout(db: Session = Depends(get_db)):
    response = JSONResponse(content={"message": "Logged Out"})
    response.delete_cookie(key="Authorization")
    response.delete_cookie(key="active_session")
    return response


@users_router.post("/auth/google")
async def auth_google(google_token: GoogleAuth, db: Session = Depends(get_db)):
    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        print("HERE")
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
                "profile_picture_location": google_user["picture"]
            }

            user_create_data = UserCreateSSO(**user_data)
            db_user = user_crud.create_user(db, user_create_data)

            stripe_svc = StripeService(db)
            stripe_svc.create_customer(db_user)

        # check if users have a profile picture already
        if db_user.profile_picture_location is None:
            db_user.profile_picture_location = google_user["picture"]
            db.commit()

        # generate access_token
        access_token = create_access_token(data={"sub": db_user.email})
        response = JSONResponse(
            content={"access_token": access_token, "token_type": "bearer"})

        cookie_expiration_delta = timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        expiration = datetime.now(timezone.utc) + cookie_expiration_delta
        print("-" * 80)
        print(expiration, type(expiration), expiration.tzinfo)
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            expires=expiration
        )

        response.set_cookie(
            key="active_session",
            value="true",
            expires=expiration,
            domain=COOKIE_DOMAIN
        )

        return response
    except ValueError as e:
        print(e)
        raise Errors.credentials_error
