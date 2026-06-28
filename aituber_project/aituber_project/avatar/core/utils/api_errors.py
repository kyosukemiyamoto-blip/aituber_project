import logging
from functools import wraps

from django.http import JsonResponse


logger = logging.getLogger(__name__)


def handle_api_errors(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)

        except Exception:
            logger.exception(
                "API処理中に予期しないエラーが発生しました: %s",
                view_func.__name__,
            )

            return JsonResponse(
                {
                    "error": "サーバー処理中にエラーが発生しました。",
                    "code": "INTERNAL_SERVER_ERROR",
                },
                status=500,
            )

    return wrapper