import json

from django.http import JsonResponse

def parse_post_json(request):
    if request.method != "POST":
        return None, JsonResponse(
            {
                "error": "POSTリクエストのみ受け付けています。",
                "code": "METHOD_NOT_ALLOWED",
            },
            status=405,
        )

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return None, JsonResponse(
            {
                "error": "送信されたJSONを解析できませんでした。",
                "code": "INVALID_JSON",
            },
            status=400,
        )

    if not isinstance(data, dict):
        return None, JsonResponse(
            {
                "error": "JSONオブジェクトを送信してください。",
                "code": "INVALID_JSON_TYPE",
            },
            status=400,
        )

    return data, None