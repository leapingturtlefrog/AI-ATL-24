import os
import streamlit as st
from components.utils import ai_generate_prompt, ai_process_response, log_session

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

img_href = "https://images.unsplash.com/photo-1729366791970-3f56163c901a?q=80&w=1925&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"


html_content = f"""
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



def start_session_page(st, session_logs):
    current_dir = os.path.dirname(__file__)
    html_file_path = os.path.join(current_dir, "session.html")
    

    # with open(html_file_path, "r") as f:
        # html_content = f.read()


    st.components.v1.html(html_content, height=600, scrolling=True)

    # st.image(img_href, caption="")
