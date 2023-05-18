import stripe
from app.models import User, Subscription, PriceTier
from sqlalchemy.orm import Session
import os
import json
from datetime import datetime

stripe.api_key = os.environ.get(
    "STRIPE_API_KEY", "sk_test_51K7WUzKHkgogKyeFKj5vTjzSMpHwBPR4oFpPfb1MEszdEGGV13zoccqyXfImvsCGH9D09JxZ1GdWsRTGrzGEdqkN00v7zQXERy")
APPLICATION_SERVER = os.environ.get(
    "APPLICATION_SERVER", "http://localhost:3000/profile")


class StripeService():
    def __init__(self, db: Session):
        self.db = db

    def create_customer(self, user):
        # make sure we don't overwrite an existing customer in stripe
        if user.stripe_customer_id:
            raise "User already attached to Stripe Customer"

        customer = stripe.Customer.create(
            email=user.email,
            name=f"{user.first_name} {user.last_name}"
        )

        user.stripe_customer_id = customer["id"]
        self.db.commit()

    def create_checkout_session(self, stripe_id: str, price_name: str = "Monthly", redirect_url: str = ""):
        if redirect_url == "":
            redirect_url = APPLICATION_SERVER

        price_id = self.db.query(PriceTier).filter(
            PriceTier.name == price_name).first().id

        session = stripe.checkout.Session.create(
            success_url=f"{redirect_url}?success=true",
            cancel_url=redirect_url,
            mode="subscription",
            line_items=[{
                "price": price_id,
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

    def handle_webhook(self, request_data, signature, testing=False):
        webhook_secret = os.environ.get(
            "STRIPE_WEBHOOK_SECRET", "whsec_5b1d3db776f9410b8297cdd1c3e7df668bc032aaf84486edf9c9212b3633a13d")

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

        print(event_type)

        if event_type == "checkout.session.completed":
            customer_id = event['data']['object']['customer']

            user = self.db.query(User).filter_by(
                stripe_customer_id=customer_id).first()

            subscription_id = event['data']['object']['subscription']

            subscription_object = stripe.Subscription.retrieve(subscription_id)

            subscription_item = subscription_object["items"]["data"][0]
            subscription_item_id = subscription_item["id"]
            price_id = subscription_item["price"]["id"]
            billed_price = float(
                subscription_item["price"]["unit_amount_decimal"])

            if user:
                new_subscription = Subscription(
                    user_id=user.id,
                    stripe_subscription_id=subscription_id,
                    stripe_subscription_item_id=subscription_item_id,
                    price_tier_id=price_id,
                    billed_price=billed_price,
                )

                self.db.add(new_subscription)

                self.db.commit()

        if event_type == 'invoice.payment_failed':
            customer_id = event['data']['object']['customer']

            user = self.db.query(User).filter_by(
                stripe_customer_id=customer_id).first()

            if user:
                user.is_current = False
                self.db.commit()

        if event_type == 'invoice.paid':
            customer_id = event['data']['object']['customer']

            user = self.db.query(User).filter_by(
                stripe_customer_id=customer_id).first()

            if user:
                user.is_current = True
                self.db.commit()

        # handle product creation
        # handle product updating
        # handle product deletion
        # handle price creation
        if event_type == 'price.created':
            event_object = event["data"]["object"]
            pt = self.create_price_tier(event_object)

            self.db.add(pt)
            self.db.commit()

        # handle price updating
        if event_type == 'price.updated':
            pt = self.db.query(PriceTier).filter_by(
                id=event["data"]["object"]["id"]).first()
            event_object = event["data"]["object"]
            # our pt does not exist

            if not pt:
                pt = self.create_price_tier(event_object)

                self.db.add(pt)
            else:
                unit_amount = float(event_object["unit_amount_decimal"])

                pt.price = unit_amount or pt.price
                pt.name = event["data"]["object"]["nickname"] or pt.name

            self.db.commit()

        # handle price deletion
        if event_type == 'price.deleted':
            pt = self.db.query(PriceTier).filter_by(
                id=event["data"]["object"]["id"])

            self.db.delete(pt)
            self.db.commit()

        # handle updates to subscriptions
        if event_type == "customer.subscription.updated":
            customer_id = event['data']['object']['customer']
            user = self.db.query(User).filter_by(
                stripe_customer_id=customer_id).first()
            stripe_id = event['data']['object']['id']
            subscription = self.db.query(Subscription).filter(
                Subscription.stripe_subscription_id == stripe_id).first()
            # handle cancellation
            if event["data"]['object']['cancel_at_period_end']:
                cancel_date = event['data']['object']['cancel_at']

                subscription.deleted_at = datetime.utcfromtimestamp(
                    cancel_date)

                self.db.commit()
            # handle renewal
            elif subscription and subscription.deleted_at and not event['data']['object']['cancel_at_period_end']:
                subscription.deleted_at = None

                self.db.commit()

        return True

    def create_price_tier(self, event_object):
        pt = PriceTier(
            id=event_object["id"],
            name=event_object["nickname"] or "",
            price=float(event_object["unit_amount_decimal"])
        )

        self.db.add(pt)
        self.db.commit()
        self.db.refresh(pt)

        return pt

    def cancel_subscription(self, subscription):
        stripe.Subscription.delete(subscription.subscriptpion_item_id)

        return True

    @classmethod
    def get_user_current_window(self, subscription_id):
        # get the full subscription object from stripe
        stripe_subscription = stripe.Subscription.retrieve(subscription_id)

        # return period start and end
        period_start = datetime.fromtimestamp(
            stripe_subscription["current_period_start"])
        period_end = datetime.fromtimestamp(
            stripe_subscription["current_period_end"])

        return period_start, period_end
