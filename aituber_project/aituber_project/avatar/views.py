from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import os
import requests
from django.views.decorators.http import require_GET
from urllib.parse import parse_qs, urlparse

from .core.repositories.comment_store import get_latest_comment

from .core.utils.api_errors import handle_api_errors
from .core.utils.request_utils import parse_post_json

from .core.services.voice_service import delete_voice_file, generate_voice_reply
from .core.services.comment_service import create_generated_comment

from .core.integrations.openai_utils import generate_script_with_instruction
from .core.soul.input_builder import build_script_with_instruction_input

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



from .core.services.voice_service import build_voice_reply

def index(request):
    return render(request, "avatar/index.html")

def live_page(request):
    return render(request, "avatar/live.html")


GOOGLE_CLOUD_CONSOLE_API = os.environ.get("GOOGLE_CLOUD_CONSOLE_API")

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
def use_script_directly(request):
    data, error_response = parse_post_json(request)

    if error_response:
        return error_response
    
    script = data.get("script")
    emotion = data.get("emotion")

    if not script or not emotion:
        return JsonResponse(
            {            
                "error": "scriptとemotionは必須です。",
                "code": "INVALID_INPUT",
            },
            status=400,
        )
    
    reply_data = build_voice_reply(script, emotion)

    return JsonResponse({
        "reply": reply_data
        })
    

@csrf_exempt
@handle_api_errors
def script_with_instruction(request):
    data, error_response = parse_post_json(request)

    if error_response:
        return error_response

    instruction = str(data.get("instruction") or "").strip()

    if not instruction:
        return JsonResponse(
            {"error": "instructionがセットされていません"},
            status=400,
        )

    reply_data = generate_voice_reply(
        lambda: instruction,
        build_script_with_instruction_input,
        generate_script_with_instruction,
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



@require_GET
def youtube_live_comments_api(request):
    live_chat_id = request.GET.get("live_chat_id")
    page_token = request.GET.get("page_token")

    if not live_chat_id:
        return JsonResponse(
            {"error": "live_chat_id is required"},
            status=400,
        )

    params = {
        "part": "snippet,authorDetails",
        "liveChatId": live_chat_id,
        "key": GOOGLE_CLOUD_CONSOLE_API,
        "maxResults": 200,
    }

    if page_token:
        params["pageToken"] = page_token

    response = requests.get(
        "https://www.googleapis.com/youtube/v3/liveChat/messages",
        params=params,
        timeout=10,
    )

    data = response.json()

    if not response.ok:
        return JsonResponse(
            {
                "error": data.get(
                    "error",
                    {"message": "YouTube API error"},
                )
            },
            status=response.status_code,
        )

    comments = []

    for item in data.get("items", []):
        snippet = item.get("snippet", {})
        author = item.get("authorDetails", {})

        if snippet.get("type") != "textMessageEvent":
            continue

        comments.append({
            "id": item.get("id"),
            "username": author.get(
                "displayName",
                "unknown",
            ),
            "text": snippet.get(
                "displayMessage",
                "",
            ),
            "time": snippet.get(
                "publishedAt",
                "",
            ),
            "profileImageUrl": author.get(
                "profileImageUrl",
                "",
            ),
        })

    return JsonResponse({
        "comments": comments,
        "nextPageToken": data.get("nextPageToken"),
        "pollingIntervalMillis": data.get(
            "pollingIntervalMillis",
            5000,
        ),
        "offlineAt": data.get("offlineAt"),
    })



YOUTUBE_VIDEOS_API_URL = ("https://www.googleapis.com/youtube/v3/videos")


def extract_youtube_video_id(url: str) -> str | None:
    if not url:
        return None

    parsed_url = urlparse(url.strip())
    hostname = parsed_url.hostname or ""

    if hostname in {"youtu.be", "www.youtu.be"}:
        return parsed_url.path.strip("/").split("/")[0] or None

    if hostname in {
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
    }:
        if parsed_url.path == "/watch":
            query = parse_qs(parsed_url.query)
            return query.get("v", [None])[0]

        path_parts = [
            part
            for part in parsed_url.path.split("/")
            if part
        ]

        if (
            len(path_parts) >= 2
            and path_parts[0] in {"live", "shorts", "embed"}
        ):
            return path_parts[1]

    return None


@require_GET
def youtube_live_info_api(request):
    live_url = request.GET.get("live_url", "").strip()

    if not live_url:
        return JsonResponse(
            {"error": "live_urlが指定されていません"},
            status=400,
        )

    video_id = extract_youtube_video_id(live_url)

    if not video_id:
        return JsonResponse(
            {"error": "YouTube動画IDを取得できませんでした"},
            status=400,
        )

    api_key = os.environ.get("GOOGLE_CLOUD_CONSOLE_API")

    if not api_key:
        return JsonResponse(
            {
                "error": (
                    "GOOGLE_CLOUD_CONSOLE_APIが設定されていません"
                )
            },
            status=500,
        )

    params = {
        "part": "snippet,liveStreamingDetails",
        "id": video_id,
        "key": api_key,
    }

    try:
        response = requests.get(
            YOUTUBE_VIDEOS_API_URL,
            params=params,
            timeout=10,
        )
    except requests.RequestException as error:
        return JsonResponse(
            {
                "error": (
                    "YouTube APIへの接続に失敗しました"
                ),
                "details": str(error),
            },
            status=502,
        )

    try:
        data = response.json()
    except ValueError:
        return JsonResponse(
            {
                "error": (
                    "YouTube APIから不正な応答が返されました"
                )
            },
            status=502,
        )

    if not response.ok:
        message = (
            data.get("error", {}).get("message")
            or "YouTube APIでエラーが発生しました"
        )

        return JsonResponse(
            {"error": message},
            status=response.status_code,
        )

    items = data.get("items", [])

    if not items:
        return JsonResponse(
            {
                "error": (
                    "指定された動画が見つかりませんでした"
                )
            },
            status=404,
        )

    video = items[0]
    snippet = video.get("snippet", {})
    live_details = video.get(
        "liveStreamingDetails",
        {},
    )

    live_chat_id = live_details.get(
        "activeLiveChatId"
    )

    if not live_chat_id:
        return JsonResponse(
            {
                "error": (
                    "ライブチャットを取得できません。"
                    "配信が終了している、開始前である、"
                    "またはチャットが無効な可能性があります"
                ),
                "videoId": video_id,
                "title": snippet.get("title", ""),
            },
            status=400,
        )

    return JsonResponse({
        "videoId": video_id,
        "liveChatId": live_chat_id,
        "title": snippet.get("title", ""),
        "channelTitle": snippet.get(
            "channelTitle",
            "",
        ),
        "actualStartTime": live_details.get(
            "actualStartTime"
        ),
        "scheduledStartTime": live_details.get(
            "scheduledStartTime"
        ),
    })