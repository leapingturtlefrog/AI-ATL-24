# login.py

import streamlit as st
from streamlit_oauth import OAuth2Component
import base64
import json
import os

def sign_in_or_register_page(st):
    st.markdown(
        """
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@500&display=swap" rel="stylesheet">
        <style>
        .centered-container {
            display: flex;
            align-items: center;
            justify-content: center;
            margin-top: 20vh;
        }
        .logo {
            width: 2.5em;  /* Match logo size to title font size */
            height: 2.5em;  /* Keep aspect ratio consistent */
            margin-right: 15px;
        }
        .title {
            font-size: 2.5em;
            font-family: 'Poppins', sans-serif;
            font-weight: 500;
            color: #333333;
            text-transform: capitalize;
            letter-spacing: 0.03em;
        }
        .google-button {
            width: 200px;  /* Set a specific width for the Google button */
            padding: 10px 15px;  /* Adjust padding to make the button narrower */
            font-size: 1em;  /* Adjust font size if needed */
            display: flex;
            align-items: center;
            justify-content: center;
            margin-top: 20px;
            background-color: #f5f5f5;  /* Light background */
            border-radius: 5px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);  /* Optional shadow */
            border: none;  /* Remove any border if present */
        }
        </style>
        """,
        unsafe_allow_html=True
    )



        # Generate absolute path for the logo file and check if it exists
    # Generate absolute path for the logo file and check if it exists
    logo_path = os.path.join(os.path.dirname(__file__), "../static/icon.svg")

    if os.path.exists(logo_path):
        with open(logo_path, "r") as file:
            svg_content = file.read()  # Read SVG content directly

        # Modify SVG size by adding width and height attributes
        svg_content = svg_content.replace('<svg', '<svg width="2.5em" height="2.5em"', 1)
        
        st.markdown(
            f"""
            <div class="centered-container">
                <div class="logo">{svg_content}</div>  <!-- Embed SVG directly with updated size -->
                <span class="title">Cognisense</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        # Show error with absolute path for troubleshooting
        st.markdown(
            """
            <div class="centered-container">
                <span class="title">cognisense</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.error(f"Logo file not found at {logo_path}. Please check the path.")


    # OAuth2 Setup and Google sign-in button
    CLIENT_ID = st.secrets.google_auth_client_id
    CLIENT_SECRET = st.secrets.google_auth_client_secret
    AUTHORIZE_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
    REVOKE_ENDPOINT = "https://oauth2.googleapis.com/revoke"

    if "auth" not in st.session_state:
        oauth2 = OAuth2Component(
            CLIENT_ID, CLIENT_SECRET, AUTHORIZE_ENDPOINT, TOKEN_ENDPOINT, TOKEN_ENDPOINT, REVOKE_ENDPOINT
        )
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
        
        # Process result from Google OAuth
        if result:
            id_token = result["token"]["id_token"]
            payload = id_token.split(".")[1]
            payload += "=" * (-len(payload) % 4)
            payload = json.loads(base64.b64decode(payload))
            email = payload["email"]
            
            # Store user information in session state
            st.session_state["auth"] = payload["email"]
            st.session_state["token"] = result["token"]
            st.session_state["patient_name"] = payload["name"]
            st.session_state["patient_first_name"] = payload["name"].split(" ")[0]
            st.session_state.signed_in = True
            st.session_state.page = "home"
            st.rerun()
    else:
        # Display logged-in state
        st.write("You are logged in!")
        st.write(st.session_state["auth"])
        st.write(st.session_state["token"])
        
        # Logout button
        if st.button("Logout"):
            del st.session_state["auth"]
            del st.session_state["token"]
            st.session_state.signed_in = False
            st.session_state.signed_out_recently = True
            st.rerun()

    # Logout success message
    if 'signed_out_recently' in st.session_state and st.session_state.signed_out_recently:
        st.success("Logged out successfully.")
