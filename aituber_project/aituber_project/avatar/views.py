from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .core.repositories.comment_store import get_latest_comment

from .core.utils.api_errors import handle_api_errors
from .core.utils.request_utils import parse_post_json

from .core.services.voice_service import delete_voice_file
from .core.services.comment_service import create_generated_comment

from .core.services.talk_service import (
    create_self_introduction_reply,
    create_news_talk_reply,
    create_weather_talk_reply,
)

from .core.services.user_comment_service import (
    create_user_comment_reply,
)

from .core.services.comment_reply_service import (
    create_comment_reply,
)

def index(request):
    return render(request, "avatar/index.html")



@handle_api_errors
def generate_comment_api(request):
    result = create_generated_comment()

    return JsonResponse(result)

@handle_api_errors
def reply_to_comment_api(request):
    latest_comment = get_latest_comment()

    if latest_comment is None:
        return JsonResponse(
            {
                "error": "返信対象のコメントがありません。",
                "code": "COMMENT_NOT_FOUND",
            },
            status=400,
        )

    result = create_comment_reply(
        latest_comment=latest_comment,
    )

    return JsonResponse(result)


@handle_api_errors
def self_introduction_api(request):
    reply_data = create_self_introduction_reply()

    return JsonResponse({
        "reply": reply_data,
    })

@handle_api_errors
def news_talk_api(request):
    reply_data = create_news_talk_reply()

    return JsonResponse({
        "reply": reply_data,
    })

@handle_api_errors
def weather_talk_api(request):
    reply_data = create_weather_talk_reply()

    return JsonResponse({
        "reply": reply_data,
    })


@csrf_exempt
@handle_api_errors
def user_comment_api(request):
    data, error_response = parse_post_json(request)

    if error_response:
        return error_response

    username = data.get("username")
    user_message = data.get("message")

    if not username or not user_message:
        return JsonResponse(
            {
                "error": "usernameとmessageは必須です。",
                "code": "INVALID_INPUT",
            },
            status=400,
        )

    reply_data = create_user_comment_reply(
        username=username,
        user_message=user_message,
    )

    return JsonResponse({
        "reply": reply_data,
    })


@csrf_exempt
@handle_api_errors
def delete_voice_api(request):
    data, error_response = parse_post_json(request)

    if error_response:
        return error_response

    audio_id = data.get("audio_id")

    if not audio_id:
        return JsonResponse(
            {
                "error": "audio_idが必要です。",
                "code": "AUDIO_ID_REQUIRED",
            },
            status=400,
        )

    result = delete_voice_file(audio_id)

    return JsonResponse(result)