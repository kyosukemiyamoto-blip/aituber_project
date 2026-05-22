import feedparser
from openai import OpenAI
import os
import json

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

feed = feedparser.parse("https://www.nhk.or.jp/rss/news/cat0.xml")

entry = feed.entries[0]
title = entry.title
summary = entry.summary

def news_talk_generator(title: str, summary: str) -> dict:
    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions=f"""
あなたは猫型VTuberの「猫」です。指定されたニュース情報を読み上げ、簡単な感想を言ってください。

キャラクター設定:
- 明るく元気
- 猫らしい語尾を自然に少し使う
- 返答は日本語
- AIや言語モデルであるとは言わない

出力ルール:
- 必ずJSON形式だけで出力する
- JSON以外の文章、説明、コードブロックは出力しない
- キーは必ず "script" と "emotion" の2つだけにする
- script には実際に読み上げる返答文を入れる
- emotionには、与えられたニュースに適切な感情を入れること。例えば、和やかなニュースは"happy",いまたしい事故は"sad"など。
- emotion は次のいずれかだけを使う:
  - normal
  - happy
  - surprised
  - angry
  - sad

出力例:
{{
  "script": "...",
  "emotion": "..."
}}
""",
        input=f"""
読み上げるニュースのタイトル: {title}
読み上げるニュースの本文: {summary}
この二つをもとに、120文字から200文字の文章を生成してください。
"""
    )
    raw_text = response.output_text.strip()
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        print("返信JSON parse error:")
        print(raw_text)
        data = {
            "script": f"",
            "emotion": "normal"
        }

    allowed_emotions = ["normal", "happy", "surprised", "angry", "sad"]

    script = data.get("script")
    emotion = data.get("emotion", "normal")

    if emotion not in allowed_emotions:
        emotion = "normal"

    print(f"Script: {script}\nEmotion: {emotion}")
    return {
        "script": script,
        "emotion": emotion
    }

news_talk_generator(title,summary)