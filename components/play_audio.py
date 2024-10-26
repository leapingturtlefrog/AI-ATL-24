import streamlit as st
import os

def play_audio_page(st):
    st.subheader("Play Audio")
    
    audio_folder = "uploaded_audio"
    current_dir = os.path.dirname(__file__)
    audio_directory_path = os.path.join(current_dir, "..", audio_folder)
    
    audio_files = [f for f in os.listdir(audio_directory_path) if f.endswith('.webm')]
    
    selected_audio = st.selectbox("Select an audio file to play: ", audio_files)
    
    if selected_audio:
        audio_file_path = os.path.join(audio_directory_path, selected_audio)
        
        st.audio(audio_file_path, format="audio/webm")
