# upload_photos.py

import streamlit as st
from utils import analyze_photos

def upload_photos_page(st, photo_db):
    st.subheader("Upload Photos")
    st.write("Upload the patient's photo library.")
    uploaded_files = st.file_uploader("Choose images", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])
    if uploaded_files:
        st.session_state.photos_uploaded = True
        st.write("Analyzing photos...")
        # Simulate photo analysis
        analyzed_photos = analyze_photos(uploaded_files)
        st.session_state.analyzed_photos.extend(analyzed_photos)
        photo_db[st.session_state.user_email] = st.session_state.analyzed_photos
        st.success("Photos uploaded and analyzed successfully!")
    else:
        st.write("No photos uploaded yet.")
