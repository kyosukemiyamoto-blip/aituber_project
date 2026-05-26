from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import threading
from .utils.openai_utils import (
    generate_comment, 
    generate_character_reply, 
    generate_self_introduction, 
    generate_news_talk, 
    generate_weather_talk,
    generate_LongTermMemory)
from .utils.azure_utils import speak
from .utils.store import (
    add_comment,
    add_reply,
    get_latest_comment,
    add_ShortTermMemory,
    get_ShortTermMemory,
    add_LongTermMemory,
    get_LongTermMemory)
from .utils.soul.history_builder import format_history
from .utils.soul.instruction_builder import (
    generate_comment_instruction,
    generate_character_reply_instruction,
    generate_self_instroduction_instruction,
    generate_news_talk_instruction,
    generate_weather_talk_instruction,
    generate_LongTermMemory_instruction)
from .utils.soul.input_builder import (
    build_generate_comment_input,
    build_generate_self_instruction_input,
    build_generate_news_talk_input,
    build_generate_weather_talk_input,
    build_character_reply_input,
    build_LongTermMemory_input)


def index(request):
    return render(request, "avatar/index.html")


def generate_comment_api(request):
    instruction = generate_comment_instruction()
    prompt_input = build_generate_comment_input()
    generated = generate_comment(instruction, prompt_input)

    comment_data = {
        "username": generated["username"],
        "text": generated["comment"],
        "time": "now"
    }

    comments = add_comment(comment_data)

    return JsonResponse({
        "comment": comment_data,
        "comments": comments
    })


def reply_to_comment_api(request):
    latest_comment = get_latest_comment()

    if latest_comment is None:
        return JsonResponse({
            "error": "No comments yet."
        }, status=400)

    username = latest_comment["username"]
    user_message = latest_comment["text"]

    history = get_ShortTermMemory(username)
    formatted_history = format_history(history,username)

    instruction = generate_character_reply_instruction()
    prompt_input = build_character_reply_input(username, user_message, formatted_history)
    ai_output = generate_character_reply(instruction, prompt_input)

    script = ai_output["script"]
    emotion = ai_output["emotion"]

    add_ShortTermMemory(username, user_message, script)

    reply_data = {
        "target_comment": latest_comment,
        "script": script,
        "emotion": emotion
    }

    replies = add_reply(reply_data)

    speak(script)

    return JsonResponse({
        "reply": reply_data,
        "replies": replies
    })




def self_introduction_api(request):
    instruction = generate_self_instroduction_instruction()
    prompt_input = build_generate_self_instruction_input()
    ai_output = generate_self_introduction(instruction, prompt_input)
    script = ai_output["script"]
    speak(script)

    return JsonResponse({
        "script": script
    })


def news_talk_api(request):
    instruction = generate_news_talk_instruction()
    prompt_input = build_generate_news_talk_input()
    ai_output = generate_news_talk(instruction, prompt_input)
    script = ai_output["script"]
    emotion = ai_output["emotion"]
    speak(script)

    return JsonResponse({
        "script": script,
        "emotion": emotion
    })

def weather_talk_api(request):
    instruction = generate_weather_talk_instruction()
    prompt_input = build_generate_weather_talk_input()
    ai_output = generate_weather_talk(instruction, prompt_input)
    script = ai_output["script"]
    emotion = ai_output["emotion"]
    speak(script)

    return JsonResponse({
        "script": script,
        "emotion": emotion
    })



@csrf_exempt
def user_comment_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    data = json.loads(request.body)

    username = data.get("username")
    user_message = data.get("message")

    if not username or not user_message:
        return JsonResponse({"error": "invalid input"}, status=400)


    history = get_ShortTermMemory(username)
    formatted_history = format_history(history,username)

    instruction = generate_character_reply_instruction()
    prompt_input = build_character_reply_input(username, user_message, formatted_history)
    ai_output = generate_character_reply(instruction,prompt_input)
    script = ai_output["script"]
    emotion = ai_output["emotion"]

    user_msg, assistant_msg = add_ShortTermMemory(username, user_message, script)
    source_messages = [user_msg]    
    threading.Thread(target=speak, args=(script,)).start()
    
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

    if (memory_type in VALID_MEMORY_TYPES and content != "" and importance >= 0.6):
        add_LongTermMemory(username, memory_type, content, importance, source_messages)

    return JsonResponse({
        "reply": {
            "script": script,
            "emotion": emotion
        }
    })