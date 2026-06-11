import os
import azure.cognitiveservices.speech as speechsdk

AZURE_SPEECH_KEY = os.environ.get("AZURE_API_KEY")
AZURE_SPEECH_REGION = "japaneast"

def speak(text: str):
    """
    指定したテキストをAzure TTS(人間猫モデル)喋らせる関数
    """
    if not AZURE_SPEECH_KEY:
        print("エラー: 環境変数 'AZURE_API_KEY' が設定されていません。")
        return

    # Azure Speechの構成設定
    speech_config = speechsdk.SpeechConfig(
        subscription=AZURE_SPEECH_KEY, 
        region=AZURE_SPEECH_REGION
    )
    
    # スピーカーへ出力するための設定
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    ssml = f"""
    <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xmlns:mstts='http://www.w3.org/2001/mstts' xml:lang='ja-JP'>
        <voice name='ja-JP-AoiNeural'>
            <mstts:express-as style='chat'>
                <prosody rate='-1.00%' pitch='+5.00%'>
                    {text}
                </prosody>
            </mstts:express-as>
        </voice>
    </speak>
    """

    print(f"音声生成中: {text}")
    
    # SSML形式で音声を非同期生成し、完了を待つ
    result = synthesizer.speak_ssml_async(ssml).get()

    # エラーチェック
    if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"音声合成エラー: {result.reason}")




        