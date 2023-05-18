from fastapi import APIRouter, Depends, Request, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import os
from enum import Enum

from app.dependencies import get_db, get_current_user
from app.schemas import User
from app.services import StripeService
from app.subscription_tiers import tiers

subscriptions_router = APIRouter(tags=["Subscriptions API"])


class BillCycle(str, Enum):
    SILVER_MONTHLY = "SILVER_monthly"
    SILVER_ANNUALLY = "SILVER_annually"
    GOLD_MONTHLY = "GOLD_monthly"
    GOLD_ANNUALLY = "GOLD_annually"
    PLATINUM_MONTHLY = "PLATINUM_monthly"
    PLATINUM_ANNUALLY = "PLATINUM_annually"


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

@subscriptions_router.get("/tiers")
async def get_tiers(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return tiers
