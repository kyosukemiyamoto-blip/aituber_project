import requests
import winsound
import threading
import time
import wave
import numpy as np
import matplotlib.pyplot as plt

AIVIS_URL = "http://127.0.0.1:10101"
SPEAKER_ID = 888753760

# =========================================
# 設定
# =========================================

MORA_DURATION = 0.12
LIP_SYNC_OFFSET = 0.03

# =========================================
# 音声再生
# =========================================

def play_audio(audio_bytes):
    winsound.PlaySound(
        audio_bytes,
        winsound.SND_MEMORY
    )

# =========================================
# wav解析
# =========================================

def analyze_wav(wav_path, timeline=None):

    wav = wave.open(wav_path, "rb")

    n_frames = wav.getnframes()
    framerate = wav.getframerate()

    audio = wav.readframes(n_frames)

    signal = np.frombuffer(audio, dtype=np.int16)

    wav.close()

    # =========================================
    # 時間軸
    # =========================================

    time_axis = np.linspace(
        0,
        len(signal) / framerate,
        num=len(signal)
    )

    # =========================================
    # 波形
    # =========================================

    plt.figure(figsize=(15, 4))

    plt.plot(time_axis, signal)

    # timeline描画
    if timeline:
        for item in timeline:
            plt.axvline(
                x=item["time"],
                linestyle="--"
            )

    plt.title("Waveform")
    plt.xlabel("Time (sec)")
    plt.ylabel("Amplitude")

    plt.show()

    # =========================================
    # RMS解析
    # =========================================

    chunk_size = 1024

    rms_values = []
    rms_times = []

    for i in range(0, len(signal), chunk_size):

        chunk = signal[i:i + chunk_size]

        if len(chunk) == 0:
            continue

        rms = np.sqrt(
            np.mean(
                chunk.astype(np.float64) ** 2
            )
        )

        rms_values.append(rms)

        rms_times.append(i / framerate)

    # =========================================
    # RMSグラフ
    # =========================================

    plt.figure(figsize=(15, 4))

    plt.plot(rms_times, rms_values)

    if timeline:
        for item in timeline:
            plt.axvline(
                x=item["time"],
                linestyle="--"
            )

    plt.title("RMS Volume")
    plt.xlabel("Time (sec)")
    plt.ylabel("Volume")

    plt.show()

    # =========================================
    # 発話開始検出
    # =========================================

    THRESHOLD = 1000

    for t, rms in zip(rms_times, rms_values):

        if rms > THRESHOLD:
            print(f"\n[VOICE START] {t:.3f} sec")
            break

    # =========================================
    # Spectrogram
    # =========================================

    plt.figure(figsize=(15, 6))

    plt.specgram(signal, Fs=framerate)

    if timeline:
        for item in timeline:
            plt.axvline(
                x=item["time"],
                linestyle="--"
            )

    plt.title("Spectrogram")
    plt.xlabel("Time (sec)")
    plt.ylabel("Frequency")

    plt.show()

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

            print(
                f"[{elapsed:.3f}] "
                f"{item['text']} "
                f"-> "
                f"{item['vowel']}"
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
    # wav保存
    # =========================================

    wav_path = "output.wav"

    with open(wav_path, "wb") as f:
        f.write(synthesis_response.content)

    # =========================================
    # timeline生成
    # =========================================

    timeline = build_timeline(audio_query)

    print("\n===== TIMELINE =====")

    for item in timeline:
        print(item)

    # =========================================
    # 音声再生開始
    # =========================================

    audio_thread = threading.Thread(
        target=play_audio,
        args=(synthesis_response.content,)
    )

    start_time = time.perf_counter()

    audio_thread.start()

    # =========================================
    # リップシンク実行
    # =========================================

    run_lip_sync(
        timeline,
        start_time
    )

    audio_thread.join()

    # =========================================
    # wav解析
    # =========================================

    analyze_wav(
        wav_path,
        timeline
    )

# =========================================
# main
# =========================================

if __name__ == "__main__":

    speak(
        "非常に長い文章を生成してわぶファイルを分析することにより、確実に発話開始のタイミングを計れます"
    )