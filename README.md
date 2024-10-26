# Project for AI ATL 2024 Hackathon
Run `./setup.sh`
<br>Run `source venv/bin/activate`
<br>Run `streamlit run app.py`
<br>
<br>ALSA errors are okay. If there is a pyaudio error, download the pyaudio dependencies such as
<br>`sudo apt-get install python3-pyaudio`
<br>`sudo apt-get install portaudio19-dev`
<br>There may be more
<br>
<br>That's the only solution I have for now unless you can get the Docker to connect with the system's audio.
<br>In `run.sh` I put a command in to maybe get closer to fixing it (it should connect audio) but I can't test it with WSL (explained in the file). Maybe try it on a Mac.
<br>
<br>~Alex