from ..integrations.openai_utils import generate_character_reply

from ..repositories.memory_repository import (
    get_ShortTermMemory,
    get_LongTermMemory,
)

from ..soul.history_builder import (
    format_short_term_memory,
    format_long_term_memory,
)

from ..soul.instruction_builder import (
    generate_character_reply_instruction,
)

from ..soul.input_builder import (
    build_character_reply_input,
)




def generate_user_reply(
    username: str,
    user_message: str,
) -> dict:
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

    ai_output = generate_character_reply(
        instruction,
        prompt_input,
    )

    script = ai_output.get("script", "")
    emotion = ai_output.get("emotion", "normal")

    if not script:
        raise ValueError("script is empty")



    return {
        "script": script,
        "emotion": emotion,
        "long_term_memories": long_term_memory,
    }