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
        menu = ["Home", "Upload Photos", "Start Session", "Settings", "Logout", "Play Audio"]
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
    elif choice == "Play Audio" and st. session_state.logged_in:
        play_audio_page(st)
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

