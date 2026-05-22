import requests
import winsound
import os
from openai import OpenAI
import json

AIVIS_URL = "http://127.0.0.1:10101"
SPEAKER_ID = 888753760

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def generate_character_reply(user_message: str) -> str:
    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions = """
あなたは猫型VTuberの「猫」です。

キャラクター設定:
- 明るく元気
- 猫らしい語尾を自然に少し使う
- 返答は日本語
- 返答は1〜2文
- 80文字以内
- AIや言語モデルであるとは言わない

出力ルール:
- 必ずJSON形式だけで出力する
- JSON以外の文章、説明、コードブロックは出力しない
- キーは必ず "script" と "emotion" の2つだけにする
- comment には実際に読み上げる返答文を入れる
- emotion は次のいずれかだけを使う:
  - normal
  - happy
  - surprised
  - sleepy
  - sad

出力例:
{
  "script": "来てくれてありがとうにゃ！今日も元気にいくにゃ！",
  "emotion": "happy"
}
""",
        input=f"返信をするコメント: {user_message}"
    )

    raw_text = response.output_text.strip()
    data = json.loads(raw_text)
    return data

def speak(text:str):
    query_response = requests.post(f"{AIVIS_URL}/audio_query",params={"text":text,"speaker":SPEAKER_ID})
    query_response.raise_for_status()
    audio_query = query_response.json()

    synthesis_response = requests.post(f"{AIVIS_URL}/synthesis",params={"speaker":SPEAKER_ID},json=audio_query)
    synthesis_response.raise_for_status()

    winsound.PlaySound(synthesis_response.content,winsound.SND_MEMORY)

if __name__ == "__main__":
    while True:
        text = input("Please input the texts you want him to speak : ")
        if text.lower() in ["exit","quit"]:
            break
        if not text.strip():
            continue

        ai_output = generate_character_reply(text)
        script = ai_output["script"]
        emotion = ai_output["emotion"]
        print(script)
        print(emotion)
        speak(script)