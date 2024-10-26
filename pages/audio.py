import streamlit as st
from st_audiorec import st_audiorec

st.set_page_config(page_title="streamlit_audio_recorder")

def audiorec_demo_app():
    st.title("streamlit audio recorder")

    wav_audio_data = st_audiorec()

    col_info, col_space = st.columns([0.57, 0.43])
    with col_info:
        st.write("\n") 
        st.write("\n")
        st.write("The .wav audio data is below")

    if wav_audio_data is not None:
        col_playback, col_space = st.columns([0.58, 0.42])
        with col_playback:
            st.audio(wav_audio_data, format="audio/wav")


if __name__ == "__main__":
    audiorec_demo_app()
