import os
import json
from openai import OpenAI



client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

API_MODEL = "gpt-4.1-mini"
ALLOWED_EMOTIONS = [
    "normal",
    "happy",
    "surprised",
    "angry",
    "sad"
]


#------------------------------------------------------------------------------------------------------------------------------------

def safe_json_parse(raw_text: str, fallback: dict):
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        print("JSON parse error:")
        print(raw_text)
        return fallback
    
#------------------------------------------------------------------------------------------------------------------------------------



def generate_comment(instruction:str, prompt_input:str) -> dict:
    response = client.responses.create(model=API_MODEL, instructions=instruction,input= prompt_input)

    data = safe_json_parse(
        response.output_text.strip(),
        {
            "username": "viewer",
            "comment": "こんにちは！"
        }
    )

    return {
        "username": data.get("username", "viewer"),
        "comment": data.get("comment", "こんにちは！")
    }



#------------------------------------------------------------------------------------------------------------------------------------

def generate_character_reply(instruction: str, prompt_input:str) -> dict:
    response = client.responses.create(model=API_MODEL,instructions= instruction,input=prompt_input)

    data = safe_json_parse(response.output_text.strip(),fallback={})

    script = data.get("script")

    emotion = data.get(
        "emotion",
        "normal"
    )

    if emotion not in ALLOWED_EMOTIONS:
        emotion = "normal"

    return {
        "script": script,
        "emotion": emotion
    }


#------------------------------------------------------------------------------------------------------------------------------------

def generate_self_introduction(instruction:str, prompt_input:str):
    response = client.responses.create(model=API_MODEL,instructions=instruction,input=prompt_input)

    data = safe_json_parse(
        response.output_text.strip(),
        {
            "script": (
                "自己紹介をする予定でしたが、"
                "急遽予定を変更して、しません。"
            )
        }
    )

    return data


#------------------------------------------------------------------------------------------------------------------------------------

def generate_news_talk(instruction:str,prompt_input:str) -> dict:
    response = client.responses.create(model=API_MODEL, instructions=instruction ,input=prompt_input)

    data = safe_json_parse(
        response.output_text.strip(),
        {
            "script": "",
            "emotion": "normal"
        }
    )

    emotion = data.get(
        "emotion",
        "normal"
    )

    if emotion not in ALLOWED_EMOTIONS:
        emotion = "normal"

    return {
        "script": data.get("script", ""),
        "emotion": emotion
    }


#------------------------------------------------------------------------------------------------------------------------------------


def generate_weather_talk(instruction:str, prompt_input:str):

    response = client.responses.create(model=API_MODEL, instructions=instruction, input=prompt_input)

    data = safe_json_parse(
        response.output_text.strip(),
        {
            "script": ""
        }
    )

    return {
        "script": data.get("script", ""),
        "emotion": "normal"
    }

#------------------------------------------------------------------------------------------------------------------------------------

def generate_LongTermMemory(instruction:str,prompt_input:str):
    response = client.responses.create(model=API_MODEL, instructions=instruction, input=prompt_input)

    data = safe_json_parse(
        response.output_text.strip(),
        {
            "memory_type":"",
            "content":"",
            "importance":0.0,
        }
    )

    memory_type = data.get("memory_type", "none")
    content = data.get("content", "")
    importance = data.get("importance", 0.0)

    try:
        importance = float(importance)
    except (TypeError, ValueError):
        importance = 0.0

    return {
        "memory_type": memory_type,
        "content": content,
        "importance": importance
    }

# Object example :
# {
#   "user": "kyosuke",
#   "memory_type": "preference",
#   "content": "ユーザーはC言語やアセンブリに興味がある",
#   "importance": 0.7,
#   "source_messages": [2],
#   "created_at": "2026-05-26T00:10:02Z"
# }