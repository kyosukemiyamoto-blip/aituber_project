from .conversation_service import generate_user_reply
from .memory_service import create_long_term_memory_if_needed
from .voice_service import build_voice_reply

from ..repositories.memory_repository import add_ShortTermMemory


def create_user_comment_reply(
    username: str,
    user_message: str,
) -> dict:
    conversation_data = generate_user_reply(
        username=username,
        user_message=user_message,
    )

    user_message_object, assistant_message_object = add_ShortTermMemory(
        username,
        user_message,
        conversation_data["script"],
    )

    reply_data = build_voice_reply(
        conversation_data["script"],
        conversation_data["emotion"],
    )

    create_long_term_memory_if_needed(
        username=username,
        user_message=user_message,
        existing_memories=conversation_data[
            "long_term_memories"
        ],
        source_messages=[
            user_message_object
        ],
    )

    return reply_data