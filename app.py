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

import threading
from streamlit_autorefresh import st_autorefresh

from resources.microphone_stream import MicrophoneStream, RATE, CHUNK
from resources.speech_recognition import start_recognition

class TranscriptionManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.transcription = "Listening..."

    def update_transcription(self, text):
        with self.lock:
            self.transcription = text
            print(f"Updated transcription: {text}")  # Debugging

    def get_transcription(self):
        with self.lock:
            return self.transcription

@st.cache_resource
def get_transcription_manager():
    return TranscriptionManager()

def listen_and_update(manager: TranscriptionManager):
    """
    Background thread function to listen to microphone input and update transcription.
    """
    def listen_print_loop(responses):
        try:
            for response in responses:
                if not response.results:
                    continue
                result = response.results[0]
                if not result.alternatives:
                    continue
                transcript = result.alternatives[0].transcript
                if result.is_final:
                    manager.update_transcription(f"Final transcript: {transcript}")
                else:
                    manager.update_transcription(f"Interim transcript: {transcript}")
        except Exception as e:
            manager.update_transcription(f"Error in listen_print_loop: {e}")
            print(f"Error in listen_print_loop: {e}")

    try:
        with MicrophoneStream(RATE, CHUNK) as stream:
            audio_generator = stream.generator()
            start_recognition(audio_generator, listen_print_loop)
    except Exception as e:
        manager.update_transcription(f"Error in listen_and_update: {e}")
        print(f"Error in listen_and_update: {e}")

def display_audio5(st):
    import os
    html_file_path = os.path.join("pages", "listen.html")
    with open(html_file_path, "r") as f:
        html_content = f.read()

    st.components.v1.html(html_content, height=600, scrolling=True)

def main():
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

     # Initialize the transcription manager
    manager = get_transcription_manager()

    # Start the background thread once
    if 'thread_started' not in st.session_state:
        st.session_state['thread_started'] = True
        thread = threading.Thread(target=listen_and_update, args=(manager,), daemon=True)
        thread.start()
        print("Started background thread for transcription.")

    # Auto-refresh the Streamlit app every 5 seconds (5000 milliseconds)
    st_autorefresh(interval=5000, limit=None, key="transcription_counter")

    # Get the latest transcription
    current_transcription = manager.get_transcription()

    # Display the transcription
    st.subheader("Transcription:")
    st.write(current_transcription)

def logout(st):
    st.session_state.logged_in = False
    st.session_state.user_email = ''
    st.session_state.patient_name = ''
    st.session_state.caregiver_name = ''
    st.session_state.photos_uploaded = False
    st.session_state.analyzed_photos = []
    st.session_state.session_history = []
    st.session_state.current_photo = None
    st.success("Logged out successfully.")
    st.experimental_rerun()

if __name__ == "__main__":
    main()
