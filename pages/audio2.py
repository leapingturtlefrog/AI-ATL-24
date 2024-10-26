import streamlit as st
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import os
import tempfile

# Function to record audio
def record_audio(duration):
    fs = 44100  # Sample rate
    print("Recording...")
    audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()  # Wait until recording is finished
    print("Recording finished")
    return audio_data

# Streamlit app layout
st.title("Real-time Audio Recorder")

# Button to start recording
if st.button("Record Audio (5 seconds)"):
    audio_chunk = record_audio(5)  # Record for 5 seconds
    audio_chunk = audio_chunk.flatten()  # Flatten to 1D array

    # Create a temporary file to save the audio
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    wav.write(temp_file.name, 44100, audio_chunk)

    # Provide a download link for the audio file
    with open(temp_file.name, "rb") as f:
        st.download_button(
            label="Download Audio",
            data=f,
            file_name="recorded_audio.wav",
            mime="audio/wav"
        )

    # Optionally delete the file after download
    os.remove(temp_file.name)
    st.success("File has been downloaded and deleted.")
