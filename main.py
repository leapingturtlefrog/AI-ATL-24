import streamlit as st
import threading
from streamlit_autorefresh import st_autorefresh

from microphone_stream import MicrophoneStream, RATE, CHUNK
from speech_recognition import start_recognition

class TranscriptionManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.transcription = "Listening..."

    def update_transcription(self, text):
        with self.lock:
            self.transcription = text
            print(f"Updated transcription: {text}")  # Debugging

    def get_transcription(self):
        with self.lock:
            return self.transcription

@st.cache_resource
def get_transcription_manager():
    return TranscriptionManager()

def listen_and_update(manager: TranscriptionManager):
    """
    Background thread function to listen to microphone input and update transcription.
    """
    def listen_print_loop(responses):
        try:
            for response in responses:
                if not response.results:
                    continue
                result = response.results[0]
                if not result.alternatives:
                    continue
                transcript = result.alternatives[0].transcript
                if result.is_final:
                    manager.update_transcription(f"Final transcript: {transcript}")
                else:
                    manager.update_transcription(f"Interim transcript: {transcript}")
        except Exception as e:
            manager.update_transcription(f"Error in listen_print_loop: {e}")
            print(f"Error in listen_print_loop: {e}")

    try:
        with MicrophoneStream(RATE, CHUNK) as stream:
            audio_generator = stream.generator()
            start_recognition(audio_generator, listen_print_loop)
    except Exception as e:
        manager.update_transcription(f"Error in listen_and_update: {e}")
        print(f"Error in listen_and_update: {e}")

def main():
    st.title("Real-Time Speech Transcription")

    # Initialize the transcription manager
    manager = get_transcription_manager()

    # Start the background thread once
    if 'thread_started' not in st.session_state:
        st.session_state['thread_started'] = True
        thread = threading.Thread(target=listen_and_update, args=(manager,), daemon=True)
        thread.start()
        print("Started background thread for transcription.")

    # Auto-refresh the Streamlit app every 5 seconds (5000 milliseconds)
    st_autorefresh(interval=5000, limit=None, key="transcription_counter")

    # Get the latest transcription
    current_transcription = manager.get_transcription()

    # Display the transcription
    st.subheader("Transcription:")
    st.write(current_transcription)

if __name__ == "__main__":
    main()