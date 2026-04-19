import json
import sys
import os
import re
from pathlib import Path

# Add project root to sys.path to allow imports from sibling directories like 'schemas'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

# Schemas and Chains
from schemas.product import CinematographyProduct
from chains.script_generation import generate_script
from chains.scene_planning import plan_scenes
from chains.voiceover_enricher import enrich_voiceover
from services.pexels_service import fetch_and_save_pexels_video_batch

# Renderers
from renderer.ffmpeg_scene_renderer import render_scene
from renderer.final_concat import concat_scenes

# TTS
from tts.fish_tts import generate_voiceover_audio


def build_search_query(product: CinematographyProduct) -> str:
    def normalize(value: str) -> str:
        value = value.strip().lower()
        value = value.replace("/", " ")
        value = re.sub(r"[^a-z0-9\s-]", " ", value)
        value = re.sub(r"\s+", " ", value)
        return value.strip()

    candidates = []

    for value in [
        product.category,
        product.surface,
        product.athleteType,
        product.forPet,
        product.petAgeGroup,
    ]:
        if isinstance(value, str) and value.strip():
            normalized = normalize(value)
            if normalized:
                candidates.extend(normalized.split())

    if product.slug:
        slug_terms = normalize(product.slug).split("-")
        candidates.extend(term for term in slug_terms if term)

    if product.tags:
        for tag in product.tags[:4]:
            normalized = normalize(tag)
            if normalized:
                candidates.extend(normalized.split())

    unique_terms = []
    seen = set()
    stop_words = {"product", "best", "latest", "mens", "men", "womens", "women"}
    for term in candidates:
        if term in stop_words or len(term) < 3:
            continue
        if term not in seen:
            seen.add(term)
            unique_terms.append(term)

    if {"running", "road"} <= set(unique_terms):
        return "runner road training"
    if "running" in unique_terms:
        return "runner training track"
    if "shoes" in unique_terms or "shoe" in unique_terms:
        return "athlete training footwear"
    if product.forPet and product.petAgeGroup:
        return f"{normalize(product.petAgeGroup)} {normalize(product.forPet)} playing"
    if len(unique_terms) >= 3:
        return " ".join(unique_terms[:3])
    if len(unique_terms) >= 1:
        return " ".join(unique_terms)

    return normalize(product.brand) or "lifestyle product"


def main():
    # 0️⃣ Load environment variables
    print("🔌 Loading environment variables...")
    load_dotenv()

    # 1️⃣ Load product
    print("📦 Loading product data...")
    product_json = Path("data/products/sample_product.json").read_text()
    product = CinematographyProduct.model_validate_json(product_json)

    # 2️⃣ Fetch hook videos
    search_query = build_search_query(product)
    print(f"🔍 Searching Pexels for: {search_query}...")

    video_list = fetch_and_save_pexels_video_batch(search_query, count=20)
    if not video_list:
        print("❌ No videos found on Pexels.")
        return

    # 3️⃣ User selects hook
    print("\n" + "=" * 30)
    print("   SELECT YOUR HOOK VIDEO")
    print("=" * 30)
    for idx, vid in enumerate(video_list):
        print(f"[{idx}] ID: {vid.get('id')} | Duration: {vid.get('duration')}s")

    try:
        choice = int(input("\nEnter the number (0-19): "))
        selected_video = video_list[choice]
    except (ValueError, IndexError):
        print("⚠️ Invalid selection. Defaulting to [0].")
        selected_video = video_list[0]

    video_path = selected_video["path"]
    hook_duration = selected_video["duration"]

    print(f"\n🚀 Using selected hook video ({hook_duration}s)")

    # 4️⃣ Generate script
    print("\n🤖 Generating script...")
    script_data = generate_script(product, hook_duration)

    print("\n--- SCRIPT PREVIEW ---")
    print(json.dumps(script_data, indent=2))
    print("-" * 30)

    # 5️⃣ Plan scenes
    print("🎬 Planning scenes...")
    scenes = plan_scenes(script_data, product, video_path, hook_duration)

    # 6️⃣ Enrich voiceover
    print("✍️ Generating voiceover text...")
    vo_output = enrich_voiceover(
        script_data,
        [s.model_dump() for s in scenes],
        hook_duration
    )

    # 7️⃣ Generate audio
    print("🎙️ Generating TTS audio...")
    generate_voiceover_audio(
        [{"text": line.text} for line in vo_output.voiceover]
    )

    # 8️⃣ Render scenes
    print("🎞️ Rendering video scenes...")
    rendered_scenes = []

    for idx, scene in enumerate(scenes, start=1):
        scene_dict = scene.model_dump()

        # -----------------------------
        # 🎬 ALL OTHER SCENES → FFMPEG
        # -----------------------------
        if scene.scene_id == 1:
            visual = {
                "type": "video",
                "path": scene_dict.get("media_path")
            }
        elif scene.scene_id == 4:
            visual = {
                "type": "video",
                "path": video_path
            }
        elif scene_dict.get("media_path"):
            visual = {
                "type": "image",
                "path": scene_dict["media_path"]
            }
        else:
            visual = {"type": "solid"}

        out = render_scene(
            scene=scene_dict,
            scene_index=idx,
            visual=visual,
            product=product,
            execute=True
        )

        rendered_scenes.append(out)

    # 9️⃣ Concatenate final video
    print("🎬 Concatenating final video...")
    final_video = concat_scenes(rendered_scenes)

    print("\n✅ FINAL VIDEO READY")
    print(final_video)


if __name__ == "__main__":
    main()
