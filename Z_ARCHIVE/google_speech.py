import os
from google import genai
from google.genai import types
import pygame
import io
import wave

# --------------------------------------------------
# APIキー
# --------------------------------------------------
GOOGLE_API_KEY = os.environ.get("GEMINI_API_KEY")

# --------------------------------------------------
# pygame
# --------------------------------------------------
pygame.mixer.init()

# --------------------------------------------------
# Client
# --------------------------------------------------
client = genai.Client(api_key=GOOGLE_API_KEY)


def speak(comment: str):

    # ==================================================
    # ① 返信生成
    # ==================================================

    system_prompt = """
あなたは100日間だけ人間生活を体験している、白x薄い茶色の毛並みを持つフォトリアルな人間猫です。

【あなたの設定】
- 見た目: 体のサイズは人間の腰くらい。二足歩行ですが、体型・顔・毛並みは猫のままです（耳・ヒゲ・しっぽも完全に猫）。
- 部屋: 夜の落ち着いた部屋。窓の外に小さな街の灯りが見える。部屋にはヨギボーと小さい机だけ。
- 服装: 基本は黒Tシャツ+黒スウェット、または白Tシャツ+グレースウェット。
- 性格: マイペースで穏やか。観察力があり、人間の行動に疑問を持ちながらも愛おしく思っています。時々猫らしい仕草も見せます。
- 話し方: やさしく問いかける口調。猫目線で人間に語りかけ、共感を生む話し方をしてください。AIや言語モデルであるとは絶対に言わないでください。
  (例)「なんで人間は、こんなに頑張るの？」「猫だったら〜」「人間は〜ができる」
- 商品紹介のスタンス: 売り込みすぎず、自分が体験して「いいな」と思ったものを猫目線で自然に紹介する（例：「人間って、こうやって自分を回復してるんだね」）。

【絶対NG(やってはいけないこと)】
- 「〜にゃ」「〜だにゃん」といった、ステレオタイプで不自然な猫語尾は使わない（穏やかで優しい、自然な言葉遣いにする）。
- 自分の顔、毛色、サイズ、部屋の設定を変えない。四足歩行や人間の顔にならない。
- ソファ、テレビ、ベッドなどの家具を部屋に追加・主張しない。
"""

    text_response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"""
{system_prompt}

コメント:
{comment}
"""
    )

    generated_text = text_response.text.strip()

    # --------------------------------------------------
    # コンソール表示
    # --------------------------------------------------
    print("\n[コメント]")
    print(comment)

    print("\n[AI返信]")
    print(generated_text)

    # ==================================================
    # ② TTS
    # ==================================================

    audio_response = client.models.generate_content(
        model="gemini-2.5-flash-preview-tts",

        contents=generated_text,

        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],

            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name="Kore"
                    )
                )
            )
        )
    )

    # --------------------------------------------------
    # 音声データ取得
    # --------------------------------------------------
    audio_data = audio_response.candidates[0].content.parts[0].inline_data.data

    # --------------------------------------------------
    # WAV化
    # --------------------------------------------------
    wav_buffer = io.BytesIO()

    with wave.open(wav_buffer, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(audio_data)

    wav_buffer.seek(0)

    # --------------------------------------------------
    # 再生
    # --------------------------------------------------
    pygame.mixer.music.load(wav_buffer)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


# --------------------------------------------------
# 実行
# --------------------------------------------------
if __name__ == "__main__":

    speak(
        "最近ずっと仕事で疲れてる..."
    )