import os
from pathlib import Path
from kokoro import KPipeline
import soundfile as sf

# Initialize the Kokoro pipeline locally
# 'a' stands for American English, but it sounds very natural/global
pipeline = KPipeline(lang_code='a') 

def generate_voiceover_audio(voiceover_items: list):
    """
    Generates audio locally using Kokoro TTS. 
    100% Free, No API required.
    """
    audio_paths = []
    output_dir = Path("data/audio_cache")
    output_dir.mkdir(parents=True, exist_ok=True)

    for idx, item in enumerate(voiceover_items):
        text = item.get("text", "")
        if not text:
            continue
            
        file_path = output_dir / f"scene_{idx+1}.wav"
        print(f"🎙️ Kokoro Generating Scene {idx+1}...")

        # Kokoro generates audio in chunks (generator)
        # af_bella is a very natural female voice. 
        # For a male Indian-style voice, you can try 'am_adam'
        generator = pipeline(
            text, voice='af_bella', # You can change voice here
            speed=1, split_pattern=r'\n+'
        )

        # Collect and save the audio
        for i, (gs, ps, audio) in enumerate(generator):
            sf.write(str(file_path), audio, 24000) # 24khz is standard for Kokoro
        
        print(f"✅ Created: {file_path}")
        audio_paths.append(str(file_path))

    return audio_paths