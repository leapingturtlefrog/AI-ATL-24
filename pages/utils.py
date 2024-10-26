# utils.py
import uuid
import datetime

def ai_generate_prompt(photo_data, session_history):
    # Simulate AI-generated prompt
    return "Look at this photo! Do you remember when this was taken?"

def ai_process_response(response, session_history):
    # Simulate AI processing of patient response
    return "That's wonderful! Tell me more about it."

# Function to log sessions
def log_session(st, session_logs):
    duration = len(st.session_state.session_history) * 2  # Assume each interaction takes ~2 minutes
    session_log = {
        'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'duration': duration,
        'interactions': st.session_state.session_history,
    }
    logs = session_logs.get(st.session_state.user_email, [])
    logs.append(session_log)
    session_logs[st.session_state.user_email] = logs
