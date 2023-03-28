from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import os

from app.dependencies import get_db, get_current_user
from app.schemas import User
from app.services import StripeService

subscriptions_router = APIRouter(tags=["Subscriptions API"])

@subscriptions_router.get("/subscriptions/checkout-session")
async def get_checkout_session(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    stripe_svc = StripeService()

    url = stripe_svc.create_checkout_session(current_user.stripe_customer_id, "")
    
    return JSONResponse(content={"url": url})

@subscriptions_router.get("/subscriptions/customer-portal-session")
async def get_customer_portal_session(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    stripe_svc = StripeService()

    url = ""
    if current_user.subscribed:
        url = stripe_svc.create_portal_session(
            current_user.stripe_customer_id, redirect_url="")
    else:
        url = stripe_svc.create_checkout_session(current_user.stripe_customer_id, "")

    return JSONResponse(content={"url": url})