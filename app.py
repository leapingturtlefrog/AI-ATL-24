import streamlit as st

from components.data import session_logs, photo_db, initialize_session_state
from components.home import home_page
from components.sign_in_or_register import sign_in_or_register_page
from components.register import register_page
from components.upload_photos import upload_photos_page
from components.start_session import start_session_page
from components.profile import profile_page
from components.play_audio import play_audio_page

from functions.sign_out_function import sign_out_function

def main():
    initialize_session_state()
    
    if 'logged_out_recently' not in st.session_state:
        st.session_state.logged_out_recently = False
    
    if st.session_state.logged_out_recently:
        sign_in_or_register_page(st)
        return
    
    if 'signed_in' not in st.session_state:
        st.session_state.signed_in = False
    
    st.title("Memory Lane")
   
    if st.session_state.signed_in:
        menu = ["Home", "Start Session", "Profile", "Upload Photos", "Sign out"]
    else:
        menu = ["Sign in or Register"]

    choice = st.sidebar.selectbox("Menu", menu)
    
    match choice:
        case "Home":
            home_page(st, session_logs)
        case "Start Session":
            start_session_page(st, session_logs)
        case "Profile":
            profile_page(st)
        case "Upload Photos":
            upload_photos_page(st, photo_db)
        case "Sign out":
            sign_out_function(st)
            sign_in_or_register_page(st)
        case "Sign in or Register":
            sign_in_or_register_page(st)
        case _:
            print("Error. Selection Other Than Options Made")
            st.subheader("Please select one of the options.")

if __name__ == "__main__":
    main()

