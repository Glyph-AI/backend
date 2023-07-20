from app.models import User, Subscription, PriceTier, Product
from sqlalchemy.orm import Session
from apiclient.discovery import build
from datetime import datetime, timedelta
import base64
import json

import app.schemas as schemas

PACKAGE_NAME = "com.glyphassistant.app.twa"
SUBSCRIPTION_ID = "glyph"
GRACE_PERIOD_DAYS = 7

class GooglePlayService():
    def __init__(self, db: Session):
        self.service = build('androidpublisher', 'v3')
        self.db = db
        self.webhook_method_map = {
            # SUBSCRIPTION_RECOVERED
            1: self.handle_recovery,
            
            # SUBSCRIPTION_RENEWED
            2: self.handle_renewal,
            
            # SUBSCRIPTION_CANCELED
            3: self.handle_cancel,
            
            # SUBSCRIPTION_PURCHASED
            4: self.handle_purchase,
            
            # SUBSCRIPTION_ON_HOLD
            5: self.handle_hold,
            
            # SUBSCRIPTION_IN_GRACE_PERIOD
            6: self.handle_grace_period,

            # SUBSCRIPTION_RESTARTED
            7: self.handle_restart,
            
            # "SUBSCRIPTION_PRICE_CHANGE_CONFIRMED": ,
            # 8:
            
            # SUBSCRIPTION_DEFERRED
            9: self.handle_defer,
            
            # SUBSCRIPTION_PAUSED
            10: self.handle_pause ,
            
            # SUBSCRIPTION_PAUSE_SCHEDULE_CHANGED
            11: self.handle_pause_schedule_change,
            
            # SUBSCRIPTION_REVOKED
            12: self.handle_revoke,
            
            # SUBSCRIPTION_EXPIRED
            13: self.handle_expiration
        }

    def get_subscription_from_play(self, token):
        resp = self.service.purchases().subscriptions().get(packageName=PACKAGE_NAME, subscriptionId=SUBSCRIPTION_ID, token=token).execute()
        return resp

    def validate_subscription(self, googleToken: str, current_user: schemas.User):
        try:
            # verify purchase
            resp = self.get_subscription_from_play(googleToken)
            # grant access by creating a subscription
            price_tier = self.db.query(PriceTier).filter(PriceTier.price == 499).first()
            subscription = Subscription(
                user_id=current_user.id,
                price_tier_id=price_tier.id,
                google_token=googleToken,
                current_window_start_date=datetime.now(),
                current_window_end_date=datetime.fromtimestamp(int(resp["expiryTimeMillis"]) // 1000) + timedelta(days=GRACE_PERIOD_DAYS)
            )

            self.db.add(subscription)
            self.db.commit()
            self.db.refresh(subscription)

            current_user.is_current = True
            self.db.commit()
            # acknolwedge to the server
            self.service.purchases().subscriptions().acknowledge(packageName=PACKAGE_NAME, subscriptionId=SUBSCRIPTION_ID, token=googleToken).execute()
            return True
        except Exception as e:
            print("VALIDATION FAILED")
            print(e)
            return False
        
    def get_user_from_purchase_token(self, token):
        sub = self.db.query(Subscription).filter(Subscription.google_token == token).first()
        return sub.user
        
    def handle_recovery(self, notification):
        self.handle_renewal(notification)
        pass

    def handle_renewal(self, notification):
        # if a subscription renews, we just update the current_window start and end
        user = self.get_user_from_purchase_token(notification["purchaseToken"])
        user_sub = user.active_subscriptions()[0]
        resp = self.get_subscription_from_play(notification["purchaseToken"])
        
        # assume that the renewal is right at the start of the new period
        user_sub.current_window_start_date = datetime.now()
        user_sub.current_window_end_date = datetime.fromtimestamp(int(resp["expiryTimeMillis"]) // 1000)

        if user_sub.deleted_at:
            user_sub.deleted_at = None

        self.db.commit()
        
        return True

    def handle_cancel(self, notification):
        # If a user cancelswe do nothing, we go ahead and add deleted_at to the subscription to match the end 
        # of the current window
        user = self.get_user_from_purchase_token(notification["purchaseToken"])
        user_sub = user.active_subscriptions()[0]
        user_sub.deleted_at = user_sub.current_window_end_date - timedelta(days=GRACE_PERIOD_DAYS)

        self.db.commit()
        
        return True

    def handle_purchase(self, notification):
        # this should be handled by the Ack flow, but let's make sure anyways
        # The token should exist on a subscription already
        sub = self.db.query(Subscription).filter(Subscription.google_token == notification["purchaseToken"]).first()
        # if we don't have one we should go ahead and create one
        if not sub:
            resp = self.get_subscription_from_play(notification["purchaseToken"])
            # grant access by creating a subscription
            price_tier = self.db.query(PriceTier).filter(PriceTier.price == 499).first()
            user = self.get_user_from_purchase_token(notification["purchaseToken"])
            subscription = Subscription(
                user_id=user.id,
                price_tier_id=price_tier.id,
                google_token=notification["purchaseToken"],
                current_window_start_date=datetime.now(),
                current_window_end_date=datetime.fromtimestamp(int(resp["expiryTimeMillis"]) // 1000)
            )

            self.db.add(subscription)
            self.db.commit()
            self.db.refresh(subscription)

        return True

    def handle_hold(self, notification):
        # treat hold like revoke for now. User re-subscribe will behave like renewal.
        self.handle_revoke(notification)
        return True

    def handle_restart(self, notification):
        # use renewal logic to handle this
        self.handle_renewal(notification)
        return True

    def handle_defer(self, notification):
        pass

    def handle_pause(self, notification):
        self.handle_cancel(notification)
        return True

    def handle_pause_schedule_change(self, notification):
        pass

    def handle_grace_period(self, notification):
        user = self.get_user_from_purchase_token(notification["purchaseToken"])
        user_sub = user.active_subscriptions()[0]
        user_sub.current_window_end_date = datetime.now() + timedelta(days=GRACE_PERIOD_DAYS)
        self.db.commit()

        return True

    def handle_revoke(self, notification):
        user = self.get_user_from_purchase_token(notification["purchaseToken"])
        user_sub = user.active_subscriptions()[0]
        user_sub.deleted_at = datetime.now()

        user.is_current = False

        self.db.commit()
        self.db.refresh(user_sub)
        return True

    def handle_expiration(self, notification):
        user = self.get_user_from_purchase_token(notification["purchaseToken"])
        user_sub = user.active_subscriptions()[0]
        user_sub.deleted_at = datetime.now()
        user.is_current = False
        self.db.commit()
        return True
        
    def handle_webhook(self, webhook_event):
        print("-" * 80)
        print(base64.b64decode(webhook_event["message"]["data"]).decode('utf-8'))
        event = json.loads(base64.b64decode(webhook_event["message"]["data"]).decode('utf-8'))
        
        if "subscriptionNotification" not in event:
            print("Not a subscription notification. Acking to the queue.")
            return True
        
        notification = event["subscriptionNotification"]
        try:
            method = self.webhook_method_map[notification["notificationType"]]
            return method(notification)

        except KeyError as ke:
            print(ke)
            return True
        except Exception as e:
            print(e)
            return True