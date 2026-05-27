import os
import io
import requests
import pygame


ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = "hMK7c1GPJmptCzI4bQIu"
ELEVENLABS_MODEL_ID = "eleven_multilingual_v2"


def speak(text: str):
    if not ELEVENLABS_API_KEY:
        print("エラー: 環境変数 'ELEVENLABS_API_KEY' が設定されていません。")
        return

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"

    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }

    data = {
        "text": text,
        "model_id": ELEVENLABS_MODEL_ID,
    }

    try:
        print(f"音声生成中: {text}")

        response = requests.post(url, headers=headers, json=data, timeout=30)

        if response.status_code != 200:
            print(f"音声合成エラー: {response.status_code}")
            print(response.text)
            return

        pygame.mixer.init()
        audio_stream = io.BytesIO(response.content)
        pygame.mixer.music.load(audio_stream)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    except Exception as e:
        print(f"音声合成エラー: {e}")