import streamlit as st
from st_audiorec import st_audiorec

st.set_page_config(page_title="streamlit_audio_recorder")
st.markdown('''<style>.css-1egvi7u {margin-top: -3rem;}</style>''',
            unsafe_allow_html=True)
st.markdown('''<style>.stAudio {height: 45px;}</style>''',
            unsafe_allow_html=True)
st.markdown('''<style>.css-v37k9u a {color: #0000ff;}</style>''',
            unsafe_allow_html=True) 


def audiorec_demo_app():

    st.title('streamlit audio recorder')

    wav_audio_data = st_audiorec()

    col_info, col_space = st.columns([0.57, 0.43])
    with col_info:
        st.write('\n') 
        st.write('\n')
        st.write('The .wav audio data, as received in the backend Python code,'
                 ' will be displayed below this message as soon as it has'
                 ' been processed. [This informative message is not part of'
                 ' the audio recorder and can be removed easily] 🎈')

    if wav_audio_data is not None:
        col_playback, col_space = st.columns([0.58,0.42])
        with col_playback:
            st.audio(wav_audio_data, format='audio/wav')


if __name__ == '__main__':
    audiorec_demo_app()
