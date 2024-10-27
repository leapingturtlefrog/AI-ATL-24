import streamlit as st
import firebase_admin
from firebase_admin import db, credentials, storage

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
    page_title="CareConnect",
    page_icon="./static/icon.svg",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if not firebase_admin._apps:
    cred = credentials.Certificate("./components/config/creds.json")
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://ai-atl-new-default-rtdb.firebaseio.com/",
        "storageBucket": "ai-atl-new.appspot.com"
    })
    db_ref = db.reference("/") 
    bucket = storage.bucket() 

with open("./components/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def fetch_metrics():
    ref = db.reference("metrics")
    data = ref.get()
    parsed_metrics = {k: v for k, v in data.items()}
    # image_dict = {entry["description"]: entry["image_url"] for entry in data.values()}
    print(data)
    print(parsed_metrics)
    return parsed_metrics

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
    
    add_custom_css(st)
    
    with st.sidebar:
        if st.session_state.signed_in:
            st.image("./static/icon.svg", caption="", width=40)
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
            metrics = fetch_metrics()
            largest_keys = sorted(metrics.keys(), reverse=True)[:10]
            sorted_metrics = {key: metrics[key] for key in largest_keys}
            sorted_metrics = dict(sorted(sorted_metrics.items()))
            home_page(st, sorted_metrics)
        case "session":
            start_session_page(st)
        case "profile":
            profile_page(st, photo_db)
        case "sign_in_or_register":
            sign_in_or_register_page(st)
        case _:
            print("Selection not available.")

def home_button():
    if st.session_state.page == "session":
        upload_user_data()
    st.session_state.page = "home"

def session_button():
    st.session_state.page = "session"

def profile_button():
    if st.session_state.page == "session":
        upload_user_data()
    st.session_state.profile_viewed_once = False
    st.session_state.page = "profile"

def sign_out_button():
    if st.session_state.page == "session":
        upload_user_data()
    sign_out(st)
    st.session_state.page = "sign_in_or_register"

def sign_in_button():
    st.session_state.page = "sign_in_or_register"

def upload_user_data():
    counter_ref = db.reference("counter")
    counter_ref.child("counter").set(counter_ref.child("counter").get()+1)
    number = counter_ref.child("counter").get()
    metrics_ref = db.reference("metrics")
    metrics_ref.child(str(number)).set(st.session_state.metrics)
    conversations_histories_ref = db.reference("conversation_histories")
    conversations_histories_ref.child(str(number)).set(st.session_state.conversation_history)
    print("Uploaded data.")

if __name__ == "__main__":
    main()
