from google.cloud import speech

# Audio recording parameters
RATE = 16000

def start_recognition(audio_generator, callback):
    client = speech.SpeechClient()

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code="en-US",
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config, interim_results=True
    )

    requests = (speech.StreamingRecognizeRequest(audio_content=content)
                for content in audio_generator)

    try:
        responses = client.streaming_recognize(streaming_config, requests)
        callback(responses)
    except Exception as e:
        print(f"Error during recognition: {e}")