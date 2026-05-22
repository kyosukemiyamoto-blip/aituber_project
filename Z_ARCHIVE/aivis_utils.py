import requests
import winsound

AIVIS_URL = "http://127.0.0.1:10101"
SPEAKER_ID = 888753760


def speak(text: str):
    query_response = requests.post(
        f"{AIVIS_URL}/audio_query",
        params={
            "text": text,
            "speaker": SPEAKER_ID
        },
        timeout=30
    )
    query_response.raise_for_status()
    audio_query = query_response.json()

    synthesis_response = requests.post(
        f"{AIVIS_URL}/synthesis",
        params={
            "speaker": SPEAKER_ID
        },
        json=audio_query,
        timeout=60
    )
    synthesis_response.raise_for_status()

    winsound.PlaySound(
        synthesis_response.content,
        winsound.SND_MEMORY
    )