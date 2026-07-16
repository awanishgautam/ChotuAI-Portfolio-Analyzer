import streamlit as st

from services.auth.auth_factory import AuthFactory
from brokers.types import BrokerType

def login(
    broker: BrokerType,
):

    auth = AuthFactory.create(broker)

    # Process broker callback first
    try:

        access_token = auth.authenticate_from_callback(
            st.query_params,
        )

        if access_token:

            st.session_state.access_token = access_token
            st.query_params.clear()

            st.rerun()

    except Exception as e:

        st.error(str(e))
        st.stop()

    # No session yet → show login
    if "access_token" not in st.session_state:

        st.info(
            "Please login to continue."
        )

        st.link_button(
            "Login",
            auth.login_url,
        )

        st.stop()

    # Existing session → verify it
    if not auth.verify(
        st.session_state.access_token,
    ):

        st.session_state.pop(
            "access_token",
            None,
        )

        st.warning(
            "Session expired. Please login again."
        )

        st.rerun()