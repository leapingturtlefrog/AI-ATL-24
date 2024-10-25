# home.py

import streamlit as st

def home_page(st, session_logs):
    st.success(f"Welcome back, {st.session_state.caregiver_name}!")
    st.write(f"Patient: {st.session_state.patient_name}")
    st.write("Select an option from the menu to get started.")
    # Display recent sessions
    st.subheader("Recent Sessions")
    logs = session_logs.get(st.session_state.user_email, [])
    if logs:
        for log in logs[-3:][::-1]:
            st.write(f"Session on {log['date']} - Duration: {log['duration']} mins")
    else:
        st.write("No sessions found.")
