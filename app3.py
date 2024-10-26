import streamlit as st
from PIL import Image

from components.data import session_logs, photo_db, initialize_session_state
from components.home import home_page
from components.login import login_page
from components.register import register_page
from components.upload_photos import upload_photos_page
from components.start_session import start_session_page
from components.settings import settings_page
from components.play_audio import play_audio_page
from components.profile import profile_page


def add_custom_css():


    st.markdown(
    """
    <style>
    button {
        background: none!important;
        border: none;
        padding: 0!important;
        color: #6EAEA1 !important;
        text-decoration: none;
        cursor: pointer;
        border: none !important;
    }
    button:hover {
        text-decoration: none;
        color: black !important;
    }
    button:focus {
        outline: none !important;
        box-shadow: none !important;
        color: black !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
    )

def main():
    # TODO: do not hardcode this
    st.session_state.logged_in = True

    if 'logged_out_recently' not in st.session_state:
        st.session_state.logged_out_recently = False

    if st.session_state.logged_out_recently:
        login_page(st)
        return

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    initialize_session_state()
    add_custom_css()

    with st.sidebar:
        if st.session_state.logged_in:
            if st.button("Home"):
                st.session_state.page = "home"
            if st.button("Upload Photos"):
                st.session_state.page = "upload_photos"
            if st.button("Start Session"):
                st.session_state.page = "start_session"
            if st.button("Settings"):
                st.session_state.page = "settings"
            if st.button("Play Audio"):
                st.session_state.page = "play_audio"
            if st.button("Logout"):
                logout(st)
            if st.button("Profile"):
                st.session_state.page = "profile"
        else:
            if st.button("Home"):
                st.session_state.page = "welcome"
            if st.button("Login"):
                st.session_state.page = "login"
            if st.button("Register"):
                st.session_state.page = "register"

    if "page" not in st.session_state:
        st.session_state.page = "welcome"

    if st.session_state.logged_in:
        if st.session_state.page == "home":
            home_page(st, session_logs)
        elif st.session_state.page == "upload_photos":
            upload_photos_page(st, photo_db)
        elif st.session_state.page == "start_session":
            start_session_page(st, session_logs)
        elif st.session_state.page == "settings":
            settings_page(st)
        elif st.session_state.page == "profile":
            profile_page(st, photo_db)
        elif st.session_state.page == "play_audio":
            play_audio_page(st)
    else:
        if st.session_state.page == "welcome":
            welcome_msg()
        elif st.session_state.page == "login":
            login_page(st)
        elif st.session_state.page == "register":
            register_page(st)


def welcome_msg():
    st.subheader("Welcome to Memory Lane")
    st.write("Please login or register to continue.")

def logout(st):
    st.session_state.logged_in = False
    st.session_state.logged_out_recently = True
    st.session_state.user_email = ''
    st.session_state.patient_name = ''
    st.session_state.caregiver_name = ''
    st.session_state.photos_uploaded = False
    st.session_state.analyzed_photos = []
    st.session_state.session_history = []
    st.session_state.current_photo = None
    st.success("Logged out successfully.")
    st.session_state.page = "welcome"
    st.rerun()

if __name__ == "__main__":
    main()