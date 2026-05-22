import os
import json
import requests
import winsound

from openai import OpenAI
from django.shortcuts import render
from django.http import JsonResponse


AIVIS_URL = "http://127.0.0.1:10101"
SPEAKER_ID = 888753760

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

comments = []
replies = []


def index(request):
    return render(request, "avatar/index.html")


def generate_comment():
    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions="""
貴方はVTuberを視聴している人間です。
VTuberに対して人間っぽいコメントを作成してください。

出力ルール:
- 必ずJSON形式だけで出力する
- JSON以外の文章、説明、コードブロックは出力しない
- キーは必ず "username" と "comment" の2つだけにする
- username にはTikTokやYouTubeにいそうな自然なユーザー名を入れる
- comment には実際のコメント文を入れる
- comment の文字数は1〜30文字まで
- コメントのスタイルは、褒める、軽いツッコミ、挨拶をする、の3パターンからランダムに出力
- 暴言、差別、性的表現、個人情報は含めない

出力例:
{
  "username": "mika_22",
  "comment": "今日もかわいい！"
}
""",
        input="VTuber配信の視聴者コメントを1つ作成してください。"
    )

    raw_text = response.output_text.strip()

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        print("コメントJSON parse error:")
        print(raw_text)
        data = {
            "username": "viewer",
            "comment": "こんにちは！"
        }

    return {
        "username": data.get("username", "viewer"),
        "comment": data.get("comment", "こんにちは！")
    }


def generate_character_reply(username: str, user_message: str) -> dict:
    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions="""
あなたは猫型VTuberの「猫」です。

キャラクター設定:
- 明るく元気
- 猫らしい語尾を自然に少し使う
- 返答は日本語
- 返答は1〜2文
- 80文字以内
- AIや言語モデルであるとは言わない
- 返信相手の名前を自然に呼ぶ

出力ルール:
- 必ずJSON形式だけで出力する
- JSON以外の文章、説明、コードブロックは出力しない
- キーは必ず "script" と "emotion" の2つだけにする
- script には実際に読み上げる返答文を入れる
- script の冒頭で「{username}さん、」のように相手の名前を呼ぶ
- emotion は次のいずれかだけを使う:
  - normal
  - happy
  - surprised
  - sleepy
  - sad

出力例:
{
  "script": "mika_22さん、ありがとうにゃ！今日も来てくれてうれしいにゃ！",
  "emotion": "happy"
}
""",
        input=f"""
返信相手のユーザー名: {username}
返信するコメント: {user_message}
"""
    )

    raw_text = response.output_text.strip()

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        print("返信JSON parse error:")
        print(raw_text)
        data = {
            "script": f"{username}さん、ありがとうにゃ！",
            "emotion": "normal"
        }

    allowed_emotions = ["normal", "happy", "surprised", "sleepy", "sad"]

    script = data.get("script", f"{username}さん、ありがとうにゃ！")
    emotion = data.get("emotion", "normal")

    if emotion not in allowed_emotions:
        emotion = "normal"

    return {
        "script": script,
        "emotion": emotion
    }


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


def generate_comment_api(request):
    generated = generate_comment()

    comment_data = {
        "username": generated["username"],
        "text": generated["comment"],
        "time": "now"
    }

    comments.append(comment_data)

    if len(comments) > 30:
        comments.pop(0)

    return JsonResponse({
        "comment": comment_data,
        "comments": comments
    })


def reply_to_comment_api(request):
    if not comments:
        return JsonResponse({
            "error": "No comments yet."
        }, status=400)

    latest_comment = comments[-1]

    username = latest_comment["username"]
    user_message = latest_comment["text"]

    ai_output = generate_character_reply(username, user_message)

    script = ai_output["script"]
    emotion = ai_output["emotion"]

    reply_data = {
        "target_comment": latest_comment,
        "script": script,
        "emotion": emotion
    }

    replies.append(reply_data)

    if len(replies) > 30:
        replies.pop(0)

    speak(script)

    return JsonResponse({
        "reply": reply_data,
        "replies": replies
    })


def get_comments_api(request):
    return JsonResponse({
        "comments": comments
    })

