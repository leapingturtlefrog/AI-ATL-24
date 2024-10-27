import os
import streamlit as st
import random
from firebase_admin import db
from google.cloud import texttospeech
import google.generativeai as genai
import mimetypes
import pathlib
import tempfile
import ffmpeg
import uuid
import time
import firebase_admin
from firebase_admin import db, credentials, storage

if not firebase_admin._apps:
    cred = credentials.Certificate("./components/config/creds.json")
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://ai-atl-new-default-rtdb.firebaseio.com/",
        "storageBucket": "ai-atl-new.appspot.com"
    })
    db_ref = db.reference("/")
    bucket = storage.bucket()

conversation_history = [
        {
            'text': "You are a caring and therapeutic caretake for alzheimers patients meant to help them remember context of their memories through images they show you."
        }
]
model = 'gemini-1.5-flash'
generation_config = {
    'temperature': 0.7,
    'top_p': 0.95,
    'top_k': 40,
    'max_output_tokens': 256
}
current_dir = os.path.dirname(__file__)
key_path = os.path.join(current_dir, "config/google_genai_credentials.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path
tts_client = texttospeech.TextToSpeechClient()

def convert_to_mp3(input_file, output_file):
    (
        ffmpeg
        .input(input_file)
        .output(output_file, format='mp3')
        .run()
    )
    print(f"Conversion complete {output_file}")

def fetch_images_and_descriptions():
    ref = db.reference("test_photos")
    data = ref.get()
    image_dict = {entry["description"]: entry["image_url"] for entry in data.values()}
    return image_dict

def select_random_description(image_dict):
    selected_description = random.choice(list(image_dict.keys()))
    selected_image = image_dict[selected_description]
    context_descriptions = [desc for desc in image_dict if desc != selected_description]
    return selected_description, selected_image, context_descriptions

def call_gemini(photo_description):
    initial_prompt = (
        "You are a caring caretaker for this alzheimers patient. Based on the following photo description, generate a caring and playful hint "
    "as if discussing the photo with a friend that is brief but helps the patient remember their experience in the photo. Except it has to be about the specific picture. Be comforting and be therapist-esc.\n\n"
    f"{photo_description}"
    )
    
    gais_contents = [{
        'parts': [
            {'text': initial_prompt}
        ]
    }]
    gemini = genai.GenerativeModel(model_name=model)
    response_description = gemini.generate_content (
        gais_contents,
        generation_config=generation_config,
        stream=False,
    )
    ai_description = response_description.text.strip()
    # speech part
    synthesis_input = texttospeech.SynthesisInput(text=ai_description)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
    response_tts = tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

    # Save the audio to a file and play it
    audio_file = 'initial_description.mp3'
    with open(audio_file, 'wb') as out:
        out.write(response_tts.audio_content)
    # Get the full path to the audio file
    audio_file_path = os.path.abspath(audio_file)
    # Play the audio file in Streamlit
    with open(audio_file_path, 'rb') as audio_file:
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format='audio/mp3', start_time=0, autoplay=True)
    conversation_history.append({'text': f"Chatbot: {ai_description}\n"})
    return ai_description

def transcribe_audio(uploaded_file):
    if not uploaded_file:
        print("no file in transcribe method")
        return 'exit'
    
    file_name = uploaded_file["name"]
    file_data = uploaded_file["data"]
    print("got file name and data")
    # Determine MIME type
    mime_type = mimetypes.guess_type(file_name)[0] or 'audio/webm'

    # This writes the actual binary content (file_data) to the temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_name)[1]) as temp_file:
        temp_file.write(file_data)
        temp_file_path = temp_file.name
    
    # Prepare gais_contents with the temp file path
    gais_contents = [{
        'parts': [
            {'text': 'Transcribe the following audio file into text.'},
            {'file_data': {
                'mime_type': mime_type,
                'filename': temp_file_path,
                'display_name': file_name
            }},
            {'text': 'Transcription: '}
        ]
    }]
    
    def upload_file_data(file_data):
        print("inside upload file data")
        mime_type = file_data["mime_type"]
        if 'drive_id' in file_data:
            file_data.pop('drive_id')
        elif 'url' in file_data:
            file_data.pop('url')
        elif 'filename' in file_data:
            name = file_data.pop("filename")
            path = pathlib.Path(name)
            if not path.exists():
                raise IOError(f"Local file `{name}` does not exist. Please upload a file.")
            print(f"Uploading: {str(path)}")
            display_name = file_data.pop('display_name', name)
            file_info = genai.upload_file(path=path, display_name=display_name, mime_type=mime_type)
            print(f"uploaded file uri: {file_info.uri}")
            file_data["file_uri"] = file_info.uri
        elif "inline_data" in file_data:
            return
        else:
            raise ValueError("File data must include `drive_id`, `url`, `filename`, or `inline_data`.")

    # Upload the file to the API
    for content in gais_contents:
        for part in content["parts"]:
            if 'file_data' in part:
                upload_file_data(part['file_data'])
                print("uploaded file data")

    # Generate the transcription
    gemini_transcribe = genai.GenerativeModel(model_name=model)
    response = gemini_transcribe.generate_content(
        gais_contents,
        generation_config={
            'temperature': 0.1,
            'top_p': 0.95,
            'top_k': 40,
            'max_output_tokens': 1024
        },
        safety_settings={},
        stream=False,
    )

    # Extract the transcription
    if response.candidates:
        transcription = response.candidates[0].content.parts[-1].text.strip()
        print(transcription)
        os.remove(temp_file_path)
        return transcription
    else:
        print("no file in transcribe method")
        os.remove(temp_file_path)
        return ''

def render_html():
    html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="ISO-8859-1">
                <title>Session</title>
                <style>
                    /* Reset body margins to prevent pushing other content */
                    body {{
                        margin: 0;
                        padding: 0;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        flex-direction: column;
                    }}

                    /* Button styling */
                    .btn {{
                        background-color: #a7d8ff;   /* Primary color */
                        border: none;
                        border-radius: 4px;
                        color: #1a3c6e;             /* Accent color for text */
                        cursor: pointer;
                        font-size: 16px;
                        padding: 10px 20px;
                        transition: background-color 0.3s ease, color 0.3s ease;
                        display: inline-block;       /* Inline block to prevent stacking */
                        margin: 5px;                 /* Small spacing between buttons */
                    }}

                    .btn:hover {{
                        background-color: #4da3ff;   /* Darker shade on hover */
                        color: #ffffff;             /* White text on hover */
                    }}
                </style>
                <script type="text/javascript">
                    var webaudio_tooling_obj = function () {{
                        var audioContext = new AudioContext();
                        console.log("Audio is starting up ...");

                        var microphone_stream = null, mediaRecorder = null;
                        var audioChunks = [];

                        if (!navigator.mediaDevices.getUserMedia) {{
                            alert('getUserMedia not supported in this browser.');
                            return;
                        }}

                        navigator.mediaDevices.getUserMedia({{audio: true}})
                            .then(function(stream) {{
                                start_microphone(stream);
                            }})
                            .catch(function(e) {{
                                alert('Error capturing audio.');
                            }});

                        function start_microphone(stream) {{
                            microphone_stream = audioContext.createMediaStreamSource(stream);
                            mediaRecorder = new MediaRecorder(stream);

                            mediaRecorder.ondataavailable = function(event) {{
                                audioChunks.push(event.data);
                            }};

                            mediaRecorder.onstop = function() {{
                                var blob = new Blob(audioChunks, {{ type: 'audio/webm' }});
                                sendAudioToServer(blob);
                                audioChunks = []; // Clear the chunks for the next recording
                            }};

                            document.getElementById("startBtn").onclick = function() {{
                                audioChunks = []; // Clear previous audio chunks
                                mediaRecorder.start();
                                console.log("Recording started...");
                            }};

                            document.getElementById("stopBtn").onclick = function() {{
                                mediaRecorder.stop();
                                console.log("Recording stopped...");
                            }};
                        }}
                        
                        function sendAudioToServer(blob) {{
                            var formData = new FormData();
                            formData.append('audio', blob, 'audio_chunk_' + Date.now() + '.webm');

                            fetch('http://127.0.0.1:8502/upload-audio', {{
                                method: 'POST',
                                body: formData
                            }})
                            .then(response => response.json())
                            .then(data => {{
                                console.log('Audio sent successfully:', data);
                            }})
                            .catch(error => {{
                                console.error('Error sending audio:', error);
                            }});
                        }}
                    }}();
                </script>
            </head>
            <body>
                <div id="controls">
                    <button id="startBtn" class="btn">Start Recording</button>
                    <button id="stopBtn" class="btn">Stop Recording</button>
                </div>
            </body>
            </html>
            """
    return html

current_dir = os.path.dirname(__file__)
audio_folder = "uploaded_audio"
audio_directory_path = os.path.join(current_dir, "..", audio_folder)
image_set = fetch_images_and_descriptions()
visited = []
# initial render every time next image is called 

def init_render(random_description, selected_image):
    # return text   
    st.image(selected_image)
    text_response = call_gemini(random_description)
    html = render_html()
    st.components.v1.html(html, height=600, scrolling=True)
    hint_title = text_response


def read_mp3(path):
    with open(path, 'rb') as mp3_f:
        mp3_data = mp3_f.read()
    return mp3_data

def start_session_page(st):
    start_time = time.time()
    images_count, responses = 1, 1
    gemini_chatbot = genai.GenerativeModel(model_name=model)
    unique_key = str(uuid.uuid4())
    next_image = st.button("Next Image!", key=unique_key)
    random_description, selected_image, context_descriptions = select_random_description(image_set)
    visited.append(random_description)
    init_render(random_description, selected_image)
    while True:
        audio_files = [f for f in os.listdir(audio_directory_path) if 'webm' in f]
        if len(audio_files) == 1:
            print(True)
        if next_image:
            images_count += 1
            while True:
                random_description, selected_image = select_random_description(image_set)
                if random_description not in visited:
                    visited.append(random_description)
                    break
            init_render(random_description, selected_image)
        if len(audio_files) == 1:
            responses += 1
            # Process the new audio file(s)
            audio_file = audio_files[0]
            audio_file_path = os.path.join(audio_directory_path, audio_file)
            with open(audio_file_path, 'rb') as f:
                file_data = f.read()
            # Determine the file name and pass it to the transcribe_audio function
            file_name = os.path.basename(audio_file)
            input_file = {"name": file_name, "data": file_data}
            convert_to_mp3(audio_file_path, 'output_file.mp3')
            # Update the mp3_file_path and read it
            mp3_file_path = os.path.abspath('output_file.mp3')
            mp3_data = read_mp3(mp3_file_path)
            uploaded_file = {"name": 'output_file.mp3', "data": mp3_data}
            user_input = transcribe_audio(uploaded_file=uploaded_file)
            print(user_input)
            conversation_history.append({'text': f"User: {user_input}\n"})
            gais_contents = [{
                'parts': conversation_history + [{'text': "Chatbot: "}]
            }]
            response_chatbot = gemini_chatbot.generate_content(
                gais_contents,
                generation_config=generation_config,
                stream=False
            )
            chatbot_response = response_chatbot.text.strip()
            chatbot_response = chatbot_response.split("\n")[0]
            conversation_history.append({'text': f"{chatbot_response}\n"})
            print(chatbot_response)
            print(conversation_history)
            st.session_state.conversation_history = conversation_history
            end_time = time.time()
            total_time_seconds = end_time - start_time
            print("MINUTES", total_time_seconds)
            total_time_minutes = total_time_seconds / 60.0
            print("MINUTES", total_time_minutes)
            st.session_state.metrics = {
                "total_time_minutes": total_time_minutes,
                "images_count": images_count,
                "responses": responses
            }
            synthesis_input = texttospeech.SynthesisInput(text=chatbot_response)
            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US",
                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
            )
            audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
            response_tts = tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
            response_audio = 'output.mp3'
            with open(response_audio, 'wb') as out:
                out.write(response_tts.audio_content)
            response_file_path = os.path.abspath(response_audio)

            with open(response_file_path, 'rb') as response_audio_file:
                audio_bytes = response_audio_file.read()
            st.audio(audio_bytes, format='audio/mp3', start_time=0, autoplay=True)
            os.remove(audio_file_path)
            os.remove(response_file_path)
            os.remove(mp3_file_path)
            audio_files = []
            time.sleep(0.5)
