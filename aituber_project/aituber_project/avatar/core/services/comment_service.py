from ..integrations.openai_utils import generate_comment

from ..repositories.comment_store import add_comment

from ..soul.instruction_builder import (
    generate_comment_instruction,
)

from ..soul.input_builder import (
    build_generate_comment_input,
)


def create_generated_comment() -> dict:
    instruction = generate_comment_instruction()
    prompt_input = build_generate_comment_input()

    generated = generate_comment(
        instruction,
        prompt_input,
    )

    comment_data = {
        "username": generated["username"],
        "text": generated["comment"],
        "time": "now",
    }

    comments = add_comment(comment_data)

    return {
        "comment": comment_data,
        "comments": comments,
    }