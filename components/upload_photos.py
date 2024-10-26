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
from sentence_transformers import SentenceTransformer
# Load the embedding model
embed_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

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
        # Read the file and encode it
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
        "temperature": 0.2,  # Lower temperature for more deterministic output
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",  # Keeping as text/plain; we'll enforce JSON in the prompt
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

def upload_photos_page(st, photo_db):
    st.subheader("Upload Photos")
    st.write("Upload the patient's photo library.")
    uploaded_files = st.file_uploader("Choose images", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])

    if uploaded_files:
        st.session_state.photos_uploaded = True
        st.write("Generating descriptions for photos...")

        # Generate descriptions before uploading to Firebase
        descriptions = generate_descriptions(uploaded_files)
        # Debugging: Output the descriptions to verify correct structure
        st.write("Descriptions dictionary:", descriptions)
        
        if not descriptions or len(descriptions) < len(uploaded_files):
            st.error("Failed to generate descriptions or mismatch in file count.")
            return
        

        st.write("Descriptions generated. Uploading files...")
        embedding_dict = {}

        for idx, file in enumerate(uploaded_files):
            filename = os.path.basename(file.name)  # Define filename at the start of the loop
            description_key = f"image_{idx + 1}.jpg"  # Adjusted to match the "image_x.jpg" key format
            st.write(f"Processing file {filename} with description key: {description_key}")

            file_description = descriptions.get(description_key, "No description available for this image")

            # Embedding part
            embedding_file_name = file.name
            embedding = embed_model.encode(file_description)
            st.write(f"Embedding for {filename}: {embedding}")
            embedding_dict[filename] = embedding.tolist()

            st.write(f"Description for {description_key}: {file_description}")

            # Generate a unique filename for Firebase Storage
            photo_id = str(uuid.uuid4())
            st.write(f"Uploading file: {filename} as {photo_id}_{filename}")

            # Save the file temporarily and upload to Firebase Storage
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(file.read())
                temp_file_path = temp_file.name

            # Upload the file to Firebase Storage
            blob = storage.bucket().blob(f"photos/{photo_id}_{filename}")
            blob.upload_from_filename(temp_file_path)
            blob.make_public()
            image_url = blob.public_url
            st.write(f"File uploaded to: {image_url}")

            # Delete the temporary file
            os.remove(temp_file_path)

            # Store image URL and description in Realtime Database
            photo_entry = {
                'image_url': image_url,
                'description': file_description, # Add embedding value somehow (numpy array)
            }
            test_photos_ref = db.reference("test_photos")
            test_photos_ref.child(photo_id).set(photo_entry)
            st.write(f"Photo entry saved with ID {photo_id}")

        st.success("Photos and descriptions uploaded successfully!")
        
    else:
        st.write("No photos uploaded yet.")





def retrieve_photos():
    """Retrieve photos and descriptions from the database"""
    try:
        test_photos_ref = db.reference("test_photos")
        photos = test_photos_ref.get()
        
        if not photos:
            return {}
        
        result = {}
        for photo_id, photo_data in photos.items():
            # Create a dictionary with both image data and description
            result[photo_data['file_name']] = {
                'description': photo_data['description'],
                'image_data': photo_data['image_data'],
                'timestamp': photo_data.get('timestamp', 0)
            }
        
        return result
    except Exception as e:
        st.error(f"Error retrieving photos: {e}")
        return {}

# Example of how to display a retrieved image
def display_retrieved_photo(image_data, description):
    try:
        # Decode the base64 image
        decoded_image = decode_image(image_data)
        if decoded_image:
            # Create a BytesIO object from the decoded image data
            image_bytesio = BytesIO(decoded_image)
            # Display the image using Streamlit
            st.image(image_bytesio)
            st.write(f"Description: {description}")
    except Exception as e:
        st.error(f"Error displaying image: {e}")

# Example usage of retrieval and display
def display_photos_page():
    st.subheader("Stored Photos")
    
    # Retrieve all photos
    photos = retrieve_photos()
    
    if not photos:
        st.write("No photos found in the database.")
        return
    
    # Display each photo with its description
    for filename, data in photos.items():
        st.write(f"File: {filename}")
        display_retrieved_photo(data['image_data'], data['description'])
        st.write("---")  # Separator between photos
