import json
import math
from schemas.voiceover import VoiceoverOutput
from llm.groq_client import call_groq


def enrich_voiceover(script: dict, scenes: list[dict], hook_duration) -> VoiceoverOutput:
    """
    Converts structured script + scene plan into
    duration-aligned spoken voiceover lines.
    """

    prompt = f"""
You are a professional voiceover script adapter
working on a faceless informational product video.

Your task is to convert the provided script content
into spoken narration that FITS EXACT SCENE DURATIONS.

IMPORTANT CONTEXT RULES:
- This is NOT an advertisement
- This is NOT persuasive marketing
- This is neutral, informational narration
- Target audience: Indian consumers
- Calm, trustworthy, professional tone

SPECIAL INSTRUCTIONS:
- For PRODUCT INTRO scenes (Scene 2):
  The narration MUST clearly connect to the prior concern,
  using phrasing such as:
  "To address this concern…" or
  "To help meet these needs…"
  before introducing the product.

- For SOCIAL PROOF scenes:
  Summarize outcomes from user reviews relevant to the product category
  Do NOT quote reviews verbatim
  Do NOT exaggerate

SPEAKING RATE (STRICT):
- 140 words per minute
- ~2.3 words per second
# Inside enrich_voiceover prompt, add this under SPECIAL INSTRUCTIONS:

- For FEATURE scenes (Scenes 5, 6, 7, and 8):
  The narration MUST be the EXACT keywords provided in the script.
  Do NOT expand them into sentences. 
  Do NOT add words. 
  If the script says "High quality protein", the voiceover MUST only say "High quality protein".

GLOBAL RULES (NON-NEGOTIABLE):
- Do NOT add new facts
- Do NOT remove important facts
- Do NOT exaggerate or praise
- Do NOT make medical or health claims
- Do NOT mention price, discounts, Amazon, or offers
- Do NOT compare brands
- Use short, natural sentences
- Exactly ONE voiceover line per scene
- Do NOT repeat the same sentence across scenes
- Scene 1 narration is AUTHORITATIVE.
- You MUST NOT rewrite, expand, paraphrase, or add words for Scene 1.
- For Scene 1, return the EXACT scene.voiceover text as provided.

For EACH scene:
- If scene_id == 1 or scene_id == 2:
  - Use the scene.voiceover EXACTLY as provided
  - Do NOT rewrite
- For all other scenes:
  - Rewrite the relevant script content into spoken narration
  - Ensure it fits the scene duration



SCRIPT CONTENT (AUTHORITATIVE):
{json.dumps(script, indent=2)}

USER REVIEWS (FOR SOCIAL PROOF SUMMARIZATION ONLY):
{json.dumps(script.get("user_reviews", []), indent=2)}

SCENES (AUTHORITATIVE — DO NOT CHANGE ORDER OR DURATION):
{json.dumps(scenes, indent=2)}

TASK:
For EACH scene:
- Identify the scene intent
- Rewrite the relevant script content into spoken narration
- Ensure it comfortably fits the scene duration
- Maintain logical flow across scenes

OUTPUT FORMAT (JSON ONLY — STRICT):
{{
  "voiceover": [
    {{
      "scene_id": 1,
      "text": "Spoken narration for this scene",
      "approx_duration_sec": 11,
      "word_count": 24
    }}
  ]
}}
"""

    raw = call_groq(prompt).strip()

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Voiceover JSON parsing failed: {e}\n\nRAW OUTPUT:\n{raw}"
        )

    parsed["voiceover"] = _normalize_voiceover(parsed.get("voiceover", []), scenes)

    return VoiceoverOutput.model_validate(parsed)


def _normalize_voiceover(voiceover: list[dict], scenes: list[dict]) -> list[dict]:
    scene_durations = {
        int(scene["scene_id"]): int(scene["duration"])
        for scene in scenes
        if scene.get("scene_id") is not None and scene.get("duration") is not None
    }

    normalized = []
    for item in voiceover:
        if not isinstance(item, dict):
            continue

        scene_id = item.get("scene_id")
        if scene_id is None:
            continue

        scene_id = int(scene_id)
        duration = item.get("approx_duration_sec", scene_durations.get(scene_id, 1))
        if isinstance(duration, float):
            duration = round(duration)
        elif isinstance(duration, str):
            duration = math.ceil(float(duration))

        duration = max(1, int(duration))
        scene_max = scene_durations.get(scene_id)
        if scene_max is not None:
            duration = min(duration, scene_max)

        text = str(item.get("text", "")).strip()
        if not text:
            continue

        normalized.append({
            "scene_id": scene_id,
            "text": text,
            "approx_duration_sec": duration,
            "word_count": item.get("word_count"),
        })

    return normalized
