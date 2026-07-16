from kiteconnect import KiteConnect

from app_config import settings
from services.auth.broker_auth import BrokerAuth

from pydantic import SecretStr

def secret(value):
    if value is None:
        return None
    if isinstance(value, SecretStr):
        return value.get_secret_value()
    return value

class ZerodhaAuth(BrokerAuth):

    def __init__(self):

        self.kite = KiteConnect(
            api_key=secret(settings.zerodha_api_key),
        )

    @property
    def login_url(self):

        return self.kite.login_url()

    def exchange_request_token(
        self,
        request_token: str,
    ) -> str:

        session = self.kite.generate_session(
            request_token=request_token,
            api_secret=secret(settings.zerodha_api_secret),
        )

        return session["access_token"]

    def verify(
        self,
        access_token: str,
    ) -> bool:

        try:

            self.kite.set_access_token(
                access_token,
            )

            self.kite.profile()

            return True

        except Exception:

            return False
        
    def authenticate_from_callback(
        self,
        query_params,
    ) -> str | None:

        request_token = query_params.get(
            "request_token",
        )

        if not request_token:

            return None

        return self.exchange_request_token(
            request_token,
        )