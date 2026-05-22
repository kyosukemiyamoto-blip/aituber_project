import requests
import winsound
import threading
import time

AIVIS_URL = "http://127.0.0.1:10101"
SPEAKER_ID = 888753760

# =========================================
# 設定
# =========================================

MORA_DURATION = 0.12

# リップ同期の微調整
LIP_SYNC_OFFSET = 0.03

# 実際のオーディオ出力遅延
# 環境によって調整
AUDIO_DEVICE_DELAY = 0.08

# =========================================
# 音声再生
# =========================================

def play_audio(audio_bytes):

    winsound.PlaySound(
        audio_bytes,
        winsound.SND_MEMORY
    )

# =========================================
# 母音イベント
# =========================================

def on_vowel(vowel, text, elapsed):

    print(
        f"[{elapsed:.3f}] "
        f"{text} "
        f"-> "
        f"{vowel}"
    )

# =========================================
# timeline生成
# =========================================

def build_timeline(audio_query):

    timeline = []

    current_time = (
        audio_query["prePhonemeLength"]
        - LIP_SYNC_OFFSET
    )

    for phrase in audio_query["accent_phrases"]:

        for mora in phrase["moras"]:

            timeline.append({
                "text": mora["text"],
                "vowel": mora["vowel"],
                "time": max(0, current_time)
            })

            current_time += MORA_DURATION

    return timeline

# =========================================
# リップシンク
# =========================================

def run_lip_sync(timeline, start_time):

    index = 0

    while index < len(timeline):

        elapsed = (
            time.perf_counter()
            - start_time
        )

        target = timeline[index]["time"]

        if elapsed >= target:

            item = timeline[index]

            on_vowel(
                item["vowel"],
                item["text"],
                elapsed
            )

            index += 1

        time.sleep(0.001)

# =========================================
# speak
# =========================================

def speak(text: str):

    # =========================================
    # audio_query
    # =========================================

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

    # =========================================
    # synthesis
    # =========================================

    synthesis_response = requests.post(
        f"{AIVIS_URL}/synthesis",
        params={
            "speaker": SPEAKER_ID
        },
        json=audio_query,
        timeout=60
    )

    synthesis_response.raise_for_status()

    # =========================================
    # timeline生成
    # =========================================

    timeline = build_timeline(audio_query)

    print("\n===== TIMELINE =====")

    for item in timeline:
        print(item)

    # =========================================
    # 音声再生スレッド
    # =========================================

    audio_thread = threading.Thread(
        target=play_audio,
        args=(synthesis_response.content,)
    )

    # =========================================
    # 再生開始
    # =========================================

    audio_thread.start()

    # =========================================
    # 実際の音声出力に合わせる
    # =========================================

    start_time = (
        time.perf_counter()
        - AUDIO_DEVICE_DELAY
    )

    # =========================================
    # リップシンク開始
    # =========================================

    run_lip_sync(
        timeline,
        start_time
    )

    audio_thread.join()

# =========================================
# main
# =========================================

if __name__ == "__main__":

    speak(
        "私の名前は小池百合子です"
    )