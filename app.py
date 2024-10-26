import streamlit as st

from components.data import session_logs, photo_db, initialize_session_state
from components.home import home_page
from components.sign_in_or_register import sign_in_or_register_page
from components.register import register_page
from components.upload_photos import upload_photos_page
from components.start_session import start_session_page
from components.profile import profile_page
from components.play_audio import play_audio_page

from functions.sign_out_function import sign_out
from functions.add_custom_css_function import add_custom_css

st.set_page_config(
    page_title="Memory Lane",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def main():
    initialize_session_state()
    
    if "logged_out_recently" not in st.session_state:
        st.session_state.logged_out_recently = False
    
    if st.session_state.logged_out_recently:
        sign_in_or_register_page(st)
        return
    
    if "signed_in" not in st.session_state:
        st.session_state.signed_in = False
    
    st.title("Memory Lane\n")
   
    if st.session_state.signed_in:
        menu = ["Home", "Start Session", "Profile", "Upload Photos", "Sign out"]
    else:
        menu = ["Sign in or Register"]
    
    add_custom_css(st)
    
    with st.sidebar:
        if st.session_state.signed_in:
            if st.button("Home"):
                st.session_state.page = "home"
                st.session_state.sidebar_visible = False
            elif st.button("Start Session"):
                st.session_state.page = "session"
                st.session_state.sidebar_visible = False
            elif st.button("Profile"):
                st.session_state.page = "profile"
            elif st.button("Sign Out"):
                sign_out(st)
                st.session_state.page = "sign_in_or_register"
        else:
            if st.button("Please sign in or Register"):
                st.session_state.page = "sign_in_or_register"
    
    if "page" not in st.session_state:
        st.session_state.page = "sign_in_or_register"
    
    match st.session_state.page:
        case "home":
            home_page(st, session_logs)
        case "session":
            start_session_page(st, session_logs)
        case "profile":
            profile_page(st, photo_db)
        case "sign_in_or_register":
            sign_in_or_register_page(st)
        case _:
            print("Selection not available.")

if __name__ == "__main__":
    main()
