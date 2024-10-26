# app.py

import streamlit as st
from PIL import Image

from pages.data import session_logs, photo_db, initialize_session_state
from pages.home import home_page
from pages.login import login_page
from pages.register import register_page
from pages.upload_photos import upload_photos_page
from pages.start_session import start_session_page
from pages.settings import settings_page

def display_audio5(st):
    import os
    html_file_path = os.path.join("pages", "listen.html")
    with open(html_file_path, "r") as f:
        html_content = f.read()

    st.components.v1.html(html_content, height=600, scrolling=True)

def main():
    if 'logged_out_recently' not in st.session_state:
        st.session_state.logged_out_recently = False
    
    if st.session_state.logged_out_recently:
        login_page(st)
        return
    
    st.session_state.logged_in = True
    st.title("Memory Lane")
    initialize_session_state()
   
    if st.session_state.logged_in:
        menu = ["Home", "Upload Photos", "Start Session", "Settings", "Logout", "Audio5"]
    else:
        menu = ["Home", "Login", "Register"]

    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        if st.session_state.logged_in:
            home_page(st, session_logs)
        else:
            st.subheader("Welcome to Memory Lane")
            st.write("Please login or register to continue.")
    elif choice == "Login":
        login_page(st)
    elif choice == "Register":
        register_page(st, user_db)
    elif choice == "Upload Photos" and st.session_state.logged_in:
        upload_photos_page(st, photo_db)
    elif choice == "Start Session" and st.session_state.logged_in:
        start_session_page(st, session_logs)
    elif choice == "Settings" and st.session_state.logged_in:
        settings_page(st)
    elif choice == "Logout" and st.session_state.logged_in:
        logout(st)
    elif choice == "Audio5":
        pass
        display_audio5(st)
    else:
        st.subheader("Please login to access this page.")

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
    st.rerun()

if __name__ == "__main__":
    main()

