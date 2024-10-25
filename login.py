# login.py

import streamlit as st

def login_page(st, user_db):
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type='password')
    if st.button("Login"):
        user = user_db.get(email)
        if user and user['password'] == password:
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.session_state.patient_name = user['patient_name']
            st.session_state.caregiver_name = user['caregiver_name']
            st.success("Login successful!")
            st.experimental_rerun()
        else:
            st.error("Invalid email or password.")
