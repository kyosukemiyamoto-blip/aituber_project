import azure.cognitiveservices.speech as speechsdk
import os

# --------------------------------------------------
# 【設定】さっきコピーした情報に書き換えてください
# --------------------------------------------------
AZURE_SPEECH_KEY = os.environ.get("OPENAI_API_KEY")
AZURE_SPEECH_REGION = "japaneast" # 例: 東日本の場合は japaneast

def test_speak():
    # Azureの設定を読み込む
    speech_config = speechsdk.SpeechConfig(
        subscription=AZURE_SPEECH_KEY, 
        region=AZURE_SPEECH_REGION
    )
    
    # 人間猫キャラクターに合う、穏やかで優しい声（音声モデル）を指定
    # ※今回は標準的で自然な「Nanami」さんを設定しています
    speech_config.speech_synthesis_voice_name = "ja-JP-NanamiNeural"

    # スピーカーへ出力するための設定
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    # 喋らせたいセリフ（人間猫風）
    text = "人間は、なんでこんなに頑張るの？たまには、ヨギボーでゆっくり休んだらいいのに。"

    print("音声を生成中...")
    result = synthesizer.speak_text_async(text).get()

    # エラーチェック
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("大成功！声が聞こえたはずです。")
    else:
        print(f"エラーが発生しました: {result.reason}")

# テスト実行
if __name__ == "__main__":
    test_speak()
