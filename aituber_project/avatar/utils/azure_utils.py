import os
import uuid
import html
import azure.cognitiveservices.speech as speechsdk
from django.conf import settings

AZURE_SPEECH_KEY = os.environ.get("AZURE_API_KEY")
AZURE_SPEECH_REGION = "japaneast"


def synthesize_for_vtube(text: str) -> dict:
    if not AZURE_SPEECH_KEY:
        raise RuntimeError("環境変数 'AZURE_API_KEY' が設定されていません。")

    speech_config = speechsdk.SpeechConfig(
        subscription=AZURE_SPEECH_KEY,
        region=AZURE_SPEECH_REGION
    )

    speech_config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Riff24Khz16BitMonoPcm
    )

    filename = f"voice_{uuid.uuid4().hex}.wav"

    output_dir = os.path.join(settings.MEDIA_ROOT, "voices")
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, filename)
    audio_url = settings.MEDIA_URL + f"voices/{filename}"

    audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)

    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config
    )

    viseme_events = []

    def on_viseme(evt):
        offset_seconds = evt.audio_offset / 10_000_000

        viseme_events.append({
            "offset": offset_seconds,
            "viseme_id": evt.viseme_id
        })

    synthesizer.viseme_received.connect(on_viseme)

    escaped_text = html.escape(text)

    ssml = f"""
    <speak version='1.0'
           xmlns='http://www.w3.org/2001/10/synthesis'
           xmlns:mstts='http://www.w3.org/2001/mstts'
           xml:lang='ja-JP'>
        <voice name='ja-JP-AoiNeural'>
            <mstts:express-as style='chat'>
                <prosody rate='-1.00%' pitch='+5.00%'>
                    {escaped_text}
                </prosody>
            </mstts:express-as>
        </voice>
    </speak>
    """

    print(f"音声ファイル生成中: {text}")

    result = synthesizer.speak_ssml_async(ssml).get()

    if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
        raise RuntimeError(f"音声合成エラー: {result.reason}")

    lip_sync = convert_visemes_to_lip_sync(viseme_events)

    return {
        "audio_id": filename,
        "audio_url": audio_url,
        "lip_sync": lip_sync,
    }


def convert_visemes_to_lip_sync(viseme_events: list[dict]) -> list[dict]:
    if not viseme_events:
        return []

    viseme_to_mouth = {
        0: 0.00,
        1: 0.25,
        2: 0.45,
        3: 0.35,
        4: 0.50,
        5: 0.40,
        6: 0.55,
        7: 0.65,
        8: 0.30,
        9: 0.40,
        10: 0.45,
        11: 0.55,
        12: 0.70,
        13: 0.35,
        14: 0.45,
        15: 0.50,
        16: 0.60,
        17: 0.75,
        18: 0.30,
        19: 0.40,
        20: 0.50,
        21: 0.65,
    }

    lip_sync = []

    for i, event in enumerate(viseme_events):
        current_offset = event["offset"]

        if i + 1 < len(viseme_events):
            next_offset = viseme_events[i + 1]["offset"]
            duration = max(0.03, next_offset - current_offset)
        else:
            duration = 0.08

        viseme_id = event["viseme_id"]
        mouth = viseme_to_mouth.get(viseme_id, 0.20)

        lip_sync.append({
            "mouth": round(mouth, 3),
            "duration": round(duration, 3),
            "viseme_id": viseme_id,
        })

    return smooth_lip_sync(lip_sync)



def smooth_lip_sync(lip_sync: list[dict]) -> list[dict]:
    if len(lip_sync) < 3:
        return lip_sync

    smoothed = []

    for i, item in enumerate(lip_sync):
        if i == 0 or i == len(lip_sync) - 1:
            smoothed.append(item)
            continue

        prev_mouth = lip_sync[i - 1]["mouth"]
        current_mouth = item["mouth"]
        next_mouth = lip_sync[i + 1]["mouth"]

        smoothed_mouth = (prev_mouth * 0.25 + current_mouth * 0.50 + next_mouth * 0.25)

        smoothed.append({
            **item,
            "mouth": round(smoothed_mouth, 3),
        })

    return smoothed