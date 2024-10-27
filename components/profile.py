import streamlit as st
import os
import google.generativeai as genai
import tempfile
import uuid
import firebase_admin
from firebase_admin import db, credentials, storage
import json
import base64
from io import BytesIO
import json
import pickle
from components.start_session import fetch_images_and_descriptions

if not firebase_admin._apps:
    cred = credentials.Certificate("./components/config/creds.json")
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://ai-atl-new-default-rtdb.firebaseio.com/",
        "storageBucket": "ai-atl-new.appspot.com"
    })
    db_ref = db.reference("/")
    bucket = storage.bucket()

def encode_image(uploaded_file):
    """Convert uploaded file to base64 string"""
    try:
        bytes_data = uploaded_file.getvalue()
        base64_string = base64.b64encode(bytes_data).decode('utf-8')
        return base64_string
    except Exception as e:
        st.error(f"Error encoding image: {e}")
        return None

def decode_image(base64_string):
    """Convert base64 string back to image data"""
    try:
        image_data = base64.b64decode(base64_string)
        return image_data
    except Exception as e:
        st.error(f"Error decoding image: {e}")
        return None

def generate_descriptions(uploaded_files):
    generation_config = {
        "temperature": 0.2, 
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain", 
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro-002",
        generation_config=generation_config,
    )

    parts = []
    file_names = []

    for file in uploaded_files:
        file.seek(0)
        file_data = file.read()
        mime_type = file.type or 'application/octet-stream'
        part = {
            "inline_data": {
                "mime_type": mime_type,
                "data": file_data,
            }
        }
        parts.append(part)
        file.seek(0)  # Reset file pointer after reading

    if not parts:
        st.error("No files were uploaded successfully.")
        return None

    chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": parts,
            },
        ]
    )
    response = chat_session.send_message(
        "Create a description for what is in each of these photos in JSON format in the order uploaded. "
        "The JSON should be in this format: {\"image_1.jpg\": \"Description\", \"image_2.jpg\": \"Description\"}"
    )

    try:
        # Clean the response text to ensure it's valid JSON
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "")
        # Parse the JSON response
        descriptions_dict = json.loads(response_text)
        return descriptions_dict
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse JSON response: {e}")
        st.write("Raw response:", response.text)
        return None

def profile_page(st, photo_db):
    st.title("Profile")
    st.write("\n")
    st.subheader("Settings")
    st.write("Configure your information.")
    
    name_error = False
    age_error = False
    preferred_name_error = False

    name_input = st.text_input("Full Name", value=st.session_state.patient_name)
    st.session_state.patient_name = name_input
    
    if st.session_state.patient_name == '':
        name_error = True
    
    preferred_name_input = st.text_input("Preferred Name", value=st.session_state.patient_first_name)
    if preferred_name_input != '':
        st.session_state.patient_first_name = preferred_name_input
        print("K" + st.session_state.patient_first_name + "J")
    else:
        preferred_name_error = True
    
    age_input = st.text_input("Age", value=st.session_state.patient_age)
    
    try:
        st.session_state.patient_age = int(age_input)
    except ValueError:
        if age_input:
            st.error("Please enter a valid age.")
        age_error = True
    
    st.button("Save Profile", on_click=save_profile_button(name_error, age_error, preferred_name_error))
    
    st.session_state.profile_viewed_once = True

    # TODO: persist data

    st.write("\n")
    st.subheader("Upload Photos")
    st.write("Upload to your photo library.")
    uploaded_files = st.file_uploader("", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])
    
    image_hrefs = []
    if uploaded_files:
        st.session_state.photos_uploaded = True

        descriptions = generate_descriptions(uploaded_files)

        if not descriptions or len(descriptions) < len(uploaded_files):
            st.error("Failed to generate descriptions or mismatch in file count.")
            return


        embedding_dict = {}

        for idx, file in enumerate(uploaded_files):
            filename = os.path.basename(file.name) 
            description_key = f"image_{idx + 1}.jpg"

            file_description = descriptions.get(description_key, "No description available for this image")

            photo_id = str(uuid.uuid4())

            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(file.read())
                temp_file_path = temp_file.name

            blob = storage.bucket().blob(f"photos/{photo_id}_{filename}")
            blob.upload_from_filename(temp_file_path)
            blob.make_public()
            image_url = blob.public_url
            image_hrefs.append(image_url)

            os.remove(temp_file_path)

            photo_entry = {
                'image_url': image_url,
                'description': file_description,
            }
            test_photos_ref = db.reference("test_photos")
            test_photos_ref.child(photo_id).set(photo_entry)

        st.success("Photos and descriptions uploaded successfully!")

    display_photos_page(list(set(image_hrefs + [v for v in fetch_images_and_descriptions().values()])))


def display_photos_page(hrefs):
    st.subheader("Stored Photos")
    images_per_row = 4
    
    for i in range(0, len(hrefs), images_per_row):
        cols = st.columns(images_per_row)
        for j in range(images_per_row):
            if i + j < len(hrefs): 
                cols[j].image(hrefs[i + j], use_column_width='auto', width=100)


def save_profile_button(name_error, age_error, preferred_name_error):
    if st.session_state.profile_viewed_once:
        if name_error and preferred_name_error and age_error:
            st.error("Please enter your name and age.")
        elif name_error and preferred_name_error:
            st.error("Please enter your full and preferrd names.")
        elif name_error and age_error:
            st.error("Please enter your full name and age.")
        elif preferred_name_error and age_error:
            st.error("Please enter your age and preferred name.")
        elif age_error:
            st.error("Please enter your age.")
        elif preferred_name_error:
            st.error("Please enter your preferred name.")
        elif name_error:
            st.error("Please enter your full name.")
        else:
            st.success("Profile saved!")
