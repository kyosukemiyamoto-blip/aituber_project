from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

import json
import os

from .utils.openai_utils import (
    generate_comment,
    generate_character_reply,
    generate_self_introduction,
    generate_news_talk,
    generate_weather_talk,
    generate_LongTermMemory,
)

from .utils.azure_utils import synthesize_for_vtube

from .utils.store import (
    add_comment,
    add_reply,
    get_latest_comment,
    add_ShortTermMemory,
    get_ShortTermMemory,
    add_LongTermMemory,
    get_LongTermMemory,
)

from .utils.soul.history_builder import (
    format_short_term_memory,
    format_long_term_memory,
)

from .utils.soul.instruction_builder import (
    generate_comment_instruction,
    generate_character_reply_instruction,
    generate_self_instroduction_instruction,
    generate_news_talk_instruction,
    generate_weather_talk_instruction,
    generate_LongTermMemory_instruction,
)

from .utils.soul.input_builder import (
    build_generate_comment_input,
    build_generate_self_instruction_input,
    build_generate_news_talk_input,
    build_generate_weather_talk_input,
    build_character_reply_input,
    build_LongTermMemory_input,
)


def index(request):
    return render(request, "avatar/index.html")


def build_voice_reply(script: str, emotion: str) -> dict:
    """
    script / emotion に対して、
    Azure TTS音声ファイル + lip_syncデータを付与したreply dictを作る。
    """
    voice_data = synthesize_for_vtube(script)

    return {
        "script": script,
        "emotion": emotion,
        "audio_id": voice_data["audio_id"],
        "audio_url": voice_data["audio_url"],
        "lip_sync": voice_data["lip_sync"],
    }


def generate_comment_api(request):
    instruction = generate_comment_instruction()
    prompt_input = build_generate_comment_input()
    generated = generate_comment(instruction, prompt_input)

    comment_data = {
        "username": generated["username"],
        "text": generated["comment"],
        "time": "now",
    }

    comments = add_comment(comment_data)

    return JsonResponse({
        "comment": comment_data,
        "comments": comments,
    })


def reply_to_comment_api(request):
    latest_comment = get_latest_comment()

    if latest_comment is None:
        return JsonResponse({
            "error": "No comments yet."
        }, status=400)

    username = latest_comment["username"]
    user_message = latest_comment["text"]

    short_term_memory = get_ShortTermMemory(username)
    formatted_short_term_memory = format_short_term_memory(
        short_term_memory,
        username,
    )

    long_term_memory = get_LongTermMemory(username)
    formatted_long_term_memory = format_long_term_memory(
        long_term_memory,
        username,
    )

    instruction = generate_character_reply_instruction()
    prompt_input = build_character_reply_input(
        username,
        user_message,
        formatted_short_term_memory,
        formatted_long_term_memory,
    )

    ai_output = generate_character_reply(instruction, prompt_input)

    script = ai_output["script"]
    emotion = ai_output["emotion"]

    add_ShortTermMemory(username, user_message, script)

    reply_data = build_voice_reply(script, emotion)
    reply_data["target_comment"] = latest_comment

    replies = add_reply(reply_data)

    return JsonResponse({
        "reply": reply_data,
        "replies": replies,
    })


def self_introduction_api(request):
    instruction = generate_self_instroduction_instruction()
    prompt_input = build_generate_self_instruction_input()
    ai_output = generate_self_introduction(instruction, prompt_input)

    script = ai_output["script"]
    emotion = ai_output.get("emotion", "normal")

    reply_data = build_voice_reply(script, emotion)

    return JsonResponse({
        "reply": reply_data,
        "script": script,
        "emotion": emotion,
        "audio_id": reply_data["audio_id"],
        "audio_url": reply_data["audio_url"],
        "lip_sync": reply_data["lip_sync"],
    })


def news_talk_api(request):
    instruction = generate_news_talk_instruction()
    prompt_input = build_generate_news_talk_input()
    ai_output = generate_news_talk(instruction, prompt_input)

    script = ai_output["script"]
    emotion = ai_output["emotion"]

    reply_data = build_voice_reply(script, emotion)

    return JsonResponse({
        "reply": reply_data,
        "script": script,
        "emotion": emotion,
        "audio_id": reply_data["audio_id"],
        "audio_url": reply_data["audio_url"],
        "lip_sync": reply_data["lip_sync"],
    })


def weather_talk_api(request):
    instruction = generate_weather_talk_instruction()
    prompt_input = build_generate_weather_talk_input()
    ai_output = generate_weather_talk(instruction, prompt_input)

    script = ai_output["script"]
    emotion = ai_output.get("emotion", "normal")

    reply_data = build_voice_reply(script, emotion)

    return JsonResponse({
        "reply": reply_data,
        "script": script,
        "emotion": emotion,
        "audio_id": reply_data["audio_id"],
        "audio_url": reply_data["audio_url"],
        "lip_sync": reply_data["lip_sync"],
    })


@csrf_exempt
def user_comment_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "invalid json"}, status=400)

    username = data.get("username")
    user_message = data.get("message")

    if not username or not user_message:
        return JsonResponse({"error": "invalid input"}, status=400)

    short_term_memory = get_ShortTermMemory(username)
    formatted_short_term_memory = format_short_term_memory(
        short_term_memory,
        username,
    )

    long_term_memory = get_LongTermMemory(username)
    formatted_long_term_memory = format_long_term_memory(
        long_term_memory,
        username,
    )

    instruction = generate_character_reply_instruction()
    prompt_input = build_character_reply_input(
        username,
        user_message,
        formatted_short_term_memory,
        formatted_long_term_memory,
    )

    ai_output = generate_character_reply(instruction, prompt_input)

    script = ai_output["script"]
    emotion = ai_output["emotion"]

    user_msg, assistant_msg = add_ShortTermMemory(
        username,
        user_message,
        script,
    )

    source_messages = [user_msg]

    # Azure TTSで音声ファイル生成 + lip_sync生成
    reply_data = build_voice_reply(script, emotion)

    # 長期記憶生成
    ltm_instruction = generate_LongTermMemory_instruction()
    ltm_input = build_LongTermMemory_input(user_message)
    ltm_data = generate_LongTermMemory(ltm_instruction, ltm_input)

    VALID_MEMORY_TYPES = {
        "fact",
        "preference",
        "emotion",
        "skill",
        "event",
    }

    memory_type = ltm_data.get("memory_type", "none")
    content = ltm_data.get("content", "").strip()

    try:
        importance = float(ltm_data.get("importance", 0.0))
    except (TypeError, ValueError):
        importance = 0.0

    if (
        memory_type in VALID_MEMORY_TYPES
        and content != ""
        and importance >= 0.6
    ):
        add_LongTermMemory(
            username,
            memory_type,
            content,
            importance,
            source_messages,
        )

    return JsonResponse({
        "reply": reply_data
    })


@csrf_exempt
def delete_voice_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "invalid json"}, status=400)

    audio_id = data.get("audio_id")

    if not audio_id:
        return JsonResponse({"error": "audio_id required"}, status=400)

    # パストラバーサル対策
    audio_id = os.path.basename(audio_id)

    file_path = os.path.join(settings.MEDIA_ROOT, "voices", audio_id)

    if os.path.exists(file_path):
        os.remove(file_path)
        return JsonResponse({
            "deleted": True,
            "audio_id": audio_id,
        })

    return JsonResponse({
        "deleted": False,
        "reason": "file not found",
        "audio_id": audio_id,
    })