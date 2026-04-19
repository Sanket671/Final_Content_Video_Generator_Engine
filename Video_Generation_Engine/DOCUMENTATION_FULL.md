```markdown
# Reticulo Video Engine — Full Technical Documentation

This document describes the video generation engine in depth: architecture, dataflow, module responsibilities, configuration, rendering internals, troubleshooting, and recommended improvements. Use this as the canonical reference when developing, running, or extending the engine.

---

## 1. High‑level Overview

**Purpose**  
Automatically generate vertical (1080×1920) product explainer shorts from a product JSON. The final video combines:
- A hook video (stock footage from Pexels)
- An LLM‑generated neutral, factual script
- Scene planning (product image, bullet features, social proof overlay, outro)
- Voiceover (local Kokoro TTS or ElevenLabs)
- FFmpeg composition (backgrounds, image overlays, text, motion)
- (Optional) Blender rendering for stylised hero scenes

**Input**  
- Product metadata (JSON conforming to `CinematographyProduct` schema)
- Environment variables for API keys (Groq, Pexels, optional ElevenLabs)

**Output**  
`outputs/youtube_shorts/final_video.mp4` – a complete, timed, narrated short video.

**Core Design Principles**
- **Faceless** – no presenter, only visuals + voiceover.
- **Informational** – no hype, no medical claims, no pricing.
- **Modular** – each scene rendered independently, then concatenated.
- **Configurable** – YAML files control app behaviour, forbidden terms, resolution, etc.

---

## 2. Execution Flow (Step‑by‑step)

The orchestrator is `runner/main.py`. Steps:

1. **Load environment** (`load_dotenv()`) and config (implicitly via modules that read YAML).
2. **Load product** – reads `data/products/sample_product.json` into `schemas.product.CinematographyProduct`.
3. **Build search query** – `build_search_query()` heuristically combines category, surface, tags, brand to create a compact Pexels query.
4. **Fetch hook videos** – `services/pexels_service.fetch_and_save_pexels_video_batch()` downloads up to 20 vertical clips into `data/stock_broll/`.
5. **User selects hook** – CLI prompt shows candidates; operator picks one.
6. **Generate script** – `chains/script_generation.generate_script()` calls Groq with a strict prompt, returns JSON containing `hook`, `problem`, `product_intro`, `social_proof`, `features` (4 items), `outro`.
7. **Plan scenes** – `chains/scene_planning.plan_scenes()` maps script sections to `Scene` objects (id, type, duration, overlay text, media path, voiceover text). Scene types: `video`, `product_image`, `review_text`, `blue_bg_bullets`, `text_overlay`, `silence`.
8. **Enrich voiceover** – `chains/voiceover_enricher.enrich_voiceover()` uses Groq again to align voiceover lines to scene durations (assuming 140 wpm). Returns `VoiceoverOutput` (per‑scene text + estimated duration).
9. **Generate TTS audio** – by default `tts/fish_tts.py` (Kokoro) synthesises WAV files into `data/audio_cache/scene_{idx}.wav`. `tts/elevenlabs_tts.py` is available as an alternative.
10. **Render each scene** – `renderer/ffmpeg_scene_renderer.render_scene()` composes each scene’s visual + audio into `video_segments/scene_{idx}.mp4`. For Blender‑based scenes, `blender_scene_renderer.py` and `frames_to_video.py` are used.
11. **Concatenate scenes** – `renderer/final_concat.concat_scenes()` creates a concat list and runs `ffmpeg -f concat -safe 0 -i scenes.txt -c copy` to produce the final MP4.
12. **Output** – final video saved to `outputs/youtube_shorts/final_video.mp4`.

---

## 3. Module Index (File → Responsibility)

| File | Responsibility |
|------|----------------|
| `runner/main.py` | Orchestrator – loads product, fetches hook, user selection, invokes chains, TTS, renderers, concat. |
| `chains/script_generation.py` | Builds prompt, calls Groq, returns structured script JSON. |
| `chains/scene_planning.py` | Converts script + product + hook path into a list of `Scene` objects. |
| `chains/voiceover_enricher.py` | Calls Groq to align voiceover text to scene durations (speaking rate logic). |
| `planner/scene_allocator.py` | Stub – future scene ordering/assignment logic. |
| `planner/timing_calculator.py` | Stub – future advanced timing calculations. |
| `planner/visual_mapper.py` | Resolves visual type (image, video, solid) per scene (used in main orchestration). |
| `llm/groq_client.py` | Low‑level Groq API caller with JSON‑only instruction. |
| `services/pexels_service.py` | Downloads vertical stock videos from Pexels, caches them locally. |
| `tts/fish_tts.py` | Local TTS using Kokoro (no API key). Writes WAVs to `data/audio_cache/`. |
| `tts/elevenlabs_tts.py` | ElevenLabs cloud TTS (requires API key). |
| `renderer/ffmpeg_scene_renderer.py` | FFmpeg‑based scene composer – handles video, image, solid background scenes, text overlays, motion, audio sync. |
| `renderer/blender_scene_renderer.py` | Launches Blender to render frames; used for product hero scenes. |
| `renderer/frames_to_video.py` | Converts image sequence to MP4 and merges with audio. |
| `renderer/final_concat.py` | Concatenates scene MP4s into final output using `-c copy`. |
| `renderer/stock_broll_manager.py` | Local b‑roll cache lookup and Pexels fallback. |
| `renderer/motion_presets.py` | Zoom/pan presets for FFmpeg `zoompan` filter. |
| `utils/overlay_shortener.py` | Reduces feature text to 1–2 words for on‑screen overlays. |
| `utils/tts_normalizer.py` | Converts ALL CAPS brand names to title case for TTS. |
| `validators/forbidden_terms.py` | Scans text for prohibited words (e.g., “best”, “cure”). |
| `validators/compliance_runner.py` | Applies forbidden terms scan to script fields. |
| `schemas/*.py` | Pydantic models: `CinematographyProduct`, `Scene`, `VoiceoverOutput`, etc. |
| `config/*.yaml` | Static configuration: app flags, forbidden terms, FFmpeg defaults, platform limits, voice settings. |

---

## 4. Data Flow (Detailed)

### 4.1 Product → Script
```json
{
  "name": "Nike Air Zoom Pegasus 40...",
  "category": "RUNNING",
  "surface": "Road/Treadmill",
  "tags": ["nike", "running shoes", ...],
  "user_reviews": ["The cushioning is perfect...", ...]
}
↓ build_search_query() → "runner road training"
↓ fetch_and_save_pexels_video_batch("runner road training") → list of video paths
↓ User selects one hook video → hook_video_path, hook_duration

4.2 Script Generation (Groq)
Prompt enforces:

Hook + problem = continuous narrative lasting hook_duration seconds.

No product mention before product_intro.

Exactly 4 keyword‑only features.

Neutral tone, no medical claims, no pricing.

Output JSON:

json
{
  "hook": "...",
  "problem": "...",
  "product_intro": "To address this training need, the Nike Air Zoom Pegasus 40...",
  "social_proof": "Over 3400 users have rated it 4.6 stars...",
  "features": ["Responsive React foam", "Dual Zoom Air units", "Breathable mesh", "Secure midfoot lockdown"],
  "outro": "This video was sponsored by Reticulo."
}
4.3 Scene Planning
Each script section becomes one or more Scene objects. Example mapping:

Scene ID	Type	Duration	Overlay	Media path	Voiceover
1	video	hook_duration	(hook text)	hook_video_path	hook + problem
2	product_image	4	product name	product image URL	product_intro
3	review_text	3	"⭐ 4.6+ Rated"	–	social_proof
4	text_overlay	3	"Why It Works"	–	"These results are supported by key ingredients..."
5-8	blue_bg_bullets	5 each	short feature (2 words)	–	full feature sentence
9	outro	4	–	–	outro (disclosure)
4.4 Voiceover Enrichment
For scenes 1 and 2: voiceover text is taken exactly as provided (no rewriting).

For feature scenes (5‑8): voiceover must be the exact feature keywords (no expansion).

For other scenes: LLM rewrites script content to fit the scene duration (140 wpm speaking rate).

Output: VoiceoverOutput with per‑scene text and approx_duration_sec.

4.5 TTS Generation
tts/fish_tts.py uses Kokoro’s KPipeline with voice af_bella (natural female). Generates data/audio_cache/scene_{idx}.wav at 24 kHz.

4.6 Rendering (FFmpeg)
renderer/ffmpeg_scene_renderer.render_scene() handles:

Hook video (scene_id=1, type=video) – scales/crops input to 1080×1920, uses setpts to match audio duration, overlays audio.

Product image – creates a solid brand‑coloured background (#0EA49F), scales product image (900px max dimension), applies gentle zoom (1.02+0.0008*n), shadow blur, contrast/saturation tweaks, overlays audio.

Silence / fallback – solid colour background with optional drawtext overlay.

Outro (scene_id=9) – uses defaults/end_credits.mp4, stretches to audio duration.

All scenes output to video_segments/scene_{idx}.mp4 with consistent codec (libx264, aac) and resolution.

4.7 Concatenation
final_concat.py writes a FFmpeg concat file and runs:

bash
ffmpeg -y -f concat -safe 0 -i scenes.txt -c copy outputs/youtube_shorts/final_video.mp4
The -c copy preserves quality and avoids re‑encoding.

5. Configuration & Environment Variables
5.1 Environment Variables (.env)
Variable	Required	Purpose
GROQ_API_KEY	Yes	Groq LLM API key
GROQ_MODEL	Yes	e.g. llama-3.1-8b-instant
PEXELS_API_KEY	Yes	Pexels API key for stock videos
ELEVENLABS_API_KEY	No	ElevenLabs TTS (if used)
ELEVENLABS_VOICE_ID	No	Voice ID for ElevenLabs
ELEVENLABS_MODEL	No	Model for ElevenLabs
5.2 YAML Configuration Files (config/)
app.yaml – dry_run flag, application name.

compliance.yaml – forbidden_terms list, affiliate disclosure text.

ffmpeg.yaml – resolution (1080x1920), FPS (30).

platforms.yaml – max duration per platform (YouTube Shorts, Instagram Reels).

voices.yaml – default voice and speed.

These are loaded by respective modules (e.g., ffmpeg_scene_renderer.py reads ffmpeg.yaml for resolution).

6. Rendering Internals
6.1 FFmpeg Scene Renderer (ffmpeg_scene_renderer.py)
Key constants:

python
WIDTH = 1080
HEIGHT = 1920
FPS = 30
BRAND_BG = "#0EA49F"          # Teal background for product shots
PRODUCT_SCALE = 900           # Max dimension of product image
PRODUCT_ZOOM = "1.02+0.0008*n"
SHADOW_BLUR = 18
Product image scene command (simplified):

bash
ffmpeg -y \
  -f lavfi -i color=c=#0EA49F:s=1080x1920:d={audio_dur}:r=30 \
  -loop 1 -i product.png \
  -i scene_audio.wav \
  -filter_complex "
    [1:v]scale=900:-1,format=rgba,boxblur=18:1,
         zoompan=z='1.02+0.0006*on':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)',
         eq=contrast=1.05:saturation=0.92[product];
    [0:v][product]overlay=(W-w)/2:(H-h)/2[v];
    [2:a]aresample=44100[a]
  " -map "[v]" -map "[a]" -t {audio_dur} -c:v libx264 -c:a aac output.mp4
Hook video scene:

Input video scaled/cropped to fill 1080×1920.

setpts factor = audio_dur / original_video_dur to speed up or slow down.

Audio mapped directly.

6.2 Blender Rendering (blender_scene_renderer.py + blender/render_frames.py)
blender_scene_renderer.render_product_scene():

Calls Blender in background mode:

bash
blender --background blender/studio.blend --python blender/render_frames.py -- <product_image> <duration> <output_dir>
render_frames.py loads the product image into the scene’s material, sets up camera movement, renders frames.

Then frames_to_video.py converts the frame sequence to MP4 and merges with audio.

Note: The Blender path is hardcoded as /Applications/Blender.app/Contents/MacOS/Blender – adjust for your OS.

7. Dependencies & System Requirements
Python Packages (from requirements.txt)
pydantic>=2.0

PyYAML

python-dotenv

requests

Additional Python Packages (required for TTS)
kokoro – local TTS engine

soundfile – saving WAV files

Install with:

bash
pip install kokoro soundfile
System Binaries
ffmpeg and ffprobe – must be in PATH.

blender (optional) – if using Blender scenes.

API Keys
Groq: https://console.groq.com

Pexels: https://www.pexels.com/api/

8. Running the Engine – Step‑by‑step
Install system dependencies

macOS: brew install ffmpeg blender

Ubuntu: sudo apt install ffmpeg blender

Windows: download from official websites and add to PATH.

Set up Python environment (see Quickstart in README).

Create .env with at least GROQ_API_KEY, GROQ_MODEL, PEXELS_API_KEY.

Place product JSON at data/products/sample_product.json (or edit the path in runner/main.py).

Run:

bash
python runner/main.py
Select hook video when prompted.

Wait – generation may take several minutes (downloading videos, LLM calls, TTS, FFmpeg encoding).

Find final video at outputs/youtube_shorts/final_video.mp4.

9. Artifacts & File Locations
Path	Description
data/stock_broll/*.mp4	Downloaded Pexels hook videos
data/audio_cache/scene_*.wav	TTS‑generated audio per scene
video_segments/scene_*.mp4	Rendered scenes (one per scene)
outputs/youtube_shorts/final_video.mp4	Final concatenated video
outputs/youtube_shorts/scenes.txt	FFmpeg concat list (debug)
tmp_product_*.png/jpg	Downloaded product images (temporary)
blender/outputs/scene_*_frames/	Blender frame sequences (if used)
10. Validation & Compliance
validators/forbidden_terms.py checks for words listed in config/compliance.yaml (e.g., “best”, “guaranteed”, “cure”).

The compliance runner (validators/compliance_runner.py) is called manually – integrate into the pipeline as needed.

LLM prompts explicitly forbid medical claims, pricing, and hype. However, output should still be reviewed.

11. Known Issues & Limitations
Blender path hardcoded for macOS – set BLENDER_BIN environment variable or modify blender_scene_renderer.py.

Kokoro TTS not in requirements.txt – must be installed separately.

FFmpeg filter quoting – may break on Windows; consider using shlex.quote or passing filter arguments as a list.

Stock b‑roll manager (stock_broll_manager.py) expects PEXELS_API_KEY but doesn’t call load_dotenv() – ensure the key is set in the environment.

Interactive hook selection – not suitable for headless/batch runs. Add a --auto-select flag.

No retry logic for API calls (Groq, Pexels) – may fail on transient errors.

Planner stubs (scene_allocator.py, timing_calculator.py) are not used – production timing is handled inside voiceover_enricher.py.

12. Troubleshooting
Problem	Likely cause	Solution
ffmpeg: command not found	FFmpeg not installed or not in PATH	Install FFmpeg and verify ffmpeg -version
FileNotFoundError: data/audio_cache/scene_1.wav	TTS generation skipped or failed	Check TTS module; run with print statements; ensure Kokoro installed
Groq API error (401, 429)	Invalid or exhausted API key	Verify .env and quota
Pexels returns empty list	Bad query or API key	Test query manually; check key permissions
Blender render fails	Incorrect path to Blender binary	Set BLENDER_BIN environment variable
Overlay text not appearing	drawtext filter syntax error	Inspect generated FFmpeg command; escape special characters
Final video has no audio	Audio track missing from one scene	Check that all scenes have corresponding .wav files
13. Architectural Views
13.1 Developer Perspective
Modify narrative: edit chains/script_generation.py (prompt) and chains/voiceover_enricher.py.

Change scene types/durations: chains/scene_planning.py.

Tweak visual rendering: renderer/ffmpeg_scene_renderer.py (constants, filter graphs).

13.2 Dataflow / Architectural
text
Product JSON → Search Query → Pexels API → Hook video
Product JSON → Groq → Script JSON → Scene list → Voiceover lines
Voiceover lines → TTS → WAV files
Scene list + WAVs + visuals → FFmpeg → Scene MP4s → Concat → Final MP4
13.3 Runtime / Operations
Heavy steps: Pexels download (network), TTS (CPU), FFmpeg encoding (CPU).

Disk usage: each scene MP4 ~5‑10 MB, final video ~20‑40 MB for 30‑60s.

13.4 QA / Evaluation
Check per‑scene audio duration matches visual duration (use ffprobe).

Verify overlays are readable at 1080×1920 (text size, position).

Ensure no forbidden terms appear.

13.5 Security & Compliance
API keys stored in .env, not in code.

Forbidden terms scan before publishing.

No user data collected.

14. Recommended Improvements
Configurable Blender path – read from environment or config.

Non‑interactive mode – CLI argument to automatically pick first or best hook video.

Unified TTS interface – abstract base class with ElevenLabs and Kokoro implementations.

Better error handling – retries for API calls, graceful fallback to solid colour if product image fails.

Unit tests for prompt parsing, scene planning, and FFmpeg command generation.

Logging instead of print statements.

Caching of LLM responses for identical product inputs.

Parallel rendering of scenes (multiprocessing) to speed up generation.

15. Appendix – Useful Commands
Run orchestrator

bash
python runner/main.py
Manually test TTS

python
from tts.fish_tts import generate_voiceover_audio
generate_voiceover_audio([{"text": "Hello world"}])
Render a single scene with FFmpeg

bash
python -c "from renderer.ffmpeg_scene_renderer import render_scene; render_scene({'scene_id':2,'duration':5}, 2, {'type':'image','path':'product.png'})"
Concatenate existing MP4s

bash
ffmpeg -f concat -safe 0 -i <(for f in video_segments/scene_*.mp4; do echo "file '$PWD/$f'"; done) -c copy output.mp4
End of Documentation