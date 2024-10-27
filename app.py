import streamlit as st

from components.data import metrics, photo_db, initialize_session_state
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
        st.session_state.signed_in = True
    if "profile_viewed_once" not in st.session_state:
        st.session_state.profile_viewed_once = False
    
    if st.session_state.signed_in:
        menu = ["Home", "Start Session", "Profile", "Upload Photos", "Sign out"]
    else:
        menu = ["Sign in"]
    
    add_custom_css(st)
    
    with st.sidebar:
        if st.session_state.signed_in:
            st.button("Home", on_click=home_button, key=1)
            st.button("Start Session", on_click=session_button, key=2)
            st.button("Profile", on_click=profile_button, key=3)
            st.button("Sign out", on_click=sign_out_button, key=4)
        else:
            st.button("Sign in", on_click=sign_in_button, key=5)
    
    if "page" not in st.session_state:
        if st.session_state.signed_in:
            st.session_state.page = "home"
        else:
            st.session_state.page = "sign_in_or_register"
        
    match st.session_state.page:
        case "home":
            # TODO: hardcoding metrics for now - change later
            import random
            metrics = {"Session " + str(i):[random.randint(1, 60), random.randint(1, 60), random.randint(1, 60)] for i in range(1, 11)}
            home_page(st, metrics, "CHANGE ME")
        case "session":
            start_session_page(st, "")
        case "profile":
            profile_page(st, photo_db)
        case "sign_in_or_register":
            sign_in_or_register_page(st)
        case _:
            print("Selection not available.")

def home_button():
    st.session_state.page = "home"

def session_button():
    st.session_state.page = "session"

def profile_button():
    st.session_state.profile_viewed_once = False
    st.session_state.page = "profile"

def sign_out_button():
    sign_out(st)
    st.session_state.page = "sign_in_or_register"

def sign_in_button():
    st.session_state.page = "sign_in_or_register"

if __name__ == "__main__":
    main()
