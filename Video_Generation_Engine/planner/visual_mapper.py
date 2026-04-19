# planner/visual_mapper.py
from pathlib import Path
from renderer.stock_broll_manager import get_stock_broll


KEYWORD_MAP = {
    "food": "dog_food",
    "nutrition": "dog_food",
    "puppy": "puppy",
    "benefit": "dog_play",
    "play": "dog_play",
    "lifestyle": "lifestyle",
    "groom": "grooming"
}


def resolve_visual(scene, product_images, image_index):
    scene_type = scene["scene_type"]

    if scene_type == "hook":
        return {"type": "solid"}

    if scene_type == "product_overview" and product_images:
        return {
            "type": "image",
            "path": product_images[image_index % len(product_images)]
        }

    if scene_type in ("benefits", "audience"):
        broll = get_stock_broll(scene["overlay"])
        if broll:
            return {"type": "video", "path": broll}

    return {"type": "solid"}
