# start_session.py

import streamlit as st
from pages.utils import ai_generate_prompt, ai_process_response, log_session

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
