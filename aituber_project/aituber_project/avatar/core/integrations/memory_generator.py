import os

from openai import OpenAI

from .openai_utils import safe_json_parse

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
API_MODEL = "gpt-4.1-mini"

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