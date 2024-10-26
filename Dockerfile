FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y \
    libasound-dev \
    build-essential \
    python3-pyaudio \
    python3-dev \
    portaudio19-dev \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app
COPY requirements_large.txt .
RUN pip install --no-cache-dir -r requirements_large.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir uploaded_audio
COPY . .

EXPOSE 8501 8502

CMD streamlit run app.py --server.address=0.0.0.0 & uvicorn backend:app --host 0.0.0.0 --port 8502 --reload

