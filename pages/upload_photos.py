import streamlit as st
import os
import google.generativeai as genai
import tempfile
import uuid
import json
import pickle
from sentence_transformers import SentenceTransformer

# Load the embedding model
embed_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

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
        file_names.append(file.name)

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

    # Enhanced prompt to enforce JSON response within a code block
    prompt = (
        f"Create a description for each of these photos in strict JSON format. "
        f"Each key should be the file name, and each value should be a concise description. "
        f"Provide only the JSON without any additional text or explanations.\n\n"
        f"File names: {file_names}\n\n"
        f"JSON Output:\n```json\n{{\n"
    )

    # Sending the prompt to Gemini
    response = chat_session.send_message(prompt + "\n```\n")

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
            st.write("**Raw Descriptions Received:**")
            st.code(descriptions)  # Display raw descriptions for debugging

            # Attempt to extract JSON from the response
            try:
                # Find the JSON block within code fences
                json_start = descriptions.find("{")
                json_end = descriptions.rfind("}") + 1
                json_str = descriptions[json_start:json_end]

                # Optional: Remove any Unicode non-breaking space characters or other invisible chars
                json_str = json_str.replace('\u202f', ' ')

                # Parse the JSON string
                descriptions_dict = json.loads(json_str)
            except json.JSONDecodeError as e:
                st.error(f"Failed to parse descriptions: {e}")
                st.write("**Processed Description String:**")
                st.text(json_str)  # Display the processed string for debugging
                return

            # Initialize the embedding dictionary
            embedding_dict = {}

            for file in uploaded_files:
                file_name = file.name
                description = descriptions_dict.get(file_name)

                if description:
                    # Generate embedding
                    embedding = embed_model.encode(description)

                    # Display the embedding in Streamlit
                    st.write(f"Embedding for {file_name}: {embedding}")

                    # Add to embedding_dict
                    embedding_dict[file_name] = embedding.tolist()  # Convert numpy array to list for pickling

                    # Create photo entry
                    photo_entry = {
                        'photo_id': str(uuid.uuid4()),
                        'image': file,
                        'description': description,
                    }
                    user_photos = photo_db.get(st.session_state.user_email, [])
                    user_photos.append(photo_entry)
                    photo_db[st.session_state.user_email] = user_photos
                else:
                    st.error(f"No description found for file {file_name}")

            # Save the embedding dictionary to a file
            try:
                with open('embedding_image_dict.pkl', 'wb') as f:
                    pickle.dump(embedding_dict, f)
                st.write(f"Embeddings saved to 'embedding_image_dict.pkl'.")
            except Exception as e:
                st.error(f"Failed to save embeddings: {e}")
        else:
            st.error("Failed to generate descriptions.")
    else:
        st.write("No photos uploaded yet.")