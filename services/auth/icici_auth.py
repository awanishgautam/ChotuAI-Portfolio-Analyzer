from breeze_connect import BreezeConnect

from app_config import settings

from pydantic import SecretStr
import uvicorn
import threading
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from services.auth.broker_auth import BrokerAuth
from network.callback_server import app
from urllib.parse import quote_plus
import streamlit as st


def secret(value):

    if value is None:
        return None

    if isinstance(value, SecretStr):
        return value.get_secret_value()

    return value

def start_callback_server():
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=5000,
        reload=False,
        log_level="warning",
    )

#---------------------------------------------------------------
# IciciAuth class
#---------------------------------------------------------------
class IciciAuth(BrokerAuth):

    def __init__(self):

        self.breeze = BreezeConnect(
            api_key=secret(
                settings.icici_api_key,
            ),
        )

        if "callback_server_started" not in st.session_state:

            threading.Thread(
                target=start_callback_server,
                daemon=True,
            ).start()

        st.session_state.callback_server_started = True

    @property
    def login_url(self) -> str:
        """
        Breeze login URL.
        """

        api_key = quote_plus(
            secret(
                settings.icici_api_key,
            )
        )

        return (
            "https://api.icicidirect.com/"
            f"apiuser/login?api_key={api_key}"
        )
    
    def exchange_request_token(
        self,
        api_session: str,
    ) -> str:

        print("exchange_request_token() entered")

        result = self.breeze.generate_session(
            api_secret=secret(settings.icici_api_secret),
            session_token=api_session,
        )

        print("generate_session returned:")
        print(result)

        return api_session

    def verify(
        self,
        access_token: str,
    ) -> bool:

        print("=" * 60)
        print("VERIFY CALLED")
        print("Access token:", access_token)

        try:

            result = self.breeze.get_customer_details(
                api_session=access_token,
            )

            print(result)

            return True

        except Exception as e:

            print("VERIFY FAILED")
            print(type(e))
            print(e)

            return False
        
    def authenticate_from_callback(
        self,
        query_params,
    ) -> str | None:

        print("=" * 80)
        print("authenticate_from_callback called")
        print("Query params:", dict(query_params))

        api_session = query_params.get("apisession")

        print("api_session:", api_session)

        if not api_session:
            print("No api_session found")
            return None

        print("Calling exchange_request_token...")

        token = self.exchange_request_token(api_session)

        print("Returned token:", token)

        return token