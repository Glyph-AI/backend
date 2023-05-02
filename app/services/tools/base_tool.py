from app.models import ToolAuthentication
from google.oauth2.credentials import Credentials
import google_auth_oauthlib
import oauthlib
import os


class BaseTool:
    def __init__(self, db, bot_id, chat_id, tool_id, user_id):
        self.db = db
        self.bot_id = bot_id
        self.chat_id = chat_id
        self.tool_id = tool_id
        self.user_id = user_id
        # fire specific class inits if they have them
        self.class_init()

    def class_init(self):
        pass

    def __internal_query_requires(self):
        return ""

    def build_google_creds(self):
        try:
            CLIENT_ID = self.client_id
            CLIENT_SECRET = self.client_secret
            auth_info = self.__get_tool_authentication()

            if auth_info.access_token is None:
                client_config = {
                    "web": {
                        "client_id": CLIENT_ID,
                        "client_secret": CLIENT_SECRET,
                        "redirect_uris": [
                            "https://dev.glyphassistant.com/auth/google",
                            "http://localhost:3000/auth/google"
                        ],
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://accounts.google.com/o/oauth2/token"
                    }
                }

                flow = google_auth_oauthlib.flow.Flow.from_client_config(
                    client_config,
                    scopes=self.scope,
                    state=None,
                    redirect_uri="http://localhost:3000/auth/google"
                )

                try:
                    creds = flow.fetch_token(code=auth_info.authorization_code)
                except oauthlib.oauth2.rfc6749.errors.InvalidGrantError as e:
                    auth_info.delete()
                    raise (e)

                print(creds)
                auth_info.access_token = creds["access_token"]
                auth_info.refresh_token = creds["refresh_token"]
                self.db.commit()

                print("SAVED INFO")

                return flow.credentials
            else:
                creds = Credentials.from_authorized_user_info(
                    info={"client_id": self.client_id,
                          "client_secret": self.client_secret,
                          "access_token": auth_info.access_token,
                          "refresh_token": auth_info.refresh_token,
                          "refresh": True},
                    scopes=[self.scope]
                )

                return creds

        except Exception as e:
            print(e)
            raise (Exception("Error retrieving google credentials"))

    def __get_tool_authentication(self):
        auth_info = self.db.query(ToolAuthentication).filter(
            ToolAuthentication.user_id == self.user_id,
            ToolAuthentication.tool_id == self.tool_id,
            ToolAuthentication.bot_id == self.bot_id
        ).first()

        if auth_info is None:
            raise (Exception("No Tool Authentication Found"))

        return auth_info
