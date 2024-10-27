import os
import random
import pandas as pd
from components.start_session import start_session_page
import google.generativeai as genai  # Import Gemini API
import google.auth  
import google.auth.transport.requests  

model = 'gemini-1.5-flash'
generation_config = {
    'temperature': 0.7,
    'top_p': 0.95,
    'top_k': 40,
    'max_output_tokens': 256
}

def home_page(st, metrics):
    # Add custom CSS for larger font, padding, and text alignment
    st.markdown(
        """
        <style>
        .welcome-title {
            font-size: 2.8em;
            margin-bottom: 1.5em;
            text-align: center;  /* Center the welcome title */
        }
        .focus-text {
            font-size: 1.25em;
            line-height: 1.6;
            max-width: 480px; /* Restrict text width for balance */
            margin-left: auto; /* Center text */
            margin-right: auto;
            padding: 0.5em; /* Add padding for breathing room */
        }
        .stChart {
            margin-top: 1em; /* Space out the graph from title */
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Display welcome title with larger font
    st.markdown(f"<div class='welcome-title'>Welcome Back, {st.session_state.patient_first_name}!</div>", unsafe_allow_html=True)

    # Initialize conversation_history as an empty list
    conversation_history = []

    # Check if 'conversation_history.txt' exists
    if os.path.exists('conversation_history.txt'):
        # Read the conversation history
        with open('conversation_history.txt', 'r') as f:
            conversation_history = f.readlines()
        
        # Convert the list of lines to a single string for prompt creation
        conversation_text = ''.join(conversation_history)
        
        # Create the prompt for Gemini
        prompt = f"Start off with a small greeting and how you are excited to begin today, then, in a couple bullet points with no description, give some positive things to work on today using this conversation history:\n{conversation_text}"
        
        # Initialize Gemini model
        gemini_model = genai.GenerativeModel(model_name=model)
        
        # Generate suggestions using Gemini
        response = gemini_model.generate_content(
            [{'text': prompt}],
            generation_config=generation_config,
            stream=False
        )
        
        # Extract the generated text
        output_text = response.text.strip()
    else:
        # If the conversation history file doesn't exist
        output_text = "I don't believe we've had a chance to get to know each other!\nStart a new session to start!"

    # Existing metrics code
    metrics_df = pd.DataFrame.from_dict(metrics, orient="index", columns=["Time Spent", "Pictures Seen", "Responses"])

    metrics_df.reset_index(inplace=True)
    metrics_df.rename(columns={"index": "Session"}, inplace=True)

    metrics_df['Session'] = metrics_df['Session'].astype(int)
    metrics_df['Session'] = "Session " + metrics_df['Session'].astype(str)

    metrics_df['Session Number'] = metrics_df['Session'].str.extract('(\d+)').astype(int)
    metrics_df.sort_values('Session Number', inplace=True)

    metrics_df.set_index("Session", inplace=True)
    metrics_df.drop(columns='Session Number', inplace=True)

    # Adjust the column widths for feng shui balance
    col1, col2 = st.columns([2.4, 1.5])  # Slightly wider graph column for balance

    with col1:
        st.subheader("Session Trends")
        st.line_chart(metrics_df)

    with col2:
        st.subheader("Today's Focus")
        st.markdown(
            f"<div class='focus-text'>{output_text}</div>",
            unsafe_allow_html=True
        )
