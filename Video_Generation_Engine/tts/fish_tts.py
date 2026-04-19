import os
from pathlib import Path
from kokoro import KPipeline
import soundfile as sf
import numpy as np

# Initialize the Kokoro pipeline locally
# 'a' stands for American English, but it sounds very natural/global
pipeline = KPipeline(lang_code='a')


def generate_voiceover_audio(voiceover_items: list):
    """
    Generates audio locally using Kokoro TTS.

    Accepts a list of dicts with keys:
      - 'scene_id' (optional): int
      - 'text': str

    Writes files to `data/audio_cache/scene_{scene_id}.wav` when provided,
    otherwise falls back to the enumeration index.
    """
    audio_paths = []
    output_dir = Path("data/audio_cache")
    output_dir.mkdir(parents=True, exist_ok=True)

    for idx, item in enumerate(voiceover_items):
        text = item.get("text", "").strip()
        if not text:
            continue

        scene_id = item.get("scene_id", idx + 1)
        file_path = output_dir / f"scene_{int(scene_id)}.wav"
        print(f"🎙️ Kokoro Generating Scene {scene_id}...")

        # Kokoro generates audio in chunks (generator)
        generator = pipeline(
            text, voice='af_bella', speed=1, split_pattern=r'\n+'
        )

        chunks = []
        for i, (gs, ps, audio) in enumerate(generator):
            # audio is a NumPy array (samples, channels)
            chunks.append(audio)

        if not chunks:
            print(f"⚠️ No audio chunks generated for scene {scene_id}")
            continue

        # Concatenate chunks along the time axis
        try:
            combined = np.concatenate(chunks, axis=0)
        except Exception:
            combined = chunks[0]

        # Write as 24kHz WAV (kokoro default). Resampling will be handled later by renderer.
        sf.write(str(file_path), combined, 24000)
        print(f"✅ Created: {file_path}")
        audio_paths.append(str(file_path))

    return audio_paths