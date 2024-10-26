Here’s a README.md file that documents how to set up and run the real-time speech transcription application with Google Cloud Speech-to-Text, including steps to register for Google Cloud and configure the API.

Real-Time Speech Transcription with Google Cloud Speech-to-Text

This application uses Google Cloud Speech-to-Text for real-time audio transcription. It captures audio from your microphone, processes it with Google Cloud Speech-to-Text, and displays the transcriptions in a web interface built with Streamlit.

Features

	•	Real-time audio transcription: The app continuously listens to your microphone and transcribes speech in real time.
	•	Streamlit-based UI: Displays the transcription with auto-refresh every 5 seconds.
	•	Google Cloud Speech-to-Text integration: Uses Google Cloud’s Speech-to-Text API for highly accurate and real-time transcription.

Prerequisites

	•	Python 3.7+: Ensure Python is installed on your system.
	•	Google Cloud Account: You will need a Google Cloud account to access the Speech-to-Text API.

Installation

	1.	Clone the repository and navigate to the project folder:

git clone <repository_url>
cd <repository_folder>


	2.	Install dependencies:

pip install -r requirements.txt

	Note: The pyaudio library may require additional setup. See PyAudio installation instructions if you encounter issues.

	3.	Register for Google Cloud and Set Up Speech-to-Text API:
Follow the steps below to set up your Google Cloud project and enable the Speech-to-Text API.

Google Cloud Setup

	1.	Create a Google Cloud Account:
	•	Visit the Google Cloud Console and sign in or create a new account.
	•	Google Cloud offers a free tier with credits for new users, allowing you to use services like Speech-to-Text without immediate charges.
	2.	Create a New Project:
	•	In the Google Cloud Console, navigate to Project settings and create a new project.
	•	Name your project (e.g., “SpeechTranscriptionApp”) and note down the Project ID for future use.
	3.	Enable Speech-to-Text API:
	•	Go to the Speech-to-Text API page in the Cloud Console.
	•	Click Enable to activate the Speech-to-Text API for your project.
	4.	Create a Service Account:
	•	In the Cloud Console, go to IAM & Admin > Service Accounts.
	•	Click Create Service Account, name the account (e.g., speech-transcription), and assign it the role Speech-to-Text API User.
	5.	Generate a Service Account Key:
	•	After creating the service account, click on it and go to Keys.
	•	Click Add Key > Create New Key, select JSON format, and save the key file to a secure location on your machine.
	6.	Set the GOOGLE_APPLICATION_CREDENTIALS Environment Variable:
	•	To allow your app to access Google Cloud, set an environment variable pointing to the service account key file you just downloaded.
Linux / macOS:

export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-file.json"

Windows:

set GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\your\service-account-file.json"



Run the Application

	1.	Start the Streamlit App:
From the terminal, navigate to the project folder and run:

streamlit run main.py


	2.	Allow Microphone Access:
	•	Ensure your microphone is available and accessible by the app. This app will continuously listen to the microphone to process audio data.
	3.	View Real-Time Transcriptions:
	•	Open the app in your web browser (default URL: http://localhost:8501).
	•	The transcription will appear in the app interface and update every 5 seconds.

File Structure

	•	main.py: The main Streamlit application script. Handles UI and background transcription thread.
	•	microphone_stream.py: Handles audio streaming from the microphone using pyaudio.
	•	speech_recognition.py: Contains the function to connect with Google Cloud Speech-to-Text and process transcriptions.
	•	requirements.txt: Lists all required Python packages.

Example Code Structure

main.py

import streamlit as st
import threading
from streamlit_autorefresh import st_autorefresh
from microphone_stream import MicrophoneStream, RATE, CHUNK
from speech_recognition import start_recognition

# Initialize and manage transcription updates
...

microphone_stream.py

import pyaudio
import queue

# Audio streaming class
...

speech_recognition.py

from google.cloud import speech

# Start recognition function
...

Troubleshooting

	•	No transcription text displayed:
	•	Ensure your microphone is accessible and not in use by another application.
	•	Verify that the GOOGLE_APPLICATION_CREDENTIALS environment variable is set correctly.
	•	Issues with pyaudio installation:
	•	pyaudio may require additional setup. See PyAudio’s official documentation for detailed installation instructions based on your operating system.
	•	Permission errors:
	•	Ensure your Google Cloud service account has the correct permissions (Speech-to-Text API User role).

License: its mine:)