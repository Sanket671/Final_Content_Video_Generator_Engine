import os
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
MODEL_ID = os.getenv("ELEVENLABS_MODEL")

if not ELEVENLABS_API_KEY:
    raise RuntimeError("ELEVENLABS_API_KEY not set")

BASE_URL = "https://api.elevenlabs.io/v1/text-to-speech"


def generate_voiceover_audio(voiceover_items: list[dict], output_dir: str = "audio") -> list[dict]:
    """
    Generates one WAV file per scene.
    Returns metadata for downstream FFmpeg usage.
    """

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    audio_outputs = []

    for item in voiceover_items:
        scene_id = item["scene_id"]
        text = item["text"]

        output_path = f"{output_dir}/scene_{scene_id}.wav"

        response = requests.post(
            f"{BASE_URL}/{VOICE_ID}",
            headers={
                "xi-api-key": ELEVENLABS_API_KEY,
                "Content-Type": "application/json",
                "Accept": "audio/mpeg"
            },
            json={
                "text": text,
                "model_id": MODEL_ID,
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.7
                }
            },
            timeout=30
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"ElevenLabs error {response.status_code}: {response.text}"
            )

        with open(output_path, "wb") as f:
            f.write(response.content)

        audio_outputs.append({
            "scene_id": scene_id,
            "file": output_path,
            "approx_duration_sec": item["approx_duration_sec"],
            "voice": "reticulo_narrator_v1"
        })

    return audio_outputs
