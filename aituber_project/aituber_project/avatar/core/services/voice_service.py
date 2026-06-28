import os

from django.conf import settings

from ..integrations.azure_utils import synthesize_for_vtube


def build_voice_reply(script: str, emotion: str) -> dict:
    voice_data = synthesize_for_vtube(script)

    return {
        "script": script,
        "emotion": emotion,
        "audio_id": voice_data["audio_id"],
        "audio_url": voice_data["audio_url"],
        "lip_sync": voice_data["lip_sync"],
    }


def generate_voice_reply(
    instruction_builder,
    input_builder,
    generator,
) -> dict:
    instruction = instruction_builder()
    prompt_input = input_builder()

    ai_output = generator(
        instruction,
        prompt_input,
    )

    script = ai_output.get("script", "")
    emotion = ai_output.get("emotion", "normal")

    if not script:
        raise ValueError("script is empty")

    return build_voice_reply(
        script,
        emotion,
    )



def delete_voice_file(audio_id: str) -> dict:
    safe_audio_id = os.path.basename(audio_id)

    file_path = os.path.join(
        settings.MEDIA_ROOT,
        "voices",
        safe_audio_id,
    )

    if not os.path.exists(file_path):
        return {
            "deleted": False,
            "reason": "file not found",
            "audio_id": safe_audio_id,
        }

    os.remove(file_path)

    return {
        "deleted": True,
        "audio_id": safe_audio_id,
    }