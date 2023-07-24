import google.cloud.texttospeech as tts
from datetime import datetime
import soundfile


class GoogleTtsService:
    def __init__(self, voice="en-US-Polyglot-1"):
        self.voice = voice
        self.language_code = "-".join(self.voice.split("-")[:2])

    def text_to_wav(self, text: str):
        text_input = tts.SynthesisInput(text=text)
        voice_params = tts.VoiceSelectionParams(
            language_code=self.language_code, name=self.voice
        )
        audio_config = tts.AudioConfig(
            audio_encoding=tts.AudioEncoding.LINEAR16)
        client = tts.TextToSpeechClient()
        response = client.synthesize_speech(
            input=text_input,
            voice=voice_params,
            audio_config=audio_config
        )

        return response.audio_content
