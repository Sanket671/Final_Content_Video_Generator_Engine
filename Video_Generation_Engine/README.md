# Reticulo Video Engine

This is the orchestrator and the small example engine that creates short vertical product videos using LLM-driven scripts, TTS and FFmpeg/Blender rendering.

## Quickstart

1. Create and activate a virtual environment:

```bash
python -m venv venv
# macOS / Linux
source venv/bin/activate
# Windows
venv\Scripts\activate
```

2. Install Python deps:

```bash
pip install -r requirements.txt
```

3. Add a `.env` with required API keys (see DOCUMENTATION_FULL.md for details).

4. Run the orchestrator:

```bash
python runner/main.py
```

# Reticulo Video Engine

This engine automates the creation of short vertical (1080x1920) product explainer videos. It uses LLM-generated scripts, local or cloud TTS, stock footage from Pexels, and FFmpeg/Blender rendering to produce faceless, narration-driven shorts suitable for YouTube Shorts, Instagram Reels, etc.

## Quickstart

### Prerequisites

- **Python 3.11+**
- **FFmpeg** (with `ffmpeg` and `ffprobe` in PATH) – mandatory
- **Blender** (optional, for Blender‑based product hero scenes)
- API keys: Groq (LLM), Pexels (stock videos). ElevenLabs TTS is optional.

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd Video_Generation_Engine

# Create virtual environment
python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate          # Windows

# Install Python dependencies
pip install -r requirements.txt

# (Optional) Install Kokoro TTS for local voice synthesis
pip install kokoro soundfile
Configuration
Copy .env.example to .env and fill in your keys:

ini
GROQ_API_KEY=your_groq_key
GROQ_MODEL=llama-3.1-8b-instant
PEXELS_API_KEY=your_pexels_key
# Optional ElevenLabs (if you prefer cloud TTS)
ELEVENLABS_API_KEY=
ELEVENLABS_VOICE_ID=
ELEVENLABS_MODEL=
Run the Engine
bash
python runner/main.py
You will be prompted to select a hook video from downloaded Pexels clips. The engine then:

Generates a script (Groq)

Plans scenes

Aligns voiceover to durations

Synthesizes audio (Kokoro by default)

Renders each scene with FFmpeg

Concatenates everything into outputs/youtube_shorts/final_video.mp4

Folder Structure (key items)
text
.
├── blender/               # Blender scene template & render script
├── chains/                # LLM prompts: script, scene planning, voiceover enrichment
├── config/                # YAML configs (app, compliance, ffmpeg, platforms, voices)
├── data/                  # Product JSON, audio cache, stock b-roll
├── defaults/              # Default assets (outro audio, end credits, etc.)
├── llm/                   # Groq API client
├── planner/               # Scene allocation, timing, visual mapping stubs
├── renderer/              # FFmpeg/Blender renderers, concat, motion presets
├── runner/                # Main orchestrator
├── schemas/               # Pydantic models for product, scene, script, voiceover
├── services/              # Pexels video downloader
├── tts/                   # TTS providers: fish_tts.py (Kokoro), elevenlabs_tts.py
├── utils/                 # Overlay shortener, TTS text normalizer
├── validators/            # Forbidden terms scanner
├── outputs/               # Final video and intermediate concatenation files
└── video_segments/        # Per‑scene rendered MP4s

Documentation
For full architecture, data flow, configuration reference, and troubleshooting, see DOCUMENTATION_FULL.md.

Dependencies
Python packages: pydantic>=2.0, PyYAML, python-dotenv, requests

System tools: ffmpeg, ffprobe

Optional: blender, kokoro + soundfile

---

## Notes

- The project uses FFmpeg and (optionally) Blender; make sure both are installed and accessible.
- TTS options: local Kokoro (no API) or ElevenLabs (API-based). Add the packages and keys as needed.

