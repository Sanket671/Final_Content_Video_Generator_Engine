from pathlib import Path
try:
    from renderer.stock_broll_manager import get_stock_broll
except Exception:
    # If stock b-roll manager cannot be imported (e.g., missing PEXELS key),
    # fall back to returning None from get_stock_broll.
    def get_stock_broll(keyword: str):
        return None


def resolve_visual(scene: dict, product_images: list, image_index: int) -> dict:
    """
    Resolve a visual for the given scene. Returns a dict with keys:
      - type: 'video'|'image'|'solid'
      - path: optional path to the asset

    Uses product images if available, otherwise tries to pick a cached stock b-roll
    clip by keyword. Falls back to a solid brand background.
    """
    scene_type = scene.get("scene_type", "").lower()
    overlay = scene.get("overlay", "")

    # Preserve explicit media_path if provided
    if scene.get("media_path"):
        path = scene.get("media_path")
        # if it's a file-like path or URL, allow renderer to handle it
        return {"type": "video" if str(path).lower().endswith(".mp4") else "image", "path": path}

    # Hook / video scenes
    if scene_type in ("video", "hook"):
        return {"type": "solid"}

    # Product image scenes -> use product images when available
    if scene_type in ("product_image", "product_overview"):
        if product_images:
            return {"type": "image", "path": product_images[image_index % len(product_images)]}
        return {"type": "solid"}

    # For text-heavy scenes try to find a short stock b-roll by keyword
    if scene_type in ("review_text", "text_overlay", "blue_bg_bullets", "feature"):
        keyword = overlay.split()[0].lower() if overlay else ""
        if keyword:
            b = get_stock_broll(keyword)
            if b:
                return {"type": "video", "path": b}

    return {"type": "solid"}
