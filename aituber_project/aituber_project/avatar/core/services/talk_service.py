from ..integrations.openai_utils import (
    generate_self_introduction,
    generate_news_talk,
    generate_weather_talk,
)

from ..soul.instruction_builder import (
    generate_self_introduction_instruction,
    generate_news_talk_instruction,
    generate_weather_talk_instruction,
)

from ..soul.input_builder import (
    build_generate_self_introduction_input,
    build_generate_news_talk_input,
    build_generate_weather_talk_input,
)

from .voice_service import generate_voice_reply

from .voice_service import generate_voice_reply


def create_self_introduction_reply() -> dict:
    return generate_voice_reply(
        generate_self_introduction_instruction,
        build_generate_self_introduction_input,
        generate_self_introduction,
    )


def create_news_talk_reply() -> dict:
    return generate_voice_reply(
        generate_news_talk_instruction,
        build_generate_news_talk_input,
        generate_news_talk,
    )


def create_weather_talk_reply() -> dict:
    return generate_voice_reply(
        generate_weather_talk_instruction,
        build_generate_weather_talk_input,
        generate_weather_talk,
    )