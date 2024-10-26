# login.py

import streamlit as st
from streamlit_oauth import OAuth2Component
import base64
import json

def sign_in_or_register_page(st):
    st.title("Sign in or Register")

    CLIENT_ID = st.secrets.google_auth_client_id
    CLIENT_SECRET = st.secrets.google_auth_client_secret
    AUTHORIZE_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
    REVOKE_ENDPOINT = "https://oauth2.googleapis.com/revoke"

    if "auth" not in st.session_state:
        oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZE_ENDPOINT, TOKEN_ENDPOINT, TOKEN_ENDPOINT, REVOKE_ENDPOINT)
        result = oauth2.authorize_button(
            name="Continue with Google",
            icon="https://www.google.com.tw/favicon.ico",
            redirect_uri="http://localhost:8501/",
            scope="openid email profile",
            key="google",
            extras_params={"access_type": "offline"},
            use_container_width=True,
            pkce="S256",
        )
        
        if result:
            st.write(result)
            id_token = result["token"]["id_token"]
            payload = id_token.split(".")[1]
            payload += "=" * (-len(payload) % 4)
            payload = json.loads(base64.b64decode(payload))
            email = payload["email"]
            
            st.session_state["auth"] = email
            st.session_state["token"] = result["token"]
            st.session_state.signed_in = True
            st.rerun()
    else:
        st.write("You are logged in!")
        st.write(st.session_state["auth"])
        st.write(st.session_state["token"])
        if st.button("Logout"):
            del st.session_state["auth"]
            del st.session_state["token"]
            st.session_state.signed_in = False
    
    if 'signed_out_recently' in st.session_state and st.session_state.signed_out_recently:
        st.success("Logged out successfully.")
    
