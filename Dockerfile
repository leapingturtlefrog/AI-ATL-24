FROM python:3.10-slim
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    portaudio19-dev \
    && apt-get install -y ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app
COPY requirements_large.txt .
RUN pip install --no-cache-dir -r requirements_large.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
ENTRYPOINT ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
