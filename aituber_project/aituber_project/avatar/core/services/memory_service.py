from ..repositories.memory_repository import add_LongTermMemory

from ..integrations.memory_generator import generate_LongTermMemory

from ..soul.history_builder import (
    format_long_term_memory_for_comparison,
)

from ..soul.instruction_builder import (
    generate_LongTermMemory_instruction,
)

from ..soul.input_builder import (
    build_LongTermMemory_input,
)


VALID_MEMORY_TYPES = {
    "fact",
    "preference",
    "emotion",
    "skill",
    "event",
}


def create_long_term_memory_if_needed(
    username: str,
    user_message: str,
    existing_memories: list,
    source_messages: list,
):
    formatted_memories = format_long_term_memory_for_comparison(
        existing_memories,
        username,
    )

    instruction = generate_LongTermMemory_instruction(
        formatted_memories,
    )

    prompt_input = build_LongTermMemory_input(user_message)

    memory_data = generate_LongTermMemory(
        instruction,
        prompt_input,
    )

    memory_type = memory_data.get("memory_type", "none")
    content = str(memory_data.get("content") or "").strip()

    try:
        importance = float(
            memory_data.get("importance", 0.0)
        )
    except (TypeError, ValueError):
        importance = 0.0

    if (
        memory_type not in VALID_MEMORY_TYPES
        or not content
        or importance < 0.6
    ):
        return None

    return add_LongTermMemory(
        username,
        memory_type,
        content,
        importance,
        source_messages,
    )