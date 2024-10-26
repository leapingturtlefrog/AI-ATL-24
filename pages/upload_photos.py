# upload_photos.py
import streamlit as st
import os
import google.generativeai as genai
import tempfile
import uuid

def upload_to_gemini(uploaded_file, mime_type=None):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_file_path = tmp_file.name

    try:
        genai_file = genai.upload_file(tmp_file_path, mime_type=mime_type)
        print(f"Uploaded file '{genai_file.display_name}' as: {genai_file.uri}")
    except Exception as e:
        print(f"Error uploading file: {e}")
        genai_file = None

    os.remove(tmp_file_path)
    uploaded_file.seek(0)

    return genai_file

def generate_descriptions(uploaded_files):
    generation_config = {
        "temperature": 1,
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
    for file in uploaded_files:
        file.seek(0)  
        file_data = file.read()
        mime_type = file.type or 'application/octet-stream'

        # Construct the part with inline_data
        part = {
            "inline_data": {
                "mime_type": mime_type,
                "data": file_data,
            }
        }
        parts.append(part)

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
    response = chat_session.send_message("Create a description for what is in each of these photos in JSON format in the order uploaded. There should be one description for each image and each description should have its own key in the json labeled image_[image_number].")
    return response.text


def upload_photos_page(st, photo_db):
    st.subheader("Upload Photos")
    st.write("Upload the patient's photo library.")
    uploaded_files = st.file_uploader("Choose images", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])

    if uploaded_files:
        st.session_state.photos_uploaded = True
        st.write("Analyzing photos...")

        GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")
        if not GEMINI_API_KEY:
            st.error("API key not found. Please add your GEMINI_API_KEY to Streamlit secrets.")
            return

        genai.configure(api_key=GEMINI_API_KEY)

        descriptions = generate_descriptions(uploaded_files)
        if descriptions:
            st.success("Photos analyzed successfully!")
            st.write(descriptions)
            for i, file in enumerate(uploaded_files):
                photo_entry = {
                    'photo_id': str(uuid.uuid4()),
                    'image': file,
                    'description': descriptions,  
                }
                user_photos = photo_db.get(st.session_state.user_email, [])
                user_photos.append(photo_entry)
                photo_db[st.session_state.user_email] = user_photos
        else:
            st.error("Failed to generate descriptions.")
    else:
        st.write("No photos uploaded yet.")
