import os
import io
import requests
import pygame
import json
import base64
import time
import sys

# --------------------------------------------------
# 【設定】ご自身の情報に書き換えてください
# --------------------------------------------------
ELEVENLABS_API_KEY = os.environ.get("ELEVENLAB_API_KEY") # または直接文字列を入れる
VOICE_ID = "EXAVITQu4vr4xnSDxMaL"  # 使用したいボイスID

def speak(text: str):
    """
    ElevenLabsの音声とリップシンクデータを取得し、
    発音のタイミングと完全に同期してターミナルに文字を出力する関数
    """
    if not ELEVENLABS_API_KEY:
        print("エラー: APIキーが設定されていません。")
        return

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/with-timestamps"
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    
    data = {
        "text": text,
        "model_id": "eleven_turbo_v2_5", 
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True
        }
    }

    print(f"音声生成中（メモリダイレクト再生）: {text}")
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        response_json = response.json()
        
        # タイムスタンプデータの抽出
        alignment = response_json.get("alignment", {})
        characters = alignment.get("characters", [])
        start_times = alignment.get("character_start_times_seconds", [])
        
        # 音声データのデコード
        audio_base64 = response_json.get("audio_base64")
        audio_bytes = base64.b64decode(audio_base64)
        
        # pygameの初期化と再生準備
        pygame.mixer.init()
        audio_stream = io.BytesIO(audio_bytes)
        pygame.mixer.music.load(audio_stream)
        
        print("\n--- [発音同期スタート] ---")
        
        # 音声の再生を開始（バックグラウンドで流れます）
        pygame.mixer.music.play()
        
        # 再生開始時刻を記録（基準点）
        start_wall_time = time.time()
        
        # タイムスタンプを1文字ずつ処理するループ
        for char, target_start_time in zip(characters, start_times):
            
            # 再生が追いつくまで無限ループで待機（ビジーウェイト）
            while True:
                # 再生開始からの経過時間を計算（秒）
                elapsed_time = time.time() - start_wall_time
                
                # 目標の発音時間に到達したらループを抜けて文字を出力
                if elapsed_time >= target_start_time:
                    break
                    
                # CPUの負荷を下げるために極小のウェイトを挟む
                time.sleep(0.005)
            
            # 文字を改行せずに即座に出力（sys.stdout.write + flush で遅延を無くす）
            sys.stdout.write(char)
            sys.stdout.flush()
            
        print("\n--- [発音同期終了] ---\n")
        
        # 最後の文字が出た後、音声が完全に終了するまで待機
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
            
    else:
        print(f"エラーが発生しました: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    speak("にんげんは、なんでこんなに、がんばるの？たまには、ゆっくりやすんだらいいのに。")