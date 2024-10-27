# home.py

import streamlit as st

def home_page(st, session_logs, name):
    st.subheader(f"Welcome Back, {name}!")

    st.write("Recent Sessions")
