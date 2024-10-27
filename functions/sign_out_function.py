import streamlit as st

def sign_out(st):
    st.session_state.signed_in = False
    st.session_state.signed_out_recently = True
    st.session_state.user_email = ''
    st.session_state.patient_name = ''
    st.session_state.caregiver_name = ''
    st.session_state.session_history = []
    st.session_state.current_photo = None
    
    if 'auth' in st.session_state:
        del st.session_state.auth
    if 'token' in st.session_state:
        del st.session_state.token
    
    '''
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
    '''
