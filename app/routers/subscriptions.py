from fastapi import APIRouter, Depends, Request, Header
from fastapi.responses import JSONResponse
from apiclient.discovery import build
from sqlalchemy.orm import Session
from datetime import datetime
import os
from enum import Enum

from app.dependencies import get_db, get_current_user
from app.models import PriceTier, Subscription
from app.schemas import User, GoogleAcknolwedgement
from app.services import StripeService, GooglePlayService

subscriptions_router = APIRouter(tags=["Subscriptions API"])


class BillCycle(str, Enum):
    MONTHLY = "Monthly"
    ANNUAL = "Annual"


@subscriptions_router.get("/subscriptions/checkout-session")
async def get_checkout_session(bill_cycle: BillCycle, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    stripe_svc = StripeService(db)

    url = stripe_svc.create_checkout_session(
        current_user.stripe_customer_id, price_name=bill_cycle)

    return JSONResponse(content={"url": url})


@subscriptions_router.get("/subscriptions/customer-portal-session")
async def get_customer_portal_session(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    stripe_svc = StripeService(db)

    url = stripe_svc.create_portal_session(
        current_user.stripe_customer_id, redirect_url="")

    return JSONResponse(content={"url": url})


@subscriptions_router.post("/stripe-webhook")
async def webhook_receive(request: Request, stripe_signature: str = Header(None), db: Session = Depends(get_db)):
    stripe_svc = StripeService(db)
    stripe_data = await request.body()
    stripe_svc.handle_webhook(stripe_data, stripe_signature)

    return JSONResponse(content={"status": "success"})

@subscriptions_router.post("/google-verification")
async def verify_google_purchase(data: GoogleAcknolwedgement, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    gps = GooglePlayService(db)
    return {"success": gps.validate_subscription(data.googleToken, current_user)} 
    
@subscriptions_router.post("/google-webhook")
async def google_webhook(webhook_event: dict, db: Session = Depends(get_db)):
    gps = GooglePlayService(db)
    return gps.handle_webhook(webhook_event)