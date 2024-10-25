# register.py

import streamlit as st

def register_page(st, user_db):
    st.subheader("Register")
    with st.form(key='register_form'):
        email = st.text_input("Email")
        password = st.text_input("Password", type='password')
        patient_name = st.text_input("Patient's Name")
        caregiver_name = st.text_input("Caregiver's Name")
        relationship = st.text_input("Relationship to Patient")
        patient_age = st.number_input("Age of Patient", min_value=1, max_value=120, value=70)
        consent = st.checkbox("I agree to the data usage policies.")
        submit_button = st.form_submit_button(label='Register')

    if submit_button:
        if email in user_db:
            st.error("Email already registered.")
        elif not consent:
            st.error("You must agree to the data usage policies.")
        else:
            user_db[email] = {
                'password': password,
                'patient_name': patient_name,
                'caregiver_name': caregiver_name,
                'relationship': relationship,
                'patient_age': patient_age,
            }
            st.success("Registration successful! Please login.")
            st.experimental_rerun()
