from ..repositories.comment_store import add_reply
from ..repositories.memory_repository import add_ShortTermMemory

from .conversation_service import generate_user_reply
from .voice_service import build_voice_reply


def create_comment_reply(
    latest_comment: dict,
) -> dict:
    username = latest_comment["username"]
    user_message = latest_comment["text"]

    conversation_data = generate_user_reply(
        username=username,
        user_message=user_message,
    )

    add_ShortTermMemory(
        username,
        user_message,
        conversation_data["script"],
    )

    reply_data = build_voice_reply(
        conversation_data["script"],
        conversation_data["emotion"],
    )

    reply_data["target_comment"] = latest_comment

    replies = add_reply(reply_data)

    return {
        "reply": reply_data,
        "replies": replies,
    }