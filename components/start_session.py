import os
import streamlit as st
from components.utils import ai_generate_prompt, ai_process_response, log_session
import random
from firebase_admin import db
from google.cloud import texttospeech
import google.generativeai as genai
import mimetypes
from IPython.display import display, Markdown, Audio
import pathlib
import tempfile
import ffmpeg
import uuid


"""
def start_session_page(st, session_logs):
    st.subheader("Start Reminiscence Session")
    if not st.session_state.analyzed_photos:
        st.error("Please upload and process photos before starting a session.")
        return

    st.write("Select a theme for the session or let the AI choose:")
    themes = ["Family", "Travel", "Friends", "Events", "Random"]
    selected_theme = st.selectbox("Choose a theme", themes)

    if st.button("Start Session"):
        st.session_state.session_history = []
        st.session_state.current_photo = None
        st.experimental_rerun()

    if st.session_state.session_history == []:
        # Start new session
        st.session_state.current_photo = st.session_state.analyzed_photos[0]
        st.session_state.session_history.append({
            'photo': st.session_state.current_photo,
            'ai_prompt': ai_generate_prompt(st.session_state.current_photo, st.session_state.session_history),
            'patient_response': '',
        })
    else:
        # Continue session
        current_interaction = st.session_state.session_history[-1]
        st.image(current_interaction['photo']['image'], use_column_width=True)
        st.write(f"AI Assistant: {current_interaction['ai_prompt']}")
        patient_response = st.text_input("Your Response", key=f"response_{len(st.session_state.session_history)}")
        if st.button("Submit Response"):
            current_interaction['patient_response'] = patient_response
            # AI processes response
            ai_reply = ai_process_response(patient_response, st.session_state.session_history)
            st.write(f"AI Assistant: {ai_reply}")
            # Move to next photo
            next_index = len(st.session_state.session_history)
            if next_index < len(st.session_state.analyzed_photos):
                st.session_state.current_photo = st.session_state.analyzed_photos[next_index]
                st.session_state.session_history.append({
                    'photo': st.session_state.current_photo,
                    'ai_prompt': ai_generate_prompt(st.session_state.current_photo, st.session_state.session_history),
                    'patient_response': '',
                })
            else:
                st.success("Session completed!")
                # Log session
                log_session(st, session_logs)
                if st.button("Return to Dashboard"):
                    st.experimental_rerun()

"""
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
        "You are a caring caretaker and doctor for this alzheimers patient. Based on the following photo description, generate a caring and playful hint "
    "as if discussing the photo with a friend that is brief but helps the patient remember their experience in the photo. Use phrases like 'Remember that photo?', "
    "'That's such a great,' or 'wonderful, (light question)?' Except it has to be about the specific picture. be comforting and be therapist-esc.\n\n"
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
        st.audio(audio_bytes, format='audio/mp3', start_time=0)
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

def start_session_page(st, session_logs):
    current_dir = os.path.dirname(__file__)
    audio_folder = "uploaded_audio"
    audio_directory_path = os.path.join(current_dir, "..", audio_folder)
    image_set = fetch_images_and_descriptions()
    random_description, selected_image, context_descriptions = select_random_description(image_set)
    # return text   
    text_response = call_gemini(random_description)
    # somehow show this as a response here

    audio_files = [True]
    while True:
        img_href = selected_image
        hint_title = text_response
        # st.success(text_response)
        if len(audio_files) > 0:
            print("found a file")
            print(len(audio_files))
            # Process the new audio file(s)
            for audio_file in audio_files:
                print(audio_files)
                if isinstance(audio_file, bool):
                    print("failure")
                    break
                # Here you can process the audio file if needed
                audio_folder = "uploaded_audio"
                current_dir = os.path.dirname(__file__)
                audio_directory_path = os.path.join(current_dir, "..", audio_folder)
                audio_file_path = os.path.join(audio_directory_path, audio_file)
                st.audio(audio_file_path, format="audio/webm")
                with open(audio_file_path, 'rb') as f:
                    file_data = f.read()
                    print(file_data)
                # Determine the file name and pass it to the transcribe_audio function
                file_name = os.path.basename(audio_file)
                print("file captured")
                input_file = {"name": file_name, "data": file_data}
                convert_to_mp3(audio_file_path, 'output_file.mp3')
                
                # Update the mp3_file_path and read it
                mp3_file_path = os.path.abspath('output_file.mp3')
                with open(mp3_file_path, 'rb') as mp3_f:
                    mp3_data = mp3_f.read()
                
                uploaded_file = {"name": 'output_file.mp3', "data": mp3_data}
                user_input = transcribe_audio(uploaded_file=uploaded_file)
                print(user_input)
                conversation_history.append({'text': f"User: {user_input}\n"})
                gais_contents = [{
                    'parts': conversation_history + [{'text': "Chatbot: "}]
                }]
                gemini_chatbot = genai.GenerativeModel(model_name=model)
                response_chatbot = gemini_chatbot.generate_content(
                    gais_contents,
                    generation_config=generation_config,
                    stream=False
                )
                chatbot_response = response_chatbot.text.strip()
                conversation_history.append({'text': f"Chatbot: {chatbot_response}\n"})
                # display response to question
                print(chatbot_response)
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

                # Get the full path to the audio file
                response_file_path = os.path.abspath(response_audio)

                # Play the audio file in Streamlit
                with open(response_file_path, 'rb') as response_audio_file:
                    audio_bytes = response_audio_file.read()
                    st.audio(audio_bytes, format='audio/mp3', start_time=0)

                # Clear the image reference
                img_href = ""

                # Remove the processed audio file
                os.remove(response_file_path)

            # Create the HTML content
            html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="ISO-8859-1">
                <title>Session</title>
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
                <input id="volume" type="range" min="0" max="1" step="0.1" value="0.5"/>
                <button id="startBtn">Start Recording</button>
                <button id="stopBtn">Stop Recording</button>
                <br><br>
                <img id="myImage" src="{img_href}" alt="image" />
            </body>
            </html>
            """
            if display_page(st, html):
                random_description = select_random_description(image_set)
                text_response = call_gemini(random_description)
        audio_files = [f for f in os.listdir(audio_directory_path)]
        

def display_page(st, html_content):
    unique_key = str(uuid.uuid4())
    next_image = st.button("Next Image!", key=unique_key)
    st.components.v1.html(html_content, height=600, scrolling=True)
    return next_image