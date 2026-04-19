from schemas.scene import Scene
from typing import Dict, Any
from pathlib import Path
from utils.tts_normalizer import tts_safe_text
from utils.overlay_shortener import short_overlay


def resolve_product_image(product: Any, scene_id: int) -> str:
    local_candidates = [
        Path(f"tmp_product_{scene_id}.png"),
        Path(f"tmp_product_{scene_id}.jpg"),
        Path(f"tmp_product_{scene_id}.jpeg"),
        Path("tmp_product_2.png"),
        Path("tmp_product_2.jpg"),
        Path("tmp_product_2.jpeg"),
    ]

    for candidate in local_candidates:
        if candidate.exists():
            return str(candidate)

    if getattr(product, "images", None):
        return str(product.images[0])

    return ""


def plan_scenes(
    script_data: Dict[str, Any],
    product: Any,
    hook_video_path: str,
    hook_duration: int
):
    scenes = []

    # 1️⃣ Hook + Problem (FULL HOOK VIDEO)
    intro_voiceover = f"{script_data['hook']} {script_data['problem']}"

    scenes.append(Scene(
        scene_id=1,
        scene_type="video",
        duration=hook_duration,
        overlay=script_data["hook"],
        media_path=hook_video_path,
        voiceover=intro_voiceover
    ))

    # 2️⃣ Product Intro
    product_intro_voiceover = script_data["product_intro"]

    scenes.append(Scene(
    scene_id=2,
    scene_type="product_image",
    duration=4,
    overlay=product.name,
    media_path=resolve_product_image(product, 2),
    voiceover=tts_safe_text(product_intro_voiceover)
))


    # 3️⃣ Social Proof
    scenes.append(Scene(
        scene_id=3,
        scene_type="review_text",
        duration=3,
        overlay=f"⭐ {product.rating}+ Rated",
        voiceover=script_data["social_proof"]
    ))

    # 4️⃣ Feature Intro / Bridge
    scenes.append(Scene(
        scene_id=4,
        scene_type="text_overlay",
        duration=3,
        overlay="Why It Works",
        voiceover="These results are supported by key ingredients and formulation features."
    ))

    # 5️⃣–8️⃣ Features (SHORT OVERLAY, FULL VOICEOVER)
    for i, feature in enumerate(script_data["features"]):
     scenes.append(Scene(
        scene_id=5 + i,
        scene_type="blue_bg_bullets",
        duration=5,
        overlay=short_overlay(feature),  # now clean 2-word overlays
        voiceover=feature
    ))


    return scenes
