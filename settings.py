# settings.py

import streamlit as st

def settings_page(st):
    st.subheader("Settings")
    st.write("Configure your preferences.")
    interaction_mode = st.selectbox("Interaction Mode", ["Text", "Voice"])
    st.write("Settings saved.")
