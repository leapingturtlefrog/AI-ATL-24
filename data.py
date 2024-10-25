# data.py
import streamlit as st

# Dummy databases
user_db = {}
session_logs = {}
photo_db = {}

# Session state management
def initialize_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_email' not in st.session_state:
        st.session_state.user_email = ''
    if 'patient_name' not in st.session_state:
        st.session_state.patient_name = ''
    if 'caregiver_name' not in st.session_state:
        st.session_state.caregiver_name = ''
    if 'photos_uploaded' not in st.session_state:
        st.session_state.photos_uploaded = False
    if 'analyzed_photos' not in st.session_state:
        st.session_state.analyzed_photos = []
    if 'session_history' not in st.session_state:
        st.session_state.session_history = []
    if 'current_photo' not in st.session_state:
        st.session_state.current_photo = None
