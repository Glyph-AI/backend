import stripe
from app.models import User, Subscription, PriceTier
from sqlalchemy.orm import Session
import os
import json
from datetime import datetime

stripe.api_key = os.environ.get("STRIPE_API_KEY", "sk_test_51K7WUzKHkgogKyeFKj5vTjzSMpHwBPR4oFpPfb1MEszdEGGV13zoccqyXfImvsCGH9D09JxZ1GdWsRTGrzGEdqkN00v7zQXERy")
APPLICATION_SERVER = os.environ.get("APPLICATION_SERVER", "http://localhost:3000/settings")

class StripeService():
    def __init__(self):
        self.subscription_price = os.environ.get("STRIPE_PRICE_ID", "price_1MqRWhKHkgogKyeF2oYa2oNL")

    def create_customer(self, user, db: Session):
        # make sure we don't overwrite an existing customer in stripe
        if user.stripe_customer_id:
            raise "User already attached to Stripe Customer"

        # get email for user attached to organization

        customer = stripe.Customer.create(
            email=user.email,
            name=f"{user.first_name} {user.last_name}"
        )

        user.stripe_customer_id = customer["id"]
        db.commit()

    def create_checkout_session(self, stripe_id: str, redirect_url: str = ""):
        if redirect_url == "":
            redirect_url = APPLICATION_SERVER
        session = stripe.checkout.Session.create(
            success_url=f"{redirect_url}?success=true",
            cancel_url=redirect_url,
            mode="subscription",
            line_items=[{
                "price": self.subscription_price,
                "quantity": 1
            }],
            customer=stripe_id
        )

        return session.url

    def create_portal_session(self, stripe_id: str, redirect_url: str = ""):
        if redirect_url == "":
            redirect_url = APPLICATION_SERVER
        session = stripe.billing_portal.Session.create(
            customer=stripe_id,
            return_url=redirect_url
        )

        return session.url

    def handle_webhook(self, request, db: Session, testing=False):
        # webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
        # webhook_secret = "whsec_2zC14MeNJzbEajzXCjwovH2iqrQ0jtGT"
        request_data = request.data

        signature = request.headers.get("stripe-signature")
        event = None
        event_type = None
        if not testing:
            try:
                event = stripe.Webhook.construct_event(
                    payload=request_data, sig_header=signature, secret=webhook_secret
                )

                event_type = event.type
            except Exception as e:
                raise e
        else:
            event = json.loads(request_data)
            event_type = event["type"]


        if event_type == "checkout.session.completed":
            customer_id = event['data']['object']['customer']
            # get Organization from stripe customer_id
            user = db.query(User).filter_by(
                stripe_customer_id=customer_id).first()

            subscription_id = event['data']['object']['subscription']

            subscription_object = stripe.Subscription.retrieve(subscription_id)
            subscription_item = subscription_object["items"]["data"][0]
            subscription_item_id = subscription_item["id"]
            price_id = subscription_item["price"]["id"]
            billed_price = float(
                subscription_item["price"]["unit_amount_decimal"])

            if org:
                new_subscription = Subscription(
                    user_id=user.id,
                    stripe_subscription_item_id=subscription_item_id,
                    price_tier_id=price_id,
                    billed_price=billed_price,
                )

                db.add(new_subscription)

                db.commit()

        if event_type == 'invoice.payment_failed':
            customer_id = event['data']['object']['customer']

            org = db.query(User).filter_by(
                stripe_customer_id=customer_id).first()

            if user:
                user.is_current = False
                db.commit()

        if event_type == 'invoice.paid':
            customer_id = event['data']['object']['customer']

            org = db.query(User).filter_by(
                stripe_customer_id=customer_id).first()

            if user:
                user.is_current = True
                db.commit()

        # handle product creation
        # handle product updating
        # handle product deletion
        # handle price creation
        if event_type == 'price.created':
            event_object = event["data"]["object"]
            pt = self.create_price_tier(event_object)

            db.add(pt)
            db.commit()
        
        # handle price updating
        if event_type == 'price.updated':
            pt = db.query(PriceTier).filter_by(id=event["data"]["object"]["id"]).first()
            event_object = event["data"]["object"]
            # our pt does not exist

            if not pt:
                pt = self.create_price_tier(event_object)

                db.add(pt)
            else:
                unit_amount = float(event_object["unit_amount_decimal"])
            
                pt.price = unit_amount or pt.price
                pt.name = event["data"]["object"]["nickname"] or pt.name

            db.commit()

        # handle price deletion
        if event_type == 'price.deleted':
            pt = db.query(PriceTier).filter_by(id=event["data"]["object"]["id"])

            db.delete(pt)
            db.commit()

        return True

    def create_price_tier(self, event_object, db: Session):
        pt = PriceTier(
            id=event_object["id"],
            name=event_object["nickname"] or "",
            price_per_unit=float(event_object["unit_amount_decimal"])
        )

        db.add(pt)
        db.commit()
        db.refresh(pt)

        return pt

    def cancel_subscription(self, subscription):
        stripe.Subscription.delete(subscription.subscriptpion_item_id)

        return True